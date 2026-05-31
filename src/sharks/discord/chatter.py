"""#雜談 chatter — hourly news → 速解讀 因果鏈 on the LOCAL model.

Every hour the bot fetches the latest free-RSS tech/政經/market headlines
(sharks.news_fetch) and asks the local Ollama model to weave them into a 游庭澔-style
速解讀 causal chain (這些事 → 方向/類股 → 對 NVDA/費半/台股 AI 鏈的含義), posted to
#雜談. Periodically the council also debates the headlines there.

The LLM call is injected (ask_fn) so the compose logic is testable offline. Local +
free + private (RTX 5070); needs Ollama up — degrades gracefully if not.
Recommend-only / educational — never an order.
"""

from __future__ import annotations

from typing import Callable, Optional

# ask_fn(system, user, max_tokens) -> (text, ok)
AskFn = Callable[[str, str, int], tuple[str, bool]]

CHATTER_SYS = (
    "你是游庭澔式的『財經速解讀』員,專長把零散的科技/政經/市場新聞串成因果鏈。"
    "只做研究判讀,不喊單、不下單、不捏造數字或價格。繁體中文,務實、鮮明、精簡。"
)


def fetch_headlines(n: int = 8) -> tuple[list[str], list[str]]:
    """Latest market/tech/政經 headlines via the free-RSS aggregator. Network."""
    from sharks.news_fetch import collect
    agg = collect(max_total=n)
    return [it["title"] for it in agg["items"]], agg["sources_ok"]


def quick_take(headlines: list[str], ask_fn: AskFn, max_tokens: int = 420) -> tuple[str, bool]:
    """One LLM pass: headlines → 速解讀 因果鏈. PURE given ask_fn (no network)."""
    if not headlines:
        return "", False
    hl = "\n".join(f"- {h}" for h in headlines)
    user = (
        f"以下是最近一小時各大科技/政經/市場頭條:\n{hl}\n\n"
        f"【任務】用 3-5 句把它們串成因果鏈:\n"
        f"① 最關鍵的 1-2 條是什麼、為什麼重要;\n"
        f"② 它們指向哪個方向(risk-on / risk-off、利率、哪些類股強弱);\n"
        f"③ 對 NVDA / 費半 / 台股 AI 鏈的隔日含義。\n"
        f"鮮明但務實,不喊單、不下單。"
    )
    return ask_fn(CHATTER_SYS, user, max_tokens)


def compose_chatter(model: str = "qwen2.5:7b", n: int = 8,
                    ask_maker: Optional[Callable[[str], tuple[AskFn, str]]] = None) -> dict:
    """Fetch headlines + run the 速解讀 on the local model. Returns a dict for the
    bot to render. ``ask_maker`` defaults to the council's local Ollama client."""
    if ask_maker is None:
        from sharks.discord.council import make_local_ask
        ask_maker = make_local_ask
    headlines, ok_sources = fetch_headlines(n)
    ask, backend = ask_maker(model)
    take, ok = quick_take(headlines, ask)
    return {"headlines": headlines, "sources_ok": ok_sources,
            "take": take, "ok": ok, "backend": backend, "model": model}


def council_topic_from_news(headlines: list[str]) -> tuple[str, str]:
    """Build a (topic, brief) for a council debate seeded by the latest headlines."""
    topic = "根據最新頭條,接下來整體該偏多還偏空?最該盯的風險是什麼?"
    brief = "最新科技/政經/市場頭條:\n" + "\n".join(f"- {h}" for h in headlines[:10])
    return topic, brief
