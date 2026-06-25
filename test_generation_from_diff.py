#m2
# Set: GITHUB_TOKEN, GITHUB_REPO (owner/repo), PR_NUMBER
import os, re, json
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO = os.getenv("GITHUB_REPO", "")
PR_NUMBER = os.getenv("PR_NUMBER", "1")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

DEFECT_HISTORY = {
    "src/payment/processor.py": 7,
    "src/auth/token_validator.py": 4,
    "src/orders/checkout.py": 2,
}

SAMPLE_DIFF = """
diff --git a/src/payment/processor.py b/src/payment/processor.py
--- a/src/payment/processor.py
+++ b/src/payment/processor.py
@@ -45,0 +45,6 @@
+    def validate_card_expiry(self, month, year):
+        from datetime import date
+        today = date.today()
+        return not (year < today.year or (year == today.year and month < today.month))
+    def apply_discount(self, code, subtotal):
+        rates = {"SAVE10": 0.10, "SAVE20": 0.20}
+        return subtotal * (1 - rates.get(code.upper(), 0))
diff --git a/src/auth/token_validator.py b/src/auth/token_validator.py
--- a/src/auth/token_validator.py
+++ b/src/auth/token_validator.py
@@ -12,0 +12,5 @@
+    def refresh_token(self, token):
+        import jwt
+        payload = jwt.decode(token, self.secret, algorithms=["HS256"])
+        payload["exp"] += 3600
+        return jwt.encode(payload, self.secret, algorithm="HS256")
"""

def fetch_diff():
    if not GITHUB_TOKEN:
        return SAMPLE_DIFF
    resp = requests.get(
        f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}",
        headers={**HEADERS, "Accept": "application/vnd.github.v3.diff"}
    )
    return resp.text if resp.ok else SAMPLE_DIFF

def parse_changed_functions(diff):
    results, current_file = [], ""
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            m = re.search(r"b/(.+)", line)
            current_file = m.group(1) if m else ""
        if line.startswith("+") and current_file.endswith(".py"):
            m = re.match(r"^\+\s*def (\w+)\s*\(", line)
            if m:
                results.append({"file": current_file, "function": m.group(1)})
    return results

def rank_by_risk(functions):
    for f in functions:
        f["defect_history"] = DEFECT_HISTORY.get(f["file"], 0)
    return sorted(functions, key=lambda x: x["defect_history"], reverse=True)

if __name__ == "__main__":
    diff = fetch_diff()
    functions = parse_changed_functions(diff)
    ranked = rank_by_risk(functions)
    print(f"{'Function':<30} {'File':<40} {'Defect History':>14}")
    print("-" * 86)
    for f in ranked:
        print(f"  {f['function']:<28} {f['file']:<40} {f['defect_history']:>14}")