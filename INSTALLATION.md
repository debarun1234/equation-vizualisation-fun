# Installation Instructions

## For macOS Users

1. **Download the latest `.dmg` file** from the project releases or your distribution source.
2. **Open the `.dmg` file** by double-clicking it in Finder.
3. **Drag the `Math Series Visualizer` app icon** into the `Applications` folder shortcut in the same window.
4. **Eject the DMG** (right-click the mounted volume and select Eject).
5. **Open `Applications` and double-click `Math Series Visualizer`** to launch the app.
   - If you see a security warning, right-click the app and choose `Open` the first time.
6. **No Terminal or command line is required!**

---

## For Windows Users

1. **Download the project ZIP or clone the repository.**
2. **Double-click `setup_env.bat`** in the project folder.
   - This will automatically:
     - Create a Python virtual environment
     - Install all required packages
     - Launch the application
3. **(Optional) Create a desktop shortcut:**
   - Right-click `main.py` or the generated `.exe` (if you use PyInstaller in the future)
   - Choose "Send to > Desktop (create shortcut)"
   - Right-click the shortcut, choose Properties, and set the icon to `assets/app_icon.ico`

---

## For Developers (All Platforms)

- **Python 3.10+ is required.**
- All dependencies are listed in `requirements.txt`.
- For advanced packaging or installer creation, see the project README and scripts.

---

**Enjoy exploring mathematical series visually!**
