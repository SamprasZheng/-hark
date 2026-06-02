---
type: synthesis
domain: tech-trend
tags: [moc, industry-map, semiconductor, electronics, value-chain, vertical, horizontal, supply-chain, edge-cloud-seam]
as_of_timestamp: 2026-05-31T23:30:00+08:00
author_role: researcher
status: live
schema_version: 1
---
# 半導體 / 電子產業全圖 — 垂直價值鏈 × 水平分段 / Semiconductor & Electronics Industry Map

> Principal 要的「脈絡」:把所有 tech/ 頁、所有個股,掛上一張**垂直(誰賣給誰)× 水平(做哪一類晶片)**的母圖。這張圖是 [[index]] 的骨幹——每一條趨勢頁都是這張圖上某幾格的放大。Research/educational,非買賣建議。

## 0. 一句話心智模型
**「沙子 → 雲」一條龍**:把石英砂變成 AI 推論,中間經過 ~12 道垂直關卡;每一關都有 1–3 家定價權瓶頸。**alpha 不在「誰做晶片」,在「哪一關卡最窄、最難被替代、且還沒被定價」。** Principal 的 RF 論點([[rf-connectivity]])就是其中一關:**地端(edge device)與雲端(cloud)都在強化,中間的「連結縫」(RF/光/網路)必須變寬** —— 這條縫垂直貫穿「設計→晶圓→封測→系統」,水平橫跨「RF / 光 / 網通」三段。

---

## 1. 垂直價值鏈 (上游 → 下游) — 12 關卡 + 瓶頸 + 對應頁

| # | 關卡 Layer | 在做什麼 | 定價權瓶頸 / 代表 | 對應 tech/ 頁 |
|---|---|---|---|---|
| 1 | **材料 Materials** | 矽晶圓、光阻、特殊氣體、CMP、載板基材、化合物基板(GaN/SiC/InP/GaAs) | 矽晶圓(信越/SUMCO)、光阻(JSR/TOK)、InP 基板(住友/AXT)、SiC(WOLF 出清中) | [[optical-supply-chain-deep]]、[[rf-connectivity]](RF-SOI/GaN) |
| 2 | **設備 Equipment** | 微影、蝕刻、沉積、量測、封裝設備 | **EUV 微影=ASML 獨佔**;蝕刻/沉積(AMAT/LRCX/TEL);量測(KLAC + hybrid-bond 的 Onto/FormFactor/Auros) | [[optical-supply-chain-deep]](量測最未擁擠) |
| 3 | **EDA / IP** | 設計工具 + 可授權 IP 核 | EDA 三雄(Synopsys/Cadence/Siemens);IP(ARM=幾乎每顆 edge SoC 的權利金、CEVA=連結性 IP) | [[ai-edge-devices]]、[[rf-connectivity]](CEVA) |
| 4 | **無晶圓設計 Fabless** | 設計但不製造的晶片公司 | NVDA/AMD/QCOM/AVGO/MRVL/Apple-silicon;RF 設計(QRVO/SWKS) | 幾乎每一頁 |
| 5 | **晶圓代工 Foundry** | 把設計變成晶片 | **先進製程=TSMC 獨大**;特殊製程 foundry(GFS=RF-SOI/FDX、TSEM=RF-SOI/SiPho、WIN=GaAs) | [[rf-connectivity]](GFS/TSEM)、[[china-ai-stack]](SMIC) |
| 6 | **先進封裝 Advanced Packaging** | CoWoS / HBM 堆疊 / 混合鍵合 / CPO 共封裝 | **CoWoS=TSMC 瓶頸**;HBM(SK海力士/三星/MU);OSAT(ASE/Amkor) | [[memory-supercycle]]、[[optical-interconnect-cpo]] |
| 7 | **記憶體 Memory** | DRAM / HBM / NAND | HBM 三雄定價權;**2026 記憶體擠壓是手機 RF 的逆風** | [[memory-supercycle]] |
| 8 | **被動 / 電源 / 類比 Passives·Power·Analog** | MLCC、電源管理 IC、broad 類比、GaN 充電/供電 | broad 類比(TXN/ADI);AI 垂直供電(MPWR/VICR/ADI-Empower);GaN(POWI/NVTS) | [[rf-connectivity]]、[[ai-datacenter-power]] |
| 9 | **互連 Interconnect** | 光模組、CPO、銅纜、交換器、DPU、RF 前端 | 光(COHR/LITE/光 DSP=MRVL);CPO(TSMC COUPE);**RF 前端(BAW 雙雄 AVGO/QRVO)** | [[optical-interconnect-cpo]]、[[rf-connectivity]] |
| 10 | **系統 / 整機 System·ODM** | 伺服器、手機、PC、網通設備、基地台、衛星 | 伺服器(DELL/HPE/SMCI/鴻海);手機(Apple/三星);基地台(ERIC/NOK 谷底) | [[ai-edge-devices]]、[[satcom-future]]、[[rf-connectivity]] |
| 11 | **基礎設施 Infra** | 資料中心電力/散熱/電網、衛星星座、地面網路 | 電力(VRT/ETN/GEV/IPP);散熱(液冷);頻譜(D2C) | [[ai-datacenter-power]]、[[satcom-future]] |
| 12 | **應用 / 雲 Application·Cloud** | 模型、軟體、agent、終端服務 | 模型層(輪動);軟體(captor 贏家);算力雲(CSP) | [[model-leadership-and-data]]、[[ai-eats-software]]、[[ai-coding-agents]]、[[cybersecurity-ai]] |

