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
from sharks.discord import wiki_ingest, wiki_rag
from sharks.discord.config import TPE, Settings
from sharks.discord.content import run_content_local
from sharks.discord.council import CouncilResult, run_council_local
from sharks.discord.feedback import FeedbackReport, compose_feedback
from sharks.discord.dipbuy import DipCandidate, run_dipbuy
from sharks.discord.basecross import BaseCrossCandidate, run_basecross
from sharks.discord import basecross as _basecross
from sharks.scoring import rally_signal as _rally
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

# /rescan job sets — (label, `python -m` args, timeout_s). Run in project_root so
# each module writes outputs/<…>-<date>.json that /picks then reposts. FOM is the
# real 選股 (full-universe scan, can be slow); health = 持倉 + 姿態 refresh.
_SCAN_SETS: dict[str, list[tuple[str, list[str], int]]] = {
    "fom": [("選股 · FOM 全宇宙掃描", ["sharks.scoring.fom"], 600)],
    "signals": [("籌碼 FSM 掃描 (state)", ["sharks.scoring.chip_flow_fsm"], 300),
                ("每日 10-訊號編譯 (picks)", ["sharks.daily_picks"], 120)],
    "health": [("持倉健檢 (portfolio audit)", ["sharks.backtest.portfolio_audit"], 240),
               ("姿態健檢 (regime + posture)", ["sharks.cli", "health-check"], 180)],
}
# all = 選股 + 每日訊號 + 健檢 (signals must follow its own FSM step, so order matters)
_SCAN_SETS["all"] = _SCAN_SETS["fom"] + _SCAN_SETS["signals"] + _SCAN_SETS["health"]


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


def council_to_embed(r: CouncilResult) -> discord.Embed:
    """Render a council debate (vote tally + chair conclusion) as one embed."""
    lean = r.lean()
    e = discord.Embed(
        title=f"🗳️ 議會結論 · 傾向 {_VOTE_EMOJI.get(lean, '')} {lean}",
        description=(r.conclusion or "—")[:4096],
        color=_COLORS["council"],
    )
    t = r.tally or {}
    e.add_field(
        name="投票",
        value=(f"🟢 多 {t.get('多', 0)} · 🔴 空 {t.get('空', 0)} · "
               f"⚪ 中性 {t.get('中性', 0)} · 平均信心 {t.get('avg_conviction', '?')}/5"),
        inline=False,
    )
    lines = [
        f"{_VOTE_EMOJI.get(v.vote, '')} **{v.title}** `{v.model}` 信心{v.conviction} · {v.action or '—'}"
        for v in r.votes
    ]
    if lines:
        e.add_field(name="各人投票(模型)", value="\n".join(lines)[:1024], inline=False)
    models_used = ", ".join(sorted({v.model for v in r.votes if v.model}))
    e.set_footer(text=f"本地多模型議會(立場→交叉質詢→投票)· {models_used} · "
                      f"結論回寫 wiki 記憶 · 僅研究非建議,永不下單"[:2048])
    return e


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


def basecross_to_embed(title: str, rows: list[BaseCrossCandidate]) -> discord.Embed:
    """Render the 月線底部金叉 + 資金介入 screen (Boeing/Snowflake 大底形態)."""
    e = discord.Embed(
        title=f"📈 月線大底金叉 · {title}",
        description="題材(2022殺/AI錯殺軟體)+ 月線底部金叉 + 資金介入。找 Boeing/Snowflake 那種大底翻揚。",
        color=0x8E44AD,
    )
    green = [c for c in rows if c.verdict.startswith("🟢")]
    yellow = [c for c in rows if c.verdict.startswith("🟡")]
    blue = [c for c in rows if c.verdict.startswith("🔵")]
    def line(c: BaseCrossCandidate) -> str:
        if c.last is None:
            return f"`{c.ticker}` — {c.note}"
        th = f" [{c.theme}]" if c.theme else ""
        vs = f" · 量×{c.vol_surge:.1f}" if c.vol_surge else ""
        return f"`{c.ticker}`{th} 距高 {c.dist_ath_pct:.0f}%{vs}"
    if green:
        e.add_field(name="🟢 金叉+資金(主力候選)", value="\n".join(line(c) for c in green)[:1024], inline=False)
    if yellow:
        e.add_field(name="🟡 金叉或量能,待另一半確認", value="\n".join(line(c) for c in yellow)[:1024], inline=False)
    if blue:
        e.add_field(name="🔵 築底中 · 待金叉", value="\n".join(line(c) for c in blue[:12])[:1024], inline=False)
    e.set_footer(text="recommend-only · 月線=日線重抽樣近似 · 距高/量能即時算,盈利 q 需 FOM 宇宙覆蓋")
    return e


