"""Smoke and integration tests for the Streamlit app interface using AppTest."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_app_loads_and_runs_without_exceptions():
    """Validates that app.py loads cleanly and completes inference on default settings."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception, f"App raised exception: {at.exception}"
    assert len(at.tabs) >= 6
    assert len(at.dataframe) >= 1


def test_app_preset_easy_rct():
    """Validates clicking Easy RCT preset button."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    btn = next(b for b in at.button if b.label == "Easy RCT")
    btn.click().run()
    assert not at.exception
    assert at.session_state.preset_name == "Easy (Ideal RCT)"


def test_app_preset_trap():
    """Validates clicking Hidden Confounder Trap preset button."""
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.run()
    assert not at.exception

    btn = next(b for b in at.button if b.label == "Trap")
    btn.click().run()
    assert not at.exception
    assert at.session_state.preset_name == "Hidden Confounder (Trap)"
