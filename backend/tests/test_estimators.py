"""Unit tests for ope/estimators.py."""

import numpy as np

from ope.estimators import (
    effective_sample_size,
    estimate_direct_method,
    estimate_doubly_robust,
    estimate_ipw,
    estimate_naive,
    estimate_replay,
    estimate_snipw,
    evaluate_all_estimators,
    fast_logistic_propensity,
)
from ope.simulator import simulate_dgp


def test_fast_propensity_bounds():
    """Checks that estimated propensities obey [0.01, 0.99] bounds."""
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, size=3000)
    a = (rng.uniform(size=3000) < 0.6).astype(int)

    props = fast_logistic_propensity(x, a, clip_min=0.01, clip_max=0.99)
    assert np.all(props >= 0.01)
    assert np.all(props <= 0.99)


def test_estimators_unbiased_without_confounding():
    """Validates that with c=0 and overlap 0.9, IPW, SNIPW, DR, and DM are close to 0.6798

    on average over multiple seeds, while Naive is clearly biased.
    """
    dr_vals, ipw_vals, snipw_vals, dm_vals, naive_vals = [], [], [], [], []

    for seed in range(20):
        ds = simulate_dgp(
            n=5000,
            confounding=0.0,
            overlap=0.9,
            noise=0.3,
            seed=seed + 500,
        )
        summary = evaluate_all_estimators(ds)
        dr_vals.append(summary.get("Doubly Robust").value)
        ipw_vals.append(summary.get("IPW").value)
        snipw_vals.append(summary.get("SNIPW").value)
        dm_vals.append(summary.get("Direct Method").value)
        naive_vals.append(summary.get("Naive").value)

    v_star = ds.true_interventional_value
    avg_dr = float(np.mean(dr_vals))
    avg_ipw = float(np.mean(ipw_vals))
    avg_snipw = float(np.mean(snipw_vals))
    avg_dm = float(np.mean(dm_vals))
    avg_naive = float(np.mean(naive_vals))

    # OPE estimators are close to true interventional value (within 0.015)
    assert abs(avg_dr - v_star) < 0.015
    assert abs(avg_ipw - v_star) < 0.015
    assert abs(avg_snipw - v_star) < 0.015
    assert abs(avg_dm - v_star) < 0.015

    # Naive is clearly biased (error > 0.15)
    assert abs(avg_naive - v_star) > 0.15


def test_bias_amplification_under_hidden_confounding():
    """Validates that at confounding 0.8 and overlap 0.7, the average bias of

    IPW, SNIPW, DR, and DM is at least 5 times larger in absolute value
    than at confounding 0.
    """
    n_seeds = 30
    v_star = 0.679788

    # Setting 1: c=0.0, overlap=0.9
    bias_c0 = {"IPW": [], "SNIPW": [], "Direct Method": [], "Doubly Robust": []}
    for s in range(n_seeds):
        ds0 = simulate_dgp(n=5000, confounding=0.0, overlap=0.9, noise=0.3, seed=s + 100)
        res0 = evaluate_all_estimators(ds0)
        for k, val_list in bias_c0.items():
            val_list.append(res0.get(k).value - v_star)

    # Setting 2: c=0.8, overlap=0.7
    bias_c8 = {"IPW": [], "SNIPW": [], "Direct Method": [], "Doubly Robust": []}
    for s in range(n_seeds):
        ds8 = simulate_dgp(n=5000, confounding=0.8, overlap=0.7, noise=0.3, seed=s + 500)
        res8 = evaluate_all_estimators(ds8)
        for k, val_list in bias_c8.items():
            val_list.append(res8.get(k).value - v_star)

    for est in ["IPW", "SNIPW", "Direct Method", "Doubly Robust"]:
        mean_bias_c0 = float(np.mean(bias_c0[est]))
        mean_bias_c8 = float(np.mean(bias_c8[est]))
        abs_c0 = max(abs(mean_bias_c0), 1e-4)
        abs_c8 = abs(mean_bias_c8)

        # Assert bias under c=0.8 is at least 5x larger than at c=0
        ratio = abs_c8 / abs_c0
        assert ratio >= 5.0, (
            f"{est}: bias at c=0.8 ({mean_bias_c8:+.4f}) not >= 5x larger than at c=0 ({mean_bias_c0:+.4f})"
        )


def test_ipw_bias_monotonically_increases_with_confounding():
    """Validates that the mean absolute bias of IPW is non-decreasing across

    confounding levels 0.0, 0.3, 0.6, 0.9.
    """
    v_star = 0.679788
    c_levels = [0.0, 0.3, 0.6, 0.9]
    abs_biases = []

    for c in c_levels:
        seed_biases = []
        for s in range(35):
            ds = simulate_dgp(n=5000, confounding=c, overlap=0.8, noise=0.3, seed=s + 3000)
            res = evaluate_all_estimators(ds)
            seed_biases.append(res.get("IPW").value - v_star)
        abs_biases.append(abs(float(np.mean(seed_biases))))

    # Verify non-decreasing sequence (with small numerical tolerance)
    for i in range(len(abs_biases) - 1):
        assert abs_biases[i] <= abs_biases[i + 1] + 1e-4, (
            f"IPW bias decreased from c={c_levels[i]} ({abs_biases[i]:.4f}) to c={c_levels[i+1]} ({abs_biases[i+1]:.4f})"
        )


def test_weight_diagnostics_properties():
    """Checks that ESS > 0 and max weight >= 1."""
    ds = simulate_dgp(n=1000, confounding=0.5, overlap=0.2, noise=0.3, seed=888)
    summary = evaluate_all_estimators(ds)

    assert summary.max_weight >= 1.0
    assert summary.ess > 0
    assert summary.ess <= ds.n
    assert 0.0 < summary.ess_ratio <= 1.0


def test_empty_data_handling():
    """Checks that estimators handle empty arrays without unhandled exceptions."""
    empty_arr = np.array([], dtype=float)
    empty_int = np.array([], dtype=int)

    assert estimate_naive(empty_int, empty_arr) == 0.0
    assert estimate_replay(empty_int, empty_arr, empty_int) == 0.0
    assert estimate_direct_method(empty_arr) == 0.0
    assert estimate_ipw(empty_arr, empty_arr) == 0.0
    assert estimate_snipw(empty_arr, empty_arr) == 0.0
    assert estimate_doubly_robust(empty_arr, empty_arr, empty_arr, empty_arr) == 0.0
    assert effective_sample_size(empty_arr) == 0.0
