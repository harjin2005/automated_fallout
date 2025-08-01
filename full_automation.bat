@echo off
REM Change to the project directory (including drive letter)
cd /d "D:\Personal Work\attacked.ai\falloutroom"

echo ============================================
echo    FALLOUT ROOM - AUTOMATED INCIDENT RESPONSE
echo ============================================
echo.

echo [STEP 1/4] Creating Incident...
python manage.py auto_create_incidents

echo.
echo [STEP 2/4] Generating Action Plans...
python manage.py auto_create_actions_deliverables

echo.
echo [STEP 3/4] AI Document Generation...
python manage.py trigger_ai_generation

echo.
echo [STEP 4/4] Automation Complete!
echo.
echo Check Django Admin for results:
echo http://localhost:8000/admin/
echo.
echo ============================================
echo    INCIDENT RESPONSE AUTOMATION SUCCESSFUL
echo ============================================
pause
