/* 🦈 $hark Screener — 點選式前端。資料一次下發、前端過濾零延遲;recommend-only。 */
"use strict";

const $ = (id) => document.getElementById(id);
const api = async (path, opts) => {
  const r = await fetch(path, opts);
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || `${r.status} ${path}`);
  return r.headers.get("content-type")?.includes("json") ? r.json() : r.text();
};
const fmt = (v, d = 1) => (v === null || v === undefined) ? "—" : (+v).toFixed(d);
const fmtB = (v) => (v === null || v === undefined) ? "—" : (Math.abs(v) >= 1e12 ? (v / 1e12).toFixed(2) + "T" : (v / 1e9).toFixed(2) + "B");
const toast = (msg, ms = 2600) => { const t = $("toast"); t.textContent = msg; t.classList.remove("hidden"); clearTimeout(t._h); t._h = setTimeout(() => t.classList.add("hidden"), ms); };

/* ── 狀態 ── */
let ROWS = {};            // ticker -> scan row
let BREADTH = {};
let META = { tickers: [], scopes: [] };
const F = {               // 篩選器狀態
  signals: {},            // key -> 0 不限 / 1 必須 / -1 排除
  sectors: new Set(),
  rsi: [0, 100], dh: [-80, 0], dl: [0, 300],
};
let sortKey = "dist_52w_high_pct", sortDir = -1;
let screenKind = "rally", screenScope = "all";

const SIGNALS = [
  ["aligned", "連線(多頭排列)"], ["riding", "騎線(沿MA20)"],
  ["cross_ma20", "越線MA20"], ["cross_ma60", "越線MA60"],
  ["bottom", "大底(量縮+背離)"], ["rejection_bar", "拒絕棒"],
  ["above_ma50", "站上MA50"], ["above_ma200", "站上MA200"],
  ["vol_contract", "量縮"], ["rsi_divergence", "RSI背離"],
];

const PRESETS = [
  ["連騎越 Quad", { aligned: 1, riding: 1, cross_ma60: 1 }],
  ["乾淨 Quad(無拒絕棒)", { aligned: 1, riding: 1, cross_ma60: 1, rejection_bar: -1 }],
  ["大底吸籌", { bottom: 1 }],
  ["騎線推進", { riding: 1, above_ma50: 1, rejection_bar: -1 }],
  ["剛越 MA60", { cross_ma60: 1 }],
  ["創高在即", {}, { dh: [-3, 0] }],
  ["超跌深水區", {}, { dh: [-80, -30] }],
  ["RSI 低位 <40", {}, { rsi: [0, 40] }],
  ["RSI 過熱 >75", {}, { rsi: [75, 100] }],
];

const KINDS = [["rally", "起漲 rally"], ["basecross", "月線金叉 basecross"],
               ["stealth", "隱蔽吸籌 stealth"], ["ecomrank", "綜合 ecomrank"]];

/* ── 初始化 ── */
async function init() {
  if (window._noECharts) toast("⚠️ ECharts CDN 載入失敗(離線?)— 圖表無法畫,表格照常");
  renderSignalChips(); renderPresets(); renderKindChips(); bindUI();
  try {
    META = await api("/api/meta");
    $("tickerList").innerHTML = META.tickers.map(t => `<option value="${t}">`).join("");
    renderScopeChips();
    await loadScan(false);
  } catch (e) { toast("初始化失敗:" + e.message, 6000); }
}

async function loadScan(refresh) {
  toast(refresh ? "♻️ 離線重掃中…" : "讀取掃描中…");
  const rep = await api("/api/scan" + (refresh ? "?refresh=1" : ""));
  ROWS = rep.rows || {}; BREADTH = rep.sector_breadth || {};
  $("asOfChip").textContent = "as_of " + (rep.as_of || "—") + " · " + Object.keys(ROWS).length + " 檔";
  $("intradayChip").classList.toggle("hidden", !rep.intraday);
  renderSectorChips(); renderBreadth(); renderTable();
  toast("✅ 掃描就緒 as_of " + rep.as_of);
}

