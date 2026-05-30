"""PolkaSharks Sharks Dashboard — Streamlit MVP.

每頁 = 一張投影片,適合錄影:
  1. 🦈 Welcome
  2. 🚨 Alert Status
  3. 🎯 Today's Top Picks
  4. 💎 Bubble Chart Explorer
  5. 📊 Filter Table
  6. 📉 Portfolio Risk
  7. 🔄 Multi-Model Compare
  8. 🩹 2022 Oversold Recovery
  9. 🔥 Bubble Watch
  10. 📋 System Audit
  11. 🧠 Deep Research + AI(本地 LLM)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Make sharks package importable when run from project root
_PROJECT_ROOT = Path("D:/DOT/$hark")
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# ─── Config ───
st.set_page_config(
    page_title="🦈 PolkaSharks — Sharks System",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for shark/finance aesthetic
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #0f1419 0%, #1a2330 100%); }
    .main h1 { color: #00d4ff; font-weight: 800; }
    .main h2 { color: #4dd0e1; border-bottom: 2px solid #00d4ff; padding-bottom: 8px; }
    .main h3 { color: #80deea; }
    .stMetric { background: #1c2832; padding: 16px; border-radius: 8px; border: 1px solid #2c3e50; }
    .stMetric [data-testid="stMetricLabel"] { color: #80deea; }
    .stDataFrame { border: 1px solid #2c3e50; }
    div[data-testid="stMetricValue"] { color: #00d4ff; font-size: 32px; }
    .alert-red { background: linear-gradient(135deg, #c62828, #8b0000); padding: 20px; border-radius: 12px; color: white; }
    .alert-yellow { background: linear-gradient(135deg, #f57c00, #ef6c00); padding: 20px; border-radius: 12px; color: white; }
    .alert-green { background: linear-gradient(135deg, #2e7d32, #1b5e20); padding: 20px; border-radius: 12px; color: white; }
</style>
""", unsafe_allow_html=True)

OUT = Path("D:/DOT/$hark/outputs")


# ─── Helpers ───
@st.cache_data(ttl=3600)
def load_latest(prefix: str):
    files = sorted(OUT.glob(f"{prefix}*.json"), reverse=True)
    if not files:
        return None
    try:
        return json.loads(files[0].read_text(encoding="utf-8"))
    except Exception:
        return None


# ─── Sidebar nav ───
st.sidebar.markdown("# 🦈 PolkaSharks")
st.sidebar.markdown("**Sharks 交易系統**")
st.sidebar.markdown("---")

page = st.sidebar.radio("導航 / Navigation", [
    "🦈 1. Welcome",
    "🚨 2. Alert Status",
    "🎯 3. Today's Top Picks",
    "💎 4. Bubble Chart Explorer",
    "📊 5. Filter Table",
    "📉 6. Portfolio Risk",
    "🔄 7. Multi-Model Compare",
    "🩹 8. 2022 Oversold Recovery",
    "🔥 9. Bubble Watch",
    "📋 10. System Audit",
    "🧠 11. Deep Research + AI",
])

st.sidebar.markdown("---")
st.sidebar.markdown("⚡ **Backtest**: +975% (10y)")
st.sidebar.markdown("📊 **vs SPY**: +846% alpha")
st.sidebar.markdown("🛡️ **Sharpe**: ~1.0")


# ─── PAGE 1: Welcome ───
if "Welcome" in page:
    st.markdown("# 🦈 PolkaSharks — Sharks Trading System")
    st.markdown("### *Data-driven sharks hunting alpha across markets*")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎯 10y Backtest", "+975%", "+846% vs SPY")
    col2.metric("📊 Coverage", "30%", "→ 80% (本週)")
    col3.metric("🔄 Models", "9", "FOM + 變體")
    col4.metric("🚨 Alert", "YELLOW", "BTC 🔴 / GLD 🟡")

    st.markdown("---")
    st.markdown("## 🎯 System Promise")
    st.markdown("""
    - ✅ **Backtest 8.5× SPY** (2016-2026 real data)
    - ✅ **9 維度交叉驗證** — momentum + contrarian + cyclic + quality + bubble + buffett + chip flow + meme + breadth
    - ✅ **誠實揭露** — 自我打臉(ORCL case)
    - ✅ **Adaptive** — postmortem feedback + IC measurement
    - ⚠️ **非投資建議** — 純研究 / 系統訊號分享
    """)

    st.markdown("---")
    st.info("👈 從左側選擇頁面開始")


