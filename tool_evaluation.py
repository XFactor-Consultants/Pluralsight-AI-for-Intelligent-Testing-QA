#m4
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

CRITERIA = {
    "false_positive_rate":      5,
    "integration_breadth":      4,
    "ease_of_adoption":         4,
    "security_and_privacy":     4,
    "model_transparency":       3,
    "pricing_model":            3,
    "open_source_availability": 2,
}

TOOLS = {
    "Healenium":  {"cat": "Self-Healing",   "false_positive_rate": 4, "integration_breadth": 3, "ease_of_adoption": 4, "security_and_privacy": 5, "model_transparency": 4, "pricing_model": 5, "open_source_availability": 5},
    "Testim":     {"cat": "Self-Healing",   "false_positive_rate": 4, "integration_breadth": 4, "ease_of_adoption": 5, "security_and_privacy": 3, "model_transparency": 3, "pricing_model": 2, "open_source_availability": 1},
    "Applitools": {"cat": "Visual",         "false_positive_rate": 5, "integration_breadth": 5, "ease_of_adoption": 4, "security_and_privacy": 3, "model_transparency": 4, "pricing_model": 2, "open_source_availability": 2},
    "Launchable": {"cat": "Prioritization", "false_positive_rate": 4, "integration_breadth": 5, "ease_of_adoption": 4, "security_and_privacy": 3, "model_transparency": 4, "pricing_model": 3, "open_source_availability": 1},
    "BuildPulse": {"cat": "Flakiness",      "false_positive_rate": 4, "integration_breadth": 5, "ease_of_adoption": 5, "security_and_privacy": 3, "model_transparency": 3, "pricing_model": 3, "open_source_availability": 1},
    "SonarQube":  {"cat": "Defect",         "false_positive_rate": 3, "integration_breadth": 5, "ease_of_adoption": 3, "security_and_privacy": 5, "model_transparency": 5, "pricing_model": 4, "open_source_availability": 5},
}

if __name__ == "__main__":
    cols = list(CRITERIA.keys())
    w = np.array(list(CRITERIA.values()), dtype=float)
    w /= w.sum()
    rows = []
    for name, d in TOOLS.items():
        s = np.array([d[c] for c in cols], dtype=float)
        rows.append({"Tool": name, "Category": d["cat"],
                     "Score": round((s * w).sum() * 5, 2)})
    df = pd.DataFrame(rows).sort_values("Score", ascending=False)
    print(df.to_string(index=False))
    plt.barh(df["Tool"], df["Score"])
    plt.xlabel("Weighted Score (1–5)")
    plt.title("AI QA Tool Rankings")
    plt.tight_layout()
    plt.savefig("tool_rankings.png", dpi=150)
    print("Chart → tool_rankings.png")