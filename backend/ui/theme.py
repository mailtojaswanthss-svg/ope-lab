"""Visual theme matching the new visual spec:
- Page background white in light mode (#ffffff)
- Full-width hero banner with a vertical ribbed-glass gradient:
  90deg linear gradient (#dfe0f7, #2f9be0, #0a86d4, #0c7a4c, #f06ab8, #f472b6, #0b5a2b)
  with a repeating 28px vertical stripe overlay (rgba(255,255,255,.3) to transparent to rgba(0,0,0,.2)).
  Title "Off-Policy Evaluation Lab" in white DM Sans, weight 500, up to 104px, letter spacing -0.035em, centered,
  with a 26px subtitle underneath.
- Left column: no card. Large labels (26px, weight 500), light-gray (#f0f1f7) 8px-radius input boxes with number and unit,
  and grey-purple sliders (6px track #b3b8d3, 20px round thumb #68709a).
- Right column: dark green card (#024526, 16px radius, 32px padding), heading 25px, huge white number (weight 800),
  three darker mini cards (#032817) with uppercase white labels and values in amber #fbbf24, pink #ff6dbe, sky #38bdf8,
  and thin 16px bars in pink and amber.
"""

from __future__ import annotations

import streamlit as st


def get_theme_css(is_dark: bool = False) -> str:
    """Returns custom CSS adhering precisely to the visual specification."""
    page_bg = "#0b1220" if is_dark else "#ffffff"
    text_color = "#f8fafc" if is_dark else "#0f172a"
    sub_color = "#94a3b8" if is_dark else "#475569"

    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&display=swap');

        /* Global Canvas Background */
        html, body, [data-testid="stAppViewContainer"], [class*="css"] {{
            font-family: 'DM Sans', 'Inter', -apple-system, sans-serif;
            background-color: {page_bg} !important;
            color: {text_color};
        }}

        /* Full-Width Ribbed-Glass Gradient Hero Banner */
        .hero-ribbed-banner {{
            width: 100%;
            background-image:
                repeating-linear-gradient(
                    90deg,
                    rgba(255, 255, 255, 0.3) 0px,
                    transparent 14px,
                    rgba(0, 0, 0, 0.2) 28px
                ),
                linear-gradient(
                    90deg,
                    #dfe0f7 0%,
                    #2f9be0 16.6%,
                    #0a86d4 33.3%,
                    #0c7a4c 50%,
                    #f06ab8 66.6%,
                    #f472b6 83.3%,
                    #0b5a2b 100%
                );
            border-radius: 20px;
            padding: 56px 24px 60px 24px;
            margin-bottom: 28px;
            text-align: center;
            box-shadow: 0 14px 40px -10px rgba(10, 134, 212, 0.35);
            position: relative;
            overflow: hidden;
        }}

        .hero-ribbed-title {{
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 500 !important;
            font-size: clamp(48px, 6.2vw, 104px) !important;
            line-height: 1.05 !important;
            letter-spacing: -0.035em !important;
            color: #ffffff !important;
            margin: 0 auto 14px auto !important;
            text-shadow: 0 3px 12px rgba(0, 0, 0, 0.35);
            max-width: 1200px;
        }}

        .hero-ribbed-subtitle {{
            font-family: 'DM Sans', sans-serif !important;
            font-size: 26px !important;
            font-weight: 400 !important;
            color: #ffffff !important;
            line-height: 1.4 !important;
            letter-spacing: -0.01em !important;
            margin: 0 auto !important;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            max-width: 880px;
            opacity: 0.95;
        }}

        /* Left Column Controls (NO CARD, 26px Large Labels) */
        .left-controls-label {{
            font-family: 'DM Sans', sans-serif !important;
            font-size: 26px !important;
            font-weight: 500 !important;
            letter-spacing: -0.025em !important;
            color: {text_color} !important;
            line-height: 1.25 !important;
            margin: 16px 0 6px 0 !important;
        }}

        /* Light-Gray (#f0f1f7) 8px-Radius Input Boxes with Number & Unit */
        [data-testid="stNumberInput"] input {{
            background-color: #f0f1f7 !important;
            border: 1px solid #dcdfe8 !important;
            border-radius: 8px !important;
            color: #1e293b !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            padding: 10px 14px !important;
        }}
        .custom-param-box {{
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            background-color: #f0f1f7 !important;
            border: 1px solid #dcdfe8 !important;
            border-radius: 8px !important;
            padding: 10px 16px !important;
            margin-bottom: 6px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        }}
        .custom-param-box .param-val {{
            font-family: 'DM Sans', sans-serif !important;
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #0f172a !important;
        }}
        .custom-param-box .param-unit {{
            font-family: 'DM Sans', sans-serif !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            color: #64748b !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
        }}

        /* Grey-Purple Sliders (6px track #b3b8d3, 20px round thumb #68709a) */
        [data-testid="stSlider"],
        [data-testid="stSlider"] * {{
            --primary-color: #68709a !important;
            --primary: #68709a !important;
        }}
        [data-testid="stSlider"] div[data-baseweb="slider"] {{
            margin-top: 2px !important;
            margin-bottom: 8px !important;
        }}
        [data-testid="stSlider"] div[data-testid="stSliderTickBar"] {{
            display: none !important;
        }}
        [data-testid="stSlider"] [data-baseweb="slider"] > div > div,
        [data-baseweb="slider"] > div > div {{
            height: 6px !important;
            background-color: #b3b8d3 !important;
            background: #b3b8d3 !important;
            border-radius: 3px !important;
        }}
        [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div,
        [data-baseweb="slider"] > div > div > div {{
            background-color: #68709a !important;
            background: #68709a !important;
            height: 6px !important;
            border-radius: 3px !important;
        }}
        [data-testid="stSlider"] [role="slider"],
        [data-testid="stSlider"] div[role="slider"],
        div[role="slider"],
        [data-baseweb="slider"] [role="slider"] {{
            width: 20px !important;
            height: 20px !important;
            background-color: #68709a !important;
            background: #68709a !important;
            border: 2px solid #ffffff !important;
            border-radius: 50% !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35) !important;
            cursor: pointer !important;
        }}
        [data-testid="stSliderThumbValue"],
        [data-testid="stSlider"] div[data-testid="stSliderThumbValue"] {{
            color: #68709a !important;
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 600 !important;
        }}

        /* Right Column: Dark Green Card (#024526, 16px radius, 32px padding) */
        .dark-green-card {{
            background-color: #024526;
            border-radius: 16px;
            padding: 32px;
            color: #ffffff;
            box-shadow: 0 16px 40px -8px rgba(2, 69, 38, 0.45);
            margin-bottom: 24px;
        }}
        .green-card-heading {{
            font-family: 'DM Sans', sans-serif;
            font-size: 25px;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: -0.015em;
            margin: 0 0 10px 0;
        }}
        .huge-white-number {{
            font-family: 'DM Sans', sans-serif;
            font-size: clamp(52px, 5.5vw, 84px);
            font-weight: 800;
            color: #ffffff;
            line-height: 1.0;
            letter-spacing: -0.035em;
            margin: 6px 0 10px 0;
            text-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
        }}
        .green-card-desc {{
            font-size: 15px;
            color: rgba(255, 255, 255, 0.85);
            line-height: 1.45;
            margin-bottom: 20px;
        }}

        /* Three Darker Mini Cards (#032817) */
        .mini-card-dark {{
            background-color: #032817;
            border-radius: 12px;
            padding: 16px 18px;
            height: 100%;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .mini-card-label {{
            font-family: 'DM Sans', sans-serif;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: #ffffff;
            margin-bottom: 6px;
        }}
        .mini-card-val-amber {{
            font-family: 'DM Sans', sans-serif;
            font-size: 26px;
            font-weight: 800;
            color: #fbbf24;
            line-height: 1.15;
            margin-bottom: 4px;
        }}
        .mini-card-val-pink {{
            font-family: 'DM Sans', sans-serif;
            font-size: 26px;
            font-weight: 800;
            color: #ff6dbe;
            line-height: 1.15;
            margin-bottom: 4px;
        }}
        .mini-card-val-sky {{
            font-family: 'DM Sans', sans-serif;
            font-size: 26px;
            font-weight: 800;
            color: #38bdf8;
            line-height: 1.15;
            margin-bottom: 4px;
        }}
        .mini-card-sub {{
            font-size: 12px;
            color: rgba(255, 255, 255, 0.75);
        }}

        /* Thin 16px Bars in Pink and Amber */
        .thin-bar-label {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.85);
            margin-top: 14px;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .thin-bar-container {{
            width: 100%;
            height: 16px;
            background-color: rgba(0, 0, 0, 0.35);
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 12px;
        }}
        .thin-bar-pink {{
            height: 16px;
            background-color: #ff6dbe;
            border-radius: 8px;
        }}
        .thin-bar-amber {{
            height: 16px;
            background-color: #fbbf24;
            border-radius: 8px;
        }}

        /* Pill Buttons */
        .stButton button {{
            border-radius: 9999px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 600 !important;
            padding: 8px 18px !important;
            transition: all 0.2s ease !important;
            background-color: {"#1e293b" if is_dark else "#f0f1f7"} !important;
            color: {"#f8fafc" if is_dark else "#1e293b"} !important;
            border: 1px solid {"rgba(255, 255, 255, 0.15)" if is_dark else "#dcdfe8"} !important;
        }}
        .stButton button:hover {{
            background-color: {"#334155" if is_dark else "#e2e8f0"} !important;
            border-color: #68709a !important;
            color: {"#ffffff" if is_dark else "#0f172a"} !important;
        }}
        .stButton button p {{
            color: {"#f8fafc" if is_dark else "#1e293b"} !important;
        }}

        /* Streamlit Tabs Navigation */
        button[data-baseweb="tab"] p {{
            font-family: 'DM Sans', sans-serif !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            color: {text_color} !important;
        }}

        /* Key Insight Alert Box */
        .insight-box {{
            background: {"rgba(249, 115, 22, 0.12)" if is_dark else "#fff7ed"};
            border-left: 5px solid #f97316;
            border-radius: 12px;
            padding: 16px 20px;
            margin: 16px 0 20px 0;
            color: {"#ffedd5" if is_dark else "#7c2d12"};
            font-size: 15px;
            line-height: 1.5;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }}

        .brand-footer {{
            text-align: center;
            font-size: 13px;
            color: {sub_color};
            padding: 32px 0 16px 0;
            border-top: 1px solid rgba(120, 120, 120, 0.15);
            margin-top: 40px;
        }}
    </style>
    """


def inject_theme(is_dark: bool = False) -> None:
    """Injects the visual match theme CSS into the current Streamlit page."""
    st.markdown(get_theme_css(is_dark), unsafe_allow_html=True)
