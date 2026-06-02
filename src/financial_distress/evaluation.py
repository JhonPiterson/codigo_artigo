from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, auc, brier_score_loss, confusion_matrix, roc_curve


def correct_predictions(
    test_df: pd.DataFrame,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    model,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, pd.Series]:
    x_test_clean = x_test.dropna()
    y_test_clean = y_test.loc[x_test_clean.index]

    if x_test_clean.empty:
        test_full = test_df.copy()
        test_full["XGB"] = np.nan
        test_full["XGB-prob"] = np.nan
        return test_full, np.array([]), np.array([]), y_test_clean

    y_proba = model.predict_proba(x_test_clean)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    test_full = test_df.copy()
    test_full["XGB"] = np.nan
    test_full["XGB-prob"] = np.nan
    test_full.loc[x_test_clean.index, "XGB"] = y_pred
    test_full.loc[x_test_clean.index, "XGB-prob"] = np.round(y_proba, 4)

    return test_full, y_pred, y_proba, y_test_clean


def calculate_evaluation_metrics(
    y_test: pd.Series,
    y_pred: np.ndarray,
    y_proba: np.ndarray,
    cv_acc_mean: float = np.nan,
    cv_auc_mean: float = np.nan,
) -> pd.DataFrame:
    if y_test.empty or len(y_pred) == 0 or len(y_proba) == 0:
        return pd.DataFrame(
            {
                "ModelxMeasure": ["XGB"],
                "TP": [np.nan],
                "TN": [np.nan],
                "FP": [np.nan],
                "FN": [np.nan],
                "TError_I": [np.nan],
                "TError_II": [np.nan],
                "ACC": [np.nan],
                "SENS": [np.nan],
                "SPEC": [np.nan],
                "BS": [np.nan],
                "AUC": [np.nan],
                "KS": [np.nan],
                "CV_ACC_Mean": [cv_acc_mean],
                "CV_AUC_Mean": [cv_auc_mean],
            }
        )

    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    acc = accuracy_score(y_test, y_pred)
    t_error_i = round(100 * fp / (fp + tn), 2) if (fp + tn) > 0 else np.nan
    t_error_ii = round(100 * fn / (fn + tp), 2) if (fn + tp) > 0 else np.nan
    brier = brier_score_loss(y_test, y_proba)

    if y_test.nunique() < 2:
        roc_auc_score = np.nan
        ks = np.nan
    else:
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc_score = auc(fpr, tpr)
        ks = max(tpr - fpr)

    return pd.DataFrame(
        {
            "ModelxMeasure": ["XGB"],
            "TP": [tp],
            "TN": [tn],
            "FP": [fp],
            "FN": [fn],
            "TError_I": [t_error_i],
            "TError_II": [t_error_ii],
            "ACC": [acc],
            "SENS": [tp / (tp + fn) if (tp + fn) > 0 else np.nan],
            "SPEC": [tn / (tn + fp) if (tn + fp) > 0 else np.nan],
            "BS": [brier],
            "AUC": [roc_auc_score],
            "KS": [ks],
            "CV_ACC_Mean": [cv_acc_mean],
            "CV_AUC_Mean": [cv_auc_mean],
        }
    )


def save_performance_results(
    results_df: pd.DataFrame,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    dataset_name: str,
    results_path: str | Path,
) -> None:
    output_path = Path(results_path) / f"Performance-{dataset_name}.xlsx"
    with pd.ExcelWriter(output_path) as writer:
        results_df.to_excel(writer, sheet_name="metrics", index=False)
        train_df.to_excel(writer, sheet_name="train", index=False)
        test_df.to_excel(writer, sheet_name="testfull", index=False)


def save_feature_importance(model, feature_names: list[str], dataset_name: str, results_path: str | Path) -> None:
    results_dir = Path(results_path)
    importance_df = pd.DataFrame(
        {
            "Feature": feature_names,
            "Importance": model.feature_importances_,
        }
    ).sort_values(by="Importance", ascending=False)

    importance_df.to_csv(results_dir / f"varimp-xgb-{dataset_name}.csv", index=False)

    plt.figure(figsize=(10, 6))
    sns.barplot(x="Importance", y="Feature", data=importance_df, color="gray")
    plt.title("XGBoost Feature Importance")
    plt.tight_layout()
    plt.savefig(results_dir / f"varimp-xgb-{dataset_name}.pdf")
    plt.close()


def plot_roc_curve(y_test: pd.Series, y_proba: np.ndarray, dataset_name: str, results_path: str | Path) -> None:
    if y_test.empty or y_test.nunique() < 2 or len(y_proba) == 0:
        return

    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc_score = auc(fpr, tpr)

    results_dir = Path(results_path)
    plt.figure()
    plt.plot(fpr, tpr, label=f"XGBoost (AUC = {roc_auc_score:.2f})", color="blue")
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.title("ROC Curve")
    plt.xlabel("FPR")
    plt.ylabel("TPR")
    plt.legend()
    plt.tight_layout()
    plt.savefig(results_dir / f"ROC-xgb-{dataset_name}.png", dpi=160)
    plt.savefig(results_dir / f"ROC-xgb-{dataset_name}.pdf")
    plt.close()

