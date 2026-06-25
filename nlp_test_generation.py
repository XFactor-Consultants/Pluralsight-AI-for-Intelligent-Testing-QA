#m2
import os, re
from pathlib import Path
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM = """You are a senior QA engineer expert in BDD.
Generate comprehensive Gherkin scenarios for the given user story.
Rules:
- Cover happy paths AND error/edge cases
- Use concrete values, not placeholders
- Tag each scenario @happy_path, @error_case, or @edge_case
- Output ONLY valid Gherkin — no preamble or explanation"""

USER_STORY = """
User Story: Password Reset via Email
As a registered user, I want to reset my password via email so I can regain access if I forget my credentials.

Acceptance Criteria:
- Reset email sent within 2 minutes of request
- Reset link expires after 60 minutes
- Old password is invalidated immediately after successful reset
- If email is not registered, return a generic message (no enumeration)
- Reset link can only be used once
"""

def generate_gherkin(story: str) -> str:
    print("Generating scenarios...\n")
    result = ""
    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        system=SYSTEM,
        messages=[{"role": "user", "content": story}]
    ) as stream:
        for chunk in stream.text_stream:
            print(chunk, end="", flush=True)
            result += chunk
    print()
    return result

def validate_gherkin(text: str) -> list[str]:
    issues = []
    for i, block in enumerate(re.split(r"\n\s*Scenario", text)[1:], 1):
        for keyword in ("Given", "When", "Then"):
            if keyword.lower() not in block.lower():
                issues.append(f"Scenario {i}: missing {keyword}")
    return issues

if __name__ == "__main__":
    gherkin = generate_gherkin(USER_STORY)

    issues = validate_gherkin(gherkin)
    if issues:
        print("\nValidation issues:")
        for issue in issues: print(f"  ⚠  {issue}")
    else:
        print("\n✓ All scenarios pass structural validation.")

    out = Path("password_reset.feature")
    out.write_text(gherkin)
    print(f"Saved → {out}")