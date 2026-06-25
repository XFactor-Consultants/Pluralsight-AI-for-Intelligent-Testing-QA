#m1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

INSTABILITY_THRESHOLD = 0.15
CORRELATION_THRESHOLD = 0.75

def load_execution_history():
    rng = np.random.default_rng(42)
    tests = [f"test_{i:02d}" for i in range(10)]
    rows = []
    flaky = {2: 0.35, 7: 0.28, 5: 0.08}
    for run in range(100):
        for i, name in enumerate(tests):
            outcome = "fail" if rng.random() < flaky.get(i, 0.01) else "pass"
            rows.append({"test_name": name, "run_id": run, "outcome": outcome})
    return pd.DataFrame(rows)

def instability_scores(df):
    summary = df.groupby("test_name")["outcome"].agg(
        total="count",
        failures=lambda s: (s == "fail").sum()
    )
    summary["instability_score"] = summary["failures"] / summary["total"]
    summary["status"] = summary["instability_score"].apply(
        lambda x: "QUARANTINE" if x >= INSTABILITY_THRESHOLD else "stable"
    )
    return summary.sort_values("instability_score", ascending=False)

def failure_correlation(df):
    pivot = df.pivot_table(index="run_id", columns="test_name",
                           values="outcome",
                           aggfunc=lambda s: int((s == "fail").any())).fillna(0)
    pairs = []
    for t1, t2 in combinations(pivot.columns, 2):
        both = ((pivot[t1] == 1) & (pivot[t2] == 1)).sum()
        either = ((pivot[t1] == 1) | (pivot[t2] == 1)).sum()
        if either and (both / either) >= CORRELATION_THRESHOLD:
            pairs.append({"test_a": t1, "test_b": t2,
                          "correlation": round(both / either, 3)})
    return pd.DataFrame(pairs)

if __name__ == "__main__":
    df = load_execution_history()
    scores = instability_scores(df)
    print(scores.to_string())

    corr = failure_correlation(df)
    if not corr.empty:
        print("\nCorrelated pairs (likely shared state):")
        print(corr.to_string(index=False))

    plt.barh(scores.index, scores["instability_score"],
             color=["#e74c3c" if s == "QUARANTINE" else "#2ecc71"
                    for s in scores["status"]])
    plt.axvline(INSTABILITY_THRESHOLD, linestyle="--",
                color="orange", label="Quarantine threshold")
    plt.xlabel("Instability Score")
    plt.title("Test Suite Instability")
    plt.legend()
    plt.tight_layout()
    plt.savefig("instability.png", dpi=150)
    print("\nChart saved → instability.png")