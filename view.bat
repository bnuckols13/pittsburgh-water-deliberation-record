@echo off
REM Double-click this file to view the Pittsburgh Water Deliberation Record.
REM It starts a tiny local web server in this folder and opens the landing page
REM in your browser. Close this black window when you are done to stop the server.
cd /d "%~dp0"
echo.
echo   The Pittsburgh Water Deliberation Record
echo   ----------------------------------------
echo   Opening http://127.0.0.1:8137/ in your browser...
echo   Leave this window open while you browse. Close it to stop.
echo.
start "" http://127.0.0.1:8137/
python -m http.server 8137
