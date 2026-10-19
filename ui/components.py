"""UI Components for OPE Lab.

Provides reusable presentation components:
- Mission-control header
- 4 key metric cards (Ground Truth, Naive, Doubly Robust, Weight Health)
- Weight Health status badge (Healthy / Caution / Unreliable)
- Contextual Insight Banner (with mandatory unobserved confounding warning)
- Overview Tab (The Coupon Story + 5-step pipeline diagram)
- Mission control footer
"""

from __future__ import annotations

import streamlit as st


def render_header() -> None:
    """Renders the futuristic mission-control header."""
    st.markdown(
        """
        <div class="mission-header">
            <div class="header-logo">
                <span>🛰️ PERCEPTRON HACKATHON 2026</span>
                <span>•</span>
                <span>PROBLEM 3</span>
            </div>
            <h1 class="header-title">OPE Lab: Off-Policy Evaluation Studio</h1>
            <p class="header-subtitle">
                Did the policy actually work, or did it just look like it did?
                Evaluate new decision policies using logged data before risking live production traffic.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_health_badge(ess_ratio: float) -> tuple[str, str]:
    """Returns CSS class and status label for Kish's Effective Sample Size ratio."""
    if ess_ratio >= 0.30:
        return "chip-healthy", "HEALTHY"
    elif ess_ratio >= 0.10:
        return "chip-caution", "CAUTION"
    else:
        return "chip-unreliable", "UNRELIABLE"


def render_metric_cards(
    true_val: float,
    naive_val: float,
    naive_ci: tuple[float, float],
    dr_val: float,
    dr_ci: tuple[float, float],
    ess: float,
    max_weight: float,
    n: int,
) -> None:
    """Renders the 4 key glass-card metrics at the top of the Results tab."""
    col1, col2, col3, col4 = st.columns(4)

    naive_bias = naive_val - true_val
    naive_sign = "+" if naive_bias >= 0 else ""
    dr_bias = dr_val - true_val
    dr_sign = "+" if dr_bias >= 0 else ""

    ess_ratio = ess / n if n > 0 else 0.0
    chip_class, chip_label = get_health_badge(ess_ratio)

    with col1:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="glass-metric-label">Target Interventional Value</div>
                <div class="glass-metric-value" style="color: #22d3ee;">{true_val:.4f}</div>
                <div class="glass-metric-delta" style="color: #94a3b8;">
                    Ground Truth V*(π<sub>e</sub>)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        naive_color = "#f87171" if abs(naive_bias) > 0.05 else "#34d399"
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="glass-metric-label">Naive Logging Value</div>
                <div class="glass-metric-value" style="color: {naive_color};">{naive_val:.4f}</div>
                <div class="glass-metric-delta" style="color: {naive_color};">
                    Bias: {naive_sign}{naive_bias:.4f} <span style="color:#64748b;">[{naive_ci[0]:.3f}, {naive_ci[1]:.3f}]</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        dr_color = "#34d399" if abs(dr_bias) < 0.05 else "#fbbf24"
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="glass-metric-label">Doubly Robust (DR)</div>
                <div class="glass-metric-value" style="color: {dr_color};">{dr_val:.4f}</div>
                <div class="glass-metric-delta" style="color: {dr_color};">
                    Bias: {dr_sign}{dr_bias:.4f} <span style="color:#64748b;">[{dr_ci[0]:.3f}, {dr_ci[1]:.3f}]</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="glass-metric-label" style="display:flex; justify-content:space-between; align-items:center;">
                    <span>Weight Diagnostics</span>
                    <span class="status-chip {chip_class}">{chip_label}</span>
                </div>
                <div class="glass-metric-value" style="font-size: 1.55rem;">
                    {ess:.0f} <span style="font-size:0.95rem; color:#94a3b8; font-weight:500;">ESS ({ess_ratio:.1%})</span>
                </div>
                <div class="glass-metric-delta" style="color: #cbd5e1;">
                    Max Weight: <b>{max_weight:.2f}</b> <span style="color:#64748b;">(n = {n:,})</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_insight_banner(
    confounding: float,
    overlap: float,
    closest_estimator: str,
    ess_ratio: float,
) -> None:
    """Renders the contextual dynamic takeaway banner.

    MANDATORY RULE: If confounding > 0.2, explicitly warn that all estimators can
    be biased due to unobserved confounding. Never claim Doubly Robust fixes it.
    """
    if confounding > 0.2:
        title = f"⚠️ Unobserved Confounding Active (Confounding = {confounding:.2f})"
        message = (
            "A hidden factor <code>U</code> directly influences treatment selection and modifies "
            "treatment effect. <b>Because no estimator can observe <code>U</code>, all standard OPE "
            "estimators (including Doubly Robust, SNIPW, and IPW) are subject to omitted-variable bias.</b> "
            "Doubly Robust protects against misspecification of observed models under unconfoundedness, "
            "but <i>cannot fix hidden confounding</i>. Explore the <b>Sensitivity</b> tab to calculate "
            "the critical Rosenbaum sensitivity bound Γ."
        )
        border_color = "#f97316"
    elif overlap < 0.25:
        title = f"⚠️ Severe Overlap Deficit (Overlap = {overlap:.2f})"
        message = (
            f"The logging policy is near-deterministic in parts of the context space. "
            f"Standard IPW suffers from extreme weight spikes and explosive variance. "
            f"<b>Self-Normalized IPW (SNIPW)</b> and <b>Doubly Robust (DR)</b> stabilize variance, "
            f"as reflected in Kish's ESS ({ess_ratio:.1%}). Notice the widened confidence interval on IPW."
        )
        border_color = "#eab308"
    else:
        title = f"✅ Unconfounded Regime with Positive Overlap (c = {confounding:.2f}, α = {overlap:.2f})"
        message = (
            f"Both key causal assumptions hold: no unobserved confounders (c = 0) and strong common support. "
            f"Under this setting, <b>Doubly Robust</b> and <b>IPW</b> are asymptotically unbiased. "
            f"<b>{closest_estimator}</b> achieved the closest empirical value to the true interventional target "
            f"in this dataset."
        )
        border_color = "#22d3ee"

    st.markdown(
        f"""
        <div class="insight-box" style="border-left-color: {border_color};">
            <div style="font-weight: 700; font-size: 1.02rem; margin-bottom: 4px;">{title}</div>
            <div>{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview_tab() -> None:
    """Renders the Overview tab featuring the Coupon Story and 5-Step Pipeline."""
    st.markdown("### 🏷️ The Intuition: The Coupon Story")
    st.markdown(
        r"""
        Imagine an e-commerce platform running an old promotion policy:
        > **Old Policy (Logging $\pi_0$):** High-spending customers with high loyalty scores ($X > 0$) 
        > were almost always sent a 20% discount coupon ($A = 1$). Low-spending visitors rarely received one.

        Now, marketing proposes a **New Policy ($\pi_e$)**:
        > **New Policy ($\pi_e$):** Send a coupon strictly to users with positive engagement ($X > 0$).
        
        **Why can't you just look at average revenue among coupon recipients?**
        - **The Naive Trap:** Customers who got coupons were already your most loyal, high-spending buyers! 
          Comparing coupon recipients to non-recipients mixes the *coupon's actual causal lift* with 
          *pre-existing customer behavior*. That is **confounding bias**.
        - **The A/B Testing Dilemma:** Testing unproven policies live on real customers burns marketing budget, 
          churns users, and risks revenue.
        - **The OPE Solution:** Off-Policy Evaluation (OPE) mathematically reweights historical interactions 
          to answer: *"What would our revenue have been if we had run the new policy all along?"*
        """
    )

    st.markdown("---")
    st.markdown("### 🔄 The 5-Step Off-Policy Evaluation Pipeline")

    p1, p2, p3, p4, p5 = st.columns(5)
    with p1:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">1</div>
                <div style="font-weight: 700; font-size: 0.9rem; margin-bottom: 6px;">Logged Data</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">
                    Observe historical interactions (X, A, R) recorded under logging policy π₀.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">2</div>
                <div style="font-weight: 700; font-size: 0.9rem; margin-bottom: 6px;">Propensity Model</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">
                    Estimate ê(X) = P(A=1|X) using fast logistic regression.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p3:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">3</div>
                <div style="font-weight: 700; font-size: 0.9rem; margin-bottom: 6px;">Weight Diagnostics</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">
                    Calculate W = πₑ(A|X)/ê(X), track Kish's ESS and maximum weight spikes.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p4:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">4</div>
                <div style="font-weight: 700; font-size: 0.9rem; margin-bottom: 6px;">Outcome Model</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">
                    Fit Q̂(X,A) to predict expected rewards and enable Doubly Robust augmentation.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p5:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-num">5</div>
                <div style="font-weight: 700; font-size: 0.9rem; margin-bottom: 6px;">Evaluation & CI</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">
                    Estimate V̂(πₑ) with 95% bootstrap confidence intervals for risk-aware decisions.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_footer() -> None:
    """Renders the subtle application footer."""
    st.markdown(
        """
        <div class="mission-footer">
            <b>OPE Lab</b> • Perceptron Hackathon 2026 • Off-Policy Evaluation & Causal Decision Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )
