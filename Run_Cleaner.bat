@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  set "PYTHON=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3 not found. Install Python 3 and try again.
    pause
    exit /b 1
  )
  set "PYTHON=python"
)
echo.
echo =========================================
echo    DUPLICATE PAIR CLEANER v2.2.0
echo =========================================
echo.
echo Pick a folder, choose two extensions, and review the changes.
echo Nothing changes until you type YES.
echo.
%PYTHON% "%~dp0file_pair_cleaner.py" --select-folder --ask-extensions --ask-subfolders --page-size 5
set "RESULT=%ERRORLEVEL%"
echo.
pause
exit /b %RESULT%
