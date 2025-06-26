<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Mathematical Series Visualization Project

This is a Python application for visualizing mathematical series like Fourier Series and Taylor Series using animated rotating vectors (epicycles) and graphs.

## Project Structure
- `/main.py`: Main application entry point
- `/ui/`: PyQt5 GUI components and layout management
- `/visuals/`: Mathematical calculations and animation logic
- `/config/`: Theme configurations and color presets
- `/utils/`: Helper functions for math, plotting, and file operations
- `/assets/`: Generated images and GIF files

## Key Features
- Interactive PyQt5 GUI with matplotlib integration
- Animated epicycle visualization for mathematical series
- Support for Fourier series (square wave, triangle wave, sawtooth)
- Taylor series expansions
- Lissajous curves
- Play/pause/reset controls
- Save as PNG/GIF functionality
- Multiple color themes

## Development Guidelines
- Use PyQt5 for GUI components
- Integrate matplotlib.animation for smooth animations
- Maintain modular code structure with clear separation of concerns
- Optimize performance for 20+ terms in series calculations
- Follow Python best practices and PEP 8 style guidelines