/* ── 篩選器渲染 ── */
function renderSignalChips() {
  $("signalChips").innerHTML = SIGNALS.map(([k, label]) =>
    `<span class="fchip" data-sig="${k}">${label}</span>`).join("");
  $("signalChips").querySelectorAll(".fchip").forEach(ch => ch.onclick = () => {
    const k = ch.dataset.sig;
    F.signals[k] = ((F.signals[k] || 0) + 2) % 3 - 1;   // 0→1→-1→0
    syncSignalChips(); renderTable();
  });
}
function syncSignalChips() {
  $("signalChips").querySelectorAll(".fchip").forEach(ch => {
    const v = F.signals[ch.dataset.sig] || 0;
    ch.classList.toggle("req", v === 1); ch.classList.toggle("exc", v === -1);
    const base = SIGNALS.find(s => s[0] === ch.dataset.sig)[1];
    ch.textContent = (v === 1 ? "✓ " : v === -1 ? "✗ " : "") + base;
  });
}
function renderPresets() {
  $("presetBtns").innerHTML = PRESETS.map(([name], i) =>
    `<span class="fchip" data-p="${i}">${name}</span>`).join("");
  $("presetBtns").querySelectorAll(".fchip").forEach(ch => ch.onclick = () => {
    const [, sigs, ranges] = PRESETS[+ch.dataset.p];
    F.signals = { ...sigs };
    Object.assign(F, { rsi: [0, 100], dh: [-80, 0], dl: [0, 300] }, ranges || {});
    syncSliders(); syncSignalChips(); renderTable();
    toast("已套用:" + PRESETS[+ch.dataset.p][0]);
  });
}
function renderSectorChips() {
  const sectors = [...new Set(Object.values(ROWS).map(r => r.sector || "Unknown"))].sort();
  $("sectorChips").innerHTML = sectors.map(s =>
    `<span class="fchip ${F.sectors.has(s) ? "on" : ""}" data-sec="${s}">${s}</span>`).join("");
  $("sectorChips").querySelectorAll(".fchip").forEach(ch => ch.onclick = () => {
    const s = ch.dataset.sec;
    F.sectors.has(s) ? F.sectors.delete(s) : F.sectors.add(s);
    ch.classList.toggle("on"); renderBreadth(); renderTable();
  });
}
function renderKindChips() {
  $("kindChips").innerHTML = KINDS.map(([v, n]) =>
    `<span class="fchip ${v === screenKind ? "on" : ""}" data-k="${v}">${n}</span>`).join("");
  $("kindChips").querySelectorAll(".fchip").forEach(ch => ch.onclick = () => {
    screenKind = ch.dataset.k;
    $("kindChips").querySelectorAll(".fchip").forEach(c => c.classList.toggle("on", c === ch));
  });
}
function renderScopeChips() {
  $("scopeChips").innerHTML = META.scopes.map(s =>
    `<span class="fchip ${s.value === screenScope ? "on" : ""}" data-s="${s.value}" title="${s.name}">${s.value}</span>`).join("");
  $("scopeChips").querySelectorAll(".fchip").forEach(ch => ch.onclick = () => {
    screenScope = ch.dataset.s;
    $("scopeChips").querySelectorAll(".fchip").forEach(c => c.classList.toggle("on", c === ch));
  });
}
function syncSliders() {
  $("rsiMin").value = F.rsi[0]; $("rsiMax").value = F.rsi[1];
  $("dhMin").value = F.dh[0]; $("dhMax").value = F.dh[1];
  $("dlMin").value = F.dl[0]; $("dlMax").value = F.dl[1];
  updateSliderLabels();
}
function updateSliderLabels() {
  $("rsiVal").textContent = `${F.rsi[0]} – ${F.rsi[1]}`;
  $("dhVal").textContent = `${F.dh[0]} – ${F.dh[1]}`;
  $("dlVal").textContent = `${F.dl[0]} – ${F.dl[1]}${F.dl[1] >= 300 ? "+" : ""}`;
}

/* ── 板塊廣度 ── */
function renderBreadth() {
  $("breadthStrip").innerHTML = Object.entries(BREADTH).map(([sec, b]) => `
    <div class="bd-row ${F.sectors.has(sec) ? "sel" : ""}" data-sec="${sec}">
      <span class="bd-name">${sec}</span>
      <span class="bd-bar"><span class="bd-fill" style="width:${b.pct_above_ma50}%"></span></span>
      <span class="bd-pct">${b.pct_above_ma50}% · ${b.n}檔</span>
    </div>`).join("");
  $("breadthStrip").querySelectorAll(".bd-row").forEach(el => el.onclick = () => {
    const s = el.dataset.sec;
    F.sectors.has(s) ? F.sectors.delete(s) : F.sectors.add(s);
    renderSectorChips(); renderBreadth(); renderTable();
  });
}

