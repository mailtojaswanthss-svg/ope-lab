"""Unit tests for the analysis engine: Failure Study sweeps and Decision Map logic."""

from __future__ import annotations

import numpy as np

from ope.analysis import (
    ELIGIBLE_WINNERS,
    DecisionCellResult,
    EstimatorStats,
    aggregate_estimator_stats,
    compute_confounding_sweep,
    compute_decision_map,
    compute_overlap_sweep,
)
from ope.simulator import TRUE_INTERVENTIONAL_VALUE


def test_aggregate_estimator_stats():
    """Verify statistical aggregation produces correct mean, bias, variance, and RMSE."""
    true_v = TRUE_INTERVENTIONAL_VALUE
    raw_data = {
        "IPW": [0.65, 0.67, 0.69],
        "Doubly Robust": [0.68, 0.68, 0.68],
    }
    stats = aggregate_estimator_stats(raw_data, true_val=true_v)

    assert "IPW" in stats
    assert "Doubly Robust" in stats

    dr_stat = stats["Doubly Robust"]
    assert np.isclose(dr_stat.mean_estimate, 0.68)
    assert np.isclose(dr_stat.bias, 0.68 - true_v)
    assert np.isclose(dr_stat.variance, 0.0)
    assert np.isclose(dr_stat.rmse, abs(0.68 - true_v))


def test_decision_cell_tie_and_unreliable_logic():
    """Test Decision Map winner selection, tie detection, and honesty rule on handmade inputs."""
    true_v = 0.68

    # Scenario 1: Clear winner (Doubly Robust has 0.02 RMSE vs runner-up 0.05 RMSE, bias < 0.05)
    def make_cell_from_stats(custom_stats: dict[str, tuple[float, float]]) -> DecisionCellResult:
        # custom_stats: name -> (mean_estimate, rmse)
        stats_dict = {}
        for name in ["Naive", "Replay", "Direct Method", "IPW", "SNIPW", "Doubly Robust"]:
            mean_est, rmse = custom_stats.get(name, (0.68, 0.10))
            bias = mean_est - true_v
            stats_dict[name] = EstimatorStats(
                name=name,
                estimates=[mean_est],
                mean_estimate=mean_est,
                bias=bias,
                abs_bias=abs(bias),
                variance=0.001,
                std_err=0.001,
                mse=rmse**2,
                rmse=rmse,
            )

        ranked = sorted(ELIGIBLE_WINNERS, key=lambda n: stats_dict[n].rmse)
        w, r = ranked[0], ranked[1]
        w_rmse, r_rmse = stats_dict[w].rmse, stats_dict[r].rmse
        w_abs_bias = stats_dict[w].abs_bias
        is_tie = (r_rmse - w_rmse) / w_rmse <= 0.10
        is_unreliable = w_abs_bias > 0.05

        if is_unreliable:
            label = "No method reliable"
        elif is_tie:
            label = "Tie"
        else:
            label = w

        return DecisionCellResult(
            confounding=0.0,
            overlap=0.8,
            n_seeds=20,
            n_samples=5000,
            stats=stats_dict,
            median_ess=2500.0,
            winner=w,
            runner_up=r,
            winner_rmse=w_rmse,
            runner_up_rmse=r_rmse,
            winner_abs_bias=w_abs_bias,
            is_tie=is_tie,
            is_unreliable=is_unreliable,
            label=label,
        )

    # 1. Clear winner: DR has 0.02 RMSE, Direct Method has 0.05 RMSE, bias 0.01
    c1 = make_cell_from_stats({
        "Naive": (0.80, 0.001),  # Naive has tiny RMSE but must be excluded!
        "Doubly Robust": (0.685, 0.020),
        "Direct Method": (0.690, 0.050),
        "SNIPW": (0.690, 0.060),
        "IPW": (0.690, 0.070),
        "Replay": (0.690, 0.080),
    })
    assert c1.winner == "Doubly Robust"
    assert c1.label == "Doubly Robust"
    assert not c1.is_tie
    assert not c1.is_unreliable

    # 2. Tie: DR (0.020) and SNIPW (0.021) within 10% (5% difference), bias < 0.05
    c2 = make_cell_from_stats({
        "Doubly Robust": (0.682, 0.020),
        "SNIPW": (0.683, 0.021),
        "Direct Method": (0.690, 0.050),
        "IPW": (0.690, 0.060),
        "Replay": (0.690, 0.080),
    })
    assert c2.winner == "Doubly Robust"
    assert c2.runner_up == "SNIPW"
    assert c2.is_tie
    assert c2.label == "Tie"
    assert not c2.is_unreliable

    # 3. Honesty Rule: Winner has bias > 0.05 (e.g. 0.09 bias) -> Must be "No method reliable"
    c3 = make_cell_from_stats({
        "Doubly Robust": (0.770, 0.095),  # bias = 0.090 > 0.05
        "SNIPW": (0.780, 0.105),
        "Direct Method": (0.775, 0.100),
        "IPW": (0.790, 0.120),
        "Replay": (0.800, 0.150),
    })
    assert c3.winner == "Doubly Robust"
    assert c3.is_unreliable
    assert c3.label == "No method reliable"


