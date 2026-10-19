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

from ope.analysis import DecisionMapResult, SweepResult
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


def create_confounding_sweep_chart(
    sweep_res: SweepResult,
    metric: str = "rmse",
    is_dark: bool = True,
) -> go.Figure:
    """Builds Chart A: Error as hidden confounding grows (0 to 1).

    Args:
        sweep_res: SweepResult containing points for confounding 0 to 1.
        metric: 'rmse' (Root Mean Squared Error) or 'abs_bias' (Absolute Bias).
        is_dark: Whether to render in dark or light theme.

    Returns:
        Plotly Figure with one line per estimator, consistent colors, and distinct symbols.
    """
    text_color = "#f8fafc" if is_dark else "#0f172a"
    grid_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.08)"
    transparent_bg = "rgba(0, 0, 0, 0)"

    metric_series = sweep_res.get_metric_series(metric)
    x_vals = sweep_res.parameter_values

    metric_label = "Root Mean Squared Error (RMSE)" if metric == "rmse" else "Absolute Bias |E[V̂] - V*|"
    chart_title = (
        f"<b>Chart A: {metric_label} as Hidden Confounding Grows</b><br>"
        f"<span style='font-size:12px; font-weight:400; color:{'#94a3b8' if is_dark else '#64748b'};'>"
        f"Averaged over {sweep_res.n_seeds} Monte Carlo seeds per level (n={sweep_res.n_samples:,})"
        f"</span>"
    )

    fig = go.Figure()

    estimator_names = [
        "Naive",
        "Replay",
        "Direct Method",
        "IPW",
        "SNIPW",
        "Doubly Robust",
    ]

    for name in estimator_names:
        y_vals = metric_series[name]
        color = ESTIMATOR_COLORS.get(name, "#38bdf8")
        symbol = ESTIMATOR_SYMBOLS.get(name, "circle")

        hover_template = (
            f"<b>{name}</b><br>"
            "Confounding (c): %{x:.2f}<br>"
            f"{metric.upper()}: %{{y:.4f}}<extra></extra>"
        )

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines+markers",
                name=name,
                line={"color": color, "width": 2.5},
                marker={"size": 8, "symbol": symbol, "color": color},
                hovertemplate=hover_template,
            )
        )

    # 0.05 Bias Tolerance reference threshold
    if metric == "abs_bias":
        fig.add_hline(
            y=0.05,
            line_dash="dot",
            line_color="#f97316",
            line_width=1.8,
            annotation_text="Critical Bias Threshold (0.05)",
            annotation_position="top left",
            annotation_font={"color": "#f97316", "size": 11},
        )

    fig.update_layout(
        title={
            "text": chart_title,
            "font": {"color": text_color, "size": 15},
            "x": 0.01,
            "y": 0.96,
        },
        paper_bgcolor=transparent_bg,
        plot_bgcolor=transparent_bg,
        font={"color": text_color, "family": "Inter, sans-serif"},
        xaxis={
            "title": "<b>Hidden Confounding Strength (c)</b>",
            "gridcolor": grid_color,
            "zeroline": False,
            "tickmode": "linear",
            "tick0": 0.0,
            "dtick": 0.1,
            "tickfont": {"color": text_color, "size": 11},
        },
        yaxis={
            "title": f"<b>{metric_label}</b>",
            "gridcolor": grid_color,
            "zeroline": False,
            "tickfont": {"color": text_color, "size": 11},
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1.0,
            "font": {"size": 11},
        },
        margin={"l": 50, "r": 40, "t": 75, "b": 45},
        height=400,
    )

    return fig


