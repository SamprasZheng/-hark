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
    list_ollama_models,
)
from sharks.discord.config import TPE, Settings
from sharks.discord.content import run_content_local
from sharks.discord.council import CouncilResult, run_council_local
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
    e.set_footer(text=f"本地多模型議會 · {models_used} · 僅研究非建議,永不下單"[:2048])
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
        e.add_field(name="人格", value=", ".join(sorted(self.personas)) or "—", inline=False)
        e.set_footer(text="recommend-only · 永不下單 · /ask 唯讀 · 議會跑本地")
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
            "`/council <主題>` — 6 人質疑→投票→結論(本地)\n"
            "例:`/council 今晚美股該偏多還偏空`\n"
            "`/meeting <morning|noon|evening|weekly>` — 手動開會\n"
            "`/picks` — 最近一次選股 / 訊號"), inline=False)
        e.add_field(name="📣 自媒體", value=(
            "`/content <x|blog|youtube|all> [主題]` — 產草稿到 #自媒體(不代發)\n"
            "例:`/content all 今日半導體` · `/content x AI 泡沫`"), inline=False)
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
        if not s.meetings_enabled:
            return
        now = datetime.now(TPE)
        hhmm, today = now.strftime("%H:%M"), now.date().isoformat()
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
