"""Unit tests for confounding sensitivity bounds and marginal sensitivity model."""

from __future__ import annotations

import numpy as np
import pytest

from ope.sensitivity import compute_sensitivity_bounds
from ope.simulator import TRUE_INTERVENTIONAL_VALUE, simulate_dgp


def test_sensitivity_at_lambda_one():
    """At Lambda = 1.0, lower bound and upper bound must equal the SNIPW point estimate."""
    dataset = simulate_dgp(n=2000, confounding=0.0, overlap=0.8, seed=42)
    lambdas = np.array([1.0, 1.5, 2.0, 2.5, 3.0])
    res = compute_sensitivity_bounds(dataset, lambdas=lambdas)

    assert np.isclose(res.lower_bounds[0], res.point_estimate, atol=1e-6)
    assert np.isclose(res.upper_bounds[0], res.point_estimate, atol=1e-6)


def test_sensitivity_monotonicity():
    """Upper bound should be non-decreasing, lower bound non-increasing with Lambda."""
    dataset = simulate_dgp(n=2000, confounding=0.5, overlap=0.7, seed=123)
    lambdas = np.linspace(1.0, 3.0, 21)
    res = compute_sensitivity_bounds(dataset, lambdas=lambdas)

    # Upper bounds increase or stay same
    assert np.all(np.diff(res.upper_bounds) >= -1e-8)
    # Lower bounds decrease or stay same
    assert np.all(np.diff(res.lower_bounds) <= 1e-8)
    # Lower <= Upper everywhere
    assert np.all(res.lower_bounds <= res.upper_bounds + 1e-8)


def test_sensitivity_unconfounded_coverage():
    """In unconfounded setting (c = 0), bounds should cover V* at or near Lambda = 1."""
    dataset = simulate_dgp(n=5000, confounding=0.0, overlap=0.9, seed=42)
    res = compute_sensitivity_bounds(dataset)

    assert res.lambda_star is not None
    # For c=0, point estimate is very close to 0.6798, so lambda_star is 1.0 or very close
    assert res.lambda_star <= 1.1


def test_sensitivity_confounded_expansion():
    """Under confounding (c = 0.8), point estimate is biased high, so lambda_star > 1.0."""
    dataset = simulate_dgp(n=5000, confounding=0.8, overlap=0.7, seed=42)
    res = compute_sensitivity_bounds(dataset)

    # Point estimate is inflated above V* = 0.6798
    assert res.point_estimate > TRUE_INTERVENTIONAL_VALUE
    # Bounds must expand to eventually cover V*
    assert res.lambda_star is not None
    assert res.lambda_star > 1.0
    # At lambda_star, lower bound <= V* <= upper bound
    idx = int(np.where(np.isclose(res.lambdas, res.lambda_star))[0][0])
    assert res.lower_bounds[idx] <= TRUE_INTERVENTIONAL_VALUE <= res.upper_bounds[idx]


def test_sensitivity_invalid_lambda():
    """Passing Lambda < 1.0 must raise ValueError."""
    dataset = simulate_dgp(n=500, confounding=0.0, overlap=0.5, seed=42)
    with pytest.raises(ValueError, match="All Lambda values must be >= 1.0"):
        compute_sensitivity_bounds(dataset, lambdas=np.array([0.8, 1.0, 1.5]))
