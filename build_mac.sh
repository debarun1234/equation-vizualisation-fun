#!/bin/bash
# === Mathematical Series Visualizer macOS DMG Build Script ===
# This script must be run on macOS with Python 3 and Xcode command line tools installed.
# It will create a .app and a .dmg for easy distribution.

set -e

# Step 1: Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate
PYTHON=".venv/bin/python"
PIP=".venv/bin/pip"

# Step 2: Install requirements
$PIP install --upgrade pip
$PIP install PyQt5 matplotlib numpy scipy Pillow imageio py2app

# Step 2.1: Check for create-dmg tool
if ! command -v create-dmg &> /dev/null; then
    echo "ERROR: 'create-dmg' is not installed. Please install it with: brew install create-dmg"
    exit 1
fi

# Step 2.5: Convert PNG icon to ICNS (macOS icon format)
ICON_PNG="assets/app_icon.png"
ICON_ICNS="assets/app_icon.icns"
if [ -f "$ICON_PNG" ]; then
    mkdir -p icon.iconset
    sips -z 16 16     $ICON_PNG --out icon.iconset/icon_16x16.png
    sips -z 32 32     $ICON_PNG --out icon.iconset/icon_16x16@2x.png
    sips -z 32 32     $ICON_PNG --out icon.iconset/icon_32x32.png
    sips -z 64 64     $ICON_PNG --out icon.iconset/icon_32x32@2x.png
    sips -z 128 128   $ICON_PNG --out icon.iconset/icon_128x128.png
    sips -z 256 256   $ICON_PNG --out icon.iconset/icon_128x128@2x.png
    sips -z 256 256   $ICON_PNG --out icon.iconset/icon_256x256.png
    sips -z 512 512   $ICON_PNG --out icon.iconset/icon_256x256@2x.png
    sips -z 512 512   $ICON_PNG --out icon.iconset/icon_512x512.png
    cp $ICON_PNG icon.iconset/icon_512x512@2x.png
    iconutil -c icns icon.iconset -o $ICON_ICNS
    rm -rf icon.iconset
    echo "Created $ICON_ICNS for macOS app bundle."
else
    echo "Warning: $ICON_PNG not found. App will use default icon."
fi

# Step 3: Create setup.py for py2app
cat > setup.py <<EOF
from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt5', 'matplotlib', 'numpy', 'scipy', 'PIL', 'imageio'],
    'iconfile': 'assets/app_icon.icns',
    'includes': ['PIL'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
EOF

# Step 4: Build the .app bundle
$PYTHON setup.py py2app

# Check if the .app bundle was created
if [ ! -d "dist/main.app" ]; then
    echo "ERROR: dist/main.app was not created. Check the output above for errors during py2app packaging."
    exit 1
fi

# Step 5: Create the DMG (requires create-dmg)
# Add Applications shortcut for drag-and-drop install
create-dmg \
  --volname "Math Series Visualizer" \
  --window-pos 200 120 \
  --window-size 500 300 \
  --icon-size 128 \
  --icon "main.app" 120 140 \
  --app-drop-link 380 140 \
  dist/main.app

echo "DMG creation complete. Check the dist/ folder."
