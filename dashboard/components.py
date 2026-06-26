from __future__ import annotations

from html import escape
from textwrap import dedent

import pandas as pd
import streamlit as st

from dashboard.constants import FD_DESCRIPTIONS, VARIABLE_DESCRIPTIONS


def render_metric_card(label: str, value: str, note: str) -> None:
    safe_label = escape(label)
    safe_value = escape(value)
    safe_note = escape(note)
    st.markdown(
        dedent(
            f"""
            <div class="metric-card">
                <div class="metric-label">{safe_label}</div>
                <div class="metric-value">{safe_value}</div>
                <div class="metric-note">{safe_note}</div>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )


def render_fd_legend() -> None:
    cards_html = "".join(
        dedent(
            f"""
            <div class="fd-mini-card">
                <div class="fd-mini-title">{escape(fd_type)}</div>
                <div class="fd-mini-copy">{escape(description)}</div>
            </div>
            """
        ).strip()
        for fd_type, description in FD_DESCRIPTIONS.items()
    )

    st.markdown(
        dedent(
            f"""
            <div class="section-card">
                <h3>Tipos de Dificuldade Financeira (Financial Distress) analisadas</h3>
                <div class="fd-grid">{cards_html}</div>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

    with st.expander("Variáveis independentes utilizadas", expanded=False):
        variables_df = pd.DataFrame(VARIABLE_DESCRIPTIONS, columns=["Variável", "Descrição"])
        st.dataframe(variables_df, width="stretch", hide_index=True)
