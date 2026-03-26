@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Gesture Action Motion Engine — App Builder
echo ============================================================
echo.

:: ── Check Python ──────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not found in PATH.
    echo         Install Python 3.10-3.12 from https://python.org and retry.
    pause
    exit /b 1
)

:: ── Install / upgrade PyInstaller ─────────────────────────────
echo [1/3] Installing / upgrading PyInstaller...
pip install --upgrade pyinstaller
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller. Check your internet / pip setup.
    pause
    exit /b 1
)

:: ── Install project requirements ──────────────────────────────
echo.
echo [2/3] Installing project requirements...
pip install -r "%~dp0..\requirements.txt"
if errorlevel 1 (
    echo [WARNING] Some requirements may have failed. Continuing anyway...
)

:: ── Run PyInstaller with the spec file ────────────────────────
echo.
echo [3/3] Building app with PyInstaller...
cd /d "%~dp0"
pyinstaller GestureApp.spec --noconfirm
if errorlevel 1 (
    echo.
    echo [ERROR] Build FAILED. Check the output above for details.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   BUILD SUCCESSFUL!
echo   Distributable app: GestureApp\dist\GestureApp\
echo   Share the entire GestureApp folder (zip it first).
echo ============================================================
pause
