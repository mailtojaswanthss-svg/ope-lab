"""Data generating process and ground-truth simulator for OPE Lab.

Simulates contextual bandit environments with controllable unobserved confounding,
overlap, and reward noise. Ground truth is known analytically as the interventional
value of the new policy.

Causal Formulation:
- Observed context: X ~ N(0, 1)
- Unobserved confounder: U ~ N(0, 1)
- Logging policy: P(A=1 | X, U) = sigmoid(L*X + 3*c*U)
  where L = 0.5 + 5*(1 - overlap) controls positivity.
- Structural Reward Equation:
  R = 0.5 + 0.3*X + A*(0.2 + 0.2*X + 0.5*U) + 0.4*U + noise*N(0, 1)

Why this breaks unadjusted estimators under hidden confounding:
In earlier specifications where U only entered additively (+ 0.4*U), the bias
induced by U on treated rows (A=1) and control rows (A=0) cancelled out symmetrically
around X = 0 under the target policy (treat when X > 0). By allowing U to also modify
the treatment effect (A * 0.5*U), units that the logging policy selectively chooses to
treat have E[U | A=1] > 0. Because estimators only observe X and never U, propensity
and regression models cannot adjust for U, creating genuine omitted variable bias.

Under the causal intervention do(A = pi_e(X)), A is independent of U given X,
and since E[U] = 0, E[A * 0.5*U] = 0. Hence the true interventional value remains:
V*(pi_e) = 0.5 + 0.1 + 0.2 * 0.398942 = 0.679788.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from ope.logging_config import logger

# Analytical Interventional Ground Truth Value of Target Policy pi_e:
# E[R | do(A = pi_e(X))] = 0.5 + 0.3*E[X] + 0.2*E[1_{X>0}] + 0.2*E[X*1_{X>0}] + 0.5*E[1_{X>0}*U] + 0.4*E[U]
# Since U is independent of X with E[U]=0: E[1_{X>0}*U] = E[1_{X>0}]*E[U] = 0.
# For X ~ N(0,1), E[X]=0, E[1_{X>0}]=0.5, and E[X*1_{X>0}] = 1/sqrt(2*pi) ~ 0.39894228
# V*(pi_e) = 0.5 + 0.1 + 0.2 * 0.398942 = 0.679788
TRUE_INTERVENTIONAL_VALUE: float = 0.5 + 0.1 + 0.2 * (1.0 / math.sqrt(2.0 * math.pi))


@dataclass(frozen=True)
class Dataset:
    """Immutable container for logged contextual bandit interaction data."""

    x: np.ndarray  # Observed context, shape (n,)
    u: np.ndarray  # Unobserved confounder, shape (n,)
    pi_0_prob: np.ndarray  # True logging policy propensity P(A=1 | X, U), shape (n,)
    a: np.ndarray  # Logged binary action {0, 1}, shape (n,)
    r: np.ndarray  # Observed scalar reward, shape (n,)
    pi_e_action: np.ndarray  # Target policy action {0, 1}, shape (n,)
    confounding: float
    overlap: float
    noise: float
    true_interventional_value: float = TRUE_INTERVENTIONAL_VALUE

    @property
    def n(self) -> int:
        """Sample size."""
        return len(self.x)


def sigmoid(z: np.ndarray) -> np.ndarray:
    """Numerically stable sigmoid activation function.

    Args:
        z: Input array.

    Returns:
        Element-wise sigmoid 1 / (1 + exp(-z)).
    """
    z_clipped = np.clip(z, -30.0, 30.0)
    return 1.0 / (1.0 + np.exp(-z_clipped))


def target_policy(x: np.ndarray) -> np.ndarray:
    """Evaluates target policy pi_e: Treat (a=1) if x > 0, else 0.

    Args:
        x: Context array of shape (n,).

    Returns:
        Binary action array of shape (n,) where a = 1 if x > 0 else 0.
    """
    return (x > 0.0).astype(int)


def simulate_dgp(
    n: int = 5000,
    confounding: float = 0.0,
    overlap: float = 0.9,
    noise: float = 0.3,
    seed: int | None = None,
) -> Dataset:
    """Simulates contextual bandit data according to the benchmark DGP specification.

    Args:
        n: Number of logged interaction rows (n >= 100).
        confounding: Confounding strength c in [0.0, 1.0].
        overlap: Overlap parameter in [0.05, 1.0] (lower = more deterministic logging).
        noise: Standard deviation of Gaussian reward noise (noise > 0.0).
        seed: Optional random seed for reproducible sampling.

    Returns:
        Dataset with observed context, logged actions, rewards, and target decisions.

    Raises:
        ValueError: If any input parameters violate domain constraints.
    """
    if n < 100:
        raise ValueError(f"Sample size n must be >= 100, got {n}")
    if not (0.0 <= confounding <= 1.0):
        raise ValueError(f"Confounding must be in [0.0, 1.0], got {confounding}")
    if not (0.05 <= overlap <= 1.0):
        raise ValueError(f"Overlap must be in [0.05, 1.0], got {overlap}")
    if noise <= 0.0:
        raise ValueError(f"Noise standard deviation must be > 0.0, got {noise}")

    rng = np.random.default_rng(seed)

    # 1. Observed context X and unobserved confounder U
    x = rng.normal(loc=0.0, scale=1.0, size=n)
    u = rng.normal(loc=0.0, scale=1.0, size=n)

    # 2. Logging policy propensity with overlap and confounding
    # L = 0.5 + 5 * (1 - overlap): overlap=1.0 -> L=0.5; overlap=0.05 -> L=5.25
    ell = 0.5 + 5.0 * (1.0 - overlap)
    logit = ell * x + 3.0 * confounding * u
    pi_0_prob = sigmoid(logit)

    # 3. Logged action sampled from behavior policy
    a = (rng.uniform(size=n) < pi_0_prob).astype(int)

    # 4. Observed reward from structural equation + treatment effect modification + confounding + noise
    reward_noise = rng.normal(loc=0.0, scale=noise, size=n)
    r = 0.5 + 0.3 * x + a * (0.2 + 0.2 * x + 0.5 * u) + 0.4 * u + reward_noise

    # 5. Target policy actions (only sees x)
    pi_e_act = target_policy(x)

    logger.debug(
        "Simulated DGP: n=%d, c=%.2f, overlap=%.2f, noise=%.2f, seed=%s",
        n,
        confounding,
        overlap,
        noise,
        str(seed),
    )

    return Dataset(
        x=x,
        u=u,
        pi_0_prob=pi_0_prob,
        a=a,
        r=r,
        pi_e_action=pi_e_act,
        confounding=confounding,
        overlap=overlap,
        noise=noise,
        true_interventional_value=TRUE_INTERVENTIONAL_VALUE,
    )