# ─── PAGE 2: Alert Status ───
elif "Alert Status" in page:
    st.markdown("# 🚨 警報狀態 / Alert Status")
    st.markdown("---")

    liquidity = load_latest("liquidity-signals")
    breadth = load_latest("breadth-indicator")

    if liquidity:
        comp = liquidity.get("composite_alert", {})
        level = comp.get("level", "?")
        col1, col2 = st.columns([1, 3])
        with col1:
            color = {"GREEN": "alert-green", "YELLOW": "alert-yellow",
                     "ORANGE": "alert-yellow", "RED": "alert-red"}.get(level, "alert-yellow")
            st.markdown(f"""<div class="{color}"><h1 style="margin:0;">{level}</h1>
            <p>{comp.get('headline', '')}</p></div>""", unsafe_allow_html=True)
        with col2:
            m2 = liquidity.get("m2_signal", {})
            btc = liquidity.get("btc_signal", {})
            gld = liquidity.get("gold_signal", {})
            st.markdown("### 三大流動性訊號")
            c1, c2, c3 = st.columns(3)
            c1.metric("💵 M2", f"+{m2.get('yoy_growth_pct', '?')}% YoY",
                       "🟢 支持" if not m2.get("is_bearish") else "🔴 警示")
            c2.metric("🪙 BTC", f"${btc.get('last_price', '?'):,.0f}",
                       f"-{btc.get('dist_from_high_pct', '?')}% 距高")
            c3.metric("🥇 黃金 GLD", f"${gld.get('last_price', '?'):.2f}",
                       f"+{gld.get('r6_pct', '?')}% 6m")

    st.markdown("---")

    if breadth:
        st.markdown("### 📏 市場寬度(NDTW / R2TW)")
        verdict = breadth.get("verdict", "?")
        ndx = breadth.get("ndx_breadth_sample", {})
        rut = breadth.get("rut_breadth_sample", {})
        c1, c2, c3 = st.columns(3)
        c1.metric("📊 NDX > 50MA", f"{ndx.get('above_50ma_pct', 0):.0f}%")
        c2.metric("📊 RUT > 50MA", f"{rut.get('above_50ma_pct', 0):.0f}%")
        c3.metric("🎯 判定", verdict)
        if verdict == "OVERHEATED":
            st.error(f"🔥 {breadth.get('interpretation', '')}")
            for r in breadth.get("overheated_reasons", []):
                st.write(f"- {r}")


# ─── PAGE 3: Today's Top Picks ───
elif "Top Picks" in page:
    st.markdown("# 🎯 Today's Top Picks")
    st.markdown("---")

    fom = load_latest("fom-alpha")
    if fom:
        st.markdown("## 🥇 SP500 Top 3 — 大盤穩健 Alpha")
        cols = st.columns(3)
        for i, p in enumerate(fom.get("top_3_sp500_eligible", [])[:3]):
            with cols[i]:
                st.markdown(f"### {p['ticker']}")
                st.metric("FOM", f"{p['final_fom_alpha']:.1f}")
                st.write(f"🟢 Momentum: {p['momentum']}")
                st.write(f"🔵 Contrarian: {p['contrarian']}")
                st.write(f"🛡️ Bubble: {p['bubble_guard']}")
                st.write(f"🏛️ Buffett: {p.get('buffett_value', 'N/A')}")
                if p.get("trump_policy_bonus", 0) > 0:
                    st.success(f"🇺🇸 Trump +{p['trump_policy_bonus']}")
                if p.get("golden_cross_bonus", 0) > 0:
                    st.info("✨ Golden Cross")

        st.markdown("---")
        st.markdown("## 💎 Russell 2000 Top 3 — 小型股 Alpha")
        cols = st.columns(3)
        for i, p in enumerate(fom.get("top_3_r2k_eligible", [])[:3]):
            with cols[i]:
                st.markdown(f"### {p['ticker']}")
                st.metric("FOM", f"{p['final_fom_alpha']:.1f}")
                st.write(f"🟢 Momentum: {p['momentum']}")
                st.write(f"🔵 Contrarian: {p['contrarian']}")
                st.write(f"🛡️ Bubble: {p['bubble_guard']}")


