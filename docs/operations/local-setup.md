# Local Setup

This document explains how to prepare the local development environment.

## 1. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2. Install the Project

```powershell
python -m pip install -e .[dev]
```

## 3. Install Playwright Browser

```powershell
python -m playwright install chromium
```

## 4. Run the Browser Smoke Test

Forebet currently defaults to headed mode during development because headless mode triggers a security verification page.

```powershell
python scripts\smoke_fetch.py --source forebet --save-snapshot --screenshot
```

To force headless mode for comparison:

```powershell
python scripts\smoke_fetch.py --source forebet --headless --save-snapshot --screenshot
```

For Polymarket:

```powershell
python scripts\smoke_fetch.py --source polymarket --save-snapshot --screenshot
```

## Notes

- The smoke test only checks that the browser layer can load a page.
- Real source-specific parsing comes later.
- Saved snapshots and screenshots go under `data/raw/`, which is ignored by git.
- If a source shows security verification, the browser layer should warn instead of pretending the data is valid.
