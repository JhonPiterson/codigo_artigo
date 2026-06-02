from __future__ import annotations

from pathlib import Path

import pandas as pd

from financial_distress.data import find_split_year, get_unique_sectors, load_raw_data
from financial_distress.modeling import split_by_year, train_and_evaluate_split, train_single_dataset
from financial_distress.preprocessing import build_raw_model_datasets


def _build_summary_row(
    metrics_df: pd.DataFrame,
    sector_name: str,
    dataset_name: str,
    model_scope: str,
    split_year: int,
    train_rows: int,
    test_rows: int,
    train_rows_used: int,
    test_rows_scored: int,
) -> dict[str, object]:
    row = metrics_df.iloc[0].to_dict()
    row.update(
        {
            "Sector": sector_name,
            "Dataset": dataset_name,
            "ModelScope": model_scope,
            "SplitYear": split_year,
            "TrainRows": train_rows,
            "TestRows": test_rows,
            "TrainRowsUsed": train_rows_used,
            "TestRowsScored": test_rows_scored,
        }
    )
    return row


def run_sector_pipeline(raw_data_df, sector_name: str, split_year: int, results_base_path: str | Path) -> None:
    results_path = Path(results_base_path) / sector_name.replace(" ", "_")
    datasets = build_raw_model_datasets(raw_data_df, sector_name=sector_name)
    for dataset_name, dataset_df in datasets.items():
        train_single_dataset(
            dataset_df,
            dataset_name,
            split_year,
            results_path,
            categorical_columns=["Country"],
            drop_feature_columns=["Sector"],
            model_tag="sector_only",
        )


def run_full_pipeline(raw_data_df, split_year: int, results_base_path: str | Path) -> None:
    results_path = Path(results_base_path) / "Full_Dataset"
    datasets = build_raw_model_datasets(raw_data_df, sector_name=None)
    for dataset_name, dataset_df in datasets.items():
        train_single_dataset(
            dataset_df,
            dataset_name,
            split_year,
            results_path,
            categorical_columns=["Country", "Sector"],
            model_tag="global",
        )