def create_overlap_sweep_chart(
    sweep_res: SweepResult,
    is_dark: bool = True,
) -> go.Figure:
    """Builds Chart B: What low overlap does (overlap 0.1 to 1.0 at confounding 0).

    Shows RMSE per estimator on primary y-axis, and median Effective Sample Size (ESS)
    on secondary y-axis.

    Args:
        sweep_res: SweepResult containing points for overlap 0.1 to 1.0.
        is_dark: Whether to render in dark or light theme.

    Returns:
        Plotly Figure with dual-axis visualization.
    """
    text_color = "#f8fafc" if is_dark else "#0f172a"
    grid_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.08)"
    transparent_bg = "rgba(0, 0, 0, 0)"

    rmse_series = sweep_res.get_metric_series("rmse")
    ess_vals = sweep_res.get_ess_series()
    x_vals = sweep_res.parameter_values

    fig = go.Figure()

    estimator_names = [
        "Doubly Robust",
        "SNIPW",
        "IPW",
        "Direct Method",
        "Replay",
    ]

    # Primary axis: RMSE lines per estimator
    for name in estimator_names:
        y_vals = rmse_series[name]
        color = ESTIMATOR_COLORS.get(name, "#38bdf8")
        symbol = ESTIMATOR_SYMBOLS.get(name, "circle")

        fig.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines+markers",
                name=f"{name} (RMSE)",
                line={"color": color, "width": 2.5},
                marker={"size": 7, "symbol": symbol, "color": color},
                hovertemplate=f"<b>{name}</b><br>Overlap (α): %{{x:.2f}}<br>RMSE: %{{y:.4f}}<extra></extra>",
                yaxis="y1",
            )
        )

    # Secondary axis: Median Kish Effective Sample Size (ESS)
    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=ess_vals,
            mode="lines+markers",
            name="Median Kish ESS",
            line={"color": "#fbbf24", "width": 2, "dash": "dash"},
            marker={"size": 6, "symbol": "diamond", "color": "#fbbf24"},
            hovertemplate="Overlap (α): %{x:.2f}<br>Median ESS: %{y:,.0f}<extra></extra>",
            yaxis="y2",
        )
    )

    chart_title = (
        "<b>Chart B: What Low Overlap Does (Unconfounded c = 0)</b><br>"
        f"<span style='font-size:12px; font-weight:400; color:{'#94a3b8' if is_dark else '#64748b'};'>"
        f"RMSE per estimator vs. Kish Effective Sample Size across {sweep_res.n_seeds} Monte Carlo seeds"
        "</span>"
    )

    fig.update_layout(
        title={
            "text": chart_title,
            "font": {"color": text_color, "size": 15},
            "x": 0.01,
            "y": 0.96,
        },
        paper_bgcolor=transparent_bg,
        plot_bgcolor=transparent_bg,
        font={"color": text_color, "family": "Inter, sans-serif"},
        xaxis={
            "title": "<b>Propensity Overlap Level (α)</b>",
            "gridcolor": grid_color,
            "zeroline": False,
            "tickmode": "linear",
            "tick0": 0.1,
            "dtick": 0.1,
            "tickfont": {"color": text_color, "size": 11},
        },
        yaxis={
            "title": "<b>RMSE (Root Mean Squared Error)</b>",
            "gridcolor": grid_color,
            "zeroline": False,
            "tickfont": {"color": text_color, "size": 11},
        },
        yaxis2={
            "title": "<b>Median Kish ESS</b>",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
            "tickfont": {"color": "#fbbf24", "size": 11},
            "title_font": {"color": "#fbbf24"},
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1.0,
            "font": {"size": 11},
        },
        margin={"l": 50, "r": 60, "t": 75, "b": 45},
        height=400,
    )

    return fig


