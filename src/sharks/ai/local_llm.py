"""Local LLM integration — Ollama / llama.cpp.

支援:
  1. Ollama(最簡單)— http://localhost:11434
  2. llama.cpp server — http://localhost:8080
  3. LM Studio — OpenAI-compatible endpoint

用途:
  - 生成個股 thesis(摘要 deep_research)
  - 反方論點(Devil's Advocate)
  - 新聞 sentiment
  - 自訂 prompt 分析

優勢:
  - 完全本地、無 API 成本
  - 隱私保護(你的 portfolio 不外流)
  - 內化你的系統知識(可微調)
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2:3b"  # 輕量、快、夠用


def check_ollama_running() -> bool:
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def list_local_models() -> list:
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
            data = json.loads(r.read().decode("utf-8"))
            return [m.get("name") for m in data.get("models", [])]
    except Exception:
        return []


def generate(prompt: str, model: str = DEFAULT_MODEL, system: str = None,
             max_tokens: int = 500, temperature: float = 0.3) -> str:
    """Call Ollama /api/generate."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens, "temperature": temperature},
    }
    if system:
        payload["system"] = system
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(OLLAMA_URL, data=data,
                                       headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            result = json.loads(r.read().decode("utf-8"))
            return result.get("response", "")
    except Exception as e:
        return f"[ERROR: {e}]"


# ─── Prompts ───
SYSTEM_ANDYSHARKS = """你是 Sharks / PolkaSharks 鯊魚交易系統的分析師。
你的個性:
  - 銳利、直接、數據驅動
  - 自嘲幽默(承認錯誤)
  - 強烈意見但有依據
  - 不財務建議,但分享系統訊號

你的知識:
  - Buffett 3M(Moat/Management/Margin)
  - 多週期理論(BTC halving + Presidential + Sector seasonality)
  - 5 維 FOM 評分系統
  - 籌碼面 + 量價背離
  - 妖股年特徵(2026 確認)

回答要簡潔、有重點、用 markdown 結構化。
"""


def generate_thesis(ticker: str, deep_research_data: dict, model: str = DEFAULT_MODEL) -> str:
    """產出推薦理由 / thesis。"""
    moat = deep_research_data.get("🏰 moat_analysis", {})
    ev = deep_research_data.get("🎯 evidence_check", [])
    risks = deep_research_data.get("⚠️ risk_check", [])
    verdict = deep_research_data.get("📋 verdict", "?")

    prompt = f"""根據以下 deep research 數據,為 {ticker} 產出一段「推薦理由」:

公司:{deep_research_data.get('company_name', ticker)}
產業:{deep_research_data.get('sector', '?')}

護城河:{moat.get('moat_score_buffett', '?')}/100,{moat.get('moat_type', '?')}
原則:{moat.get('thesis', '?')}

證據:{chr(10).join(ev[:8])}
風險:{chr(10).join(risks[:5])}

系統判決:{verdict}

請用 PolkaSharks 鯊魚風格寫一段 100-150 字的推薦理由,
要點:為什麼買、進場區、停損、何時出。
"""
    return generate(prompt, model=model, system=SYSTEM_ANDYSHARKS,
                     max_tokens=400, temperature=0.4)


def generate_devils_advocate(ticker: str, deep_research_data: dict, model: str = DEFAULT_MODEL) -> str:
    """產出反方論點(Devil's Advocate)— 為什麼不該買。"""
    risks = deep_research_data.get("⚠️ risk_check", [])

    prompt = f"""你是反方論點分析師,專門打臉系統推薦。

針對 {ticker} 的系統判決「{deep_research_data.get('📋 verdict', '?')}」,
請列出 3 個強烈反對理由 + 1 個可能讓推薦失效的情境。

已知風險:{chr(10).join(risks[:5])}

請冷靜尖銳,不要為了反對而反對。
"""
    return generate(prompt, model=model, system="你是嚴格的反方論點分析師。",
                     max_tokens=300, temperature=0.5)


def summarize_news(ticker: str, news_texts: list, model: str = DEFAULT_MODEL) -> dict:
    """摘要新聞 + sentiment 評估。"""
    if not news_texts:
        return {"sentiment": "neutral", "summary": "no news"}
    news_blob = "\n\n".join(news_texts[:5])
    prompt = f"""分析以下 {ticker} 相關新聞,給出:
1. Sentiment(-1 to +1)
2. 100 字以內摘要
3. 對股價的潛在影響(short / medium term)

新聞:
{news_blob[:3000]}
"""
    resp = generate(prompt, model=model, max_tokens=400, temperature=0.2)
    return {"raw_response": resp, "ticker": ticker}


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    print("Checking Ollama...", file=sys.stderr)
    if not check_ollama_running():
        print("⚠️ Ollama 未啟動", file=sys.stderr)
        report = {
            "status": "OLLAMA_NOT_RUNNING",
            "setup": [
                "1. 安裝 Ollama: https://ollama.com/download/windows",
                "2. 啟動 Ollama Desktop(背景跑)",
                "3. 拉模型: `ollama pull llama3.2:3b`(2GB,輕量)",
                "    或:`ollama pull qwen2.5:7b`(中文好,4GB)",
                "    或:`ollama pull deepseek-r1:7b`(推理強,4GB)",
                "4. 重跑此模組",
            ],
            "recommended_models_for_finance": {
                "llama3.2:3b": "通用,2GB,RTX 5070 跑超快",
                "qwen2.5:7b": "中文強,4GB",
                "deepseek-r1:7b": "推理強,適合分析",
                "phi3.5:3.8b": "Microsoft,小但聰明",
            },
        }
    else:
        models = list_local_models()
        print(f"  Ollama 跑中,模型:{models}", file=sys.stderr)
        # Try generate
        test_prompt = "用一句話介紹 Sharks 系統(中文)"
        resp = generate(test_prompt, max_tokens=100)
        report = {
            "status": "OK",
            "local_models": models,
            "test_response": resp,
            "ready_for": [
                "generate_thesis(ticker, deep_research_data)",
                "generate_devils_advocate(ticker, deep_research_data)",
                "summarize_news(ticker, news_texts)",
            ],
        }

    out_path = out_dir / f"local-llm-status-{today}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