# ─── PAGE 4: Bubble Chart Explorer ───
elif "Bubble Chart" in page:
    st.markdown("# 💎 Bubble Chart Explorer")
    st.markdown("---")

    data = load_latest("github-universe-fom")
    if not data:
        st.warning("等 github-universe-fom 跑出資料")
    else:
        rows = data.get("top_100_overall", [])
        df = pd.DataFrame(rows)
        if not df.empty:
            sec = st.multiselect("Sector filter", df["sector"].dropna().unique())
            if sec:
                df = df[df["sector"].isin(sec)]
            fig = px.scatter(
                df, x="momentum", y="contrarian", size="r12m_pct",
                color="sector", hover_data=["ticker", "name", "fom"],
                text="ticker", title=f"FOM Bubble Chart — {len(df)} tickers",
                template="plotly_dark",
            )
            fig.update_traces(textposition="top center")
            fig.update_layout(height=700, plot_bgcolor="#0f1419", paper_bgcolor="#0f1419")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("**X = 順勢 momentum** | **Y = 逆勢 contrarian** | **size = 12m 漲幅**")


# ─── PAGE 5: Filter Table ───
elif "Filter Table" in page:
    st.markdown("# 📊 Filter Table — 全 716 ticker")
    st.markdown("---")

    data = load_latest("github-universe-fom")
    if data:
        rows = data.get("top_100_overall", [])
        df = pd.DataFrame(rows)
        col1, col2, col3 = st.columns(3)
        with col1:
            min_fom = st.slider("Min FOM", 0, 100, 50)
        with col2:
            max_bubble_penalty = st.slider("Max Bubble Penalty (negative)", -100, 50, -50)
        with col3:
            sectors = st.multiselect("Sectors", df["sector"].dropna().unique())

        filtered = df[(df["fom"] >= min_fom) & (df["bubble_guard"] >= max_bubble_penalty)]
        if sectors:
            filtered = filtered[filtered["sector"].isin(sectors)]
        st.dataframe(filtered, use_container_width=True, height=600)
        st.caption(f"{len(filtered)} of {len(df)} tickers")


# ─── PAGE 6: Portfolio Risk ───
elif "Portfolio Risk" in page:
    st.markdown("# 📉 Portfolio Risk Analysis")
    st.markdown("---")

    corr = load_latest("correlation-matrix")
    if corr:
        st.markdown("## 你 NVDA 集中度的真實對沖工具")
        div = corr.get("highest_diversifiers_vs_nvda", {})
        if div:
            df_div = pd.DataFrame(list(div.items())[:10], columns=["Ticker", "NVDA Correlation"])
            fig = px.bar(df_div, x="Ticker", y="NVDA Correlation", color="NVDA Correlation",
                         color_continuous_scale="RdYlGn_r", title="最強分散工具(負相關 = 真對沖)",
                         template="plotly_dark")
            fig.update_layout(height=500, plot_bgcolor="#0f1419", paper_bgcolor="#0f1419")
            st.plotly_chart(fig, use_container_width=True)

        bear = corr.get("bear_hedge_effectiveness", {})
        if bear:
            st.markdown("## 黑天鵝對沖效果")
            cols = st.columns(len(bear))
            for i, (k, v) in enumerate(bear.items()):
                with cols[i]:
                    emoji = "🔴" if v < -0.3 else "🟡" if v < 0 else "🟢"
                    st.metric(f"{emoji} {k}", f"{v:.2f}")


# ─── PAGE 7: Multi-Model Compare ───
elif "Multi-Model" in page:
    st.markdown("# 🔄 Multi-Model Comparison")
    st.markdown("---")
    st.info("⏳ Phase B 開發中 — 7 個模型(積極/保守/追漲/主力/技術/基本/綜合)同 ticker 多角度評分")

    st.markdown("""
    | 模型 | 邏輯 | 建議場景 |
    |---|---|---|
    | **Aggressive 積極** | Momentum 50% + Bubble -25% | 牛市末段 |
    | **Conservative 保守** | Buffett 40% + Quality 30% | 熊市 / 升息 |
    | **Trend 追漲** | Pure momentum + Golden cross | 強勢市 |
    | **Smart Money 主力** | Chip flow 50% + Inst change 30% | 多空轉折 |
    | **Technical 技術** | TD-9 + Bollinger + MA | 短線 swing |
    | **Fundamental 基本** | Buffett 3M 50% + Sector growth | 長線 |
    | **Ensemble 綜合** | 6 模型 voting | 全市況 |
    """)
    st.markdown("---")
    st.markdown("### 🎯 投票規則")
    st.code("""
6+ models agree → STRONG_BUY (max position)
4-5 agree       → BUY (standard position)
2-3 agree       → WATCH
0-1 agree       → SKIP
    """)


