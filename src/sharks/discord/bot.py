"""The Sharks Discord bot — one process, four capabilities.

Run:  python -m sharks.discord.bot   (or scripts/run_discord_bot.ps1)

Capabilities
  • Meetings    — posts 晨會 (07:30) / 晚會 (22:30) / 週會 (Mon) digests on a TPE
                  schedule, composed from outputs/ and (optionally) topped with a
                  short Claude research narrative.
  • /ask + #問claude — read-only Claude Code loopback over the $hark tree.
  • #分析師議會 + /persona — analyst personas on local Nemotron.
  • /picks /status /personas /meeting — manual controls.

Safety: recommend-only, never trades; /ask is read-only; the bot never invites
anyone and alerts (does not kick) if an unexpected member appears.
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
import sys
from datetime import datetime
from typing import Optional

import discord
from discord import app_commands
from discord.ext import tasks

from sharks.discord import config as C
from sharks.discord.brains import (
    ask_backend,
    ask_claude_research,
    ask_persona,
    ask_wiki,
    list_ollama_models,
)
from sharks.discord import vision, wiki_ingest, wiki_rag
from sharks.discord.config import TPE, Settings
from sharks.discord.content import run_content_local
from sharks.discord.council import CouncilResult, run_council_local
from sharks.discord.feedback import FeedbackReport, compose_feedback
from sharks.discord.dipbuy import (
    CRYPTO_FINTECH_OBSERVE,
    SOFTWARE_AI_DIPBUY,
    DipCandidate,
    run_dipbuy,
)
from sharks.scoring.cufolio_optimize import optimize as cufolio_optimize
from sharks.scoring import chokepoint
from sharks.discord.meetings import (
    MeetingDigest,
    compose_evening,
    compose_morning,
    compose_noon,
    compose_weekly,
    digest_to_brief,
    research_prompt,
)
from sharks.discord.personas import ChatPersona, load_personas, resolve_persona

log = logging.getLogger("sharks.discord")

_COLORS = {
    "morning": 0xF5A623, "noon": 0x16A085, "evening": 0x4A90D9,
    "weekly": 0x9B59B6, "status": 0x95A5A6, "council": 0xE67E22,
}
_VOTE_EMOJI = {"多": "🟢", "空": "🔴", "中性": "⚪"}


def _chunks(text: str, size: int = 1990) -> list[str]:
    text = text or "—"
    return [text[i : i + size] for i in range(0, len(text), size)]


def digest_to_embeds(d: MeetingDigest, narrative: Optional[str] = None) -> list[discord.Embed]:
    """Render a MeetingDigest as one (or two) Discord embeds."""
    emb = discord.Embed(
        title=d.title[:256],
        description=d.subtitle[:4096],
        color=_COLORS.get(d.kind, _COLORS["status"]),
    )
    for s in d.sections[:24]:
        emb.add_field(name=s.heading[:256], value=(s.body or "—")[:1024], inline=False)
    emb.set_footer(text=f"{d.footer} · as_of {d.as_of}"[:2048])
    embeds = [emb]
    if narrative:
        n = discord.Embed(
            title="🧭 今日敘事（Claude 研究 · 唯讀）",
            description=narrative[:4096],
            color=0x2ECC71,
        )
        n.set_footer(text="僅供研究,非個人化投資建議")
        embeds.append(n)
    return embeds


def council_to_embeds(r: CouncilResult) -> list[discord.Embed]:
    """Render a cross-examination debate as up to 2 embeds:
    (1) 結論 + 正反方數據對照 + 票數/各人投票, (2) 交叉質詢逐筆 Q→答辯."""
    lean = r.lean()
    t = r.tally or {}
    e1 = discord.Embed(
        title=f"🗳️ 議會結論 · 傾向 {_VOTE_EMOJI.get(lean, '')} {lean}",
        description=(r.conclusion or "—")[:2048],
        color=_COLORS["council"],
    )
    e1.add_field(
        name="票數",
        value=(f"🟢 多 {t.get('多', 0)} · 🔴 空 {t.get('空', 0)} · "
               f"⚪ 中性 {t.get('中性', 0)} · 平均信心 {t.get('avg_conviction', '?')}/5"),
        inline=False,
    )
    if r.bull or r.bear:
        if r.bull:
            e1.add_field(name="🟢 正方 · 看多",
                         value="\n".join(f"• {b}" for b in r.bull)[:1024], inline=True)
        if r.bear:
            e1.add_field(name="🔴 反方 · 看空",
                         value="\n".join(f"• {b}" for b in r.bear)[:1024], inline=True)
    elif r.ledger:                                   # parse failed → show raw ledger
        e1.add_field(name="⚔️ 正反方對照", value=r.ledger[:1024], inline=False)
    if r.crux or r.unresolved:
        crux = (f"⚖️ 分歧:{r.crux}" if r.crux else "")
        unres = (f"\n🔍 待驗證:{r.unresolved}" if r.unresolved else "")
        e1.add_field(name="關鍵", value=(crux + unres).strip()[:1024], inline=False)
    lines = [
        f"{_VOTE_EMOJI.get(v.vote, '')} **{v.title}** `{v.model}` 信心{v.conviction} · {v.action or '—'}"
        for v in r.votes
    ]
    if lines:
        e1.add_field(name="🗳️ 各人投票(模型)", value="\n".join(lines)[:1024], inline=False)
    models_used = ", ".join(sorted({v.model for v in r.votes if v.model}))
    e1.set_footer(text=f"本地多模型議會 · {models_used} · 僅研究非建議,永不下單"[:2048])
    embeds = [e1]

    # (2) 交叉辯論 — group questions by the persona being interrogated
    if r.exchanges:
        e2 = discord.Embed(title="🔁 交叉質詢 · 互相提問與答辯",
                           color=_COLORS.get("council", 0x5865F2))
        by_target: dict[str, list] = {}
        for ex in r.exchanges:
            by_target.setdefault(ex.target, []).append(ex)
        for tname, exs in list(by_target.items())[:25]:
            qs = "\n".join(f"❓ {ex.asker_title}:{ex.question}" for ex in exs)
            ans = exs[0].answer or "(未答辯)"
            val = f"{qs}\n\n💬 **{exs[0].target_title}**:{ans}"
            e2.add_field(name=f"🎯 質詢 {exs[0].target_title}", value=val[:1024], inline=False)
        if e2.fields:
            embeds.append(e2)
    return embeds


def council_to_embed(r: CouncilResult) -> discord.Embed:
    """Back-compat single-embed view (結論 + 正反方); callers prefer council_to_embeds."""
    return council_to_embeds(r)[0]


def _brief_with_news(base: str, n: int = 6) -> str:
    """Append a few live RSS headlines so the debate argues over 數據+消息, not data
    alone. Best-effort — network failure just returns the data-only brief."""
    try:
        from sharks.discord.chatter import fetch_headlines
        heads = fetch_headlines(n)[0]
    except Exception:
        heads = []
    if not heads:
        return base
    news = "\n".join(f"- {h}" for h in heads[:n])
    return f"{base}\n\n近期消息(point-in-time 頭條):\n{news}"


_FB_META = {
    "HOLD_AND_DEEPEN": ("🟢 不換股 · 深挖支撐", 0x2ECC71),
    "WATCH": ("⚪ 正常健檢", 0x95A5A6),
    "ROTATE": ("🔴 真反轉 · 執行換股", 0xE74C3C),
}


def feedback_to_embed(r: FeedbackReport) -> discord.Embed:
    """Render the performance-feedback rotation throttle as one embed."""
    label, color = _FB_META.get(r.verdict, _FB_META["WATCH"])
    e = discord.Embed(title=f"📊 換股節流 · {label}", description=r.note[:4096], color=color)
    basis = ("你回報" if r.perf_basis == "stated" else "推估")
    e.add_field(name="反饋依據",
                value=(f"績效({basis}):**{r.perf_label}** · "
                       f"反轉:{'是 ⚠️ ' + '、'.join(r.reversal_reasons) if r.reversal else '否'}"),
                inline=False)
    if r.support and r.verdict != "ROTATE":
        lines = [f"`{h.ticker}` {h.pct:.1f}% · FOM={h.final_fom if h.final_fom is not None else '?'}"
                 f" (mom {h.momentum}/qual {h.quality})" for h in r.support]
        e.add_field(name="支撐數據(贏家為何續抱)", value="\n".join(lines)[:1024], inline=False)
    if r.rotation:
        lines = [f"`{h.ticker}` {h.pct:.1f}% · {h.verdict}"
                 + (f" · decay {h.decay_pct}%/yr" if h.decay_pct else "") for h in r.rotation]
        head = "換股候選" if r.verdict == "ROTATE" else "減碼衛生(非換股,槓桿 decay 優先)"
        e.add_field(name=head, value="\n".join(lines)[:1024], inline=False)
    e.add_field(name="翻為『換股』的觸發", value="\n".join(f"• {t}" for t in r.invalidation)[:1024],
                inline=False)
    e.set_footer(text="recommend-only · 永不下單 · 換股需十足證據;防守可快"[:2048])
    return e


def dipbuy_to_embed(title: str, rows: list[DipCandidate]) -> discord.Embed:
    """Render the 抄底起漲 screen (距高 + 盈利 + 起漲) as one embed."""
    e = discord.Embed(
        title=f"🎯 抄底起漲 · {title}",
        description="距 ATH 有段 + 盈利支持 + 開始起漲。賣弱→抄底起漲(H2-2026 頂底互換)。",
        color=0x1ABC9C,
    )
    hot = [c for c in rows if c.verdict.startswith(("🟢", "🟡"))]
    wait = [c for c in rows if c.verdict.startswith("🔵")]
    other = [c for c in rows if c not in hot and c not in wait]
    def line(c: DipCandidate) -> str:
        if c.last is None:
            return f"`{c.ticker}` — {c.note}"
        return (f"`{c.ticker}` {c.verdict} · 距高 {c.dist_ath_pct:.0f}% · "
                f"1m {c.ret_1m:+.0f}%" + (f" · q{c.quality:.0f}" if c.quality is not None else ""))
    if hot:
        e.add_field(name="🟢 起漲候選(可進場觀察)", value="\n".join(line(c) for c in hot)[:1024], inline=False)
    if wait:
        e.add_field(name="🔵 抄底待起漲(等動能轉強)", value="\n".join(line(c) for c in wait)[:1024], inline=False)
    if other:
        e.add_field(name="其他(近高/太深/資料不足)", value="\n".join(line(c) for c in other)[:1024], inline=False)
    e.set_footer(text="recommend-only · 即時 yfinance + FOM quality · 盈利 TBD=待納入 FOM 宇宙")
    return e


# ── cuFOLIO Mean-CVaR (GPU cuOpt on RTX 5070) ────────────────────────────────
_CRYPTO_YF = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "DOT": "DOT-USD"}
_MEGACAP = ["MSFT", "AAPL", "GOOGL", "AMZN", "META", "NVDA", "AVGO", "AMD"]


def _resolve_universe(uni: str, tickers: Optional[str]) -> tuple[list[str], str]:
    """Map a /optimize universe choice (or free-text tickers) to a symbol list."""
    if tickers:
        syms = [s.strip().upper() for s in tickers.replace(",", " ").split() if s.strip()]
        return syms, f"自訂 {len(syms)} 檔"
    if uni == "crypto":
        return [_CRYPTO_YF.get(t, t) for t in CRYPTO_FINTECH_OBSERVE], "加密/fintech"
    if uni == "megacap":
        return list(_MEGACAP), "大型科技權值"
    return list(SOFTWARE_AI_DIPBUY), "軟體/AI 抄底"


def optimize_to_embed(res: dict, label: str, solver: str) -> discord.Embed:
    """Render a cuFOLIO Mean-CVaR weight suggestion as one embed."""
    if not res.get("ok"):
        e = discord.Embed(title="🧮 Mean-CVaR 最佳化", color=0xE74C3C,
                          description=f"⚠️ {res.get('error', '失敗')}")
        if res.get("detail"):
            e.add_field(name="detail", value=f"```{str(res['detail'])[:300]}```", inline=False)
        return e
    dev = "GPU cuOpt · RTX 5070" if solver == "cuopt" else "CPU CLARABEL"
    er, cvar = res.get("expected_return"), res.get("CVaR")
    er_a = f"{er * 252 * 100:+.0f}%/yr" if isinstance(er, (int, float)) else "—"   # daily→年化(約)
    cvar_s = f"{cvar * 100:.2f}%/day" if isinstance(cvar, (int, float)) else "—"
    e = discord.Embed(
        title=f"🧮 Mean-CVaR 最佳建議權重 · {label}",
        description=(f"在候選集合上最小化尾部風險(CVaR@95%)的 long-only 配置。\n"
                     f"預期報酬 ≈ **{er_a}** · 日 CVaR ≈ **{cvar_s}** · "
                     f"納入 **{res.get('used', '?')}/{res.get('requested', '?')}** 檔"),
        color=0x9B59B6)
    rows = res.get("top") or []
    held = [(t, w) for t, w in rows if w and w > 0.001]
    if held:
        bars = "\n".join(f"`{t:<6}` {'█' * max(1, round(w * 20))} {w * 100:4.1f}%"
                         for t, w in held)
        e.add_field(name="建議權重(long-only)", value=bars[:1024], inline=False)
    zeros = [t for t, w in rows if not w or w <= 0.001]
    if zeros:
        e.add_field(name="排除(權重→0:尾部風險/相關性不划算)",
                    value=" ".join(f"`{t}`" for t in zeros)[:1024], inline=False)
    e.set_footer(text=f"recommend-only · {dev} · 解題 {res.get('solve_time', '?')}s · "
                      f"非投資建議,Risk Officer 與證據門檻仍有最終否決權")
    return e


def chokepoint_to_embed(result: dict) -> discord.Embed:
    """Render a chokepoint analysis (bottleneck -> FOM-scored candidates) as one embed."""
    bt_types = chokepoint.BOTTLENECK_TYPES
    e = discord.Embed(
        title=f"🔗 卡脖子分析 · {result['topic'][:200]}",
        description=("供應鏈瓶頸 → 握有瓶頸的公司 → 用你的 FOM 重新評分。研究非建議。"
                     + ("" if result["matched"] else " ⚠️ 無對應 lane,以下為本地 LLM 提名,需查證。")),
        color=0x8E44AD,
    )
    for lane in result["lanes"][:3]:
        lines = []
        for r in (lane.get("candidates") or [])[:6]:
            rr = f"{r['ret_3m']:+.0f}%" if r.get("ret_3m") is not None else "—"
            lines.append(
                f"`{r['ticker']}` FOMα{r.get('final_fom_alpha', 0):.0f} · 護城河{r.get('ip_defensibility', '?')}"
                f" · 逆勢{r.get('contrarian', 0):.0f} · 動能{r.get('momentum', 0):.0f} · 近3月{rr}")
        bt = bt_types.get(lane.get("bottleneck_type"))
        body = f"**瓶頸**:{lane['bottleneck']}" + (f"({bt})" if bt else "")
        if lane.get("stack"):
            body += "\n**stack**:" + " → ".join(lane["stack"])
        body += "\n" + ("\n".join(lines) if lines else "(無有效標的資料)")
        if lane.get("thesis_breaker"):
            body += f"\n_破論點:{lane['thesis_breaker']}_"
        e.add_field(name=f"▸ {lane['label']}", value=body[:1024], inline=False)
    e.set_footer(text="recommend-only · FOM 自評分(不採信外部分數)· 永不下單")
    return e


class SharksBot(discord.Client):
    def __init__(self, settings: Settings, run_once: Optional[list[str]] = None):
        intents = discord.Intents.default()
        intents.message_content = True   # privileged — enable in Dev Portal
        intents.members = True           # privileged — for the privacy alert
        super().__init__(intents=intents)
        self.settings = settings
        self.tree = app_commands.CommandTree(self)
        self.personas: dict[str, ChatPersona] = load_personas(settings)
        self._last_fired: dict[str, str] = {}
        self._chatter_count = 0          # hourly 雜談 ticks (council runs every Nth)
        self.run_once = run_once or []   # one-shot meeting kinds, then exit

    # ── lifecycle ─────────────────────────────────────────────────────────────
    async def setup_hook(self) -> None:
        if self.run_once:
            return  # one-shot: skip command sync + scheduler
        self._register_commands()
        guild = self._guild()
        if guild:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)   # instant in one guild
        else:
            await self.tree.sync()
        self.scheduler.start()

    async def on_ready(self) -> None:
        log.info("logged in as %s (guilds=%d)", self.user, len(self.guilds))
        if self.run_once:
            for kind in self.run_once:
                try:
                    await self.post_meeting(kind)
                except Exception as exc:  # pragma: no cover - network
                    log.exception("run_once meeting %s failed: %s", kind, exc)
            await self.close()
            return
        ch = self._channel(C.CH_STATUS)
        if ch:
            await ch.send(embed=self._status_embed("✅ 上線"))

    # ── helpers ───────────────────────────────────────────────────────────────
    def _guild(self) -> Optional[discord.Guild]:
        if self.settings.guild_id:
            g = self.get_guild(self.settings.guild_id)
            if g:
                return g
        return self.guilds[0] if self.guilds else None

    def _channel(self, name: str) -> Optional[discord.TextChannel]:
        g = self._guild()
        if not g:
            return None
        return discord.utils.get(g.text_channels, name=name)

    def _status_embed(self, title: str) -> discord.Embed:
        s = self.settings
        e = discord.Embed(title=f"PolkaSharks bot — {title}", color=_COLORS["status"])
        e.add_field(name="後端", value=s.backend, inline=True)
        e.add_field(name="Claude 模型", value=s.claude_model, inline=True)
        e.add_field(name="本地模型", value=s.local_model, inline=True)
        e.add_field(name="晨/午/晚",
                    value=f"{s.morning_hhmm} / {s.noon_hhmm} / {s.evening_hhmm} TPE", inline=True)
        e.add_field(name="議會",
                    value=(f"{'on' if s.council_enabled else 'off'} · "
                           f"{s.effective_council_model()} · {'/'.join(s.council_personas)}"),
                    inline=False)
        e.add_field(name="雜談",
                    value=(f"{'on' if s.chatter_enabled else 'off'} · 每小時速解讀 → #{C.CH_GENERAL} · "
                           f"council 每 {s.chatter_council_every} 次"), inline=False)
        e.add_field(name="人格", value=", ".join(sorted(self.personas)) or "—", inline=False)
        e.set_footer(text="recommend-only · 永不下單 · /ask 唯讀 · 議會/雜談跑本地")
        return e

    def _help_embed(self) -> discord.Embed:
        e = discord.Embed(
            title="🦈 PolkaSharks 指令表",
            description="斜線指令打 `/` 會跳選單;也可在頻道直接打字。`!cmd` 隨時叫出這張表。",
            color=_COLORS["status"],
        )
        e.add_field(name="💬 問答", value=(
            "`/ask <問題>` — 問本地 Claude Code(唯讀讀 $hark)\n"
            "例:`/ask 現在 regime 跟 posture 是什麼`\n"
            "在 **#問claude** 直接打字 = /ask\n"
            "`/llm <後端> <問題> [model]` — claude / local / wiki / codex\n"
            "例:`/llm wiki BBU 是什麼` · `/llm local 大盤怎麼看 model:qwen2.5:7b`\n"
            "`/models` — 列出本地 Ollama 模型"), inline=False)
        e.add_field(name="🤖 人格", value=(
            "`/persona <名> <訊息>` 例:`/persona huang CoWoS 還能追嗎`\n"
            "在 **#分析師議會** 打 `huang: 你的問題`(預設 sharks)\n"
            "`/personas` — 列出全部人格"), inline=False)
        e.add_field(name="🗳️ 議會 / 會議", value=(
            "`/council <主題>` — 交叉辯論:開場→互相質詢→答辯→投票→正反方數據(本地)\n"
            "例:`/council 今晚美股該偏多還偏空`\n"
            "`/meeting <morning|noon|evening|weekly>` — 手動開會\n"
            "`/chatter [council:1]` — 立刻產一則 #雜談 速解讀(免費新聞→本地;每小時自動)\n"
            "`/picks` — 最近一次選股 / 訊號\n"
            "`/feedback [perf]` — 換股節流(績效強不換股+深挖支撐;真反轉才換)\n"
            "`/dipbuy [software|crypto|all]` — 抄底起漲篩選(距高+盈利+起漲)\n"
            "`/optimize [universe|tickers] [cap] [solver]` — GPU Mean-CVaR 最佳權重(cuFOLIO/RTX 5070)"),
            inline=False)
        e.add_field(name="📣 自媒體", value=(
            "`/content <x|blog|youtube|all> [主題]` — 產草稿到 #自媒體(不代發)\n"
            "例:`/content all 今日半導體` · `/content x AI 泡沫`"), inline=False)
        e.add_field(name="📓 筆記本 / 知識庫(本地 NotebookLM)", value=(
            "`/notebook <問題>` — 用本地 qwen 讀整個 $hark 回答(附出處);或在 **#筆記本** 直接打字\n"
            "`/ingest <文字或網址> [標題]` — 把知識灌進 $hark;或在 **#知識注入** 直接貼(手機也行)\n"
            "`/wikisearch <關鍵字>` 直接找片段 · `/recent` 看最近灌入"), inline=False)
        e.add_field(name="🖼️ 截圖判讀(本地 vision · 私密)", value=(
            "`/portfolio <圖>` — 判讀投組截圖:持倉抽取 + 集中/槓桿風險讀數\n"
            "`/factcheck <圖>` — 查核貼文/損益截圖:可查核 vs 紅旗(報酬異常/拉群/截圖非證據)\n"
            "或直接把圖丟進 **#截圖評估** / **#查核**"), inline=False)
        e.add_field(name="🔗 卡脖子(供應鏈瓶頸)", value=(
            "`/chokepoint <主題>` — 拆瓶頸 → 握瓶頸的公司 → 你的 FOM 評分\n"
            "例:`/chokepoint AI 工廠` · `/chokepoint CPO 矽光子` · `/chokepoint 液冷`"), inline=False)
        e.add_field(name="⚙️ 其他", value="`/status` · `!cmd` / `!help` 這張表", inline=False)
        e.set_footer(text="只建議不下單 · 議會/人格跑本地 · /ask 唯讀")
        return e

    async def _persona_say(self, channel: discord.abc.Messageable,
                           persona: ChatPersona, text: str) -> None:
        """Speak as a persona via webhook (own name); fall back to a plain message."""
        try:
            if isinstance(channel, discord.TextChannel):
                whs = await channel.webhooks()
                wh = discord.utils.get(whs, name="sharks-persona") or \
                    await channel.create_webhook(name="sharks-persona")
                for c in _chunks(text):
                    await wh.send(content=c, username=persona.reply_name())
                return
        except (discord.Forbidden, discord.HTTPException):
            pass
        for c in _chunks(f"**{persona.reply_name()}**\n{text}"):
            await channel.send(c)

    # ── slash commands ────────────────────────────────────────────────────────
    def _register_commands(self) -> None:
        tree, settings = self.tree, self.settings

        @tree.command(name="ask", description="問本地 Claude Code(唯讀,讀得到整個 $hark)")
        @app_commands.describe(question="你的問題")
        async def ask(interaction: discord.Interaction, question: str):
            await interaction.response.defer(thinking=True)
            rep = await asyncio.to_thread(ask_claude_research, question, settings)
            head = f"💬 **{question}**\n"
            tail = f"\n\n_— Claude Code · ${rep.cost_usd or 0:.3f}_" if rep.ok else ""
            await self._send_followup(interaction, head + rep.display(1700) + tail)

        @tree.command(name="persona", description="找一位分析師人格聊聊(本地 Nemotron)")
        @app_commands.describe(name="人格名稱(/personas 看清單)", message="你想問的")
        async def persona_cmd(interaction: discord.Interaction, name: str, message: str):
            p = self.personas.get(name.lower())
            if not p:
                await interaction.response.send_message(
                    f"找不到人格 `{name}`。可用:{', '.join(sorted(self.personas))}",
                    ephemeral=True)
                return
            await interaction.response.defer(thinking=True)
            rep = await asyncio.to_thread(ask_persona, p, message, settings)
            await self._send_followup(interaction,
                                      f"**{p.reply_name()}**\n{rep.display(1700)}")

        @tree.command(name="personas", description="列出可用的分析師人格")
        async def personas_cmd(interaction: discord.Interaction):
            lines = [f"- `{n}` — {p.title}" for n, p in sorted(self.personas.items())]
            await interaction.response.send_message(
                "可用人格:\n" + "\n".join(lines), ephemeral=True)

        @tree.command(name="picks", description="貼出最近一次 FOM 選股 / 每日訊號")
        async def picks_cmd(interaction: discord.Interaction):
            await interaction.response.defer(thinking=True)
            digest = compose_evening(settings, datetime.now(TPE))
            await interaction.followup.send(embeds=digest_to_embeds(digest))

        @tree.command(name="meeting", description="手動開一場會(morning/noon/evening/weekly)")
        @app_commands.describe(kind="morning / noon / evening / weekly")
        async def meeting_cmd(interaction: discord.Interaction, kind: str):
            kind = kind.lower().strip()
            if kind not in ("morning", "noon", "evening", "weekly"):
                await interaction.response.send_message(
                    "kind 需為 morning / noon / evening / weekly", ephemeral=True)
                return
            await interaction.response.defer(thinking=True)
            await self.post_meeting(kind, interaction=interaction)

        @tree.command(name="council", description="議會交叉辯論(開場→互相質詢→答辯→投票→正反方→結論)")
        @app_commands.describe(topic="要辯論的主題")
        async def council_cmd(interaction: discord.Interaction, topic: str):
            await interaction.response.defer(thinking=True)
            digest = compose_evening(settings, datetime.now(TPE))
            base = digest_to_brief(digest)
            result = await asyncio.to_thread(
                lambda: run_council_local(
                    topic, _brief_with_news(base, 6),
                    model=settings.effective_council_model(),
                    council_names=tuple(settings.council_personas),
                    chair_name=settings.council_chair,
                    council_models=tuple(settings.council_models),
                    personas=self.personas, settings=settings,
                ))
            if not result.votes:
                await interaction.followup.send(f"議會無法召開:{result.note or '人格載入失敗'}")
                return
            await interaction.followup.send(embeds=council_to_embeds(result))

        @tree.command(name="content",
                      description="生成自媒體草稿(x/blog/youtube)→ 只產草稿,不自動發佈")
        @app_commands.describe(kind="x / blog / youtube / all", topic="主題(可省略,預設用今日結論)")
        async def content_cmd(interaction: discord.Interaction, kind: str = "all", topic: str = ""):
            kind = (kind or "all").lower().strip()
            kinds = ["x", "blog", "youtube"] if kind in ("all", "") else [kind]
            if any(k not in ("x", "blog", "youtube") for k in kinds):
                await interaction.response.send_message(
                    "kind 需為 x / blog / youtube / all", ephemeral=True)
                return
            await interaction.response.defer(thinking=True)
            topic = topic.strip() or "今日市場觀察與選股"
            brief = digest_to_brief(compose_evening(settings, datetime.now(TPE)))
            draft = await asyncio.to_thread(
                run_content_local, kinds, topic, brief,
                model=settings.effective_council_model())
            sections = draft.as_sections()
            if not sections:
                await interaction.followup.send("草稿生成失敗(本地模型無回應)。")
                return
            await interaction.followup.send(
                f"📣 **自媒體草稿 · {topic}** _(草稿,請自行檢視後再發佈;bot 不會代發)_ "
                f"— 本地 {draft.model}")
            for head, body in sections:
                for chunk in _chunks(f"**{head}**\n{body}"):
                    await interaction.followup.send(chunk)

        @tree.command(name="llm", description="問任一資源後端:claude / local / wiki / codex")
        @app_commands.describe(backend="後端", question="你的問題", model="(local 用)模型名,可省略")
        @app_commands.choices(backend=[
            app_commands.Choice(name="claude — Claude Code 唯讀讀 $hark", value="claude"),
            app_commands.Choice(name="local — 本地 Ollama 模型(GPU)", value="local"),
            app_commands.Choice(name="wiki — 本地 LLM-wiki RAG", value="wiki"),
            app_commands.Choice(name="codex — OpenAI Codex CLI", value="codex"),
        ])
        async def llm_cmd(interaction: discord.Interaction,
                          backend: app_commands.Choice[str], question: str, model: str = ""):
            await interaction.response.defer(thinking=True)
            rep = await asyncio.to_thread(ask_backend, backend.value, question, settings, model)
            mtag = f"·{model}" if (model and backend.value == "local") else ""
            tail = f"\n\n_— {rep.backend} {rep.model or ''}_" if rep.ok else ""
            await self._send_followup(
                interaction, f"[{backend.value}{mtag}] **{question}**\n{rep.display(1600)}{tail}")

        @tree.command(name="models", description="列出本地 Ollama 可用模型")
        async def models_cmd(interaction: discord.Interaction):
            models = await asyncio.to_thread(list_ollama_models)
            body = "\n".join(f"- `{m}`" for m in models) if models else "(Ollama 未啟動或無模型)"
            await interaction.response.send_message("本地 Ollama 模型:\n" + body, ephemeral=True)

        @tree.command(name="status", description="bot 狀態與設定")
        async def status_cmd(interaction: discord.Interaction):
            await interaction.response.send_message(embed=self._status_embed("狀態"),
                                                    ephemeral=True)

        @tree.command(name="chatter",
                      description="立刻產一則 #雜談 速解讀(免費新聞→本地 LLM 因果鏈);council:1 同時開議會")
        @app_commands.describe(council="是否同時召開議會辯論(預設否)")
        async def chatter_cmd(interaction: discord.Interaction, council: bool = False):
            await interaction.response.defer(thinking=True, ephemeral=True)
            await self.post_chatter(run_council=council)
            tgt = "#雜談" if self._channel(C.CH_GENERAL) else "#bot-狀態"
            await interaction.followup.send(f"✅ 已貼到 {tgt}" + ("(含議會)" if council else ""),
                                            ephemeral=True)

        # ── 本地 NotebookLM:讀 $hark 回答 + 灌入知識 ──────────────────────────
        @tree.command(name="notebook",
                      description="像 NotebookLM:用本地 qwen 讀整個 $hark 回答你的問題(附出處)")
        @app_commands.describe(question="你的問題")
        async def notebook_cmd(interaction: discord.Interaction, question: str):
            await interaction.response.defer(thinking=True)
            rep = await asyncio.to_thread(ask_wiki, question, settings)
            await self._send_followup(interaction, f"📓 **{question}**\n{rep.display(1700)}")

        @tree.command(name="ingest",
                      description="把知識灌進 $hark wiki(貼文字或網址)→ 立刻可被 /notebook 搜到")
        @app_commands.describe(content="要灌入的文字或網址", title="標題(可省略)")
        async def ingest_cmd(interaction: discord.Interaction, content: str, title: str = ""):
            await interaction.response.defer(thinking=True, ephemeral=True)
            res = await asyncio.to_thread(
                wiki_ingest.ingest, content, title=(title or None),
                source="discord-slash", settings=settings)
            if not res.get("ok"):
                await interaction.followup.send(f"灌入失敗:{res.get('error')}", ephemeral=True)
                return
            u = f"\n網址:{res['url']}" if res.get("url") else ""
            await interaction.followup.send(
                f"✅ 已寫入 `{res['path']}`(標題:{res['title']},{res['chars']} 字){u}\n"
                f"現在就能用 `/notebook` 或 #筆記本 問它。", ephemeral=True)

        @tree.command(name="wikisearch", description="不經 LLM,直接在 $hark 找相關片段(快)")
        @app_commands.describe(query="關鍵字 / ticker / 概念")
        async def wikisearch_cmd(interaction: discord.Interaction, query: str):
            await interaction.response.defer(thinking=True)
            hits = await asyncio.to_thread(wiki_rag.search, query, settings.project_root, 6)
            if not hits:
                await interaction.followup.send("找不到相關片段。")
                return
            lines = [f"**{h.path}** (score {h.score})\n{h.text[:240]}…" for h in hits]
            await self._send_followup(interaction, f"🔎 **{query}**\n\n" + "\n\n".join(lines))

        @tree.command(name="recent", description="列出最近灌入 $hark 的知識筆記")
        async def recent_cmd(interaction: discord.Interaction):
            paths = await asyncio.to_thread(wiki_ingest.recent, settings, 12)
            body = "\n".join(f"- `{p}`" for p in paths) if paths else "(還沒有灌入任何筆記)"
            await interaction.response.send_message("最近的知識注入:\n" + body, ephemeral=True)

        @tree.command(name="feedback",
                      description="換股節流:績效強→不換股+深挖支撐;真反轉→才換股")
        @app_commands.describe(perf="你的投組績效(可省略 → 用持倉強度推估)")
        @app_commands.choices(perf=[
            app_commands.Choice(name="非常好 → 續抱、深挖支撐", value="great"),
            app_commands.Choice(name="普通", value="ok"),
            app_commands.Choice(name="差", value="bad"),
        ])
        async def feedback_cmd(interaction: discord.Interaction,
                               perf: Optional[app_commands.Choice[str]] = None):
            await interaction.response.defer(thinking=True)
            rep = await asyncio.to_thread(
                compose_feedback, settings.outputs_dir, perf.value if perf else None)
            await interaction.followup.send(embed=feedback_to_embed(rep))

        @tree.command(name="dipbuy",
                      description="抄底起漲篩選(距高+盈利+起漲):H2-2026 頂底互換名單")
        @app_commands.describe(which="software / crypto / all")
        @app_commands.choices(which=[
            app_commands.Choice(name="軟體/AI 抄底名單", value="software"),
            app_commands.Choice(name="加密/fintech 觀察", value="crypto"),
            app_commands.Choice(name="全部", value="all"),
        ])
        async def dipbuy_cmd(interaction: discord.Interaction,
                             which: Optional[app_commands.Choice[str]] = None):
            await interaction.response.defer(thinking=True)   # yfinance fetch ~10-20s
            title, rows = await asyncio.to_thread(
                run_dipbuy, which.value if which else "software", settings=settings)
            await interaction.followup.send(embed=dipbuy_to_embed(title, rows))

        @tree.command(name="optimize",
                      description="GPU Mean-CVaR 最佳權重(cuFOLIO/cuOpt on RTX 5070;只建議)")
        @app_commands.describe(
            universe="預設名單;給 tickers 則覆蓋",
            tickers="自訂標的,逗號或空白分隔",
            cap="單檔權重上限 0.05–1.0(預設 0.25)",
            solver="cuopt=GPU(預設)/ clarabel=CPU")
        @app_commands.choices(
            universe=[
                app_commands.Choice(name="軟體/AI 抄底名單", value="software"),
                app_commands.Choice(name="加密/fintech 觀察", value="crypto"),
                app_commands.Choice(name="大型科技權值", value="megacap"),
            ],
            solver=[
                app_commands.Choice(name="GPU cuOpt(RTX 5070)", value="cuopt"),
                app_commands.Choice(name="CPU CLARABEL", value="clarabel"),
            ])
        async def optimize_cmd(interaction: discord.Interaction,
                               universe: Optional[app_commands.Choice[str]] = None,
                               tickers: Optional[str] = None,
                               cap: Optional[float] = None,
                               solver: Optional[app_commands.Choice[str]] = None):
            await interaction.response.defer(thinking=True)   # yfinance + GPU ~15-40s
            uni = universe.value if universe else "software"
            slv = solver.value if solver else "cuopt"
            wmax = max(0.05, min(1.0, cap if cap else 0.25))
            syms, label = _resolve_universe(uni, tickers)
            if len(syms) < 2:
                await interaction.followup.send("⚠️ 需要至少 2 檔有效標的(逗號分隔)")
                return
            res = await asyncio.to_thread(
                cufolio_optimize, syms, solver=slv, w_max=wmax, num_scen=3000)
            await interaction.followup.send(embed=optimize_to_embed(res, label, slv))

        # ── 截圖判讀(本地 vision · 私密不外傳)──────────────────────────────────
        @tree.command(name="portfolio",
                      description="判讀投組截圖:持倉抽取+集中/槓桿風險讀數(本地 vision,私密)")
        @app_commands.describe(image="投組/持倉截圖")
        async def portfolio_cmd(interaction: discord.Interaction, image: discord.Attachment):
            if not (image.content_type or "").startswith("image/"):
                await interaction.response.send_message("請附一張圖片。", ephemeral=True)
                return
            await interaction.response.defer(thinking=True)
            data = await image.read()
            res = await asyncio.to_thread(vision.eval_portfolio_image, data, settings)
            await self._send_followup(interaction, res.message if res.ok else f"⚠️ {res.error}")

        @tree.command(name="factcheck",
                      description="查核貼文/損益截圖:紅旗 + FOM實際數據對照(deep=web 深查)")
        @app_commands.describe(image="要查核的截圖", deep="深度 web 查核(Claude+WebSearch,較慢)")
        async def factcheck_cmd(interaction: discord.Interaction, image: discord.Attachment,
                                deep: bool = False):
            if not (image.content_type or "").startswith("image/"):
                await interaction.response.send_message("請附一張圖片。", ephemeral=True)
                return
            await interaction.response.defer(thinking=True)
            data = await image.read()
            res = await asyncio.to_thread(vision.factcheck_image, data, settings, deep_web=deep)
            await self._send_followup(interaction, res.message if res.ok else f"⚠️ {res.error}")

        @tree.command(name="chokepoint",
                      description="卡脖子分析:供應鏈瓶頸 → 握瓶頸的公司 → 你的 FOM 評分")
        @app_commands.describe(topic="主題/終端系統,例:AI 工廠 · HBM · CPO 矽光子 · 液冷 · RF 前端")
        async def chokepoint_cmd(interaction: discord.Interaction, topic: str):
            await interaction.response.defer(thinking=True)   # yfinance fetch ~15-30s
            res = await asyncio.to_thread(chokepoint.analyze, topic, settings)
            if not res["lanes"]:
                await interaction.followup.send(
                    "沒有對應的 lane,且本地 LLM 未提名標的。試試:AI 工廠 / HBM / CPO / 液冷 / RF 前端。")
                return
            await interaction.followup.send(embed=chokepoint_to_embed(res))

        # screens/finviz layer (basecross/rally/stealth/ecomrank/finviz/guide/playbook)
        from sharks.discord import screen_commands
        screen_commands.register(tree, settings)

    async def _send_followup(self, interaction: discord.Interaction, text: str) -> None:
        parts = _chunks(text)
        await interaction.followup.send(parts[0])
        for p in parts[1:]:
            await interaction.followup.send(p)

    # ── message routing (#分析師議會 + #問claude) ─────────────────────────────
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return
        ch_name = getattr(message.channel, "name", "")
        content = (message.content or "").strip()

        # 截圖判讀:an image dropped in 截圖評估/查核 → local vision analysis.
        if message.attachments and ch_name in (C.CH_SHOTEVAL, C.CH_FACTCHECK):
            imgs = [a for a in message.attachments
                    if (a.content_type or "").startswith("image/")]
            if imgs:
                fn = (vision.eval_portfolio_image if ch_name == C.CH_SHOTEVAL
                      else vision.factcheck_image)
                async with message.channel.typing():
                    data = await imgs[0].read()
                    res = await asyncio.to_thread(fn, data, self.settings)
                for c in _chunks(res.message if res.ok else f"⚠️ {res.error}"):
                    await message.channel.send(c)
                return

        if not content:
            return

        # !cmd / !help — cheat-sheet, works in ANY channel.
        if content.lower() in ("!cmd", "!cmds", "!help", "!commands", "!指令"):
            await message.channel.send(embed=self._help_embed())
            return

        if ch_name == C.CH_COUNCIL:
            persona, q = resolve_persona(content, self.personas, self.settings.default_persona)
            if persona is None:
                await message.channel.send("沒有可用人格;檢查 analysts/ 目錄。")
                return
            async with message.channel.typing():
                rep = await asyncio.to_thread(ask_persona, persona, q or content, self.settings)
            await self._persona_say(message.channel, persona, rep.display(1700))

        elif ch_name == C.CH_ASK:
            async with message.channel.typing():
                rep = await asyncio.to_thread(ask_claude_research, content, self.settings)
            tail = f"\n\n_— Claude Code · ${rep.cost_usd or 0:.3f}_" if rep.ok else ""
            for c in _chunks(rep.display(1800) + tail):
                await message.channel.send(c)

        elif ch_name == C.CH_NOTEBOOK:
            # local NotebookLM: qwen reads $hark and answers with citations.
            async with message.channel.typing():
                rep = await asyncio.to_thread(ask_wiki, content, self.settings)
            for c in _chunks(f"📓 {rep.display(1800)}"):
                await message.channel.send(c)

        elif ch_name == C.CH_INGEST:
            # paste text / URL → write a note into $hark wiki/inbox.
            async with message.channel.typing():
                res = await asyncio.to_thread(
                    wiki_ingest.ingest, content, source="discord-channel", settings=self.settings)
            if res.get("ok"):
                u = f" · {res['url']}" if res.get("url") else ""
                await message.channel.send(
                    f"✅ 已灌入 `{res['path']}`(標題:{res['title']},{res['chars']} 字){u}\n"
                    f"→ 可用 **#筆記本** 或 `/notebook` 問它。")
            else:
                await message.channel.send(f"灌入失敗:{res.get('error')}")

    # ── privacy: alert (do NOT auto-kick) on unexpected member ────────────────
    async def on_member_join(self, member: discord.Member) -> None:
        ch = self._channel(C.CH_STATUS)
        if ch:
            await ch.send(
                f"⚠️ 有新成員加入:**{member}** (`{member.id}`)。"
                "這是私人雙人伺服器 — 若非預期,請到 伺服器設定→邀請 撤銷所有邀請連結,"
                "並移除該成員。(bot 不會自動踢人。)")

    # ── scheduler ─────────────────────────────────────────────────────────────
    @tasks.loop(seconds=30)
    async def scheduler(self):  # pragma: no cover - timing loop
        await self._tick()

    @scheduler.before_loop
    async def _before_scheduler(self):  # pragma: no cover - waits for gateway
        await self.wait_until_ready()

    async def _tick(self) -> None:
        s = self.settings
        now = datetime.now(TPE)
        hhmm, today = now.strftime("%H:%M"), now.date().isoformat()

        # Hourly #雜談 chatter (news → 速解讀) + a council every Nth hour.
        # Independent of meetings_enabled; fires once at the top of each hour.
        if s.chatter_enabled and now.minute == 0:
            slot = now.strftime("%Y-%m-%d-%H")
            if self._last_fired.get("chatter") != slot:
                self._last_fired["chatter"] = slot
                self._chatter_count += 1
                do_council = (s.chatter_council_every > 0
                              and self._chatter_count % s.chatter_council_every == 0)
                try:
                    await self.post_chatter(run_council=do_council)
                except Exception as exc:  # pragma: no cover - network/LLM
                    log.warning("chatter tick failed: %s", exc)

        if not s.meetings_enabled:
            return
        if hhmm == s.morning_hhmm and self._last_fired.get("morning") != today:
            self._last_fired["morning"] = today
            await self.post_meeting("morning")
        if hhmm == s.noon_hhmm and self._last_fired.get("noon") != today:
            self._last_fired["noon"] = today
            await self.post_meeting("noon")
        if hhmm == s.evening_hhmm and self._last_fired.get("evening") != today:
            self._last_fired["evening"] = today
            await self.post_meeting("evening")

    # ── meeting posting ───────────────────────────────────────────────────────
    _TOPICS = {
        "morning": "今天美股盤前 / 台亞洲開盤,整體該偏多還偏空?要追半導體嗎?",
        "noon": "盤中該加碼、減碼還是續抱?有沒有要調整的部位?",
        "evening": "今晚美股開盤前,整體傾向與最該盯的風險是什麼?",
        "weekly": "本週整體配置傾向與再平衡重點?",
    }
    _CH = {"morning": C.CH_MORNING, "noon": C.CH_NOON,
           "evening": C.CH_EVENING, "weekly": C.CH_MORNING}

    async def post_meeting(self, kind: str,
                           interaction: Optional[discord.Interaction] = None) -> None:
        s = self.settings
        if s.meeting_refresh:
            await self._refresh_outputs()
        now = datetime.now(TPE)
        composer = {"morning": compose_morning, "noon": compose_noon,
                    "evening": compose_evening, "weekly": compose_weekly}[kind]
        digest = composer(s, now)
        ch_name = self._CH.get(kind, C.CH_MORNING)

        # 1) data digest (+ optional Claude macro narrative)
        narrative = None
        if s.meeting_research and s.backend != "local":
            rep = await asyncio.to_thread(ask_claude_research, research_prompt(kind), s)
            narrative = rep.text if rep.ok else None
        embeds = digest_to_embeds(digest, narrative)

        # 2) local council debate -> 議會結論 (runs on the local model)
        if s.council_enabled:
            council = await asyncio.to_thread(
                run_council_local, self._TOPICS.get(kind, "今天的整體傾向?"),
                digest_to_brief(digest),
                model=s.effective_council_model(),
                council_names=tuple(s.council_personas),
                chair_name=s.council_chair,
                council_models=tuple(s.council_models),
                personas=self.personas, settings=s,
            )
            if council.votes:
                embeds.extend(council_to_embeds(council))

        # 4) performance-feedback rotation throttle (pure/local, no cost)
        if s.feedback_in_meetings:
            fb = await asyncio.to_thread(compose_feedback, s.outputs_dir, None)
            embeds.append(feedback_to_embed(fb))

        if interaction is not None:
            for e in embeds:
                await interaction.followup.send(embed=e)
            return
        channel = self._channel(ch_name) or self._channel(C.CH_STATUS)
        if not channel:
            log.warning("meeting %s: channel %s not found", kind, ch_name)
            return
        for e in embeds:
            await channel.send(embed=e)

    async def _refresh_outputs(self) -> None:
        """Run `sharks health-check` to refresh outputs/ before a meeting."""
        try:
            await asyncio.to_thread(
                subprocess.run,
                [sys.executable, "-m", "sharks.cli", "health-check"],
                cwd=str(self.settings.project_root),
                capture_output=True, text=True, timeout=180,
            )
        except Exception as exc:  # never let a refresh failure block the meeting
            log.warning("health-check refresh failed: %s", exc)

    # ── hourly #雜談 chatter ──────────────────────────────────────────────────
    async def post_chatter(self, run_council: bool = False) -> None:
        """#雜談: free-RSS news → 速解讀 因果鏈 (local LLM); every Nth also a council."""
        s = self.settings
        ch = self._channel(C.CH_GENERAL) or self._channel(C.CH_STATUS)
        if not ch:
            log.warning("chatter: #%s not found", C.CH_GENERAL)
            return
        from sharks.discord import chatter
        data = await asyncio.to_thread(
            chatter.compose_chatter, s.effective_council_model(), s.chatter_news_n)
        e = discord.Embed(
            title="📰 每小時速解讀(本地)",
            description=(data["take"] or "(本地模型無回應 — 確認 Ollama 已啟動)")[:4096],
            color=_COLORS["noon"],
        )
        if data["headlines"]:
            e.add_field(name="頭條來源", value="、".join(data["sources_ok"][:6]) or "—", inline=False)
            e.add_field(name="頭條",
                        value="\n".join(f"• {h}" for h in data["headlines"][:6])[:1024], inline=False)
        e.set_footer(text=f"本地 {data.get('backend', '?')} · 免費 RSS · 僅研究非建議,永不下單")
        await ch.send(embed=e)

        if run_council and s.council_enabled and data["headlines"]:
            from sharks.discord.chatter import council_topic_from_news
            topic, brief = council_topic_from_news(data["headlines"])
            result = await asyncio.to_thread(
                run_council_local, topic, brief,
                model=s.effective_council_model(),
                council_names=tuple(s.council_personas),
                chair_name=s.council_chair,
                council_models=tuple(s.council_models),
                personas=self.personas, settings=s,
            )
            if result.votes:
                await ch.send(embeds=council_to_embeds(result))


def main(argv: Optional[list[str]] = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="sharks.discord.bot")
    ap.add_argument("--run-meeting", choices=["morning", "noon", "evening", "weekly", "all"],
                    default=None, help="post the meeting(s) once and exit (no listener)")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = Settings.load()
    problems = settings.missing()
    if problems:
        print("無法啟動 — 設定問題:")
        for p in problems:
            print(f"  • {p}")
        return 1
    run_once = None
    if args.run_meeting:
        run_once = (["morning", "noon", "evening"] if args.run_meeting == "all"
                    else [args.run_meeting])
    bot = SharksBot(settings, run_once=run_once)
    bot.run(settings.token, log_handler=None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