def rally_to_embed(title: str, signals: list) -> discord.Embed:
    """Render the 起漲訊號 tracker (5維融合 + 連續起漲 → 可考慮買入)."""
    e = discord.Embed(
        title=f"🚀 起漲訊號追蹤 · {title}",
        description="融合 資金/技術/消息/供應鏈/基本面;**連續起漲**才『可考慮買入』。"
                    "對齊 2020–26 暴漲股 DNA(INTC/MU/NVDA/TSLA…)。",
        color=0xE74C3C,
    )
    def dimstr(s) -> str:
        return " ".join(f"{_rally.DIM_ZH[d]}{int(s.dims[d])}" if s.dims.get(d) is not None
                        else f"{_rally.DIM_ZH[d]}–" for d in _rally.DIMENSIONS)
    def line(s) -> str:
        return (f"`{s.ticker}` C{s.composite:.0f}/DNA{s.dna_match:.0f} 連{s.streak} · "
                f"{dimstr(s)}")
    buy = [s for s in signals if s.buy_consider]
    rising = [s for s in signals if s.is_rallying and not s.buy_consider]
    grave = [s for s in signals if s.warning]
    coil = [s for s in signals if not s.is_rallying and not s.warning and s.composite >= 45]
    if buy:
        e.add_field(name="🟢 連續起漲 · 可考慮買入(分批/小倉)",
                    value="\n".join(line(s) for s in buy)[:1024], inline=False)
    if rising:
        e.add_field(name="🟡 起漲中(觀察,未達連續門檻)",
                    value="\n".join(line(s) for s in rising[:10])[:1024], inline=False)
    if coil:
        e.add_field(name="🔵 蓄勢(尚未起漲)",
                    value="\n".join(line(s) for s in coil[:8])[:1024], inline=False)
    if grave:
        e.add_field(name="🚫 純炒作·無實證(墓園型 — 不追)",
                    value="\n".join(f"`{s.ticker}` {s.warning[:60]}" for s in grave[:6])[:1024],
                    inline=False)
    e.set_footer(text="recommend-only · 連續起漲才考慮 · 墓園型一律不追 · 進場仍配 regime/資金面健檢")
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
        # NOTE: do NOT sync here — setup_hook runs before the gateway connects, so
        # self.guilds is empty and a guild sync silently degrades to a *global*
        # sync (up to ~1h to show new commands). We sync in on_ready instead, where
        # the guild is known → instant. Wrapped so a sync hiccup can't crash startup.
        try:
            self.scheduler.start()
        except Exception as exc:  # never let the scheduler take the bot down
            log.exception("scheduler failed to start: %s", exc)

    async def _sync_commands(self) -> None:
        """Sync the slash-command tree once, to the guild (instant) if known."""
        if getattr(self, "_synced", False):
            return
        try:
            guild = self._guild()
            if guild:
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)   # instant in one guild
                log.info("synced %d slash commands to guild %s", len(synced), guild.id)
            else:
                synced = await self.tree.sync()              # global: ~1h to propagate
                log.warning("no guild in cache — synced %d commands GLOBALLY "
                            "(can take ~1h to appear)", len(synced))
            self._synced = True
        except Exception as exc:  # a sync failure must not break the live bot
            log.exception("slash-command sync failed: %s", exc)

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
        await self._sync_commands()      # now that the guild is in cache → instant
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
                           f"{s.effective_council_model()} · {'/'.join(s.council_personas)}\n"
                           f"交叉質詢 {'on' if s.council_cross_exam else 'off'} · "
                           f"記憶 {'on' if s.council_memory_enabled else 'off'} · "
                           f"回寫wiki {'on' if s.council_writeback else 'off'}"),
                    inline=False)
        e.add_field(name="雜談",
                    value=(f"{'on' if s.chatter_enabled else 'off'} · 每小時速解讀 → #{C.CH_GENERAL} · "
                           f"council 每 {s.chatter_council_every} 次"), inline=False)
        e.add_field(name="人格", value=", ".join(sorted(self.personas)) or "—", inline=False)
        ncmds = len(self.tree.get_commands())
        e.set_footer(text=f"code {self._git_rev()} · {ncmds} 指令 · recommend-only · 永不下單 · 議會/雜談跑本地")
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
            "`/council <主題>` — 多人格 立場→交叉質詢→投票→結論(本地;結論回寫 wiki 記憶)\n"
            "例:`/council 今晚美股該偏多還偏空`\n"
            "`/meeting <morning|noon|evening|weekly>` — 手動開會\n"
            "`/chatter [council:1]` — 立刻產一則 #雜談 速解讀(免費新聞→本地;每小時自動)\n"
            "`/picks` — 貼最近一次選股 / 訊號(不重跑,只貼快取)\n"
            "`/rescan [fom|signals|health|all]` — **重跑**選股/訊號/健檢掃描(本地)再貼最新\n"
            "`/feedback [perf]` — 換股節流(績效強不換股+深挖支撐;真反轉才換)\n"
            "`/dipbuy [software|crypto|all]` — 抄底起漲篩選(距高+盈利+起漲)\n"
            "`/basecross [killed2022|ai_software|all] [tickers:CRWD,VST]` — 月線底部金叉+資金介入(Boeing/Snowflake 大底)\n"
            "`/rally [killed2022|ai_software|ecommerce|all] [tickers:SHOP,SE]` — 起漲訊號追蹤(5維融合;連續起漲才可考慮買入)"), inline=False)
        e.add_field(name="📣 自媒體", value=(
            "`/content <x|blog|youtube|all> [主題]` — 產草稿到 #自媒體(不代發)\n"
            "例:`/content all 今日半導體` · `/content x AI 泡沫`"), inline=False)
        e.add_field(name="📓 筆記本 / 知識庫(本地 NotebookLM)", value=(
            "`/notebook <問題>` — 用本地 qwen 讀整個 $hark 回答(附出處);或在 **#筆記本** 直接打字\n"
            "`/ingest <文字或網址> [標題]` — 把知識灌進 $hark;或在 **#知識注入** 直接貼(手機也行)\n"
            "`/wikisearch <關鍵字>` 直接找片段 · `/recent` 看最近灌入"), inline=False)
        e.add_field(name="⚙️ 其他", value=(
            "`/status` 看狀態(含 code 版本)· `/cmd` 教學範例 · `!cmd` / `!help` 這張表\n"
            "`!sync` 重新同步斜線指令並列出本機實際擁有的指令(找不到新指令時用這個查)"), inline=False)
        e.set_footer(text="只建議不下單 · 議會/人格跑本地 · /ask 唯讀")
        return e

    def _tutorial_embed(self) -> discord.Embed:
        """A worked, step-by-step 教學範例 (distinct from the flat /help table).

        Each field is a 情境 → 指令 → 會發生什麼 walkthrough, headlined by the
        council closed loop so a new user can see the memory build up across runs."""
        e = discord.Embed(
            title="🎓 PolkaSharks 指令教學範例",
            description=("一步步帶你走一輪。每格是「**情境 → 指令 → 會發生什麼**」。\n"
                         "斜線指令直接打 `/`;前提:本地 Ollama 已啟動(`/models` 可驗)。"),
            color=_COLORS["council"],
        )
        e.add_field(name="① 召開議會(主打:一個指令跑完閉環)", value=(
            "**情境**:想知道今晚美股偏多偏空。\n"
            "**指令**:`/council 今晚美股該偏多還偏空`\n"
            "**會發生**:多人格 `立場 → 交叉質詢 → 投票 → 主席結論`,結果貼出投票統計+結論,"
            "並**自動回寫** `wiki/council/`。你什麼都不用多做。"), inline=False)
        e.add_field(name="② 再開一次 → 看「記憶」生效", value=(
            "**情境**:隔天同主題再問。\n"
            "**指令**:`/council 今晚美股該偏多還偏空`\n"
            "**會發生**:主席會說這次是**延續**還是**反轉**上次;每個人格被提醒「你上次投什麼」,"
            "要嘛延續、要嘛認錯修正 → 越開越有效率(記憶會累積,第一次跑是空白起步)。"), inline=False)
        e.add_field(name="③ 餵知識 → 讓議會更聰明", value=(
            "**情境**:看到一篇關鍵新聞/研究。\n"
            "**指令**:在 **#知識注入** 直接貼網址,或 `/ingest https://… CoWoS 產能`\n"
            "**會發生**:存進 `wiki/inbox/` 並立刻可被搜尋。**下一次 `/council`** 的主題 RAG 會把它"
            "(連同 `philosophy/` 底層邏輯)一起讀進去 → 本機+網路文檔一起推理。"), inline=False)
        e.add_field(name="④ 重跑一次選股", value=(
            "**情境**:想要最新一輪選股,而不是看上次快取。\n"
            "**指令**:`/rescan`(預設 `fom`)· `/rescan signals`(每日 10-訊號)· "
            "`/rescan all`(選股+訊號+健檢,較久)\n"
            "**會發生**:本地重跑掃描 → 寫進 `outputs/` → 直接貼出更新後的結果。"
            "FOM 全宇宙較久,跑完才會回貼;只想看上次就用 `/picks`(不重跑)。"), inline=False)
        e.add_field(name="⑤ 回讀結論 / 找片段", value=(
            "**指令**:`/notebook 最近議會對半導體的結論是什麼`(本地 qwen 讀整個 $hark,附出處)\n"
            "或 `/wikisearch 議會 半導體` 直接撈片段 · `/recent` 看最近灌入了什麼。"), inline=False)
        e.add_field(name="⑥ 單獨問一個人格", value=(
            "**指令**:`/persona huang CoWoS 還能追嗎`,或在 **#分析師議會** 打 `serenity: 總經怎麼看`。\n"
            "`/personas` 列出全部(議會預設席位:quant 四人 + huang/serenity/sam/yupupin/bear/momentum)。"), inline=False)
        e.add_field(name="想關掉某層?", value=(
            "全在 `.env`:`SHARKS_DISCORD_COUNCIL_CROSSEXAM=0`(關交叉質詢,改快速版)、"
            "`…_MEMORY=0`(不讀記憶)、`…_WRITEBACK=0`(不回寫)。`/status` 看目前開關。"), inline=False)
        e.set_footer(text="閉環:結論 → wiki → RAG → 下一場記憶 → 新結論 · 只建議不下單,永不下單")
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
            await self._send_followup(interaction, head + rep.display(redacted) + tail)

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
                                      f"**{p.reply_name()}**\n{rep.display(redacted)}")

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

        @tree.command(name="council", description="召開分析師議會辯論(本地模型:質疑→投票→結論)")
        @app_commands.describe(topic="要辯論的主題")
        async def council_cmd(interaction: discord.Interaction, topic: str):
            await interaction.response.defer(thinking=True)
            digest = compose_evening(settings, datetime.now(TPE))
            result = await asyncio.to_thread(
                run_council_local, topic, digest_to_brief(digest),
                model=settings.effective_council_model(),
                council_names=tuple(settings.council_personas),
                chair_name=settings.council_chair,
                council_models=tuple(settings.council_models),
                personas=self.personas, settings=settings,
            )
            if not result.votes:
                await interaction.followup.send(f"議會無法召開:{result.note or '人格載入失敗'}")
                return
            await interaction.followup.send(embed=council_to_embed(result))

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
                interaction, f"[{backend.value}{mtag}] **{question}**\n{rep.display(redacted)}{tail}")

        @tree.command(name="models", description="列出本地 Ollama 可用模型")
        async def models_cmd(interaction: discord.Interaction):
            models = await asyncio.to_thread(list_ollama_models)
            body = "\n".join(f"- `{m}`" for m in models) if models else "(Ollama 未啟動或無模型)"
            await interaction.response.send_message("本地 Ollama 模型:\n" + body, ephemeral=True)

        @tree.command(name="status", description="bot 狀態與設定")
        async def status_cmd(interaction: discord.Interaction):
            await interaction.response.send_message(embed=self._status_embed("狀態"),
                                                    ephemeral=True)

        @tree.command(name="cmd",
                      description="指令教學範例(情境→指令→會發生什麼;主打議會閉環)")
        async def cmd_cmd(interaction: discord.Interaction):
            await interaction.response.send_message(embed=self._tutorial_embed(),
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
            await self._send_followup(interaction, f"📓 **{question}**\n{rep.display(redacted)}")

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

        @tree.command(name="basecross",
                      description="月線底部金叉+資金介入篩選(2022殺/AI錯殺軟體;可丟自訂 ticker)")
        @app_commands.describe(which="killed2022 / ai_software / ecommerce / all(預設)",
                               tickers="額外加篩的代號,逗號分隔(例:CRWD,VST,8454.TW)")
        @app_commands.choices(which=[
            app_commands.Choice(name="2022 殺下來的大底", value="killed2022"),
            app_commands.Choice(name="AI 錯殺軟體股", value="ai_software"),
            app_commands.Choice(name="電商 · agentic-commerce", value="ecommerce"),
            app_commands.Choice(name="小型電商(高賠率高風險)", value="ecommerce_small"),
            app_commands.Choice(name="全名單", value="all"),
        ])
        async def basecross_cmd(interaction: discord.Interaction,
                                which: Optional[app_commands.Choice[str]] = None,
                                tickers: str = ""):
            await interaction.response.defer(thinking=True)   # yfinance 5y fetch, ~slow
            extra = [t.strip().upper() for t in tickers.replace(" ", ",").split(",") if t.strip()]
            title, rows = await asyncio.to_thread(
                run_basecross, which.value if which else "all",
                settings=settings, extra_tickers=extra or None)
            await interaction.followup.send(embed=basecross_to_embed(title, rows))

        @tree.command(name="rally",
                      description="起漲訊號追蹤(融合資金/技術/消息/供應鏈/基本面;連續起漲才可考慮買入)")
        @app_commands.describe(which="killed2022 / ai_software / ecommerce / all(預設)",
                               tickers="額外加入的代號,逗號分隔(例:SHOP,SE,MELI,8454.TW)")
        @app_commands.choices(which=[
            app_commands.Choice(name="2022 殺下來的大底", value="killed2022"),
            app_commands.Choice(name="AI 錯殺軟體股", value="ai_software"),
            app_commands.Choice(name="電商 · agentic-commerce", value="ecommerce"),
            app_commands.Choice(name="小型電商(高賠率高風險)", value="ecommerce_small"),
            app_commands.Choice(name="全名單", value="all"),
        ])
        async def rally_cmd(interaction: discord.Interaction,
                            which: Optional[app_commands.Choice[str]] = None,
                            tickers: str = ""):
            await interaction.response.defer(thinking=True)   # yfinance 5y fetch, ~slow
            extra = [t.strip().upper() for t in tickers.replace(" ", ",").split(",") if t.strip()]
            title, rows = await asyncio.to_thread(
                run_basecross, which.value if which else "all",
                settings=settings, extra_tickers=extra or None)
            quality = await asyncio.to_thread(_basecross.quality_from_fom, settings.outputs_dir)
            prior = await asyncio.to_thread(_rally.load_prior_streaks, settings.outputs_dir)
            signals = _rally.build_signals(rows, quality_by_ticker=quality, prior_streaks=prior)
            await asyncio.to_thread(_rally.write_state, settings.outputs_dir, signals)
            await interaction.followup.send(embed=rally_to_embed(title, signals))

        @tree.command(name="rescan",
                      description="重跑選股/訊號/健檢掃描(本地;FOM 全宇宙掃描較久),完成後貼最新結果")
        @app_commands.describe(scope="fom=選股(預設)· signals=每日10訊號 · health=持倉+姿態 · all=全部")
        @app_commands.choices(scope=[
            app_commands.Choice(name="選股(FOM 全宇宙掃描)", value="fom"),
            app_commands.Choice(name="每日 10-訊號(籌碼 FSM → picks)", value="signals"),
            app_commands.Choice(name="持倉 + 姿態健檢", value="health"),
            app_commands.Choice(name="全部(選股+訊號+健檢,較久)", value="all"),
        ])
        async def rescan_cmd(interaction: discord.Interaction,
                             scope: Optional[app_commands.Choice[str]] = None):
            key = scope.value if scope else "fom"
            jobs = _SCAN_SETS.get(key, _SCAN_SETS["fom"])
            await interaction.response.defer(thinking=True)   # scans run locally, can be slow
            results = []
            for label, modargs, timeout in jobs:
                ok, tail = await self._run_scan_module(modargs, timeout)
                results.append((label, ok, tail))
            status = "\n".join(
                f"{'✅' if ok else '⚠️'} {label}" + (f" — {tail}" if (tail and not ok) else "")
                for label, ok, tail in results)
            digest = compose_evening(settings, datetime.now(TPE))
            await interaction.followup.send(
                content=f"🔄 重跑完成({key}):\n{status}\n\n下面是更新後的最新結果:",
                embeds=digest_to_embeds(digest))

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
        if not content:
            return

        # !cmd / !help — cheat-sheet, works in ANY channel.
        if content.lower() in ("!cmd", "!cmds", "!help", "!commands", "!指令"):
            await message.channel.send(embed=self._help_embed())
            return

        # !教學 / !tutorial — worked step-by-step examples (the /cmd tutorial).
        if content.lower() in ("!教學", "!tutorial", "!範例", "!example", "!教學範例"):
            await message.channel.send(embed=self._tutorial_embed())
            return

        # !sync / !ver — force re-sync slash commands AND report what THIS running
        # process actually has. If `rescan` is missing from the list, the bot is on
        # OLD code (git pull + restart needed); if it's listed but not in Discord's
        # menu, this re-sync fixes it. Either way you can tell which it is.
        if content.lower() in ("!sync", "!resync", "!同步", "!ver", "!version", "!版本"):
            rev = await asyncio.to_thread(self._git_rev)
            have = sorted(c.name for c in self.tree.get_commands())
            note = "" if "rescan" in have else "\n⚠️ 這個 process 沒有 `rescan` → 跑的是舊程式碼,請 git pull + 重啟。"
            try:
                g = self._guild()
                if g:
                    self.tree.copy_global_to(guild=g)
                    synced = await self.tree.sync(guild=g)
                else:
                    synced = await self.tree.sync()
                await message.channel.send(
                    f"✅ 已重新同步 {len(synced)} 個斜線指令(code `{rev}`):\n"
                    f"{', '.join(sorted(c.name for c in synced))}{note}")
            except Exception as exc:
                await message.channel.send(
                    f"⚠️ 同步失敗(code `{rev}`):{exc}\n本 process 現有指令:{', '.join(have)}{note}")
            return

        if ch_name == C.CH_COUNCIL:
            persona, q = resolve_persona(content, self.personas, self.settings.default_persona)
            if persona is None:
                await message.channel.send("沒有可用人格;檢查 analysts/ 目錄。")
                return
            async with message.channel.typing():
                rep = await asyncio.to_thread(ask_persona, persona, q or content, self.settings)
            await self._persona_say(message.channel, persona, rep.display(redacted))

        elif ch_name == C.CH_ASK:
            async with message.channel.typing():
                rep = await asyncio.to_thread(ask_claude_research, content, self.settings)
            tail = f"\n\n_— Claude Code · ${rep.cost_usd or 0:.3f}_" if rep.ok else ""
            for c in _chunks(rep.display(redacted) + tail):
                await message.channel.send(c)

        elif ch_name == C.CH_NOTEBOOK:
            # local NotebookLM: qwen reads $hark and answers with citations.
            async with message.channel.typing():
                rep = await asyncio.to_thread(ask_wiki, content, self.settings)
            for c in _chunks(f"📓 {rep.display(redacted)}"):
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
                embeds.append(council_to_embed(council))

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

    def _git_rev(self) -> str:
        """Short commit the bot's code is running, for 'is it on new code?' checks."""
        try:
            p = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                               cwd=str(self.settings.project_root),
                               capture_output=True, text=True, timeout=10)
            return (p.stdout or "").strip() or "?"
        except Exception:
            return "?"

    async def _run_scan_module(self, args: list[str], timeout: int) -> tuple[bool, str]:
        """Run `python -m <args>` in project_root → (ok, last_output_line). Never raises."""
        try:
            proc = await asyncio.to_thread(
                subprocess.run,
                [sys.executable, "-m", *args],
                cwd=str(self.settings.project_root),
                capture_output=True, text=True, timeout=timeout,
            )
            out = ((proc.stdout or "") + (proc.stderr or "")).strip()
            tail = out.splitlines()[-1] if out else ""
            return proc.returncode == 0, tail[:300]
        except subprocess.TimeoutExpired:
            return False, f"逾時(>{timeout}s) — 全宇宙掃描較久,可稍後再看 /picks"
        except Exception as exc:  # never let a scan failure crash the handler
            log.warning("scan %s failed: %s", args, exc)
            return False, str(exc)[:300]

    async def _refresh_outputs(self) -> None:
        """Run `sharks health-check` to refresh outputs/ before a meeting."""
        await self._run_scan_module(["sharks.cli", "health-check"], 180)

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
                await ch.send(embed=council_to_embed(result))


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

