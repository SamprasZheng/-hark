"""Self-media content generator — turn the day's view into post-ready drafts.

Strict-format drafts for X (thread), a blog post (Docusaurus-ready markdown), and
a YouTube short (title + script + description), in the PolkaSharks "shark" voice.

DRAFTS ONLY. The bot posts these to a private review channel (#自媒體); it never
publishes to X / YouTube / the blog — that stays an explicit human action. Every
output carries a not-financial-advice disclaimer. Recommend-only.

Pure engine: the LLM call is injected as ``ask_fn(system, user, max_tokens) ->
(text, ok)`` (same contract as council.py), so it's testable and backend-agnostic.
``run_content_local`` wires it to the local Ollama model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from sharks.discord.council import make_local_ask

AskFn = Callable[[str, str, int], tuple[str, bool]]

DISCLAIMER = "⚠️ 僅為研究與市場觀察,非投資建議,請自行判斷、自負盈虧 (DYOR)。"

_VOICE = (
    "你是 PolkaSharks 的自媒體寫手:鯊魚人格——銳利、有梗、敢戳同溫層,但**用數據說話**,"
    "絕不浮誇承諾報酬、不喊單。你寫的是『市場觀察 / 投資教育』內容,不是個人化投資建議。"
    "繁體中文為主,個股用 $代號(例:$NVDA);語氣自信但誠實,該講風險就講。"
    "每篇結尾務必附上免責聲明。只輸出要求的內容本體,不要額外解釋。"
)

_KINDS = ("x", "blog", "youtube")


@dataclass
class ContentDraft:
    topic: str = ""
    x_thread: str = ""
    blog: str = ""
    youtube: str = ""
    model: str = ""
    backend: str = ""
    note: str = ""

    def as_sections(self) -> list[tuple[str, str]]:
        out = []
        if self.x_thread:
            out.append(("🐦 X / Twitter Thread", self.x_thread))
        if self.blog:
            out.append(("📝 Blog 草稿 (Docusaurus md)", self.blog))
        if self.youtube:
            out.append(("▶️ YouTube Short", self.youtube))
        return out


def gen_x_thread(topic: str, brief: str, ask_fn: AskFn) -> str:
    user = (
        f"依嚴格格式寫一條 X(Twitter)thread。主題:「{topic}」。\n背景數據:\n{brief}\n\n"
        f"格式(每則『獨立一行』,每則 ≤200 字,共 5-6 則):\n"
        f"1/ 鉤子 + 今日核心結論(一句吸睛、帶 $代號)\n"
        f"2/ 關鍵數據點 ①\n3/ 關鍵數據點 ②\n4/ 反方 / 風險(誠實打臉自己)\n"
        f"5/ 收尾 + 行動觀察點\n6/ {DISCLAIMER}\n"
        f"鯊魚口吻、適度 emoji。只輸出 thread 本體。"
    )
    text, _ = ask_fn(_VOICE, user, 900)
    return text


def gen_blog(topic: str, brief: str, ask_fn: AskFn) -> str:
    user = (
        f"寫一篇 250-400 字的繁體中文部落格草稿(Docusaurus markdown)。主題:「{topic}」。\n"
        f"背景數據:\n{brief}\n\n"
        f"需包含:`# 標題`、2-3 個 `## 小節`、條列重點、一段反方/風險、"
        f"結尾用 `> {DISCLAIMER}` 引言區塊。只輸出 markdown 本體。"
    )
    text, _ = ask_fn(_VOICE, user, 1000)
    return text


def gen_youtube(topic: str, brief: str, ask_fn: AskFn) -> str:
    user = (
        f"為一支 60-90 秒 YouTube Short 產出腳本包。主題:「{topic}」。\n背景數據:\n{brief}\n\n"
        f"格式:\n**標題**(≤60 字,吸睛帶 $代號)\n**腳本**(3-5 點口語旁白,每點一行)\n"
        f"**影片描述**(2-3 句 + 3-5 個 #hashtag)\n**{DISCLAIMER}**\n只輸出這些。"
    )
    text, _ = ask_fn(_VOICE, user, 900)
    return text


_GENERATORS = {"x": gen_x_thread, "blog": gen_blog, "youtube": gen_youtube}


def generate(kinds: list[str], topic: str, brief: str, ask_fn: AskFn,
             *, brief_cap: int = 1800) -> ContentDraft:
    brief = (brief or "").strip()[:brief_cap]
    draft = ContentDraft(topic=topic)
    for kind in kinds:
        gen = _GENERATORS.get(kind)
        if not gen:
            continue
        text = gen(topic, brief, ask_fn).strip()
        if kind == "x":
            draft.x_thread = text
        elif kind == "blog":
            draft.blog = text
        elif kind == "youtube":
            draft.youtube = text
    return draft


def run_content_local(kinds: list[str], topic: str, brief: str,
                      *, model: str = "qwen2.5:7b", temperature: float = 0.8) -> ContentDraft:
    """Generate drafts on the local Ollama model."""
    if kinds == ["all"] or not kinds:
        kinds = list(_KINDS)
    ask_fn, backend = make_local_ask(model, temperature=temperature)
    draft = generate(kinds, topic, brief, ask_fn)
    draft.model, draft.backend = model, backend
    return draft
