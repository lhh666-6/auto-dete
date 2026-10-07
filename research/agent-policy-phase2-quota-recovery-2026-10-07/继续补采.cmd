@echo off
setlocal
title Phase 2 Resume
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0continue_collection.ps1"
pause
endlocal
