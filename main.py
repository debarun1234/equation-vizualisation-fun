#!/usr/bin/env python3
"""
Mathematical Series Visualization Application

Main entry point for the PyQt5-based application that visualizes
mathematical series using animated epicycles and graphs.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add the current directory to the path to enable imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.enhanced_main_window import EnhancedMainWindow as MainWindow


def main():
    """Initialize and run the application."""
    # Enable high DPI display support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Mathematical Series Visualizer")
    app.setApplicationVersion("1.0.0")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
