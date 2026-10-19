# OPE Lab: Empirical Abstract Facts & Quantitative Benchmarks

> **Notice**: All numbers in this document are generated directly from execution of
> `scripts/make_abstract_facts.py` using fixed random seeds. No values are hand-written.
> **Generated at**: `2026-10-19 17:10:36`
> **Ground Truth Interventional Target**: `V*(π_e) = 0.679788`

---

## 1. Primary Benchmark Performance Comparison (200 Seeds, n = 5,000)

### Setting 1: Ideal RCT (Confounding c = 0.0, Overlap α = 0.90, Noise σ = 0.30)
*Both key causal assumptions hold: zero unobserved confounding and strong common support.*

| Estimator | Mean Estimate V̂ | Bias vs V* | Abs Bias | Variance | Std Error | RMSE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Naive** | 0.9040 | +0.2243 | 0.2243 | 0.000488 | 0.0016 | **0.2253** |
| **Replay** | 0.6883 | +0.0085 | 0.0085 | 0.000274 | 0.0012 | **0.0186** |
| **Direct Method** | 0.6783 | -0.0014 | 0.0014 | 0.000200 | 0.0010 | **0.0142** |
| **IPW** | 0.6782 | -0.0016 | 0.0016 | 0.000239 | 0.0011 | **0.0155** |
| **SNIPW** | 0.6782 | -0.0016 | 0.0016 | 0.000249 | 0.0011 | **0.0158** |
| **Doubly Robust** | 0.6782 | -0.0016 | 0.0016 | 0.000247 | 0.0011 | **0.0158** |

### Setting 2: Confounder Trap (Confounding c = 0.80, Overlap α = 0.70, Noise σ = 0.30)
*Hidden factor U influences treatment selection and effect modification; unobserved by all estimators.*

| Estimator | Mean Estimate V̂ | Bias vs V* | Abs Bias | Variance | Std Error | RMSE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Naive** | 1.4032 | +0.7234 | 0.7234 | 0.000291 | 0.0012 | **0.7236** |
| **Replay** | 0.7874 | +0.1076 | 0.1076 | 0.000311 | 0.0012 | **0.1091** |
| **Direct Method** | 0.7871 | +0.1073 | 0.1073 | 0.000231 | 0.0011 | **0.1084** |
| **IPW** | 0.7818 | +0.1020 | 0.1020 | 0.000263 | 0.0011 | **0.1032** |
| **SNIPW** | 0.7838 | +0.1040 | 0.1040 | 0.000248 | 0.0011 | **0.1052** |
| **Doubly Robust** | 0.7838 | +0.1040 | 0.1040 | 0.000247 | 0.0011 | **0.1052** |

---

## 2. 95% Bootstrap Confidence Interval Coverage & Width (100 Seeds, B = 100)

| Setting | Estimator | Empirical 95% Coverage | Mean Interval Width | Std Width | Runtime |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Ideal RCT (c=0)** | IPW | **95.0%** | 0.0587 | 0.0055 | 16.3s |
| **Ideal RCT (c=0)** | SNIPW | **94.0%** | 0.0558 | 0.0050 | 16.3s |
| **Ideal RCT (c=0)** | Doubly Robust | **93.0%** | 0.0559 | 0.0053 | 16.3s |
| **Confounder Trap (c=0.8)** | IPW | **0.0%** | 0.0584 | 0.0054 | 17.4s |
| **Confounder Trap (c=0.8)** | SNIPW | **0.0%** | 0.0547 | 0.0053 | 17.4s |
| **Confounder Trap (c=0.8)** | Doubly Robust | **0.0%** | 0.0546 | 0.0053 | 17.4s |

> **Key Insight**: In the unconfounded regime, 95% bootstrap intervals achieve close to nominal
> coverage (93.0% for Doubly Robust). Under unobserved confounding,
> coverage collapses to **0.0%** because confidence intervals shrink
> around a biased point estimate.

---

## 3. 3×3 Estimator Decision Map Classification

Evaluated across 20 replications per cell (n = 5,000, noise σ = 0.30).
Winner is chosen by lowest RMSE among eligible OPE methods (Naive excluded).
Cells where top two RMSEs are within 10% are marked **Tie**.
Cells where the winner's absolute bias exceeds 0.05 are marked **No method reliable**.