# ─── PAGE 8: 2022 Oversold Recovery ───
elif "Oversold Recovery" in page:
    st.markdown("# 🩹 2022 升息錯殺股回升")
    st.markdown("### 在升息中跌 50%+ 但剛開始爬升的中型股")
    st.markdown("---")

    data = load_latest("oversold-2022-recovery")
    if data:
        rows = data.get("top_25_overall", [])[:10]
        df = pd.DataFrame(rows)
        st.markdown(f"### Top {len(df)} 候選")
        st.dataframe(df[["rank", "ticker", "drawdown_from_2021_high_pct",
                          "recovery_from_low_pct", "dist_below_2021_high_pct",
                          "current_price", "h2021_high", "low_2022"]],
                     use_container_width=True, height=400)

        st.markdown("---")
        st.markdown("## 🥇 觀察候選 — Top 3 鯊魚精選")
        cols = st.columns(3)
        for i, r in enumerate(rows[:3]):
            with cols[i]:
                st.markdown(f"### {r['ticker']}")
                st.metric("跌幅", f"-{r['drawdown_from_2021_high_pct']:.0f}%")
                st.metric("反彈", f"+{r['recovery_from_low_pct']:.0f}%")
                st.metric("仍距 2021 高", f"-{r['dist_below_2021_high_pct']:.0f}%")
                st.write(r["notes"])


# ─── PAGE 9: Bubble Watch ───
elif "Bubble Watch" in page:
    st.markdown("# 🔥 Bubble Watch — 系統警告過熱清單")
    st.markdown("---")

    data = load_latest("fom-alpha")
    if data:
        bubble = data.get("ranked_full") or data.get("top_50_watchlist", [])
        if bubble:
            df = pd.DataFrame(bubble)
            overheated = df[df["bubble_guard"] <= -30] if "bubble_guard" in df.columns else df.head(10)
            st.warning(f"🔴 {len(overheated)} 隻 bubble_guard 低於 -30 — 不要追!")
            st.dataframe(overheated[["ticker", "final_fom_alpha", "momentum",
                                       "bubble_guard"]].head(20), use_container_width=True)

    meme = load_latest("meme-squeeze-hunter")
    if meme:
        st.markdown("---")
        st.markdown("## 🔥 妖股年現役 PUMP 警告")
        for p in meme.get("top_25_by_score", [])[:10]:
            with st.expander(f"⚠️ {p['ticker']} — score {p['squeeze_score']}"):
                st.write(f"1m: {p['r1m_pct']}% / 1y: {p['r12m_pct']}% / 距 12m 高: -{p['dist_from_12m_high_pct']}%")
                st.write(f"Flags: {', '.join(p['flags'])}")


# ─── PAGE 10: System Audit ───
elif "System Audit" in page:
    st.markdown("# 📋 System Audit — 透明度檢討")
    st.markdown("---")

    st.markdown("## ✅ 已驗證有效")
    col1, col2 = st.columns(2)
    with col1:
        st.success("- 2016-2026 backtest +975%(SPY +129%)")
        st.success("- NVDA 從 2016/04 抓 55 次 top 3")
        st.success("- ORCL drawdown_acceleration 抓破絕(原則旗的)")
        st.success("- 5 訊號同向 OVERHEATED")
    with col2:
        st.success("- Correlation 揭露假分散(MSFT/META 跟 NVDA 0.6+)")
        st.success("- Postmortem 公開承認錯誤")
        st.success("- 系統 backtest 對沖 SPY")

    st.markdown("---")
    st.markdown("## 🚨 已知漏洞(不藏)")
    col1, col2 = st.columns(2)
    with col1:
        st.warning("- Universe coverage 之前只 6%(今天升 30%)")
        st.warning("- fom.py v2 buffett_value 沒真正部署")
        st.warning("- Persistence 跨週沒實際追蹤")
    with col2:
        st.error("- 沒真實 Form 4 insider")
        st.error("- 沒真實 13F")
        st.error("- 沒新聞 sentiment")

    st.markdown("---")
    st.markdown("## 🎯 升級路線")
    st.markdown("""
    | Phase | 時程 | 升級 |
    |---|---|---|
    | A | 2-4 週 | Fama-French + IC |
    | B | 1-2 月 | XGBoost + RL 動態權重 |
    | C | 1 月 | Markowitz / Risk parity / Kelly |
    | D | 3+ 月 | IB / Alpaca read-only + paper trading |
    """)


