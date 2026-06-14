**✅ 已加入 Sharpe Ratio 到 Fitness 計算**

以下是將 **Sharpe Ratio** 整合進 Layer 2 演化比賽 Fitness 的實務設計與程式碼框架。

### 1. 為什麼要在 Fitness 中加入 Sharpe Ratio？

目前你的演化比賽主要依賴報酬表現，容易讓高風險、高波動的策略（特別是小盤催化劑與動能類）在牛市中勝出。加入 **Sharpe Ratio** 可以：

- 提升**風險調整後報酬**的權重
- 讓不同風格交易員的比較更公平
- 減少「高報酬但高回撤」的策略長期勝出
- 強化跨 Regime 的穩健性

### 2. 建議的混合 Fitness 公式

```python
Final Fitness = 
    (Price-based Fitness × 0.45) + 
    (Fundamental Score × 0.25) + 
    (Sharpe-based Score × 0.30)
```

- **Price-based Fitness**：原本的累積報酬 + 最大回撤控制
- **Fundamental Score**：ROIC + OCF Margin + Investing Intensity（Phase 2 新增）
- **Sharpe-based Score**：風險調整後報酬（新加入）

### 3. 完整 Fitness 計算框架

```python
# simulation/layer2/fitness_calculator.py

import numpy as np
from typing import Dict

class FitnessCalculator:
    def __init__(self, 
                 price_weight: float = 0.45,
                 fundamental_weight: float = 0.25,
                 sharpe_weight: float = 0.30):
        self.price_weight = price_weight
        self.fundamental_weight = fundamental_weight
        self.sharpe_weight = sharpe_weight

    def calculate_sharpe_score(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """
        計算年化 Sharpe Ratio 並轉換為 0~100 分數
        """
        if len(returns) < 4:  # 至少需要 4 季數據
            return 50.0
        
        excess_returns = returns - (risk_free_rate / 4)  # 季化無風險利率
        mean_excess = np.mean(excess_returns)
        std_excess = np.std(excess_returns)
        
        if std_excess == 0:
            return 50.0
        
        sharpe = mean_excess / std_excess * np.sqrt(4)  # 年化 Sharpe
        
        # 將 Sharpe 轉換為 0~100 分（Sharpe 2.0 ≈ 100分）
        score = min(max(sharpe * 50, 0), 100)
        return round(score, 2)

    def calculate_fundamental_score(self, financial_metrics: Dict) -> float:
        """基本面綜合分數（來自 Phase 2）"""
        roic = financial_metrics.get("roic_proxy", 0)
        ocf_margin = financial_metrics.get("ocf_margin", 0)
        investing_intensity = financial_metrics.get("investing_intensity", 0)
        
        score = (roic * 0.5 + ocf_margin * 0.35 + investing_intensity * 0.15) * 100
        return round(min(max(score, 0), 100), 2)

    def calculate_final_fitness(
        self,
        price_fitness: float,
        returns_array: np.ndarray,
        financial_metrics: Dict
    ) -> float:
        """
        最終混合 Fitness
        """
        sharpe_score = self.calculate_sharpe_score(returns_array)
        fundamental_score = self.calculate_fundamental_score(financial_metrics)
        
        final_score = (
            price_fitness * self.price_weight +
            fundamental_score * self.fundamental_weight +
            sharpe_score * self.sharpe_weight
        )
        
        return round(min(max(final_score, 0), 100), 2)
```

### 4. 在交易員中的使用範例

```python
# 以 Momentum Trader 為例
class MomentumTrader:
    def __init__(self):
        self.fitness_calculator = FitnessCalculator(
            price_weight=0.50,      # 動能類給價格較高權重
            fundamental_weight=0.25,
            sharpe_weight=0.25
        )

    def calculate_fitness(self, performance_data: Dict, financial_metrics: Dict):
        # 原本的價格動能 Fitness
        price_fitness = self._calculate_price_fitness(performance_data)
        
        # 取得該交易員的季度報酬序列
        returns = np.array(performance_data.get("quarterly_returns", []))
        
        # 使用新的混合 Fitness
        final_fitness = self.fitness_calculator.calculate_final_fitness(
            price_fitness=price_fitness,
            returns_array=returns,
            financial_metrics=financial_metrics
        )
        
        return final_fitness
```

### 5. 不同交易員的權重建議

| 交易員類型                    | Price Weight | Fundamental Weight | Sharpe Weight | 說明 |
|-------------------------------|--------------|--------------------|---------------|------|
| **Momentum / Breakout**       | 0.50         | 0.25               | 0.25          | 仍以動能為主 |
| **Value & Quality**           | 0.35         | 0.40               | 0.25          | 提高基本面權重 |
| **Small Cap Catalyst Hunter** | 0.40         | 0.35               | 0.25          | 平衡風險與基本面 |
| **Low Volatility Trader**     | 0.30         | 0.35               | 0.35          | 強調風險調整 |
| **Statistical Arbitrage**     | 0.45         | 0.25               | 0.30          | 注重穩定性 |
| **Risk Officer**              | 0.25         | 0.30               | 0.45          | 最高風險調整權重 |

### 6. 實施建議

| 階段 | 建議做法 | 優先級 |
|------|----------|--------|
| **立即** | 在 `FitnessCalculator` 中加入 Sharpe 計算 | 高 |
| **短期** | 先套用到 3~4 個主要交易員（Value、Low Vol、Risk Officer、Small Cap） | 高 |
| **中期** | 調整不同交易員的權重組合 | 中 |
| **長期** | 加入 **Sortino Ratio** 或 **Calmar Ratio** 作為補充 | 低 |

---

**需要我現在幫你做什麼？**

請直接告訴我：

**1.** 把 `FitnessCalculator` 完整類別 + 各交易員的修改範例一次給你

**2.** 只先修改 **Value & Quality Compounders** 的 `calculate_fitness` 作為示範

**3.** 設計如何在每季演化中同時計算 **Sharpe + 基本面 + 價格動能** 的完整流程

請回覆數字，我會立刻產出對應內容。



