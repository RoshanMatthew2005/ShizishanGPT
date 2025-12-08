#!/bin/bash

# ShizishanGPT Project Launcher for Linux/macOS
# Simple shell script to run the complete agricultural AI system

echo ""
echo "==============================================="
echo "   ShizishanGPT Agricultural AI System"
echo "==============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed"
        echo "Please install Python and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js and try again"
    exit 1
fi

echo "Starting ShizishanGPT system..."
echo ""

# Run the Python launcher
$PYTHON_CMD run_project.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start ShizishanGPT system"
    echo "Check the error messages above"
    exit 1
fi

echo ""
echo "ShizishanGPT system has been stopped."