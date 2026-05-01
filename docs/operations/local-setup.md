# Local Setup

This document explains how to prepare the local development environment.

## 1. Create a Virtual Environment

```powershell
python -m venv .venv
```

## 2. Standardize on the Repo Python

From this point onward, always use the project interpreter instead of the
system/global Python:

```powershell
.\.venv\Scripts\python.exe
```

This matters because Playwright package installs and browser installs must be
performed by the same interpreter.

## 3. Install the Project and Playwright Browsers

The safest path is to use the project bootstrap script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_playwright.ps1
```

What this script does:
- installs project dependencies into `.venv`
- installs Chromium for the same interpreter
- sets `PLAYWRIGHT_BROWSERS_PATH=0` during install so the browser binaries do
  not depend on the shared user-level Playwright cache
- verifies that Playwright can launch Chromium successfully

## 4. Manual Equivalent (If You Need It)

If you prefer to run the steps yourself:

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH = "0"
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe -m playwright install chromium
```

## 5. Run Forebet Smoke Tests

Forebet currently defaults to headed mode during development because headless
mode triggers a security verification page.

Basketball is the default Forebet target:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_fetch.py --source forebet --save-snapshot --screenshot
```

Explicit basketball target:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_fetch.py --source forebet --target basketball_today --save-snapshot --screenshot
```

Football target:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_fetch.py --source forebet --target football_today --save-snapshot --screenshot
```

To force headless mode for comparison:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_fetch.py --source forebet --target basketball_today --headless --save-snapshot --screenshot
```

## 6. Run Polymarket Inspection

```powershell
.\.venv\Scripts\python.exe scripts\fetch_polymarket_gamma.py --limit 5 --scan-limit 100
```

## Notes

- Use one interpreter consistently: `\.venv\Scripts\python.exe`.
- Avoid mixing the repo venv with the global `python.exe` when running
  Playwright-based scripts.
- If a script says the Playwright browser executable does not exist, rerun the
  bootstrap script or the manual Playwright install commands above.
- Saved snapshots and screenshots go under `data/raw/`, which is ignored by git.
