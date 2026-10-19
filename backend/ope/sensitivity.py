"""Confounding sensitivity bounds for Off-Policy Evaluation.

Implements a basic approximation of the marginal sensitivity model (MSM)
on self-normalized importance weighting (SNIPW) over matched rows.

Under the marginal sensitivity model, an unobserved confounder can alter
the odds of treatment selection by at most a factor of Lambda >= 1.0:
    1 / Lambda <= w_i^* / w_i <= Lambda

The worst-case lower and upper bounds on policy value are computed via an
O(n log n) sorted-reward threshold sweep over prefix sums.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ope.estimators import fast_logistic_propensity
from ope.logging_config import logger
from ope.simulator import TRUE_INTERVENTIONAL_VALUE, Dataset


@dataclass(frozen=True)
class SensitivityResult:
    """Quantitative results from marginal sensitivity analysis."""

    lambdas: np.ndarray
    lower_bounds: np.ndarray
    upper_bounds: np.ndarray
    point_estimate: float
    lambda_star: float | None
    covers_at_one: bool
    method_label: str = "Basic approximation of the marginal sensitivity model"

    @property
    def max_lambda(self) -> float:
        return float(self.lambdas[-1]) if len(self.lambdas) > 0 else 1.0


def compute_sensitivity_bounds(
    dataset: Dataset,
    lambdas: np.ndarray | None = None,
    true_target: float = TRUE_INTERVENTIONAL_VALUE,
) -> SensitivityResult:
    """Computes worst-case lower and upper bounds on policy value under hidden confounding.

    Args:
        dataset: The observed interaction log (context X, action A, reward R).
        lambdas: 1D array of odds ratios Lambda >= 1.0. Defaults to 40 points in [1.0, 3.0].
        true_target: Interventional target value V*(pi_e). Defaults to TRUE_INTERVENTIONAL_VALUE (0.679788).

    Returns:
        SensitivityResult containing odds ratios, bounds, point estimate, and lambda_star.
    """
    if lambdas is None:
        lambdas = np.linspace(1.0, 3.0, 41)
    else:
        lambdas = np.asarray(lambdas, dtype=float)

    if np.any(lambdas < 1.0):
        raise ValueError("All Lambda values must be >= 1.0.")

    # 1. Fit propensity model e_hat(X) on observed data (never observing hidden U)
    p_hat = fast_logistic_propensity(dataset.x, dataset.a)

    # 2. Identify matched rows where logged action matches target policy pi_e(X) = 1[X > 0]
    matched_mask = dataset.a == dataset.pi_e_action
    matched_rewards = dataset.r[matched_mask]
    matched_actions = dataset.a[matched_mask]
    matched_p = p_hat[matched_mask]

    # Importance weights: w_i = 1 / p_hat(A_i | X_i)
    propensities = np.where(matched_actions == 1, matched_p, 1.0 - matched_p)
    weights = 1.0 / np.clip(propensities, 0.01, 0.99)

    m = len(matched_rewards)
    if m == 0:
        logger.warning("No matched actions found between logging policy and target policy.")
        zeros = np.zeros_like(lambdas)
        return SensitivityResult(
            lambdas=lambdas,
            lower_bounds=zeros,
            upper_bounds=zeros,
            point_estimate=0.0,
            lambda_star=None,
            covers_at_one=False,
        )

    # Baseline SNIPW point estimate at Lambda = 1.0
    tot_w = float(np.sum(weights))
    point_estimate = float(np.sum(weights * matched_rewards) / tot_w) if tot_w > 0 else 0.0

    # 3. Sort matched rows by ascending reward
    sort_idx = np.argsort(matched_rewards)
    r_sorted = matched_rewards[sort_idx]
    w_sorted = weights[sort_idx]

    # 4. Compute prefix sums over sorted weights and weighted rewards
    # W[k] = sum_{i=0}^{k-1} w_i, WR[k] = sum_{i=0}^{k-1} w_i * r_i
    W = np.zeros(m + 1, dtype=float)
    WR = np.zeros(m + 1, dtype=float)
    np.cumsum(w_sorted, out=W[1:])
    np.cumsum(w_sorted * r_sorted, out=WR[1:])

    tot_W = W[-1]
    tot_WR = WR[-1]

    lower_bounds = np.zeros(len(lambdas), dtype=float)
    upper_bounds = np.zeros(len(lambdas), dtype=float)

    # 5. Threshold sweep for each Lambda
    # Low-reward block [0, k) has weight W[k] and sum WR[k]
    # High-reward block [k, m) has weight tot_W - W[k] and sum tot_WR - WR[k]
    low_W = W
    low_WR = WR
    high_W = tot_W - low_W
    high_WR = tot_WR - low_WR

    for idx, lam in enumerate(lambdas):
        if np.isclose(lam, 1.0):
            lower_bounds[idx] = point_estimate
            upper_bounds[idx] = point_estimate
            continue

        up = lam
        dn = 1.0 / lam

        # For upper bound: downweight low rewards (dn), upweight high rewards (up)
        upper_vals = (dn * low_WR + up * high_WR) / (dn * low_W + up * high_W)
        upper_bounds[idx] = float(np.max(upper_vals))

        # For lower bound: upweight low rewards (up), downweight high rewards (dn)
        lower_vals = (up * low_WR + dn * high_WR) / (up * low_W + dn * high_W)
        lower_bounds[idx] = float(np.min(lower_vals))

    # 6. Find smallest Lambda where [lower_bound, upper_bound] covers true_target
    covers_mask = (lower_bounds <= true_target) & (true_target <= upper_bounds)
    covers_at_one = bool(covers_mask[0])

    lambda_star: float | None = None
    if np.any(covers_mask):
        first_cover_idx = int(np.argmax(covers_mask))
        lambda_star = float(lambdas[first_cover_idx])

    logger.info(
        f"Sensitivity analysis completed: point_est={point_estimate:.4f}, "
        f"lambda_star={lambda_star}, covers_at_one={covers_at_one}"
    )

    return SensitivityResult(
        lambdas=lambdas,
        lower_bounds=lower_bounds,
        upper_bounds=upper_bounds,
        point_estimate=point_estimate,
        lambda_star=lambda_star,
        covers_at_one=covers_at_one,
    )
