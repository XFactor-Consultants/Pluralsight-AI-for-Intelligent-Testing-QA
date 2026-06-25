#m4
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DEPLOYED = 5


def make_data(n=20):
    rng = np.random.default_rng(42)
    rows = []
    for w in range(1, n + 1):
        t = max(0, w - DEPLOYED)
        imp = 0 if w < DEPLOYED else 1 - np.exp(-t / 5)
        rows.append({"week": w,
                     "flakiness":    max(0.01,  0.18 - imp * 0.14 + rng.normal(0, 0.01)),
                     "mttd_hours":   max(0.2,   4.8  - imp * 3.5  + rng.normal(0, 0.3)),
                     "escaped_rate": max(0.005, 0.12 - imp * 0.09 + rng.normal(0, 0.008)),
                     "suite_min":    max(5,     68   - imp * 40   + rng.normal(0, 2))})
    return pd.DataFrame(rows)


def summary(df):
    pre = df[df["week"] < DEPLOYED].mean()
    post = df.tail(4).mean()
    for col, label in [("flakiness", "Flakiness"), ("mttd_hours", "MTTD"),
                       ("escaped_rate", "Escaped"), ("suite_min", "Suite time")]:
        pct = (pre[col] - post[col]) / pre[col] * 100
        print(f"  {label:<14} {pre[col]:.3f} → {post[col]:.3f}  ({pct:.1f}% ↓)")


if __name__ == "__main__":
    df = make_data()
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    fig.suptitle("AI QA Impact Dashboard", fontweight="bold")
    for (col, title, ax) in [("flakiness", "Flakiness Rate", axes[0, 0]),
                              ("mttd_hours", "MTTD (hrs)", axes[0, 1]),
                              ("escaped_rate", "Escaped Defects", axes[1, 0]),
                              ("suite_min", "Suite Time (min)", axes[1, 1])]:
        ax.plot(df["week"], df[col], linewidth=2, marker="o", markersize=3)
        ax.axvline(DEPLOYED, color="gray", linestyle="--", label="AI deployed")
        ax.axhline(df[df["week"] < DEPLOYED][col].mean(),
                   color="gray", linestyle=":", alpha=0.6, label="Baseline")
        ax.set_title(title, fontweight="bold")
        ax.legend(fontsize=7)
        ax.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig("qa_dashboard.png", dpi=150)
    print("Dashboard → qa_dashboard.png\n")
    summary(df)