#m3
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import git
import radon.complexity as radon_cc

REPO_PATH = Path(os.getenv("REPO_PATH", "./flask"))


def git_churn(repo):
    since = (datetime.now() - timedelta(days=90)).isoformat()
    freq, authors = defaultdict(int), defaultdict(set)
    for commit in repo.iter_commits(since=since):
        for f in commit.stats.files:
            if f.endswith(".py"):
                freq[f] += 1
                authors[f].add(commit.author.email)
    return [{"file": f, "churn": freq[f], "authors": len(authors[f])} for f in freq]


def avg_complexity(root, files):
    rows = []
    for f in files:
        try:
            blocks = radon_cc.cc_visit((root / f).read_text(errors="ignore"))
            cc = sum(b.complexity for b in blocks) / len(blocks) if blocks else 1
        except Exception:
            cc = 1
        rows.append({"file": f, "cc": round(cc, 1)})
    return rows


if __name__ == "__main__":
    repo = git.Repo(REPO_PATH, search_parent_directories=True)
    df = pd.DataFrame(git_churn(repo)).merge(
        pd.DataFrame(avg_complexity(Path(repo.working_dir),
                     pd.DataFrame(git_churn(repo))["file"].tolist())), on="file")
    norm = lambda s: (s - s.min()) / (s.max() - s.min() + 1e-9)
    df["score"] = norm(df["cc"]) * norm(df["churn"])
    df["hotspot"] = (df["cc"] >= 3) & (df["churn"] >= 2)
    print(df.sort_values("score", ascending=False).head(10).to_string(index=False))
    print(f"\n{df['hotspot'].sum()} hotspot(s) found")
    colors = df["hotspot"].map({True: "red", False: "green"})
    plt.scatter(df["churn"], df["cc"], c=colors, alpha=0.7)
    plt.axvline(5, ls="--", color="gray")
    plt.axhline(10, ls="--", color="gray")
    plt.xlabel("Churn")
    plt.ylabel("Complexity")
    plt.title("Hotspot Map")
    plt.tight_layout()
    plt.savefig("hotspot_map.png", dpi=150)
    print("Chart → hotspot_map.png")