/* ── 過濾 + 表格 ── */
function passes(r) {
  for (const [k, v] of Object.entries(F.signals)) {
    if (v === 1 && !r[k]) return false;
    if (v === -1 && r[k]) return false;
  }
  if (F.sectors.size && !F.sectors.has(r.sector || "Unknown")) return false;
  if (r.rsi !== null && (r.rsi < F.rsi[0] || r.rsi > F.rsi[1])) return false;
  if (F.rsi[0] > 0 && r.rsi === null) return false;
  const dh = r.dist_52w_high_pct, dl = r.dist_52w_low_pct;
  if (dh !== null && (dh < F.dh[0] || dh > F.dh[1])) return false;
  if (dl !== null && (dl < F.dl[0] || (F.dl[1] < 300 && dl > F.dl[1]))) return false;
  return true;
}

const COLS = [
  ["ticker", "代號"], ["sector", "板塊"], ["close", "收盤"],
  ["dist_52w_high_pct", "距52w高%"], ["dist_52w_low_pct", "距52w低%"],
  ["rsi", "RSI"], ["_sigs", "訊號"], ["above_ma50", "MA50"], ["above_ma200", "MA200"],
];

function sigBadges(r) {
  let h = "";
  if (r.aligned) h += `<span class="sig a">連</span>`;
  if (r.riding) h += `<span class="sig r">騎</span>`;
  if (r.cross_ma20) h += `<span class="sig c">越20</span>`;
  if (r.cross_ma60) h += `<span class="sig c">越60</span>`;
  if (r.bottom) h += `<span class="sig b">底</span>`;
  if (r.rejection_bar) h += `<span class="sig j">拒</span>`;
  return h || "—";
}

function renderTable() {
  const rows = Object.entries(ROWS).filter(([, r]) => passes(r));
  rows.sort(([ta, a], [tb, b]) => {
    if (sortKey === "ticker") return sortDir * ta.localeCompare(tb);
    if (sortKey === "sector") return sortDir * String(a.sector).localeCompare(String(b.sector));
    if (sortKey === "_sigs") {
      const n = (r) => ["aligned", "riding", "cross_ma20", "cross_ma60", "bottom"].filter(k => r[k]).length;
      return sortDir * (n(a) - n(b));
    }
    const va = a[sortKey], vb = b[sortKey];
    if (va === null || va === undefined) return 1;
    if (vb === null || vb === undefined) return -1;
    return sortDir * (va - vb);
  });
  $("resultHead").innerHTML = COLS.map(([k, n]) =>
    `<th data-k="${k}">${n}${k === sortKey ? (sortDir > 0 ? " ▲" : " ▼") : ""}</th>`).join("");
  $("resultHead").querySelectorAll("th").forEach(th => th.onclick = () => {
    const k = th.dataset.k;
    if (k === sortKey) sortDir *= -1; else { sortKey = k; sortDir = -1; }
    renderTable();
  });
  $("rowCount").textContent = `(${rows.length} 檔)`;
  $("resultBody").innerHTML = rows.slice(0, 400).map(([t, r]) => `
    <tr data-t="${t}">
      <td class="tk">${t}</td><td>${r.sector || "—"}</td><td>${fmt(r.close, 2)}</td>
      <td class="${r.dist_52w_high_pct > -3 ? "pos" : ""}">${fmt(r.dist_52w_high_pct)}</td>
      <td>${fmt(r.dist_52w_low_pct)}</td>
      <td class="${r.rsi > 75 ? "pos" : r.rsi < 35 ? "neg" : ""}">${fmt(r.rsi)}</td>
      <td>${sigBadges(r)}</td>
      <td><span class="dot ${r.above_ma50 ? "y" : "n"}"></span></td>
      <td><span class="dot ${r.above_ma200 ? "y" : "n"}"></span></td>
    </tr>`).join("");
  $("resultBody").querySelectorAll("tr").forEach(tr => tr.onclick = () => openResearch(tr.dataset.t));
}

