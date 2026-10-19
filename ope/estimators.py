"""Off-Policy Estimators, fast propensity modeling, and diagnostics for OPE Lab.

Implements:
1. Fast pure-NumPy Newton-Raphson logistic regression propensity model (clipped to [0.01, 0.99]).
2. 6 Estimators: Naive, Replay, Direct Method, IPW, Self-Normalized IPW, and Doubly Robust.
3. Weight diagnostics: Kish's Effective Sample Size (ESS) and maximum importance weight.
Estimators never observe the hidden confounder u.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ope.logging_config import logger
from ope.simulator import Dataset


@dataclass(frozen=True)
class EstimatorResult:
    """Output metrics for a single off-policy estimator."""

    name: str
    value: float
    error: float  # Absolute error |value - V*|
    signed_error: float  # Signed error (value - V*)


@dataclass(frozen=True)
class EvaluationSummary:
    """Consolidated evaluation summary across all estimators and diagnostics."""

    results: dict[str, EstimatorResult]
    max_weight: float
    ess: float
    ess_ratio: float  # ESS / n
    true_value: float
    best_estimator: str  # Best among valid OPE methods (excluding Naive)
    weights: np.ndarray = field(default_factory=lambda: np.array([], dtype=float))

    def get(self, name: str) -> EstimatorResult:
        """Retrieves an individual estimator result by name."""
        return self.results[name]


# Aliases for convenience
EstimatorSummary = EvaluationSummary
compute_all_estimators = None  # Defined below after evaluate_all_estimators


def fast_logistic_propensity(
    x: np.ndarray,
    a: np.ndarray,
    clip_min: float = 0.01,
    clip_max: float = 0.99,
    max_iter: int = 10,
    tol: float = 1e-6,
) -> np.ndarray:
    """Fits 1D logistic regression P(A=1 | X) using Newton-Raphson in pure NumPy.

    Learns parameters theta = [theta_0, theta_1] for P(A=1|X) = sigmoid(theta_0 + theta_1 * X)
    in 4-5 iterations (< 0.2 ms for n=10,000). Never sees the hidden confounder u.

    Args:
        x: Observed context array of shape (n,).
        a: Logged binary action array of shape (n,).
        clip_min: Minimum propensity bound.
        clip_max: Maximum propensity bound.
        max_iter: Maximum optimization iterations.
        tol: Parameter update convergence tolerance.

    Returns:
        Estimated propensities P(A=1 | X), clipped to [clip_min, clip_max].
    """
    n = len(x)
    if n == 0:
        return np.array([], dtype=float)

    mean_a = float(np.mean(a))
    # Degenerate case: only one action class observed
    if mean_a <= 0.0 or mean_a >= 1.0:
        val = np.clip(mean_a, clip_min, clip_max)
        return np.full(n, val, dtype=float)

    # Design matrix: [1, x]
    X_mat = np.column_stack((np.ones(n, dtype=float), x.astype(float)))
    theta = np.zeros(2, dtype=float)
    l2_reg = 1e-4

    for _ in range(max_iter):
        z = X_mat @ theta
        z_clipped = np.clip(z, -30.0, 30.0)
        p = 1.0 / (1.0 + np.exp(-z_clipped))
        w = p * (1.0 - p) + 1e-8

        # Gradient: X^T (a - p) - l2_reg * theta
        grad = X_mat.T @ (a - p) - l2_reg * theta

        # Hessian: -X^T diag(w) X - l2_reg * I
        X_w = X_mat * w[:, np.newaxis]
        hess = -(X_mat.T @ X_w) - l2_reg * np.eye(2)

        try:
            delta = np.linalg.solve(hess, -grad)
        except np.linalg.LinAlgError:
            delta = -grad / (np.sum(w) + l2_reg)

        theta += delta
        if np.linalg.norm(delta) < tol:
            break

    z_final = np.clip(X_mat @ theta, -30.0, 30.0)
    p_pred = 1.0 / (1.0 + np.exp(-z_final))
    return np.clip(p_pred, clip_min, clip_max)


def compute_importance_weights(
    a: np.ndarray,
    pi_e_action: np.ndarray,
    propensities: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculates importance weights w_i = 1_{A_i = pi_e(X_i)} / mu(A_i | X_i).

    Args:
        a: Logged actions {0, 1}, shape (n,).
        pi_e_action: Target policy decisions {0, 1}, shape (n,).
        propensities: Estimated P(A=1 | X), shape (n,).

    Returns:
        Tuple of (importance weights w, observed action propensities mu_a).
    """
    if len(a) == 0:
        return np.array([], dtype=float), np.array([], dtype=float)

    mu_a = np.where(a == 1, propensities, 1.0 - propensities)
    matches = (a == pi_e_action).astype(float)
    w = matches / np.maximum(mu_a, 1e-4)
    return w, mu_a


