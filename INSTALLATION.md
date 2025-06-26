# Installation & Release Instructions

## For macOS Users (End Users)

1. **Download the latest `.dmg` file** from the project releases (e.g., `Math Series Visualizer.dmg`).
2. **Open the `.dmg` file** by double-clicking it in Finder.
3. **Drag the `Math Series Visualizer` app icon** into the `Applications` folder shortcut in the same window.
4. **Eject the DMG** (right-click the mounted volume and select Eject).
5. **Open `Applications` and double-click `Math Series Visualizer`** to launch the app.
   - If you see a security warning, right-click the app and choose `Open` the first time.
6. **No Terminal or command line is required!**

**For macOS releases:**
- Only upload the `.dmg` file as the release asset. Do NOT include `.venv/`, `.github/`, `.vscode/`, or source code folders for end users.

---

## For Windows Users (End Users)

1. **Download the project ZIP** from the Windows release on GitHub.
2. **Extract the ZIP** to a folder.
3. **Double-click `setup_env.bat`** in the project folder.
   - This will automatically:
     - Create a Python virtual environment
     - Install all required packages
     - Launch the application
4. **(Optional) Create a desktop shortcut:**
   - Right-click `main.py` or the generated `.exe` (if you use PyInstaller in the future)
   - Choose "Send to > Desktop (create shortcut)"
   - Right-click the shortcut, choose Properties, and set the icon to `assets/app_icon.ico`

**For Windows releases:**
- Only include the necessary project files in the ZIP: code, assets, `setup_env.bat`, `requirements.txt`, and documentation. Do NOT include `.venv/`, `.github/`, or `.vscode/`.

---

## For Developers (All Platforms)

- **Python 3.10+ is required.**
- All dependencies are listed in `requirements.txt`.
- For advanced packaging or installer creation, see the project README and scripts.
- The `.venv/`, `.github/`, and `.vscode/` folders should NOT be included in release packages.

---

**Enjoy exploring mathematical series visually!**