/* ── 主題池掃描(背景 job)── */
async function runScreenJob() {
  const btn = $("btnRunScreen"); btn.disabled = true;
  $("jobStatus").textContent = `⏳ ${screenKind} · ${screenScope} 跑批中(yfinance 抓池,分鐘級)…`;
  try {
    const { id } = await api("/api/jobs", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "screen", kind: screenKind, scope: screenScope }) });
    const job = await pollJob(id);
    renderScreenResult(job.result);
    $("jobStatus").textContent = "✅ 完成 " + new Date().toLocaleTimeString();
  } catch (e) { $("jobStatus").textContent = "❌ " + e.message; }
  btn.disabled = false;
}
async function pollJob(id) {
  for (;;) {
    await new Promise(r => setTimeout(r, 2500));
    const j = await api("/api/jobs/" + id);
    if (j.status === "done") return j;
    if (j.status === "error") throw new Error(j.error);
  }
}
function renderScreenResult(res) {
  const rows = res.rows || [];
  $("screenResultPanel").classList.remove("hidden");
  $("screenResultTitle").textContent = `🛰️ ${res.title}(${rows.length} 檔,點代號開調研)`;
  if (!rows.length) { $("screenResultTable").innerHTML = "<div class='muted'>沒有結果</div>"; return; }
  const keys = Object.keys(rows[0]).filter(k => typeof rows[0][k] !== "object" || rows[0][k] === null).slice(0, 12);
  $("screenResultTable").innerHTML = `<table><thead><tr>${keys.map(k => `<th>${k}</th>`).join("")}</tr></thead>
    <tbody>${rows.slice(0, 60).map(r => `<tr data-t="${r.ticker || ""}">${keys.map(k => {
      let v = r[k];
      if (typeof v === "number") v = Math.abs(v) > 1e6 ? fmtB(v) : (Math.round(v * 100) / 100);
      if (typeof v === "boolean") v = v ? "✓" : "";
      return `<td class="${k === "ticker" ? "tk" : ""}">${v ?? "—"}</td>`;
    }).join("")}</tr>`).join("")}</tbody></table>`;
  $("screenResultTable").querySelectorAll("tr[data-t]").forEach(tr =>
    tr.onclick = () => tr.dataset.t && openResearch(tr.dataset.t));
}

/* ── 調研 overlay ── */
let currentTicker = null;
const charts = {};
function echart(id) {
  const el = $(id);
  if (!window.echarts) return null;
  if (!charts[id]) charts[id] = echarts.init(el, null, { renderer: "canvas" });
  return charts[id];
}
const GRID_STYLE = { axisLine: { lineStyle: { color: "#2c3e50" } }, axisLabel: { color: "#7d93a3" },
                     splitLine: { lineStyle: { color: "#223041" } } };

async function openResearch(t) {
  currentTicker = t;
  $("research").classList.remove("hidden");
  $("rsTitle").textContent = t;
  const r = ROWS[t];
  $("rsBadges").innerHTML = r ? sigBadges(r) + ` <span class="chip">close ${fmt(r.close, 2)}</span>
    <span class="chip">距高 ${fmt(r.dist_52w_high_pct)}%</span><span class="chip">RSI ${fmt(r.rsi)}</span>` : "";
  $("rsSuspect").classList.add("hidden");
  switchTab("tech");
  loadTech(t);                       // 離線,秒回
  loadResearch(t);                   // 線上,慢 — 各 tab 自己掛 loading
  loadLocal(t);
}
function switchTab(name) {
  document.querySelectorAll("#rsTabs .tab").forEach(b => b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".tabpane").forEach(p => p.classList.toggle("active", p.id === "tab-" + name));
  setTimeout(() => Object.values(charts).forEach(c => c && c.resize()), 50);
}

