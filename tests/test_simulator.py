"""Unit tests for ope/simulator.py."""

import numpy as np
import pytest

from ope.simulator import (
    TRUE_INTERVENTIONAL_VALUE,
    simulate_dgp,
    target_policy,
)


def test_interventional_ground_truth_monte_carlo():
    """Validates the analytical interventional value against a 500,000-sample Monte Carlo run."""
    rng = np.random.default_rng(2026)
    n = 500_000
    x = rng.normal(0.0, 1.0, size=n)
    u = rng.normal(0.0, 1.0, size=n)
    eps = rng.normal(0.0, 0.3, size=n)
    a_target = (x > 0.0).astype(int)

    # Interventional structural equation:
    # R = 0.5 + 0.3X + A*(0.2 + 0.2X) + 0.4U + eps
    r_interventional = 0.5 + 0.3 * x + a_target * (0.2 + 0.2 * x) + 0.4 * u + eps
    mc_estimate = float(np.mean(r_interventional))

    # Analytical value: 0.5 + 0.1 + 0.2 * 0.398942 = 0.679788
    assert abs(mc_estimate - TRUE_INTERVENTIONAL_VALUE) < 0.003
    assert abs(TRUE_INTERVENTIONAL_VALUE - 0.679788) < 1e-5


def test_simulator_determinism():
    """Checks that identical seeds produce bitwise identical datasets."""
    ds1 = simulate_dgp(n=500, confounding=0.5, overlap=0.8, noise=0.2, seed=999)
    ds2 = simulate_dgp(n=500, confounding=0.5, overlap=0.8, noise=0.2, seed=999)

    np.testing.assert_array_equal(ds1.x, ds2.x)
    np.testing.assert_array_equal(ds1.u, ds2.u)
    np.testing.assert_array_equal(ds1.a, ds2.a)
    np.testing.assert_array_equal(ds1.r, ds2.r)
    np.testing.assert_array_equal(ds1.pi_e_action, ds2.pi_e_action)


def test_target_policy_threshold():
    """Checks that target policy treats if and only if x > 0."""
    x_test = np.array([-3.0, -0.001, 0.0, 0.001, 2.5])
    acts = target_policy(x_test)
    np.testing.assert_array_equal(acts, [0, 0, 0, 1, 1])


@pytest.mark.parametrize(
    ("n", "confounding", "overlap", "noise"),
    [
        (50, 0.5, 0.5, 0.2),  # n < 100
        (500, -0.1, 0.5, 0.2),  # confounding < 0
        (500, 1.1, 0.5, 0.2),  # confounding > 1
        (500, 0.5, 0.01, 0.2),  # overlap < 0.05
        (500, 0.5, 1.2, 0.2),  # overlap > 1
        (500, 0.5, 0.5, 0.0),  # noise <= 0
        (500, 0.5, 0.5, -0.5),  # noise < 0
    ],
)
def test_simulator_invalid_inputs(n: int, confounding: float, overlap: float, noise: float):
    """Validates that input constraint violations raise explicit ValueErrors."""
    with pytest.raises(ValueError):
        simulate_dgp(n=n, confounding=confounding, overlap=overlap, noise=noise)
