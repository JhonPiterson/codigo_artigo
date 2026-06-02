from __future__ import annotations

from typing import Iterable

import pandas as pd
from sklearn.preprocessing import OneHotEncoder

BASE_COLUMN_INDEXES = list(range(0, 5)) + [6, 7, 9, 10, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 25]
TIME_WINDOWS = {
    1: list(range(26, 30)),
    2: list(range(30, 34)),
    3: list(range(34, 38)),
}
RENAMED_COLUMNS = [
    "ID",
    "YEAR",
    "Name",
    "Country",
    "Sector",
    "LIQ",
    "LVC",
    "NIE",
    "NICA",
    "EPS",
    "DTE",
    "X1A",
    "X2A",
    "X3A",
    "X4A",
    "X5A",
    "OPM",
    "CROE",
    "CPB",
    "GSA",
    "FD1",
    "FD2",
    "FD3",
    "FD4",
]
IDENTIFIER_COLUMNS = ["ID", "YEAR", "Name", "FD"]


def _make_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore")
    except TypeError:
        return OneHotEncoder(drop="first", sparse=False, handle_unknown="ignore")


def _slice_time_window(df: pd.DataFrame, time_window: int) -> pd.DataFrame:
    indexes = [i for i in BASE_COLUMN_INDEXES + TIME_WINDOWS[time_window] if i < df.shape[1]]
    sliced = df.iloc[:, indexes].copy()
    sliced.columns = RENAMED_COLUMNS[: len(sliced.columns)]
    return sliced


def _build_fd_dataset(df: pd.DataFrame, fd_index: int) -> pd.DataFrame:
    fd_column = f"FD{fd_index}"
    drop_columns = [f"FD{i}" for i in range(1, 5) if i != fd_index]
    dataset = df[df[fd_column].notna()].copy()
    dataset = dataset.drop(columns=drop_columns)
    dataset = dataset.rename(columns={fd_column: "FD"})
    return dataset


def _encode_dataset(df: pd.DataFrame, categorical_columns: Iterable[str]) -> pd.DataFrame:
    categorical_columns = list(categorical_columns)
    df_copy = df.copy()
    y = df_copy["FD"].reset_index(drop=True)
    other_vars = df_copy.drop(columns=categorical_columns + ["FD"]).reset_index(drop=True)

    if df_copy.empty:
        return pd.concat([other_vars, y], axis=1)

    encoder = _make_encoder()
    encoded = encoder.fit_transform(df_copy[categorical_columns])
    encoded_columns = encoder.get_feature_names_out(categorical_columns)
    encoded_df = pd.DataFrame(encoded, columns=encoded_columns, index=other_vars.index)

    return pd.concat([other_vars, encoded_df, y], axis=1)


def build_raw_model_datasets(raw_data_df: pd.DataFrame, sector_name: str | None = None) -> dict[str, pd.DataFrame]:
    source_df = raw_data_df.copy()
    if sector_name is not None:
        source_df = source_df.loc[source_df.iloc[:, 4] == sector_name].copy()

    datasets: dict[str, pd.DataFrame] = {}

    for time_window in TIME_WINDOWS:
        time_df = _slice_time_window(source_df, time_window)
        for fd_index in range(1, 5):
            dataset_name = f"dataset{fd_index}{time_window}"
            datasets[dataset_name] = _build_fd_dataset(time_df, fd_index)

    return datasets


def build_model_datasets(raw_data_df: pd.DataFrame, sector_name: str | None = None) -> dict[str, pd.DataFrame]:
    if sector_name is None:
        categorical_columns = ["Country", "Sector"]
    else:
        categorical_columns = ["Country"]

    raw_datasets = build_raw_model_datasets(raw_data_df, sector_name=sector_name)
    datasets: dict[str, pd.DataFrame] = {}

    for dataset_name, dataset_df in raw_datasets.items():
        encoded_input = dataset_df.drop(columns=["Sector"]) if sector_name is not None else dataset_df
        datasets[dataset_name] = _encode_dataset(encoded_input, categorical_columns)

    return datasets
