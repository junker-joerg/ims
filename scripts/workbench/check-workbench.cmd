@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"

pushd "%REPO_ROOT%" >nul
if errorlevel 1 (
  echo IMS Workbench check failed: repository root not found.
  exit /b 1
)

if not exist "frontend\dist\index.html" (
  echo IMS Workbench check failed: frontend\dist is missing. Build the frontend first.
  popd >nul
  exit /b 1
)

set "PYTHONPATH=%REPO_ROOT%\python_port;%PYTHONPATH%"

python -m ims.api.workbench_diagnostics --frontend-dist frontend/dist
if errorlevel 1 (
  popd >nul
  exit /b 1
)

python -m ims.api.workbench_readiness --frontend-dist frontend/dist
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
