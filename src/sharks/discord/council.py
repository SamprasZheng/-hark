"""Council debate engine — multi-persona 質疑 → 投票 → 結論.

A small multi-agent debate that runs **entirely on the local Ollama model**
(private, free, on the RTX 5070). It exists so a meeting's conclusion is not one
voice but a roomful that disagrees on the record:

  Round 1 (立場)   — each of K analyst personas takes a stance on the day's brief.
  Round 2 (質疑+投票) — each reads the others, rebuts the one it most disagrees
                      with, then casts a structured vote (多/空/中性 + 信心 + 動作).
  主席結論          — a chair persona synthesises the tally + key split into a
                      final 結論 + discipline reminder.

The LLM call is injected as ``ask_fn(system, user, max_tokens) -> (text, ok)`` so
the engine is testable offline and backend-agnostic. ``run_council`` wires it to
the local Nemotron client by default.

Why a clean instruct model by default (qwen2.5:7b): ``nemotron-3-nano:4b`` is a
*reasoning* model — it spends the token budget in a separate ``reasoning`` channel
and returns empty ``content`` when truncated, which is poor for many short debate
turns. The model is configurable; nemotron still works with a larger budget.

Recommend-only: the conclusion is a research view, never an order.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional

from sharks.ai.nemotron_client import NemotronClient
from sharks.discord.personas import ChatPersona, load_personas

# ask_fn(system, user, max_tokens) -> (text, ok)
AskFn = Callable[[str, str, int], tuple[str, bool]]

DEFAULT_COUNCIL = ("fomquant", "bayes", "valuation", "regimequant",
                   "huang", "serenity", "sam", "yupupin", "bear", "momentum")
DEFAULT_CHAIR = "sharks"
_VOTE_WORDS = {"多": "多", "空": "空", "中性": "中性", "中立": "中性"}
_VOTE_RE = re.compile(r"投票[:：]?\s*(多|空|中性|中立).*?信心[:：]?\s*([1-5])", re.DOTALL)


@dataclass
class Vote:
    persona: str
    title: str
    model: str = ""           # the local model this seat ran on
    stance: str = ""          # round-1 立場 text
    crossexam: str = ""       # round-2 交叉質詢 text (cross_exam mode only)
    rebuttal_vote: str = ""   # final 質疑+投票 text
    vote: str = "中性"        # 多 | 空 | 中性
    conviction: int = 3       # 1..5
    action: str = ""


@dataclass
class CouncilResult:
    topic: str
    votes: list[Vote] = field(default_factory=list)
    tally: dict = field(default_factory=dict)         # {多:int, 空:int, 中性:int, avg_conviction:float}
    conclusion: str = ""
    model: str = ""
    backend: str = ""
    ok: bool = False
    note: str = ""

    def lean(self) -> str:
        t = self.tally
        if not t:
            return "中性"
        order = sorted(("多", "空", "中性"), key=lambda k: t.get(k, 0), reverse=True)
        return order[0]


# ── local ask_fn ──────────────────────────────────────────────────────────────

def make_local_ask(model: str, temperature: float = 0.75) -> tuple[AskFn, str]:
    """Return (ask_fn, backend_name) backed by the local Nemotron/Ollama client."""
    client = NemotronClient()

    def ask(system: str, user: str, max_tokens: int = 260) -> tuple[str, bool]:
        call = client.chat(
            "executor",
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            reasoning="off", temperature=temperature, max_tokens=max_tokens, model=model,
        )
        return (call.content or "").strip(), (call.error is None and bool((call.content or "").strip()))

    return ask, client.backend.name


# ── vote parsing ──────────────────────────────────────────────────────────────

def _parse_vote(text: str) -> tuple[str, int, str]:
    """Pull (vote, conviction, action) from a round-2 reply. Tolerant: defaults to
    中性/3 if the structured line is missing."""
    vote, conv, action = "中性", 3, ""
    m = _VOTE_RE.search(text or "")
    if m:
        vote = _VOTE_WORDS.get(m.group(1), "中性")
        try:
            conv = max(1, min(5, int(m.group(2))))
        except ValueError:
            conv = 3
    am = re.search(r"動作[:：]\s*(.+)$", text or "", re.MULTILINE)
    if am:
        action = am.group(1).strip()[:80]
    return vote, conv, action


def _tally(votes: list[Vote]) -> dict:
    out = {"多": 0, "空": 0, "中性": 0}
    for v in votes:
        out[v.vote] = out.get(v.vote, 0) + 1
    convs = [v.conviction for v in votes] or [0]
    out["avg_conviction"] = round(sum(convs) / len(convs), 1)
    return out


# ── engine ────────────────────────────────────────────────────────────────────

def run_council(
    topic: str,
    brief: str,
    *,
    council: list[ChatPersona],
    chair: Optional[ChatPersona] = None,
    models: Optional[dict[str, str]] = None,
    default_model: str = "qwen2.5:7b",
    ask_maker: Callable[[str], tuple[AskFn, str]] = make_local_ask,
    brief_cap: int = 1600,
    memory: str = "",
    persona_memory: Optional[dict[str, str]] = None,
    cross_exam: bool = True,
) -> CouncilResult:
    """Run the debate. Each persona can sit on a DIFFERENT local model
    (multi-model council) via ``models`` = {persona_name: model}; a missing name
    falls back to ``default_model``. ``ask_maker(model) -> (ask_fn, backend)`` is
    the single injection point (tests pass a stub that ignores the model).

    Closed-loop memory (optional, injected — engine stays pure):
      * ``memory`` — a shared block of 近期結論 + RAG over local/ingested docs,
        prepended to every prompt so the bench builds on past conclusions.
      * ``persona_memory`` — {name: text} each seat's own past 立場/投票, so a
        persona is reminded of and held to what *it* argued.
      * ``cross_exam`` — when True, run a distinct 交叉質詢 layer (stance →
        cross-examination → vote → chair) instead of the combined 質疑+投票 round;
        the vote then accounts for the challenges raised against that seat."""
    brief = (brief or "").strip()[:brief_cap]
    models = dict(models or {})
    persona_memory = dict(persona_memory or {})
    mem_block = f"\n\n{memory.strip()}" if (memory or "").strip() else ""
    res = CouncilResult(topic=topic, model=default_model, backend="local")
    if not council:
        res.note = "no council personas configured"
        return res

    _ask_cache: dict[str, AskFn] = {}

    def ask_for(model: str) -> AskFn:
        if model not in _ask_cache:
            _ask_cache[model] = ask_maker(model)[0]
        return _ask_cache[model]

    # Round 1 — 立場 (each persona on its own model, memory-aware)
    for p in council:
        mdl = models.get(p.name, default_model)
        pm = persona_memory.get(p.name, "")
        pm_block = f"\n\n【你的記憶】{pm}" if pm else ""
        user = (
            f"今日簡報(數據已是 point-in-time):\n{brief}{mem_block}{pm_block}\n\n"
            f"【任務】針對「{topic}」,用你的人格視角給 2-3 句立場。"
            f"先明確選邊:**看多 或 看空**(只有真的毫無方向才用中性),"
            f"再給最關鍵的 1 個理由(扣著上面數據;若與你過去立場不同,點明為何修正)。"
            f"態度要鮮明、符合你的人格,不要騎牆、不要跟別人一樣。繁體中文,精簡。"
        )
        text, ok = ask_for(mdl)(p.system_prompt, user, 260)
        res.votes.append(Vote(persona=p.name, title=p.title, model=mdl,
                              stance=text if ok else "(模型無回應)"))

    by_name = {v.persona: v for v in res.votes}

    # Round 2 — 交叉質詢 (optional layer: challenge only, no vote yet)
    if cross_exam:
        for p in council:
            v = by_name[p.name]
            others = "\n".join(f"[{o.title}] {o.stance}"
                               for o in res.votes if o.persona != p.name)
            user = (
                f"今日簡報:\n{brief}{mem_block}\n\n其他分析師的立場:\n{others}\n\n"
                f"【任務·交叉質詢】挑出你最不同意的 1-2 位,**指名道姓**,用具體數據/"
                f"邏輯對他們提出最尖銳的問題或反證(點出盲點與風險)。這回合**不要投票**。"
                f"繁體中文,精簡。"
            )
            text, ok = ask_for(v.model)(p.system_prompt, user, 280)
            v.crossexam = text if ok else "(模型無回應)"

    # Final round — 投票 (sees others' stances; in cross-exam mode also the
    # challenges raised, and must answer those aimed at it)
    for p in council:
        v = by_name[p.name]
        others = "\n".join(f"[{o.title}] {o.stance}" for o in res.votes if o.persona != p.name)
        if cross_exam:
            challenges = "\n".join(
                f"[{o.title}] {o.crossexam}" for o in res.votes
                if o.persona != p.name and o.crossexam and "無回應" not in o.crossexam
            )
            user = (
                f"今日簡報:\n{brief}{mem_block}\n\n其他分析師的立場:\n{others}\n\n"
                f"交叉質詢回合中各方提出的挑戰:\n{challenges or '(無)'}\n\n"
                f"【任務】綜合以上,**尤其回應針對你的質詢**(被問倒就誠實修正),"
                f"再給最終投票——盡量在 多/空 之間選邊,中性只留給真的沒有邊際的情況。"
                f"結尾務必『獨立一行』輸出,格式嚴格:\n"
                f"投票: 多/空/中性 | 信心: 1-5 | 動作: <一個具體標的或動作>\n"
                f"繁體中文,精簡。"
            )
        else:
            user = (
                f"今日簡報:\n{brief}{mem_block}\n\n其他分析師的立場:\n{others}\n\n"
                f"【任務】(1) 用一句話**辛辣地反駁**你最不同意的一位(指名道姓,點出他盲點);"
                f"(2) 給最終投票——盡量在 多/空 之間選邊,中性只保留給真的沒有邊際的情況。"
                f"結尾務必『獨立一行』輸出,格式嚴格:\n"
                f"投票: 多/空/中性 | 信心: 1-5 | 動作: <一個具體標的或動作>\n"
                f"繁體中文,精簡。"
            )
        text, ok = ask_for(v.model)(p.system_prompt, user, 300)
        v.rebuttal_vote = text if ok else "(模型無回應)"
        v.vote, v.conviction, v.action = _parse_vote(text)

    res.tally = _tally(res.votes)

    # 主席結論 (chair runs on default_model — usually the strongest 繁中 model)
    chair_sys = (chair.system_prompt if chair else
                 "你是 PolkaSharks 投研議會主席,綜合各analyst意見做結論,只建議不下單。用繁體中文。")
    votes_block = "\n".join(
        f"[{v.title}/{v.model}] 投票={v.vote} 信心={v.conviction} 動作={v.action or '—'}"
        for v in res.votes
    )
    user = (
        f"今日簡報:\n{brief}{mem_block}\n\n議會票數:多={res.tally['多']} 空={res.tally['空']} "
        f"中性={res.tally['中性']} 平均信心={res.tally['avg_conviction']}\n各人最終意見:\n{votes_block}\n\n"
        f"【任務】你是主席,用繁體中文 4-6 句做出今日結論:(1) 綜合票數的整體傾向"
        f"(若有近期議會記憶,點明這次是延續還是反轉);(2) 點出最大分歧(可點名不同人格/模型);"
        f"(3) 一句具體可執行的觀察/紀律提醒。只建議、不下單,不要捏造數字。"
    )
    conclusion, ok = ask_for(default_model)(chair_sys, user, 460)
    res.conclusion = conclusion if ok else "(主席結論:模型無回應)"
    res.ok = any(v.stance and "無回應" not in v.stance for v in res.votes)
    res.note = "models: " + ", ".join(sorted(set(v.model for v in res.votes)))
    return res


def run_council_local(
    topic: str,
    brief: str,
    *,
    model: str = "qwen2.5:7b",                 # chair + fallback model
    council_names: tuple[str, ...] = DEFAULT_COUNCIL,
    chair_name: str = DEFAULT_CHAIR,
    council_models: tuple[str, ...] = (),      # per-seat models (positional w/ council_names)
    personas: Optional[dict[str, ChatPersona]] = None,
    settings=None,
    cross_exam: Optional[bool] = None,
    use_memory: Optional[bool] = None,
    writeback: Optional[bool] = None,
    ask_maker: Callable[[str], tuple[AskFn, str]] = make_local_ask,
) -> CouncilResult:
    """Convenience: load personas and run a (multi-model) council locally.

    ``council_models`` assigns a model to each seat positionally (round-robin if
    shorter). Empty → every seat uses ``model`` (single-model council).

    Closed loop (on by default when ``settings`` is given): reads recent
    conclusions + per-persona memory + topic RAG into the debate, then writes the
    new conclusion back to ``wiki/council/`` so the next council remembers it.
    Each flag falls back to the matching ``Settings`` field, then to a safe
    default, so tests calling without settings get the plain offline behaviour."""
    personas = personas or load_personas(settings)
    council = [personas[n] for n in council_names if n in personas]
    chair = personas.get(chair_name)
    models: dict[str, str] = {}
    if council_models:
        for i, name in enumerate(council_names):
            models[name] = council_models[i % len(council_models)]

    def _flag(explicit, attr, default):
        if explicit is not None:
            return explicit
        if settings is not None:
            return getattr(settings, attr, default)
        return default

    do_cross = _flag(cross_exam, "council_cross_exam", True)
    do_memory = _flag(use_memory, "council_memory_enabled", settings is not None)
    do_write = _flag(writeback, "council_writeback", settings is not None)

    memory, persona_memory = "", None
    if do_memory and settings is not None:
        try:
            from sharks.discord import council_memory
            memory = council_memory.memory_brief(settings, topic)
            persona_memory = council_memory.persona_memories(settings)
        except Exception:
            memory, persona_memory = "", None

    res = run_council(topic, brief, council=council, chair=chair,
                      models=models, default_model=model, ask_maker=ask_maker,
                      memory=memory, persona_memory=persona_memory,
                      cross_exam=bool(do_cross))
    if not council:
        res.note = f"none of {council_names} found in roster {sorted(personas)}"
        return res

    if do_write and settings is not None and res.votes:
        try:
            from sharks.discord import council_memory
            council_memory.record(res, settings, topic=topic)
        except Exception:
            pass
    return res
