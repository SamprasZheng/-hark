"""Screenshot understanding for the Discord bot — OCR + semantic eval, LOCAL by default.

Two modes the principal asked for:
  • portfolio  — read a portfolio / 持倉 screenshot (his OR someone else's), extract the
                 holdings, and give a quick risk read (concentration, leverage-ETF load,
                 obvious red flags). 評估別人的 portfolio 截圖.
  • factcheck  — read a screenshot of a POST / P&L / 對帳 claim and surface what is
                 checkable vs suspicious (impossible returns, scam language, round-number
                 PnL, "a screenshot is not proof"). 查核截圖貼文.

Privacy: runs on the LOCAL Ollama vision model on the principal's GPU by default — a
portfolio screenshot is private financial data and must NOT be shipped to a cloud API
unless explicitly opted in. OCR is the floor; the value is the structured extract +
the risk/credibility read on top. Recommend-only / research; never trades.

The vision CALL is the only network part. Everything else (model pick, JSON parse, the
portfolio risk read, the fact-check red-flag heuristics) is PURE and unit-tested offline.
"""
from __future__ import annotations

import base64
import json
import re
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

OLLAMA_URL = "http://127.0.0.1:11434"

# Vision-capable Ollama models, in preference order (first one present wins).
VISION_MODELS = ["qwen2.5vl:7b", "qwen2-vl:7b", "llama3.2-vision:11b",
                 "minicpm-v:8b", "llava:13b", "moondream:latest"]
_VISION_HINTS = ("vl", "vision", "llava", "minicpm-v", "moondream")


# ─── Pure helpers ───────────────────────────────────────────────────────────────
def pick_vision_model(available: list[str], preferred: str = "") -> Optional[str]:
    """Choose a vision model from the locally-pulled list. Honours `preferred`
    (exact or family match), then the VISION_MODELS order, then any name that
    looks vision-capable. None if the box has no vision model. Pure."""
    avail = list(available or [])
    wants = ([preferred] if preferred else []) + VISION_MODELS
    for want in wants:
        if not want:
            continue
        fam = want.split(":")[0]
        for a in avail:
            if a == want or a.split(":")[0] == fam:
                return a
    for a in avail:
        if any(k in a.lower() for k in _VISION_HINTS):
            return a
    return None


