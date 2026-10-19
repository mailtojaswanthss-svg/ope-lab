"""Interactive Plotly visualizations for OPE Lab.

Features:
- Dot-and-whisker plot with 95% bootstrap confidence intervals for all 6 estimators
- High-contrast semantic palette with distinct marker shapes for color-blind accessibility
- Ground truth reference line (V* = 0.6798) with direct label
- Gold halo highlight around the top-performing estimator
- Plain-English chart title: "How far off is each method?"
- Weight distribution histogram with log/linear scale and ESS annotation
- Full theme awareness (dark mission control / clean light) and transparent background
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from ope.bootstrap import BootstrapSummary
from ope.simulator import TRUE_INTERVENTIONAL_VALUE

# Semantic color definitions
ESTIMATOR_COLORS: dict[str, str] = {
    "Naive": "#ef4444",  # Red
    "Replay": "#f59e0b",  # Amber
    "Direct Method": "#3b82f6",  # Blue
    "IPW": "#a855f7",  # Purple
    "SNIPW": "#2dd4bf",  # Teal
    "Doubly Robust": "#10b981",  # Emerald Green
}

# Distinct marker symbols for color-blind accessibility
ESTIMATOR_SYMBOLS: dict[str, str] = {
    "Naive": "circle",
    "Replay": "square",
    "Direct Method": "diamond",
    "IPW": "triangle-up",
    "SNIPW": "cross",
    "Doubly Robust": "star",
}


def create_estimator_ci_chart(
    boot_summary: BootstrapSummary,
    true_val: float = TRUE_INTERVENTIONAL_VALUE,
    is_dark: bool = True,
) -> go.Figure:
    """Builds an interactive dot-and-whisker chart comparing all 6 OPE estimators.

    Args:
        boot_summary: BootstrapSummary containing point estimates and 95% CIs.
        true_val: Target interventional ground truth value.
        is_dark: Whether to render in dark or light theme.

    Returns:
        Plotly Figure ready for st.plotly_chart.
    """
    estimator_names = [
        "Naive",
        "Replay",
        "Direct Method",
        "IPW",
        "SNIPW",
        "Doubly Robust",
    ]

    # Find the estimator closest to the true value
    errors = {
        name: abs(boot_summary.get(name).point_estimate - true_val)
        for name in estimator_names
    }
    closest_name = min(errors, key=errors.get)

    fig = go.Figure()

    # Base theme styling: transparent background and thin grid lines
    text_color = "#f8fafc" if is_dark else "#0f172a"
    grid_color = "rgba(255, 255, 255, 0.06)" if is_dark else "rgba(0, 0, 0, 0.06)"
    transparent_bg = "rgba(0, 0, 0, 0)"

    for name in estimator_names:
        res = boot_summary.get(name)
        color = ESTIMATOR_COLORS.get(name, "#38bdf8")
        symbol = ESTIMATOR_SYMBOLS.get(name, "circle")
        is_winner = name == closest_name

        err_minus = res.point_estimate - res.ci_lower
        err_plus = res.ci_upper - res.point_estimate
        bias = res.point_estimate - true_val
        bias_str = f"+{bias:.4f}" if bias >= 0 else f"{bias:.4f}"

        # Add gold halo marker if closest
        if is_winner:
            fig.add_trace(
                go.Scatter(
                    x=[name],
                    y=[res.point_estimate],
                    mode="markers",
                    marker={
                        "size": 26,
                        "color": "rgba(234, 179, 8, 0.22)",
                        "symbol": "circle",
                        "line": {"color": "#eab308", "width": 2.5},
                    },
                    name="Closest to Truth",
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        # Main point and CI bar
        hover_text = (
            f"<b>{name}</b><br>"
            f"Estimate: {res.point_estimate:.4f}<br>"
            f"95% CI: [{res.ci_lower:.4f}, {res.ci_upper:.4f}]<br>"
            f"Std Error: ±{res.std_err:.4f}<br>"
            f"Bias vs Target V*: {bias_str}<br>"
            + ("<b>★ Lowest Bias in Sample</b>" if is_winner else "")
        )

        fig.add_trace(
            go.Scatter(
                x=[name],
                y=[res.point_estimate],
                error_y={
                    "type": "data",
                    "symmetric": False,
                    "array": [err_plus],
                    "arrayminus": [err_minus],
                    "color": color,
                    "thickness": 2.5,
                    "width": 8,
                },
                mode="markers",
                marker={
                    "size": 13,
                    "color": color,
                    "symbol": symbol,
                    "line": {
                        "color": "#ffffff" if is_dark else "#0f172a",
                        "width": 1.5,
                    },
                },
                name=name,
                text=hover_text,
                hoverinfo="text",
                showlegend=False,
            )
        )

    # Reference line for Ground Truth V* with clear direct label
    fig.add_hline(
        y=true_val,
        line_dash="dash",
        line_color="#22d3ee",
        line_width=2,
        annotation_text=f"Ground Truth Target V* = {true_val:.4f}",
        annotation_position="top right",
        annotation_font={"color": "#22d3ee", "size": 11, "family": "Inter, sans-serif"},
    )

    fig.update_layout(
        title={
            "text": "<b>How far off is each method? (95% Bootstrap CI vs Target)</b>",
            "font": {"color": text_color, "size": 15},
            "x": 0.01,
            "y": 0.96,
        },
        paper_bgcolor=transparent_bg,
        plot_bgcolor=transparent_bg,
        font={"color": text_color, "family": "Inter, sans-serif"},
        xaxis={
            "title": "<b>Estimator</b>",
            "showgrid": False,
            "zeroline": False,
            "tickfont": {"color": text_color, "size": 11},
        },
        yaxis={
            "title": "<b>Estimated Policy Value V̂(π<sub>e</sub>)</b>",
            "gridcolor": grid_color,
            "zeroline": False,
            "tickfont": {"color": text_color, "size": 11},
        },
        margin={"l": 50, "r": 40, "t": 50, "b": 40},
        height=380,
    )

    return fig


def create_weight_distribution_chart(
    weights: np.ndarray,
    is_dark: bool = True,
) -> go.Figure:
    """Builds a diagnostic distribution plot of importance weights W_i = pi_e / e(X).

    Args:
        weights: Array of importance sampling weights.
        is_dark: Whether to render in dark or light theme.

    Returns:
        Plotly Figure showing weight distribution and diagnostic cutoffs.
    """
    text_color = "#f8fafc" if is_dark else "#0f172a"
    grid_color = "rgba(255, 255, 255, 0.06)" if is_dark else "rgba(0, 0, 0, 0.06)"
    transparent_bg = "rgba(0, 0, 0, 0)"

    fig = go.Figure()

    # Filter non-zero weights for clarity
    active_weights = weights[weights > 0]
    if len(active_weights) == 0:
        active_weights = np.array([0.0])

    p99 = float(np.percentile(active_weights, 99))
    max_w = float(np.max(active_weights))

    fig.add_trace(
        go.Histogram(
            x=active_weights,
            nbinsx=40,
            marker={
                "color": "rgba(34, 211, 238, 0.65)",
                "line": {"color": "#22d3ee", "width": 1},
            },
            name="Importance Weights",
            hoverinfo="x+y",
        )
    )

    fig.add_vline(
        x=p99,
        line_dash="dot",
        line_color="#2dd4bf",
        line_width=1.5,
        annotation_text=f"99th %ile: {p99:.2f}",
        annotation_position="top right",
        annotation_font={"color": "#2dd4bf", "size": 10},
    )

    fig.update_layout(
        title={
            "text": f"<b>Importance Weight Diagnostics (Max: {max_w:.2f})</b>",
            "font": {"color": text_color, "size": 13},
            "x": 0.01,
            "y": 0.96,
        },
        paper_bgcolor=transparent_bg,
        plot_bgcolor=transparent_bg,
        font={"color": text_color, "family": "Inter, sans-serif"},
        xaxis={
            "title": "Weight W<sub>i</sub> = π<sub>e</sub>(A<sub>i</sub>|X<sub>i</sub>) / ê(X<sub>i</sub>)",
            "gridcolor": grid_color,
            "zeroline": False,
            "tickfont": {"color": text_color, "size": 10},
        },
        yaxis={
            "title": "Count",
            "gridcolor": grid_color,
            "zeroline": False,
            "tickfont": {"color": text_color, "size": 10},
        },
        margin={"l": 40, "r": 30, "t": 45, "b": 35},
        height=260,
        showlegend=False,
    )

    return fig
