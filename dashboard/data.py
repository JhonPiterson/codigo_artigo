from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from dashboard.constants import LONG_PATH, MODEL_FILE_TAGS, OUTPUTS_DIR, WIDE_PATH


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not WIDE_PATH.exists() or not LONG_PATH.exists():
        raise FileNotFoundError(
            "Arquivos de comparação não encontrados. Execute primeiro o pipeline com `python main.py --data-path ...`."
        )

    wide_df = enrich_dataset_metadata(pd.read_csv(WIDE_PATH, sep=";", encoding="utf-8-sig"))
    long_df = enrich_dataset_metadata(pd.read_csv(LONG_PATH, sep=";", encoding="utf-8-sig"))
    return wide_df, long_df


@st.cache_data(show_spinner=False)
def load_feature_importance(sector: str, dataset: str, model_label: str) -> pd.DataFrame:
    sector_dir = OUTPUTS_DIR / sector.replace(" ", "_")
    model_tag = MODEL_FILE_TAGS[model_label]
    file_path = sector_dir / f"varimp-xgb-{dataset}-{model_tag}.csv"
    if not file_path.exists():
        return pd.DataFrame(columns=["Feature", "Importance"])
    return pd.read_csv(file_path)


def parse_dataset_code(dataset_code: str) -> dict[str, object]:
    match = re.fullmatch(r"dataset(\d)(\d)", str(dataset_code).strip().lower())
    if not match:
        return {
            "DatasetCode": dataset_code,
            "FDType": "Desconhecido",
            "FDNumber": pd.NA,
            "HorizonYears": pd.NA,
            "HorizonLabel": "Desconhecido",
            "DatasetLabel": str(dataset_code),
            "DatasetSortKey": 999,
        }

    fd_number = int(match.group(1))
    horizon_years = int(match.group(2))
    horizon_suffix = "ano" if horizon_years == 1 else "anos"
    fd_type = f"FD{fd_number}"
    return {
        "DatasetCode": dataset_code,
        "FDType": fd_type,
        "FDNumber": fd_number,
        "HorizonYears": horizon_years,
        "HorizonLabel": f"{horizon_years} {horizon_suffix}",
        "DatasetLabel": f"{fd_type} | {horizon_years} {horizon_suffix}",
        "DatasetSortKey": fd_number * 10 + horizon_years,
    }


def enrich_dataset_metadata(df: pd.DataFrame) -> pd.DataFrame:
    if "Dataset" not in df.columns:
        return df

    enriched_df = df.copy()
    metadata_df = enriched_df["Dataset"].apply(parse_dataset_code).apply(pd.Series)
    for column in metadata_df.columns:
        enriched_df[column] = metadata_df[column]
    return enriched_df


def build_dataset_lookup(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "Dataset",
        "DatasetCode",
        "DatasetLabel",
        "FDType",
        "FDNumber",
        "HorizonYears",
        "HorizonLabel",
        "DatasetSortKey",
    ]
    available_columns = [column for column in columns if column in df.columns]
    return (
        df[available_columns]
        .drop_duplicates()
        .sort_values(["FDNumber", "HorizonYears", "DatasetCode"])
        .reset_index(drop=True)
    )


def filter_comparison_frames(
    wide_df: pd.DataFrame,
    long_df: pd.DataFrame,
    selected_sectors: list[str],
    selected_fd_types: list[str],
    selected_horizons: list[int],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    filtered_wide = wide_df.copy()
    filtered_long = long_df.copy()

    if selected_sectors:
        filtered_wide = filtered_wide[filtered_wide["Sector"].isin(selected_sectors)]
        filtered_long = filtered_long[filtered_long["Sector"].isin(selected_sectors)]
    if selected_fd_types:
        filtered_wide = filtered_wide[filtered_wide["FDType"].isin(selected_fd_types)]
        filtered_long = filtered_long[filtered_long["FDType"].isin(selected_fd_types)]
    if selected_horizons:
        filtered_wide = filtered_wide[filtered_wide["HorizonYears"].isin(selected_horizons)]
        filtered_long = filtered_long[filtered_long["HorizonYears"].isin(selected_horizons)]

    return filtered_wide, filtered_long
