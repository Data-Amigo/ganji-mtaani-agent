# =============================================================================
# Playwright Project Bootstrap Script
# =============================================================================
# This script standardizes how Playwright is installed for this repo.
#
# Why this exists:
# - We were mixing the global Python interpreter and the .venv interpreter.
# - Playwright package installs and browser installs can drift apart.
# - The default global browser cache under AppData can also drift.
#
# The key fix is setting PLAYWRIGHT_BROWSERS_PATH=0 so the browser binaries are
# installed in a project-local Playwright location instead of relying on the
# shared user cache.

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    throw "Virtual environment Python was not found at: $venvPython"
}

Write-Host "Using project root: $projectRoot"
Write-Host "Using Python: $venvPython"

Push-Location $projectRoot
try {
    $env:PLAYWRIGHT_BROWSERS_PATH = "0"

    Write-Host "Installing project dependencies into .venv..."
    & $venvPython -m pip install -e ".[dev]"

    Write-Host "Installing Chromium for the same interpreter..."
    & $venvPython -m playwright install chromium

    Write-Host "Verifying Playwright browser launch..."
    $verificationScript = @"
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    print("playwright-browser-ok")
    browser.close()
"@

    $verificationScript | & $venvPython -
}
finally {
    Pop-Location
}
