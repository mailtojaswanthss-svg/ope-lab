"""Vectorized adaptive percentile bootstrap for confidence intervals in OPE Lab.

Computes 95% confidence intervals and standard errors for all 6 estimators:
Naive, Replay, Direct Method, IPW, Self-Normalized IPW, and Doubly Robust.
Each resample re-fits the propensity and reward models. Automatically lowers
iterations when n > 10,000 for sub-second UI responsiveness.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from ope.estimators import (
    compute_importance_weights,
    estimate_direct_method,
    estimate_doubly_robust,
    estimate_ipw,
    estimate_naive,
    estimate_replay,
    estimate_snipw,
    fast_logistic_propensity,
    fit_reward_model,
)
from ope.logging_config import logger
from ope.simulator import Dataset


@dataclass(frozen=True)
class BootstrapResult:
    """Confidence interval and dispersion metrics for an individual estimator."""

    name: str
    point_estimate: float
    ci_lower: float
    ci_upper: float
    std_err: float
    boot_samples: np.ndarray

    @property
    def ci_width(self) -> float:
        """Width of 95% confidence interval."""
        return self.ci_upper - self.ci_lower


@dataclass(frozen=True)
class BootstrapSummary:
    """Summary of bootstrap uncertainty for all estimators."""

    results: dict[str, BootstrapResult]
    b_iterations: int
    elapsed_sec: float

    def get(self, name: str) -> BootstrapResult:
        """Retrieves bootstrap result by estimator name."""
        return self.results[name]


def get_adaptive_bootstrap_b(n: int, requested_b: int = 100) -> int:
    """Lowers default bootstrap iterations when sample size is very large (n > 10,000)

    to preserve instantaneous UI responsiveness while preserving asymptotic coverage.
    """
    if n > 10_000:
        return min(requested_b, 40)
    return requested_b


def run_bootstrap_ci(
    dataset: Dataset,
    b: int = 100,
    seed: int | None = None,
    progress_callback: Callable[[float, str], None] | None = None,
) -> BootstrapSummary:
    """Performs non-parametric percentile bootstrap across all 6 estimators.

    Each resample independently draws indices with replacement, re-fits
    the fast pure-NumPy propensity model and outcome regression, and records
    all estimator values.

    Args:
        dataset: Logged dataset.
        b: Number of bootstrap iterations (adaptive when n > 10,000).
        seed: Random seed for reproducible resamples.
        progress_callback: Optional callback receiving (fraction, status_text).

    Returns:
        BootstrapSummary containing point estimates, 95% CIs, and std errors.

    Raises:
        ValueError: If b < 10 or dataset is empty.
    """
    if b < 10:
        raise ValueError(f"Bootstrap iterations B must be >= 10, got {b}")
    if dataset.n < 10:
        raise ValueError(f"Dataset sample size must be >= 10, got {dataset.n}")

    start_time = time.perf_counter()
    n = dataset.n
    b_effective = get_adaptive_bootstrap_b(n, requested_b=b)

    rng = np.random.default_rng(seed)

    estimator_names = [
        "Naive",
        "Replay",
        "Direct Method",
        "IPW",
        "SNIPW",
        "Doubly Robust",
    ]

    boot_records: dict[str, list[float]] = {name: [] for name in estimator_names}

    # Extract base arrays
    x = dataset.x
    a = dataset.a
    r = dataset.r
    pi_e_action = dataset.pi_e_action

    # Compute point estimates on full dataset
    p_full = fast_logistic_propensity(x, a)
    w_full, _ = compute_importance_weights(a, pi_e_action, p_full)
    r_hat_pi_e_full, r_hat_a_full = fit_reward_model(x, a, r, pi_e_action)

    point_estimates = {
        "Naive": estimate_naive(a, r),
        "Replay": estimate_replay(a, r, pi_e_action),
        "Direct Method": estimate_direct_method(r_hat_pi_e_full),
        "IPW": estimate_ipw(w_full, r),
        "SNIPW": estimate_snipw(w_full, r),
        "Doubly Robust": estimate_doubly_robust(
            w_full, r, r_hat_pi_e_full, r_hat_a_full
        ),
    }

    # Resample loop
    for iter_idx in range(b_effective):
        idx = rng.integers(0, n, size=n)
        x_b = x[idx]
        a_b = a[idx]
        r_b = r[idx]
        pi_e_b = pi_e_action[idx]

        p_b = fast_logistic_propensity(x_b, a_b)
        w_b, _ = compute_importance_weights(a_b, pi_e_b, p_b)
        r_hat_pi_e_b, r_hat_a_b = fit_reward_model(x_b, a_b, r_b, pi_e_b)

        boot_records["Naive"].append(estimate_naive(a_b, r_b))
        boot_records["Replay"].append(estimate_replay(a_b, r_b, pi_e_b))
        boot_records["Direct Method"].append(estimate_direct_method(r_hat_pi_e_b))
        boot_records["IPW"].append(estimate_ipw(w_b, r_b))
        boot_records["SNIPW"].append(estimate_snipw(w_b, r_b))
        boot_records["Doubly Robust"].append(
            estimate_doubly_robust(w_b, r_b, r_hat_pi_e_b, r_hat_a_b)
        )

        if progress_callback is not None and (iter_idx + 1) % 10 == 0:
            frac = (iter_idx + 1) / b_effective
            progress_callback(frac, f"Bootstrap resample {iter_idx + 1}/{b_effective}...")

    results: dict[str, BootstrapResult] = {}
    for name in estimator_names:
        arr = np.array(boot_records[name], dtype=float)
        ci_lower = float(np.percentile(arr, 2.5))
        ci_upper = float(np.percentile(arr, 97.5))
        std_err = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0

        results[name] = BootstrapResult(
            name=name,
            point_estimate=point_estimates[name],
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            std_err=std_err,
            boot_samples=arr,
        )

    elapsed = time.perf_counter() - start_time
    logger.debug(
        "Completed bootstrap CI: B=%d (requested=%d), n=%d in %.3f s",
        b_effective,
        b,
        n,
        elapsed,
    )

    return BootstrapSummary(
        results=results,
        b_iterations=b_effective,
        elapsed_sec=elapsed,
    )
