# Pluralsight-AI-for-Intelligent-Testing-QA Setup Guide

## Virtual Environment

```
python -m venv venv
source venv/bin/activate
```

## pip installs

```
pip install flask
pip install selenium
pip install playwright
pip install pillow
pip install applitools-selenium
pip install gitpython
pip install radon
pip install scikit-learn
pip install pandas
pip install numpy
pip install matplotlib
pip install anthropic
pip install requests
```

Then install Playwright's browser binaries:
```
playwright install chromium
```

## Environment Variables

```
export ANTHROPIC_API_KEY=your_key_here
export GITHUB_TOKEN=your_token_here
export GITHUB_REPO=owner/repo
export PR_NUMBER=1
export REPO_PATH=./flask
export APPLITOOLS_API_KEY=your_key_here
```

To get your Anthropic API key, go to console.anthropic.com, sign in, and navigate to API Keys. Create a new key and copy it. To make it permanent across terminal sessions, add the export line to your `~/.zshrc` or `~/.bashrc` file.

## External Setup

Clone Flask into your project root for the hotspot analysis clip:
```
git clone https://github.com/pallets/flask.git
```

ChromeDriver must be installed and on your PATH for Selenium clips. Match the version to your installed Chrome browser: https://chromedriver.chromium.org/downloads

## Dependency Reference

| Package | What it does |
|---------|-------------|
| flask | Lightweight Python web framework — used to run the local demo app that Selenium tests run against |
| selenium | Browser automation library — drives Chrome to simulate user interactions in test scripts |
| playwright | Modern browser automation library — used for visual regression screenshot capture |
| pillow | Python image processing library — used to open and compare screenshots in pixel-diff testing |
| applitools-selenium | Applitools Eyes SDK — provides AI-powered visual comparison against stored baselines |
| gitpython | Python interface to git — used to iterate commit history and compute file churn metrics |
| radon | Python static analysis tool — computes cyclomatic complexity scores per function |
| scikit-learn | Machine learning library — used for GradientBoosting, KMeans clustering, and TF-IDF vectorization |
| pandas | Data manipulation library — used throughout for tabular data handling and metric aggregation |
| numpy | Numerical computing library — used for array operations, probability calculations, and normalization |
| matplotlib | Plotting library — generates all charts saved to disk across every module |
| anthropic | Anthropic Python SDK — used to call Claude for NLP test generation and CI triage |
| requests | HTTP library — used to call the GitHub REST API for PR diff fetching and comment posting |