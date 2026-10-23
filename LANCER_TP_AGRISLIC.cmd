@echo off
setlocal EnableExtensions
title Lancement du TP AgriSLIC

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"
set "VENV_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"

echo.
echo  AgriSLIC - lancement du demonstrateur du TP
echo  --------------------------------------------
echo  Le client affiche d'abord la simulation synthetique.
echo  Un resultat reel valide peut etre charge depuis backend\results\latest_result.json.
echo  Ce lanceur ne telecharge pas de donnees et ne lance aucun entrainement.
echo.

where node >nul 2>nul
if errorlevel 1 (
  echo ERREUR : Node.js est introuvable. Installe Node.js 22.12 ou plus recent.
  goto :failed
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
  echo ERREUR : npm est introuvable. Reinstalle Node.js avec npm.
  goto :failed
)

node -e "const [major,minor]=process.versions.node.split('.').map(Number);process.exit(major>22||(major===22&&minor>=12)?0:1)"
if errorlevel 1 (
  echo ERREUR : cette application demande Node.js 22.12 ou plus recent.
  goto :failed
)

if not exist "%VENV_PYTHON%" (
  echo Creation de l'environnement Python local...
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -m venv "%BACKEND_DIR%\.venv"
  ) else (
    where python >nul 2>nul
    if errorlevel 1 (
      echo ERREUR : Python 3 est introuvable. Installe Python 3.10 ou plus recent.
      goto :failed
    )
    python -m venv "%BACKEND_DIR%\.venv"
  )
  if errorlevel 1 (
    echo ERREUR : impossible de creer l'environnement Python.
    goto :failed
  )
)

"%VENV_PYTHON%" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
  echo ERREUR : Python 3.10 ou plus recent est requis.
  goto :failed
)

"%VENV_PYTHON%" -c "import fastapi, uvicorn" >nul 2>nul
if errorlevel 1 (
  echo Installation des dependances FastAPI...
  "%VENV_PYTHON%" -m pip install -r "%BACKEND_DIR%\requirements-lock.txt"
  if errorlevel 1 (
    echo ERREUR : installation Python echouee. Verifie la connexion Internet.
    goto :failed
  )
)

if not exist "%FRONTEND_DIR%\node_modules\vite\bin\vite.js" (
  echo Installation des dependances Vue.js...
  pushd "%FRONTEND_DIR%"
  call npm.cmd install
  if errorlevel 1 (
    popd
    echo ERREUR : installation npm echouee. Verifie la connexion Internet.
    goto :failed
  )
  popd
)

echo.
echo Ouverture de deux fenetres : FastAPI et client Vue.js.
echo Client : http://localhost:5173
echo API    : http://127.0.0.1:8000/docs
echo Ferme ces deux fenetres pour arreter le TP.
echo.

start "AgriSLIC - API FastAPI" cmd.exe /k ""%PROJECT_ROOT%scripts\run_api.cmd""
start "AgriSLIC - Client Vue" cmd.exe /k ""%PROJECT_ROOT%scripts\run_vue.cmd""
timeout /t 3 /nobreak >nul
start "" "http://localhost:5173"
endlocal
exit /b 0

:failed
echo.
echo Consulte doc\LANCEMENT_RAPIDE.md pour les prerequis et les erreurs courantes.
pause
endlocal
exit /b 1