async function loadTech(t) {
  try {
    const d = await api(`/api/ticker/${t}/chart?bars=260`);
    const c = echart("chartMain"); if (!c) return;
    const kdata = d.dates.map((_, i) => [d.open[i], d.close[i], d.low[i], d.high[i]]);
    const volColor = d.dates.map((_, i) => (d.close[i] >= d.open[i] ? "#ef5350" : "#26a69a"));
    c.setOption({
      backgroundColor: "transparent",
      tooltip: { trigger: "axis", axisPointer: { type: "cross" }, backgroundColor: "#1c2832",
                 borderColor: "#2c3e50", textStyle: { color: "#d7e3ea" } },
      legend: { data: ["MA5", "MA20", "MA60", "MA200"], textStyle: { color: "#7d93a3" }, top: 0 },
      axisPointer: { link: [{ xAxisIndex: "all" }] },
      grid: [{ left: 60, right: 20, top: 28, height: "55%" },
             { left: 60, right: 20, top: "66%", height: "12%" },
             { left: 60, right: 20, top: "82%", height: "12%" }],
      xAxis: [0, 1, 2].map(i => ({ type: "category", data: d.dates, gridIndex: i, ...GRID_STYLE,
                                   axisLabel: { color: "#7d93a3", show: i === 2 } })),
      yAxis: [{ scale: true, gridIndex: 0, ...GRID_STYLE },
              { gridIndex: 1, ...GRID_STYLE, axisLabel: { show: false }, splitLine: { show: false } },
              { gridIndex: 2, min: 0, max: 100, ...GRID_STYLE }],
      dataZoom: [{ type: "inside", xAxisIndex: [0, 1, 2], start: 40, end: 100 },
                 { type: "slider", xAxisIndex: [0, 1, 2], bottom: 0, height: 16 }],
      series: [
        { name: t, type: "candlestick", data: kdata,
          itemStyle: { color: "#ef5350", color0: "#26a69a", borderColor: "#ef5350", borderColor0: "#26a69a" } },
        ...["ma5", "ma20", "ma60", "ma200"].map((k, i) => ({
          name: "MA" + k.slice(2), type: "line", data: d[k], showSymbol: false,
          lineStyle: { width: 1.2, color: ["#ffd54f", "#00d4ff", "#ab47bc", "#90a4ae"][i] } })),
        { name: "Vol", type: "bar", xAxisIndex: 1, yAxisIndex: 1, data: d.volume,
          itemStyle: { color: (p) => volColor[p.dataIndex] } },
        { name: "RSI", type: "line", xAxisIndex: 2, yAxisIndex: 2, data: d.rsi, showSymbol: false,
          lineStyle: { color: "#4dd0e1" },
          markLine: { silent: true, symbol: "none", label: { show: false },
                      data: [{ yAxis: 30 }, { yAxis: 70 }],
                      lineStyle: { color: "#44535f", type: "dashed" } } },
      ],
    }, true);
  } catch (e) { toast("K 線載入失敗:" + e.message); }
}

async function loadResearch(t) {
  $("fundCards").innerHTML = $("cashCards").innerHTML = $("chipCards").innerHTML =
    "<div class='muted'>⏳ yfinance 調研中…</div>";
  let d;
  try { d = await api(`/api/ticker/${t}/research`); }
  catch (e) { $("fundCards").innerHTML = "❌ " + e.message; return; }
  if (t !== currentTicker) return;

  // 數據可疑警示(EUR/ADR 換算汙染 lint)
  const sus = d.derived_fields_suspect_reasons || [];
  $("rsSuspect").classList.toggle("hidden", !sus.length);
  if (sus.length) $("rsSuspect").textContent = "⚠️ 衍生估值欄位疑似損毀(EUR/ADR 換算 bug):" + sus.join(" · ") + " — 估值比率僅供參考";

  // 基本面 cards + 營收圖
  const f = d.fundamentals || {};
  const card = (k, v, small) => `<div class="card"><div class="k">${k}</div><div class="v ${small ? "small" : ""}">${v}</div></div>`;
  $("fundCards").innerHTML =
    card("名稱", (d.name || t) + (d.source === "lake-snapshot" ? " (湖快照)" : ""), 1) +
    card("市值", f.market_cap_billion ? f.market_cap_billion + "B" : "—") +
    card("Trailing P/E", fmt(f.trailing_pe)) + card("Forward P/E", fmt(f.forward_pe)) +
    card("P/B" + (sus.some(s => s.includes("priceToBook")) ? " ⚠️" : ""), fmt(f.price_to_book)) +
    card("EV/EBITDA", fmt(f.ev_to_ebitda)) +
    card("毛利率", fmt(f.profit_margin_pct) + "%") + card("營益率", fmt(f.operating_margin_pct) + "%") +
    card("ROE", fmt(f.return_on_equity_pct) + "%") +
    card("營收YoY", fmt(f.revenue_growth_yoy_pct) + "%") + card("EPS YoY", fmt(f.earnings_growth_yoy_pct) + "%") +
    card("分析師目標", fmt(f.analyst_target_mean, 2) + (d.price ? ` (現 ${fmt(d.price, 2)})` : ""), 1) +
    card("評級", f.recommendation || "—", 1) + card("財報日", d.earnings_date || "—", 1) +
    (d.moat ? card("護城河", `${d.moat.moat} · ${d.moat.moat_type}`, 1) : "");
  drawPeriodBars("chartRevenue", "年度 營收 vs 淨利", d.income.annual, [["revenue", "營收"], ["net_income", "淨利"]]);
  drawPeriodBars("chartRevenueQ", "季度 營收(近 8 季)", d.income.quarterly, [["revenue", "營收"], ["gross_profit", "毛利"]]);

  // 現金流
  const cfA = d.cashflow.annual;
  const years = Object.keys(cfA.operating || {});
  const lastY = years[0];
  $("cashCards").innerHTML =
    card("最新年度 OCF", fmtB((cfA.operating || {})[lastY])) +
    card("最新年度 FCF", fmtB((cfA.free_cash_flow || {})[lastY])) +
    card("Capex", fmtB((cfA.capex || {})[lastY])) +
    card("投資現金流", fmtB((cfA.investing || {})[lastY])) +
    card("融資現金流", fmtB((cfA.financing || {})[lastY]));
  drawPeriodBars("chartCashflow", "現金流分布(年度)", cfA,
    [["operating", "營運"], ["investing", "投資"], ["financing", "融資"], ["free_cash_flow", "FCF"]]);
  drawPeriodBars("chartFcf", "季度 OCF / FCF", d.cashflow.quarterly,
    [["operating", "營運"], ["free_cash_flow", "FCF"]]);

  // 資金面
  const cp = d.chip_flow || {};
  $("chipCards").innerHTML =
    card("機構持股", fmt(cp.heldPercentInstitutions_pct) + "%") +
    card("內部人持股", fmt(cp.heldPercentInsiders_pct) + "%") +
    card("空單 % float" + (sus.some(s => s.includes("floatShares")) ? " ⚠️" : ""), fmt(cp.shortPercentOfFloat_pct) + "%") +
    card("Short Ratio(回補天數)", fmt(cp.shortRatio)) +
    card("流通股(百萬)", fmt(cp.floatShares_millions, 0)) +
    card("負債/權益", fmt(f.debt_to_equity)) + card("流動比", fmt(f.current_ratio)) +
    card("自由現金流", f.free_cashflow_billion ? f.free_cashflow_billion + "B" : "—") +
    card("總負債", f.total_debt_billion ? f.total_debt_billion + "B" : "—");
  $("chipNotes").textContent = `來源:${d.source} · 抓取 ${d.fetched_at}(快取 15 分)· 機構/空單為 yfinance 月頻快照,非即時盤口`;
}