def fit_reward_model(
    x: np.ndarray,
    a: np.ndarray,
    r: np.ndarray,
    pi_e_action: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Fits reward regression R ~ 1 + X + A + A*X and predicts counterfactuals.

    Args:
        x: Observed contexts, shape (n,).
        a: Logged actions, shape (n,).
        r: Observed rewards, shape (n,).
        pi_e_action: Decisions of target policy, shape (n,).

    Returns:
        Tuple of (r_hat_pi_e, r_hat_a):
            - r_hat_pi_e: Counterfactual prediction under target policy.
            - r_hat_a: Factual prediction under logged actions.
    """
    n = len(x)
    if n == 0:
        return np.array([], dtype=float), np.array([], dtype=float)

    F_logged = np.column_stack((
        np.ones(n, dtype=float),
        x.astype(float),
        a.astype(float),
        (a * x).astype(float),
    ))

    reg_eye = 1e-4 * np.eye(4)
    reg_eye[0, 0] = 0.0  # Preserve unpenalized intercept

    try:
        beta = np.linalg.solve(F_logged.T @ F_logged + reg_eye, F_logged.T @ r)
    except np.linalg.LinAlgError:
        beta, _, _, _ = np.linalg.lstsq(F_logged, r, rcond=None)

    F_pi_e = np.column_stack((
        np.ones(n, dtype=float),
        x.astype(float),
        pi_e_action.astype(float),
        (pi_e_action * x).astype(float),
    ))

    r_hat_pi_e = F_pi_e @ beta
    r_hat_a = F_logged @ beta
    return r_hat_pi_e, r_hat_a


def estimate_naive(a: np.ndarray, r: np.ndarray) -> float:
    """Naive estimator: average reward of treated units (a=1)."""
    treated = a == 1
    if not np.any(treated):
        return float(np.mean(r)) if len(r) > 0 else 0.0
    return float(np.mean(r[treated]))


def estimate_replay(a: np.ndarray, r: np.ndarray, pi_e_action: np.ndarray) -> float:
    """Replay estimator: unweighted mean of rewards on exact matching actions."""
    matches = a == pi_e_action
    if not np.any(matches):
        return float(np.mean(r)) if len(r) > 0 else 0.0
    return float(np.mean(r[matches]))


def estimate_direct_method(r_hat_pi_e: np.ndarray) -> float:
    """Direct Method (DM): mean of counterfactual regression predictions."""
    return float(np.mean(r_hat_pi_e)) if len(r_hat_pi_e) > 0 else 0.0


def estimate_ipw(w: np.ndarray, r: np.ndarray) -> float:
    """Inverse Propensity Weighting (Horvitz-Thompson)."""
    return float(np.mean(w * r)) if len(w) > 0 else 0.0


def estimate_snipw(w: np.ndarray, r: np.ndarray) -> float:
    """Self-Normalized Inverse Propensity Weighting (Hajek)."""
    sum_w = float(np.sum(w))
    if sum_w <= 1e-12:
        return 0.0
    return float(np.sum(w * r) / sum_w)


def estimate_doubly_robust(
    w: np.ndarray,
    r: np.ndarray,
    r_hat_pi_e: np.ndarray,
    r_hat_a: np.ndarray,
) -> float:
    """Doubly Robust (AIPW) estimator."""
    if len(w) == 0:
        return 0.0
    dr_terms = r_hat_pi_e + w * (r - r_hat_a)
    return float(np.mean(dr_terms))


def effective_sample_size(w: np.ndarray) -> float:
    """Kish's Effective Sample Size (ESS): (sum(w))^2 / sum(w^2)."""
    sum_w = float(np.sum(w))
    sum_w2 = float(np.sum(w**2))
    if sum_w2 <= 1e-12:
        return 0.0
    return float((sum_w**2) / sum_w2)


def evaluate_all_estimators(dataset: Dataset) -> EvaluationSummary:
    """Computes all 6 estimators and diagnostics on a logged dataset.

    Args:
        dataset: Contextual bandit dataset.

    Returns:
        EvaluationSummary containing point estimates, errors relative to V*,
        ESS, and maximum importance weight.
    """
    x = dataset.x
    a = dataset.a
    r = dataset.r
    pi_e_action = dataset.pi_e_action
    v_star = dataset.true_interventional_value

    # 1. Fast propensity model on x (never sees u)
    props = fast_logistic_propensity(x, a)

    # 2. Importance weights
    w, _ = compute_importance_weights(a, pi_e_action, props)

    # 3. Reward model
    r_hat_pi_e, r_hat_a = fit_reward_model(x, a, r, pi_e_action)

    # 4. Compute all 6 estimators
    vals: dict[str, float] = {
        "Naive": estimate_naive(a, r),
        "Replay": estimate_replay(a, r, pi_e_action),
        "Direct Method": estimate_direct_method(r_hat_pi_e),
        "IPW": estimate_ipw(w, r),
        "SNIPW": estimate_snipw(w, r),
        "Doubly Robust": estimate_doubly_robust(w, r, r_hat_pi_e, r_hat_a),
    }

    results: dict[str, EstimatorResult] = {}
    for name, val in vals.items():
        results[name] = EstimatorResult(
            name=name,
            value=val,
            error=abs(val - v_star),
            signed_error=val - v_star,
        )

    max_w = float(np.max(w)) if len(w) > 0 else 0.0
    ess = effective_sample_size(w)
    ess_ratio = ess / dataset.n if dataset.n > 0 else 0.0

    # Best among valid OPE methods (excluding Naive)
    ope_candidates = [
        "Replay",
        "Direct Method",
        "IPW",
        "SNIPW",
        "Doubly Robust",
    ]
    best_est = min(ope_candidates, key=lambda k: results[k].error)

    logger.debug(
        "Evaluated estimators: DR=%.4f (err=%.4f), Naive=%.4f (err=%.4f), MaxW=%.2f, ESS=%.1f",
        results["Doubly Robust"].value,
        results["Doubly Robust"].error,
        results["Naive"].value,
        results["Naive"].error,
        max_w,
        ess,
    )

    return EvaluationSummary(
        results=results,
        max_weight=max_w,
        ess=ess,
        ess_ratio=ess_ratio,
        true_value=v_star,
        best_estimator=best_est,
        weights=w,
    )


compute_all_estimators = evaluate_all_estimators
