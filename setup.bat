@echo off
echo ========================================
echo Stock Management System - Quick Setup
echo ========================================
echo.

echo [1/5] Installing Python packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo.

echo [2/5] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo .env file created!
) else (
    echo .env file already exists
)
echo.

echo [3/5] Initializing database...
flask initdb
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo.

echo [4/5] Creating admin user...
flask create_admin
if %errorlevel% neq 0 (
    echo ERROR: Failed to create admin user
    pause
    exit /b 1
)
echo.

echo [5/5] Setup complete!
echo.
echo ========================================
echo Default Admin Credentials:
echo Username: admin
echo Password: admin123
echo ========================================
echo.
echo To start the application, run:
echo   python run.py
echo.
echo Then open your browser to:
echo   http://localhost:5000
echo.
pause
