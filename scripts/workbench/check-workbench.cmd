@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "REPO_ROOT=%%~fI"

pushd "%REPO_ROOT%" >nul
if errorlevel 1 (
  echo IMS Workbench check failed: repository root not found.
  exit /b 1
)

if not defined IMS_FRONTEND_DIST set "IMS_FRONTEND_DIST=%REPO_ROOT%\frontend\dist"
if not defined IMS_METADATA_DB set "IMS_METADATA_DB=%REPO_ROOT%\.ims_workbench\metadata.sqlite"
if not defined IMS_WORKBENCH_HOST set "IMS_WORKBENCH_HOST=127.0.0.1"
if not defined IMS_WORKBENCH_PORT set "IMS_WORKBENCH_PORT=8000"

if not exist "%IMS_FRONTEND_DIST%\index.html" (
  echo IMS Workbench check failed: frontend dist is missing: %IMS_FRONTEND_DIST%
  popd >nul
  exit /b 1
)

set "PYTHONPATH=%REPO_ROOT%\python_port;%PYTHONPATH%"

if exist "%IMS_METADATA_DB%" (
  python -m ims.api.workbench_diagnostics --frontend-dist "%IMS_FRONTEND_DIST%" --db "%IMS_METADATA_DB%"
) else (
  python -m ims.api.workbench_diagnostics --frontend-dist "%IMS_FRONTEND_DIST%"
)
if errorlevel 1 (
  popd >nul
  exit /b 1
)

if exist "%IMS_METADATA_DB%" (
  python -m ims.api.workbench_readiness --frontend-dist "%IMS_FRONTEND_DIST%" --db "%IMS_METADATA_DB%"
) else (
  python -m ims.api.workbench_readiness --frontend-dist "%IMS_FRONTEND_DIST%"
)
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
