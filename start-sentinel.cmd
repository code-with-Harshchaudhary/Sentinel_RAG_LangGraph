@echo off
setlocal
cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
  echo [Sentinel] Python tool "uv" is not installed or is not on PATH.
  echo Install it from https://docs.astral.sh/uv/ and run this file again.
  pause
  exit /b 1
)

where npx >nul 2>nul
if errorlevel 1 (
  echo [Sentinel] Node.js is not installed or "npx" is not on PATH.
  echo Install the current Node.js LTS release and run this file again.
  pause
  exit /b 1
)

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo [Sentinel] Created .env from .env.example.
  echo Add your GEMINI_API_KEY to .env, then run this file again.
  notepad ".env"
  exit /b 1
)

if not exist "data\inputs" mkdir "data\inputs"
if not exist "data\rag_storage" mkdir "data\rag_storage"
if not exist "data\prompts" mkdir "data\prompts"

echo [Sentinel] Preparing the React interface...
pushd "lightrag_webui"
call npx --yes bun@1 install --frozen-lockfile
if errorlevel 1 goto :frontend_error
call npx --yes bun@1 run build
if errorlevel 1 goto :frontend_error
popd

echo.
echo [Sentinel] Starting at http://127.0.0.1:9621/webui/
echo [Sentinel] Press Ctrl+C to stop.
echo.
uv run sentinel-rag-server --host 127.0.0.1 --port 9621
exit /b %errorlevel%

:frontend_error
popd
echo [Sentinel] The interface build failed. Review the error above.
pause
exit /b 1
