#m1
# Set env var: APPLITOOLS_API_KEY=<your_key>
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np
from applitools.playwright import Eyes, Target, BatchInfo, MatchLevel

APP_URL = "http://localhost:3000"
BASELINE_DIR = Path("baselines")
BASELINE_DIR.mkdir(exist_ok=True)
PAGES = ["/", "/login", "/dashboard"]

def pixel_diff(current_path, baseline_path):
    if not baseline_path.exists():
        current_path.rename(baseline_path)
        return True, 0.0

    curr = np.array(Image.open(current_path).convert("RGB"))
    base = np.array(Image.open(baseline_path).convert("RGB"))

    if curr.shape != base.shape:
        return False, 100.0

    changed = (np.abs(curr.astype(int) - base.astype(int)) > 5).any(axis=2).mean() * 100
    return changed <= 0.5, round(changed, 3)

def applitools_check(page, eyes, name):
    eyes.check(name, Target.window().fully().match_level(MatchLevel.STRICT))

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        eyes = None
        if os.getenv("APPLITOOLS_API_KEY"):
            eyes = Eyes()
            eyes.api_key = os.environ["APPLITOOLS_API_KEY"]
            eyes.batch = BatchInfo("Visual Regression Demo")
            eyes.open(page, "Demo App", "Visual Suite")

        for route in PAGES:
            name = route.strip("/") or "home"
            page.goto(APP_URL + route)
            page.wait_for_load_state("networkidle")

            shot = Path(f"current_{name}.png")
            page.screenshot(path=str(shot), full_page=True)
            passed, pct = pixel_diff(shot, BASELINE_DIR / f"{name}.png")
            print(f"  pixel-diff  {name:<12} {'PASS' if passed else 'FAIL'}  ({pct}% changed)")

            if eyes:
                applitools_check(page, eyes, name)
                print(f"  applitools  {name:<12} (see dashboard for result)")

        if eyes:
            eyes.close_async()
        browser.close()