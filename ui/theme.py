"""Futuristic, accessible design system and theme manager for OPE Lab.

Features:
- Animated gradient mesh hero for the Overview tab (deep navy to violet to teal, CSS-only)
- Calculator-style layout cards with 16-20px rounded corners and 8px spacing scale
- High-contrast WCAG AA typography and dark/light modes
- Pill-style buttons and status badges with focus/hover feedback
- Strict palette: Orange (#f97316) reserved solely for key causal insights;
  all other accents use navy, cyan (#22d3ee), teal (#2dd4bf), and emerald (#10b981).
"""

from __future__ import annotations

import streamlit as st


def get_theme_css(is_dark: bool = True) -> str:
    """Returns custom CSS for either futuristic Dark mode or crisp Light mode."""
    if is_dark:
        bg_color = "#0b1220"
        card_bg = "rgba(15, 23, 42, 0.78)"
        card_border = "rgba(34, 211, 238, 0.22)"
        card_hover_border = "rgba(34, 211, 238, 0.65)"
        card_shadow = "0 10px 30px -5px rgba(0, 0, 0, 0.45)"
        text_primary = "#f8fafc"
        text_secondary = "#94a3b8"
        text_muted = "#64748b"
        mesh_gradient = (
            "linear-gradient(-45deg, #0b1220, #1e1b4b, #0f172a, #042f2e, #134e4a, #0b1220)"
        )
        mesh_border = "rgba(34, 211, 238, 0.3)"
        mesh_shadow = "0 16px 40px -10px rgba(0, 0, 0, 0.6)"
        insight_bg = "rgba(249, 115, 22, 0.12)"
        insight_border = "#f97316"
        insight_text = "#ffedd5"
        calc_card_bg = "rgba(15, 23, 42, 0.88)"
    else:
        bg_color = "#f8fafc"
        card_bg = "#ffffff"
        card_border = "#cbd5e1"
        card_hover_border = "#0f766e"
        card_shadow = "0 8px 25px -4px rgba(15, 23, 42, 0.08)"
        text_primary = "#0f172a"
        text_secondary = "#475569"
        text_muted = "#64748b"
        mesh_gradient = (
            "linear-gradient(-45deg, #f0fdfa, #f8fafc, #ede9fe, #f1f5f9, #ccfbf1)"
        )
        mesh_border = "#cbd5e1"
        mesh_shadow = "0 10px 30px -6px rgba(15, 23, 42, 0.08)"
        insight_bg = "#fff7ed"
        insight_border = "#ea580c"
        insight_text = "#7c2d12"
        calc_card_bg = "#ffffff"

    return f"""
    <style>
        /* Base Global Typography & Contrast */
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: {text_primary};
        }}

        [data-testid="stAppViewContainer"] {{
            background-color: {bg_color};
        }}

        /* Universal WCAG AA High Contrast Text */
        h1, h2, h3, h4, h5, h6, .header-title, .calc-panel-title,
        [data-testid="stMarkdownContainer"] p, [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] *, label, .stSlider label,
        .mission-header, .mission-header div, .glass-card div,
        .stat-card .stat-value, .calc-panel div {{
            color: {text_primary} !important;
        }}

        .brand-title {{
            color: {text_primary} !important;
            font-size: 1.55rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }}
        .brand-subtitle {{
            color: {"#22d3ee" if is_dark else "#0284c7"};
            font-weight: 500;
            font-size: 1.1rem;
        }}

        /* Widget and Slider Labels Contrast */
        [data-testid="stSlider"] label p,
        [data-testid="stNumberInput"] label p,
        [data-testid="stSelectSlider"] label p,
        [data-testid="stWidgetLabel"] label p,
        .stSlider label, .stNumberInput label {{
            color: {text_primary} !important;
            font-weight: 600 !important;
        }}

        .headline-desc, .stat-subtext, .hero-subtitle,
        .headline-label, .stat-label, [data-testid="stMarkdownContainer"] caption,
        [data-testid="stMarkdownContainer"] small {{
            color: {text_secondary} !important;
        }}

        /* Streamlit Tabs Visibility */
        button[data-baseweb="tab"] p, button[data-baseweb="tab"] div {{
            color: {text_primary} !important;
            font-weight: 600 !important;
        }}

        /* Subtle Fade In Animation */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes meshShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        @keyframes pulseGlow {{
            0% {{ transform: scale(0.99); opacity: 0.95; }}
            50% {{ transform: scale(1.01); opacity: 1; }}
            100% {{ transform: scale(1.0); opacity: 1; }}
        }}

        .stPlotlyChart {{
            animation: fadeIn 0.3s ease-in-out;
        }}

        /* Hero Section with Soft Animated Gradient Mesh */
        .hero-section {{
            background: {mesh_gradient};
            background-size: 300% 300%;
            animation: meshShift 18s ease infinite;
            border: 1px solid {mesh_border};
            border-radius: 20px;
            padding: 36px 36px;
            margin-bottom: 24px;
            box-shadow: {mesh_shadow};
        }}
        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(34, 211, 238, 0.15);
            color: #22d3ee;
            border: 1px solid rgba(34, 211, 238, 0.4);
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}
        .hero-title {{
            font-size: 2.85rem;
            font-weight: 850;
            letter-spacing: -0.035em;
            line-height: 1.12;
            margin: 0 0 10px 0;
            color: {text_primary};
        }}
        .hero-subtitle {{
            font-size: 1.15rem;
            font-weight: 400;
            color: {text_secondary};
            line-height: 1.5;
            margin: 0;
            max-width: 820px;
        }}

        /* Mission Header */
        .mission-header {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 18px;
            padding: 20px 24px;
            margin-bottom: 20px;
            box-shadow: {card_shadow};
        }}

        /* Universal Glass Card (Consistent 8px scale & 18px corners) */
        .glass-card {{
            background: {card_bg};
            border: 1px solid {card_border};
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 18px;
            padding: 24px;
            box-shadow: {card_shadow};
            transition: all 0.2s ease-in-out;
            animation: fadeIn 0.3s ease;
            margin-bottom: 16px;
        }}
        .glass-card:hover {{
            border-color: {card_hover_border};
            transform: translateY(-2px);
        }}

        /* Streamlit Native Bordered Containers */
        [data-testid="stVerticalBlockBorderWrapper"] > div {{
            background: {card_bg} !important;
            border: 1px solid {card_border} !important;
            border-radius: 18px !important;
            padding: 20px 22px !important;
            box-shadow: {card_shadow} !important;
        }}

        /* Calculator Controls Card */
        .calc-panel {{
            background: {calc_card_bg};
            border: 1px solid {card_border};
            border-radius: 18px;
            padding: 24px;
            box-shadow: {card_shadow};
        }}
        .calc-panel-title {{
            font-size: 1.05rem;
            font-weight: 750;
            letter-spacing: -0.01em;
            margin-bottom: 16px;
            color: {text_primary};
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Big Headline Number Result Card */
        .headline-result-card {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 18px;
            padding: 28px 32px;
            box-shadow: {card_shadow};
            margin-bottom: 16px;
            animation: fadeIn 0.35s ease;
            position: relative;
            overflow: hidden;
        }}
        .headline-label {{
            font-size: 0.82rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {text_secondary};
            margin-bottom: 6px;
        }}
        .headline-number {{
            font-size: 3.3rem;
            font-weight: 900;
            letter-spacing: -0.035em;
            line-height: 1.05;
            margin: 0 0 8px 0;
            animation: pulseGlow 0.4s ease-out;
        }}
        .headline-desc {{
            font-size: 0.95rem;
            color: {text_secondary};
            font-weight: 450;
            line-height: 1.45;
        }}

        /* Sub-Stat Cards */
        .stat-card {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: {card_shadow};
            height: 100%;
        }}
        .stat-label {{
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {text_secondary};
            margin-bottom: 4px;
        }}
        .stat-value {{
            font-size: 1.65rem;
            font-weight: 800;
            line-height: 1.2;
            color: {text_primary};
            margin-bottom: 4px;
        }}
        .stat-subtext {{
            font-size: 0.82rem;
            color: {text_muted};
        }}

        /* Pill-style Status Chips */
        .pill-chip {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 14px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 750;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}
        .pill-healthy {{
            background: rgba(16, 185, 129, 0.18);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }}
        .pill-caution {{
            background: rgba(245, 158, 11, 0.18);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }}
        .pill-unreliable {{
            background: rgba(239, 68, 68, 0.18);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }}

        /* Pill-style Preset Button Row */
        .preset-pill-active {{
            background: linear-gradient(135deg, #0284c7 0%, #0f766e 100%) !important;
            color: #ffffff !important;
            border-color: #22d3ee !important;
            box-shadow: 0 0 12px rgba(34, 211, 238, 0.35) !important;
        }}

        /* Key Insight Box (Sole use of Orange accent) */
        .insight-box {{
            background: {insight_bg};
            border-left: 5px solid {insight_border};
            border-radius: 14px;
            padding: 16px 20px;
            margin: 16px 0 20px 0;
            color: {insight_text};
            font-size: 0.95rem;
            line-height: 1.5;
            box-shadow: {card_shadow};
        }}

        /* Responsive Mobile Tweaks */
        @media (max-width: 768px) {{
            .hero-title {{
                font-size: 2.1rem !important;
            }}
            .headline-number {{
                font-size: 2.5rem !important;
            }}
            .hero-section {{
                padding: 24px 20px !important;
            }}
            .headline-result-card {{
                padding: 20px 18px !important;
            }}
        }}

        /* Subtle Mission Footer */
        .mission-footer {{
            text-align: center;
            font-size: 0.82rem;
            color: {text_muted};
            padding: 24px 0 10px 0;
            border-top: 1px solid {card_border};
            margin-top: 36px;
        }}
    </style>
    """


def inject_theme(is_dark: bool = True) -> None:
    """Injects the theme CSS into the current Streamlit page."""
    st.markdown(get_theme_css(is_dark), unsafe_allow_html=True)