| Overlap α \ Confounding c | c = 0.0 (Unconfounded) | c = 0.5 (Moderate) | c = 1.0 (Severe) |
| :--- | :---: | :---: | :---: |
| **α = 0.9** | **Tie**<br>RMSE: 0.0106 | **No method reliable**<br>RMSE: 0.0959 | **No method reliable**<br>RMSE: 0.1457 |
| **α = 0.5** | **Tie**<br>RMSE: 0.0119 | **No method reliable**<br>RMSE: 0.0621 | **No method reliable**<br>RMSE: 0.0908 |
| **α = 0.2** | **Direct Method**<br>RMSE: 0.0113 | **Tie**<br>RMSE: 0.0415 | **No method reliable**<br>RMSE: 0.0706 |

### Detailed Decision Grid Cell Breakdown:

| Cell (c, α) | Classification | Winner | Runner-Up | Winner RMSE | Runner-Up RMSE | Winner Abs Bias | Median ESS |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| (c=0.0, α=0.2) | **Direct Method** | Direct Method | Doubly Robust | 0.0113 | 0.0129 | 0.0030 | 4,279 |
| (c=0.0, α=0.5) | **Tie** | Doubly Robust | SNIPW | 0.0119 | 0.0120 | 0.0006 | 4,025 |
| (c=0.0, α=0.9) | **Tie** | Direct Method | SNIPW | 0.0106 | 0.0112 | 0.0019 | 3,279 |
| (c=0.5, α=0.2) | **Tie** | IPW | SNIPW | 0.0415 | 0.0422 | 0.0402 | 4,092 |
| (c=0.5, α=0.5) | **No method reliable** | IPW | Doubly Robust | 0.0621 | 0.0651 | 0.0606 | 3,806 |
| (c=0.5, α=0.9) | **No method reliable** | IPW | Doubly Robust | 0.0959 | 0.0963 | 0.0949 | 3,095 |
| (c=1.0, α=0.2) | **No method reliable** | IPW | Doubly Robust | 0.0706 | 0.0747 | 0.0690 | 3,794 |
| (c=1.0, α=0.5) | **No method reliable** | IPW | SNIPW | 0.0908 | 0.0942 | 0.0899 | 3,494 |
| (c=1.0, α=0.9) | **No method reliable** | Direct Method | SNIPW | 0.1457 | 0.1459 | 0.1450 | 2,931 |

---

## 4. Confounding Sensitivity Breakdown Thresholds

Minimum confounding strength $c$ where each estimator's absolute bias first exceeds the 0.05 tolerance:

| Estimator | Confounding Threshold (Bias > 0.05) | Status at c = 1.0 |
| :--- | :---: | :--- |
| **Naive** | **c = 0.00** | Unreliable (Broken by Confounder) |
| **Replay** | **c = 0.20** | Unreliable (Broken by Confounder) |
| **Direct Method** | **c = 0.30** | Unreliable (Broken by Confounder) |
| **IPW** | **c = 0.30** | Unreliable (Broken by Confounder) |
| **SNIPW** | **c = 0.30** | Unreliable (Broken by Confounder) |
| **Doubly Robust** | **c = 0.30** | Unreliable (Broken by Confounder) |

---

## 5. Overlap Breakdown Threshold (IPW vs. Doubly Robust)

- **Overlap threshold where IPW RMSE > 2× DR RMSE**: **None** (ratio never exceeds 2.0×; maximum observed ratio was `1.14×`).
- **Mathematical explanation**: In this data-generating process, logging probability logit is proportional to $L \cdot X$. As overlap decreases (higher $L$), logging behavior concentrates actions along the same threshold decision boundary as the target policy $\pi_e(X) = \mathbb{I}(X > 0)$, stabilizing density ratios on concordant treatment selections.

---

## 6. Reproducibility Metadata

- **Python Version**: `3.11.9`
- **Random Seed Protocol**: Base seeds = 42, 1000, 4242, 5000, 7000, 9000, 12000
- **Sample Size**: $n = 5,000$ per simulation replication
- **Target Policy Ground Truth**: $V^*(\pi_e) = 0.679788$
- **Executed by**: `scripts/make_abstract_facts.py` on 2026-10-19 17:10:36