**測試與封裝橫跨各關**:測試=KEYS(6G/RF/NTN tollbooth)、TER/AEHR(SoC/burn-in);**KEYS 是「不管哪個頻段/標準贏都收過路費」的乾淨瓶頸**([[rf-connectivity]] §4g)。

---

## 2. 水平分段 (晶片類別) × 各段的定價權與頁面

| 水平段 Segment | 是什麼 | 定價權結構 | 代表 / 頁 |
|---|---|---|---|
| **邏輯 Logic / 運算** | CPU/GPU/NPU/ASIC | GPU=NVDA;客製 ASIC=AVGO/MRVL+CSP 自研(TPU/Trainium) | [[model-leadership-and-data]]、[[china-ai-stack]] |
| **記憶體 Memory** | DRAM/HBM/NAND | 三雄寡占 | [[memory-supercycle]] |
| **類比 / 電源 Analog·Power** | 電源管理、訊號鏈、broad 類比、WBG | 分散但高黏著;TXN/ADI 龍頭;GaN/SiC 新興 | [[rf-connectivity]]、[[ai-datacenter-power]] |
| **射頻 RF / 連結性** | PA/濾波器/switch/tuner、Wi-Fi/BT/UWB、modem | **BAW 雙雄(AVGO/QRVO)**;濾波器=中國最難啃;UWB=NXP | **[[rf-connectivity]]**、[[satcom-future]] |
| **光電 Optical / 光子** | 光模組、SiPho、CPO、雷射 | EML 寡占;SiPho foundry(GFS/TSEM) | [[optical-interconnect-cpo]]、[[optical-supply-chain-deep]] |
| **感測 Sensors** | CIS、LiDAR、MEMS、雷達 | CIS(Sony);LiDAR 商品化 | [[autonomous-driving]]、[[ar-vr-smart-glasses]] |
| **分離 / 功率元件 Discretes·Power devices** | MOSFET、IGBT、SiC/GaN 元件 | ON/STM/Infineon;WOLF 出清 | [[rf-connectivity]] |
| **顯示驅動 Display** | DDIC、LCoS、microLED | HIMX;AR 微顯示 | [[ar-vr-smart-glasses]] |

---

## 3. Principal 的「edge ↔ cloud 縫」貫穿圖
```
   地端 EDGE                    ┌──── 連結縫 THE SEAM ────┐                   雲端 CLOUD
 (端側裝置/SLM)                 (RF / 光 / 網通 — 必須變寬)               (資料中心/大模型)
 手機·PC·眼鏡·IoT  ──無線──▶  RF 前端(BAW/PA/濾波器) ─▶ 基地台/Wi-Fi/衛星  ──光──▶  交換器/CPO/光模組 ─▶ GPU/HBM/電力
 [[ai-edge-devices]]         [[rf-connectivity]]·[[satcom-future]]        [[optical-interconnect-cpo]]·[[ai-datacenter-power]]
   記憶體得利                  你的本行 + 變數#15 急單                      記憶體/CPO/電力瓶頸
```
**讀法**:兩端(edge SLM、cloud LLM)都在 [[../philosophy/11-cloud-local-split]] 的「大模型蒐集派發 / 小模型執行」框架下強化;**縫**有兩條物理路徑——**地面無線(RF,6G FR3 拉 massive-MIMO)** + **天上(衛星 D2C/NTN)** → 進到資料中心後變成 **光(CPO/SiPho)**。所以「縫變寬」的投資表達 = RF 前端(已便宜)+ 光子 foundry(GFS/TSEM)+ 測試(KEYS),而非追已 OVERHEAT 的電源/類比(見 `outputs/rfpm-cycle-*.json` 即時讀數)。

---

## 4. 三條鐵律 (跨全圖)
1. **受益者 ≠ 該價位的股票**:全 [[scoreboard]] 22+ 條的共識——真實趨勢多已被定價。**唯一方向相反的是 RF/類比([[rf-connectivity]]):基本面被忽略而非敘事超前(anti-bubble)**——但「便宜≠低估」,手機前端便宜是結構性的。
2. **擁瓶頸,不擁故事**:每一關卡的 alpha 在最窄、最難替代、最未擁擠的節點(EUV、CoWoS、HBM、BAW 濾波器、RF-SOI、hybrid-bond 量測、6G 測試)。
3. **二階 > 一階**:鏟子(設備/材料/測試/foundry/IP)的現金流比終端品牌更可預測,且常更未擁擠——[[optical-supply-chain-deep]] / [[rf-connectivity]] §4g / [[glp1-supply-chain]] 都是這個邏輯。

## 5. See also
- [[index]] — tech-DD 導覽 · [[scoreboard]] — 全趨勢計分板 · [[99_cross_synthesis]] — 跨趨勢綜效
- [[rf-connectivity]] — RF/連結縫(本圖第 4·9 段)· [[offshore-energy]] — 能源實體層(非半導體,但同 rubric)
- [[../philosophy/concepts/supply-chain-bottleneck]] — 瓶頸 alpha 框架 · [[../philosophy/11-cloud-local-split]] — edge↔cloud 契約