def create_decision_map_grid_chart(
    decision_map: DecisionMapResult,
    is_dark: bool = True,
) -> go.Figure:
    """Builds an interactive 3x3 phase diagram for the Decision Map tab.

    Cells are colored by winner status:
    - Doubly Robust / SNIPW / Direct Method / Replay: distinct colors
    - Tie: Blue/indigo
    - No method reliable: Muted gray

    Args:
        decision_map: DecisionMapResult containing the 3x3 matrix.
        is_dark: Whether to render in dark or light theme.

    Returns:
        Plotly Figure with interactive heatmap cells and rich hover statistics.
    """
    text_color = "#f8fafc" if is_dark else "#0f172a"
    transparent_bg = "rgba(0, 0, 0, 0)"

    # X axis: Confounding levels [0.0, 0.5, 1.0]
    # Y axis: Overlap levels [0.9, 0.5, 0.2] (high to low)
    c_levels = decision_map.confounding_levels
    ovl_levels = decision_map.overlap_levels

    # Status to numeric code for colorscale
    # 0: No method reliable (muted gray)
    # 1: Tie (soft blue)
    # 2: Replay (purple)
    # 3: Direct Method (amber)
    # 4: IPW (pink)
    # 5: SNIPW (teal)
    # 6: Doubly Robust (emerald green)
    def status_to_code(label: str) -> int:
        if "No method reliable" in label:
            return 0
        elif "Tie" in label:
            return 1
        elif "Replay" in label:
            return 2
        elif "Direct Method" in label:
            return 3
        elif "IPW" in label:
            return 4
        elif "SNIPW" in label:
            return 5
        elif "Doubly Robust" in label:
            return 6
        return 0

    z_matrix: list[list[int]] = []
    text_matrix: list[list[str]] = []
    hover_matrix: list[list[str]] = []

    for alpha in ovl_levels:
        z_row: list[int] = []
        text_row: list[str] = []
        hover_row: list[str] = []

        for c in c_levels:
            cell = decision_map.cells[(c, alpha)]
            code = status_to_code(cell.label)
            z_row.append(code)

            # Cell display text
            if cell.is_unreliable:
                display_txt = (
                    "<b>NO METHOD RELIABLE</b><br>"
                    "<span style='font-size:11px;'>Bias &gt; 0.05 (Broken by Confounder)</span>"
                )
            elif cell.is_tie:
                display_txt = (
                    f"<b>TIE</b><br>"
                    f"<span style='font-size:11px;'>{cell.winner} ≈ {cell.runner_up}</span><br>"
                    f"<span style='font-size:10px;'>RMSE: {cell.winner_rmse:.4f}</span>"
                )
            else:
                display_txt = (
                    f"<b>{cell.winner.upper()}</b><br>"
                    f"<span style='font-size:11px;'>Lowest RMSE: {cell.winner_rmse:.4f}</span><br>"
                    f"<span style='font-size:10px;'>Bias: {cell.winner_abs_bias:.4f}</span>"
                )
            text_row.append(display_txt)

            # Rich hover text with table of all estimators
            table_lines = [
                f"<b>Cell: Confounding c = {c:.2f}, Overlap α = {alpha:.2f}</b>",
                f"<b>Status: {cell.label}</b> (n={cell.n_samples:,}, seeds={cell.n_seeds})",
                f"Median Kish ESS: {cell.median_ess:,.0f}",
                "───────────────────────────────",
                "<b>Estimator Performance Breakdown:</b>",
            ]
            for est_name in ["Doubly Robust", "SNIPW", "IPW", "Direct Method", "Replay", "Naive"]:
                stat = cell.stats[est_name]
                prefix = "★ " if est_name == cell.winner and not cell.is_unreliable else "  "
                table_lines.append(
                    f"{prefix}<b>{est_name}</b>: RMSE = {stat.rmse:.4f} | Bias = {stat.bias:+.4f} | Mean = {stat.mean_estimate:.4f}"
                )
            hover_row.append("<br>".join(table_lines) + "<extra></extra>")

        z_matrix.append(z_row)
        text_matrix.append(text_row)
        hover_matrix.append(hover_row)

    # Discrete colorscale for the 7 categories
    # 0: Slate/gray (#475569)
    # 1: Blue (#2563eb)
    # 2: Purple (#9333ea)
    # 3: Amber (#d97706)
    # 4: Pink (#ec4899)
    # 5: Teal (#0d9488)
    # 6: Emerald (#059669)
    discrete_colors = [
        "#475569",  # 0: No method reliable
        "#2563eb",  # 1: Tie
        "#9333ea",  # 2: Replay
        "#d97706",  # 3: Direct Method
        "#ec4899",  # 4: IPW
        "#0d9488",  # 5: SNIPW
        "#059669",  # 6: Doubly Robust
    ]

    # Map discrete colors to normalized values [0, 1]
    colorscale = []
    n_colors = len(discrete_colors)
    for idx, col in enumerate(discrete_colors):
        low = idx / n_colors
        high = (idx + 1) / n_colors
        colorscale.append([low, col])
        colorscale.append([high, col])

    fig = go.Figure(
        data=go.Heatmap(
            z=z_matrix,
            x=[f"c = {c:.1f}" for c in c_levels],
            y=[f"α = {alpha:.1f}" for alpha in ovl_levels],
            text=text_matrix,
            texttemplate="%{text}",
            textfont={"size": 13, "color": "#ffffff"},
            customdata=hover_matrix,
            hovertemplate="%{customdata}",
            colorscale=colorscale,
            zmin=0,
            zmax=n_colors,
            showscale=False,
        )
    )

    chart_title = (
        "<b>3×3 Estimator Decision Matrix (Lowest RMSE)</b><br>"
        f"<span style='font-size:12px; font-weight:400; color:{'#94a3b8' if is_dark else '#64748b'};'>"
        f"Averaged over {decision_map.n_seeds} random seeds per cell (n={decision_map.n_samples:,}). "
        "Naive excluded. Gray = bias &gt; 0.05 (unreliable due to confounding)."
        "</span>"
    )

    fig.update_layout(
        title={
            "text": chart_title,
            "font": {"color": text_color, "size": 15},
            "x": 0.01,
            "y": 0.96,
        },
        paper_bgcolor=transparent_bg,
        plot_bgcolor=transparent_bg,
        font={"color": text_color, "family": "Inter, sans-serif"},
        xaxis={
            "title": "<b>Hidden Confounding Strength (c)</b>",
            "side": "bottom",
            "tickfont": {"color": text_color, "size": 12, "family": "DM Sans"},
        },
        yaxis={
            "title": "<b>Propensity Overlap Level (α)</b>",
            "tickfont": {"color": text_color, "size": 12, "family": "DM Sans"},
        },
        margin={"l": 60, "r": 40, "t": 75, "b": 50},
        height=450,
    )

    return fig

