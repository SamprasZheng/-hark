"""tech/ due-diligence → FOM overlay (the `tech_dd` bridge).

Turns the qualitative, multi-horizon verdicts produced by the `tech/` layer
(`tech/scoreboard.md` + the per-trend pages, gated weekly by
`tech/_weekly-watch.md`) into a BOUNDED, OBSERVE-FIRST overlay on the FOM scorer.
It is the runnable implementation of the design in `tech/fom-integration.md`.

For each covered ticker it produces:
  - a DD verdict ∈ {質變, 結構, 過熱, 太早, 受損} + optional per-ticker flags,
  - a sleeve SUGGESTION in the EXISTING four-sleeve vocabulary
    (FOM_CORE / VALUE / MOONSHOT) — reconciled against
    `backtest.sleeve_classifier.classify_sleeve`, and
  - a bounded weight tilt applied through the SAME machinery as the
    analyst-persona ensemble (`analysts.persona.apply_persona_tilt`).

Guardrails (so the DD layer can never blow up the scorer or the book):
  * OBSERVE-FIRST — this overlay is an ANNOTATION. It is NOT folded into
    `final_fom`; the report carries a hypothetical `dd_tilted_base` for
    comparison only, until a walk-forward shows the tilt adds IC (per
    `philosophy/concepts/fom-predictive-validity` + `nasdaq100-calibration`:
    don't fit the narrative into the score).
  * 太早 / 過熱 / front-run → MOONSHOT ring-fence only (≤ the 20% sleeve cap,
    no leverage) — matches the principal's Alpha-sleeve rule.
  * Nothing here trades, sets price targets, or overrides the Risk Officer,
    the position / sector caps, or the 5-dim 十足的證據 gate.

Pure logic + a thin `main()` that reads the latest `outputs/fom-monthly-*.json`
for `bubble_guard` (no network, no new dependency). Curated verdicts are the
judgment layer — review, don't trust blindly.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from sharks.analysts.persona import DIMENSIONS, apply_persona_tilt
from sharks.scoring.ticker_suffix import fx_caveat, parse_ticker, region_of

# ─── Vocabulary ──────────────────────────────────────────────────────────────
VERDICTS = ("質變", "結構", "過熱", "太早", "受損")
# 質變 real qualitative change (data-backed) · 結構 real but largely priced ·
# 過熱 narrative > data (echo-chamber) · 太早 real tech, no near-term P&L/timeline ·
# 受損 structurally impaired (a loser / value-trap).

FLAGS = (
    "cashflow",            # realized P&L 質變 engine
    "froth",               # parabolic / late-stage (usually bubble_guard ≤ -40)
    "front_run",           # right thesis, valuation already reflects it
    "bottom_fish",         # 抄底 turnaround candidate (condition-gated)
    "second_derivative",   # un-crowded pick-and-shovel node (the real early edge)
    "loser",               # structurally eaten / impaired
)

# Sleeve labels MIRROR backtest.sleeve_classifier (FOM_CORE / VALUE / MOONSHOT).
DD_MAX_TILT = 0.06   # DD nudges even more gently than a persona (0.08 ceiling)
DEFAULT_BASE = {"momentum": 0.25, "contrarian": 0.25, "cyclic": 0.15,
                "quality": 0.15, "bubble_guard": 0.20}


@dataclass(frozen=True)
class TechDD:
    ticker: str
    verdict: str
    trend: str                       # source tech/ page slug
    flags: tuple = ()
    milestone_score: float = 0.33    # fraction of the trend's milestone ladder ✅ (tech/_weekly-watch)
    note: str = ""


def _dd(*args) -> TechDD:
    return TechDD(*args)


# ─── The DD registry (broad; per-ticker verdicts from the 15 tech/ pages) ──────
# US-listed only. Curated judgment layer — verdicts/flags trace to a tech/ page.
_ENTRIES = [
    # memory + HBM/optical metrology (memory-supercycle, optical-supply-chain-deep)
    ("MU",  "結構", "memory-supercycle", ("froth",), 0.33, "DRAM/HBM pure-play; bubble_guard -95"),
    ("WDC", "結構", "memory-supercycle", ("froth",), 0.30, ""),
    ("STX", "結構", "memory-supercycle", ("froth",), 0.30, ""),
    ("FORM", "結構", "optical-supply-chain-deep", ("second_derivative",), 0.40, "HBM/CPO probe-card metrology"),
    ("ONTO", "結構", "optical-supply-chain-deep", ("second_derivative",), 0.40, "Dragonfly HBM 2.5D/3D metrology"),
    ("CAMT", "結構", "optical-supply-chain-deep", ("second_derivative",), 0.38, "inspection/metrology crossover"),
    ("AEHR", "過熱", "optical-supply-chain-deep", ("froth",), 0.20, "+5000%/1y on tiny rev"),
    # CPO / optical interconnect (optical-interconnect-cpo)
    ("AXTI", "過熱", "optical-interconnect-cpo", ("froth",), 0.20, "InP substrate; vertical on $27M rev"),
    ("LITE", "結構", "optical-interconnect-cpo", ("froth",), 0.33, "CW laser/EML; NVDA $4B; bg -55"),
    ("COHR", "結構", "optical-interconnect-cpo", (), 0.35, "EML duopoly; bg -40 mild"),
    ("FN",   "結構", "optical-interconnect-cpo", (), 0.40, "system assembly; bg ~0 cleaner"),
    ("MRVL", "結構", "optical-interconnect-cpo", (), 0.38, "custom silicon + optical DSP"),
    ("AAOI", "過熱", "optical-interconnect-cpo", ("froth",), 0.20, "pluggable; parabolic"),
    ("ALAB", "過熱", "optical-interconnect-cpo", ("froth",), 0.22, "connectivity; parabolic"),
    ("CRDO", "過熱", "optical-interconnect-cpo", ("froth",), 0.25, "interconnect; rich"),
    # leadership compute (model-leadership-and-data)
    ("NVDA", "結構", "model-leadership-and-data", (), 0.45, "DRIVE+training; bubble_guard +15 healthy"),
    ("AVGO", "結構", "model-leadership-and-data", (), 0.42, "custom ASIC; +15"),
    ("TSM",  "結構", "optical-interconnect-cpo", (), 0.42, "COUPE CPO chip; upstream chokepoint"),
    ("AMD",  "結構", "ai-edge-devices", (), 0.35, ""),
    ("ARM",  "結構", "ai-edge-devices", (), 0.38, "NPU royalty on ~every edge SoC"),
    ("QCOM", "結構", "ai-edge-devices", (), 0.36, "Snapdragon X / AR SoC / Ride"),
    ("INTC", "結構", "ai-edge-devices", (), 0.28, "turnaround risk"),
    ("AAPL", "結構", "ai-edge-devices", (), 0.35, "VP stalled but core fine"),
    # autonomous (autonomous-driving)
    ("HSAI", "結構", "autonomous-driving", (), 0.35, "LiDAR volume leader; commoditising"),
    ("MBLY", "結構", "autonomous-driving", (), 0.33, "ADAS incumbent; vision-vs-hybrid contested"),
    ("LAZR", "受損", "autonomous-driving", ("loser",), 0.00, "Volvo-dropped, Ch.11; commoditised"),
    ("TSLA", "結構", "autonomous-driving", ("front_run",), 0.30, "robotaxi narrative; L2 today"),
    # pharma + GLP-1 (ai-pharma-glp1, glp1-supply-chain)
    ("LLY",  "質變", "ai-pharma-glp1", ("cashflow",), 0.55, "GLP-1 realized cashflow engine"),
    ("NVO",  "結構", "ai-pharma-glp1", ("cashflow",), 0.40, "GLP-1 #2; orals/去中介 risk"),
    ("RXRX", "太早", "ai-pharma-glp1", (), 0.20, "AI-drug platform; option not cashflow"),
    ("SDGR", "太早", "ai-pharma-glp1", (), 0.22, "physics+AI sim; long-dated option"),
    ("TMO",  "結構", "glp1-supply-chain", ("second_derivative",), 0.38, "merchant fill-finish post-Catalent"),
    # quantum (quantum-vs-bitcoin)
    ("IONQ", "太早", "quantum-vs-bitcoin", (), 0.10, "no near-term economics"),
    ("QBTS", "太早", "quantum-vs-bitcoin", (), 0.10, "annealing, not Shor-capable"),
    ("RGTI", "太早", "quantum-vs-bitcoin", (), 0.08, "rev collapse; narrative-only"),
    # software (ai-eats-software, ai-coding-agents)
    ("MSFT", "結構", "ai-eats-software", ("cashflow",), 0.45, "captor + Copilot/Coding distribution moat"),
    ("AMZN", "結構", "ai-eats-software", ("cashflow",), 0.42, "AWS AI-cloud captor + retail/ads"),
    ("CRM",  "結構", "ai-eats-software", (), 0.35, "captor; data+workflow"),
    ("NOW",  "結構", "ai-eats-software", (), 0.38, "captor; workflow lock-in"),
    ("ADBE", "結構", "ai-eats-software", (), 0.30, "contested; Firefly monetization slow"),
    ("INTU", "結構", "ai-eats-software", ("cashflow",), 0.38, "SMB/tax workflow captor"),
    ("PLTR", "過熱", "ai-eats-software", ("front_run",), 0.35, "right thesis, fwd P/S >85x"),
    ("CHGG", "受損", "ai-eats-software", ("loser",), 0.00, "-99%; eaten by ChatGPT/AI Overviews"),
    # youth-culture platforms (youth-culture-shifts)
    ("UBER", "結構", "youth-culture-shifts", ("cashflow",), 0.42, "delivery×mobility×ads FCF flywheel"),
    ("DASH", "結構", "youth-culture-shifts", ("cashflow",), 0.38, "GAAP-positive; thin margin"),
    ("META", "結構", "youth-culture-shifts", ("cashflow",), 0.42, "attention monopoly + Ray-Ban"),
    ("NFLX", "結構", "youth-culture-shifts", ("cashflow",), 0.40, "streaming > linear"),
    ("SPOT", "結構", "youth-culture-shifts", ("cashflow",), 0.38, "scale + podcasts"),
    ("GOOGL", "結構", "youth-culture-shifts", (), 0.35, "search-share erosion vector"),
    # luxury + apparel (luxury-and-apparel)
    ("NKE",  "結構", "luxury-and-apparel", ("bottom_fish",), 0.40, "inventory reset ✅, brand reset ⏳"),
    ("LULU", "結構", "luxury-and-apparel", (), 0.30, "Americas soft; neutral-bearish"),
    ("ONON", "結構", "luxury-and-apparel", ("front_run",), 0.33, "real share gain, valuation reflects"),
    ("DECK", "結構", "luxury-and-apparel", (), 0.35, "Hoka share gain"),
    ("PDD",  "結構", "luxury-and-apparel", ("froth",), 0.25, "Temu; de-minimis/tariff policy risk"),
    # IP / entertainment (ip-economy-collectibles)
    ("DIS",  "結構", "ip-economy-collectibles", ("bottom_fish",), 0.50, "DTC turn ✅; flywheel reignition"),
    ("HAS",  "結構", "ip-economy-collectibles", ("bottom_fish",), 0.38, "Wizards/MTG bright; toys weak"),
    ("MAT",  "結構", "ip-economy-collectibles", ("bottom_fish",), 0.33, "needs next IP film after Barbie"),
    ("SONY", "結構", "ip-economy-collectibles", (), 0.38, "IP + microdisplay (also AR)"),
    # AR/VR (ar-vr-smart-glasses)
    ("HIMX", "結構", "ar-vr-smart-glasses", ("second_derivative",), 0.33, "display driver / LCoS"),
    ("KOPN", "太早", "ar-vr-smart-glasses", ("froth",), 0.18, "microdisplay spec, tiny"),
    # satcom (satcom-future)
    ("ASTS", "太早", "satcom-future", ("froth",), 0.20, "D2C binary funding/execution bet"),
    ("GSAT", "結構", "satcom-future", (), 0.33, "Apple/partner-funded D2D"),
    ("IRDM", "結構", "satcom-future", (), 0.38, "profitable niche MSS"),
    ("VSAT", "結構", "satcom-future", ("bottom_fish",), 0.40, "deleveraging GEO turnaround"),
    ("SATS", "受損", "satcom-future", ("loser",), 0.10, "EchoStar going-concern; spectrum liquidation"),
    ("RKLB", "結構", "satcom-future", ("front_run",), 0.33, "space pure-play leader; priced"),
    # defense (defense-tech)
    ("LMT",  "結構", "defense-tech", ("bottom_fish",), 0.38, "de-rated; cash-flow defensive"),
    ("RTX",  "結構", "defense-tech", ("bottom_fish",), 0.38, "record backlog $251B"),
    ("NOC",  "結構", "defense-tech", ("bottom_fish",), 0.36, ""),
    ("GD",   "結構", "defense-tech", (), 0.35, ""),
    ("AVAV", "結構", "defense-tech", ("front_run",), 0.33, "drones; priced"),
    ("KTOS", "結構", "defense-tech", ("front_run",), 0.32, "Valkyrie drones; priced"),
    # ── Phase C (2026-05-31) ──────────────────────────────────────────────────
    # ai-datacenter-power (the AI power crunch)
    ("ETN",  "結構", "ai-datacenter-power", (), 0.42, "electricals; DC order backlog"),
    ("VRT",  "結構", "ai-datacenter-power", (), 0.42, "power + liquid cooling"),
    ("GEV",  "結構", "ai-datacenter-power", ("front_run",), 0.38, "gas turbines; ~37-69x fwd"),
    ("PWR",  "結構", "ai-datacenter-power", (), 0.38, "grid buildout"),
    ("NVT",  "結構", "ai-datacenter-power", (), 0.35, "electrical connections"),
    ("CEG",  "結構", "ai-datacenter-power", ("bottom_fish",), 0.45, "nuclear IPP; PPA wave; fell on beat"),
    ("VST",  "結構", "ai-datacenter-power", ("bottom_fish",), 0.42, "IPP"),
    ("TLN",  "結構", "ai-datacenter-power", ("bottom_fish",), 0.40, "IPP; Amazon PPA"),
    ("CCJ",  "結構", "ai-datacenter-power", (), 0.40, "uranium"),
    ("UEC",  "結構", "ai-datacenter-power", ("froth",), 0.30, "uranium small-cap"),
    ("OKLO", "太早", "ai-datacenter-power", ("froth",), 0.15, "pre-rev SMR; COD 2027+ priced like producer"),
    ("SMR",  "太早", "ai-datacenter-power", ("froth",), 0.15, "NuScale pre-rev SMR"),
    ("NNE",  "太早", "ai-datacenter-power", ("froth",), 0.12, "Nano Nuclear pre-rev"),
    # stablecoins-tokenization
    ("CRCL", "結構", "stablecoins-tokenization", ("front_run",), 0.35, "USDC issuer; rate-sensitive, run ahead"),
    ("COIN", "結構", "stablecoins-tokenization", (), 0.38, "~44% USDC econ + Base ~62% tx"),
    ("V",    "結構", "stablecoins-tokenization", ("cashflow",), 0.42, "rails; quiet stablecoin winner"),
    ("MA",   "結構", "stablecoins-tokenization", ("cashflow",), 0.42, "rails; quiet stablecoin winner"),
    ("PYPL", "結構", "stablecoins-tokenization", ("bottom_fish",), 0.33, "PYUSD; turnaround"),
    # cybersecurity-ai
    ("CRWD", "結構", "cybersecurity-ai", ("front_run",), 0.42, "ARR $5.25B; ~20x fwd rev"),
    ("PANW", "結構", "cybersecurity-ai", (), 0.40, "platformization + CyberArk identity"),
    ("ZS",   "結構", "cybersecurity-ai", (), 0.36, "zero-trust edge"),
    ("FTNT", "結構", "cybersecurity-ai", (), 0.38, "cheapest large consolidator"),
    ("NET",  "結構", "cybersecurity-ai", ("front_run",), 0.35, "edge zero-trust; rich"),
    ("S",    "結構", "cybersecurity-ai", ("bottom_fish",), 0.30, "SentinelOne turnaround (unconfirmed)"),
    ("OKTA", "結構", "cybersecurity-ai", ("bottom_fish",), 0.33, "identity turnaround; agent-identity optionality"),
    # china-ai-stack (US ADRs)
    ("BABA", "結構", "china-ai-stack", ("bottom_fish",), 0.38, "Qwen + capex; policy-trap discount"),
    ("BIDU", "結構", "china-ai-stack", ("bottom_fish",), 0.33, "Ernie; cheap"),
    ("JD",   "結構", "china-ai-stack", ("bottom_fish",), 0.33, "value; policy risk"),
    ("TCEHY", "結構", "china-ai-stack", (), 0.36, "Tencent ADR pink; H200-cleared"),
    # space-economy (RKLB/ASTS already mapped under satcom-future)
    ("LUNR", "結構", "space-economy", ("front_run",), 0.33, "lunar gov contracts; priced"),
    ("RDW",  "結構", "space-economy", ("front_run",), 0.28, "~10x P/S Strong Sell"),
    ("PL",   "結構", "space-economy", ("front_run",), 0.33, "EO data; ~51x P/S"),
    # humanoid-robotics (most beneficiaries non-US; NVDA/TSLA already mapped)
    # ── Phase D (2026-05-31) — rf-connectivity (QCOM/AVGO/MRVL/ARM already mapped above) ──
    # handset RFFE — the anti-bubble core (cheap, hated, structurally challenged)
    ("QRVO", "結構", "rf-connectivity", ("bottom_fish",), 0.33, "RFFE; SWKS merger arb (~3.6% gross spread, China SAMR swing); ~half Apple"),
    ("SWKS", "結構", "rf-connectivity", ("bottom_fish",), 0.33, "RFFE; QRVO merger acquirer; ~60% Apple; Broad Mkts +10% diversifying"),
    # power / broad analog — the leading-door cyclical recovery (variable #15)
    ("MPWR", "結構", "rf-connectivity", ("front_run",), 0.38, "AI server power +97.7%; Nvidia socket contested (Infineon/Renesas/ADI); ~50-67x"),
    ("TXN",  "結構", "rf-connectivity", (), 0.38, "broad analog bellwether; recovery + capex/FCF debate; EV/S ~2x 10y median"),
    ("ADI",  "結構", "rf-connectivity", ("cashflow",), 0.40, "broad analog; +30% broad-based recovery; Empower $1.5B vertical-power M&A"),
    ("ON",   "結構", "rf-connectivity", ("bottom_fish",), 0.33, "power/SiC; auto +5% first growth in 8 qtrs; SiC still soft"),
    ("MCHP", "結構", "rf-connectivity", ("bottom_fish",), 0.36, "MCU+analog; cycle bottom confirmed, dist inventory 26 days"),
    ("POWI", "結構", "rf-connectivity", (), 0.33, "high-voltage power conversion + PowiGaN +40%; industrial +23%"),
    ("VICR", "結構", "rf-connectivity", ("front_run",), 0.33, "48V->PoL vertical power for AI; backlog +70%; ~60x + ITC litigation"),
    ("NVTS", "太早", "rf-connectivity", ("froth",), 0.12, "GaN/SiC pure-play; AI 800V demos not revenue; $8.6M rev, ~6-qtr cash runway"),
    ("DIOD", "結構", "rf-connectivity", ("bottom_fish",), 0.35, "discrete/analog consumer-cycle proxy; 6th straight double-digit qtr"),
    ("AOSL", "結構", "rf-connectivity", (), 0.25, "power discretes/PMIC; China exposure, thin 21% GM — value-trap risk"),
    # connectivity (WiFi/BT/Thread/UWB) + audio
    ("SLAB", "結構", "rf-connectivity", (), 0.30, "IoT connectivity bellwether; TI acquisition $231/sh — deal-arb, guidance suspended"),
    ("SYNA", "結構", "rf-connectivity", (), 0.36, "IoT/Veros wireless + edge AI; Core IoT +31%, FY26 +40%"),
    ("NXPI", "結構", "rf-connectivity", (), 0.38, "UWB leader + auto/industrial IoT; Ind&IoT +24%"),
    ("CRUS", "結構", "rf-connectivity", (), 0.30, "audio; ~91% Apple — content growth offsets flat units; latent in-housing risk"),
    ("CEVA", "結構", "rf-connectivity", ("second_derivative",), 0.35, "BT/WiFi/UWB IP royalty; 87% GM; benefits from SoC integration"),
    # picks-and-shovels — own the chokepoint (foundry/test) regardless of who wins
    ("KEYS", "結構", "rf-connectivity", (), 0.40, "6G/NTN/AI test chokepoint — the tollbooth; orders +56%"),
    ("GFS",  "結構", "rf-connectivity", ("second_derivative",), 0.38, "RF-SOI/FDX foundry chokepoint; pivoting to AI silicon photonics"),
    ("TSEM", "結構", "rf-connectivity", ("second_derivative",), 0.38, "RF-SOI/SiGe/SiPho foundry; AI SiPho pivot ($1.3B 2027 commitments)"),
    ("MTSI", "結構", "rf-connectivity", ("front_run",), 0.35, "GaN-on-SiC/mmWave/defense + DC optical; owns Wolfspeed RF; ~73x priced for perfection"),
    ("WOLF", "受損", "rf-connectivity", ("loser",), 0.05, "post-Ch.11; RF business sold to MACOM; SiC balance-sheet scar — not an RF name now"),
    # ── Phase D — offshore-energy (gap-fill; energy physical-resource layer, same rubric) ──
    ("RIG",  "結構", "offshore-energy", ("bottom_fish",), 0.35, "UDW pure-play; P/B ~0.93, deleveraging; acquiring Valaris (73 rigs)"),
    ("VAL",  "結構", "offshore-energy", ("bottom_fish",), 0.33, "cleanest BS (<1x net debt); merging into Transocean"),
    ("NE",   "結構", "offshore-energy", ("bottom_fish",), 0.35, "backlog $7.2B; dividend+buyback; floater dayrate $422k moderating"),
    ("SDRL", "結構", "offshore-energy", (), 0.20, "asset-light; FCF -$35M, slipped to net debt — weakest of the four"),
    ("SLB",  "結構", "offshore-energy", (), 0.35, "OFS #1 intl/offshore; EBITDA -12% YoY cyclical decompression"),
    ("HAL",  "結構", "offshore-energy", (), 0.30, "OFS #2 NAM-frac heavy; near-term headwind"),
    ("BKR",  "結構", "offshore-energy", ("cashflow",), 0.38, "OFSE + LNG/IET growth engine — best diversified"),
    ("FTI",  "結構", "offshore-energy", ("front_run",), 0.33, "subsea chokepoint; backlog $15.8B but re-rated hard"),
    # ── Phase D — copper-electrification (gap-fill #2; physical-resource layer) ──
    ("FCX",  "結構", "copper-electrification", ("front_run",), 0.33, "largest US Cu+gold; Grasberg -35% 2026; ~23x P/E rich"),
    ("SCCO", "結構", "copper-electrification", ("front_run",), 0.30, "lowest-cost pure Cu; record NI but Scotia Underperform/stretched"),
    ("TECK", "結構", "copper-electrification", (), 0.38, "Cu-focused; EBITDA +125%; Anglo merger catalyst"),
    ("ERO",  "結構", "copper-electrification", (), 0.30, "small-cap Brazil pure-Cu torque"),
    ("HBM",  "結構", "copper-electrification", (), 0.33, "mid-cap Cu; record rev $757M"),
    ("BHP",  "結構", "copper-electrification", ("cashflow",), 0.40, "Cu now 51% of EBITDA; best quality Cu leverage, lower multiple"),
    ("RIO",  "結構", "copper-electrification", ("cashflow",), 0.38, "Cu growth engine (Oyu Tolgoi); diversified, cheaper"),
    ("VALE", "結構", "copper-electrification", (), 0.30, "diversified Fe/Ni + growing Cu; cheap but not a clean Cu play"),
    # ── Phase D — consumer-credit-stress (gap-fill #3; RISK GAUGE, A4=0; exposures not longs) ──
    ("ALLY", "結構", "consumer-credit-stress", (), 0.25, "subprime-auto canary; NCO improving (realized) but guiding worse on labor — risk gauge, not a long thesis"),
    ("COF",  "結構", "consumer-credit-stress", (), 0.25, "card+auto; credit improving YoY — consumer-credit gauge input"),
    ("AFRM", "結構", "consumer-credit-stress", ("front_run",), 0.20, "BNPL leader; credit stable but equity ran — don't chase; risk-gauge exposure"),
    ("KLAR", "結構", "consumer-credit-stress", ("front_run",), 0.15, "BNPL; provision +102% YoY + securities class action — the bear's exhibit"),
    ("CVNA", "結構", "consumer-credit-stress", ("front_run",), 0.20, "used-car; 44% nonprime/deep-subprime credit-mix risk; equity ran hard"),
    ("KMX",  "結構", "consumer-credit-stress", ("bottom_fish",), 0.30, "used-car; Tier-3 deepening; value but credit-cycle exposed"),
    ("DG",   "結構", "consumer-credit-stress", ("bottom_fish",), 0.33, "dollar-store; low-income wallet read + trade-down tailwind"),
    ("DLTR", "結構", "consumer-credit-stress", ("bottom_fish",), 0.33, "dollar-store; trade-down skews higher-income = mild positive"),
]

TECH_DD: dict[str, TechDD] = {e[0]: _dd(*e) for e in _ENTRIES}

# Non-US nodes covered by the tech/ pages but awaiting Phase-2 ticker-suffix
# support (documented for breadth; NOT scanned until suffixes land). See
# watchlist/serenity-supply-chain.yaml for the supply-chain subset.
TECH_DD_NONUS = {
    # memory
    "000660.KS": ("結構", "memory-supercycle", "SK Hynix — HBM4 pricing-power chokepoint"),
    "005930.KS": ("結構", "memory-supercycle", "Samsung — HBM4 recovery optionality"),
    # optical / CPO
    "8053.T": ("結構", "optical-supply-chain-deep", "Sumitomo — InP substrate + EML (the calm one)"),
    "5801.T": ("結構", "optical-supply-chain-deep", "Furukawa — DFB CW laser"),
    "2455.TW": ("結構", "optical-interconnect-cpo", "VPEC — InP epi foundry"),
    "3008.TW": ("結構", "ar-vr-smart-glasses", "Largan — precision optics"),
    "322310.KQ": ("結構", "optical-supply-chain-deep", "Auros — hybrid-bond metrology (most un-crowded)"),
    "0522.HK": ("結構", "optical-supply-chain-deep", "ASMPT — CPO coupling + TCB/hybrid bond"),
    # luxury
    "MC.PA": ("結構", "luxury-and-apparel", "LVMH — recovering"),
    "RMS.PA": ("結構", "luxury-and-apparel", "Hermès — quality compounder"),
    "CFR.SW": ("結構", "luxury-and-apparel", "Richemont"),
    "KER.PA": ("受損", "luxury-and-apparel", "Kering/Gucci — value-trap until Demna sell-through"),
    # IP
    "9992.HK": ("結構", "ip-economy-collectibles", "Pop Mart — star-machine, tightest valuation"),
    "8136.T": ("結構", "ip-economy-collectibles", "Sanrio — asset-light licensing"),
    "7832.T": ("結構", "ip-economy-collectibles", "Bandai Namco — IP flywheel"),
    # AR
    "EL.PA": ("結構", "ar-vr-smart-glasses", "EssilorLuxottica — Ray-Ban brand+channel+assembly"),
    # defense
    "RHM.DE": ("結構", "defense-tech", "Rheinmetall — signed backlog, the highest-conviction"),
    "HAG.DE": ("結構", "defense-tech", "Hensoldt — book-to-bill 1.5-2.0x"),
    "SAAB-B.ST": ("結構", "defense-tech", "Saab"),
    # GLP-1 supply
    "BANB.SW": ("結構", "glp1-supply-chain", "Bachem — peptide API duopoly"),
    "YPSN.SW": ("結構", "glp1-supply-chain", "Ypsomed — auto-injector"),
}


# ─── Pure logic: tilt, sleeve routing, milestone gate ──────────────────────────
def _dd_clamp(tilt: dict) -> dict:
    """Clamp each dimension delta into [-DD_MAX_TILT, +DD_MAX_TILT]."""
    return {d: max(-DD_MAX_TILT, min(DD_MAX_TILT, float(tilt.get(d, 0.0)))) for d in DIMENSIONS}


def dd_verdict_tilt(verdict: str, flags=()) -> dict:
    """Map a DD verdict (+ flags) to a bounded per-dimension weight tilt.
    The regime/quant decides; DD only nudges (|delta| <= DD_MAX_TILT)."""
    flags = set(flags)
    t = {d: 0.0 for d in DIMENSIONS}
    base = {
        "質變": {"momentum": 0.03, "quality": 0.03},
        "結構": {"quality": 0.02, "momentum": -0.01},
        "過熱": {"momentum": -0.06},
        "太早": {"momentum": -0.04, "quality": -0.02},
        "受損": {"momentum": -0.06, "quality": -0.06},
    }.get(verdict, {})
    for k, v in base.items():
        t[k] += v
    if "second_derivative" in flags:
        t["contrarian"] += 0.03      # reward the not-yet-crowded node
    if "bottom_fish" in flags:
        t["contrarian"] += 0.03
        t["quality"] += 0.02
    if "front_run" in flags:
        t["momentum"] -= 0.04        # do not chase the priced-in darling
    if "froth" in flags:
        t["momentum"] -= 0.03
    if "cashflow" in flags:
        t["quality"] += 0.02
    return _dd_clamp(t)


def dd_sleeve(verdict: str, bubble_guard: Optional[float] = None,
              milestone_score: float = 0.0, flags=()) -> dict:
    """Route a name to a sleeve (FOM_CORE / VALUE / MOONSHOT) + a posture.
    Mirrors tech/fom-integration.md §2a. bubble_guard is the FOM late-cycle
    reading (negative = stress); None = route on the verdict alone."""
    flags = set(flags)
    frothy = (bubble_guard is not None and bubble_guard <= -40) or ("froth" in flags)

    if verdict == "受損" or "loser" in flags:
        return {"sleeve": "MOONSHOT", "posture": "avoid",
                "reason": "structurally impaired / value-trap — avoid or tax-loss only"}
    if verdict == "太早":
        return {"sleeve": "MOONSHOT", "posture": "ring_fence",
                "reason": "no near-term P&L / timeline — Moonshot ring-fence ≤20%, no leverage"}
    if verdict == "過熱" or "front_run" in flags:
        return {"sleeve": "MOONSHOT", "posture": "ring_fence",
                "reason": "narrative > data / valuation front-run — ring-fence; wait for pullback"}
    if verdict == "質變":
        if milestone_score >= 0.5 and (bubble_guard is None or bubble_guard >= -20):
            return {"sleeve": "FOM_CORE", "posture": "core",
                    "reason": "realized-cashflow 質變 + milestone met — core-eligible (still gated by evidence + caps)"}
        return {"sleeve": "FOM_CORE", "posture": "core_watch",
                "reason": "質變 but milestone/bubble_guard not yet clear — core watch"}
    if verdict == "結構":
        if frothy:
            return {"sleeve": "VALUE", "posture": "value_on_pullback",
                    "reason": "real but overheated (bubble_guard low / froth) — Value sleeve only on a confirmed, quality-filtered pullback"}
        if "bottom_fish" in flags:
            posture = "core_watch" if milestone_score >= 0.5 else "value_on_pullback"
            return {"sleeve": "VALUE", "posture": posture,
                    "reason": "beaten-down QUALITY 抄底 (撿菸頭) — condition-gated; margin of safety in the quality filter"}
        if "second_derivative" in flags:
            return {"sleeve": "FOM_CORE", "posture": "core_watch",
                    "reason": "un-crowded second-derivative node — the early edge; build on confirmation"}
        if bubble_guard is not None and bubble_guard >= 0:
            posture = "core" if milestone_score >= 0.5 else "core_watch"
            return {"sleeve": "FOM_CORE", "posture": posture, "reason": "結構 + healthy bubble_guard — better-entry side"}
        return {"sleeve": "FOM_CORE", "posture": "core_watch", "reason": "結構 — default core watch"}
    return {"sleeve": "FOM_CORE", "posture": "core_watch", "reason": "uncovered verdict — default core watch"}


# ─── Multi-horizon routing (verdict_by_horizon → FOM 3m/12m/36m lenses) ────────
# Per-trend T0-T3 verdict arcs (from tech/scoreboard.md). A name can be 過熱 at T0
# (don't chase the 3m) yet 質變 at T2-T3 (accumulate for the 36m/value sleeve).
_H = ("T0", "T1", "T2", "T3")
TREND_HORIZON: dict[str, dict[str, str]] = {
    # Phase A
    "memory-supercycle":         {"T0": "結構", "T1": "結構", "T2": "結構", "T3": "結構"},
    "optical-interconnect-cpo":  {"T0": "結構", "T1": "結構", "T2": "結構", "T3": "結構"},
    "optical-supply-chain-deep": {"T0": "結構", "T1": "結構", "T2": "結構", "T3": "結構"},
    "ai-edge-devices":           {"T0": "過熱", "T1": "過熱", "T2": "結構", "T3": "結構"},
    "autonomous-driving":        {"T0": "結構", "T1": "結構", "T2": "質變", "T3": "質變"},
    "ai-pharma-glp1":            {"T0": "結構", "T1": "質變", "T2": "質變", "T3": "結構"},
    "glp1-supply-chain":         {"T0": "結構", "T1": "結構", "T2": "結構", "T3": "結構"},
    "quantum-vs-bitcoin":        {"T0": "太早", "T1": "太早", "T2": "太早", "T3": "結構"},
    "ai-eats-software":          {"T0": "結構", "T1": "結構", "T2": "質變", "T3": "質變"},
    "model-leadership-and-data": {"T0": "質變", "T1": "結構", "T2": "結構", "T3": "結構"},
    "youth-culture-shifts":      {"T0": "結構", "T1": "結構", "T2": "結構", "T3": "結構"},
    # Phase B
    "luxury-and-apparel":        {"T0": "過熱", "T1": "結構", "T2": "結構", "T3": "結構"},
    "ip-economy-collectibles":   {"T0": "過熱", "T1": "結構", "T2": "結構", "T3": "質變"},
    "ai-coding-agents":          {"T0": "質變", "T1": "結構", "T2": "結構", "T3": "結構"},
    "ar-vr-smart-glasses":       {"T0": "結構", "T1": "結構", "T2": "太早", "T3": "質變"},
    "satcom-future":             {"T0": "結構", "T1": "結構", "T2": "太早", "T3": "太早"},
    "defense-tech":              {"T0": "結構", "T1": "結構", "T2": "質變", "T3": "質變"},
    # Phase C
    "humanoid-robotics":         {"T0": "太早", "T1": "結構", "T2": "質變", "T3": "質變"},
    "ai-datacenter-power":       {"T0": "結構", "T1": "結構", "T2": "質變", "T3": "太早"},
    "stablecoins-tokenization":  {"T0": "結構", "T1": "結構", "T2": "過熱", "T3": "太早"},
    "cybersecurity-ai":          {"T0": "結構", "T1": "質變", "T2": "質變", "T3": "結構"},
    "china-ai-stack":            {"T0": "結構", "T1": "結構", "T2": "質變", "T3": "質變"},
    "space-economy":             {"T0": "結構", "T1": "質變", "T2": "太早", "T3": "太早"},
    # Phase D
    "rf-connectivity":           {"T0": "結構", "T1": "結構", "T2": "結構", "T3": "質變"},
    "offshore-energy":           {"T0": "結構", "T1": "結構", "T2": "質變", "T3": "太早"},
    "copper-electrification":    {"T0": "過熱", "T1": "結構", "T2": "質變", "T3": "質變"},
    "consumer-credit-stress":    {"T0": "結構", "T1": "結構", "T2": "結構", "T3": "結構"},
}
_HORIZON_TO_FOM = {"T0": "fom_3m", "T1": "fom_12m", "T2": "fom_36m", "T3": "fom_36m"}

# Per-trend 5-axis rubric (from tech/scoreboard.md). Used by bayesian_update to
# build a quality-differentiated prior (verdict alone is too coarse — all 結構
# names would otherwise share a prior). A ticker inherits its trend's rubric.
TREND_RUBRIC: dict[str, dict[str, int]] = {
    "memory-supercycle":         {"A1": 2, "A2": 2, "A3": 2, "A4": 2, "A5": 1},
    "optical-interconnect-cpo":  {"A1": 2, "A2": 1, "A3": 2, "A4": 2, "A5": 1},
    "optical-supply-chain-deep": {"A1": 2, "A2": 1, "A3": 2, "A4": 2, "A5": 1},
    "ai-edge-devices":           {"A1": 1, "A2": 1, "A3": 2, "A4": 2, "A5": 1},
    "autonomous-driving":        {"A1": 2, "A2": 2, "A3": 2, "A4": 1, "A5": 1},
    "ai-pharma-glp1":            {"A1": 2, "A2": 2, "A3": 2, "A4": 2, "A5": 1},
    "glp1-supply-chain":         {"A1": 2, "A2": 2, "A3": 2, "A4": 2, "A5": 1},
    "quantum-vs-bitcoin":        {"A1": 2, "A2": 1, "A3": 2, "A4": 1, "A5": 1},
    "ai-eats-software":          {"A1": 2, "A2": 2, "A3": 2, "A4": 1, "A5": 1},
    "model-leadership-and-data": {"A1": 2, "A2": 2, "A3": 2, "A4": 1, "A5": 2},
    "youth-culture-shifts":      {"A1": 2, "A2": 2, "A3": 2, "A4": 2, "A5": 1},
    "luxury-and-apparel":        {"A1": 2, "A2": 2, "A3": 2, "A4": 2, "A5": 1},
    "ip-economy-collectibles":   {"A1": 2, "A2": 2, "A3": 2, "A4": 1, "A5": 1},
    "ai-coding-agents":          {"A1": 2, "A2": 2, "A3": 2, "A4": 1, "A5": 2},
    "ar-vr-smart-glasses":       {"A1": 2, "A2": 2, "A3": 2, "A4": 2, "A5": 1},
    "satcom-future":             {"A1": 2, "A2": 2, "A3": 2, "A4": 1, "A5": 1},
    "defense-tech":              {"A1": 2, "A2": 2, "A3": 2, "A4": 1, "A5": 1},
    "humanoid-robotics":         {"A1": 1, "A2": 1, "A3": 2, "A4": 2, "A5": 1},
    "ai-datacenter-power":       {"A1": 2, "A2": 2, "A3": 2, "A4": 2, "A5": 1},
    "stablecoins-tokenization":  {"A1": 2, "A2": 2, "A3": 2, "A4": 1, "A5": 1},
    "cybersecurity-ai":          {"A1": 2, "A2": 2, "A3": 2, "A4": 1, "A5": 1},
    "china-ai-stack":            {"A1": 2, "A2": 2, "A3": 2, "A4": 1, "A5": 2},
    "rf-connectivity":           {"A1": 2, "A2": 2, "A3": 2, "A4": 2, "A5": 1},
    "offshore-energy":           {"A1": 2, "A2": 1, "A3": 1, "A4": 2, "A5": 1},
    "copper-electrification":    {"A1": 2, "A2": 2, "A3": 1, "A4": 1, "A5": 1},
    "consumer-credit-stress":    {"A1": 2, "A2": 2, "A3": 2, "A4": 0, "A5": 1},
}


def dd_horizon_routing(ticker: str, bubble_guard: Optional[float] = None) -> dict:
    """Per-horizon sleeve for a covered name: maps the trend's T0-T3 verdict arc
    (TREND_HORIZON) onto the FOM 3m/12m/36m lenses. Realises the principal's
    '同一檔 3m=過熱不追、36m=質變佈局'. Falls back to the headline verdict if the
    trend carries no arc."""
    dd = TECH_DD.get(ticker.upper())
    if dd is None:
        return {}
    arc = TREND_HORIZON.get(dd.trend)
    out = {}
    for h in _H:
        v = arc[h] if arc else dd.verdict
        r = dd_sleeve(v, bubble_guard, dd.milestone_score, dd.flags)
        out[h] = {"verdict": v, "fom_lens": _HORIZON_TO_FOM[h],
                  "sleeve": r["sleeve"], "posture": r["posture"]}
    return out


def annotate_ticker(ticker: str, bubble_guard: Optional[float] = None,
                    base_weights: Optional[dict] = None) -> Optional[dict]:
    """Full DD annotation for one ticker (pure). Returns None if not covered.
    `dd_tilted_base` is OBSERVE-ONLY — it is never the live final_fom."""
    dd = TECH_DD.get(ticker.upper())
    if dd is None:
        return None
    base = dict(base_weights or DEFAULT_BASE)
    tilt = dd_verdict_tilt(dd.verdict, dd.flags)
    sleeve = dd_sleeve(dd.verdict, bubble_guard, dd.milestone_score, dd.flags)
    out = {
        "ticker": dd.ticker,
        "dd_verdict": dd.verdict,
        "trend": dd.trend,
        "flags": list(dd.flags),
        "milestone_score": dd.milestone_score,
        "note": dd.note,
        "bubble_guard": bubble_guard,
        "dd_sleeve": sleeve["sleeve"],
        "posture": sleeve["posture"],
        "reason": sleeve["reason"],
        "dd_tilt": tilt,
        "dd_tilted_base": apply_persona_tilt(base, tilt),   # observe-only
        "horizon_routing": dd_horizon_routing(dd.ticker, bubble_guard),
    }
    # Cross-check against the structural character-set classifier (打臉/agreement).
    try:
        from sharks.backtest.sleeve_classifier import classify_sleeve
        struct = classify_sleeve(dd.ticker)
        out["structural_sleeve"] = struct["sleeve"]
        out["sleeve_agreement"] = (struct["sleeve"] == sleeve["sleeve"])
    except Exception:  # pragma: no cover - classifier optional
        out["structural_sleeve"] = None
        out["sleeve_agreement"] = None
    return out


def annotate_non_us(symbol: str) -> Optional[dict]:
    """Lightweight annotation for a documented non-US node (Phase-2 後綴支援):
    verdict-only routing + region/FX tags via ticker_suffix. bubble_guard is
    unavailable until a regional FOM scan lands, so routing is verdict-only and
    carries the FX caveat."""
    rec = TECH_DD_NONUS.get(symbol)
    if rec is None:
        return None
    verdict, trend, note = rec
    sleeve = dd_sleeve(verdict, None, 0.33, ())
    p = parse_ticker(symbol)
    return {
        "ticker": symbol,
        "dd_verdict": verdict,
        "trend": trend,
        "note": note,
        "milestone_score": 0.33,
        "region": region_of(symbol),
        "currency": p.exchange.currency if p.exchange else "USD",
        "dd_sleeve": sleeve["sleeve"],
        "posture": sleeve["posture"],
        "reason": sleeve["reason"],
        "fx_caveat": fx_caveat(symbol),
        "non_us": True,
    }


# ─── FOM bubble_guard loader (no network) ──────────────────────────────────────
def load_fom_bubble_guard(out_dir: Path) -> dict:
    """Read the latest outputs/fom-monthly-*.json → {ticker: {bubble_guard, final_fom}}.
    Returns {} if no FOM report is present (routing then falls back to verdict-only)."""
    files = sorted(Path(out_dir).glob("fom-monthly-*.json"))
    if not files:
        return {}
    data = json.loads(files[-1].read_text(encoding="utf-8"))
    rows = data.get("ranked_full") or data.get("top_50_watchlist") or []
    bg = {}
    for r in rows:
        t = r.get("ticker")
        if not t:
            continue
        bg[t] = {"bubble_guard": r.get("bubble_guard_val", r.get("bubble_guard")),
                 "final_fom": r.get("final_fom")}
    return bg


def build_report(out_dir: Path = Path("outputs"), base_weights: Optional[dict] = None,
                 include_non_us: bool = False) -> dict:
    """Annotate the whole DD registry, bucket by suggested sleeve, sort. Observe-first.
    include_non_us folds the documented non-US nodes in (verdict-only routing + FX
    caveat, Phase-2 後綴支援)."""
    bg_map = load_fom_bubble_guard(out_dir)
    annotated = []
    for t in TECH_DD:
        bg = (bg_map.get(t) or {}).get("bubble_guard")
        row = annotate_ticker(t, bubble_guard=bg, base_weights=base_weights)
        if row:
            row["final_fom"] = (bg_map.get(t) or {}).get("final_fom")
            annotated.append(row)
    if include_non_us:
        for sym in TECH_DD_NONUS:
            nr = annotate_non_us(sym)
            if nr:
                nr["final_fom"] = None
                annotated.append(nr)

    buckets: dict[str, list] = {"FOM_CORE": [], "VALUE": [], "MOONSHOT": []}
    for r in annotated:
        buckets.setdefault(r["dd_sleeve"], []).append(r)
    for s in buckets:
        buckets[s].sort(key=lambda r: (-(r["milestone_score"]), -((r.get("final_fom") or 0))))

    disagreements = [
        {"ticker": r["ticker"], "dd_sleeve": r["dd_sleeve"], "structural_sleeve": r["structural_sleeve"]}
        for r in annotated if r.get("sleeve_agreement") is False
    ]
    return {
        "observe_first": True,
        "note": ("OBSERVE-ONLY overlay. dd_tilted_base is hypothetical; final_fom is "
                 "unchanged. Verdicts are screen outputs — Risk Officer + caps + the "
                 "5-dim evidence gate still govern. See tech/fom-integration.md."),
        "fom_report_used": bool(bg_map),
        "coverage": {"us_listed": len(TECH_DD), "non_us_documented": len(TECH_DD_NONUS),
                     "non_us_included": include_non_us},
        "buckets": buckets,
        "sleeve_disagreements_vs_structural": disagreements,
    }


def main(out_dir: Path = Path("outputs")) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_report(out_dir)
    # stamp time at write (not in pure logic, to keep build_report deterministic/testable)
    report["as_of"] = datetime.now(timezone.utc).isoformat()
    counts = {s: len(v) for s, v in report["buckets"].items()}
    out_path = out_dir / "tech-dd-overlay.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"  coverage: {report['coverage']}  fom_used={report['fom_report_used']}", file=sys.stderr)
    print(f"  sleeve buckets: {counts}", file=sys.stderr)
    if report["sleeve_disagreements_vs_structural"]:
        print(f"  DD vs structural-classifier disagreements: "
              f"{[d['ticker'] for d in report['sleeve_disagreements_vs_structural']]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
