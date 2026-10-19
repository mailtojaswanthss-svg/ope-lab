"""Analysis and benchmarking engine for OPE Lab.

Provides:
- Confounding sweep: Evaluates estimator bias and RMSE as hidden confounding grows.
- Overlap sweep: Evaluates variance inflation and Kish Effective Sample Size as overlap degrades.
- Decision Map: 3x3 empirical phase matrix mapping best estimator by RMSE with
  tie detection and unobserved confounding honesty rules.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np

from ope.estimators import ESTIMATOR_NAMES, compute_all_estimators
from ope.simulator import TRUE_INTERVENTIONAL_VALUE, simulate_dgp

logger = logging.getLogger(__name__)

# Naive is strictly excluded from winning decision map cells
ELIGIBLE_WINNERS = [
    "Replay",
    "Direct Method",
    "IPW",
    "SNIPW",
    "Doubly Robust",
]


@dataclass(frozen=True)
class EstimatorStats:
    """Summary statistics for an estimator across multiple Monte Carlo seeds."""

    name: str
    estimates: list[float]
    mean_estimate: float
    bias: float
    abs_bias: float
    variance: float
    std_err: float
    mse: float
    rmse: float


@dataclass
class SweepPoint:
    """Results for a single parameter value in a sweep."""

    parameter_value: float
    estimator_stats: dict[str, EstimatorStats]
    median_ess: float
    mean_ess: float
    min_ess: float


@dataclass
class SweepResult:
    """Full results from a parameter sweep across multiple seeds."""

    parameter_name: str
    parameter_values: list[float]
    points: list[SweepPoint]
    n_samples: int
    n_seeds: int

    def get_metric_series(self, metric: str) -> dict[str, list[float]]:
        """Extracts a metric series across sweep points for each estimator.

        Args:
            metric: One of 'rmse', 'abs_bias', 'bias', 'mean_estimate', 'std_err'.

        Returns:
            Dictionary mapping estimator name to a list of float values.
        """
        series: dict[str, list[float]] = {name: [] for name in ESTIMATOR_NAMES}
        for pt in self.points:
            for name in ESTIMATOR_NAMES:
                stat = pt.estimator_stats[name]
                val = getattr(stat, metric, 0.0)
                series[name].append(val)
        return series

    def get_ess_series(self) -> list[float]:
        """Returns median ESS values across parameter points."""
        return [pt.median_ess for pt in self.points]


@dataclass
class DecisionCellResult:
    """Evaluation result for one cell in the 3x3 decision matrix."""

    confounding: float
    overlap: float
    n_seeds: int
    n_samples: int
    stats: dict[str, EstimatorStats]
    median_ess: float
    winner: str
    runner_up: str
    winner_rmse: float
    runner_up_rmse: float
    winner_abs_bias: float
    is_tie: bool
    is_unreliable: bool
    label: str  # Winner name, "Tie", or "No method reliable"
    details: dict[str, dict[str, float]] = field(default_factory=dict)


@dataclass
class DecisionMapResult:
    """Complete 3x3 decision map grid across confounding and overlap axes."""

    confounding_levels: list[float]
    overlap_levels: list[float]
    cells: dict[tuple[float, float], DecisionCellResult]
    grid_labels: list[list[str]]  # 2D grid of display labels (rows: overlap desc, cols: confounding)
    n_seeds: int
    n_samples: int
    noise: float


def run_monte_carlo_trial(
    n: int,
    confounding: float,
    overlap: float,
    noise: float,
    seed: int,
) -> tuple[dict[str, float], float]:
    """Runs a single simulation and returns point estimates and Kish ESS."""
    dataset = simulate_dgp(
        n=n,
        confounding=confounding,
        overlap=overlap,
        noise=noise,
        seed=seed,
    )
    summary = compute_all_estimators(dataset)
    estimates = {name: summary.results[name].value for name in ESTIMATOR_NAMES}
    return estimates, summary.ess


def aggregate_estimator_stats(
    estimates_by_name: dict[str, list[float]],
    true_val: float = TRUE_INTERVENTIONAL_VALUE,
) -> dict[str, EstimatorStats]:
    """Computes mean estimate, bias, variance, and RMSE across seeds."""
    stats_dict: dict[str, EstimatorStats] = {}
    for name, raw_vals in estimates_by_name.items():
        arr = np.asarray(raw_vals, dtype=np.float64)
        mean_est = float(np.mean(arr))
        bias = float(mean_est - true_val)
        abs_bias = float(abs(bias))
        variance = float(np.var(arr, ddof=1)) if len(arr) > 1 else 0.0
        std_err = float(np.std(arr, ddof=1) / np.sqrt(len(arr))) if len(arr) > 1 else 0.0
        mse = float(np.mean((arr - true_val) ** 2))
        rmse = float(np.sqrt(mse))

        stats_dict[name] = EstimatorStats(
            name=name,
            estimates=raw_vals,
            mean_estimate=mean_est,
            bias=bias,
            abs_bias=abs_bias,
            variance=variance,
            std_err=std_err,
            mse=mse,
            rmse=rmse,
        )
    return stats_dict


def compute_confounding_sweep(
    confounding_levels: list[float] | None = None,
    n_seeds: int = 30,
    n: int = 5000,
    overlap: float = 0.80,
    noise: float = 0.30,
    base_seed: int = 42,
) -> SweepResult:
    """Evaluates bias and RMSE for all estimators across confounding levels."""
    if confounding_levels is None:
        confounding_levels = [round(c, 2) for c in np.linspace(0.0, 1.0, 11)]

    logger.info(
        "Starting confounding sweep: %d levels, %d seeds/level, n=%d, overlap=%.2f",
        len(confounding_levels),
        n_seeds,
        n,
        overlap,
    )

    points: list[SweepPoint] = []

    for idx, c in enumerate(confounding_levels):
        raw_estimates: dict[str, list[float]] = {name: [] for name in ESTIMATOR_NAMES}
        ess_vals: list[float] = []

        for s in range(n_seeds):
            run_seed = base_seed + (idx * 1000) + s
            point_ests, ess = run_monte_carlo_trial(
                n=n,
                confounding=c,
                overlap=overlap,
                noise=noise,
                seed=run_seed,
            )
            for name in ESTIMATOR_NAMES:
                raw_estimates[name].append(point_ests[name])
            ess_vals.append(ess)

        stats = aggregate_estimator_stats(raw_estimates)
        med_ess = float(np.median(ess_vals))
        mean_ess = float(np.mean(ess_vals))
        min_ess = float(np.min(ess_vals))

        points.append(
            SweepPoint(
                parameter_value=c,
                estimator_stats=stats,
                median_ess=med_ess,
                mean_ess=mean_ess,
                min_ess=min_ess,
            )
        )

    return SweepResult(
        parameter_name="confounding",
        parameter_values=confounding_levels,
        points=points,
        n_samples=n,
        n_seeds=n_seeds,
    )


def compute_overlap_sweep(
    overlap_levels: list[float] | None = None,
    n_seeds: int = 30,
    n: int = 5000,
    confounding: float = 0.0,
    noise: float = 0.30,
    base_seed: int = 42,
) -> SweepResult:
    """Evaluates RMSE and Kish ESS for all estimators as overlap degrades at confounding 0."""
    if overlap_levels is None:
        overlap_levels = [round(alpha, 2) for alpha in np.linspace(0.1, 1.0, 10)]

    logger.info(
        "Starting overlap sweep: %d levels, %d seeds/level, n=%d, c=%.2f",
        len(overlap_levels),
        n_seeds,
        n,
        confounding,
    )

    points: list[SweepPoint] = []

    for idx, alpha in enumerate(overlap_levels):
        raw_estimates: dict[str, list[float]] = {name: [] for name in ESTIMATOR_NAMES}
        ess_vals: list[float] = []

        for s in range(n_seeds):
            run_seed = base_seed + (idx * 1000) + s + 50000
            point_ests, ess = run_monte_carlo_trial(
                n=n,
                confounding=confounding,
                overlap=alpha,
                noise=noise,
                seed=run_seed,
            )
            for name in ESTIMATOR_NAMES:
                raw_estimates[name].append(point_ests[name])
            ess_vals.append(ess)

        stats = aggregate_estimator_stats(raw_estimates)
        med_ess = float(np.median(ess_vals))
        mean_ess = float(np.mean(ess_vals))
        min_ess = float(np.min(ess_vals))

        points.append(
            SweepPoint(
                parameter_value=alpha,
                estimator_stats=stats,
                median_ess=med_ess,
                mean_ess=mean_ess,
                min_ess=min_ess,
            )
        )

    return SweepResult(
        parameter_name="overlap",
        parameter_values=overlap_levels,
        points=points,
        n_samples=n,
        n_seeds=n_seeds,
    )


def evaluate_decision_cell(
    confounding: float,
    overlap: float,
    n_seeds: int = 20,
    n: int = 5000,
    noise: float = 0.30,
    base_seed: int = 100,
    tie_threshold: float = 0.10,
    unreliable_bias_threshold: float = 0.05,
) -> DecisionCellResult:
    """Evaluates a single cell in the decision grid and assigns winner or unreliability label."""
    raw_estimates: dict[str, list[float]] = {name: [] for name in ESTIMATOR_NAMES}
    ess_vals: list[float] = []

    for s in range(n_seeds):
        run_seed = base_seed + s
        point_ests, ess = run_monte_carlo_trial(
            n=n,
            confounding=confounding,
            overlap=overlap,
            noise=noise,
            seed=run_seed,
        )
        for name in ESTIMATOR_NAMES:
            raw_estimates[name].append(point_ests[name])
        ess_vals.append(ess)

    stats = aggregate_estimator_stats(raw_estimates)
    median_ess = float(np.median(ess_vals))

    # Rank eligible candidates strictly by RMSE (Naive excluded!)
    ranked = sorted(
        ELIGIBLE_WINNERS,
        key=lambda name: stats[name].rmse,
    )
    winner_name = ranked[0]
    runner_up_name = ranked[1]

    winner_rmse = stats[winner_name].rmse
    runner_up_rmse = stats[runner_up_name].rmse
    winner_abs_bias = stats[winner_name].abs_bias

    # Check tie condition (top two RMSEs within 10%)
    is_tie = (runner_up_rmse - winner_rmse) / winner_rmse <= tie_threshold if winner_rmse > 0 else True

    # Honesty rule: if winner's absolute bias exceeds threshold, hidden confounding breaks all
    is_unreliable = winner_abs_bias > unreliable_bias_threshold

    if is_unreliable:
        label = "No method reliable"
    elif is_tie:
        label = "Tie"
    else:
        label = winner_name

    details: dict[str, dict[str, float]] = {
        name: {
            "mean": stats[name].mean_estimate,
            "bias": stats[name].bias,
            "abs_bias": stats[name].abs_bias,
            "rmse": stats[name].rmse,
            "variance": stats[name].variance,
        }
        for name in ESTIMATOR_NAMES
    }

    return DecisionCellResult(
        confounding=confounding,
        overlap=overlap,
        n_seeds=n_seeds,
        n_samples=n,
        stats=stats,
        median_ess=median_ess,
        winner=winner_name,
        runner_up=runner_up_name,
        winner_rmse=winner_rmse,
        runner_up_rmse=runner_up_rmse,
        winner_abs_bias=winner_abs_bias,
        is_tie=is_tie,
        is_unreliable=is_unreliable,
        label=label,
        details=details,
    )


def compute_decision_map(
    confounding_levels: list[float] | None = None,
    overlap_levels: list[float] | None = None,
    n_seeds: int = 20,
    n: int = 5000,
    noise: float = 0.30,
    base_seed: int = 100,
    tie_threshold: float = 0.10,
    unreliable_bias_threshold: float = 0.05,
) -> DecisionMapResult:
    """Computes the full 3x3 Decision Map grid."""
    if confounding_levels is None:
        confounding_levels = [0.0, 0.5, 1.0]
    if overlap_levels is None:
        overlap_levels = [0.2, 0.5, 0.9]

    cells: dict[tuple[float, float], DecisionCellResult] = {}

    for c_idx, c in enumerate(confounding_levels):
        for o_idx, alpha in enumerate(overlap_levels):
            cell_seed = base_seed + (c_idx * 1000) + (o_idx * 100)
            cell_res = evaluate_decision_cell(
                confounding=c,
                overlap=alpha,
                n_seeds=n_seeds,
                n=n,
                noise=noise,
                base_seed=cell_seed,
                tie_threshold=tie_threshold,
                unreliable_bias_threshold=unreliable_bias_threshold,
            )
            cells[(c, alpha)] = cell_res

    # Construct 2D grid of labels: rows = overlap (high to low: 0.9, 0.5, 0.2), cols = confounding (0, 0.5, 1.0)
    sorted_overlaps = sorted(overlap_levels, reverse=True)
    grid_labels: list[list[str]] = []
    for alpha in sorted_overlaps:
        row: list[str] = []
        for c in confounding_levels:
            row.append(cells[(c, alpha)].label)
        grid_labels.append(row)

    return DecisionMapResult(
        confounding_levels=confounding_levels,
        overlap_levels=sorted_overlaps,
        cells=cells,
        grid_labels=grid_labels,
        n_seeds=n_seeds,
        n_samples=n,
        noise=noise,
    )
