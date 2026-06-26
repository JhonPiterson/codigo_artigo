from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dashboard.charts import (
    make_delta_rank,
    make_grouped_bar,
    make_heatmap,
    make_importance_chart,
    make_scatter,
)
from dashboard.components import render_fd_legend, render_metric_card
from dashboard.constants import DISPLAY_NAMES, METRIC_OPTIONS
from dashboard.data import build_dataset_lookup, filter_comparison_frames, load_data, load_feature_importance
from dashboard.styles import apply_page_style
from dashboard.tables import (
    build_detailed_comparison_table,
    build_display_table,
    build_importance_comparison_table,
)


def render_hero() -> None:
    st.markdown(
        dedent(
            """
            <div class="hero">
                <h1>Desempenho do XGBoost treinado em base setorial vs global</h1>
                <div class="hero-copy">
                    Foram treinados e testados modelos de previsão de dificuldade financeira em empresas da América Latina.
                    Os modelos globais foram treinados com dados de todos os setores, enquanto os modelos setoriais
                    foram treinados apenas com dados do setor selecionado.
                </div>
                <div class="hero-copy">
                    Este dashboard tem o objetivo de comparar o desempenho dos modelos globais e setoriais
                    com base em métricas de desempenho.
                </div>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )


def render_feature_importance_header(sector: str, dataset_label: str) -> None:
    st.markdown(
        dedent(
            f"""
            <div class="section-card">
                <h3>Importância das variáveis para {sector} | {dataset_label}</h3>
                <span class="method-chip">Esquerda = treinado apenas no setor selecionado</span>
                <span class="method-chip">Direita = treinado com todos os setores e testado no mesmo setor</span>
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )


def render_metrics_tab(
    wide_df,
    long_df,
    available_sectors: list[str],
    available_fd_types: list[str],
    available_horizons: list[int],
) -> None:
    controls_col_1, controls_col_2, controls_col_3, controls_col_4 = st.columns([1, 1.25, 1, 1])
    with controls_col_1:
        selected_metric = st.selectbox(
            "Métrica principal",
            options=METRIC_OPTIONS,
            index=0,
            key="metrics_primary_metric",
            help="Para AUC, KS e Acurácia, quanto maior, melhor. Para Brier Score, quanto menor, melhor.",
        )
    with controls_col_2:
        selected_sectors = st.multiselect(
            "Setores",
            options=available_sectors,
            default=[],
            placeholder="Todos os setores",
            key="metrics_selected_sectors",
        )
    with controls_col_3:
        selected_fd_types = st.multiselect(
            "Tipo de FD",
            options=available_fd_types,
            default=[],
            placeholder="Todos os tipos de FD",
            key="metrics_selected_fd_types",
        )
    with controls_col_4:
        selected_horizons = st.multiselect(
            "Horizonte (anos)",
            options=available_horizons,
            default=[],
            placeholder="Todos os horizontes",
            key="metrics_selected_horizons",
        )

    filtered_wide, filtered_long = filter_comparison_frames(
        wide_df,
        long_df,
        selected_sectors=selected_sectors,
        selected_fd_types=selected_fd_types,
        selected_horizons=selected_horizons,
    )
    if filtered_wide.empty:
        st.warning("Nenhuma linha corresponde aos filtros atuais de métricas.")
        return

    display_df = build_display_table(filtered_wide, selected_metric)

    if selected_metric == "BS":
        average_effect = -display_df["DeltaMetric"].mean()
        effect_note = "Vantagem média do modelo global, invertida porque menor Brier é melhor."
    else:
        average_effect = display_df["DeltaMetric"].mean()
        effect_note = "Vantagem média do modelo global sobre o modelo setorial."

    global_delta_series = -display_df["DeltaMetric"] if selected_metric == "BS" else display_df["DeltaMetric"]
    best_global_row = display_df.loc[global_delta_series.idxmax()]
    best_sector_row = display_df.loc[global_delta_series.idxmin()]
    comparison_count = len(display_df)

    card_1, card_2, card_3, card_4 = st.columns(4)
    with card_1:
        render_metric_card("Comparações", str(comparison_count), "Comparações setor-dataset visíveis.")
    with card_2:
        render_metric_card("Delta médio", f"{average_effect:+.4f}", effect_note)
    with card_3:
        render_metric_card(
            "Maior ganho global",
            f"{best_global_row['DeltaMetric']:+.4f}",
            f"{best_global_row['Sector']} | {best_global_row['DatasetLabel']}",
        )
    with card_4:
        render_metric_card(
            "Maior ganho setorial",
            f"{best_sector_row['DeltaMetric']:+.4f}",
            f"{best_sector_row['Sector']} | {best_sector_row['DatasetLabel']}",
        )

    row_1_col_1, row_1_col_2 = st.columns([1.4, 1])
    with row_1_col_1:
        st.subheader(f"{DISPLAY_NAMES[selected_metric]} por dataset")
        st.plotly_chart(make_grouped_bar(display_df, selected_metric), width="stretch")
    with row_1_col_2:
        st.subheader("Delta médio por setor")
        st.plotly_chart(make_delta_rank(display_df, selected_metric, "dataset"), width="stretch")

    row_2_col_1, row_2_col_2 = st.columns([1.05, 1.25])
    with row_2_col_1:
        st.subheader("Mapa de calor do delta")
        st.plotly_chart(make_heatmap(display_df, selected_metric), width="stretch")
    with row_2_col_2:
        st.subheader("Dispersão global vs setorial")
        st.plotly_chart(make_scatter(display_df, selected_metric), width="stretch")

    st.subheader("Tabela detalhada de comparação")
    st.dataframe(build_detailed_comparison_table(display_df, selected_metric), width="stretch", hide_index=True)

    with st.expander("Raw data em formato longo", expanded=False):
        st.dataframe(filtered_long, width="stretch", hide_index=True)


def render_feature_importance_tab(available_sectors: list[str], dataset_lookup) -> None:
    available_fd_types = dataset_lookup["FDType"].dropna().unique().tolist()
    available_horizons = sorted(dataset_lookup["HorizonYears"].dropna().astype(int).unique().tolist())

    fi_col_1, fi_col_2, fi_col_3, fi_col_4 = st.columns([1.25, 1, 1, 1])
    with fi_col_1:
        focus_sector = st.selectbox(
            "Setor",
            options=available_sectors,
            index=0,
            key="feature_importance_sector",
        )
    with fi_col_2:
        focus_fd_type = st.selectbox(
            "Tipo de FD",
            options=available_fd_types,
            index=0,
            key="feature_importance_fd_type",
        )
    with fi_col_3:
        focus_horizon = st.selectbox(
            "Horizonte (anos)",
            options=available_horizons,
            index=0,
            key="feature_importance_horizon",
        )
    with fi_col_4:
        top_n = st.slider(
            "Top variáveis",
            min_value=5,
            max_value=20,
            value=10,
            step=1,
            key="feature_importance_top_n",
        )

    selected_dataset = dataset_lookup[
        (dataset_lookup["FDType"] == focus_fd_type) & (dataset_lookup["HorizonYears"] == focus_horizon)
    ]
    if selected_dataset.empty:
        st.warning("Nenhum dataset foi encontrado para esse tipo de FD e horizonte temporal.")
        return

    focus_dataset = selected_dataset.iloc[0]["DatasetCode"]
    focus_dataset_label = selected_dataset.iloc[0]["DatasetLabel"]
    importance_sector_df = load_feature_importance(focus_sector, focus_dataset, "Sector-only model")
    importance_global_df = load_feature_importance(focus_sector, focus_dataset, "Global model")

    if importance_sector_df.empty and importance_global_df.empty:
        st.info("Nenhum arquivo de importância das variáveis foi encontrado para esse setor e dataset.")
        return

    render_feature_importance_header(focus_sector, focus_dataset_label)

    left_col, right_col = st.columns(2)
    with left_col:
        st.caption("Modelo setorial")
        if importance_sector_df.empty:
            st.info("Nenhum arquivo de importância do modelo setorial foi encontrado.")
        else:
            st.plotly_chart(
                make_importance_chart(importance_sector_df, "Sector-only model", top_n),
                width="stretch",
            )
    with right_col:
        st.caption("Modelo global")
        if importance_global_df.empty:
            st.info("Nenhum arquivo de importância do modelo global foi encontrado.")
        else:
            st.plotly_chart(
                make_importance_chart(importance_global_df, "Global model", top_n),
                width="stretch",
            )

    st.markdown("**Tabela de comparação das importâncias**")
    comparison_table = build_importance_comparison_table(
        importance_sector_df,
        importance_global_df,
        top_n=top_n,
    )
    st.dataframe(comparison_table, width="stretch", hide_index=True)


def main() -> None:
    st.set_page_config(
        page_title="Dashboard de Dificuldade Financeira",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_page_style()
    render_hero()
    render_fd_legend()

    try:
        wide_df, long_df = load_data()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.code("python main.py --data-path data/raw/file_show.xlsx --results-dir outputs --mode compare")
        return

    available_sectors = sorted(wide_df["Sector"].dropna().unique().tolist())
    available_fd_types = sorted(
        wide_df["FDType"].dropna().unique().tolist(),
        key=lambda value: int(value.replace("FD", "")) if value.startswith("FD") else 999,
    )
    available_horizons = sorted(wide_df["HorizonYears"].dropna().astype(int).unique().tolist())
    dataset_lookup = build_dataset_lookup(wide_df)
    metrics_tab, importance_tab = st.tabs(["Métricas de desempenho", "Importância das variáveis"])

    with metrics_tab:
        render_metrics_tab(wide_df, long_df, available_sectors, available_fd_types, available_horizons)

    with importance_tab:
        render_feature_importance_tab(available_sectors, dataset_lookup)


if __name__ == "__main__":
    main()
