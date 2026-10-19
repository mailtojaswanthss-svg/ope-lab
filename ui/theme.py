"""Futuristic mission-control styling and theme manager for OPE Lab.

Supports dynamic Dark and Light themes with glassmorphism, glowing borders,
CSS count-up pulses, and responsive layout styling.
"""

from __future__ import annotations

import streamlit as st


def get_theme_css(is_dark: bool = True) -> str:
    """Returns custom CSS for either futuristic Dark mode or crisp Light mode."""
    if is_dark:
        card_bg = "rgba(17, 28, 51, 0.75)"
        card_border = "rgba(34, 211, 238, 0.25)"
        card_hover_border = "rgba(34, 211, 238, 0.6)"
        card_shadow = "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
        text_primary = "#f8fafc"
        text_secondary = "#94a3b8"
        metric_glow = "text-shadow: 0 0 14px rgba(34, 211, 238, 0.45);"
        banner_bg = "rgba(249, 115, 22, 0.12)"
        banner_border = "#f97316"
        banner_text = "#ffedd5"
    else:
        card_bg = "#ffffff"
        card_border = "#e2e8f0"
        card_hover_border = "#0f766e"
        card_shadow = "0 2px 8px rgba(0, 0, 0, 0.05)"
        text_primary = "#0f172a"
        text_secondary = "#64748b"
        metric_glow = ""
        banner_bg = "#fff7ed"
        banner_border = "#f97316"
        banner_text = "#7c2d12"

    return f"""
    <style>
        /* Global CSS and Base Font */
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: {text_primary};
        }}

        /* Subtle Fade In Animation for Charts and Content */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes pulseGlow {{
            0% {{ transform: scale(0.98); opacity: 0.9; }}
            50% {{ transform: scale(1.02); opacity: 1; }}
            100% {{ transform: scale(1.0); opacity: 1; }}
        }}

        .stPlotlyChart {{
            animation: fadeIn 0.35s ease-in-out;
        }}

        /* Mission Control Header */
        .mission-header {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
            border: 1px solid rgba(34, 211, 238, 0.3);
            border-radius: 12px;
            padding: 22px 26px;
            margin-bottom: 22px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        }}
        .header-logo {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(34, 211, 238, 0.15);
            color: #22d3ee;
            border: 1px solid rgba(34, 211, 238, 0.4);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .header-title {{
            font-size: 2.1rem;
            font-weight: 800;
            color: #ffffff;
            margin: 0 0 4px 0;
            letter-spacing: -0.02em;
        }}
        .header-subtitle {{
            font-size: 1.05rem;
            color: #cbd5e1;
            margin: 0;
            font-weight: 400;
        }}

        /* Futuristic Glass Cards */
        .glass-card {{
            background: {card_bg};
            border: 1px solid {card_border};
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 18px 20px;
            box-shadow: {card_shadow};
            transition: all 0.2s ease-in-out;
            animation: fadeIn 0.3s ease;
        }}
        .glass-card:hover {{
            border-color: {card_hover_border};
            transform: translateY(-2px);
        }}
        .glass-metric-label {{
            font-size: 0.82rem;
            font-weight: 600;
            color: {text_secondary};
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 4px;
        }}
        .glass-metric-value {{
            font-size: 1.85rem;
            font-weight: 800;
            color: {text_primary};
            line-height: 1.1;
            margin-bottom: 6px;
            {metric_glow}
            animation: pulseGlow 0.4s ease-out;
        }}
        .glass-metric-delta {{
            font-size: 0.85rem;
            font-weight: 600;
        }}

        /* Status Chips */
        .status-chip {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }}
        .chip-healthy {{
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid #10b981;
        }}
        .chip-caution {{
            background: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            border: 1px solid #f59e0b;
        }}
        .chip-unreliable {{
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid #ef4444;
        }}

        /* Key Insight Banner */
        .insight-box {{
            background: {banner_bg};
            border-left: 5px solid {banner_border};
            border-radius: 6px;
            padding: 14px 18px;
            margin: 16px 0 20px 0;
            color: {banner_text};
            font-size: 0.95rem;
            line-height: 1.5;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        /* Pipeline Step Card */
        .step-card {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 8px;
            padding: 16px;
            height: 100%;
        }}
        .step-num {{
            display: inline-block;
            background: #0284c7;
            color: #ffffff;
            font-size: 0.75rem;
            font-weight: 700;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            text-align: center;
            line-height: 22px;
            margin-bottom: 8px;
        }}

        /* Footer */
        .mission-footer {{
            text-align: center;
            font-size: 0.82rem;
            color: #64748b;
            padding: 24px 0 10px 0;
            border-top: 1px solid {card_border};
            margin-top: 36px;
        }}
    </style>
    """


def inject_theme(is_dark: bool = True) -> None:
    """Injects the theme CSS into the current Streamlit page."""
    st.markdown(get_theme_css(is_dark), unsafe_allow_html=True)
