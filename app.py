"""OPE Lab: Interactive Off-Policy Evaluation Studio.

Perceptron Hackathon 2026 - Problem 3:
"Did the Policy Actually Work, or Did It Just Look Like It Did?"
"""

from __future__ import annotations

import io
import time

import numpy as np
import pandas as pd
import streamlit as st

from ope.bootstrap import BootstrapSummary, run_bootstrap_ci
from ope.estimators import EstimatorSummary, compute_all_estimators
from ope.simulator import TRUE_INTERVENTIONAL_VALUE, Dataset, simulate_dgp
from ui.charts import create_estimator_ci_chart, create_weight_distribution_chart
from ui.components import (
    render_footer,
    render_header,
    render_insight_banner,
    render_metric_cards,
    render_overview_tab,
)
from ui.theme import inject_theme

# Page setup
st.set_page_config(
    page_title="OPE Lab • Off-Policy Evaluation Studio",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner=False)
def run_cached_experiment(
    n: int,
    confounding: float,
    overlap: float,
    noise: float,
    seed: int,
    b_resamples: int,
) -> tuple[Dataset, EstimatorSummary, BootstrapSummary]:
    """Caches simulation, point estimation, and bootstrap inference for sub-second UI updates."""
    dataset = simulate_dgp(
        n=n,
        confounding=confounding,
        overlap=overlap,
        noise=noise,
        seed=seed,
    )
    est_summary = compute_all_estimators(dataset)
    boot_summary = run_bootstrap_ci(
        dataset,
        b=b_resamples,
        seed=seed,
    )
    return dataset, est_summary, boot_summary


