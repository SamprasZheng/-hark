"""Load analyst voices from `analysts/*.md` as chat personas for Discord.

This is a *superset* of the FOM voting roster in `sharks.analysts.persona`:
that loader only takes files with `type: analyst-persona` (huang, sam) because
only those contribute a quantitative tilt. For CHAT we also want the prose
voices (buffett, serenity, crypto, yupupin) and the house view (sharks.md, the
constitution). Design-critique archives (codex, gemini) and scaffolding
(_TEMPLATE, README) are excluded — they are not voices to talk to.

Each persona becomes a system prompt = a guardrail header (recommend-only,
not-licensed-advice, reply in 繁體中文) + the file's own content. The body is
truncated so a small local model (Nemotron 4B) keeps the whole thing in context.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from sharks.analysts.persona import _parse_frontmatter  # reuse the dep-free reader
from sharks.discord.config import Settings

# Files in analysts/ that are NOT chat voices.
_DENYLIST = {"codex", "gemini", "_template", "readme"}

# Keep persona bodies bounded so the local model has room to actually answer.
_MAX_BODY_CHARS = 6000

# The standing guardrail wrapped around every persona — keeps the whole surface
# inside the constitution: analysis/education only, never execution.
_GUARDRAIL = (
    "你是 PolkaSharks 私人投研系統裡的一個「分析師人格」,供使用者(只有兩位)做"
    "研究、討論與教育之用。嚴守以下界線:\n"
    "1. 你只提供分析、觀點與研究,這些「不是」個人化投資建議,你也不是持牌投顧;"
    "使用者需自行判斷並承擔風險。\n"
    "2. 系統只產生研究與建議,「永遠不」代為下單、轉帳、連接券商或交易所。若被要求"
    "執行交易,明確拒絕並請使用者自行操作。\n"
    "3. 用繁體中文回答,語氣貼合你這個人格的性格;有把握再講,沒資料就說不知道,"
    "不要捏造價格、財報日或數字。\n"
    "4. 盡量簡潔(Discord 訊息),需要時用條列。\n"
)


@dataclass
class ChatPersona:
    name: str            # short id (lowercase), e.g. "huang"
    title: str           # display label, e.g. "huang · 黃靖哲"
    system_prompt: str   # full system prompt incl. guardrail
    source_file: str

    def reply_name(self) -> str:
        """Webhook display name used when the persona speaks in Discord."""
        return self.title


def _title_for(name: str, fm: dict, body: str) -> str:
    """Best-effort human label for the persona."""
    pretty = {
        "huang": "huang · 黃靖哲(供應鏈撿便宜)",
        "sam": "sam · 長線與時間交朋友",
        "sharks": "sharks · 綜合家底(憲法)",
        "buffet": "buffett · 價值投資",
        "serenity": "serenity · 總經狙擊",
        "crypto": "crypto · 加密中長線",
        "yupupin": "yupupin · 底層邏輯",
    }
    if name in pretty:
        return pretty[name]
    persona = fm.get("personality")
    return f"{name}" + (f" · {persona}" if persona else "")


def _strip_frontmatter(text: str) -> str:
    m = re.match(r"\A---\s*\n.*?\n---\s*\n", text, re.DOTALL)
    return text[m.end():] if m else text


def _build_system_prompt(name: str, fm: dict, body: str) -> str:
    parts = [_GUARDRAIL, f"\n── 你的人格:{name} ──"]
    if fm:
        for k in ("personality", "expertise", "market_focus", "signature_indicators"):
            v = fm.get(k)
            if v:
                parts.append(f"{k}: {v}")
    body = body.strip()
    if len(body) > _MAX_BODY_CHARS:
        body = body[:_MAX_BODY_CHARS].rstrip() + "\n…(人格描述過長,已截斷)"
    parts.append("\n── 人格內容(你的思維與風格來源)──\n" + body)
    return "\n".join(parts)


def load_personas(settings: Settings | None = None) -> dict[str, ChatPersona]:
    """Return {name: ChatPersona} for every chat-able analyst voice."""
    settings = settings or Settings.load()
    out: dict[str, ChatPersona] = {}
    adir = settings.analysts_dir
    if not adir.exists():
        return out
    for path in sorted(adir.glob("*.md")):
        stem = path.stem.lower()
        if stem in _DENYLIST:
            continue
        text = path.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)
        name = str(fm.get("name") or stem).lower()
        body = _strip_frontmatter(text)
        out[name] = ChatPersona(
            name=name,
            title=_title_for(name, fm, body),
            system_prompt=_build_system_prompt(name, fm, body),
            source_file=path.name,
        )
    return out


def resolve_persona(
    text: str, personas: dict[str, ChatPersona], default: str
) -> tuple[ChatPersona | None, str]:
    """Parse a leading persona selector from a chat message.

    Supports `name: question`, `@name question`, or bare text (→ default).
    Returns (persona, remaining_question). persona is None only if even the
    default is missing from the roster.
    """
    stripped = text.strip()
    chosen = default
    question = stripped
    m = re.match(r"^@?([A-Za-z一-鿿_]+)\s*[:：]\s*(.*)$", stripped, re.DOTALL)
    if m and m.group(1).lower() in personas:
        chosen = m.group(1).lower()
        question = m.group(2).strip()
    else:
        m2 = re.match(r"^@([A-Za-z_]+)\s+(.*)$", stripped, re.DOTALL)
        if m2 and m2.group(1).lower() in personas:
            chosen = m2.group(1).lower()
            question = m2.group(2).strip()
    return personas.get(chosen), question
