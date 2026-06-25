#m3
import os
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

FAILURES = [
    {"test": "test_payment_declined", "error": "NullPointerException: charge() called on null"},
    {"test": "test_payment_expired",  "error": "NullPointerException: charge() called on null"},
    {"test": "test_payment_refund",   "error": "NullPointerException: refund is null"},
    {"test": "test_db_read",          "error": "OperationalError: connection refused port 5432"},
    {"test": "test_db_write",         "error": "OperationalError: connection refused port 5432"},
    {"test": "test_db_update",        "error": "OperationalError: server not accepting port 5432"},
    {"test": "test_stripe_charge",    "error": "KeyError: STRIPE_SECRET_KEY not in environment"},
    {"test": "test_stripe_webhook",   "error": "KeyError: STRIPE_SECRET_KEY missing"},
]


def cluster(failures, k=3):
    X = normalize(TfidfVectorizer(ngram_range=(1, 2)).fit_transform(
        [f["error"] for f in failures]))
    labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(X)
    groups = {}
    for f, l in zip(failures, labels):
        groups.setdefault(int(l), []).append(f)
    return groups


def triage(failures):
    block = "\n".join(f"- {f['test']}: {f['error']}" for f in failures)
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content":
            f"These {len(failures)} failures share a root cause. "
            f'Respond ONLY as JSON: {{"root_cause":"...","first_step":"...","severity":"CRITICAL|WARNING|INFO"}}\n\n{block}'}]
    )
    return json.loads(re.sub(r"```json|```", "", resp.content[0].text).strip())


if __name__ == "__main__":
    groups = cluster(FAILURES)
    for cid, failures in groups.items():
        result = triage(failures)
        print(f"[{result['severity']}] Cluster {cid}")
        print(f"  Tests:      {', '.join(f['test'] for f in failures)}")
        print(f"  Root cause: {result['root_cause']}")
        print(f"  First step: {result['first_step']}\n")