def run_comparison_pipeline(
    raw_data_df: pd.DataFrame,
    split_year: int,
    results_base_path: str | Path,
    sectors: list[str] | None = None,
) -> pd.DataFrame:
    comparison_dir = Path(results_base_path) / "comparisons"
    comparison_dir.mkdir(parents=True, exist_ok=True)

    sector_list = sectors if sectors else get_unique_sectors(raw_data_df)
    global_datasets = build_raw_model_datasets(raw_data_df, sector_name=None)
    summary_rows: list[dict[str, object]] = []

    for sector_name in sector_list:
        sector_dir = comparison_dir / sector_name.replace(" ", "_")
        sector_dir.mkdir(parents=True, exist_ok=True)

        sector_datasets = build_raw_model_datasets(raw_data_df, sector_name=sector_name)

        for dataset_name, sector_dataset_df in sector_datasets.items():
            global_dataset_df = global_datasets[dataset_name]
            global_train_df, _ = split_by_year(global_dataset_df, split_year)
            sector_train_df, sector_test_df = split_by_year(sector_dataset_df, split_year)

            sector_result = train_and_evaluate_split(
                train_df=sector_train_df,
                test_df=sector_test_df,
                dataset_name=dataset_name,
                results_path=sector_dir,
                model_tag="sector_only",
                categorical_columns=["Country"],
                drop_feature_columns=["Sector"],
            )
            global_result = train_and_evaluate_split(
                train_df=global_train_df,
                test_df=sector_test_df,
                dataset_name=dataset_name,
                results_path=sector_dir,
                model_tag="global_on_sector_test",
                categorical_columns=["Country", "Sector"],
            )

            summary_rows.append(
                _build_summary_row(
                    metrics_df=sector_result["metrics"],
                    sector_name=sector_name,
                    dataset_name=dataset_name,
                    model_scope="sector_only",
                    split_year=split_year,
                    train_rows=sector_result["train_rows"],
                    test_rows=sector_result["test_rows"],
                    train_rows_used=sector_result["train_rows_used"],
                    test_rows_scored=sector_result["test_rows_scored"],
                )
            )
            summary_rows.append(
                _build_summary_row(
                    metrics_df=global_result["metrics"],
                    sector_name=sector_name,
                    dataset_name=dataset_name,
                    model_scope="global_on_sector_test",
                    split_year=split_year,
                    train_rows=global_result["train_rows"],
                    test_rows=global_result["test_rows"],
                    train_rows_used=global_result["train_rows_used"],
                    test_rows_scored=global_result["test_rows_scored"],
                )
            )

    summary_df = pd.DataFrame(summary_rows)
    if not summary_df.empty:
        summary_df.to_csv(comparison_dir / "comparison_summary.csv", index=False, sep=";", encoding="utf-8-sig")

        metrics_to_compare = ["ACC", "AUC", "KS", "BS", "CV_ACC_Mean", "CV_AUC_Mean"]
        pivot_df = (
            summary_df.pivot_table(
                index=["Sector", "Dataset", "SplitYear"],
                columns="ModelScope",
                values=metrics_to_compare,
                aggfunc="first",
            )
            .sort_index(axis=1)
            .reset_index()
        )
        pivot_df.columns = [
            "__".join([str(part) for part in column if str(part) != ""]).strip("_")
            if isinstance(column, tuple)
            else str(column)
            for column in pivot_df.columns
        ]

        if "AUC__global_on_sector_test" in pivot_df.columns and "AUC__sector_only" in pivot_df.columns:
            pivot_df["Delta_AUC_global_minus_sector"] = (
                pivot_df["AUC__global_on_sector_test"] - pivot_df["AUC__sector_only"]
            )
        if "ACC__global_on_sector_test" in pivot_df.columns and "ACC__sector_only" in pivot_df.columns:
            pivot_df["Delta_ACC_global_minus_sector"] = (
                pivot_df["ACC__global_on_sector_test"] - pivot_df["ACC__sector_only"]
            )
        if "KS__global_on_sector_test" in pivot_df.columns and "KS__sector_only" in pivot_df.columns:
            pivot_df["Delta_KS_global_minus_sector"] = (
                pivot_df["KS__global_on_sector_test"] - pivot_df["KS__sector_only"]
            )
        if "BS__global_on_sector_test" in pivot_df.columns and "BS__sector_only" in pivot_df.columns:
            pivot_df["Delta_BS_global_minus_sector"] = (
                pivot_df["BS__global_on_sector_test"] - pivot_df["BS__sector_only"]
            )

        pivot_df.to_csv(
            comparison_dir / "comparison_wide_summary.csv",
            index=False,
            sep=";",
            encoding="utf-8-sig",
        )

        with pd.ExcelWriter(comparison_dir / "comparison_summary.xlsx") as writer:
            summary_df.to_excel(writer, sheet_name="long_format", index=False)
            pivot_df.to_excel(writer, sheet_name="wide_format", index=False)

    return summary_df


def run_project_pipeline(
    data_path: str | Path,
    results_dir: str | Path,
    sheet_name: str = "final",
    mode: str = "all",
    sectors: list[str] | None = None,
    split_year: int | None = None,
) -> int:
    raw_data_df = load_raw_data(data_path, sheet_name=sheet_name)
    selected_split_year = split_year if split_year is not None else find_split_year(raw_data_df)

    if selected_split_year is None:
        raise ValueError("Could not determine split year from the dataset.")

    output_dir = Path(results_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if mode in {"all", "sectors"}:
        sector_list = sectors if sectors else get_unique_sectors(raw_data_df)
        for sector_name in sector_list:
            run_sector_pipeline(raw_data_df, sector_name, selected_split_year, output_dir)

    if mode in {"all", "full"}:
        run_full_pipeline(raw_data_df, selected_split_year, output_dir)

    if mode == "compare":
        run_comparison_pipeline(raw_data_df, selected_split_year, output_dir, sectors=sectors)

    return selected_split_year
