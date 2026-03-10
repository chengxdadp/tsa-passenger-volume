@echo off
setlocal EnableDelayedExpansion

set "ENV_NAME=pdf"
set "SCRIPT=%~dp0script\update.py"

echo ============================================================
echo  TSA Passenger Volume Data Update
echo  %date% %time%
echo ============================================================
echo.

:: Usage:
::   update_tsa_data.bat              -- scrape current year
::   update_tsa_data.bat --year 2025  -- backfill a specific year
::   update_tsa_data.bat --charts-only -- regenerate charts only

set "CONDA_EXE="
if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" set "CONDA_EXE=%USERPROFILE%\anaconda3\Scripts\conda.exe"
if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" set "CONDA_EXE=%USERPROFILE%\miniconda3\Scripts\conda.exe"
if exist "C:\ProgramData\anaconda3\Scripts\conda.exe" set "CONDA_EXE=C:\ProgramData\anaconda3\Scripts\conda.exe"
if exist "C:\ProgramData\miniconda3\Scripts\conda.exe" set "CONDA_EXE=C:\ProgramData\miniconda3\Scripts\conda.exe"
if exist "%LOCALAPPDATA%\anaconda3\Scripts\conda.exe" set "CONDA_EXE=%LOCALAPPDATA%\anaconda3\Scripts\conda.exe"

if "%CONDA_EXE%"=="" (
    echo [ERROR] conda not found. Please install Anaconda or Miniconda.
    goto :fail
)
echo [OK] conda: %CONDA_EXE%
echo [RUN] conda run -n %ENV_NAME% python update.py %*
echo.

"%CONDA_EXE%" run -n "%ENV_NAME%" python "%SCRIPT%" %*
set "EXIT_CODE=%errorlevel%"

echo.
echo ============================================================
if %EXIT_CODE%==0 (
    echo [DONE] Update succeeded   %date% %time%
) else (
    echo [FAIL] Exit code: %EXIT_CODE%   %date% %time%
)
echo ============================================================
pause
exit /b %EXIT_CODE%

:fail
echo ============================================================
pause
exit /b 1
