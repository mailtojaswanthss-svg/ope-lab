"""Modern, presentation-ready UI Components for OPE Lab.

Provides:
- Hero section for the Overview tab with animated gradient mesh and headline:
  "Did the policy really work?"
- Calculator-style Results layout components:
  * Large headline result card highlighting Naive estimation error vs ground truth
  * Two sub-stat cards (Doubly Robust estimate & Weight Health with pill status badge)
- Key Insight Banner: Orange (#f97316) strictly reserved for key causal warnings
- 5-step interactive pipeline cards
- Mission control footer
"""

from __future__ import annotations

import streamlit as st

from ope.analysis import DecisionMapResult, SweepResult
from ope.realdata import (
    ZOZOTOWN_ALL_META,
    get_reference_zozotown_benchmark,
    is_obp_available,
)
from ope.sensitivity import SensitivityResult


def render_header() -> None:
    """Renders the top navigation brand header."""
    st.markdown(
        """
        <div class="mission-header" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div class="hero-badge">🛰️ PERCEPTRON HACKATHON 2026 • PROBLEM 3</div>
                <div class="brand-title">
                    OPE Lab <span class="brand-subtitle">| Off-Policy Evaluation Studio</span>
                </div>
            </div>
            <div style="font-size: 0.88rem; font-weight: 500;">
                Target: <code style="color:#0284c7; font-weight:700;">V*(π<sub>e</sub>) = 0.6798</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ribbed_hero_banner() -> None:
    """Renders the full-width banner with vertical ribbed-glass gradient.

    90deg linear gradient (#dfe0f7, #2f9be0, #0a86d4, #0c7a4c, #f06ab8, #f472b6, #0b5a2b)
    with repeating 28px vertical stripe overlay (rgba(255,255,255,.3) to transparent to rgba(0,0,0,.2)).
    Title "Off-Policy Evaluation Lab" in white DM Sans, weight 500, up to 104px, letter spacing -0.035em, centered,
    with a 26px subtitle underneath.
    """
    st.markdown(
        """
        <div class="hero-ribbed-banner">
            <h1 class="hero-ribbed-title">Off-Policy Evaluation Lab</h1>
            <p class="hero-ribbed-subtitle">
                Did the policy actually work, or did it just look like it did?
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview_hero() -> None:
    """Renders the Hero section at the top of the Overview tab with animated gradient mesh."""
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-badge">CAUSAL DECISION INTELLIGENCE</div>
            <h1 class="hero-title">Did the policy really work?</h1>
            <p class="hero-subtitle">
                Off-policy evaluation separates genuine causal lift from observational illusion
                using logged historical data—before you risk budget, brand, or live production traffic.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_health_pill(ess_ratio: float) -> tuple[str, str]:
    """Returns CSS class and pill status label for Kish's Effective Sample Size ratio."""
    if ess_ratio >= 0.30:
        return "pill-healthy", "HEALTHY"
    elif ess_ratio >= 0.10:
        return "pill-caution", "CAUTION"
    else:
        return "pill-unreliable", "UNRELIABLE"


def render_calculator_headline_card(
    naive_val: float,
    true_val: float,
    naive_ci: tuple[float, float],
) -> None:
    """Renders the large headline result card showing the error of Naive vs the truth in large glowing type."""
    naive_bias = naive_val - true_val
    naive_abs_err = abs(naive_bias)
    naive_pct = (naive_abs_err / true_val) * 100 if true_val > 0 else 0.0
    sign = "+" if naive_bias >= 0 else ""

    glow_color = "rgba(239, 68, 68, 0.4)" if naive_abs_err > 0.05 else "rgba(16, 185, 129, 0.4)"
    num_color = "#ef4444" if naive_abs_err > 0.05 else "#10b981"

    st.markdown(
        f"""
        <div class="headline-result-card">
            <div class="headline-label">Naive Observational Bias (Selection Illusion)</div>
            <div class="headline-number" style="color: {num_color}; text-shadow: 0 0 24px {glow_color};">
                {sign}{naive_bias:.4f} <span style="font-size: 1.8rem; font-weight:700; color:#94a3b8;">({naive_pct:.1f}% error)</span>
            </div>
            <div class="headline-desc">
                Naive estimate observed in raw logs: <b style="color:inherit; font-weight:750;">{naive_val:.4f}</b> 
                [95% CI: {naive_ci[0]:.3f}, {naive_ci[1]:.3f}] vs True Interventional Target: 
                <b style="color:#22d3ee;">{true_val:.4f}</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_calculator_stat_cards(
    dr_val: float,
    true_val: float,
    dr_ci: tuple[float, float],
    ess: float,
    max_weight: float,
    n: int,
) -> None:
    """Renders two smaller stat cards beneath the headline number."""
    dr_bias = dr_val - true_val
    dr_sign = "+" if dr_bias >= 0 else ""
    dr_color = "#10b981" if abs(dr_bias) < 0.05 else "#22d3ee"

    ess_ratio = ess / n if n > 0 else 0.0
    chip_class, chip_label = get_health_pill(ess_ratio)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Doubly Robust (DR) Estimate</div>
                <div class="stat-value" style="color: {dr_color};">{dr_val:.4f}</div>
                <div class="stat-subtext">
                    Bias: <b>{dr_sign}{dr_bias:.4f}</b> • 95% CI: [{dr_ci[0]:.3f}, {dr_ci[1]:.3f}]
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span class="stat-label">Weight Diagnostics</span>
                    <span class="pill-chip {chip_class}">{chip_label}</span>
                </div>
                <div class="stat-value">{ess:,.0f} <span style="font-size:0.92rem; font-weight:500; color:#94a3b8;">ESS ({ess_ratio:.1%})</span></div>
                <div class="stat-subtext">
                    Max Weight: <b>{max_weight:.2f}</b> • Sample size: {n:,}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dark_green_results_card(
    naive_val: float,
    dr_val: float,
    true_val: float,
    ess: float,
    max_weight: float,
    n: int,
) -> None:
    """Renders the right-column dark green card (#024526, 16px radius, 32px padding).

    Contains:
    - 25px heading: "Policy Value & Selection Bias"
    - Huge white number (weight 800): showing Naive bias vs target
    - Three darker mini cards (#032817) with uppercase white labels and values in:
      * Sky (#38bdf8): Doubly Robust estimate
      * Pink (#ff6dbe): Naive observation
      * Amber (#fbbf24): Kish Effective Sample Size
    - Thin 16px bars in pink and amber:
      * Pink bar (#ff6dbe): Selection error share
      * Amber bar (#fbbf24): Effective sample size retention
    """
    naive_bias = naive_val - true_val
    sign = "+" if naive_bias >= 0 else ""
    ess_ratio = ess / n if n > 0 else 0.0

    # Thin bar proportions (clamped between 2% and 100% for display)
    bias_pct = min(100.0, max(4.0, (abs(naive_bias) / true_val) * 100.0 if true_val > 0 else 0.0))
    ess_pct = min(100.0, max(2.0, ess_ratio * 100.0))

    card_html = (
        f'<div class="dark-green-card">'
        f'<div class="green-card-heading">Policy Value &amp; Selection Bias</div>'
        f'<div class="huge-white-number">{sign}{naive_bias:.4f}</div>'
        f'<div class="green-card-desc">'
        f'Naive raw log estimate: <b>{naive_val:.4f}</b> vs True Interventional Target <b>{true_val:.4f}</b>. '
        f'Off-policy estimators correct for propensity skew and confounding.'
        f'</div>'
        f'<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 22px;">'
        f'<div class="mini-card-dark">'
        f'<div class="mini-card-label">DOUBLY ROBUST (DR)</div>'
        f'<div class="mini-card-val-sky">{dr_val:.4f}</div>'
        f'<div class="mini-card-sub">Error vs target: {abs(dr_val - true_val):.4f}</div>'
        f'</div>'
        f'<div class="mini-card-dark">'
        f'<div class="mini-card-label">NAIVE OBSERVATION</div>'
        f'<div class="mini-card-val-pink">{naive_val:.4f}</div>'
        f'<div class="mini-card-sub">Bias: {sign}{naive_bias:.4f}</div>'
        f'</div>'
        f'<div class="mini-card-dark">'
        f'<div class="mini-card-label">KISH EFFECTIVE SAMPLE</div>'
        f'<div class="mini-card-val-amber">{ess:,.0f}</div>'
        f'<div class="mini-card-sub">{ess_ratio:.1%} retention • Max W: {max_weight:.1f}</div>'
        f'</div>'
        f'</div>'
        f'<div class="thin-bar-label">'
        f'<span>Selection Error Share (Naive vs True Target)</span>'
        f'<span>{bias_pct:.1f}%</span>'
        f'</div>'
        f'<div class="thin-bar-container">'
        f'<div class="thin-bar-pink" style="width: {bias_pct:.1f}%;"></div>'
        f'</div>'
        f'<div class="thin-bar-label">'
        f'<span>Effective Sample Size Retention (Overlap Health)</span>'
        f'<span>{ess_pct:.1f}%</span>'
        f'</div>'
        f'<div class="thin-bar-container">'
        f'<div class="thin-bar-amber" style="width: {ess_pct:.1f}%;"></div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_insight_banner(
    confounding: float,
    overlap: float,
    closest_estimator: str,
    ess_ratio: float,
) -> None:
    """Renders the contextual dynamic takeaway banner.

    MANDATORY RULE: If confounding > 0.2, explicitly warn that all estimators can
    be biased due to unobserved confounding using the reserved Orange accent.
    """
    if confounding > 0.2:
        title = f"⚠️ Unobserved Confounding Active (Confounding = {confounding:.2f})"
        message = (
            "A hidden factor <code>U</code> directly influences treatment selection and modifies "
            "treatment effect. <b>Because no estimator can observe <code>U</code>, all standard OPE "
            "estimators (including Doubly Robust, SNIPW, and IPW) are subject to omitted-variable bias.</b> "
            "Doubly Robust protects against misspecification of observed models under unconfoundedness, "
            "but <i>cannot fix hidden confounding</i>. Explore the <b>Sensitivity</b> tab to evaluate "
            "worst-case bounds under unobserved confounding."
        )
    elif overlap < 0.25:
        title = f"⚠️ Severe Overlap Deficit (Overlap = {overlap:.2f})"
        message = (
            f"The logging policy is near-deterministic in parts of the context space. "
            f"Standard IPW exhibits severe weight spikes and wide confidence intervals. "
            f"<b>Self-Normalized IPW (SNIPW)</b> and <b>Doubly Robust (DR)</b> stabilize variance, "
            f"yielding an Effective Sample Size ratio of {ess_ratio:.1%}."
        )
    else:
        title = f"✅ Unconfounded Regime with Positive Overlap (c = {confounding:.2f}, α = {overlap:.2f})"
        message = (
            f"Both key causal assumptions hold: no unobserved confounders (c = 0) and strong common support. "
            f"Under this setting, <b>Doubly Robust</b> and <b>IPW</b> are asymptotically unbiased. "
            f"<b>{closest_estimator}</b> achieved the closest empirical value to the true interventional target "
            f"in this dataset."
        )

    st.markdown(
        f"""
        <div class="insight-box">
            <div style="font-weight: 750; font-size: 1.02rem; margin-bottom: 6px;">{title}</div>
            <div>{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview_tab() -> None:
    """Renders the Overview tab featuring the Hero, Coupon Story, and 5-Step Pipeline."""
    render_overview_hero()

    st.markdown("### 🏷️ The Intuition: The Coupon Dilemma")
    st.markdown(
        r"""
        Imagine an e-commerce platform running an old promotion policy:
        > **Old Logging Policy ($\pi_0$):** High-spending customers with high loyalty scores ($X > 0$) 
        > were almost always sent a 20% discount coupon ($A = 1$). Low-spending visitors rarely received one.

        Now, marketing proposes a **New Target Policy ($\pi_e$):**
        > **New Target Policy ($\pi_e$):** Send a coupon strictly to users with positive engagement ($X > 0$).
        
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
            <div class="glass-card" style="padding: 18px;">
                <div style="font-size:0.75rem; font-weight:800; color:#22d3ee; margin-bottom:4px;">STEP 1</div>
                <div style="font-weight: 750; font-size: 0.95rem; margin-bottom: 6px;">Logged Data</div>
                <div style="font-size: 0.82rem; color: #94a3b8; line-height:1.4;">
                    Observe historical interactions (X, A, R) recorded under logging policy π₀.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            """
            <div class="glass-card" style="padding: 18px;">
                <div style="font-size:0.75rem; font-weight:800; color:#22d3ee; margin-bottom:4px;">STEP 2</div>
                <div style="font-weight: 750; font-size: 0.95rem; margin-bottom: 6px;">Propensity Model</div>
                <div style="font-size: 0.82rem; color: #94a3b8; line-height:1.4;">
                    Estimate ê(X) = P(A=1|X) using fast logistic regression.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p3:
        st.markdown(
            """
            <div class="glass-card" style="padding: 18px;">
                <div style="font-size:0.75rem; font-weight:800; color:#22d3ee; margin-bottom:4px;">STEP 3</div>
                <div style="font-weight: 750; font-size: 0.95rem; margin-bottom: 6px;">Weight Health</div>
                <div style="font-size: 0.82rem; color: #94a3b8; line-height:1.4;">
                    Calculate W = πₑ/ê(X), monitor Kish's ESS and weight spikes.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p4:
        st.markdown(
            """
            <div class="glass-card" style="padding: 18px;">
                <div style="font-size:0.75rem; font-weight:800; color:#22d3ee; margin-bottom:4px;">STEP 4</div>
                <div style="font-weight: 750; font-size: 0.95rem; margin-bottom: 6px;">Outcome Model</div>
                <div style="font-size: 0.82rem; color: #94a3b8; line-height:1.4;">
                    Fit Q̂(X,A) to predict expected rewards and enable Doubly Robust.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with p5:
        st.markdown(
            """
            <div class="glass-card" style="padding: 18px;">
                <div style="font-size:0.75rem; font-weight:800; color:#22d3ee; margin-bottom:4px;">STEP 5</div>
                <div style="font-weight: 750; font-size: 0.95rem; margin-bottom: 6px;">Evaluation & CI</div>
                <div style="font-size: 0.82rem; color: #94a3b8; line-height:1.4;">
                    Estimate V̂(πₑ) with 95% bootstrap confidence intervals.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_failure_takeaway_a(sweep_res: SweepResult) -> None:
    """Renders plain-English takeaway for Chart A computed from real sweep results."""
    pt_c0 = sweep_res.points[0]
    candidates = ["Doubly Robust", "SNIPW", "Direct Method", "IPW", "Replay"]
    best_c0 = min(candidates, key=lambda k: pt_c0.estimator_stats[k].rmse)
    best_c0_rmse = pt_c0.estimator_stats[best_c0].rmse

    # Confounding levels where bias exceeds 0.05
    cross_points: dict[str, float | None] = {}
    for name in ["Doubly Robust", "SNIPW", "IPW", "Direct Method", "Naive"]:
        cross_val = next(
            (pt.parameter_value for pt in sweep_res.points if pt.estimator_stats[name].abs_bias > 0.05),
            None,
        )
        cross_points[name] = cross_val

    dr_cross_str = f"c ≥ {cross_points['Doubly Robust']:.1f}" if cross_points["Doubly Robust"] is not None else "c > 1.0"
    naive_cross_str = f"c ≥ {cross_points['Naive']:.1f}" if cross_points["Naive"] is not None else "c > 1.0"

    content = (
        f'<div class="insight-box" style="margin-top: 14px;">'
        f'<div style="font-weight: 750; font-size: 1.02rem; margin-bottom: 6px;">'
        f'💡 Empirical Takeaway: The Unobserved Confounding Barrier'
        f'</div>'
        f'<div>'
        f'• <b>Ideal Conditions (c = 0.0):</b> <b>{best_c0}</b> achieves the lowest error '
        f'(RMSE = <code>{best_c0_rmse:.4f}</code>). Because treatment assignment depends solely on observed X, '
        f'propensity weighting and outcome modeling are asymptotically unbiased.<br>'
        f'• <b>Confounder Breakdown:</b> As hidden factor <code>U</code> strengthens, <b>all standard OPE estimators fail</b> '
        f'because no model can adjust for unobserved selection. Absolute bias exceeds the 0.05 critical tolerance '
        f'at <b>{dr_cross_str}</b> for Doubly Robust (and {naive_cross_str} for Naive). '
        f'<i>Doubly Robust cannot fix hidden confounding.</i>'
        f'</div>'
        f'</div>'
    )
    st.markdown(content, unsafe_allow_html=True)


def render_failure_takeaway_b(sweep_res: SweepResult) -> None:
    """Renders plain-English takeaway for Chart B computed from real sweep results."""
    pt_low = sweep_res.points[0]  # overlap = 0.1
    pt_high = sweep_res.points[-1]  # overlap = 1.0

    ipw_rmse_low = pt_low.estimator_stats["IPW"].rmse
    dr_rmse_low = pt_low.estimator_stats["Doubly Robust"].rmse
    ratio_low = ipw_rmse_low / dr_rmse_low if dr_rmse_low > 0 else 1.0

    content = (
        f'<div class="insight-box" style="margin-top: 14px;">'
        f'<div style="font-weight: 750; font-size: 1.02rem; margin-bottom: 6px;">'
        f'💡 Empirical Takeaway: Overlap Dynamics &amp; Kish Effective Sample Size'
        f'</div>'
        f'<div>'
        f'• <b>Effective Sample Size (ESS):</b> Across the sweep, median Kish ESS ranges from '
        f'<b>{pt_high.median_ess:,.0f}</b> (at α = 1.0, where logging exploration is maximal) to '
        f'<b>{pt_low.median_ess:,.0f}</b> (at α = 0.1).<br>'
        f'• <b>Estimator Robustness:</b> Under unconfounded logging (c = 0.0), <b>Doubly Robust</b> maintains '
        f'low variance across all overlap levels (RMSE = <code>{dr_rmse_low:.4f}</code> at α = 0.1). '
        f'IPW achieves RMSE = <code>{ipw_rmse_low:.4f}</code> (ratio to DR: {ratio_low:.2f}×). '
        f'Self-Normalized IPW (SNIPW) and Doubly Robust provide bounded variance guarantees.'
        f'</div>'
        f'</div>'
    )
    st.markdown(content, unsafe_allow_html=True)


def render_decision_map_summary(decision_map: DecisionMapResult) -> None:
    """Renders the decision map legend, honesty notes, and cell inspector guidance."""
    unreliable_count = sum(1 for cell in decision_map.cells.values() if cell.is_unreliable)
    tie_count = sum(1 for cell in decision_map.cells.values() if cell.is_tie and not cell.is_unreliable)
    dr_count = sum(
        1
        for cell in decision_map.cells.values()
        if cell.winner == "Doubly Robust" and not cell.is_unreliable and not cell.is_tie
    )

    badge_html = (
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; '
        f'gap:12px; background:rgba(0,0,0,0.15); padding:12px 18px; border-radius:12px; margin-bottom:18px;">'
        f'<div>'
        f'<span style="font-size:0.85rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em;">'
        f'PHASE DIAGRAM LEGEND:</span> &nbsp; '
        f'<span style="display:inline-block; padding:3px 10px; border-radius:6px; background:#059669; color:#ffffff; font-size:12px; font-weight:700;">🟩 Doubly Robust ({dr_count})</span> &nbsp;'
        f'<span style="display:inline-block; padding:3px 10px; border-radius:6px; background:#2563eb; color:#ffffff; font-size:12px; font-weight:700;">🟦 Tie within 10% ({tie_count})</span> &nbsp;'
        f'<span style="display:inline-block; padding:3px 10px; border-radius:6px; background:#475569; color:#ffffff; font-size:12px; font-weight:700;">⬛ No Method Reliable ({unreliable_count})</span>'
        f'</div>'
        f'<div style="font-size:0.82rem; color:#94a3b8;">'
        f'🔬 <i>Averaged over many random seeds. Simulated data.</i>'
        f'</div>'
        f'</div>'
    )
    st.markdown(badge_html, unsafe_allow_html=True)


def render_sensitivity_summary(sens_res: SensitivityResult) -> None:
    """Renders prominent summary callout for the marginal sensitivity analysis."""
    if sens_res.lambda_star is not None:
        if sens_res.covers_at_one:
            badge_title = "🛡️ Nominal Coverage Confirmed (Λ* = 1.00)"
            box_style = "border-left: 4px solid #10b981; background: rgba(16, 185, 129, 0.08);"
            body_text = (
                f"Even under zero unobserved confounding (odds ratio bound <code>Λ = 1.00</code>), "
                f"the SNIPW estimate (<code>{sens_res.point_estimate:.4f}</code>) already encompasses the true "
                f"interventional target (<code>0.6798</code>). The policy's value cannot be trivially explained "
                f"away by mild selection bias."
            )
        else:
            pct_distortion = (sens_res.lambda_star - 1.0) * 100.0
            badge_title = f"🛡️ Sensitivity Breakdown Threshold: Λ* = {sens_res.lambda_star:.2f}"
            box_style = "border-left: 4px solid #f97316; background: rgba(249, 115, 22, 0.08);"
            body_text = (
                f"An unobserved confounder <code>U</code> would need to distort the odds of treatment selection by at "
                f"least <b>Λ* = {sens_res.lambda_star:.2f}</b> (a <b>{pct_distortion:.0f}% odds shift</b>) to expand "
                f"the worst-case policy value bounds enough to cover the true interventional target <code>V* = 0.6798</code>.<br>"
                f"If domain experts believe unmeasured variables cannot swing treatment odds by {sens_res.lambda_star:.2f}×, "
                f"the qualitative conclusion of the policy evaluation remains robust."
            )
    else:
        badge_title = "⚠️ High Vulnerability: Λ* > 3.00"
        box_style = "border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.08);"
        body_text = (
            f"Even under a severe <code>3.0×</code> odds ratio distortion (<code>Λ = 3.00</code>), the worst-case "
            f"bounds <code>[{sens_res.lower_bounds[-1]:.4f}, {sens_res.upper_bounds[-1]:.4f}]</code> do NOT cover "
            f"the true target value <code>0.6798</code>. This indicates extreme observational bias in the current data regime."
        )

    html = (
        f'<div class="insight-box" style="{box_style} margin-top: 14px; margin-bottom: 20px;">'
        f'<div style="font-weight: 750; font-size: 1.05rem; margin-bottom: 8px;">{badge_title}</div>'
        f'<div style="line-height: 1.5; font-size: 0.92rem;">{body_text}</div>'
        f'<div style="margin-top: 10px; font-size: 0.8rem; color: #94a3b8;">'
        f'🏷️ <i>Method: {sens_res.method_label}. Computed over matched rows with prefix-sum sorted-reward optimization.</i>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_realdata_card() -> None:
    """Renders the Open Bandit Dataset real-world benchmark card."""
    obp_installed = is_obp_available()
    obp_status_badge = (
        '<span style="padding: 2px 8px; border-radius: 6px; background: #059669; color: white; font-size: 11px; font-weight: 700;">OBP Active</span>'
        if obp_installed
        else '<span style="padding: 2px 8px; border-radius: 6px; background: #475569; color: white; font-size: 11px; font-weight: 700;">OBP Fallback Mode</span>'
    )

    st.markdown(
        f"""
        <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 24px; margin-bottom: 24px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom: 12px;">
                <div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc;">
                    📁 {ZOZOTOWN_ALL_META.campaign_name}
                </div>
                <div>{obp_status_badge}</div>
            </div>
            <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.5; margin-bottom: 16px;">
                Reference dataset collected on Japan's largest fashion e-commerce platform (ZOZOTOWN). 
                Logs over 12,000,000 user interactions comparing a uniform random logging policy 
                against an online Bernoulli Thompson Sampling (BTS) evaluation policy.
            </div>
            <div style="display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px;">
                <div style="background: rgba(255, 255, 255, 0.05); padding: 8px 14px; border-radius: 8px; font-size: 0.82rem;">
                    <b>Actions (Items):</b> {ZOZOTOWN_ALL_META.num_actions} items
                </div>
                <div style="background: rgba(255, 255, 255, 0.05); padding: 8px 14px; border-radius: 8px; font-size: 0.82rem;">
                    <b>Context Features:</b> {ZOZOTOWN_ALL_META.context_dim} dimensions
                </div>
                <div style="background: rgba(255, 255, 255, 0.05); padding: 8px 14px; border-radius: 8px; font-size: 0.82rem;">
                    <b>Reward:</b> {ZOZOTOWN_ALL_META.reward_metric}
                </div>
                <div style="background: rgba(255, 255, 255, 0.05); padding: 8px 14px; border-radius: 8px; font-size: 0.82rem;">
                    <b>Citation:</b> {ZOZOTOWN_ALL_META.published_reference}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 📊 Empirical Estimator Comparison (ZOZOTOWN Published Benchmark)")
    st.caption("Evaluates target Bernoulli Thompson Sampling (BTS) policy using only logged interactions from the Random policy.")

    benchmark_df = get_reference_zozotown_benchmark()
    st.dataframe(benchmark_df, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="insight-box" style="margin-top: 16px;">
            <b>💡 Benchmark Finding:</b> On real ZOZOTOWN production traffic, <b>Doubly Robust</b> (0.0053 CTR) 
            most accurately predicts the live on-policy ground truth (0.0054 CTR), achieving +51.4% predicted lift 
            over the random baseline (actual live lift: +54.3%). Naive observational comparison severely overestimates 
            performance (+77.1% lift) due to platform selection dynamics.
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
