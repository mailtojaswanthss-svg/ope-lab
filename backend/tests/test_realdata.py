"""Unit tests for real-world Open Bandit Dataset benchmark and fallback handling."""

from __future__ import annotations

from pathlib import Path

from ope.realdata import (
    ZOZOTOWN_ALL_META,
    get_reference_zozotown_benchmark,
    is_obp_available,
    load_local_zozotown_sample,
)


def test_open_bandit_meta():
    """Metadata must correctly specify campaign dimensions."""
    assert ZOZOTOWN_ALL_META.num_actions == 80
    assert ZOZOTOWN_ALL_META.context_dim == 3
    assert "ZOZOTOWN" in ZOZOTOWN_ALL_META.campaign_name


def test_reference_zozotown_benchmark():
    """Benchmark table must contain expected columns and valid numerical values."""
    df = get_reference_zozotown_benchmark()
    assert len(df) == 7
    expected_cols = ["Estimator", "Policy Value (CTR)", "Relative Lift vs Random", "Standard Error", "Status"]
    assert list(df.columns) == expected_cols

    # CTR values must be positive and bounded in (0, 0.02)
    ctrs = df["Policy Value (CTR)"].to_numpy()
    assert (ctrs > 0).all()
    assert (ctrs < 0.02).all()

    # Doubly Robust should be very close to Ground Truth
    dr_ctr = float(df[df["Estimator"] == "Doubly Robust (DR)"]["Policy Value (CTR)"].iloc[0])
    truth_ctr = float(df[df["Estimator"] == "Ground Truth (On-Policy BTS)"]["Policy Value (CTR)"].iloc[0])
    assert abs(dr_ctr - truth_ctr) <= 0.0005


def test_is_obp_available():
    """Function must return a boolean without crashing."""
    avail = is_obp_available()
    assert isinstance(avail, bool)


def test_load_local_sample_missing_file():
    """Missing file should return None safely without raising an exception."""
    result = load_local_zozotown_sample(Path("non_existent_dir/missing.csv"))
    assert result is None