function drawPeriodBars(elId, title, seriesMap, keys) {
  const c = echart(elId); if (!c) return;
  const periods = [...new Set(keys.flatMap(([k]) => Object.keys(seriesMap[k] || {})))].sort();
  if (!periods.length) { c.clear(); c.setOption({ title: { text: title + "(無資料)", textStyle: { color: "#7d93a3", fontSize: 13 } } }); return; }
  c.setOption({
    backgroundColor: "transparent",
    title: { text: title, textStyle: { color: "#4dd0e1", fontSize: 13 } },
    tooltip: { trigger: "axis", backgroundColor: "#1c2832", borderColor: "#2c3e50",
               textStyle: { color: "#d7e3ea" }, valueFormatter: fmtB },
    legend: { textStyle: { color: "#7d93a3" }, top: 0, right: 0 },
    grid: { left: 70, right: 20, top: 34, bottom: 24 },
    xAxis: { type: "category", data: periods, ...GRID_STYLE },
    yAxis: { type: "value", ...GRID_STYLE, axisLabel: { color: "#7d93a3", formatter: (v) => fmtB(v) } },
    series: keys.map(([k, name], i) => ({
      name, type: "bar", data: periods.map(p => (seriesMap[k] || {})[p] ?? null),
      itemStyle: { color: ["#00d4ff", "#ef5350", "#ffd54f", "#26a69a"][i % 4] },
    })),
  }, true);
}