def initialize_session_state() -> None:
    """Initializes session state keys with default values."""
    defaults = {
        "confounding": 0.0,
        "overlap": 0.80,
        "n_samples": 3000,
        "noise": 0.30,
        "seed": 42,
        "b_resamples": 100,
        "is_dark": True,
        "preset_name": "Custom",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def apply_preset(preset: str) -> None:
    """Updates parameter controls according to standard pedagogical benchmarks."""
    st.session_state.preset_name = preset
    if preset == "Easy (Ideal RCT)":
        st.session_state.confounding = 0.0
        st.session_state.overlap = 0.90
        st.session_state.noise = 0.30
        st.session_state.n_samples = 3000
    elif preset == "Low Overlap (Heavy Tails)":
        st.session_state.confounding = 0.0
        st.session_state.overlap = 0.15
        st.session_state.noise = 0.30
        st.session_state.n_samples = 3000
    elif preset == "Hidden Confounder (Trap)":
        st.session_state.confounding = 0.80
        st.session_state.overlap = 0.70
        st.session_state.noise = 0.30
        st.session_state.n_samples = 3000


def main() -> None:
    initialize_session_state()

    # Sidebar: Mission Configuration
    with st.sidebar:
        st.markdown("### ⚙️ Mission Controls")

        # Theme toggle
        is_dark = st.toggle("🌙 Dark Mode", value=st.session_state.is_dark)
        st.session_state.is_dark = is_dark
        inject_theme(is_dark)

        st.markdown("---")
        st.markdown("#### 🎯 Benchmark Presets")
        preset_cols = st.columns(3)
        if preset_cols[0].button("Easy RCT", use_container_width=True, help="c=0, overlap=0.9"):
            apply_preset("Easy (Ideal RCT)")
            st.rerun()
        if preset_cols[1].button("Low Ovl", use_container_width=True, help="c=0, overlap=0.15"):
            apply_preset("Low Overlap (Heavy Tails)")
            st.rerun()
        if preset_cols[2].button("Trap", use_container_width=True, help="c=0.8, overlap=0.7"):
            apply_preset("Hidden Confounder (Trap)")
            st.rerun()

        st.markdown(f"**Current:** *{st.session_state.preset_name}*")
        st.markdown("---")
        st.markdown("#### 🔬 Environment Parameters")

        confounding = st.slider(
            "Confounding Strength (c)",
            min_value=0.0,
            max_value=1.0,
            value=float(st.session_state.confounding),
            step=0.05,
            help="Strength of hidden confounder U affecting both logging policy and treatment effect. c=0 is unconfounded.",
        )
        st.session_state.confounding = confounding

        overlap = st.slider(
            "Overlap Level (α)",
            min_value=0.05,
            max_value=1.0,
            value=float(st.session_state.overlap),
            step=0.05,
            help="Controls propensity overlap. Low values force logging policy to be near-deterministic, inflating weights.",
        )
        st.session_state.overlap = overlap

        n_samples = st.slider(
            "Sample Size (n)",
            min_value=500,
            max_value=20000,
            value=int(st.session_state.n_samples),
            step=500,
            help="Number of historical logged interactions (X, A, R) generated from logging policy π₀.",
        )
        st.session_state.n_samples = n_samples

        noise = st.slider(
            "Reward Noise (σ)",
            min_value=0.1,
            max_value=1.0,
            value=float(st.session_state.noise),
            step=0.05,
            help="Standard deviation of Gaussian noise added to the reward outcome.",
        )
        st.session_state.noise = noise

        st.markdown("---")
        st.markdown("#### 🎲 Reproducibility")
        c_seed, c_btn = st.columns([2, 1])
        with c_seed:
            seed_val = st.number_input(
                "Random Seed",
                value=int(st.session_state.seed),
                step=1,
            )
            st.session_state.seed = seed_val
        with c_btn:
            st.write("")
            st.write("")
            if st.button("🎲 New", use_container_width=True, help="Generate random seed"):
                st.session_state.seed = int(np.random.randint(1, 999999))
                st.rerun()

        b_resamples = st.select_slider(
            "Bootstrap Resamples (B)",
            options=[30, 50, 100, 200],
            value=int(st.session_state.b_resamples),
            help="Resamples for 95% percentile confidence intervals. Adaptive when n > 10,000.",
        )
        st.session_state.b_resamples = b_resamples

        st.markdown("---")
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button("🔄 Reset", use_container_width=True):
                apply_preset("Custom")
                st.session_state.confounding = 0.0
                st.session_state.overlap = 0.80
                st.session_state.n_samples = 3000
                st.session_state.noise = 0.30
                st.session_state.seed = 42
                st.rerun()
        with action_col2:
            st.button("🚀 Run Lab", type="primary", use_container_width=True)

    # Main Body Header
    render_header()

    # Primary Navigation Tabs
    tab_overview, tab_results, tab_failure, tab_decision, tab_sensitivity, tab_realdata = st.tabs([
        "📖 Overview",
        "📊 Results",
        "💥 Failure Study",
        "🗺️ Decision Map",
        "🛡️ Sensitivity",
        "📁 Real Data",
    ])

    with tab_overview:
        render_overview_tab()

    with tab_results:
        # Progress indicator during execution
        with st.spinner("Executing simulation, propensity fitting & bootstrap inference..."):
            prog_bar = st.progress(0, text="Generating synthetic logged interactions...")
            prog_bar.progress(30, text="Fitting outcome regression & propensity models...")
            dataset, est_summary, boot_summary = run_cached_experiment(
                n=st.session_state.n_samples,
                confounding=st.session_state.confounding,
                overlap=st.session_state.overlap,
                noise=st.session_state.noise,
                seed=st.session_state.seed,
                b_resamples=st.session_state.b_resamples,
            )
            prog_bar.progress(100, text="Inference complete!")
            time.sleep(0.05)
            prog_bar.empty()

        # Find closest estimator
        errors = {
            name: abs(boot_summary.get(name).point_estimate - TRUE_INTERVENTIONAL_VALUE)
            for name in boot_summary.results
        }
        closest_estimator = min(errors, key=errors.get)

        # 1. Metric Cards
        naive_res = boot_summary.get("Naive")
        dr_res = boot_summary.get("Doubly Robust")
        render_metric_cards(
            true_val=TRUE_INTERVENTIONAL_VALUE,
            naive_val=naive_res.point_estimate,
            naive_ci=(naive_res.ci_lower, naive_res.ci_upper),
            dr_val=dr_res.point_estimate,
            dr_ci=(dr_res.ci_lower, dr_res.ci_upper),
            ess=est_summary.ess,
            max_weight=est_summary.max_weight,
            n=dataset.n,
        )

        # 2. Contextual Insight Banner
        render_insight_banner(
            confounding=st.session_state.confounding,
            overlap=st.session_state.overlap,
            closest_estimator=closest_estimator,
            ess_ratio=est_summary.ess / dataset.n,
        )

        # 3. Interactive Visualization Row
        col_chart, col_weights = st.columns([7, 5])
        with col_chart:
            fig_ci = create_estimator_ci_chart(
                boot_summary=boot_summary,
                true_val=TRUE_INTERVENTIONAL_VALUE,
                is_dark=st.session_state.is_dark,
            )
            st.plotly_chart(fig_ci, use_container_width=True)

        with col_weights:
            fig_weights = create_weight_distribution_chart(
                weights=est_summary.weights,
                is_dark=st.session_state.is_dark,
            )
            st.plotly_chart(fig_weights, use_container_width=True)

        # 4. Estimator Comparison Data Table
        st.markdown("### 📋 Estimator Scorecard")
        table_rows = []
        for name, res in boot_summary.results.items():
            bias = res.point_estimate - TRUE_INTERVENTIONAL_VALUE
            abs_err = abs(bias)
            is_best = name == closest_estimator
            table_rows.append({
                "Estimator": f"★ {name}" if is_best else name,
                "Estimated Value V̂(πₑ)": f"{res.point_estimate:.4f}",
                "95% CI Lower": f"{res.ci_lower:.4f}",
                "95% CI Upper": f"{res.ci_upper:.4f}",
                "Std Error": f"{res.std_err:.4f}",
                "Bias vs V*": f"{bias:+.4f}",
                "Abs Error |V̂ - V*|": f"{abs_err:.4f}",
                "Status": "Lowest Bias" if is_best else "Evaluated",
            })

        df_scorecard = pd.DataFrame(table_rows)
        st.dataframe(df_scorecard, use_container_width=True, hide_index=True)

        # CSV Download
        csv_buffer = io.StringIO()
        df_scorecard.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Scorecard CSV",
            data=csv_buffer.getvalue(),
            file_name=f"ope_lab_results_c{st.session_state.confounding}_ovl{st.session_state.overlap}_n{dataset.n}.csv",
            mime="text/csv",
        )

        # 5. Mathematical Formulations Expander
        with st.expander("📐 Mathematical Formulations & Estimator Guide"):
            st.markdown(
                r"""
                | Estimator | Formula | Strengths | Vulnerabilities |
                | :--- | :--- | :--- | :--- |
                | **Naive** | $\hat{V}_{\text{Naive}} = \frac{1}{\sum A_i} \sum_{i: A_i=1} R_i$ | Zero variance | Severely confounded when $P(A=1\|X)$ varies |
                | **Replay** | $\hat{V}_{\text{Replay}} = \frac{\sum_{i: A_i=\pi_e(X_i)} R_i}{\sum_{i: A_i=\pi_e(X_i)} 1}$ | Unbiased for uniform random logging | Discards non-matching data; high variance |
                | **Direct Method (DM)** | $\hat{V}_{\text{DM}} = \frac{1}{n} \sum_{i=1}^n \hat{Q}(X_i, \pi_e(X_i))$ | Low variance; stable | Biased if reward model $\hat{Q}$ is misspecified |
                | **IPW** | $\hat{V}_{\text{IPW}} = \frac{1}{n} \sum_{i=1}^n \frac{\mathbb{I}(A_i=\pi_e(X_i))}{e(X_i)} R_i$ | Unbiased under unconfoundedness | Extreme variance when overlap $\alpha \to 0$ |
                | **SNIPW** | $\hat{V}_{\text{SNIPW}} = \frac{\sum W_i R_i}{\sum W_i}$ | Variance-stabilized; bounded by reward range | Small-sample bias ($O(1/n)$) |
                | **Doubly Robust (DR)** | $\hat{V}_{\text{DR}} = \hat{V}_{\text{DM}} + \frac{1}{n} \sum W_i [R_i - \hat{Q}(X_i, A_i)]$ | Unbiased if **either** $e(X)$ or $\hat{Q}$ is correct | Vulnerable to unobserved confounding $U$ |
                """
            )

    # Clean placeholders for upcoming steps
    with tab_failure:
        st.markdown("### 💥 Failure Mode Deep Dive")
        st.info(
            "🔬 **Under Construction (Step 5)**: This tab will present targeted stress-tests comparing "
            "extreme weight variance (overlap breakdown) against omitted-variable bias (unobserved confounding)."
        )

    with tab_decision:
        st.markdown("### 🗺️ Estimator Decision Map")
        st.info(
            "🗺️ **Under Construction (Step 5)**: This tab will feature a 2D empirical phase diagram "
            "spanning confounding strength (x-axis) vs. overlap level (y-axis) across 20+ Monte Carlo seeds, "
            "mapping exactly which estimator minimizes MSE."
        )

    with tab_sensitivity:
        st.markdown("### 🛡️ Confounding Sensitivity Bounds (Rosenbaum Γ)")
        st.info(
            "🛡️ **Under Construction (Step 6)**: This tab will quantify policy robustness against hidden "
            "confounders by computing marginal sensitivity bounds across odds ratios $\\Lambda \\in [1.0, 3.0]$."
        )

    with tab_realdata:
        st.markdown("### 📁 Real-World Benchmark: Open Bandit Dataset")
        st.warning(
            "📦 **Open Bandit Pipeline (OBP) Fallback Card**: `obp` is not active in this environment. "
            "In Step 8, this tab will provide precomputed ZOZOTOWN benchmark metrics and offline policy "
            "comparisons without synthetic artifacts."
        )

    render_footer()


if __name__ == "__main__":
    main()
