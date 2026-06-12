"""供應鏈 ABM 情境模擬器 — World Model 的最小可行 agent-based 模型(規則式).

把 regime/world_monitor 的感測結果(GPRC_TWN 1985+ 分位數)接上一個極簡
供應鏈代理模型:依先驗抽樣世界情境(NONE / TS_HIGH / TS_BLOCKADE /
TARIFF_NEW)→ 對受影響地區的供應商施加產出衝擊 + 逐月回復動態 →
Monte Carlo 聚合成 AI-HW 供給損失分布,並映射成 deep-kill 存活率折減的
啟發式參考值(對照 wiki/06_rally_dna §6e 的 74.1% 基線)。

採用紀律(「先讓需求長到工具的尺寸」):本模組刻意 **不用 mesa** —— 純
Python + numpy 種子 RNG 已足以承載當前複雜度(單層艦隊、無代理間網絡、
無排程器)。mesa 只在模型複雜度真實成長時才引入,條件見 MESA_NOTE。

所有權重 / 機率 / 乘數皆為 **顯式先驗(guesses)**,逐一附 _doc 說明量級
依據;無任何擬合 —— 1985+ 樣本中不存在台海封鎖事件,這些先驗不可能來自
歷史頻率,只能來自量級推理。輸出必須讀成「情境壓力測試」,不是預測。

PIT:輸出帶 as_of(GPRC_TWN 分位數所屬的 GPR 月度 vintage)+ generated_at
(由呼叫端注入,run_simulation 本身不讀時鐘 → 同 seed 全純)。缺最新
world-monitor 輸出時優雅降級(degraded=true、退 base 先驗帶,不發明值)。

llm_involvement: none(規則式引擎,無模型參與)。
recommend-only:輸出是篩選 / 壓測參考,非倉位指令;本系統永不下單。

CLI:
    python -m sharks.regime.abm_supply_chain [--paths N] [--months M] [--seed S] [--dry-run]
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

import numpy as np

EXPOSURE_CONFIG = Path("config/world_exposure.json")

REGIONS = ("Taiwan", "US", "Korea", "Japan", "China", "SEA")

# config/world_exposure.json taiwan_chain.weight 的編寫時錨點(2026-06-12 = 0.9)。
# build_default_fleet 以(實際 weight / 本錨點)縮放台灣占比 → config 重校時艦隊自動跟動。
_TAIWAN_CHAIN_ANCHOR_WEIGHT = 0.9

FLEET_COMPOSITION = {
    "_doc": (
        "AI-HW 供應鏈艦隊的地區產能占比(顯式先驗,非擬合)。依據:"
        "config/world_exposure.json taiwan_chain weight 0.9 為全 repo 最高曝險群"
        "(20/37 檔)→ 台灣是 AI-HW 製造重心,占比 0.55(量級錨點=台積電先進製程"
        "代工市占約九成,但艦隊含記憶體/設備/光通訊故下修);US 0.15(設備"
        "AMAT/LRCX/KLAC + 先進封裝);Korea 0.12(HBM/記憶體);Japan 0.08(材料/設備);"
        "China 0.06(成熟製程/組裝);SEA 0.04(封測)。總和=1;"
        "每月與 world_exposure.json 對帳時一併覆核。"
    ),
    "Taiwan": 0.55, "US": 0.15, "Korea": 0.12, "Japan": 0.08, "China": 0.06, "SEA": 0.04,
}

# 艦隊顆粒度錨點 = world_exposure taiwan_chain 名單長度(20 檔)— 方便對帳的顯式先驗,
# 不是統計量;agent 數只影響異質性顆粒度,不影響期望值。
N_FLEET_AGENTS = 20

TOTAL_CAPACITY = 100.0   # 產能指數化(全艦隊總和=100 → 損失直接讀成 %)

# 衝擊烈度的代理間異質性 σ=8%(顯式猜測:同一事件下各供應商受創差異 —
# 廠址/庫存水位/客戶結構),截斷於 [0.7, 1.3] 防生成負產出或反向受益。
SHOCK_NOISE_SD = 0.08
SHOCK_NOISE_CLIP = (0.7, 1.3)

# 月度營運噪聲 σ=1%(顯式猜測,量級=正常出貨季節波動的月度化),截斷 [0.9, 1.1]。
OPER_NOISE_SD = 0.01
OPER_NOISE_CLIP = (0.9, 1.1)

# 月總出貨 < 基線 95% 視為「中斷月」— 5% 缺口約當一線 hyperscaler 單季建置
# 延宕的量級(顯式猜測)。
DISRUPTION_THRESHOLD = 0.95

SCENARIOS: dict[str, dict] = {
    "NONE": {
        "_doc": (
            "基線:無新衝擊,僅月度營運噪聲(OPER_NOISE_SD)。因噪聲在產能上限被"
            "截斷,中位損失約 0.3-0.5%(摩擦項)— 作為其他情境的對照地板。"
        ),
        "regions": (), "output_mult": 1.0, "recovery_rate": 0.0, "recovery_target": 1.0,
    },
    "TS_HIGH": {
        "_doc": (
            "台海高張力(非封鎖):大規模演習/實質禁運/航運保費飆升 → 台灣供應商"
            "出貨 ×0.65;每月 12% 速率朝 0.92×產能部分回復(分流+庫存緩衝,數月"
            "尺度,horizon 內不完全復原)。0.65/0.92/0.12 皆顯式猜測 — 量級錨點="
            "疫情期 GSCPI 尖峰時半導體交期約 2 倍化的營收衝擊粗推,無擬合。"
        ),
        "regions": ("Taiwan",), "output_mult": 0.65,
        "recovery_rate": 0.12, "recovery_target": 0.92,
    },
    "TS_BLOCKADE": {
        "_doc": (
            "尾部情境:全面封鎖 → 台灣出貨 ×0.25,每月僅 5% 朝 0.75×產能回復"
            "(結構性損害,horizon 內遠不復原)。顯式猜測 — 1985+ 零歷史樣本可"
            "擬合;0.25 殘餘=非台灣產能間接出貨+在途/庫存去化。"
        ),
        "regions": ("Taiwan",), "output_mult": 0.25,
        "recovery_rate": 0.05, "recovery_target": 0.75,
    },
    "TARIFF_NEW": {
        "_doc": (
            "中美新一輪關稅:成本驅動(非物理中斷)→ China+SEA 出貨 ×0.85,"
            "每月 15% 朝 0.95×產能回復(轉單/成本轉嫁較快)。對應 "
            "config/world_events.json TARIFF_NEW 手動旗的情境化;乘數為顯式猜測。"
        ),
        "regions": ("China", "SEA"), "output_mult": 0.85,
        "recovery_rate": 0.15, "recovery_target": 0.95,
    },
}
SCENARIO_IDS = tuple(SCENARIOS)

SCENARIO_PRIOR_BANDS = {
    "_doc": (
        "24 個月視野的情境先驗,依 GPRC_TWN 1985+ 分位數(config/world_events.json "
        "calibration:p90/p95/p99 = 0.17/0.25/0.37)分帶。全部是顯式猜測:1985+ 樣本"
        "中零台海封鎖事件,無歷史頻率可擬合,只能做量級推理 — base 帶 TS_HIGH 5% ≈ "
        "平靜期的低個位數升級先驗;extreme 帶(≥p99,即 world_monitor TS_HIGH 旗標"
        "已觸發的現狀)放大約 4 倍;TS_BLOCKADE 全帶維持個位數百分比以下(尾部,"
        "非基線預測)。pctile 缺席(world-monitor 降級)→ 退 base 帶:缺數據不假設"
        "升級,由 degraded 旗標提醒讀者。每月與 world_events.json 閾值重校同步覆核。"
    ),
    "bands": [
        {"max_pctile": 90.0, "label": "base(<p90)",
         "priors": {"NONE": 0.92, "TS_HIGH": 0.05, "TS_BLOCKADE": 0.005, "TARIFF_NEW": 0.025}},
        {"max_pctile": 95.0, "label": "elevated(p90-p95)",
         "priors": {"NONE": 0.85, "TS_HIGH": 0.10, "TS_BLOCKADE": 0.01, "TARIFF_NEW": 0.04}},
        {"max_pctile": 99.0, "label": "high(p95-p99)",
         "priors": {"NONE": 0.78, "TS_HIGH": 0.15, "TS_BLOCKADE": 0.02, "TARIFF_NEW": 0.05}},
        {"max_pctile": float("inf"), "label": "extreme(>=p99)",
         "priors": {"NONE": 0.68, "TS_HIGH": 0.22, "TS_BLOCKADE": 0.04, "TARIFF_NEW": 0.06}},
    ],
}

DEEPKILL_HAIRCUT = {
    "_doc": (
        "中位 AI-HW 供給損失(%)→ deep-kill 存活率折減(百分點)的啟發式映射。"
        "基線存活率 74.1% = wiki/06_rally_dna §6e failed-analogs 子庫(664 件 deep-kill "
        "觸發,湖內倖存者宇宙=上界)。sensitivity 0.5pp/1%:顯式猜測 — deep-kill 候選"
        "宇宙與 taiwan_chain 高度重疊(艦隊構成同源),假設中位供給損失的一半量級轉化"
        "為 disaster 機率增量;無資料可擬合。cap 10pp:dotcom 最差 5 年期存活 67% vs "
        "基線 74.1% ≈ 7pp 差距,放寬至 10pp 容忍倖存者偏差上界 — 超過此級別的情境應由 "
        "markov crisis 閘直接停開 deep-kill 倉(wiki/06 §6e),不是靠折減。本指標為 "
        "world_monitor deepkill_cap_multiplier(乘數路徑)的補充參考,兩者不疊乘。"
        "採全路徑中位數(穩健、不被尾部拉走)→ 折減≈0 代表『基準情境下不額外折減』;"
        "條件式折減看 per_scenario_loss 表內的 survival_delta_pct_conditional。"
    ),
    "baseline_survival_pct": 74.1,
    "sensitivity_pp_per_pct": 0.5,
    "max_haircut_pp": 10.0,
}

MESA_NOTE = (
    "依採用紀律「先讓需求長到工具的尺寸」:本模組為純 Python+numpy 最小可行 ABM。"
    "mesa 僅在模型複雜度成長時引入 — 代理間替代/轉單網絡、多層 BOM、事件排程器"
    "等需求出現,且 wiki/23_world_model §6 入庫條件(world 事件與個股報酬前瞻"
    "相關性累積 >= 6 個月)成立。"
)


@dataclass
class SupplierAgent:
    """供應商代理:地區 + 產能 + 當前產出(指數單位,全艦隊總和=100)。"""
    region: str
    capacity: float
    current_output: float


# ── 艦隊建構(config 驅動,缺檔退常數先驗)──

def _load_exposure_config() -> dict:
    return json.loads(EXPOSURE_CONFIG.read_text(encoding="utf-8"))


def build_default_fleet(loader: Optional[Callable[[], dict]] = None) -> list[SupplierAgent]:
    """由 config/world_exposure.json 群權重建預設艦隊(AI_HW、台灣為重)。

    台灣占比 = FLEET_COMPOSITION['Taiwan'] ×(taiwan_chain.weight / 0.9 錨點)後
    全體再歸一 → config 重校時艦隊自動跟動。config 缺席/壞 → 用常數先驗,
    優雅降級不發明值。
    """
    shares = {k: float(v) for k, v in FLEET_COMPOSITION.items() if not k.startswith("_")}
    try:
        cfg = (loader or _load_exposure_config)()
        tw_w = float(cfg["groups"]["taiwan_chain"]["weight"])
        shares["Taiwan"] = shares["Taiwan"] * (tw_w / _TAIWAN_CHAIN_ANCHOR_WEIGHT)
    except Exception:
        pass
    total = sum(shares.values())
    shares = {k: v / total for k, v in shares.items()}
    fleet: list[SupplierAgent] = []
    for region, share in shares.items():
        n = max(1, round(share * N_FLEET_AGENTS))
        cap = share * TOTAL_CAPACITY / n
        for _ in range(n):
            fleet.append(SupplierAgent(region=region, capacity=cap, current_output=cap))
    return fleet


# ── 先驗(純函式)──

def _select_band(gprc_twn_pctile: Optional[float]) -> dict:
    bands = SCENARIO_PRIOR_BANDS["bands"]
    if gprc_twn_pctile is None:
        return bands[0]            # 缺數據不假設升級(見 SCENARIO_PRIOR_BANDS._doc)
    for b in bands:
        if gprc_twn_pctile < b["max_pctile"]:
            return b
    return bands[-1]


def scenario_priors(gprc_twn_pctile: Optional[float] = None) -> dict[str, float]:
    """GPRC_TWN 分位數 → 情境先驗 dict(回傳複本,呼叫端可改不汙染常數)。"""
    return dict(_select_band(gprc_twn_pctile)["priors"])


# ── 單路徑動力學(純函式給 rng)──

def simulate_scenario_path(scenario: dict, caps: np.ndarray, regions: np.ndarray,
                           months: int, rng: np.random.Generator, *,
                           shock_noise_sd: float = SHOCK_NOISE_SD,
                           oper_noise_sd: float = OPER_NOISE_SD) -> np.ndarray:
    """一條月度路徑:潛在水位(latent level)決定論演化 — t=0 衝擊
    (× output_mult × 異質噪聲)→ 之後逐月朝 recovery_target×產能 以
    recovery_rate 指數回復;每月觀測出貨 = 水位 × 營運噪聲(觀測噪聲
    不累積,避免人工下漂),截斷於 [0, 產能](無瞬時超產=保守;
    無跨地區替代=保守簡化,先進製程短期無替代來源 — 見
    wiki/23_world_model §6 曝險地圖)。
    回傳 shape=(months,) 的「總出貨/基線」相對值。
    """
    caps = caps.astype(float)
    baseline = caps.sum()
    level = caps.copy()
    mask = np.isin(regions, list(scenario["regions"]))
    n_hit = int(mask.sum())
    rel = np.empty(months, dtype=float)
    for t in range(months):
        if n_hit:
            if t == 0:
                if shock_noise_sd > 0:
                    noise = np.clip(rng.normal(1.0, shock_noise_sd, n_hit),
                                    *SHOCK_NOISE_CLIP)
                else:
                    noise = np.ones(n_hit)
                level[mask] = caps[mask] * scenario["output_mult"] * noise
            else:
                level[mask] += scenario["recovery_rate"] * (
                    scenario["recovery_target"] * caps[mask] - level[mask])
        observed = level
        if oper_noise_sd > 0:
            observed = level * np.clip(rng.normal(1.0, oper_noise_sd, level.size),
                                       *OPER_NOISE_CLIP)
        observed = np.clip(observed, 0.0, caps)
        rel[t] = observed.sum() / baseline
    return rel


# ── deep-kill 啟發式映射 ──

def deepkill_survival_delta_pct(median_loss_pct: Optional[float]) -> Optional[float]:
    """中位 AI-HW 供給損失(%)→ 存活率折減(百分點,<=0)。依據見 DEEPKILL_HAIRCUT。"""
    if median_loss_pct is None:
        return None
    haircut = round(min(max(float(median_loss_pct), 0.0)
                        * DEEPKILL_HAIRCUT["sensitivity_pp_per_pct"],
                        DEEPKILL_HAIRCUT["max_haircut_pp"]), 2)
    return -haircut if haircut > 0 else 0.0


# ── Monte Carlo(同 seed 全純:不讀時鐘、不碰磁碟)──

def run_simulation(n_paths: int = 2000, months: int = 24, seed: int = 42,
                   metrics: Optional[dict] = None,
                   fleet: Optional[list[SupplierAgent]] = None,
                   generated_at: Optional[str] = None) -> dict:
    """情境 Monte Carlo:先驗抽情境 → 逐月衝擊+回復 → 聚合損失分布。

    metrics = world-monitor 的 metrics dict(取 gprc_twn_pctile 選先驗帶、
    gpr_date 當 as_of);None → degraded、退 base 帶。fleet=None → 由
    config/world_exposure.json 建預設艦隊。generated_at 由呼叫端注入
    (本函式不讀時鐘 → 同 seed 輸出完全可重現)。
    """
    rng = np.random.default_rng(seed)
    fleet = build_default_fleet() if fleet is None else fleet
    caps = np.array([a.capacity for a in fleet], dtype=float)
    regions = np.array([a.region for a in fleet])

    m = metrics or {}
    pctile = m.get("gprc_twn_pctile")
    band = _select_band(pctile)
    priors = dict(band["priors"])
    probs = np.array([priors[s] for s in SCENARIO_IDS], dtype=float)
    probs = probs / probs.sum()
    draws = rng.choice(len(SCENARIO_IDS), size=n_paths, p=probs)

    losses = np.empty(n_paths, dtype=float)
    disrupted_q = np.empty(n_paths, dtype=float)
    by_loss: dict[str, list[float]] = {s: [] for s in SCENARIO_IDS}
    by_disr: dict[str, list[float]] = {s: [] for s in SCENARIO_IDS}
    for i in range(n_paths):
        sid = SCENARIO_IDS[int(draws[i])]
        rel = simulate_scenario_path(SCENARIOS[sid], caps, regions, months, rng)
        loss_pct = float((1.0 - rel.mean()) * 100.0)
        dq = float((rel < DISRUPTION_THRESHOLD).sum()) / 3.0
        losses[i] = loss_pct
        disrupted_q[i] = dq
        by_loss[sid].append(loss_pct)
        by_disr[sid].append(dq)

    per_scenario: dict[str, Optional[dict]] = {}
    for sid in SCENARIO_IDS:
        vals = by_loss[sid]
        if not vals:
            per_scenario[sid] = None        # 無抽中路徑 → None,不發明
            continue
        arr = np.asarray(vals)
        med = float(np.median(arr))
        per_scenario[sid] = {
            "n_paths": len(vals),
            "loss_pct_median": round(med, 2),
            "loss_pct_p10": round(float(np.percentile(arr, 10)), 2),
            "loss_pct_p90": round(float(np.percentile(arr, 90)), 2),
            "disruption_quarters_mean": round(float(np.mean(by_disr[sid])), 2),
            "survival_delta_pct_conditional": deepkill_survival_delta_pct(med),
        }

    overall_median = float(np.median(losses))
    return {
        "as_of": m.get("gpr_date"),     # GPRC_TWN 分位數的月度 vintage 錨;缺 → None
        "generated_at": generated_at,
        "engine": "abm-supply-chain",
        "llm_involvement": "none",
        "model": "minimal-abm-v1(plain Python+numpy;mesa 採用條件見 mesa_note)",
        "params": {"n_paths": int(n_paths), "months": int(months), "seed": int(seed)},
        "inputs": {
            "gprc_twn_pctile": pctile,
            "prior_band": band["label"],
            "degraded": pctile is None,
        },
        "scenario_priors": {s: priors[s] for s in SCENARIO_IDS},
        "scenario_counts": {s: int((draws == i).sum())
                            for i, s in enumerate(SCENARIO_IDS)},
        "per_scenario_loss": per_scenario,
        "overall_loss_pct": {
            "median": round(overall_median, 2),
            "mean": round(float(losses.mean()), 2),
            "p10": round(float(np.percentile(losses, 10)), 2),
            "p90": round(float(np.percentile(losses, 90)), 2),
        },
        "expected_disruption_quarters": round(float(disrupted_q.mean()), 2),
        "deepkill_survival_baseline_pct": DEEPKILL_HAIRCUT["baseline_survival_pct"],
        "deepkill_survival_delta_pct": deepkill_survival_delta_pct(overall_median),
        "deepkill_haircut_doc": DEEPKILL_HAIRCUT["_doc"],
        "fleet_summary": _fleet_summary(fleet),
        "mesa_note": MESA_NOTE,
        "disclaimer": "recommend-only;情境模擬=壓力測試參考,非預測、非倉位指令;本系統永不下單。",
    }


def _fleet_summary(fleet: list[SupplierAgent]) -> dict:
    total = sum(a.capacity for a in fleet) or 1.0
    out: dict[str, dict] = {}
    for a in fleet:
        d = out.setdefault(a.region, {"n_agents": 0, "capacity_share": 0.0})
        d["n_agents"] += 1
        d["capacity_share"] += a.capacity
    for d in out.values():
        d["capacity_share"] = round(d["capacity_share"] / total, 4)
    return out


# ── world-monitor 讀取(優雅降級)──

def load_latest_world_metrics(out_dir: Path = Path("outputs")) -> tuple[Optional[dict], Optional[str]]:
    """最新 outputs/world-monitor-*.json 的 (metrics, 檔名);缺/壞 → (None, None)。
    依產出紀律排除含 'intraday' 與 '.bak' 結尾的檔名。"""
    try:
        files = [p for p in sorted(Path(out_dir).glob("world-monitor-*.json"))
                 if "intraday" not in p.name and not p.name.endswith(".bak")]
        if not files:
            return None, None
        data = json.loads(files[-1].read_text(encoding="utf-8"))
        metrics = data.get("metrics")
        return (metrics or None), files[-1].name
    except Exception:
        return None, None


# ── CLI ──

def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="供應鏈 ABM 情境模擬(world model,recommend-only)")
    ap.add_argument("--paths", type=int, default=2000)
    ap.add_argument("--months", type=int, default=24)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", default="outputs")
    ap.add_argument("--dry-run", action="store_true", help="印結果不落盤")
    args = ap.parse_args(argv)

    out_dir = Path(args.out_dir)
    metrics, src = load_latest_world_metrics(out_dir)
    if metrics is None:
        print("abm: world-monitor output absent -> degraded (base prior band)",
              file=sys.stderr)
    report = run_simulation(n_paths=args.paths, months=args.months, seed=args.seed,
                            metrics=metrics,
                            generated_at=datetime.now(timezone.utc).isoformat())
    report["world_monitor_source"] = src

    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")
        p = out_dir / f"abm-supply-chain-{today}.json"
        p.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                     encoding="utf-8")
        print(f"wrote {p}", file=sys.stderr)

    try:
        sys.stdout.reconfigure(encoding="utf-8")    # cp950 console 防護
    except Exception:
        pass
    o = report["overall_loss_pct"]
    print(f"abm-supply-chain:band={report['inputs']['prior_band']} "
          f"p(TS_HIGH)={report['scenario_priors']['TS_HIGH']} "
          f"loss_pct(median/p90)={o['median']}/{o['p90']} "
          f"disruption_q={report['expected_disruption_quarters']} "
          f"deepkill_delta={report['deepkill_survival_delta_pct']}pp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
