@echo off
cd ..
echo.
echo ========================================
echo   AUTO GIT PUSH
echo ========================================
echo.

REM Get current date and time (Windows 11 compatible)
for /f "tokens=2 delims==" %%I in ('powershell -command "Get-Date -Format \"yyyy-MM-dd HH:mm\""') do set datetime=%%I
set date_str=%datetime:~0,10%
set time_str=%datetime:~11,5%

echo [1/3] Adding all changes...
git add .

echo [2/3] Committing with timestamp...
git commit -m "Update %date_str% %time_str%"

echo [3/3] Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo   DONE! Pushed at %time_str%
echo ========================================
echo.
timeout /t 3