def parse_json_block(text: str) -> Optional[dict]:
    """Extract the first balanced {...} JSON object from a possibly-chatty vision
    reply (models love to wrap JSON in prose / ```json fences). Pure."""
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t).rstrip("`").strip()
    start = t.find("{")
    if start < 0:
        return None
    depth, in_str, esc = 0, False, False
    for i in range(start, len(t)):
        c = t[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(t[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def extract_pct(s) -> Optional[float]:
    """Pull a percentage from a string/number. Handles '12.3%', '+900%', '10x',
    '翻5倍'. Returns the percent as a float (10x → 900). Pure."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    txt = str(s)
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*%", txt)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*[xX倍]", txt)
    if m:
        return (float(m.group(1)) - 1.0) * 100.0
    return None


SCAM_PHRASES = (
    "保證", "穩賺", "穩賠", "包賺", "跟單", "帶單", "老師", "財富自由", "內線", "明牌",
    "必漲", "必賺", "百分百", "穩定獲利", "零風險", "無風險", "加我", "私訊我", "進群", "群組",
    "報明牌", "翻身", "guaranteed", "risk-free", "risk free", "can't lose", "cant lose",
    "double your", "100x", "to the moon", "financial freedom", "dm me", "join my",
)


def detect_scam_language(text: str) -> list[str]:
    """Phrases that mark a pump/跟單/scam post. Pure."""
    if not text:
        return []
    low = text.lower()
    hits = []
    for p in SCAM_PHRASES:
        if p in text or p.lower() in low:
            hits.append(p)
    return hits


def assess_portfolio(parsed: dict) -> dict:
    """Rule-based risk read on the extracted holdings — concentration, leverage-ETF
    load, breadth, and obviously-suspicious P/L. No FOM/network here. Pure."""
    from sharks.scoring.leveraged_etf import is_leveraged_etf

    holdings = [h for h in (parsed.get("holdings") or []) if isinstance(h, dict) and h.get("ticker")]
    n = len(holdings)
    weighted = [(h["ticker"], float(h["weight_pct"]))
                for h in holdings if isinstance(h.get("weight_pct"), (int, float))]
    weighted.sort(key=lambda x: -x[1])
    top = weighted[0] if weighted else (None, None)
    top3 = sum(w for _, w in weighted[:3])
    lev = [h["ticker"] for h in holdings if is_leveraged_etf(str(h["ticker"]))]
    lev_wt = round(sum(w for t, w in weighted if is_leveraged_etf(str(t))), 1)

    flags: list[str] = []
    if top[1] and top[1] >= 15:
        flags.append(f"集中度高:最大持倉 `{top[0]}` ≈ {top[1]:.0f}%")
    if top3 >= 50 and n >= 4:
        flags.append(f"前三大 ≈ {top3:.0f}% — 分散不足")
    if lev_wt >= 20:
        flags.append(f"槓桿 ETF 佔比 ≈ {lev_wt:.0f}%(每日 decay,當核心持倉用很危險)")
    elif lev:
        flags.append(f"含槓桿 ETF:{', '.join('`'+t+'`' for t in lev[:6])}")
    if 0 < n <= 3:
        flags.append("持倉檔數過少 — 個股風險大")
    # suspicious P/L
    pnls = [extract_pct(h.get("pnl_pct")) for h in holdings]
    extreme = [h["ticker"] for h, p in zip(holdings, pnls) if p is not None and p >= 300]
    if extreme:
        flags.append(f"異常高報酬({', '.join('`'+t+'`' for t in extreme[:4])})— 截圖非佐證,需原始對帳單")
    greens = [p for p in pnls if p is not None and p > 0]
    if pnls and len(greens) == len([p for p in pnls if p is not None]) and len(greens) >= 5:
        flags.append("全綠無紅 — 可能是挑時點/挑標的的展示,留意倖存者偏差")

    return {
        "n_holdings": n, "top": {"ticker": top[0], "weight_pct": top[1]},
        "top3_weight_pct": round(top3, 1),
        "leveraged": lev, "leveraged_weight_pct": lev_wt,
        "flags": flags,
    }


def factcheck_flags(parsed: dict) -> dict:
    """Credibility heuristics on an extracted post/PnL screenshot. Pure.

    Returns {checkable[], red_flags[], verdict}. We never assert true/false — we
    separate what can be verified against a primary source from what is a tell."""
    claims = [c for c in (parsed.get("claims") or []) if c]
    numbers = parsed.get("numbers") or []
    text = parsed.get("text_ocr") or ""
    notes = parsed.get("notes") or ""

    red: list[str] = []
    # impossible / extreme returns
    for nstr in numbers:
        p = extract_pct(nstr)
        if p is not None and p >= 300:
            red.append(f"宣稱報酬 {nstr} 過高 — 截圖可偽造,要原始券商對帳單/可驗證連結")
            break
    # round-number PnL (fabrication tell)
    for nstr in numbers:
        m = re.search(r"\$?\s*([\d,]{4,})", str(nstr))
        if m:
            val = m.group(1).replace(",", "")
            if val.isdigit() and int(val) >= 1000 and int(val) % 1000 == 0:
                red.append(f"整數金額({nstr})— 真實對帳很少剛好整千,留意造假")
                break
    # scam / pump language
    scam = detect_scam_language(text)
    if scam:
        red.append("出現拉群/跟單/保證字眼:" + "、".join(scam[:6]))
    # editability
    low_notes = (notes + " " + text).lower()
    if any(k in (notes + text) for k in ("截圖", "轉發", "二次", "裁切")) or "crop" in low_notes:
        red.append("看似截圖的截圖/裁切 — 易編輯,可信度低")
    red.append("⚠️ 任何截圖都不是證據(可 P 圖)— 結論需回到原始來源(券商、官方連結、鏈上)")

    checkable = []
    if parsed.get("tickers"):
        checkable.append("提到的標的可用 $hark 的 FOM/估值交叉比對(用 `/llm wiki` 或 `/ask`)")
    if claims:
        checkable.append("主張可逐條對照公開資料 / 財報 / 官方公告")
    if parsed.get("time_refs"):
        checkable.append("時間點可對該日的實際行情驗證(挑時點是常見話術)")

    verdict = "🔴 高度存疑" if len(red) >= 3 else ("🟡 需佐證" if red else "⚪ 資訊不足")
    return {"checkable": checkable, "red_flags": red, "verdict": verdict}


def verify_extracted(parsed: dict, settings, *, max_tickers: int = 6) -> dict:
    """FOM verification: cross-check the extracted tickers against REAL recent price
    action + $hark FOM dims, so a stock/PnL claim is checked against reality, not just
    heuristics. Best-effort + network; {} when offline. Heavy imports stay lazy."""
    seen: set[str] = set()
    tickers: list[str] = []
    for t in (parsed.get("tickers") or []):
        if isinstance(t, str):
            u = t.strip().upper()
            if re.fullmatch(r"[A-Z][A-Z.\-]{0,6}", u) and u not in seen:
                seen.add(u)
                tickers.append(u)
    tickers = tickers[:max_tickers]
    if not tickers:
        return {}
    try:
        import pandas as pd
        from sharks.scoring.fom import fetch_monthly, momentum_score, contrarian_score
        as_of = pd.Timestamp.today().normalize()
        start = (as_of - pd.Timedelta(days=420)).strftime("%Y-%m-%d")
        closes = fetch_monthly(tickers, start, as_of.strftime("%Y-%m-%d"))
        rows = []
        for t in tickers:
            if t in getattr(closes, "columns", []) and not closes[t].dropna().empty:
                s = closes[t].dropna()
                m1 = round(float(s.iloc[-1] / s.iloc[-2] - 1) * 100, 1) if len(s) >= 2 else None
                m3 = round(float(s.iloc[-1] / s.iloc[-4] - 1) * 100, 1) if len(s) >= 4 else None
                try:
                    mom = round(momentum_score(closes, t, as_of))
                    con = round(contrarian_score(closes, t, as_of))
                except Exception:
                    mom = con = None
                rows.append({"ticker": t, "found": True, "last": round(float(s.iloc[-1]), 2),
                             "m1_pct": m1, "m3_pct": m3, "momentum": mom, "contrarian": con})
            else:
                rows.append({"ticker": t, "found": False})
        return {"rows": rows, "as_of": as_of.strftime("%Y-%m-%d")}
    except Exception as exc:
        return {"error": str(exc)[:120], "rows": []}


def claim_vs_reality_flags(parsed: dict, verify: dict) -> list[str]:
    """Auto-flags from comparing claimed numbers to the real moves. Pure.
    (1) a claimed >=+100% move when every checked name is actually far lower;
    (2) tickers that don't exist (a fabrication tell)."""
    flags: list[str] = []
    found = [r for r in (verify.get("rows") or []) if r.get("found")]
    if found:
        claimed = [c for c in (extract_pct(n) for n in (parsed.get("numbers") or [])) if c is not None]
        big = max(claimed) if claimed else None
        if big is not None and big >= 100:
            best = max((r["m3_pct"] if r.get("m3_pct") is not None else -999) for r in found)
            if best < big * 0.5:
                flags.append(f"宣稱漲幅 ~{big:.0f}% 遠高於實際(查到的標的近3月最多 {best:.0f}%)— 與行情對不上")
    missing = [r["ticker"] for r in (verify.get("rows") or []) if not r.get("found")]
    if missing:
        flags.append("查無此標的(代碼可疑):" + "、".join("`" + t + "`" for t in missing[:5]))
    return flags


def _deep_web_verify(parsed: dict, settings) -> Optional[str]:
    """Route the extracted claims through the bot's read-only Claude+WebSearch
    loopback for a current-facts verdict. Opt-in (slower / costs a few cents)."""
    claims = parsed.get("claims") or []
    text = parsed.get("text_ocr") or ""
    if not (claims or text):
        return None
    try:
        from sharks.discord.brains import ask_claude_research
    except Exception:
        return None
    q = ("查核以下從截圖抽出的主張:用 WebSearch 找當前事實,逐條標 [可信/存疑/查無],"
         "最後一行給一句總評。只做查核,非投資建議,不要捏造。\n主張:\n- "
         + "\n- ".join(str(c) for c in claims[:6])
         + (f"\n原文:{text[:400]}" if text else ""))
    rep = ask_claude_research(q, settings)
    return rep.text if getattr(rep, "ok", False) else None


# ─── Prompts (kept terse; vision models follow short JSON-only instructions best) ─
PORTFOLIO_PROMPT = (
    "你是投資組合截圖判讀器。畫面是一張券商/持倉截圖。只輸出 JSON,不要任何其他文字:\n"
    '{"account":"<帳戶名或null>","currency":"<USD/TWD等>",'
    '"holdings":[{"ticker":"<代碼>","name":"<名稱或null>","weight_pct":<數字或null>,'
    '"value":<數字或null>,"pnl_pct":<數字或null>}],'
    '"totals":{"total_value":<數字或null>,"day_pnl_pct":<數字或null>},'
    '"notes":"<看不清或不確定的地方>"}\n'
    "逐筆照抓,看不清的欄位填 null,絕不編造代碼或數字。"
)
FACTCHECK_PROMPT = (
    "你是貼文/截圖查核器。畫面可能是社群貼文、損益截圖或對帳。只輸出 JSON,不要其他文字:\n"
    '{"kind":"<post|pnl|chart|other>","author":"<帳號或null>",'
    '"claims":["<可查核的主張,逐條>"],"numbers":["<關鍵數字/報酬率/金額>"],'
    '"tickers":["<提到的代碼>"],"time_refs":["<日期/時間>"],'
    '"text_ocr":"<畫面主要文字逐字>","notes":"<看不清或可疑處,如裁切/浮水印>"}\n'
    "逐字抓,先不要判斷真假。看不清填 null 或空陣列。"
)


# ─── Vision call (the only network part) ────────────────────────────────────────
def vision_chat(image_bytes: bytes, prompt: str, settings, *, model: str = "",
                base_url: str = OLLAMA_URL, timeout: int = 120) -> dict:
    """One image + prompt to a LOCAL Ollama vision model. {ok,text,model,error}.
    Never raises — a down daemon / missing model comes back as ok=False."""
    from sharks.discord.brains import list_ollama_models
    avail = list_ollama_models(base_url)
    chosen = pick_vision_model(avail, model or getattr(settings, "vision_model", "") or "")
    if not chosen:
        return {"ok": False, "text": "", "model": None,
                "error": ("本地沒有 vision 模型。先拉一個(在 GPU 機上跑):\n"
                          "`ollama pull qwen2.5vl`  或  `ollama pull llama3.2-vision`")}
    payload = {
        "model": chosen, "stream": False,
        "messages": [{"role": "user", "content": prompt,
                      "images": [base64.b64encode(image_bytes).decode("ascii")]}],
        "options": {"temperature": 0.1},
    }
    try:
        req = urllib.request.Request(
            f"{base_url}/api/chat", data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
        text = ((data.get("message") or {}).get("content") or "").strip()
        if not text:
            return {"ok": False, "text": "", "model": chosen, "error": "vision 模型空回應"}
        return {"ok": True, "text": text, "model": chosen, "error": None}
    except Exception as exc:  # daemon down / timeout / bad model
        return {"ok": False, "text": "", "model": chosen,
                "error": f"vision 呼叫失敗:{str(exc)[:160]}"}


# ─── Public entry points (used by the bot) ──────────────────────────────────────
@dataclass
class ShotResult:
    ok: bool
    mode: str
    model: Optional[str] = None
    parsed: dict = field(default_factory=dict)
    assessment: dict = field(default_factory=dict)
    message: str = ""
    error: Optional[str] = None


def _fmt_holding(h: dict) -> str:
    w = h.get("weight_pct")
    p = h.get("pnl_pct")
    bits = [f"`{h.get('ticker')}`"]
    if isinstance(w, (int, float)):
        bits.append(f"{w:.0f}%")
    if isinstance(p, (int, float)):
        bits.append(f"({p:+.0f}%)")
    return " ".join(bits)


def eval_portfolio_image(image_bytes: bytes, settings) -> ShotResult:
    """評估投組截圖 → 持倉抽取 + 風險讀數。"""
    vr = vision_chat(image_bytes, PORTFOLIO_PROMPT, settings)
    if not vr["ok"]:
        return ShotResult(False, "portfolio", error=vr["error"])
    parsed = parse_json_block(vr["text"]) or {}
    a = assess_portfolio(parsed)
    holdings = [h for h in (parsed.get("holdings") or []) if isinstance(h, dict) and h.get("ticker")]
    lines = [f"🖼️ **投組截圖判讀** _(本地 {vr['model']} · 研究非建議)_",
             f"抓到 **{a['n_holdings']}** 檔" + (f" · 幣別 {parsed.get('currency')}" if parsed.get("currency") else "")]
    if holdings:
        lines.append("**持倉**:" + " · ".join(_fmt_holding(h) for h in holdings[:18]))
    if a["flags"]:
        lines.append("\n**⚠️ 風險讀數**")
        lines += [f"• {f}" for f in a["flags"]]
    else:
        lines.append("\n**讀數**:無明顯集中/槓桿紅旗(仍非建議)")
    if parsed.get("notes"):
        lines.append(f"\n_判讀備註:{parsed['notes']}_")
    lines.append("_截圖判讀可能誤判;要精算就把代碼貼進 `/portfolio` 後續或 `/ask`。_")
    return ShotResult(True, "portfolio", model=vr["model"], parsed=parsed,
                      assessment=a, message="\n".join(lines))


def factcheck_image(image_bytes: bytes, settings, *, verify: bool = True,
                    deep_web: bool = False) -> ShotResult:
    """查核貼文/損益截圖 → 主張抽取 + 啟發式紅旗 + (FOM)實際數據對照 + (選用)web 查核。"""
    vr = vision_chat(image_bytes, FACTCHECK_PROMPT, settings)
    if not vr["ok"]:
        return ShotResult(False, "factcheck", error=vr["error"])
    parsed = parse_json_block(vr["text"]) or {}
    fc = factcheck_flags(parsed)

    ver: dict = {}
    if verify:
        ver = verify_extracted(parsed, settings)
        mismatch = claim_vs_reality_flags(parsed, ver)
        if mismatch:
            fc["red_flags"] = mismatch + fc["red_flags"]
            n = len(fc["red_flags"])
            fc["verdict"] = "🔴 高度存疑" if n >= 3 else ("🟡 需佐證" if n else "⚪ 資訊不足")
    web = _deep_web_verify(parsed, settings) if deep_web else None

    def _p(v):
        return f"{v:+.0f}%" if isinstance(v, (int, float)) else "—"

    lines = [f"🔎 **截圖查核** · {fc['verdict']} _(本地 {vr['model']} · 研究非建議)_"]
    if parsed.get("kind"):
        lines.append(f"類型:{parsed['kind']}" + (f" · {parsed.get('author')}" if parsed.get("author") else ""))
    claims = parsed.get("claims") or []
    if claims:
        lines.append("\n**主張**")
        lines += [f"• {c}" for c in claims[:6]]
    if fc["red_flags"]:
        lines.append("\n**🚩 疑點**")
        lines += [f"• {f}" for f in fc["red_flags"]]
    if ver.get("rows"):
        lines.append(f"\n**📊 對照實際(近月 · $hark FOM/yfinance · as_of {ver.get('as_of')})**")
        for r in ver["rows"]:
            if r.get("found"):
                extra = (f" · 動能{r['momentum']:.0f}/逆勢{r['contrarian']:.0f}"
                         if r.get("momentum") is not None else "")
                lines.append(f"• `{r['ticker']}` ${r.get('last')} · 近1月 {_p(r.get('m1_pct'))} · 近3月 {_p(r.get('m3_pct'))}{extra}")
            else:
                lines.append(f"• `{r['ticker']}` ⚠️ 查無此標的")
    elif ver.get("error"):
        lines.append(f"\n_(實際數據對照失敗:{ver['error']})_")
    if web:
        lines.append("\n**🌐 Web 查核(Claude+WebSearch · 唯讀)**")
        lines.append(web[:1100])
    if fc["checkable"]:
        lines.append("\n**✅ 可這樣查核**")
        lines += [f"• {c}" for c in fc["checkable"]]
    return ShotResult(True, "factcheck", model=vr["model"], parsed=parsed,
                      assessment={**fc, "verify": ver, "web": bool(web)},
                      message="\n".join(lines))