# ─── PAGE 11: Deep Research + AI ───
elif "Deep Research" in page:
    st.markdown("# 🧠 Deep Research + AI Analysis")
    st.markdown("### *深度研究 + 本地 LLM 增強(內化 > 抓取)*")
    st.markdown("---")

    # Lazy import — only when this page is open
    try:
        from sharks.ai import local_llm as _llm
        LLM_AVAILABLE = True
    except Exception as e:
        LLM_AVAILABLE = False
        _llm_err = str(e)

    data = load_latest("deep-research")
    if not data:
        st.warning("⏳ 還沒有 deep-research 結果 — 跑 `python -m sharks.scoring.deep_research` 先")
        st.stop()

    reports = data.get("reports", {})
    tickers = sorted(reports.keys())

    # ─── Selector ───
    col_sel, col_status = st.columns([2, 1])
    with col_sel:
        ticker = st.selectbox("選擇 ticker 看深度研究", tickers, index=0)
    with col_status:
        if LLM_AVAILABLE and _llm.check_ollama_running():
            models = _llm.list_local_models()
            st.success(f"🧠 Ollama OK ({len(models)} 模型)")
            model_choice = st.selectbox("本地模型", models or [_llm.DEFAULT_MODEL])
        else:
            st.warning("⚠️ Ollama 未啟動")
            st.caption("裝 https://ollama.com,跑 `ollama pull llama3.2:3b`")
            model_choice = None

    if not ticker:
        st.stop()

    r = reports[ticker]
    st.markdown("---")

    # ─── Header card ───
    verdict_emoji = {
        "STRONG_BUY": "🟢🟢", "BUY": "🟢", "WATCH": "🟡",
        "AVOID": "🔴", "STRONG_AVOID": "🔴🔴",
    }
    verdict = r.get("📋 verdict", "?")
    emoji = verdict_emoji.get(verdict, "⚪")

    st.markdown(f"## {emoji} {ticker} — {r.get('company_name', ticker)}")
    st.caption(f"📦 {r.get('sector', '?')} / {r.get('industry', '?')} · "
                f"as_of: {r.get('as_of', '?')}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Verdict", verdict)
    c2.metric("🎯 Evidence Score", r.get("evidence_score", "?"))
    c3.metric("✅ Evidence Count", len(r.get("🎯 evidence_check", [])))
    c4.metric("⚠️ Risk Count", len(r.get("⚠️ risk_check", [])))

    st.markdown("---")

    # ─── 4 columns: Moat / Fundamental / Technical / Chip ───
    moat = r.get("🏰 moat_analysis", {})
    fund = r.get("💰 fundamental", {})
    tech = r.get("📊 technical_signals", {})
    chip = r.get("📉 chip_flow", {})

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 🏰 護城河 / Buffett 3M")
        if moat:
            st.metric("Moat Score (3M)", f"{moat.get('moat_score_buffett', '?')}/100")
            st.write(f"**Type**: {moat.get('moat_type', '?')}")
            st.write(f"**Mgmt**: {moat.get('mgmt_score', '?')}/100")
            st.info(f"💡 {moat.get('thesis', '?')}")
        else:
            st.caption("未在 BUFFETT_3M_DETAILED 字典 — 待補")

        st.markdown("### 💰 基本面")
        if fund:
            df_fund = pd.DataFrame([
                {"指標": "Forward PE", "值": fund.get("forward_pe", "—")},
                {"指標": "PEG", "值": fund.get("peg_ratio", "—")},
                {"指標": "ROE %", "值": fund.get("return_on_equity_pct", "—")},
                {"指標": "FCF (B)", "值": fund.get("free_cashflow_billion", "—")},
                {"指標": "Op Margin %", "值": fund.get("operating_margin_pct", "—")},
                {"指標": "Rev YoY %", "值": fund.get("revenue_growth_yoy_pct", "—")},
                {"指標": "Mkt Cap (B)", "值": fund.get("market_cap_billion", "—")},
                {"指標": "D/E", "值": fund.get("debt_to_equity", "—")},
            ])
            st.dataframe(df_fund, use_container_width=True, hide_index=True, height=320)

    with col_b:
        st.markdown("### 📊 技術面")
        if tech:
            tc1, tc2 = st.columns(2)
            tc1.metric("Price", f"${tech.get('current_price', 0):,.2f}")
            tc2.metric("距 52w 高", f"-{tech.get('dist_from_52w_high_pct', 0):.1f}%")
            st.write(f"**MA 5/12/20**: "
                      f"{tech.get('ma_5_month', '—')} / "
                      f"{tech.get('ma_12_month', '—')} / "
                      f"{tech.get('ma_20_month', '—')}")
            st.write(f"**Golden Cross**: "
                      f"{'✅' if tech.get('golden_cross_5_vs_12') else '❌'}")
            st.write(f"**TD-9**: {tech.get('td9_setup', 'NONE')}")
            st.write(f"**Bollinger**: {tech.get('bollinger_position', 'MIDDLE')}")

        st.markdown("### 📉 籌碼面")
        if chip:
            ch1, ch2, ch3 = st.columns(3)
            ch1.metric("機構持股", f"{chip.get('heldPercentInstitutions_pct', 0):.0f}%")
            ch2.metric("Short %", f"{chip.get('shortPercentOfFloat_pct', 0):.1f}%")
            ch3.metric("Insider", f"{chip.get('heldPercentInsiders_pct', 0):.2f}%")

    st.markdown("---")

    # ─── Evidence + Risk ───
    col_e, col_r = st.columns(2)
    with col_e:
        st.markdown(f"### 🎯 證據 ({len(r.get('🎯 evidence_check', []))})")
        for ev in r.get("🎯 evidence_check", []):
            st.success(ev)
    with col_r:
        st.markdown(f"### ⚠️ 風險 ({len(r.get('⚠️ risk_check', []))})")
        for rk in r.get("⚠️ risk_check", []):
            st.error(rk)

    st.markdown("---")

    # ─── AI Analysis Buttons ───
    st.markdown("## 🧠 本地 LLM 增強分析")
    if not LLM_AVAILABLE:
        st.error(f"local_llm module 載入失敗:{_llm_err}")
    elif not _llm.check_ollama_running():
        st.warning("⚠️ Ollama 未啟動 — 裝 https://ollama.com 並 `ollama pull llama3.2:3b`")
        st.code("ollama pull llama3.2:3b\nollama serve", language="powershell")
    else:
        bcol1, bcol2, bcol3 = st.columns(3)

        # Session state
        for k in ("thesis_text", "devils_text", "news_text"):
            st.session_state.setdefault(f"{ticker}_{k}", "")

        with bcol1:
            if st.button("📝 生成 Thesis", key=f"btn_thesis_{ticker}",
                           use_container_width=True):
                with st.spinner(f"🧠 {model_choice} 生成中..."):
                    text = _llm.generate_thesis(ticker, r, model=model_choice)
                    st.session_state[f"{ticker}_thesis_text"] = text

        with bcol2:
            if st.button("😈 反方論點", key=f"btn_devils_{ticker}",
                           use_container_width=True):
                with st.spinner(f"😈 {model_choice} 打臉中..."):
                    text = _llm.generate_devils_advocate(ticker, r, model=model_choice)
                    st.session_state[f"{ticker}_devils_text"] = text

        with bcol3:
            if st.button("📰 新聞摘要(stub)", key=f"btn_news_{ticker}",
                           use_container_width=True, disabled=True):
                st.info("等 Finnhub key 接通新聞")

        # ─── Render outputs ───
        thesis_t = st.session_state.get(f"{ticker}_thesis_text", "")
        if thesis_t:
            st.markdown("### 📝 PolkaSharks Thesis")
            st.markdown(f"<div style='background:#1c2832;padding:18px;"
                         f"border-left:4px solid #00d4ff;border-radius:8px;'>"
                         f"{thesis_t}</div>", unsafe_allow_html=True)

        devils_t = st.session_state.get(f"{ticker}_devils_text", "")
        if devils_t:
            st.markdown("### 😈 反方論點(Devil's Advocate)")
            st.markdown(f"<div style='background:#2d1818;padding:18px;"
                         f"border-left:4px solid #e57373;border-radius:8px;'>"
                         f"{devils_t}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("⚠️ LLM 輸出為研究輔助,非投資建議。系統 verdict + evidence 才是主軸。")
