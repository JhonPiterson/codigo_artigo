from __future__ import annotations

import pandas as pd

from dashboard.constants import DELTA_COLUMNS, DISPLAY_NAMES


def classify_winner(row: pd.Series, metric: str) -> str:
    global_col = f"{metric}__global_on_sector_test"
    sector_col = f"{metric}__sector_only"
    global_value = row.get(global_col)
    sector_value = row.get(sector_col)

    if pd.isna(global_value) or pd.isna(sector_value):
        return "Dados insuficientes"

    if metric == "BS":
        if global_value < sector_value:
            return "Global"
        if global_value > sector_value:
            return "Setorial"
    else:
        if global_value > sector_value:
            return "Global"
        if global_value < sector_value:
            return "Setorial"

    return "Empate"


def classify_strength(delta: float, metric: str) -> str:
    if pd.isna(delta):
        return "Sem sinal"

    adjusted_delta = -delta if metric == "BS" else delta
    magnitude = abs(adjusted_delta)
    if magnitude < 0.01:
        return "Marginal"
    if magnitude < 0.05:
        return "Moderado"
    return "Forte"


def build_display_table(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    display_df = df.copy()
    display_df["Winner"] = display_df.apply(lambda row: classify_winner(row, metric), axis=1)
    display_df["Strength"] = display_df[DELTA_COLUMNS[metric]].apply(lambda delta: classify_strength(delta, metric))
    display_df["MetricSector"] = display_df[f"{metric}__sector_only"]
    display_df["MetricGlobal"] = display_df[f"{metric}__global_on_sector_test"]
    display_df["DeltaMetric"] = display_df[DELTA_COLUMNS[metric]]
    return display_df


def build_importance_comparison_table(
    sector_df: pd.DataFrame,
    global_df: pd.DataFrame,
    top_n: int,
) -> pd.DataFrame:
    merged = pd.merge(
        sector_df.rename(columns={"Feature": "Variável", "Importance": "Importância setorial"}),
        global_df.rename(columns={"Feature": "Variável", "Importance": "Importância global"}),
        on="Variável",
        how="outer",
    ).fillna(0)
    merged["Diferença absoluta"] = (merged["Importância global"] - merged["Importância setorial"]).abs()
    merged = merged.sort_values("Diferença absoluta", ascending=False).head(top_n)
    return merged.reset_index(drop=True)


def build_detailed_comparison_table(display_df: pd.DataFrame, metric: str) -> pd.DataFrame:
    metric_labels = {
        "AUC": ("AUC | Setorial", "AUC | Global"),
        "KS": ("KS | Setorial", "KS | Global"),
        "ACC": ("Acurácia | Setorial", "Acurácia | Global"),
        "BS": ("Brier | Setorial", "Brier | Global"),
    }

    selected_sector_label, selected_global_label = metric_labels[metric]
    base_table = display_df[
        [
            "Sector",
            "FDType",
            "HorizonYears",
            "DatasetLabel",
            "DatasetCode",
            "SplitYear",
            "MetricSector",
            "MetricGlobal",
            "DeltaMetric",
        ]
    ].rename(
        columns={
            "Sector": "Setor",
            "FDType": "Tipo de FD",
            "HorizonYears": "Horizonte (anos)",
            "DatasetLabel": "Dataset",
            "DatasetCode": "Código do dataset",
            "SplitYear": "Ano de corte",
            "MetricSector": selected_sector_label,
            "MetricGlobal": selected_global_label,
            "DeltaMetric": f"Delta {DISPLAY_NAMES[metric]}",
        }
    )

    extra_metric_columns: list[str] = []
    rename_map: dict[str, str] = {}
    for metric_name, labels in metric_labels.items():
        if metric_name == metric:
            continue
        sector_col = f"{metric_name}__sector_only"
        global_col = f"{metric_name}__global_on_sector_test"
        extra_metric_columns.extend([sector_col, global_col])
        rename_map[sector_col] = labels[0]
        rename_map[global_col] = labels[1]

    if not extra_metric_columns:
        return base_table

    extra_table = display_df[extra_metric_columns].rename(columns=rename_map)
    return pd.concat([base_table, extra_table], axis=1)
