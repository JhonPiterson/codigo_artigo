from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train XGBoost models for financial distress prediction by sector or on the full dataset."
    )
    parser.add_argument("--data-path", required=True, help="Path to the Excel file with the raw dataset.")
    parser.add_argument("--results-dir", default="outputs", help="Directory where outputs will be saved.")
    parser.add_argument("--sheet-name", default="final", help="Excel sheet name to load.")
    parser.add_argument(
        "--mode",
        choices=["all", "sectors", "full", "compare"],
        default="compare",
        help="Run sector models, full dataset model, or the article comparison pipeline.",
    )
    parser.add_argument(
        "--sector",
        action="append",
        dest="sectors",
        help="Sector to run. Repeat the flag to run multiple sectors.",
    )
    parser.add_argument("--split-year", type=int, help="Manual split year for train/test separation.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    from financial_distress.pipeline import run_project_pipeline

    split_year = run_project_pipeline(
        data_path=args.data_path,
        results_dir=args.results_dir,
        sheet_name=args.sheet_name,
        mode=args.mode,
        sectors=args.sectors,
        split_year=args.split_year,
    )

    print(f"Pipeline finished successfully. Split year: {split_year}")
    return 0
