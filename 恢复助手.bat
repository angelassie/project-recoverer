@echo off
set PYTHON_CMD=C:\Users\PC-HOME\AppData\Local\Programs\Python\Python312\python.exe
echo ================================================
echo    Codex Recovery Assistant
echo ================================================
echo.
echo Current project: %cd%
echo.
"%PYTHON_CMD%" "%~dp0core\recoverer.py" "%cd%"
echo.
pause