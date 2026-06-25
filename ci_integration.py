#m4
import os
import re
import json
import xml.etree.ElementTree as ET
import requests
import anthropic

client   = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
GH_TOKEN = os.getenv("GITHUB_TOKEN", "")
GH_REPO  = os.getenv("GITHUB_REPO", "")
PR_NUM   = os.getenv("PR_NUMBER", "")

def parse_junit(path):
    if not os.path.exists(path):
        return [{"name": "tests.payment.TestProcessor.test_charge_declined",
        "error": "NullPointerException: cannot call charge() on null"},
        {"name": "tests.auth.TestToken.test_refresh_expired",
        "error": "jwt.ExpiredSignatureError: signature has expired"}]
    failures = []
    for tc in ET.parse(path).iter("testcase"):
        el = tc.find("failure") or tc.find("error")
        if el is not None:
            failures.append({"name": f"{tc.get('classname')}.{tc.get('name')}",
            "error": el.get("message", "")[:300]})
        return failures

def triage(failures):
    block = "\n".join(f"- {f['name']}: {f['error']}" for f in failures)
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=400,
        system="You are a CI triage bot. Write a concise Markdown summary: root cause, affected area, one fix suggestion.",
        messages=[{"role": "user", "content": f"{len(failures)} failure(s):\n{block}"}])
    return resp.content[0].text

def post_comment(body):
    if not all([GH_TOKEN, GH_REPO, PR_NUM]):
        print("  (skipped — set GITHUB_TOKEN, GITHUB_REPO, PR_NUMBER)"); return
        r = requests.post(f"https://api.github.com/repos/{GH_REPO}/issues/{PR_NUM}/comments",
        json={"body": f"### � AI Triage\n\n{body}"},
        headers={"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"})
        print("posted ✓" if r.status_code == 201 else f"failed ({r.status_code})")

if name == "main":
    failures = parse_junit(os.getenv("JUNIT_RESULTS", "test-results/results.xml"))
    if not failures: print("All passed."); raise SystemExit(0)
    summary = triage(failures)
    print(summary)
    post_comment(summary)




# .github/workflows/intelligent_qa.yml:
# name: Intelligent QA
# on: [pull_request]
# jobs:
#   triage:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - run: pip install anthropic requests
#       - run: pytest --junitxml=test-results/results.xml
#         continue-on-error: true
#       - name: AI Triage
#         if: failure()
#         env:
#           ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
#           GITHUB_TOKEN:      ${{ secrets.GITHUB_TOKEN }}
#           GITHUB_REPO:       ${{ github.repository }}
#           PR_NUMBER:         ${{ github.event.pull_request.number }}
#         run: python mci_integration.py
 




















    
