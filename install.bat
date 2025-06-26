@echo off
REM PDF Cracker Installation Script for Windows
REM Installs dependencies and sets up the environment

setlocal EnableDelayedExpansion

echo.
echo 🔐 PDF Cracker Installation Script for Windows
echo ===============================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running with administrator privileges
) else (
    echo [WARNING] Not running as administrator. Some installations may fail.
    echo [WARNING] Consider running as administrator for best results.
    echo.
)

REM Check Python installation
echo [INFO] Checking Python installation...
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
    echo [SUCCESS] Python is installed: !PYTHON_VERSION!
) else (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Please install Python from https://python.org/downloads/
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Note: tkinter no longer needed for CLI-only version
echo [INFO] CLI-only version - no GUI dependencies needed

REM Check pip
echo [INFO] Checking pip installation...
python -m pip --version >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] pip is available
) else (
    echo [ERROR] pip is not available
    echo [INFO] Installing pip...
    python -m ensurepip --upgrade
)

REM Install Python requirements
echo [INFO] Installing Python dependencies...
if exist requirements.txt (
    echo [INFO] Installing from requirements.txt...
    python -m pip install -r requirements.txt
) else (
    echo [INFO] Installing basic dependencies...
    python -m pip install tkinter-dnd2 2>nul || echo [WARNING] tkinter-dnd2 installation failed (optional)
)

REM Check for John the Ripper
echo [INFO] Checking for John the Ripper...
john --version >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] John the Ripper is installed
) else (
    echo [WARNING] John the Ripper not found in PATH
    echo [INFO] Please install John the Ripper manually:
    echo [INFO] 1. Download from: https://www.openwall.com/john/
    echo [INFO] 2. Or use chocolatey: choco install john
    echo [INFO] 3. Add to PATH environment variable
    echo.
)

REM Check for crunch (optional on Windows)
echo [INFO] Checking for crunch...
crunch -h >nul 2>&1
if %errorLevel% == 0 (
    echo [SUCCESS] crunch is installed
) else (
    echo [WARNING] crunch not found (optional for Windows)
    echo [INFO] crunch is not commonly available on Windows
    echo [INFO] The application will use built-in password generation
    echo.
)

REM Create convenience batch files
echo [INFO] Creating convenience scripts...

REM Create wordlist generator batch file
echo @echo off > pdf-wordlist.bat
echo cd /d "%%~dp0" >> pdf-wordlist.bat
echo python src\utils\wordlist_gen.py %%* >> pdf-wordlist.bat

REM Create comprehensive wordlist generator batch file
echo @echo off > pdf-comprehensive-wordlist.bat
echo cd /d "%%~dp0" >> pdf-comprehensive-wordlist.bat
echo python src\utils\comprehensive_wordlist.py %%* >> pdf-comprehensive-wordlist.bat

REM Create comprehensive cracker batch file
echo @echo off > pdf-crack.bat
echo cd /d "%%~dp0" >> pdf-crack.bat
echo python src\utils\comprehensive_crack.py %%* >> pdf-crack.bat

echo [SUCCESS] Created convenience scripts: pdf-wordlist.bat, pdf-comprehensive-wordlist.bat, pdf-crack.bat

REM Final verification
echo.
echo [INFO] Verifying installation...
python --version
echo.

echo [SUCCESS] Installation completed!
echo.
echo Usage:
echo   Generate basic wordlist:       pdf-wordlist.bat --start 2020 --end 2025 --output passwords.txt
echo   Generate comprehensive list:   pdf-comprehensive-wordlist.bat --estimate-only
echo   Crack PDF:                     pdf-crack.bat assets\document.pdf
echo   Direct Python:                 python src\utils\comprehensive_crack.py document.pdf
echo.
echo For more options: pdf-wordlist.bat --help or pdf-crack.bat --help
echo.

REM Additional Windows-specific instructions
echo [INFO] Windows-specific notes:
echo   - If you encounter permission errors, run as administrator
echo   - Windows Defender may flag password cracking tools
echo   - Add exclusions for this folder if needed
echo.

pause