"""Council debate engine — 開場 → 交叉質詢 → 答辯 → 投票 → 正反方 → 主席結論.

A small multi-agent **cross-examination debate** that runs entirely on the local
Ollama model (private, free, on the RTX 5070). A meeting's conclusion is not one
voice but a roomful that interrogates each other on the record:

  R1 開場立場   — each analyst persona takes a side (多/空) and cites ONE concrete
                  數據/消息 from the brief.
  R2 交叉質詢   — each persona names the opponent it most disagrees with and asks
                  ONE sharp question aimed at that opponent's blind spot.
  R3 答辯       — every persona that got questioned thinks it through and answers /
                  defends (may concede, may counter — with data).
  R4 最終投票   — having heard the cross-examination, each casts a structured vote
                  (多/空/中性 + 信心 + 動作). The vote comes AFTER the debate.
  R5 正反方對照 — a 書記/裁判 reads the whole transcript and lays out the bull case
                  vs the bear case (each with its data), the 關鍵分歧, the 待驗證.
  主席結論      — the chair synthesises tally + ledger + biggest clash → 結論 + 紀律.

The LLM call is injected as ``ask_fn(system, user, max_tokens) -> (text, ok)`` so
the engine is testable offline and backend-agnostic. ``run_council`` wires it to
the local Nemotron client by default; each seat may sit on a different model.

Why a clean instruct model by default (qwen2.5:7b): ``nemotron-3-nano:4b`` is a
*reasoning* model — it spends the budget in a separate ``reasoning`` channel and
returns empty ``content`` when truncated, poor for many short debate turns.

Recommend-only: the conclusion is a research view, never an order.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional

from sharks.ai.nemotron_client import NemotronClient
from sharks.discord.personas import ChatPersona, load_personas

# ask_fn(system, user, max_tokens) -> (text, ok)
AskFn = Callable[[str, str, int], tuple[str, bool]]

DEFAULT_COUNCIL = ("fomquant", "bayes", "valuation", "regimequant", "huang", "bear", "momentum")
DEFAULT_CHAIR = "sharks"
_VOTE_WORDS = {"多": "多", "空": "空", "中性": "中性", "中立": "中性"}
_VOTE_RE = re.compile(r"投票[:：]?\s*(多|空|中性|中立).*?信心[:：]?\s*([1-5])", re.DOTALL)

# unique markers so an offline stub ask_fn can branch by round
_M_OPEN = "【開場立場】"
_M_CROSS = "【交叉質詢】"
_M_DEFEND = "【答辯】"
_M_VOTE = "【最終投票】"
_M_LEDGER = "【辯論書記】"
_M_CHAIR = "【主席結論】"


@dataclass
class Vote:
    persona: str
    title: str
    model: str = ""            # the local model this seat ran on
    stance: str = ""           # R1 開場立場
    question: str = ""         # R2 the question this persona asked
    question_target: str = ""  # internal name of who it questioned ("" if unmatched)
    answer: str = ""           # R3 this persona's answer to the questions aimed at it
    rebuttal_vote: str = ""    # R4 raw vote text
    vote: str = "中性"         # 多 | 空 | 中性
    conviction: int = 3        # 1..5
    action: str = ""


@dataclass
class Exchange:
    """One cross-examination: asker -> target question, plus target's answer."""
    asker: str            # internal name
    asker_title: str
    target: str           # internal name
    target_title: str
    question: str
    answer: str = ""      # filled from the target persona's R3 答辯


@dataclass
class CouncilResult:
    topic: str
    votes: list[Vote] = field(default_factory=list)
    tally: dict = field(default_factory=dict)         # {多,空,中性,avg_conviction}
    exchanges: list[Exchange] = field(default_factory=list)   # 交叉質詢逐筆
    bull: list[str] = field(default_factory=list)     # 正方(看多)論點+數據
    bear: list[str] = field(default_factory=list)     # 反方(看空)論點+數據
    crux: str = ""                                    # 關鍵分歧
    unresolved: str = ""                              # 待驗證數據/消息
    ledger: str = ""                                  # raw 正反方 synthesis (fallback render)
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


