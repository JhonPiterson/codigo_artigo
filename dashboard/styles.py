from __future__ import annotations

import streamlit as st


def apply_page_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Source+Sans+3:wght@400;600;700&display=swap');

        :root {
            --paper: #f4efe6;
            --ink: #172126;
            --muted: #5f6b70;
            --gold: #c28b2c;
            --teal: #1e6f72;
            --clay: #b8552d;
            --panel: rgba(255,255,255,0.78);
            --line: rgba(23,33,38,0.10);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(194,139,44,0.18), transparent 24%),
                radial-gradient(circle at top right, rgba(30,111,114,0.16), transparent 26%),
                linear-gradient(180deg, #f8f3eb 0%, var(--paper) 45%, #efe6d7 100%);
            color: var(--ink);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(23,33,38,0.96), rgba(23,33,38,0.90));
        }

        [data-testid="stSidebar"] .material-symbols-rounded,
        [data-testid="stSidebar"] .material-icons,
        [data-testid="stSidebar"] [class*="material-symbols"],
        [data-testid="stSidebar"] [class*="material-icons"] {
            font-family: "Material Symbols Rounded", "Material Icons" !important;
            color: #f4efe6 !important;
            -webkit-text-fill-color: #f4efe6 !important;
        }

        button[kind="header"] .material-symbols-rounded,
        button[kind="header"] .material-icons,
        button[kind="header"] [class*="material-symbols"],
        button[kind="header"] [class*="material-icons"] {
            color: #f4efe6 !important;
            -webkit-text-fill-color: #f4efe6 !important;
        }

        [data-testid="stSidebarCollapseButton"],
        [data-testid="collapsedControl"] {
            color: #f4efe6 !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        [data-testid="stSidebarCollapseButton"] *,
        [data-testid="collapsedControl"] * {
            color: #f4efe6 !important;
            fill: #f4efe6 !important;
            stroke: #f4efe6 !important;
            -webkit-text-fill-color: #f4efe6 !important;
            opacity: 1 !important;
            visibility: visible !important;
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] .stMultiSelect {
            color: #f4efe6 !important;
            font-family: "Source Sans 3", sans-serif !important;
        }

        [data-testid="stSidebar"] button {
            color: #f4efe6 !important;
            font-family: "Source Sans 3", sans-serif !important;
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] > div,
        [data-testid="stSidebar"] div[data-baseweb="input"] > div {
            background: rgba(244, 239, 230, 0.10) !important;
            border: 1px solid rgba(244, 239, 230, 0.24) !important;
            color: #f4efe6 !important;
        }

        [data-testid="stSidebar"] div[data-baseweb="select"] input,
        [data-testid="stSidebar"] div[data-baseweb="input"] input {
            color: #f4efe6 !important;
            -webkit-text-fill-color: #f4efe6 !important;
        }

        [data-testid="stSidebar"] div[data-baseweb="tag"] {
            background: rgba(194, 139, 44, 0.24) !important;
            color: #f4efe6 !important;
            border: 1px solid rgba(244, 239, 230, 0.18) !important;
        }

        [data-testid="stSidebar"] div[role="listbox"] {
            background: #182328 !important;
            color: #f4efe6 !important;
        }

        [data-testid="stSidebar"] div[role="option"] {
            color: #f4efe6 !important;
        }

        [data-testid="stSidebar"] button[kind="secondary"] {
            background: rgba(184, 85, 45, 0.16) !important;
            border: 1px solid rgba(184, 85, 45, 0.42) !important;
            color: #ffb8a6 !important;
        }

        [data-testid="stSidebar"] button[kind="secondary"]:hover {
            background: rgba(184, 85, 45, 0.28) !important;
            border: 1px solid rgba(184, 85, 45, 0.62) !important;
            color: #ffe1d8 !important;
        }

        .block-container {
            padding-top: 2.1rem;
            padding-bottom: 2rem;
        }

        h1, h2, h3 {
            font-family: "Libre Baskerville", serif !important;
            color: var(--ink);
            letter-spacing: -0.02em;
        }

        p, li, div[data-testid="stMarkdownContainer"] {
            font-family: "Source Sans 3", sans-serif;
        }

        .hero {
            background: linear-gradient(135deg, rgba(255,255,255,0.76), rgba(255,255,255,0.42));
            border: 1px solid var(--line);
            border-radius: 24px;
            padding: 1.4rem 1.6rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 16px 50px rgba(23,33,38,0.08);
            margin-bottom: 1rem;
        }

        .hero-kicker {
            color: var(--teal);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.82rem;
            margin-bottom: 0.5rem;
        }

        .hero-copy {
            color: var(--muted);
            font-size: 1rem;
            max-width: 58rem;
        }

        .metric-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            min-height: 132px;
            box-shadow: 0 14px 34px rgba(23,33,38,0.06);
        }

        .metric-label {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.78rem;
            font-weight: 700;
        }

        .metric-value {
            font-family: "Libre Baskerville", serif;
            font-size: 2rem;
            line-height: 1.08;
            margin-top: 0.25rem;
            color: var(--ink);
        }

        .metric-note {
            color: var(--muted);
            font-size: 0.92rem;
            margin-top: 0.4rem;
        }

        .section-card {
            background: rgba(255,255,255,0.68);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem 1.2rem 0.8rem 1.2rem;
            box-shadow: 0 14px 34px rgba(23,33,38,0.06);
        }

        .fd-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.9rem;
            margin-top: 0.9rem;
        }

        .fd-mini-card {
            background: rgba(255,255,255,0.70);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 1rem;
            min-height: 118px;
        }

        .fd-mini-title {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
            font-family: "Source Sans 3", sans-serif;
        }

        .fd-mini-copy {
            color: var(--muted);
            font-size: 0.96rem;
            line-height: 1.5;
            font-family: "Source Sans 3", sans-serif;
        }

        .method-chip {
            display: inline-block;
            margin-right: 0.5rem;
            margin-bottom: 0.45rem;
            padding: 0.38rem 0.72rem;
            border-radius: 999px;
            background: rgba(30,111,114,0.10);
            border: 1px solid rgba(30,111,114,0.18);
            color: var(--ink);
            font-size: 0.9rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.75rem;
            margin-top: 1.2rem;
            margin-bottom: 1rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: auto;
            padding: 0.95rem 1.35rem;
            border-radius: 18px;
            background: rgba(255,255,255,0.62);
            border: 1px solid rgba(23,33,38,0.12);
            box-shadow: 0 10px 24px rgba(23,33,38,0.05);
            font-family: "Source Sans 3", sans-serif !important;
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--muted);
            transition: all 0.15s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(255,255,255,0.84);
            color: var(--ink);
            border-color: rgba(30,111,114,0.24);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(30,111,114,0.18), rgba(194,139,44,0.12));
            color: var(--ink) !important;
            border-color: rgba(30,111,114,0.30);
            box-shadow: 0 14px 28px rgba(23,33,38,0.08);
        }

        div[data-testid="stExpander"] {
            background: rgba(255,255,255,0.68);
            border: 1px solid var(--line);
            border-radius: 22px;
            box-shadow: 0 14px 34px rgba(23,33,38,0.06);
            overflow: hidden;
        }

        div[data-testid="stExpander"] details {
            border: none !important;
        }

        div[data-testid="stExpander"] summary {
            padding: 0.9rem 1.1rem;
            font-family: "Source Sans 3", sans-serif !important;
            font-size: 1rem;
            font-weight: 700;
            color: var(--ink) !important;
            background: rgba(255,255,255,0.42);
        }

        div[data-testid="stExpander"] summary:hover {
            background: rgba(255,255,255,0.62);
        }

        div[data-testid="stExpanderDetails"] {
            padding: 0.2rem 1rem 1rem 1rem;
        }

        @media (max-width: 900px) {
            .fd-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 640px) {
            .fd-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
