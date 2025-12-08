@echo off
REM ShizishanGPT Project Launcher for Windows
REM Simple batch file to run the complete agricultural AI system

title ShizishanGPT Agricultural AI System

echo.
echo ===============================================
echo   ShizishanGPT Agricultural AI System
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo Starting ShizishanGPT system...
echo.

REM Run the Python launcher
python run_project.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start ShizishanGPT system
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo ShizishanGPT system has been stopped.
pause