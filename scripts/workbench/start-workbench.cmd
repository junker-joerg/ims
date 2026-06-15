@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"

pushd "%REPO_ROOT%" >nul
if errorlevel 1 (
  echo IMS Workbench start failed: repository root not found.
  exit /b 1
)

if not exist "frontend\dist\index.html" (
  echo IMS Workbench start failed: frontend\dist is missing. Build the frontend first.
  popd >nul
  exit /b 1
)

set "PYTHONPATH=%REPO_ROOT%\python_port;%PYTHONPATH%"

echo Starting IMS Workbench at http://127.0.0.1:8000/
python -m uvicorn ims.api.app:app --app-dir python_port --host 127.0.0.1 --port 8000
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
