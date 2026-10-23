@echo off
setlocal
for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
set "VENV_PYTHON=%PROJECT_ROOT%\backend\.venv\Scripts\python.exe"
cd /d "%PROJECT_ROOT%\backend"
"%VENV_PYTHON%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
endlocal
