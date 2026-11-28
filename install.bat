@echo off
setlocal EnableExtensions

set "PANDAY_REPO=%PANDAY_REPO%"
if not defined PANDAY_REPO set "PANDAY_REPO=GG-Santos/panday"
set "PANDAY_VERSION=%PANDAY_VERSION%"
if not defined PANDAY_VERSION set "PANDAY_VERSION=v1.1.2"
set "PANDAY_ARCHIVE=%PANDAY_ARCHIVE%"
if not defined PANDAY_ARCHIVE set "PANDAY_ARCHIVE=panday-%PANDAY_VERSION%.zip"
set "PANDAY_HOME=%PANDAY_HOME%"
if not defined PANDAY_HOME set "PANDAY_HOME=%LOCALAPPDATA%\Panday"

where powershell >nul 2>&1 || (
  echo PowerShell is required.
  exit /b 2
)
where uv >nul 2>&1 || (
  echo uv is required. Install it from https://docs.astral.sh/uv/getting-started/installation/
  exit /b 2
)

set "ARCHIVE=%TEMP%\panday-%RANDOM%.zip"
set "URL=https://github.com/%PANDAY_REPO%/releases/download/%PANDAY_VERSION%/%PANDAY_ARCHIVE%"
echo Downloading Panday from %URL%
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -UseBasicParsing -Uri '%URL%' -OutFile '%ARCHIVE%'"
if errorlevel 1 (
  echo Download failed.
  exit /b 1
)

if not exist "%PANDAY_HOME%" mkdir "%PANDAY_HOME%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%ARCHIVE%' -DestinationPath '%PANDAY_HOME%' -Force"
if errorlevel 1 (
  echo Archive extraction failed.
  exit /b 1
)

uv tool install --editable --force "%PANDAY_HOME%\cli"
if errorlevel 1 exit /b 1
panday init

echo.
echo Panday is installed. Add this path to %USERPROFILE%\.panday\config.toml if it is not already registered:
echo [registries]
echo paths = ["%PANDAY_HOME:\=/%/skills"]
echo.
echo Verify with: panday --version ^&^& panday --json doctor
del /q "%ARCHIVE%" >nul 2>&1
exit /b 0
