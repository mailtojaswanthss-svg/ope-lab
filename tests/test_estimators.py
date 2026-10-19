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
    """Validates that with c=0 and overlap 0.9, IPW, SNIPW, and DR are close to 0.6798

    on average over multiple seeds, while Naive is clearly biased.
    """
    dr_vals = []
    ipw_vals = []
    snipw_vals = []
    naive_vals = []

    for seed in range(15):
        ds = simulate_dgp(
            n=6000,
            confounding=0.0,
            overlap=0.9,
            noise=0.2,
            seed=seed + 500,
        )
        summary = evaluate_all_estimators(ds)
        dr_vals.append(summary.get("Doubly Robust").value)
        ipw_vals.append(summary.get("IPW").value)
        snipw_vals.append(summary.get("SNIPW").value)
        naive_vals.append(summary.get("Naive").value)

    v_star = ds.true_interventional_value
    avg_dr = float(np.mean(dr_vals))
    avg_ipw = float(np.mean(ipw_vals))
    avg_snipw = float(np.mean(snipw_vals))
    avg_naive = float(np.mean(naive_vals))

    # OPE estimators are close to 0.6798 (within 0.015)
    assert abs(avg_dr - v_star) < 0.015
    assert abs(avg_ipw - v_star) < 0.020
    assert abs(avg_snipw - v_star) < 0.020

    # Naive is clearly biased (error > 0.05)
    assert abs(avg_naive - v_star) > 0.05


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
