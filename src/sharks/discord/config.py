"""Configuration for the Sharks Discord bot.

Everything tunable lives here, sourced from environment / `.env` so no secret
ever lands in git (`.env` is .gitignored; see `.gitignore`). The module stays
dependency-tolerant: it loads `python-dotenv` if present but falls back to a tiny
built-in `.env` reader, so `Settings.load()` works even before
`pip install discord.py python-dotenv` (handy for the offline smoke test).

Timezone: Taiwan is a fixed UTC+8 with no DST, so we use a fixed offset rather
than pulling in tzdata — exact and dep-free.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import timedelta, timezone
from pathlib import Path

# $hark root = .../$hark/src/sharks/discord/config.py -> parents[3]
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Taiwan time — fixed +8, no DST. All meeting schedules are expressed in TPE.
TPE = timezone(timedelta(hours=8), name="TPE")

# ── Channel names (精簡版 — the minimal set the principal chose) ──────────────
# The bot resolves channels by NAME within the guild (setup_guild.py creates
# them), so the principal can rename in Discord and just update these.
CH_STATUS = "bot-狀態"
CH_MORNING = "晨會"
CH_NOON = "午會"
CH_EVENING = "晚會"
CH_MARKET = "市場"
CH_PICKS = "每日選股"
CH_ASK = "問claude"
CH_COUNCIL = "分析師議會"
CH_CONTENT = "自媒體"
CH_NOTEBOOK = "筆記本"     # ask-the-folder: local qwen RAG over $hark (NotebookLM)
CH_INGEST = "知識注入"     # paste text/URL → ingested into $hark wiki
CH_GENERAL = "雜談"

# Full minimal channel layout under one category, in display order.
MINIMAL_CATEGORY = "PolkaSharks"
MINIMAL_CHANNELS: tuple[str, ...] = (
    CH_STATUS, CH_MORNING, CH_NOON, CH_EVENING, CH_MARKET,
    CH_PICKS, CH_ASK, CH_COUNCIL, CH_CONTENT, CH_NOTEBOOK, CH_INGEST, CH_GENERAL,
)
# Optional voice channels (created by setup_guild only if SHARKS_DISCORD_VOICE=1).
VOICE_CHANNELS: tuple[str, ...] = ("盤中-trading-floor", "深夜")


def _read_dotenv(path: Path) -> None:
    """Populate os.environ from a .env file without clobbering real env vars.

    Prefers python-dotenv when installed; otherwise a minimal KEY=VALUE parser
    (handles quotes, `export ` prefix, and `#` comments). Missing file = no-op.
    """
    try:  # the nice path
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(path, override=False)
        return
    except Exception:
        pass
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def _env(key: str, default: str = "") -> str:
    return (os.environ.get(key) or default).strip()


def _env_int(key: str, default: int) -> int:
    try:
        return int(_env(key) or default)
    except ValueError:
        return default


def _env_float(key: str, default: float) -> float:
    try:
        return float(_env(key) or default)
    except ValueError:
        return default


@dataclass
class Settings:
    """Resolved runtime configuration for the bot."""

    # ── Discord ──────────────────────────────────────────────────────────────
    token: str = ""
    guild_id: int = 0                  # 0 = resolve the single guild the bot is in

    # ── Backend ("brain") routing ────────────────────────────────────────────
    # hybrid : personas -> Nemotron(local), /ask -> Claude Code(local) [default]
    # local  : everything -> Nemotron(local)
    # claude : everything -> Claude Code(local)
    backend: str = "hybrid"

    # /ask loopback (local Claude Code) — read-only research defaults.
    claude_model: str = "sonnet"
    claude_budget_usd: float = 0.50    # hard per-question cost ceiling
    claude_timeout_s: int = 180
    ask_allowed_tools: tuple[str, ...] = ("Read", "Grep", "Glob", "WebSearch", "WebFetch")
    ask_disallowed_tools: tuple[str, ...] = ("Write", "Edit", "NotebookEdit", "Bash")
    add_dirs: tuple[str, ...] = ()     # extra dirs claude may read (besides cwd=$hark)

    # Persona chat (local Ollama via existing nemotron_client).
    # Default to a clean instruct model: nemotron-3-nano is a *reasoning* model
    # that returns empty content when the budget is spent thinking. qwen2.5:7b
    # answers 繁中 directly. Override with SHARKS_DISCORD_LOCAL_MODEL.
    local_model: str = "qwen2.5:7b"
    persona_temperature: float = 0.6
    persona_max_tokens: int = 700
    default_persona: str = "sharks"    # house view if none specified

    # Council debate (multi-persona 質疑→投票→結論, runs on the LOCAL model).
    council_enabled: bool = True
    council_model: str = ""            # "" → use local_model
    # Expanded bench so the vote splits across真正不同的腦:
    #   4 objective quant voices — FOM / Bayesian / valuation / regime
    #   + KOL/subjective voices — 供應鏈(huang)、總經狙擊(serenity)、長線(sam)、
    #     底層邏輯(yupupin)、空方風控(bear)、動能(momentum).
    # buffet / crypto can be added via SHARKS_DISCORD_COUNCIL_PERSONAS.
    council_personas: tuple[str, ...] = (
        "fomquant", "bayes", "valuation", "regimequant",
        "huang", "serenity", "sam", "yupupin", "bear", "momentum")
    council_chair: str = "sharks"
    # Per-seat models, round-robin. Only qwen2.5:7b + llama3.1:8b — both fit in
    # 12 GB together so they stay resident (no load churn = fast), per principal.
    council_models: tuple[str, ...] = ("qwen2.5:7b", "llama3.1:8b")
    # 交叉質詢 layer: stance → 交叉質詢 → 投票 → 主席 (off → faster 質疑+投票 round).
    council_cross_exam: bool = True
    # Closed loop: read recent 結論 + per-persona memory + topic RAG into the
    # debate, and write each conclusion back to wiki/council/ (RAG-searchable).
    council_memory_enabled: bool = True
    council_writeback: bool = True

    # ── 雜談 chatter (#雜談): hourly news → 速解讀 (local LLM); periodic council ──
    chatter_enabled: bool = True
    chatter_council_every: int = 4     # run a full council every Nth hourly chatter (0 = never)
    chatter_news_n: int = 8            # headlines fed to each 速解讀

    # ── Meeting schedule (TPE, fixed UTC+8) ──────────────────────────────────
    morning_hhmm: str = "07:30"
    noon_hhmm: str = "13:00"           # 午會 — midday check-in
    evening_hhmm: str = "22:30"
    weekly_day: str = "Monday"         # weekly FOM block folds into that day's 晨會
    meetings_enabled: bool = True
    # Before a meeting, refresh outputs/ by running `sharks health-check` so the
    # digest is current even without the separate Task Scheduler routine.
    meeting_refresh: bool = True
    # Append a short Claude-Code research narrative (今日國際局勢 / 台美股行情) to
    # each meeting. Costs a few cents per meeting; needs a non-local backend.
    meeting_research: bool = True
    # Append the performance-feedback rotation throttle (績效強→不換股+深挖支撐;
    # 真反轉→換股) to each meeting. Pure/local, no cost.
    feedback_in_meetings: bool = True

    # ── Misc ─────────────────────────────────────────────────────────────────
    outputs_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "outputs")
    analysts_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "analysts")
    project_root: Path = field(default_factory=lambda: PROJECT_ROOT)
    enable_voice: bool = False

    @classmethod
    def load(cls) -> "Settings":
        _read_dotenv(PROJECT_ROOT / ".env")
        add_dirs = tuple(
            d.strip() for d in _env("SHARKS_DISCORD_ADD_DIRS").split(os.pathsep) if d.strip()
        )
        return cls(
            token=_env("DISCORD_BOT_TOKEN"),
            guild_id=_env_int("DISCORD_GUILD_ID", 0),
            backend=(_env("SHARKS_DISCORD_BACKEND", "hybrid")).lower(),
            claude_model=_env("SHARKS_DISCORD_CLAUDE_MODEL", "sonnet"),
            claude_budget_usd=_env_float("SHARKS_DISCORD_CLAUDE_BUDGET_USD", 0.50),
            claude_timeout_s=_env_int("SHARKS_DISCORD_CLAUDE_TIMEOUT_S", 180),
            add_dirs=add_dirs,
            local_model=_env("SHARKS_DISCORD_LOCAL_MODEL", "qwen2.5:7b"),
            persona_temperature=_env_float("SHARKS_DISCORD_PERSONA_TEMP", 0.6),
            persona_max_tokens=_env_int("SHARKS_DISCORD_PERSONA_MAXTOK", 700),
            default_persona=_env("SHARKS_DISCORD_DEFAULT_PERSONA", "sharks").lower(),
            council_enabled=_env("SHARKS_DISCORD_COUNCIL", "1") != "0",
            council_model=_env("SHARKS_DISCORD_COUNCIL_MODEL", ""),
            council_personas=tuple(
                p.strip().lower() for p in
                _env("SHARKS_DISCORD_COUNCIL_PERSONAS",
                     "fomquant,bayes,valuation,regimequant,"
                     "huang,serenity,sam,yupupin,bear,momentum").split(",")
                if p.strip()
            ),
            council_chair=_env("SHARKS_DISCORD_COUNCIL_CHAIR", "sharks").lower(),
            council_models=tuple(
                m.strip() for m in
                _env("SHARKS_DISCORD_COUNCIL_MODELS", "qwen2.5:7b,llama3.1:8b").split(",")
                if m.strip()
            ),
            council_cross_exam=_env("SHARKS_DISCORD_COUNCIL_CROSSEXAM", "1") != "0",
            council_memory_enabled=_env("SHARKS_DISCORD_COUNCIL_MEMORY", "1") != "0",
            council_writeback=_env("SHARKS_DISCORD_COUNCIL_WRITEBACK", "1") != "0",
            chatter_enabled=_env("SHARKS_DISCORD_CHATTER", "1") != "0",
            chatter_council_every=_env_int("SHARKS_DISCORD_CHATTER_COUNCIL_EVERY", 4),
            chatter_news_n=_env_int("SHARKS_DISCORD_CHATTER_NEWS_N", 8),
            morning_hhmm=_env("SHARKS_DISCORD_MORNING", "07:30"),
            noon_hhmm=_env("SHARKS_DISCORD_NOON", "13:00"),
            evening_hhmm=_env("SHARKS_DISCORD_EVENING", "22:30"),
            weekly_day=_env("SHARKS_DISCORD_WEEKLY_DAY", "Monday"),
            meetings_enabled=_env("SHARKS_DISCORD_MEETINGS", "1") != "0",
            meeting_refresh=_env("SHARKS_DISCORD_MEETING_REFRESH", "1") != "0",
            meeting_research=_env("SHARKS_DISCORD_MEETING_RESEARCH", "1") != "0",
            feedback_in_meetings=_env("SHARKS_DISCORD_FEEDBACK", "1") != "0",
            enable_voice=_env("SHARKS_DISCORD_VOICE", "0") == "1",
        )

    # ── Validation ───────────────────────────────────────────────────────────
    def missing(self) -> list[str]:
        """Return a list of human-readable problems (empty = ready to run)."""
        problems: list[str] = []
        if not self.token:
            problems.append(
                "DISCORD_BOT_TOKEN is empty — create the bot (see README) and put "
                "the token in $hark/.env"
            )
        if self.backend not in ("hybrid", "local", "claude"):
            problems.append(
                f"SHARKS_DISCORD_BACKEND={self.backend!r} invalid (hybrid|local|claude)"
            )
        for label, hhmm in (("MORNING", self.morning_hhmm), ("NOON", self.noon_hhmm),
                            ("EVENING", self.evening_hhmm)):
            if not _valid_hhmm(hhmm):
                problems.append(f"SHARKS_DISCORD_{label}={hhmm!r} not HH:MM")
        return problems

    def effective_council_model(self) -> str:
        return self.council_model or self.local_model


def _valid_hhmm(s: str) -> bool:
    parts = s.split(":")
    if len(parts) != 2:
        return False
    try:
        h, m = int(parts[0]), int(parts[1])
    except ValueError:
        return False
    return 0 <= h < 24 and 0 <= m < 60
