@echo off
REM === Mathematical Series Visualizer Environment Setup ===
REM This script creates a virtual environment and installs all required packages.
REM It uses the exact versions from requirements.txt (embedded below for integrity).

REM Step 1: Create virtual environment
python -m venv .venv

REM Step 2: Activate virtual environment
call .venv\Scripts\activate

REM Step 3: Install required packages (from embedded list)
REM (This ensures no tampering with requirements.txt is possible)

REM --- Begin requirements ---
REM The following lines are the required packages. Do not edit below this line.
REM (If you need to update, update this script and requirements.txt together)
REM ---
REM PyQt5==5.15.9
REM matplotlib==3.7.2
REM numpy==1.24.3
REM scipy==1.11.1
REM Pillow==10.0.0
REM imageio==2.31.1
REM --- End requirements ---

pip install PyQt5==5.15.9 matplotlib==3.7.2 numpy==1.24.3 scipy==1.11.1 Pillow==10.0.0 imageio==2.31.1

REM Step 4: Run the application
python main.py

@echo on
