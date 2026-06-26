@echo off
title Python App Runner
cd /d %~dp0
set PYTHONPATH=%cd%

echo ==================================================
echo Run the app in package mode...
echo Command: python -m app
echo ==================================================

python -m app

if %errorlevel% neq 0 (
    echo.
    echo [Error] A problem occurred during execution. Check the log.
    pause
)