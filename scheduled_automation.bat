@echo off
echo ============================================
echo   FALLOUT ROOM - SCHEDULED AUTOMATION
echo ============================================
echo %date% %time%

REM Navigate to your Django project directory
cd /d "D:\Personal Work\attacked.ai\falloutroom"

REM Verify we're in the correct directory
if not exist "manage.py" (
    echo ERROR: manage.py not found in current directory
    echo Current directory: %cd%
    echo Please check the project path
    pause
    exit /b 1
)

echo [1/4] Creating Incidents...

REM Run the Django management command
python manage.py auto_create_actions_deliverables

if %ERRORLEVEL% neq 0 (
    echo ERROR: Incident creation failed
    echo ============================================
    echo   AUTOMATION FAILED - CHECK ERROR LOGS
    echo ============================================
    pause
    exit /b 1
)

echo [2/4] Processing AI Analysis...
echo [3/4] Generating Actions...
echo [4/4] Creating Deliverables...

echo ============================================
echo   AUTOMATION COMPLETED SUCCESSFULLY
echo ============================================
pause
