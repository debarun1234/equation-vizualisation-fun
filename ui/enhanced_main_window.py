"""
Enhanced main window with formula display, parameter controls, and individual trace visualization.
"""

import sys
import os
import numpy as np
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QComboBox, QPushButton, QLabel, QSlider, QSpinBox,
                             QGroupBox, QGridLayout, QTextEdit, QSplitter, 
                             QFrame, QDoubleSpinBox, QCheckBox, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches

# Import our custom utilities
from utils.concept_loader import (load_visualization_concepts, get_dropdown_options, 
                                 parse_dropdown_selection, get_all_concepts_flat)
from utils.math_utils import generate_curve_from_concept, ConceptMath
from config.themes import get_theme_colors, get_epicycle_colors


class EnhancedAnimationCanvas(FigureCanvas):
    """Enhanced canvas with three panels: epicycles, individual traces, combined result"""
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(18, 8), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Create three subplots
        self.ax_epicycles = self.fig.add_subplot(131)    # Left: Epicycles
        self.ax_individual = self.fig.add_subplot(132)   # Middle: Individual traces
        self.ax_combined = self.fig.add_subplot(133)     # Right: Combined curve
        
        # Animation properties
        self.animation = None
        self.is_playing = False
        self.current_time = 0
        self.time_step = 0.05
        self.max_time = 4 * np.pi
        
        # Data storage
        self.epicycles = []
        self.curve_x = []
        self.curve_y = []
        self.traced_points = []
        self.individual_traces = []  # Store traces for each epicycle
        self.current_concept = None
        
        # Adjustable parameters
        self.amplitude_scale = 1.0
        self.frequency_scale = 1.0
        self.phase_offset = 0.0
        self.show_individual_traces = True
        
        self.setup_plots()
    
    def setup_plots(self):
        """Initialize the three plot panels"""
        # Setup epicycles plot (left)
        self.ax_epicycles.set_xlim(-4, 4)
        self.ax_epicycles.set_ylim(-4, 4)
        self.ax_epicycles.set_aspect('equal')
        self.ax_epicycles.grid(True, alpha=0.3)
        self.ax_epicycles.set_title('Epicycles Animation', fontsize=12, fontweight='bold')
        
        # Setup individual traces plot (middle)
        self.ax_individual.set_xlim(0, 4 * np.pi)
        self.ax_individual.set_ylim(-3, 3)
        self.ax_individual.grid(True, alpha=0.3)
        self.ax_individual.set_title('Individual Epicycle Traces', fontsize=12, fontweight='bold')
        self.ax_individual.set_xlabel('Time (t)')
        self.ax_individual.set_ylabel('Amplitude')
        
        # Setup combined curve plot (right)
        self.ax_combined.set_xlim(0, 4 * np.pi)
        self.ax_combined.set_ylim(-3, 3)
        self.ax_combined.grid(True, alpha=0.3)
        self.ax_combined.set_title('Combined Result', fontsize=12, fontweight='bold')
        self.ax_combined.set_xlabel('Time (t)')
        self.ax_combined.set_ylabel('Amplitude')
        
        # Apply theme
        self.apply_theme('dark')
        self.fig.tight_layout()
    
    def apply_theme(self, theme_name: str = 'dark'):
        """Apply color theme to all plots"""
        colors = get_theme_colors(theme_name)
        
        # Set background colors
        self.fig.patch.set_facecolor(colors['background'])
        for ax in [self.ax_epicycles, self.ax_individual, self.ax_combined]:
            ax.set_facecolor(colors['plot_background'])
            ax.xaxis.label.set_color(colors['text'])
            ax.yaxis.label.set_color(colors['text'])
            ax.title.set_color(colors['text'])
            ax.tick_params(colors=colors['text'])
            
            # Set spine colors
            for spine in ax.spines.values():
                spine.set_color(colors['text'])
    
    def set_concept_data(self, concept: Dict[str, Any], n_terms: int = 10):
        """Set the mathematical concept to visualize"""
        self.current_concept = concept
        
        # Generate curve and epicycle data with current parameters
        self.curve_x, self.curve_y, self.epicycles = generate_curve_from_concept(
            concept, n_terms, 1000
        )
        
        # Apply parameter adjustments
        for epicycle in self.epicycles:
            epicycle['radius'] *= self.amplitude_scale
            epicycle['frequency'] *= self.frequency_scale
            epicycle['phase'] += self.phase_offset
        
        # Initialize individual traces
        self.individual_traces = [[] for _ in range(len(self.epicycles))]
        self.traced_points = []
        self.current_time = 0
        
        # Update plot limits
        if len(self.curve_y) > 0:
            y_range = max(abs(np.max(self.curve_y)), abs(np.min(self.curve_y))) * self.amplitude_scale
            self.ax_individual.set_ylim(-y_range * 1.2, y_range * 1.2)
            self.ax_combined.set_ylim(-y_range * 1.2, y_range * 1.2)
        
        # Calculate epicycle system range
        total_radius = sum(ep['radius'] for ep in self.epicycles)
        if total_radius > 0:
            margin = total_radius * 1.2
            self.ax_epicycles.set_xlim(-margin, margin)
            self.ax_epicycles.set_ylim(-margin, margin)
        
        # Update plot titles
        concept_name = concept.get('name', 'Unknown')
        concept_type = concept.get('type', 'Unknown')
        self.ax_epicycles.set_title(f'Epicycles: {concept_name}', fontsize=12, fontweight='bold')
        self.ax_individual.set_title(f'Individual Components: {concept_name}', fontsize=12, fontweight='bold')
        self.ax_combined.set_title(f'{concept_type}: {concept_name}', fontsize=12, fontweight='bold')
        
        self.draw()
    
    def update_parameters(self, amplitude: float, frequency: float, phase: float):
        """Update mathematical parameters and refresh visualization"""
        self.amplitude_scale = amplitude
        self.frequency_scale = frequency
        self.phase_offset = phase
        
        if self.current_concept:
            # Re-calculate with new parameters
            n_terms = len(self.epicycles) if self.epicycles else 10
            self.set_concept_data(self.current_concept, n_terms)
    
    def animate_frame(self, frame):
        """Enhanced animation function with individual trace tracking"""
        if not self.is_playing or not self.epicycles:
            return []
        
        # Clear all plots
        self.ax_epicycles.clear()
        self.ax_individual.clear()
        self.ax_combined.clear()
        
        # Reconfigure plots
        self.setup_plots()
        
        # Get selected color palette
        epicycle_colors = get_epicycle_colors('vibrant')
        
        # Get current epicycle positions
        positions = ConceptMath.get_epicycle_chain_positions(self.epicycles, self.current_time)
        
        # Draw connecting lines between epicycle centers
        for i in range(len(positions) - 1):
            start_pos = positions[i]
            end_pos = positions[i + 1]
            color = epicycle_colors[i % len(epicycle_colors)]
            
            self.ax_epicycles.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], 
                                color=color, linewidth=2.5, alpha=0.6, linestyle='-')
        
        # Draw epicycles with enhanced styling
        for i, (epicycle, pos) in enumerate(zip(self.epicycles, positions[1:])):
            center = positions[i]
            radius = epicycle['radius']
            color = epicycle_colors[i % len(epicycle_colors)]
            
            # Draw circle
            circle = patches.Circle(center, radius, fill=False, color=color, 
                                  linewidth=2.5, alpha=0.8, linestyle='-')
            self.ax_epicycles.add_patch(circle)
            
            # Draw radius line
            self.ax_epicycles.plot([center[0], pos[0]], [center[1], pos[1]], 
                                color=color, linewidth=3, alpha=0.9, zorder=5)
            
            # Draw center and current position
            self.ax_epicycles.plot(center[0], center[1], 'o', color=color, 
                                 markersize=6, alpha=0.9, markeredgecolor='white', 
                                 markeredgewidth=1, zorder=6)
            self.ax_epicycles.plot(pos[0], pos[1], 'o', color=color, 
                                 markersize=5, alpha=0.8, zorder=7)
            
            # Track individual epicycle trace
            if self.show_individual_traces:
                # Calculate individual epicycle contribution
                individual_value = epicycle['radius'] * np.sin(
                    epicycle['frequency'] * self.current_time + epicycle['phase']
                )
                self.individual_traces[i].append((self.current_time, individual_value))
                
                # Limit trace length for performance
                if len(self.individual_traces[i]) > 1000:
                    self.individual_traces[i] = self.individual_traces[i][-1000:]
        
        # Draw final point with special highlighting
        if positions:
            final_pos = positions[-1]
            self.ax_epicycles.plot(final_pos[0], final_pos[1], 'o', color='white', 
                                 markersize=12, alpha=0.9, zorder=8)
            self.ax_epicycles.plot(final_pos[0], final_pos[1], 'o', color='#FF0040', 
                                 markersize=10, alpha=1.0, zorder=9)
            self.ax_epicycles.plot(final_pos[0], final_pos[1], 'o', color='#FFFFFF', 
                                 markersize=4, alpha=1.0, zorder=10)
            
            # Add to combined trace
            self.traced_points.append((self.current_time, final_pos[1]))
            if len(self.traced_points) > 1000:
                self.traced_points = self.traced_points[-1000:]
        
        # Draw individual traces
        if self.show_individual_traces:
            for i, trace in enumerate(self.individual_traces):
                if len(trace) > 1:
                    times, values = zip(*trace)
                    color = epicycle_colors[i % len(epicycle_colors)]
                    self.ax_individual.plot(times, values, color=color, 
                                          linewidth=2, alpha=0.7, 
                                          label=f'Epicycle {i+1}')
                    
                    # Mark current position
                    if times:
                        self.ax_individual.plot(times[-1], values[-1], 'o', 
                                              color=color, markersize=5, zorder=5)
        
        # Draw combined curve
        if self.traced_points and len(self.traced_points) > 1:
            times, values = zip(*self.traced_points)
            
            # Gradient effect for combined curve
            n_segments = min(len(times) - 1, 50)
            segment_size = max(1, len(times) // n_segments)
            
            gradient_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
            
            for i in range(0, len(times) - segment_size, segment_size):
                end_idx = min(i + segment_size, len(times))
                segment_times = times[i:end_idx]
                segment_values = values[i:end_idx]
                
                color_idx = (i // segment_size) % len(gradient_colors)
                color = gradient_colors[color_idx]
                alpha = 0.4 + 0.6 * (i / len(times))
                
                self.ax_combined.plot(segment_times, segment_values, color=color, 
                                    linewidth=2.5, alpha=alpha, zorder=3)
            
            # Current position marker
            self.ax_combined.plot(times[-1], values[-1], 'o', color='#FF0040', 
                                markersize=8, alpha=1.0, zorder=10)
        
        # Update time
        self.current_time += self.time_step
        if self.current_time > self.max_time:
            self.current_time = 0
            self.traced_points = []
            self.individual_traces = [[] for _ in range(len(self.epicycles))]
        
        # Apply theme and update
        self.apply_theme('dark')
        
        return []
    
    def start_animation(self):
        """Start the animation"""
        if self.animation is None:
            self.animation = FuncAnimation(
                self.fig, self.animate_frame, interval=50, blit=False, cache_frame_data=False
            )
        self.is_playing = True
    
    def stop_animation(self):
        """Stop the animation"""
        self.is_playing = False
    
    def reset_animation(self):
        """Reset animation to beginning"""
        self.current_time = 0
        self.traced_points = []
        self.individual_traces = [[] for _ in range(len(self.epicycles))]
        self.stop_animation()
        
        # Redraw static state
        for ax in [self.ax_epicycles, self.ax_individual, self.ax_combined]:
            ax.clear()
        self.setup_plots()
        self.draw()


class FormulaPanel(QWidget):
    """Panel for displaying mathematical formulas and adjustable parameters"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Create the formula display and parameter controls"""
        layout = QVBoxLayout(self)
        
        # Formula display section
        formula_group = QGroupBox("Mathematical Formula")
        formula_layout = QVBoxLayout(formula_group)
        
        self.formula_display = QTextEdit()
        self.formula_display.setMaximumHeight(100)
        self.formula_display.setReadOnly(True)
        self.formula_display.setFont(QFont("Courier", 10))
        formula_layout.addWidget(self.formula_display)
        
        layout.addWidget(formula_group)
        
        # Parameter controls section
        params_group = QGroupBox("Adjustable Parameters")
        params_layout = QGridLayout(params_group)
        
        # Amplitude control
        params_layout.addWidget(QLabel("Amplitude Scale:"), 0, 0)
        self.amplitude_slider = QDoubleSpinBox()
        self.amplitude_slider.setRange(0.1, 5.0)
        self.amplitude_slider.setValue(1.0)
        self.amplitude_slider.setSingleStep(0.1)
        params_layout.addWidget(self.amplitude_slider, 0, 1)
        
        # Frequency control
        params_layout.addWidget(QLabel("Frequency Scale:"), 1, 0)
        self.frequency_slider = QDoubleSpinBox()
        self.frequency_slider.setRange(0.1, 3.0)
        self.frequency_slider.setValue(1.0)
        self.frequency_slider.setSingleStep(0.1)
        params_layout.addWidget(self.frequency_slider, 1, 1)
        
        # Phase control
        params_layout.addWidget(QLabel("Phase Offset:"), 2, 0)
        self.phase_slider = QDoubleSpinBox()
        self.phase_slider.setRange(-np.pi, np.pi)
        self.phase_slider.setValue(0.0)
        self.phase_slider.setSingleStep(0.1)
        params_layout.addWidget(self.phase_slider, 2, 1)
        
        # Individual traces toggle
        self.show_individual_cb = QCheckBox("Show Individual Traces")
        self.show_individual_cb.setChecked(True)
        params_layout.addWidget(self.show_individual_cb, 3, 0, 1, 2)
        
        layout.addWidget(params_group)
        
        # Concept information section
        info_group = QGroupBox("Concept Information")
        info_layout = QVBoxLayout(info_group)
        
        self.info_display = QTextEdit()
        self.info_display.setMaximumHeight(80)
        self.info_display.setReadOnly(True)
        info_layout.addWidget(self.info_display)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
    
    def update_formula(self, concept: Dict[str, Any]):
        """Update the formula display with the current concept"""
        if not concept:
            return
        
        formula = concept.get('equation', 'No equation available')
        concept_name = concept.get('name', 'Unknown')
        concept_type = concept.get('type', 'Unknown')
        visual_desc = concept.get('visual', 'No description')
        
        # Format the formula using scientific notation
        formatted_formula = self.format_scientific_formula(formula, concept_name, concept_type)
        
        # Set the formatted formula display
        self.formula_display.setText(formatted_formula)
        
        # Format the information display
        info_text = f"Type: {concept_type}\nVisual: {visual_desc}"
        self.info_display.setText(info_text)
    
    def get_parameters(self):
        """Get current parameter values"""
        return {
            'amplitude': self.amplitude_slider.value(),
            'frequency': self.frequency_slider.value(),
            'phase': self.phase_slider.value(),
            'show_individual': self.show_individual_cb.isChecked()
        }
    
    def format_scientific_formula(self, equation: str, concept_name: str, concept_type: str) -> str:
        """
        Format mathematical formulas in proper scientific notation with enhanced readability.
        
        Args:
            equation: Raw equation string
            concept_name: Name of the mathematical concept
            concept_type: Type/category of the concept
            
        Returns:
            Formatted formula string with proper scientific notation
        """
        # Dictionary for enhanced mathematical formatting
        replacements = {
            # Greek letters (already in Unicode, but ensure consistency)
            'π': 'π',
            'Σ': 'Σ',
            'δ': 'δ',
            'θ': 'θ',
            'φ': 'φ',
            'ω': 'ω',
            
            # Mathematical symbols
            '*': '·',  # Multiplication dot
            '**': '^',  # Exponentiation
            'sqrt': '√',
            'inf': '∞',
            '+-': '±',
            
            # Fractions and special formatting
            '1/2': '½',
            '1/3': '⅓',
            '1/4': '¼',
            '3/4': '¾',
            '2/3': '⅔',
            
            # Special cases for common expressions
            '/π': '/π',
            'π²': 'π²',
            'π^2': 'π²',
            
            # Function formatting
            'sin(': 'sin(',
            'cos(': 'cos(',
            'tan(': 'tan(',
            'exp(': 'exp(',
            'log(': 'log(',
            'ln(': 'ln(',
        }
        
        # Apply basic replacements
        formatted_eq = equation
        for old, new in replacements.items():
            formatted_eq = formatted_eq.replace(old, new)
        
        # Special formatting for specific concept types
        if concept_type == "Fourier Series":
            # Enhanced Fourier series formatting
            if "Square Wave" in concept_name:
                formatted_eq = """f(x) = (4/π) · Σ (1/n) · sin(n·x)
                
where: n = 1, 3, 5, ... (odd harmonics only)

Physical meaning: Approximates a square wave using 
infinite sum of sine waves with decreasing amplitudes."""
            
            elif "Sawtooth Wave" in concept_name:
                formatted_eq = """f(x) = (2/π) · Σ [(-1)^(n+1)/n] · sin(n·x)
                
where: n = 1, 2, 3, ... (all positive integers)

Physical meaning: Creates sawtooth pattern through
alternating positive/negative harmonic contributions."""
            
            elif "Triangle Wave" in concept_name:
                formatted_eq = """f(x) = (8/π²) · Σ [(-1)^((n-1)/2)/n²] · sin(n·x)
                
where: n = 1, 3, 5, ... (odd harmonics only)

Physical meaning: Smooth triangular waveform with
rapidly decreasing harmonic amplitudes (1/n²)."""
        
        elif concept_type == "Parametric":
            if "Lissajous" in concept_name:
                formatted_eq = """Lissajous Curve:
x(t) = A · sin(a·t + δ)
y(t) = B · sin(b·t)

Parameters:
• A, B: amplitudes in x and y directions
• a, b: frequency ratios
• δ: phase difference
• t: parameter (time)

Result: Beautiful closed curves when a/b is rational."""
            
            elif "Epicycloid" in concept_name:
                formatted_eq = """Epicycloid (Rolling Circle):
x(t) = (R + r)·cos(t) - r·cos((R + r)/r · t)
y(t) = (R + r)·sin(t) - r·sin((R + r)/r · t)

Parameters:
• R: radius of fixed circle
• r: radius of rolling circle
• t: angle parameter

Geometry: Curve traced by point on circle of radius r
rolling around outside of fixed circle of radius R."""
        
        elif concept_type == "Taylor Series":
            if "Exponential" in concept_name:
                formatted_eq = """Taylor Series for e^x:
e^x = Σ (x^n)/n! = 1 + x + x²/2! + x³/3! + x⁴/4! + ...

where: n = 0, 1, 2, 3, ... (all non-negative integers)

Convergence: Converges for all real x
Physical meaning: Describes exponential growth/decay."""
            
            elif "Sine" in concept_name:
                formatted_eq = """Taylor Series for sin(x):
sin(x) = Σ [(-1)^n · x^(2n+1)]/(2n+1)!
       = x - x³/3! + x⁵/5! - x⁷/7! + ...

where: n = 0, 1, 2, 3, ...

Convergence: Converges for all real x
Physical meaning: Oscillatory motion representation."""
            
            elif "Cosine" in concept_name:
                formatted_eq = """Taylor Series for cos(x):
cos(x) = Σ [(-1)^n · x^(2n)]/(2n)!
       = 1 - x²/2! + x⁴/4! - x⁶/6! + ...

where: n = 0, 1, 2, 3, ...

Convergence: Converges for all real x
Physical meaning: Complement to sine in oscillations."""
        
        # Format the header
        header = f"═══ {concept_name} ═══\nCategory: {concept_type}\n"
        separator = "─" * 50 + "\n";
        
        return header + separator + formatted_eq


class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with formula display, parameter controls, and three-panel visualization"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mathematical Series Visualizer - Enhanced")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Load concepts from JSON
        self.concepts_data = load_visualization_concepts()
        self.dropdown_options = get_dropdown_options()
        
        # Create UI components
        self.init_ui()
        
        # Set default concept
        if self.dropdown_options:
            self.concept_dropdown.setCurrentText(self.dropdown_options[0])
            self.on_concept_changed()
    
    def init_ui(self):
        """Initialize the enhanced user interface with three-panel layout"""
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        # Use 1 for horizontal orientation if Qt.Horizontal is problematic
        splitter = QSplitter(Qt.Horizontal)  # type: ignore[attr-defined]
        main_layout.addWidget(splitter)
        
        # Left panel: Formula and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Control panel
        control_panel = self.create_control_panel()
        left_layout.addWidget(control_panel)
        
        # Formula panel
        self.formula_panel = FormulaPanel()
        left_layout.addWidget(self.formula_panel)
        
        # Connect parameter changes to animation updates
        self.formula_panel.amplitude_slider.valueChanged.connect(self.on_parameters_changed)
        self.formula_panel.frequency_slider.valueChanged.connect(self.on_parameters_changed)
        self.formula_panel.phase_slider.valueChanged.connect(self.on_parameters_changed)
        self.formula_panel.show_individual_cb.toggled.connect(self.on_parameters_changed)
        
        splitter.addWidget(left_panel)
        
        # Right panel: Enhanced animation canvas
        self.canvas = EnhancedAnimationCanvas(self)
        splitter.addWidget(self.canvas)
        
        # Set splitter proportions (30% left, 70% right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 7)
        
        # Status bar
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("Enhanced Visualizer Ready - Select a mathematical concept")
    
    def create_control_panel(self) -> QGroupBox:
        """Create the main control panel with concept selection and animation controls"""
        group = QGroupBox("Main Controls")
        layout = QGridLayout(group)
        
        # Concept selection
        layout.addWidget(QLabel("Mathematical Concept:"), 0, 0)
        self.concept_dropdown = QComboBox()
        self.concept_dropdown.addItems(self.dropdown_options)
        self.concept_dropdown.currentTextChanged.connect(self.on_concept_changed)
        layout.addWidget(self.concept_dropdown, 0, 1, 1, 2)
        
        # Number of terms
        layout.addWidget(QLabel("Number of Terms:"), 1, 0)
        self.terms_spinbox = QSpinBox()
        self.terms_spinbox.setRange(1, 25)
        self.terms_spinbox.setValue(10)
        self.terms_spinbox.valueChanged.connect(self.on_terms_changed)
        layout.addWidget(self.terms_spinbox, 1, 1)
        
        # Animation controls
        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self.toggle_animation)
        layout.addWidget(self.play_button, 2, 0)
        
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.clicked.connect(self.reset_animation)
        layout.addWidget(self.reset_button, 2, 1)
        
        self.save_button = QPushButton("💾 Save Image")
        self.save_button.clicked.connect(self.save_image)
        layout.addWidget(self.save_button, 2, 2)
        
        # GIF export button
        self.save_gif_button = QPushButton("🎬 Save GIF")
        self.save_gif_button.clicked.connect(self.save_gif)
        layout.addWidget(self.save_gif_button, 2, 3)
        
        # Theme selection
        layout.addWidget(QLabel("Theme:"), 3, 0)
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Dark", "Light", "Colorful", "Rainbow", "Ocean", "Sunset"])
        self.theme_dropdown.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_dropdown, 3, 1)
        
        # Custom equation button
        self.custom_eq_button = QPushButton("📝 Custom Equation")
        self.custom_eq_button.clicked.connect(self.open_custom_equation_dialog)
        layout.addWidget(self.custom_eq_button, 3, 2)
        
        # Add advanced export and feature buttons
        self.save_video_button = QPushButton("📹 Save Video (MP4)")
        self.save_video_button.clicked.connect(self.save_video)
        layout.addWidget(self.save_video_button, 4, 0)

        self.export_data_button = QPushButton("📊 Export Data (CSV/JSON)")
        self.export_data_button.clicked.connect(self.export_data)
        layout.addWidget(self.export_data_button, 4, 1)

        self.advanced_features_button = QPushButton("✨ Advanced Features")
        self.advanced_features_button.clicked.connect(self.show_advanced_features)
        layout.addWidget(self.advanced_features_button, 4, 2)
        
        return group
    
    def on_concept_changed(self):
        """Handle concept selection change"""
        selected = self.concept_dropdown.currentText()
        concept = parse_dropdown_selection(selected)
        
        if concept:
            n_terms = self.terms_spinbox.value()
            self.canvas.set_concept_data(concept, n_terms)
            
            # Update formula panel
            self.formula_panel.update_formula(concept)
            
            # Update status bar
            concept_name = concept.get('name', 'Unknown')
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage(f"Loaded: {concept_name}")
        else:
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage("Error: Could not load selected concept")
    
    def on_terms_changed(self):
        """Handle change in number of terms"""
        self.on_concept_changed()  # Reload with new number of terms
    
    def on_parameters_changed(self):
        """Handle parameter changes from the formula panel"""
        params = self.formula_panel.get_parameters()
        self.canvas.update_parameters(
            params['amplitude'], 
            params['frequency'], 
            params['phase']
        )
        self.canvas.show_individual_traces = params['show_individual']
    
    def on_theme_changed(self):
        """Handle theme change"""
        theme = self.theme_dropdown.currentText().lower()
        self.canvas.apply_theme(theme)
        self.canvas.draw()
    
    def toggle_animation(self):
        """Toggle animation play/pause"""
        if self.canvas.is_playing:
            self.canvas.stop_animation()
            self.play_button.setText("▶ Play")
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage("Animation paused")
        else:
            self.canvas.start_animation()
            self.play_button.setText("⏸ Pause")
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage("Animation playing")
    
    def reset_animation(self):
        """Reset animation to beginning"""
        self.canvas.reset_animation()
        self.play_button.setText("▶ Play")
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("Animation reset")
    
    def save_image(self):
        """Save current visualization as image"""
        try:
            # Create assets directory if it doesn't exist
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
            os.makedirs(assets_dir, exist_ok=True)
            
            # Generate filename
            concept_name = "unknown"
            if self.canvas.current_concept:
                concept_name = self.canvas.current_concept.get('name', 'unknown').lower().replace(' ', '_')
            
            filename = os.path.join(assets_dir, f"{concept_name}_enhanced_visualization.png")
            
            # Save the figure
            self.canvas.fig.savefig(filename, dpi=300, bbox_inches='tight', 
                                  facecolor=self.canvas.fig.get_facecolor())
            
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage(f"Image saved: {filename}")
            
            # Show success message
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Save Successful", 
                                  f"Enhanced visualization saved to:\n{filename}")
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Save Error", 
                               f"Failed to save image:\n{str(e)}")
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage("Error saving image")
    
    def save_gif(self):
        """Save the current animation as a GIF file"""
        from PyQt5.QtWidgets import QFileDialog, QProgressDialog, QApplication, QMessageBox
        from PyQt5.QtCore import Qt
        import matplotlib.animation as animation
        import os
        import numpy as np
        
        # Defensive: handle None for current_concept
        concept_name = "animation"
        if self.canvas.current_concept and 'name' in self.canvas.current_concept:
            concept_name = self.canvas.current_concept['name'].lower().replace(' ', '_')
        
        # Get save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Animation as GIF", 
            os.path.join("assets", f"{concept_name}_animation.gif"),
            "GIF files (*.gif)"
        )
        
        if not file_path:
            return
        
        # Create progress dialog
        progress = QProgressDialog("Creating GIF...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        try:
            # Store current animation state
            was_playing = getattr(self.canvas, 'is_playing', False)
            if was_playing:
                self.canvas.stop_animation()
            
            # Reset animation to beginning
            self.canvas.current_time = 0
            self.canvas.traced_points = []
            self.canvas.individual_traces = [[] for _ in range(len(self.canvas.epicycles))]
            
            # Parameters for GIF creation
            frames = 120  # Number of frames for full cycle
            fps = 20     # Frames per second
            
            def animate_frame(frame):
                if progress.wasCanceled():
                    return []
                progress.setValue(int((frame / frames) * 100))
                QApplication.processEvents()
                self.canvas.current_time = (frame / frames) * self.canvas.max_time
                self.canvas.ax_epicycles.clear()
                self.canvas.ax_individual.clear()
                self.canvas.ax_combined.clear()
                self.canvas.setup_plots()
                self.canvas.animate_frame(frame)
                # Return an empty list (no blitting)
                return []
            
            ani = animation.FuncAnimation(
                self.canvas.fig, animate_frame, frames=frames,
                interval=1000/fps, blit=False, repeat=False
            )
            progress.setLabelText("Saving GIF file...")
            ani.save(file_path, writer='pillow', fps=fps)
            progress.setValue(100)
            if was_playing:
                self.canvas.start_animation()
            QMessageBox.information(self, "Success", f"GIF saved successfully to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save GIF:\n{str(e)}")
        finally:
            progress.close()
    
    def save_video(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Coming Soon", "Video export (MP4) will be available in a future update!")
    
    def export_data(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Coming Soon", "Data export (CSV/JSON) will be available in a future update!")
    
    def show_advanced_features(self):
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Advanced Features", (
            "Planned advanced features include:\n"
            "- Mouse interaction with epicycles\n"
            "- Multiple concept comparison (side-by-side)\n"
            "- 3D epicycles\n"
            "- Complex plane visualization\n"
            "- Frequency domain plots\n\n"
            "These will be available in future updates!"
        ))
    
    def open_custom_equation_dialog(self):
        """Open dialog for custom equation input"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLabel, QComboBox, QLineEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Custom Equation Input")
        dialog.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        instructions = QLabel("""
Enter a custom mathematical function for visualization:

Supported functions: sin, cos, tan, exp, log, sqrt
Constants: pi (use np.pi), e (use np.e)
Variables: use 't' for time parameter

Examples:
• Fourier-like: A*sin(n*t) + B*cos(m*t)
• Custom wave: sin(t) + 0.5*sin(3*t) + 0.25*sin(5*t)
• Exponential: exp(-t/2)*sin(t)
        """)
        layout.addWidget(instructions)
        
        # Equation type
        layout.addWidget(QLabel("Equation Type:"))
        type_combo = QComboBox()
        type_combo.addItems(["Custom Function", "Fourier Series", "Parametric Curve"])
        layout.addWidget(type_combo)
        
        # Equation input
        layout.addWidget(QLabel("Equation (use 't' as variable):"))
        equation_input = QTextEdit()
        equation_input.setMaximumHeight(100)
        equation_input.setPlainText("sin(t) + 0.5*sin(3*t)")
        layout.addWidget(equation_input)
        
        # Name input
        layout.addWidget(QLabel("Concept Name:"))
        name_input = QLineEdit()
        name_input.setText("Custom Function")
        layout.addWidget(name_input)
        
        # Buttons
        button_layout = QVBoxLayout()
        apply_button = QPushButton("Apply Custom Equation")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        def apply_custom_equation():
            try:
                equation_text = equation_input.toPlainText().strip()
                concept_name = name_input.text().strip() or "Custom Function"
                eq_type = type_combo.currentText()
                
                # Create custom concept
                custom_concept = {
                    "name": concept_name,
                    "type": "Custom",
                    "category": "Custom",
                    "equation": equation_text,
                    "visual": f"Custom visualization: {equation_text}",
                    "custom_function": equation_text                }
                
                # Apply to visualization
                self.apply_custom_concept(custom_concept)
                dialog.accept()
                
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(dialog, "Error", f"Invalid equation:\n{str(e)}")
        
        apply_button.clicked.connect(apply_custom_equation)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def apply_custom_concept(self, custom_concept):
        """Apply a custom mathematical concept to the visualization"""
        try:
            # Set the custom concept in canvas
            n_terms = self.terms_spinbox.value()
            
            # Generate custom epicycles from the equation
            custom_epicycles = self.generate_custom_epicycles(
                custom_concept.get("custom_function", "sin(t)"), n_terms
            )
            
            # Update canvas with custom data
            self.canvas.current_concept = custom_concept
            self.canvas.epicycles = custom_epicycles
            self.canvas.individual_traces = [[] for _ in range(len(custom_epicycles))]
            self.canvas.traced_points = []
            self.canvas.current_time = 0
            
            # Update formula panel
            self.formula_panel.update_formula(custom_concept)
            
            # Update status bar
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage(f"Loaded custom equation: {custom_concept['name']}")
            
            self.canvas.draw()
            
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to apply custom equation:\n{str(e)}")
    
    def generate_custom_epicycles(self, equation_str: str, n_terms: int):
        """Generate epicycles from a custom equation string"""
        import re
        
        # Simple parser for basic trigonometric functions
        # This is a simplified version - you could make it more sophisticated
        
        epicycles = []
        
        # Try to extract sin/cos terms with their coefficients and frequencies
        sin_pattern = r'([\d\.]*)\*?sin\(([\d\.]*)\*?t\)'
        cos_pattern = r'([\d\.]*)\*?cos\(([\d\.]*)\*?t\)'
        
        sin_matches = re.findall(sin_pattern, equation_str)
        cos_matches = re.findall(cos_pattern, equation_str)
        
        # Add sin terms
        for coeff, freq in sin_matches:
            amplitude = float(coeff) if coeff else 1.0
            frequency = float(freq) if freq else 1.0
            
            epicycles.append({
                'radius': abs(amplitude),
                'frequency': frequency,
                'phase': 0 if amplitude >= 0 else np.pi,  # Phase shift for negative amplitudes
                'direction': 1
            })
        
        # Add cos terms  
        for coeff, freq in cos_matches:
            amplitude = float(coeff) if coeff else 1.0
            frequency = float(freq) if freq else 1.0
            
            epicycles.append({
                'radius': abs(amplitude),
                'frequency': frequency,
                'phase': np.pi/2 if amplitude >= 0 else 3*np.pi/2,  # cos = sin with π/2 phase shift
                'direction': 1
            })
        
        # If no matches found, create a simple default
        if not epicycles:
            epicycles.append({
                'radius': 1.0,
                'frequency': 1.0,
                'phase': 0,
                'direction': 1
            })
        
        return epicycles[:n_terms]  # Limit to requested number of terms