async function loadLocal(t) {
  try {
    const d = await api(`/api/ticker/${t}/local`);
    const r = d.scan_row || {};
    const card = (k, v) => `<div class="card"><div class="k">${k}</div><div class="v small">${v}</div></div>`;
    $("localCards").innerHTML =
      card("掃描 as_of", d.as_of || "—") +
      card("訊號", sigBadges(r)) +
      card("量縮", r.vol_contract ? "✓" : "—") + card("RSI背離", r.rsi_divergence ? "✓" : "—") +
      card("rally streak(最近)", d.rally_history.length ? d.rally_history[d.rally_history.length - 1].streak : "無紀錄");
    const c = echart("chartStreak");
    if (c && d.rally_history.length) {
      c.setOption({
        backgroundColor: "transparent",
        title: { text: "rally-state streak / composite 軌跡", textStyle: { color: "#4dd0e1", fontSize: 13 } },
        tooltip: { trigger: "axis", backgroundColor: "#1c2832", textStyle: { color: "#d7e3ea" } },
        legend: { textStyle: { color: "#7d93a3" }, top: 0, right: 0 },
        grid: { left: 50, right: 50, top: 34, bottom: 24 },
        xAxis: { type: "category", data: d.rally_history.map(h => h.date), ...GRID_STYLE },
        yAxis: [{ type: "value", name: "streak", ...GRID_STYLE },
                { type: "value", name: "composite", ...GRID_STYLE, splitLine: { show: false } }],
        series: [
          { name: "streak", type: "bar", data: d.rally_history.map(h => h.streak), itemStyle: { color: "#ef5350" } },
          { name: "composite", type: "line", yAxisIndex: 1, data: d.rally_history.map(h => h.composite),
            lineStyle: { color: "#00d4ff" } },
        ],
      }, true);
    } else if (c) { c.clear(); }
    $("localRaw").textContent = JSON.stringify({ scan_row: d.scan_row, rally_history: d.rally_history }, null, 2);
  } catch (e) { $("localRaw").textContent = "❌ " + e.message; }
}

/* ── 持股健檢 ── */
const ACTION_CLS = { "清倉": "h-sell", "換股": "h-swap", "減碼": "h-trim",
                     "待驗證": "h-tbd", "續抱⚠": "h-warn", "續抱": "h-hold" };

function renderHealth(d) {
  $("healthMeta").textContent = `scan as_of ${d.as_of_scan || "—"} · audit ${d.audit_file_basis || "—"}`;
  const card = (k, v) => `<div class="card"><div class="k">${k}</div><div class="v">${v}</div></div>`;
  $("healthCards").innerHTML =
    card("可見部位", "$" + (d.total_visible_usd || 0).toLocaleString()) +
    card("槓桿占比", fmt(d.leveraged_pct) + "%") +
    Object.entries(d.action_counts || {}).map(([a, n]) =>
      `<div class="card"><div class="k">${a}</div><div class="v ${ACTION_CLS[a] || ""}">${n}</div></div>`).join("");
  $("healthTable").innerHTML = `<table><thead><tr>
      <th>動作</th><th>帳本</th><th>代號</th><th>名稱</th><th>市值</th><th>%</th><th>audit</th><th>FOM</th>
      <th>距52w高</th><th>RSI</th><th>理由</th><th>換股候選(點開調研)</th>
    </tr></thead><tbody>` + d.rows.map(r => {
      const s = r.day_signals || {};
      return `<tr>
        <td><span class="hbadge ${ACTION_CLS[r.action] || ""}">${r.action}</span></td>
        <td class="muted">${r.book || "—"}</td>
        <td class="tk" data-open="${r.ticker}">${r.ticker}</td>
        <td>${(r.name || "").slice(0, 26)}${r.leveraged_of ? ` <span class="sig j">2x</span>` : ""}</td>
        <td>$${(r.mkt_val || 0).toLocaleString()}</td><td>${fmt(r.pct)}</td>
        <td>${r.audit_verdict || "—"}</td><td>${fmt(r.fom)}</td>
        <td>${s.dist_52w_high_pct !== undefined && s.dist_52w_high_pct !== null ? fmt(s.dist_52w_high_pct) + "%" : "—"}</td>
        <td>${fmt(s.rsi)}</td>
        <td class="h-reasons">${(r.reasons || []).map(x => `· ${x}`).join("<br>")}</td>
        <td>${(r.swaps || []).map(sw =>
          `<span class="fchip swapchip" data-open="${sw.ticker}" title="${sw.why || ""}${sw.dist_52w_high_pct != null ? " · 距高 " + sw.dist_52w_high_pct + "%" : ""}">${sw.ticker}</span>`).join(" ") || "—"}</td>
      </tr>`;
    }).join("") + "</tbody></table>";
  $("healthTable").querySelectorAll("[data-open]").forEach(el =>
    el.onclick = (e) => { e.stopPropagation(); openResearch(el.dataset.open); });
}

