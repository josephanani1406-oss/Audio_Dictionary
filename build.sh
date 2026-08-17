#!/bin/bash
# Audio Dictionary Build Script for Linux/macOS

echo "Building Audio Dictionary as Executable..."

# Check if PyInstaller is installed
pip list | grep pyinstaller > /dev/null
if [ $? -ne 0 ]; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Get the absolute paths
ASSETS_PATH=$(pwd)/assets
ICON_PATH=$(pwd)/assets/audio_dictionary_icon.ico

# Build the executable
echo "Building executable..."
pyinstaller --onefile \
    --windowed \
    --name "AudioDictionary" \
    --add-data "$ASSETS_PATH:assets" \
    --distpath ./dist \
    --buildpath ./build \
    --specpath ./build \
    main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Build successful!"
    echo "Executable created at: dist/AudioDictionary"
else
    echo "Build failed!"
    exit 1
fi
