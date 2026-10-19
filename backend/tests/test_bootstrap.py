"""Unit tests for ope/bootstrap.py."""

import numpy as np

from ope.bootstrap import get_adaptive_bootstrap_b, run_bootstrap_ci
from ope.simulator import TRUE_INTERVENTIONAL_VALUE, simulate_dgp


def test_adaptive_bootstrap_b():
    """Checks that B adapts downwards when n > 10,000."""
    assert get_adaptive_bootstrap_b(n=5000, requested_b=100) == 100
    assert get_adaptive_bootstrap_b(n=15000, requested_b=100) == 40
    assert get_adaptive_bootstrap_b(n=15000, requested_b=30) == 30


def test_bootstrap_ci_properties():
    """Checks that interval width > 0 and point estimate lies inside or near its interval."""
    ds = simulate_dgp(n=2000, confounding=0.0, overlap=0.8, noise=0.3, seed=123)
    boot = run_bootstrap_ci(ds, b=50, seed=123)

    assert boot.b_iterations == 50
    assert boot.elapsed_sec > 0.0

    for res in boot.results.values():
        assert res.ci_width > 0.0
        assert res.ci_lower < res.ci_upper
        assert res.std_err > 0.0
        # Point estimate lies within the span of bootstrap samples
        min_samp = float(np.min(res.boot_samples))
        max_samp = float(np.max(res.boot_samples))
        assert min_samp <= res.point_estimate <= max_samp


def test_bootstrap_coverage_unconfounded():
    """Coverage check: Over 100 seeds in the unconfounded setting (c=0, overlap=0.9),

    the 95% interval of IPW and DR should contain the true value roughly 85-99% of the time.
    """
    n_seeds = 100
    v_star = TRUE_INTERVENTIONAL_VALUE
    ipw_covered = 0
    dr_covered = 0

    for s in range(n_seeds):
        ds = simulate_dgp(n=3000, confounding=0.0, overlap=0.9, noise=0.3, seed=s + 7000)
        # Use B=40 for speed in the multi-seed coverage check
        boot = run_bootstrap_ci(ds, b=40, seed=s + 7000)

        ipw_res = boot.get("IPW")
        if ipw_res.ci_lower <= v_star <= ipw_res.ci_upper:
            ipw_covered += 1

        dr_res = boot.get("Doubly Robust")
        if dr_res.ci_lower <= v_star <= dr_res.ci_upper:
            dr_covered += 1

    ipw_cov_rate = ipw_covered / n_seeds
    dr_cov_rate = dr_covered / n_seeds

    # Print empirical coverage for test log reporting
    print(f"\nEmpirical 95% CI Coverage over {n_seeds} seeds: IPW={ipw_cov_rate:.1%}, DR={dr_cov_rate:.1%}")

    # Coverage should be roughly 85% to 99%
    assert 0.85 <= ipw_cov_rate <= 0.99, f"IPW coverage {ipw_cov_rate:.1%} outside [85%, 99%]"
    assert 0.85 <= dr_cov_rate <= 0.99, f"DR coverage {dr_cov_rate:.1%} outside [85%, 99%]"
