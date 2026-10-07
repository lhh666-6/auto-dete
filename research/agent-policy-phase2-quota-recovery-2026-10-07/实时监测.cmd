@echo off
chcp 65001 >nul
setlocal
set PYTHONUTF8=1
title Phase 2 Live Monitor
cd /d "%~dp0"
if exist "C:\Users\lenovo\AppData\Local\Programs\Python\Python311\python.exe" (
  "C:\Users\lenovo\AppData\Local\Programs\Python\Python311\python.exe" -u "%~dp0monitor.py" --interval 5
) else (
  python -u "%~dp0monitor.py" --interval 5
)
if errorlevel 1 pause
endlocal
