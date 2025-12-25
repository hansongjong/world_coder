@echo off
set PYTHON_EXE=C:\Users\blue\AppData\Local\Programs\Python\Python313\python.exe
set TEST_SCRIPT=tests/integration/test_business_scenario.py

echo [TEST] Starting End-to-End Business Scenario Test...
echo.

"%PYTHON_EXE%" "%TEST_SCRIPT%"

if %errorlevel% equ 0 (
    echo.
    echo [PASS] System Integrity Verified. Ready for Deployment.
) else (
    echo.
    echo [FAIL] Some tests failed. Check the logs above.
)
pause