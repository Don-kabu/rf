@echo off
setlocal
for %%I in ("%~dp0..") do set "PROJECT_ROOT=%%~fI"
cd /d "%PROJECT_ROOT%\frontend"
call npm.cmd run dev -- --host 127.0.0.1
endlocal
