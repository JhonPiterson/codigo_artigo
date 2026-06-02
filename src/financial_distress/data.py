from pathlib import Path

import pandas as pd


def load_raw_data(data_path: str | Path, sheet_name: str = "final") -> pd.DataFrame:
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    return pd.read_excel(path, sheet_name=sheet_name)


def _get_year_series(df: pd.DataFrame) -> pd.Series:
    if "YEAR" in df.columns:
        return pd.to_numeric(df["YEAR"], errors="coerce")
    return pd.to_numeric(df.iloc[:, 1], errors="coerce")


def _get_sector_series(df: pd.DataFrame) -> pd.Series:
    if "Sector" in df.columns:
        return df["Sector"]
    return df.iloc[:, 4]


def find_split_year(df: pd.DataFrame, target_train_ratio: float = 0.7) -> int | None:
    year_series = _get_year_series(df)
    unique_years = sorted(year_series.dropna().unique())

    if not unique_years:
        return None
    if len(unique_years) == 1:
        return int(unique_years[0])

    best_split_year = None
    min_diff = float("inf")

    for current_split_year in unique_years[1:]:
        train_size = (year_series < current_split_year).sum()
        total_size = len(df)
        if total_size == 0:
            continue

        train_ratio = train_size / total_size
        diff = abs(train_ratio - target_train_ratio)
        if diff < min_diff:
            min_diff = diff
            best_split_year = current_split_year

    if best_split_year is None:
        return int(unique_years[-1])
    return int(best_split_year)


def get_unique_sectors(df: pd.DataFrame) -> list[str]:
    sectors = _get_sector_series(df).dropna().astype(str).unique().tolist()
    return sorted(sectors)

