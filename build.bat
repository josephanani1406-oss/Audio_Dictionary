@echo off
REM Audio Dictionary Build Script for Windows

echo Building Audio Dictionary as Windows EXE...

REM Check if PyInstaller is installed
pip list | find "pyinstaller" > nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Get the absolute paths
set ASSETS_PATH=%CD%\assets
set ICON_PATH=%CD%\assets\audio_dictionary_icon.ico

REM Build the executable
echo Building executable...
pyinstaller --onefile ^
    --windowed ^
    --name "AudioDictionary" ^
    --add-data "%ASSETS_PATH%;assets" ^
    --icon "%ICON_PATH%" ^
    --distpath ./dist ^
    --buildpath ./build ^
    --specpath ./build ^
    main.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful!
echo Executable created at: dist\AudioDictionary.exe
echo.
pause
