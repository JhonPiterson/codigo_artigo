from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from imblearn.under_sampling import RandomUnderSampler
from sklearn.model_selection import StratifiedKFold, cross_val_score
from xgboost import XGBClassifier

from financial_distress.evaluation import (
    calculate_evaluation_metrics,
    correct_predictions,
    plot_roc_curve,
    save_feature_importance,
    save_performance_results,
)
from financial_distress.preprocessing import IDENTIFIER_COLUMNS


def split_by_year(df: pd.DataFrame, split_year: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    working_df = df.copy()
    working_df["YEAR"] = pd.to_numeric(working_df["YEAR"], errors="coerce")
    working_df = working_df.dropna(subset=["YEAR"])
    train_df = working_df[working_df["YEAR"] < split_year].copy()
    test_df = working_df[working_df["YEAR"] >= split_year].copy()
    return train_df, test_df


def encode_train_test(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    categorical_columns: list[str],
    drop_feature_columns: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    drop_feature_columns = drop_feature_columns or []
    categorical_columns = [column for column in categorical_columns if column in train_df.columns]

    feature_drop_columns = set(IDENTIFIER_COLUMNS) | set(drop_feature_columns)
    numeric_columns = [
        column
        for column in train_df.columns
        if column not in feature_drop_columns and column not in categorical_columns
    ]

    x_train_numeric = train_df[numeric_columns].apply(pd.to_numeric, errors="coerce")
    x_test_numeric = test_df[numeric_columns].apply(pd.to_numeric, errors="coerce")

    if categorical_columns:
        try:
            from sklearn.preprocessing import OneHotEncoder

            try:
                encoder = OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore")
            except TypeError:
                encoder = OneHotEncoder(drop="first", sparse=False, handle_unknown="ignore")
        except ImportError as exc:
            raise RuntimeError("scikit-learn is required to encode categorical features.") from exc

        if train_df.empty:
            train_encoded = pd.DataFrame(index=train_df.index)
            test_encoded = pd.DataFrame(index=test_df.index)
        else:
            train_categories = train_df[categorical_columns].fillna("Missing").astype(str)
            test_categories = test_df[categorical_columns].fillna("Missing").astype(str)
            train_encoded_array = encoder.fit_transform(train_categories)
            test_encoded_array = encoder.transform(test_categories)
            encoded_columns = encoder.get_feature_names_out(categorical_columns)
            train_encoded = pd.DataFrame(train_encoded_array, columns=encoded_columns, index=train_df.index)
            test_encoded = pd.DataFrame(test_encoded_array, columns=encoded_columns, index=test_df.index)
    else:
        train_encoded = pd.DataFrame(index=train_df.index)
        test_encoded = pd.DataFrame(index=test_df.index)

    x_train = pd.concat([x_train_numeric, train_encoded], axis=1)
    x_test = pd.concat([x_test_numeric, test_encoded], axis=1)
    y_train = train_df["FD"].astype(int)
    y_test = test_df["FD"].astype(int)

    return x_train, y_train, x_test, y_test


def _fit_balanced_xgboost(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = 123,
) -> tuple[XGBClassifier | None, pd.DataFrame, pd.Series, float, float]:
    cleaned_train = pd.concat([x_train, y_train], axis=1).dropna()
    if cleaned_train.empty:
        return None, pd.DataFrame(), pd.Series(dtype=int), np.nan, np.nan

    x_train_clean = cleaned_train.drop(columns="FD")
    y_train_clean = cleaned_train["FD"]

    if y_train_clean.nunique() < 2:
        return None, x_train_clean, y_train_clean, np.nan, np.nan

    sampler = RandomUnderSampler(random_state=random_state)
    x_train_balanced, y_train_balanced = sampler.fit_resample(x_train_clean, y_train_clean)

    model = XGBClassifier(eval_metric="logloss", random_state=random_state)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    min_class_count = y_train_balanced.value_counts().min()

    if min_class_count < cv.n_splits:
        cv_acc_mean = np.nan
        cv_auc_mean = np.nan
    else:
        cv_acc = cross_val_score(model, x_train_balanced, y_train_balanced, cv=cv, scoring="accuracy")
        cv_auc = cross_val_score(model, x_train_balanced, y_train_balanced, cv=cv, scoring="roc_auc")
        cv_acc_mean = float(np.mean(cv_acc))
        cv_auc_mean = float(np.mean(cv_auc))

    model.fit(x_train_balanced, y_train_balanced)
    return model, x_train_balanced, y_train_balanced, cv_acc_mean, cv_auc_mean


def train_and_evaluate_split(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    dataset_name: str,
    results_path: str | Path,
    model_tag: str,
    categorical_columns: list[str],
    drop_feature_columns: list[str] | None = None,
    random_state: int = 123,
) -> dict[str, object]:
    results_dir = Path(results_path)
    results_dir.mkdir(parents=True, exist_ok=True)

    x_train, y_train, x_test, y_test = encode_train_test(
        train_df=train_df,
        test_df=test_df,
        categorical_columns=categorical_columns,
        drop_feature_columns=drop_feature_columns,
    )

    model, x_train_balanced, y_train_balanced, cv_acc_mean, cv_auc_mean = _fit_balanced_xgboost(
        x_train=x_train,
        y_train=y_train,
        random_state=random_state,
    )

    output_name = f"{dataset_name}-{model_tag}"

    if model is None:
        empty_test = test_df.copy()
        empty_test["XGB"] = np.nan
        empty_test["XGB-prob"] = np.nan
        results_df = calculate_evaluation_metrics(pd.Series(dtype=int), np.array([]), np.array([]))
        save_performance_results(results_df, train_df, empty_test, output_name, results_dir)
        return {
            "metrics": results_df,
            "train_rows": int(len(train_df)),
            "test_rows": int(len(test_df)),
            "train_rows_used": 0,
            "test_rows_scored": 0,
        }

    joblib.dump(model, results_dir / f"{output_name}.joblib")
    save_feature_importance(model, list(x_train_balanced.columns), output_name, results_dir)

    test_full, y_pred, y_proba, y_test_clean = correct_predictions(test_df, x_test, y_test, model)
    results_df = calculate_evaluation_metrics(y_test_clean, y_pred, y_proba, cv_acc_mean, cv_auc_mean)
    plot_roc_curve(y_test_clean, y_proba, output_name, results_dir)
    save_performance_results(results_df, train_df, test_full, output_name, results_dir)

    return {
        "metrics": results_df,
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "train_rows_used": int(len(x_train_balanced)),
        "test_rows_scored": int(len(y_test_clean)),
    }


def train_single_dataset(
    df: pd.DataFrame,
    dataset_name: str,
    split_year: int,
    results_path: str | Path,
    categorical_columns: list[str],
    drop_feature_columns: list[str] | None = None,
    model_tag: str | None = None,
    random_state: int = 123,
) -> dict[str, object]:
    train_df, test_df = split_by_year(df, split_year)
    selected_model_tag = model_tag or "xgb"
    return train_and_evaluate_split(
        train_df=train_df,
        test_df=test_df,
        dataset_name=dataset_name,
        results_path=results_path,
        model_tag=selected_model_tag,
        categorical_columns=categorical_columns,
        drop_feature_columns=drop_feature_columns,
        random_state=random_state,
    )