def test_confounding_sweep_deterministic_and_trends():
    """Verify confounding sweep runs, is deterministic for seed, and demonstrates confounding bias."""
    res1 = compute_confounding_sweep(
        confounding_levels=[0.0, 0.5],
        n_seeds=4,
        n=1000,
        overlap=0.8,
        noise=0.3,
        base_seed=123,
    )
    res2 = compute_confounding_sweep(
        confounding_levels=[0.0, 0.5],
        n_seeds=4,
        n=1000,
        overlap=0.8,
        noise=0.3,
        base_seed=123,
    )

    # Determinism
    for pt1, pt2 in zip(res1.points, res2.points):
        for name in pt1.estimator_stats:
            assert np.isclose(
                pt1.estimator_stats[name].mean_estimate,
                pt2.estimator_stats[name].mean_estimate,
            )

    # Trend: Confounding increases absolute bias of IPW and DR
    pt_c0 = res1.points[0]
    pt_c5 = res1.points[1]

    dr_bias_c0 = pt_c0.estimator_stats["Doubly Robust"].abs_bias
    dr_bias_c5 = pt_c5.estimator_stats["Doubly Robust"].abs_bias
    assert dr_bias_c5 > dr_bias_c0


def test_overlap_sweep_properties():
    """Verify overlap sweep outputs have expected structure, positive ESS and valid RMSE."""
    res1 = compute_overlap_sweep(
        overlap_levels=[0.10, 0.80],
        n_seeds=4,
        n=1000,
        confounding=0.0,
        noise=0.3,
        base_seed=321,
    )
    res2 = compute_overlap_sweep(
        overlap_levels=[0.10, 0.80],
        n_seeds=4,
        n=1000,
        confounding=0.0,
        noise=0.3,
        base_seed=321,
    )

    assert len(res1.points) == 2
    pt_low = res1.points[0]
    pt_high = res1.points[1]

    # Determinism
    assert np.isclose(pt_low.median_ess, res2.points[0].median_ess)
    assert np.isclose(pt_high.median_ess, res2.points[1].median_ess)

    # All estimators must have valid positive RMSE and ESS <= n
    assert 0 < pt_low.median_ess <= 1000
    assert 0 < pt_high.median_ess <= 1000
    for name in ELIGIBLE_WINNERS:
        assert pt_low.estimator_stats[name].rmse > 0
        assert pt_high.estimator_stats[name].rmse > 0


def test_compute_decision_map_grid():
    """Verify compute_decision_map generates the 3x3 matrix with expected labels and dimensions."""
    res = compute_decision_map(
        confounding_levels=[0.0, 1.0],
        overlap_levels=[0.2, 0.9],
        n_seeds=3,
        n=1000,
        noise=0.3,
        base_seed=999,
    )

    assert len(res.cells) == 4
    assert len(res.grid_labels) == 2
    assert len(res.grid_labels[0]) == 2

    # At c = 1.0, unobserved confounding is severe, so the honesty rule must trigger "No method reliable"
    cell_c1_ovl9 = res.cells[(1.0, 0.9)]
    assert cell_c1_ovl9.is_unreliable
    assert cell_c1_ovl9.label == "No method reliable"
