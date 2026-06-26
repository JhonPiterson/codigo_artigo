from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.constants import DELTA_COLUMNS, DISPLAY_NAMES


def make_grouped_bar(df: pd.DataFrame, metric: str) -> go.Figure:
    melted = df.melt(
        id_vars=["Sector", "DatasetLabel", "DatasetSortKey", "FDType", "HorizonYears"],
        value_vars=[f"{metric}__sector_only", f"{metric}__global_on_sector_test"],
        var_name="Modelo",
        value_name="Valor",
    )
    melted["DatasetLabelWrapped"] = melted.apply(
        lambda row: (
            f"{row['FDType']}<br>{int(row['HorizonYears'])} ano"
            if int(row["HorizonYears"]) == 1
            else f"{row['FDType']}<br>{int(row['HorizonYears'])} anos"
        ),
        axis=1,
    )
    melted["Modelo"] = melted["Modelo"].map(
        {
            f"{metric}__sector_only": "Modelo setorial",
            f"{metric}__global_on_sector_test": "Modelo global",
        }
    )

    fig = px.bar(
        melted,
        x="DatasetLabelWrapped",
        y="Valor",
        color="Modelo",
        barmode="group",
        hover_data=["Sector", "FDType", "HorizonYears"],
        color_discrete_map={"Modelo setorial": "#c28b2c", "Modelo global": "#1e6f72"},
        category_orders={
            "DatasetLabelWrapped": (
                melted.sort_values("DatasetSortKey")["DatasetLabelWrapped"].drop_duplicates().tolist()
            )
        },
        labels={
            "Sector": "Setor",
            "FDType": "Tipo de FD",
            "HorizonYears": "Horizonte (anos)",
            "Valor": DISPLAY_NAMES[metric],
        },
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=16, b=28),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        yaxis_title=DISPLAY_NAMES[metric],
    )
    fig.update_xaxes(showgrid=False, title_text="Dataset")
    fig.update_yaxes(gridcolor="rgba(23,33,38,0.10)")
    return fig


def make_heatmap(df: pd.DataFrame, metric: str) -> go.Figure:
    ordered_labels = (
        df[["DatasetLabel", "DatasetSortKey"]]
        .drop_duplicates()
        .sort_values("DatasetSortKey")["DatasetLabel"]
        .tolist()
    )
    heatmap_df = (
        df.pivot(index="Sector", columns="DatasetLabel", values=DELTA_COLUMNS[metric])
        .reindex(columns=ordered_labels)
        .sort_index()
    )
    zmin = float(heatmap_df.min().min()) if not heatmap_df.empty else -1
    zmax = float(heatmap_df.max().max()) if not heatmap_df.empty else 1
    max_abs = max(abs(zmin), abs(zmax), 0.001)

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_df.values,
            x=list(heatmap_df.columns),
            y=list(heatmap_df.index),
            colorscale=[[0, "#b8552d"], [0.5, "#f4efe6"], [1, "#1e6f72"]],
            zmid=0,
            zmin=-max_abs,
            zmax=max_abs,
            colorbar_title="Delta",
            hovertemplate="Setor=%{y}<br>Dataset=%{x}<br>Delta=%{z:.4f}<extra></extra>",
        )
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=16, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def make_scatter(df: pd.DataFrame, metric: str) -> go.Figure:
    fig = px.scatter(
        df,
        x=f"{metric}__sector_only",
        y=f"{metric}__global_on_sector_test",
        color="Sector",
        hover_data=["DatasetLabel", "FDType", "HorizonYears"],
        size_max=12,
        labels={
            "Sector": "Setor",
            "DatasetLabel": "Dataset",
            "FDType": "Tipo de FD",
            "HorizonYears": "Horizonte (anos)",
        },
    )
    min_value = min(df[f"{metric}__sector_only"].min(), df[f"{metric}__global_on_sector_test"].min())
    max_value = max(df[f"{metric}__sector_only"].max(), df[f"{metric}__global_on_sector_test"].max())
    fig.add_shape(
        type="line",
        x0=min_value,
        y0=min_value,
        x1=max_value,
        y1=max_value,
        line=dict(color="#172126", dash="dash"),
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=16, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title=f"{DISPLAY_NAMES[metric]} | Setorial",
        yaxis_title=f"{DISPLAY_NAMES[metric]} | Global",
        legend_title_text="Setor",
    )
    fig.update_xaxes(gridcolor="rgba(23,33,38,0.10)")
    fig.update_yaxes(gridcolor="rgba(23,33,38,0.10)")
    return fig


def make_importance_chart(df: pd.DataFrame, model_label: str, top_n: int) -> go.Figure:
    top_df = df.sort_values("Importance", ascending=False).head(top_n).sort_values("Importance", ascending=True)
    fig = px.bar(
        top_df,
        x="Importance",
        y="Feature",
        orientation="h",
        color="Importance",
        color_continuous_scale=["#f0d7a6", "#c28b2c"] if model_label == "Sector-only model" else ["#b7dddf", "#1e6f72"],
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=16, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis_title="Importância",
        yaxis_title="",
    )
    fig.update_xaxes(gridcolor="rgba(23,33,38,0.10)")
    return fig


def make_delta_rank(df: pd.DataFrame, metric: str, focus_mode: str) -> go.Figure:
    group_col = "DatasetLabel" if focus_mode == "sector" else "Sector"
    if focus_mode == "sector":
        rank_df = (
            df.groupby(["DatasetLabel", "DatasetSortKey"], as_index=False)["DeltaMetric"]
            .mean()
            .sort_values(["DatasetSortKey", "DeltaMetric"], ascending=[True, False])
        )
    else:
        rank_df = (
            df.groupby(group_col, as_index=False)["DeltaMetric"]
            .mean()
            .sort_values("DeltaMetric", ascending=False)
        )
    fig = px.bar(
        rank_df,
        x=group_col,
        y="DeltaMetric",
        color="DeltaMetric",
        color_continuous_scale=["#b8552d", "#f4efe6", "#1e6f72"],
        category_orders={group_col: rank_df[group_col].tolist()},
    )
    fig.update_layout(
        margin=dict(l=8, r=8, t=16, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        xaxis_title="",
        yaxis_title=f"Delta médio de {DISPLAY_NAMES[metric]}",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(23,33,38,0.10)")
    return fig