# ── parsing ───────────────────────────────────────────────────────────────────

def _parse_vote(text: str) -> tuple[str, int, str]:
    """Pull (vote, conviction, action) from a vote reply. Tolerant: defaults to
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


def _parse_question(text: str, others: list[Vote]) -> tuple[str, str]:
    """From an R2 reply pull (target_name, question). Matches the 提問對象 line
    against the other seats' titles/names; tolerant fallbacks keep an unmatched
    question visible (target='')."""
    text = text or ""
    target = ""
    tm = re.search(r"提問對象[:：]\s*(.+)", text)
    needle = (tm.group(1) if tm else text[:60]).strip()
    for o in others:
        # match on the human title, its prefix before a separator, or the key
        key = o.title.split("·")[0].split("/")[0].strip()
        if (o.title and o.title in needle) or (key and key in needle) or o.persona in needle:
            target = o.persona
            break
    qm = re.search(r"問題[:：]\s*(.+)", text, re.DOTALL)
    if qm:
        question = qm.group(1).strip().split("\n")[0][:240]
    else:                       # no 問題: line — take first line that isn't 提問對象
        cand = [ln.strip() for ln in text.splitlines()
                if ln.strip() and not ln.strip().startswith("提問對象")]
        question = (cand[0] if cand else text.strip())[:240]
    if not question or question.startswith("提問對象"):
        question = "(直接質疑你的立場與數據)"
    return target, question


def _parse_ledger(text: str) -> tuple[list[str], list[str], str, str]:
    """Parse the 書記 ledger into (bull[], bear[], crux, unresolved). Tolerant —
    anything unparsed stays available via the raw ledger text."""
    sections = {"bull": [], "bear": []}
    crux, unresolved = "", ""
    cur = None
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.search(r"正方|看多|多方", line) and ("】" in line or line.endswith(("：", ":")) or len(line) < 14):
            cur = "bull"
            continue
        if re.search(r"反方|看空|空方", line) and ("】" in line or line.endswith(("：", ":")) or len(line) < 14):
            cur = "bear"
            continue
        if re.search(r"關鍵分歧|分歧", line):
            cur = "crux"
            crux = re.sub(r"^.*?(分歧)[:：】]?\s*", "", line).strip()
            continue
        if re.search(r"待驗證|待確認|未解", line):
            cur = "unresolved"
            unresolved = re.sub(r"^.*?(待驗證|待確認|未解)[:：】]?\s*", "", line).strip()
            continue
        bullet = re.sub(r"^[\-\*\d\.、)）\s]+", "", line).strip()
        if cur in ("bull", "bear") and bullet:
            sections[cur].append(bullet[:200])
        elif cur == "crux" and not crux:
            crux = bullet[:240]
        elif cur == "unresolved" and not unresolved:
            unresolved = bullet[:240]
    return sections["bull"][:5], sections["bear"][:5], crux[:300], unresolved[:300]


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
) -> CouncilResult:
    """Run the cross-examination debate. Each persona can sit on a DIFFERENT local
    model (multi-model council) via ``models`` = {persona_name: model}; a missing
    name falls back to ``default_model``. ``ask_maker(model) -> (ask_fn, backend)``
    is the single injection point (tests pass a stub that ignores the model)."""
    brief = (brief or "").strip()[:brief_cap]
    models = dict(models or {})
    res = CouncilResult(topic=topic, model=default_model, backend="local")
    if not council:
        res.note = "no council personas configured"
        return res

    _ask_cache: dict[str, AskFn] = {}

    def ask_for(model: str) -> AskFn:
        if model not in _ask_cache:
            _ask_cache[model] = ask_maker(model)[0]
        return _ask_cache[model]

    # ── R1 開場立場 ───────────────────────────────────────────────────────────
    for p in council:
        mdl = models.get(p.name, default_model)
        user = (
            f"{_M_OPEN}今日簡報(數據已是 point-in-time):\n{brief}\n\n"
            f"針對「{topic}」,用你的人格視角給 2-3 句開場立場。"
            f"先明確選邊:**看多 或 看空**(只有真的毫無方向才用中性),"
            f"再給最關鍵的 1 個理由,且**務必引用上面簡報中一個具體數據或消息**"
            f"(數字/比例/標的/事件)當證據。態度鮮明、符合人格,不要騎牆。繁體中文,精簡。"
        )
        text, ok = ask_for(mdl)(p.system_prompt, user, 240)
        res.votes.append(Vote(persona=p.name, title=p.title, model=mdl,
                              stance=text if ok else "(模型無回應)"))

    by_name = {v.persona: v for v in res.votes}
    persona_by_name = {p.name: p for p in council}

    # ── R2 交叉質詢:每人指名一位提一個尖銳問題 ─────────────────────────────────
    roster = "、".join(o.title for o in res.votes)
    for p in council:
        v = by_name[p.name]
        others = [o for o in res.votes if o.persona != p.name]
        others_txt = "\n".join(f"[{o.title}] {o.stance}" for o in others)
        user = (
            f"{_M_CROSS}今日簡報:\n{brief}\n\n其他分析師的開場立場:\n{others_txt}\n\n"
            f"從這些人({roster})中挑你**最不同意的一位**,提出一個最尖銳、"
            f"直接戳中他論證盲點或數據漏洞的問題(逼他面對他迴避的風險)。"
            f"嚴格用兩行輸出:\n提問對象: <對方名稱>\n問題: <一句話的尖銳問題>\n繁體中文。"
        )
        text, ok = ask_for(v.model)(p.system_prompt, user, 200)
        tgt, q = _parse_question(text, others)
        v.question, v.question_target = q, tgt
        if tgt and q:
            t = by_name[tgt]
            res.exchanges.append(Exchange(asker=p.name, asker_title=p.title,
                                          target=tgt, target_title=t.title, question=q))

    # ── R3 答辯:被點名者一次回答所有衝著他來的問題 ───────────────────────────
    incoming: dict[str, list[Exchange]] = defaultdict(list)
    for ex in res.exchanges:
        incoming[ex.target].append(ex)
    for tname, exs in incoming.items():
        t = by_name[tname]
        qs = "\n".join(f"- {ex.asker_title} 質問你:{ex.question}" for ex in exs)
        user = (
            f"{_M_DEFEND}今日簡報:\n{brief}\n\n你的開場立場:{t.stance}\n\n"
            f"以下分析師對你提出質詢:\n{qs}\n\n"
            f"請**逐一思考並回答**:能承認的就承認、能反擊的用簡報數據反擊,"
            f"不要迴避問題本身。2-4 句,繁體中文,鮮明。"
        )
        text, ok = ask_for(t.model)(persona_by_name[tname].system_prompt, user, 300)
        t.answer = text if ok else "(未答辯)"
        for ex in exs:
            ex.answer = t.answer

    # ── R4 最終投票:聽完交叉辯論後表態 ───────────────────────────────────────
    for p in council:
        v = by_name[p.name]
        tgt = by_name.get(v.question_target)
        their_answer = tgt.answer if tgt else ""
        my_qs = [ex for ex in res.exchanges if ex.target == p.name]
        my_block = ""
        if my_qs:
            asked = "；".join(f"{ex.asker_title}:{ex.question}" for ex in my_qs)
            my_block = f"別人對你的質詢:{asked}\n你的答辯:{v.answer}\n"
        user = (
            f"{_M_VOTE}今日簡報:\n{brief}\n\n你的開場:{v.stance}\n"
            f"你質詢了 {tgt.title if tgt else '對手'}:{v.question or '—'}\n"
            f"對方答辯:{their_answer or '(未答)'}\n{my_block}\n"
            f"【任務】聽完這輪交叉辯論,對方的答辯有沒有改變你的判斷?給**最終投票**。"
            f"盡量在 多/空 之間選邊,中性只留給真的沒有邊際。"
            f"結尾務必『獨立一行』,格式嚴格:\n"
            f"投票: 多/空/中性 | 信心: 1-5 | 動作: <一個具體標的或動作>\n繁體中文,精簡。"
        )
        text, ok = ask_for(v.model)(p.system_prompt, user, 220)
        v.rebuttal_vote = text if ok else "(模型無回應)"
        v.vote, v.conviction, v.action = _parse_vote(text)

    res.tally = _tally(res.votes)

    # ── R5 正反方對照:書記/裁判整理 bull vs bear + 數據 ───────────────────────
    debate_txt = "\n".join(
        f"[{v.title}] 立場:{v.stance} | 投票:{v.vote}(信心{v.conviction})"
        for v in res.votes
    )
    cross_txt = "\n".join(
        f"{ex.asker_title}→{ex.target_title} 問:{ex.question} | {ex.target_title}答:{ex.answer}"
        for ex in res.exchanges
    )
    ledger_sys = (
        "你是 PolkaSharks 投研議會的辯論書記,中立、只憑證據。把一場辯論整理成"
        "正方(看多)與反方(看空)的對照,每一條都要附上被引用的數據/消息。繁體中文。"
    )
    ledger_user = (
        f"{_M_LEDGER}辯論主題:{topic}\n\n各方立場與投票:\n{debate_txt}\n\n"
        f"交叉質詢與答辯:\n{cross_txt or '(無)'}\n\n"
        f"請嚴格用下列格式輸出(每條 bullet 結尾用括號標出數據/消息來源):\n"
        f"【正方·看多】\n- <論點>(數據:...)\n【反方·看空】\n- <論點>(數據:...)\n"
        f"【關鍵分歧】<一句:雙方真正卡在哪>\n【待驗證】<一句:哪個數據/消息一旦揭曉會定勝負>"
    )
    ledger, lok = ask_for(default_model)(ledger_sys, ledger_user, 640)
    if lok:
        res.ledger = ledger
        res.bull, res.bear, res.crux, res.unresolved = _parse_ledger(ledger)

    # ── 主席結論 ──────────────────────────────────────────────────────────────
    chair_sys = (chair.system_prompt if chair else
                 "你是 PolkaSharks 投研議會主席,綜合各analyst意見做結論,只建議不下單。用繁體中文。")
    votes_block = "\n".join(
        f"[{v.title}/{v.model}] 投票={v.vote} 信心={v.conviction} 動作={v.action or '—'}"
        for v in res.votes
    )
    chair_user = (
        f"{_M_CHAIR}今日簡報:\n{brief}\n\n議會票數:多={res.tally['多']} 空={res.tally['空']} "
        f"中性={res.tally['中性']} 平均信心={res.tally['avg_conviction']}\n各人最終意見:\n{votes_block}\n\n"
        f"正反方對照:\n{res.ledger or '(略)'}\n\n"
        f"【任務】你是主席,用繁體中文 4-6 句做今日結論:(1) 綜合票數的整體傾向;"
        f"(2) 點出交叉辯論中最關鍵的一次交鋒(誰戳中誰);(3) 一句具體可執行的觀察/紀律提醒。"
        f"只建議、不下單,不要捏造數字。"
    )
    conclusion, ok = ask_for(default_model)(chair_sys, chair_user, 460)
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
) -> CouncilResult:
    """Convenience: load personas and run a (multi-model) cross-examination council
    locally. ``council_models`` assigns a model to each seat positionally
    (round-robin if shorter). Empty → every seat uses ``model``."""
    personas = personas or load_personas(settings)
    council = [personas[n] for n in council_names if n in personas]
    chair = personas.get(chair_name)
    models: dict[str, str] = {}
    if council_models:
        for i, name in enumerate(council_names):
            models[name] = council_models[i % len(council_models)]
    res = run_council(topic, brief, council=council, chair=chair,
                      models=models, default_model=model)
    if not council:
        res.note = f"none of {council_names} found in roster {sorted(personas)}"
    return res
