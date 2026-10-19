"""Computes Step 2 benchmark metrics over 200 seeds in two settings.

Produces Mean Estimate, Bias, and RMSE for all 6 estimators, plus a confounding sensitivity check.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from ope.estimators import evaluate_all_estimators
from ope.simulator import TRUE_INTERVENTIONAL_VALUE, simulate_dgp


def run_benchmark(n_seeds: int = 200, n: int = 5000):
    settings = [
        {"name": "Setting 1: Unconfounded (c=0.0, overlap=0.9)", "c": 0.0, "overlap": 0.9},
        {"name": "Setting 2: Confounded (c=0.8, overlap=0.7)", "c": 0.8, "overlap": 0.7},
    ]

    estimators = ["Naive", "Replay", "Direct Method", "IPW", "SNIPW", "Doubly Robust"]
    v_star = TRUE_INTERVENTIONAL_VALUE

    for setting in settings:
        print(f"\n### {setting['name']} (N={n}, {n_seeds} seeds)")
        print(f"Ground Truth V*: {v_star:.6f}")
        print("| Estimator | Mean Estimate | Bias | RMSE |")
        print("| :--- | :---: | :---: | :---: |")

        vals = {name: [] for name in estimators}

        for seed in range(n_seeds):
            ds = simulate_dgp(
                n=n,
                confounding=setting["c"],
                overlap=setting["overlap"],
                noise=0.3,
                seed=seed + 1000,
            )
            summary = evaluate_all_estimators(ds)
            for name in estimators:
                vals[name].append(summary.get(name).value)

        for name in estimators:
            arr = np.array(vals[name])
            mean_val = float(np.mean(arr))
            bias = mean_val - v_star
            rmse = float(np.sqrt(np.mean((arr - v_star) ** 2)))
            print(f"| {name} | {mean_val:.4f} | {bias:+.4f} | {rmse:.4f} |")

    # Also evaluate IPW bias across confounding levels
    print("\n### Confounding Sensitivity Progression (Overlap=0.8, 100 seeds each)")
    print("| Confounding c | IPW Bias | SNIPW Bias | DM Bias | DR Bias | Naive Bias |")
    print("| :---: | :---: | :---: | :---: | :---: | :---: |")
    for c_level in [0.0, 0.3, 0.6, 0.9]:
        ipw_b, snipw_b, dm_b, dr_b, naive_b = [], [], [], [], []
        for s in range(100):
            ds = simulate_dgp(n=5000, confounding=c_level, overlap=0.8, noise=0.3, seed=s + 2000)
            res = evaluate_all_estimators(ds)
            ipw_b.append(res.get("IPW").value - v_star)
            snipw_b.append(res.get("SNIPW").value - v_star)
            dm_b.append(res.get("Direct Method").value - v_star)
            dr_b.append(res.get("Doubly Robust").value - v_star)
            naive_b.append(res.get("Naive").value - v_star)
        print(
            f"| {c_level:.1f} | {np.mean(ipw_b):+.4f} | {np.mean(snipw_b):+.4f} | "
            f"{np.mean(dm_b):+.4f} | {np.mean(dr_b):+.4f} | {np.mean(naive_b):+.4f} |"
        )


if __name__ == "__main__":
    run_benchmark(n_seeds=200, n=5000)
