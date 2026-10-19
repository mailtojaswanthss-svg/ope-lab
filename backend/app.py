"""OPE Lab: Interactive Off-Policy Evaluation Studio.

Perceptron Hackathon 2026 - Problem 3:
"Did the Policy Actually Work, or Did It Just Look Like It Did?"

Modern calculator layout:
- Overview tab with animated gradient mesh hero ("Did the policy really work?")
- Calculator-style Results tab: left controls card, right large result card with
  big headline number (Naive error vs truth) + two sub-stat cards
- High-contrast WCAG AA typography and pill-style controls
"""

from __future__ import annotations

import io
import time

import numpy as np
import pandas as pd
import streamlit as st

from ope.analysis import (
    DecisionMapResult,
    SweepResult,
    compute_confounding_sweep,
    compute_decision_map,
    compute_overlap_sweep,
)
from ope.bootstrap import BootstrapSummary, run_bootstrap_ci
from ope.estimators import EstimatorSummary, compute_all_estimators
from ope.sensitivity import SensitivityResult, compute_sensitivity_bounds
from ope.simulator import TRUE_INTERVENTIONAL_VALUE, Dataset, simulate_dgp
from ui.charts import (
    create_confounding_sweep_chart,
    create_decision_map_grid_chart,
    create_estimator_ci_chart,
    create_overlap_sweep_chart,
    create_sensitivity_bounds_chart,
    create_weight_distribution_chart,
)
from ui.components import (
    render_dark_green_results_card,
    render_decision_map_summary,
    render_failure_takeaway_a,
    render_failure_takeaway_b,
    render_footer,
    render_header,
    render_insight_banner,
    render_overview_tab,
    render_realdata_card,
    render_ribbed_hero_banner,
    render_sensitivity_summary,
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


@st.cache_data(show_spinner=False)
def run_cached_confounding_sweep(
    n_seeds: int,
    n_samples: int,
    overlap: float,
    noise: float,
    base_seed: int,
) -> SweepResult:
    """Caches Monte Carlo sweep across confounding levels [0.0, 1.0]."""
    return compute_confounding_sweep(
        confounding_levels=[round(c, 2) for c in np.linspace(0.0, 1.0, 11)],
        n_seeds=n_seeds,
        n=n_samples,
        overlap=overlap,
        noise=noise,
        base_seed=base_seed,
    )


@st.cache_data(show_spinner=False)
def run_cached_overlap_sweep(
    n_seeds: int,
    n_samples: int,
    confounding: float,
    noise: float,
    base_seed: int,
) -> SweepResult:
    """Caches Monte Carlo sweep across overlap levels [0.1, 1.0]."""
    return compute_overlap_sweep(
        overlap_levels=[round(alpha, 2) for alpha in np.linspace(0.1, 1.0, 10)],
        n_seeds=n_seeds,
        n=n_samples,
        confounding=confounding,
        noise=noise,
        base_seed=base_seed,
    )


@st.cache_data(show_spinner=False)
def run_cached_decision_map(
    n_seeds: int,
    n_samples: int,
    noise: float,
    base_seed: int,
) -> DecisionMapResult:
    """Caches 3x3 Decision Map grid evaluation."""
    return compute_decision_map(
        confounding_levels=[0.0, 0.5, 1.0],
        overlap_levels=[0.2, 0.5, 0.9],
        n_seeds=n_seeds,
        n=n_samples,
        noise=noise,
        base_seed=base_seed,
    )


@st.cache_data(show_spinner=False)
def run_cached_sensitivity(
    n: int,
    confounding: float,
    overlap: float,
    noise: float,
    seed: int,
    max_lambda: float = 3.0,
) -> SensitivityResult:
    """Caches marginal sensitivity bounds computation."""
    dataset = simulate_dgp(n=n, confounding=confounding, overlap=overlap, noise=noise, seed=seed)
    lambdas = np.linspace(1.0, max_lambda, 41)
    return compute_sensitivity_bounds(dataset, lambdas=lambdas)


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

    # Sidebar: Global Navigation and Preferences
    with st.sidebar:
        st.markdown("### ⚙️ Mission Preferences")

        # Theme query param handling & toggle
        q_theme = st.query_params.get("theme")
        if q_theme == "light":
            st.session_state.is_dark = False
        elif q_theme == "dark":
            st.session_state.is_dark = True

        is_dark = st.toggle("🌙 Dark Mode", value=st.session_state.is_dark)
        st.session_state.is_dark = is_dark
        inject_theme(is_dark)

        st.markdown("---")
        st.markdown("#### 🎯 Quick Presets")
        if st.button("🎯 Easy RCT (c=0, α=0.9)", key="sb_easy", use_container_width=True):
            apply_preset("Easy (Ideal RCT)")
            st.rerun()
        if st.button("⚡ Low Overlap (c=0, α=0.15)", key="sb_low", use_container_width=True):
            apply_preset("Low Overlap (Heavy Tails)")
            st.rerun()
        if st.button("🪤 Confounder Trap (c=0.8, α=0.7)", key="sb_trap", use_container_width=True):
            apply_preset("Hidden Confounder (Trap)")
            st.rerun()

        st.caption(f"Active Preset: **{st.session_state.preset_name}**")
        st.markdown("---")

        if st.button("🔄 Reset Defaults", key="sb_reset", use_container_width=True):
            apply_preset("Custom")
            st.session_state.confounding = 0.0
            st.session_state.overlap = 0.80
            st.session_state.n_samples = 3000
            st.session_state.noise = 0.30
            st.session_state.seed = 42
            st.rerun()

        st.markdown("---")
        st.markdown(
            """
            <div style="font-size:0.8rem; color:#64748b; line-height:1.4;">
                <b>Target Interventional Truth:</b><br>
                <code>V*(π<sub>e</sub>) = 0.6798</code><br>
                Evaluated under Pearl's <code>do(A = π<sub>e</sub>(X))</code>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Top Brand Header & Full-Width Ribbed-Glass Gradient Hero Banner
    render_header()
    render_ribbed_hero_banner()

    # Query params handling for testing and headless screenshot automation
    q_preset = st.query_params.get("preset")
    if q_preset:
        preset_map = {
            "easy": "Easy (Ideal RCT)",
            "low": "Low Overlap (Heavy Tails)",
            "trap": "Hidden Confounder (Trap)",
        }
        if q_preset in preset_map and st.session_state.preset_name != preset_map[q_preset]:
            apply_preset(preset_map[q_preset])

    q_tab = st.query_params.get("tab", "overview").lower()
    if q_tab == "results":
        tab_results, tab_overview, tab_failure, tab_decision, tab_sensitivity, tab_realdata = st.tabs([
            "📊 Results",
            "📖 Overview",
            "💥 Failure Study",
            "🗺️ Decision Map",
            "🛡️ Sensitivity",
            "📁 Real Data",
        ])
    elif q_tab == "failure":
        tab_failure, tab_overview, tab_results, tab_decision, tab_sensitivity, tab_realdata = st.tabs([
            "💥 Failure Study",
            "📖 Overview",
            "📊 Results",
            "🗺️ Decision Map",
            "🛡️ Sensitivity",
            "📁 Real Data",
        ])
    elif q_tab == "decision":
        tab_decision, tab_overview, tab_results, tab_failure, tab_sensitivity, tab_realdata = st.tabs([
            "🗺️ Decision Map",
            "📖 Overview",
            "📊 Results",
            "💥 Failure Study",
            "🛡️ Sensitivity",
            "📁 Real Data",
        ])
    elif q_tab == "sensitivity":
        tab_sensitivity, tab_overview, tab_results, tab_failure, tab_decision, tab_realdata = st.tabs([
            "🛡️ Sensitivity",
            "📖 Overview",
            "📊 Results",
            "💥 Failure Study",
            "🗺️ Decision Map",
            "📁 Real Data",
        ])
    elif q_tab == "realdata":
        tab_realdata, tab_overview, tab_results, tab_failure, tab_decision, tab_sensitivity = st.tabs([
            "📁 Real Data",
            "📖 Overview",
            "📊 Results",
            "💥 Failure Study",
            "🗺️ Decision Map",
            "🛡️ Sensitivity",
        ])
    else:
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
        # Visual Match Layout: Left controls column (NO CARD), Right dark green card
        col_ctrl, col_display = st.columns([4.2, 7.8], gap="large")

        with col_ctrl:
            # Pill-style preset row
            st.caption("Benchmark Presets")
            p_cols = st.columns(3)
            if p_cols[0].button("Easy RCT", key="cp_easy", use_container_width=True, help="c=0, overlap=0.9"):
                apply_preset("Easy (Ideal RCT)")
                st.rerun()
            if p_cols[1].button("Low Ovl", key="cp_low", use_container_width=True, help="c=0, overlap=0.15"):
                apply_preset("Low Overlap (Heavy Tails)")
                st.rerun()
            if p_cols[2].button("Trap", key="cp_trap", use_container_width=True, help="c=0.8, overlap=0.7"):
                apply_preset("Hidden Confounder (Trap)")
                st.rerun()

            st.caption(f"Active Scenario: **{st.session_state.preset_name}**")

            # Confounding Strength (26px label, #f0f1f7 input box with number & unit, grey-purple slider)
            st.markdown(
                f"""
                <div class="left-controls-label">Confounding Strength</div>
                <div class="custom-param-box">
                    <span class="param-val">{st.session_state.confounding:.2f}</span>
                    <span class="param-unit">c (hidden weight)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            confounding = st.slider(
                "Confounding Strength (c)",
                min_value=0.0,
                max_value=1.0,
                value=float(st.session_state.confounding),
                step=0.05,
                key="slider_confounding",
                label_visibility="collapsed",
                help="Hidden confounder U shifts logging policy and treatment effect; estimators cannot observe U.",
            )
            st.session_state.confounding = confounding

            # Overlap Level (26px label, #f0f1f7 input box with number & unit, grey-purple slider)
            st.markdown(
                f"""
                <div class="left-controls-label">Overlap Level</div>
                <div class="custom-param-box">
                    <span class="param-val">{st.session_state.overlap:.2f}</span>
                    <span class="param-unit">α (propensity overlap)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            overlap = st.slider(
                "Overlap Level (α)",
                min_value=0.05,
                max_value=1.0,
                value=float(st.session_state.overlap),
                step=0.05,
                key="slider_overlap",
                label_visibility="collapsed",
                help="Controls propensity overlap. Low values force logging policy to be near-deterministic, inflating weights.",
            )
            st.session_state.overlap = overlap

            # Sample Size (26px label, #f0f1f7 input box with number & unit, grey-purple slider)
            st.markdown(
                f"""
                <div class="left-controls-label">Sample Size</div>
                <div class="custom-param-box">
                    <span class="param-val">{st.session_state.n_samples:,}</span>
                    <span class="param-unit">n (logged interactions)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            n_samples = st.slider(
                "Sample Size (n)",
                min_value=500,
                max_value=20000,
                value=int(st.session_state.n_samples),
                step=500,
                key="slider_n",
                label_visibility="collapsed",
                help="Number of historical logged interactions (X, A, R) generated from logging policy π₀.",
            )
            st.session_state.n_samples = n_samples

            # Reward Noise (26px label, #f0f1f7 input box with number & unit, grey-purple slider)
            st.markdown(
                f"""
                <div class="left-controls-label">Reward Noise</div>
                <div class="custom-param-box">
                    <span class="param-val">{st.session_state.noise:.2f}</span>
                    <span class="param-unit">σ (std dev)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            noise = st.slider(
                "Reward Noise (σ)",
                min_value=0.1,
                max_value=1.0,
                value=float(st.session_state.noise),
                step=0.05,
                key="slider_noise",
                label_visibility="collapsed",
                help="Standard deviation of Gaussian noise added to the reward outcome.",
            )
            st.session_state.noise = noise

            # Random Seed
            st.markdown(
                """
                <div class="left-controls-label">Inference Controls</div>
                """,
                unsafe_allow_html=True,
            )
            c_seed, c_btn = st.columns([2, 1])
            with c_seed:
                seed_val = st.number_input(
                    "Random Seed",
                    value=int(st.session_state.seed),
                    step=1,
                    key="input_seed",
                )
                st.session_state.seed = seed_val
            with c_btn:
                st.write("")
                st.write("")
                if st.button("🎲 New", key="btn_new_seed", use_container_width=True):
                    st.session_state.seed = int(np.random.randint(1, 999999))
                    st.rerun()

            b_resamples = st.select_slider(
                "Bootstrap Resamples (B)",
                options=[30, 50, 100, 200],
                value=int(st.session_state.b_resamples),
                key="slider_b",
                help="Resamples for 95% percentile confidence intervals. Adaptive when n > 10,000.",
            )
            st.session_state.b_resamples = b_resamples

        with col_display:
            # Inference execution with progress bar
            with st.spinner("Computing policy values and 95% bootstrap intervals..."):
                prog_bar = st.progress(0, text="Simulating logged interactions...")
                prog_bar.progress(35, text="Estimating propensity scores & outcome regressions...")
                dataset, est_summary, boot_summary = run_cached_experiment(
                    n=st.session_state.n_samples,
                    confounding=st.session_state.confounding,
                    overlap=st.session_state.overlap,
                    noise=st.session_state.noise,
                    seed=st.session_state.seed,
                    b_resamples=st.session_state.b_resamples,
                )
                prog_bar.progress(100, text="Inference ready!")
                time.sleep(0.04)
                prog_bar.empty()

            # Find closest estimator
            errors = {
                name: abs(boot_summary.get(name).point_estimate - TRUE_INTERVENTIONAL_VALUE)
                for name in boot_summary.results
            }
            closest_estimator = min(errors, key=errors.get)

            naive_res = boot_summary.get("Naive")
            dr_res = boot_summary.get("Doubly Robust")

            # 1. Dark Green Card (#024526, 16px radius, 32px padding, huge white number, 3 mini cards, 16px bars)
            render_dark_green_results_card(
                naive_val=naive_res.point_estimate,
                dr_val=dr_res.point_estimate,
                true_val=TRUE_INTERVENTIONAL_VALUE,
                ess=est_summary.ess,
                max_weight=est_summary.max_weight,
                n=dataset.n,
            )

            # 2. Dynamic Key Insight Banner (reserved Orange accent for key causal warnings)
            render_insight_banner(
                confounding=st.session_state.confounding,
                overlap=st.session_state.overlap,
                closest_estimator=closest_estimator,
                ess_ratio=est_summary.ess / dataset.n,
            )

            # 4. Dot-and-Whisker Chart: Plain-English title "How far off is each method?"
            fig_ci = create_estimator_ci_chart(
                boot_summary=boot_summary,
                true_val=TRUE_INTERVENTIONAL_VALUE,
                is_dark=st.session_state.is_dark,
            )
            st.plotly_chart(fig_ci, use_container_width=True)

            # 5. Weight Distribution Diagnostic Chart
            fig_weights = create_weight_distribution_chart(
                weights=est_summary.weights,
                is_dark=st.session_state.is_dark,
            )
            st.plotly_chart(fig_weights, use_container_width=True)

            # 6. Estimator Scorecard Data Table & CSV Download
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
                    "Bias vs Target": f"{bias:+.4f}",
                    "Abs Error |V̂ - V*|": f"{abs_err:.4f}",
                    "Status": "Lowest Bias" if is_best else "Evaluated",
                })

            df_scorecard = pd.DataFrame(table_rows)
            st.dataframe(df_scorecard, use_container_width=True, hide_index=True)

            csv_buffer = io.StringIO()
            df_scorecard.to_csv(csv_buffer, index=False)
            st.download_button(
                label="📥 Download Scorecard CSV",
                data=csv_buffer.getvalue(),
                file_name=f"ope_lab_scorecard_c{st.session_state.confounding}_ovl{st.session_state.overlap}_n{dataset.n}.csv",
                mime="text/csv",
            )

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

    with tab_failure:
        st.markdown("### 💥 Failure Mode Deep Dive: Confounding vs. Overlap Breakdown")
        st.caption(
            "Off-policy evaluation relies on two core causal pillars: **Unconfoundedness** (no hidden factors) "
            "and **Positivity / Common Support** (logging policy explores all actions). Below, we systematically "
            "break each assumption in isolation across multiple Monte Carlo seeds."
        )

        st.markdown("---")
        st.markdown("#### 📈 Chart A: Error as Hidden Confounding Grows")
        st.caption(
            f"Evaluates all 6 estimators as confounding $c$ scales from 0.0 to 1.0 (30 seeds/level, "
            f"$n=5,000$, active overlap $\\alpha={st.session_state.overlap:.2f}$, noise $\\sigma={st.session_state.noise:.2f}$)."
        )

        col_metric, _ = st.columns([3, 7])
        with col_metric:
            selected_metric = st.radio(
                "Error Metric",
                options=["Absolute Bias", "Root Mean Squared Error (RMSE)"],
                horizontal=True,
                key="radio_failure_metric",
            )
        metric_key = "abs_bias" if selected_metric == "Absolute Bias" else "rmse"

        with st.spinner("Computing confounding sweep across 11 levels and 30 seeds..."):
            prog_c = st.progress(0, text="Simulating confounding sweep across 30 seeds per point...")
            prog_c.progress(40, text="Fitting propensity and regression models...")
            conf_sweep = run_cached_confounding_sweep(
                n_seeds=30,
                n_samples=5000,
                overlap=st.session_state.overlap,
                noise=st.session_state.noise,
                base_seed=st.session_state.seed,
            )
            prog_c.progress(100, text="Sweep complete!")
            time.sleep(0.02)
            prog_c.empty()

        fig_conf = create_confounding_sweep_chart(
            conf_sweep,
            metric=metric_key,
            is_dark=st.session_state.is_dark,
        )
        st.plotly_chart(fig_conf, use_container_width=True)
        render_failure_takeaway_a(conf_sweep)

        st.markdown("---")
        st.markdown("#### 🌊 Chart B: What Low Overlap Does (Unconfounded $c = 0$)")
        st.caption(
            f"Evaluates all estimators as overlap $\\alpha$ varies from 0.1 to 1.0 at $c = 0.0$ (30 seeds/level, "
            f"$n=5,000$, noise $\\sigma={st.session_state.noise:.2f}$). Displays estimator RMSE and median Kish Effective Sample Size."
        )

        with st.spinner("Computing overlap sweep across 10 levels and 30 seeds..."):
            prog_o = st.progress(0, text="Simulating overlap sweep across 30 seeds per point...")
            prog_o.progress(40, text="Evaluating importance weights and Kish ESS...")
            ovl_sweep = run_cached_overlap_sweep(
                n_seeds=30,
                n_samples=5000,
                confounding=0.0,
                noise=st.session_state.noise,
                base_seed=st.session_state.seed,
            )
            prog_o.progress(100, text="Sweep complete!")
            time.sleep(0.02)
            prog_o.empty()

        fig_ovl = create_overlap_sweep_chart(
            ovl_sweep,
            is_dark=st.session_state.is_dark,
        )
        st.plotly_chart(fig_ovl, use_container_width=True)
        render_failure_takeaway_b(ovl_sweep)

    with tab_decision:
        st.markdown("### 🗺️ Estimator Decision Map (3×3 Phase Diagram)")
        st.caption(
            "Empirical 2D phase matrix across **Confounding** $c \\in \\{0.0, 0.5, 1.0\\}$ and "
            "**Overlap** $\\alpha \\in \\{0.2, 0.5, 0.9\\}$ across 20+ Monte Carlo seeds per cell ($n=5,000$). "
            "Winner selection is based strictly on lowest RMSE among valid OPE methods (Naive excluded). "
            "Cells where the top two estimators are within 10% of each other are classified as **Tie**. "
            "Whenever the best method's absolute bias exceeds 0.05, the honesty rule marks the cell "
            "**No Method Reliable**."
        )

        with st.spinner("Computing 3×3 decision matrix across 180 Monte Carlo replications..."):
            prog_d = st.progress(0, text="Evaluating 9 parameter cells across 20 seeds each...")
            prog_d.progress(50, text="Ranking estimators by RMSE and checking honesty tolerance...")
            dec_map = run_cached_decision_map(
                n_seeds=20,
                n_samples=5000,
                noise=st.session_state.noise,
                base_seed=st.session_state.seed,
            )
            prog_d.progress(100, text="Decision map ready!")
            time.sleep(0.02)
            prog_d.empty()

        render_decision_map_summary(dec_map)

        fig_map = create_decision_map_grid_chart(
            dec_map,
            is_dark=st.session_state.is_dark,
        )
        st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("#### 🔍 Interactive Cell Inspector")
        inspect_cols = st.columns([2, 2, 8])
        with inspect_cols[0]:
            sel_c = st.selectbox(
                "Confounding (c)",
                options=[0.0, 0.5, 1.0],
                format_func=lambda v: f"c = {v:.1f}",
                key="sel_cell_c",
            )
        with inspect_cols[1]:
            sel_ovl = st.selectbox(
                "Overlap (α)",
                options=[0.9, 0.5, 0.2],
                format_func=lambda v: f"α = {v:.1f}",
                key="sel_cell_ovl",
            )

        cell_data = dec_map.cells[(float(sel_c), float(sel_ovl))]
        cell_rows = []
        for est_name in ["Doubly Robust", "SNIPW", "IPW", "Direct Method", "Replay", "Naive"]:
            st_obj = cell_data.stats[est_name]
            is_win = est_name == cell_data.winner and not cell_data.is_unreliable
            cell_rows.append({
                "Estimator": f"★ {est_name}" if is_win else est_name,
                "Mean Estimate": f"{st_obj.mean_estimate:.4f}",
                "Bias vs V*": f"{st_obj.bias:+.4f}",
                "Abs Bias": f"{st_obj.abs_bias:.4f}",
                "Variance": f"{st_obj.variance:.6f}",
                "Std Error": f"{st_obj.std_err:.4f}",
                "RMSE": f"{st_obj.rmse:.4f}",
                "Status": "Winner" if is_win else ("Naive (Excluded)" if est_name == "Naive" else "Evaluated"),
            })
        st.dataframe(pd.DataFrame(cell_rows), use_container_width=True, hide_index=True)

    with tab_sensitivity:
        st.markdown("### 🛡️ Confounding Sensitivity Bounds (Marginal Sensitivity Model)")
        st.caption(
            "Quantifies how resilient the policy estimate is against potential unobserved confounding $U$. "
            "Under the marginal sensitivity model, an unmeasured confounder may shift the odds of treatment selection "
            "by at most an odds ratio $\\Lambda \\ge 1.0$. The shaded band shows worst-case bounds on the true policy value."
        )

        col_s1, _ = st.columns([3, 7])
        with col_s1:
            max_lam = st.slider(
                "Max Odds Ratio Bound (Λ)",
                min_value=1.5,
                max_value=4.0,
                value=3.0,
                step=0.25,
                key="slider_max_lambda",
                help="Maximum odds ratio distortion by which an unobserved confounder could sway treatment decisions.",
            )

        with st.spinner("Computing worst-case sensitivity bounds across sorted-reward prefix sums..."):
            prog_s = st.progress(0, text="Calculating worst-case bounds across odds ratios...")
            sens_res = run_cached_sensitivity(
                n=st.session_state.n_samples,
                confounding=st.session_state.confounding,
                overlap=st.session_state.overlap,
                noise=st.session_state.noise,
                seed=st.session_state.seed,
                max_lambda=float(max_lam),
            )
            prog_s.progress(100, text="Sensitivity bounds complete!")
            time.sleep(0.02)
            prog_s.empty()

        render_sensitivity_summary(sens_res)
        fig_sens = create_sensitivity_bounds_chart(sens_res, is_dark=st.session_state.is_dark)
        st.plotly_chart(fig_sens, use_container_width=True)

    with tab_realdata:
        st.markdown("### 📁 Real-World Benchmark: Open Bandit Dataset")
        st.caption(
            "Validation on large-scale real-world e-commerce recommendations (ZOZOTOWN). "
            "Examines how well off-policy estimators predict live on-policy click-through rate (CTR) "
            "under production distribution shift."
        )
        render_realdata_card()

    render_footer()


if __name__ == "__main__":
    main()