/* ── topbar 行為 ── */
function bindUI() {
  $("btnCloseResearch").onclick = () => $("research").classList.add("hidden");
  $("research").onclick = (e) => { if (e.target === $("research")) $("research").classList.add("hidden"); };
  document.querySelectorAll("#rsTabs .tab").forEach(b => b.onclick = () => switchTab(b.dataset.tab));
  $("btnRunScreen").onclick = runScreenJob;
  $("btnRescan").onclick = () => loadScan(true).catch(e => toast("❌ " + e.message));
  $("btnLakeRefresh").onclick = async () => {
    const btn = $("btnLakeRefresh"); btn.disabled = true;
    toast("🌊 刷新湖(573 檔 ~20s)+ 重掃中…", 20000);
    try {
      const { id } = await api("/api/jobs", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "lake_refresh" }) });
      const j = await pollJob(id);
      await loadScan(false);
      toast(`✅ 湖已刷新 ${j.result.refreshed} 檔(失敗 ${j.result.n_errors})· as_of ${j.result.as_of}` +
            (j.result.intraday ? " · ⚠️ 盤中 partial bar" : ""));
    } catch (e) { toast("❌ " + e.message, 6000); }
    btn.disabled = false;
  };
  $("btnTickerRefresh").onclick = async () => {
    if (!currentTicker) return;
    const btn = $("btnTickerRefresh"); btn.disabled = true;
    toast(`🔄 ${currentTicker} 刷新中…`);
    try {
      const r = await api(`/api/ticker/${currentTicker}/refresh`, { method: "POST" });
      if (r.row) ROWS[currentTicker] = r.row;
      renderTable(); loadTech(currentTicker); loadResearch(currentTicker); loadLocal(currentTicker);
      toast("✅ 已刷新" + (r.intraday ? "(盤中 partial bar)" : ""));
    } catch (e) { toast("❌ " + e.message); }
    btn.disabled = false;
  };
  $("tickerJump").addEventListener("change", () => {
    const t = $("tickerJump").value.trim().toUpperCase();
    if (t) { openResearch(t); $("tickerJump").value = ""; }
  });
  let healthBook = "all";
  const loadHealth = async () => {
    $("healthTable").innerHTML = "<div class='muted'>⏳ 健檢中…</div>";
    try { renderHealth(await api("/api/holdings/health?book=" + healthBook)); }
    catch (e) { $("healthTable").innerHTML = "❌ " + e.message; }
  };
  $("btnHealth").onclick = () => { $("healthOverlay").classList.remove("hidden"); loadHealth(); };
  $("bookChips").querySelectorAll(".fchip").forEach(ch => ch.onclick = () => {
    healthBook = ch.dataset.book;
    $("bookChips").querySelectorAll(".fchip").forEach(c => c.classList.toggle("on", c === ch));
    loadHealth();
  });
  $("btnCloseHealth").onclick = () => $("healthOverlay").classList.add("hidden");
  $("healthOverlay").onclick = (e) => { if (e.target === $("healthOverlay")) $("healthOverlay").classList.add("hidden"); };
  $("btnReco").onclick = async () => {
    $("recoOverlay").classList.remove("hidden");
    const md = await api("/api/reco");
    if (window.marked && !window._noMarked) {
      $("recoBody").innerHTML = marked.parse(md, { gfm: true, breaks: true });
    } else {
      $("recoBody").innerHTML = `<pre class="raw">${md.replace(/</g, "&lt;")}</pre>`;
    }
  };
  $("btnCloseReco").onclick = () => $("recoOverlay").classList.add("hidden");
  $("recoOverlay").onclick = (e) => { if (e.target === $("recoOverlay")) $("recoOverlay").classList.add("hidden"); };
  $("btnClearFilters").onclick = () => {
    F.signals = {}; F.sectors = new Set();
    Object.assign(F, { rsi: [0, 100], dh: [-80, 0], dl: [0, 300] });
    syncSliders(); syncSignalChips(); renderSectorChips(); renderBreadth(); renderTable();
  };
  // 滑桿(min/max 互相鉗制)
  const wire = (minId, maxId, key) => {
    const upd = () => {
      let lo = +$(minId).value, hi = +$(maxId).value;
      if (lo > hi) [lo, hi] = [hi, lo];
      F[key] = [lo, hi]; updateSliderLabels(); renderTable();
    };
    $(minId).oninput = upd; $(maxId).oninput = upd;
  };
  wire("rsiMin", "rsiMax", "rsi"); wire("dhMin", "dhMax", "dh"); wire("dlMin", "dlMax", "dl");
  updateSliderLabels();
  window.addEventListener("resize", () => Object.values(charts).forEach(c => c && c.resize()));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { $("research").classList.add("hidden"); $("recoOverlay").classList.add("hidden"); }
  });
}

init();
