#m3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

FEATURES = ["coverage_overlap", "days_since_last_fail", "historical_fail_rate", "churn"]


def make_dataset(n=2000):
    rng = np.random.default_rng(42)
    df = pd.DataFrame({
        "coverage_overlap":     rng.beta(2, 5, n),
        "days_since_last_fail": rng.integers(0, 90, n),
        "historical_fail_rate": rng.beta(1, 9, n),
        "churn":                rng.integers(0, 50, n),
    })
    p = (
        df["coverage_overlap"] * 0.55
        + (df["churn"] / 50) * 0.30
        + df["historical_fail_rate"] * 0.15
    )
    df["failed"] = (rng.random(n) < p.clip(0.02, 0.92)).astype(int)
    return df


def apfd(ordered_fails):
    n, m = len(ordered_fails), sum(ordered_fails)
    if m == 0:
        return 1.0
    return 1 - sum(i + 1 for i, f in enumerate(ordered_fails) if f) / (n * m) + 1 / (2 * n)


if __name__ == "__main__":
    df = make_dataset()
    X, y = df[FEATURES], df["failed"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    model = GradientBoostingClassifier(n_estimators=200, max_depth=4, random_state=42)
    model.fit(X_tr, y_tr)
    print(f"ROC-AUC: {roc_auc_score(y_te, model.predict_proba(X_te)[:, 1]):.3f}")
    suite = make_dataset(100)
    suite["failure_prob"] = model.predict_proba(suite[FEATURES])[:, 1]
    suite["actually_fails"] = (suite["failure_prob"] > 0.4).astype(int)
    ranked = suite.sort_values("failure_prob", ascending=False).reset_index(drop=True)
    random = suite.sample(frac=1, random_state=7).reset_index(drop=True)
    print(f"\nAPFD — ML ranked: {apfd(ranked['actually_fails'].tolist()):.3f}")
    print(f"APFD — random:    {apfd(random['actually_fails'].tolist()):.3f}")
    for label, subset, color in [("ML Ranked", ranked, "#2980b9"), ("Random", random, "#e74c3c")]:
        cum = np.cumsum(subset["actually_fails"]) / max(subset["actually_fails"].sum(), 1)
        plt.plot(np.arange(1, 101) / 100 * 100, cum * 100, label=label, color=color)
    plt.xlabel("% Suite Executed")
    plt.ylabel("% Faults Detected")
    plt.title("Fault Detection Curve")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("apfd_curve.png", dpi=150)
    print("Chart saved → apfd_curve.png")