@echo off
rem Double-click to start Deadpan Studio (local mode). Copy this file to your Desktop if you like.
rem It starts the studio inside WSL (Ubuntu) and opens it in your browser. Keep this window open while Claude works.
title Deadpan Studio
start "" cmd /c "timeout /t 8 >nul & start http://localhost:8080"
wsl.exe -- bash -lc "cd ~/deadpan-studio && bash local/start.sh"
echo.
echo The studio has stopped. Press any key to close this window.
pause >nul
