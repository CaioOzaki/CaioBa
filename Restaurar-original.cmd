@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-or-Restore.ps1" -Mode Restore
pause
