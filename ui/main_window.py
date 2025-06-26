"""
Main window for the Mathematical Series Visualization application.
Integrates with the JSON concepts file to provide dynamic equation selection.
"""

import sys
import os
import numpy as np
from typing import List, Dict, Any, Optional
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QComboBox, QPushButton, QLabel, QSlider, QSpinBox,
                             QGroupBox, QGridLayout, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches

# Import our custom utilities
from utils.concept_loader import (load_visualization_concepts, get_dropdown_options, 
                                 parse_dropdown_selection, get_all_concepts_flat)
from utils.math_utils import generate_curve_from_concept, ConceptMath
from config.themes import get_theme_colors


class AnimationCanvas(FigureCanvas):
    """Custom matplotlib canvas for epicycle animations"""
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(12, 8), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)
          # Create subplots with better layout
        self.ax_epicycles = self.fig.add_subplot(131)  # Left: Epicycles
        self.ax_curve = self.fig.add_subplot(132)      # Middle: Generated curve  
        self.ax_individual = self.fig.add_subplot(133) # Right: Individual epicycle traces
        
        # Animation properties
        self.animation = None
        self.is_playing = False
        self.current_time = 0
        self.time_step = 0.05
        self.max_time = 4 * np.pi        # Data storage
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
        self.traced_points = []
        self.individual_traces = []  # Store traces for each epicycle
        self.current_concept = None
        
        # Visual elements
        self.epicycle_circles = []
        self.epicycle_lines = []
        self.curve_line = None
        self.trace_line = None
        self.setup_plots()
    
    def setup_plots(self):
        """Initialize the plot layouts and styling"""
        # Setup epicycles plot
        self.ax_epicycles.set_xlim(-4, 4)
        self.ax_epicycles.set_ylim(-4, 4)
        self.ax_epicycles.set_aspect('equal')
        self.ax_epicycles.grid(True, alpha=0.3)
        self.ax_epicycles.set_title('Epicycles Animation', fontsize=12, fontweight='bold')
        
        # Setup curve plot
        self.ax_curve.set_xlim(0, 4 * np.pi)
        self.ax_curve.set_ylim(-3, 3)
        self.ax_curve.grid(True, alpha=0.3)
        self.ax_curve.set_title('Final Composite Curve', fontsize=12, fontweight='bold')
        self.ax_curve.set_xlabel('Time (t)')
        self.ax_curve.set_ylabel('Amplitude')
        
        # Setup individual traces plot
        self.ax_individual.set_xlim(0, 4 * np.pi)
        self.ax_individual.set_ylim(-3, 3)
        self.ax_individual.grid(True, alpha=0.3)
        self.ax_individual.set_title('Individual Epicycle Traces', fontsize=12, fontweight='bold')
        self.ax_individual.set_xlabel('Time (t)')
        self.ax_individual.set_ylabel('Amplitude')
        
        # Apply theme
        self.apply_theme('dark')
        
        self.fig.tight_layout()
    
    def apply_theme(self, theme_name: str = 'dark'):
        """Apply color theme to the plots"""
        colors = get_theme_colors(theme_name)
          # Set background colors
        self.fig.patch.set_facecolor(colors['background'])
        self.ax_epicycles.set_facecolor(colors['plot_background'])
        self.ax_curve.set_facecolor(colors['plot_background'])
        self.ax_individual.set_facecolor(colors['plot_background'])
        
        # Set text colors
        for ax in [self.ax_epicycles, self.ax_curve, self.ax_individual]:
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
        
        # Generate curve and epicycle data
        self.curve_x, self.curve_y, self.epicycles = generate_curve_from_concept(
            concept, n_terms, 1000
        )
          # Reset traced points and individual traces
        self.traced_points = []
        self.individual_traces = [[] for _ in range(len(self.epicycles))]
        self.current_time = 0
        
        # Update plot limits based on data
        if len(self.curve_y) > 0:
            y_range = max(abs(np.max(self.curve_y)), abs(np.min(self.curve_y)))
            self.ax_curve.set_ylim(-y_range * 1.2, y_range * 1.2)
        
        # Calculate epicycle system range
        total_radius = sum(ep['radius'] for ep in self.epicycles)
        if total_radius > 0:
            margin = total_radius * 1.2
            self.ax_epicycles.set_xlim(-margin, margin)
            self.ax_epicycles.set_ylim(-margin, margin)
        
        # Update plot titles with concept information
        concept_name = concept.get('name', 'Unknown')
        concept_type = concept.get('type', 'Unknown')
        self.ax_epicycles.set_title(f'Epicycles: {concept_name}', fontsize=14, fontweight='bold')
        self.ax_curve.set_title(f'{concept_type}: {concept_name}', fontsize=14, fontweight='bold')
        
        self.draw()
    
    def animate_frame(self, frame):
        """Animation function called for each frame"""
        if not self.is_playing:
            return []
        
        # Clear previous frame
        self.ax_epicycles.clear()
        
        # Reconfigure epicycles plot
        total_radius = sum(ep['radius'] for ep in self.epicycles) if self.epicycles else 2
        margin = total_radius * 1.2
        self.ax_epicycles.set_xlim(-margin, margin)
        self.ax_epicycles.set_ylim(-margin, margin)
        self.ax_epicycles.set_aspect('equal')
        self.ax_epicycles.grid(True, alpha=0.3)
        concept_name = self.current_concept.get('name', 'Unknown') if self.current_concept else 'Unknown'
        self.ax_epicycles.set_title(f'Epicycles: {concept_name}', fontsize=12, fontweight='bold')
        
        # Get current epicycle positions
        positions = ConceptMath.get_epicycle_chain_positions(self.epicycles, self.current_time)
        
        # Get selected color palette
        palette_name = self.palette_dropdown.currentText().lower() if hasattr(self, 'palette_dropdown') else 'vibrant'
        from config.themes import get_epicycle_colors
        epicycle_colors = get_epicycle_colors(palette_name)
        
        # Draw connecting lines between epicycle centers first (behind circles)
        for i in range(len(positions) - 1):
            start_pos = positions[i]
            end_pos = positions[i + 1]
            color = epicycle_colors[i % len(epicycle_colors)]
            
            # Draw connection line with gradient effect (lighter)
            self.ax_epicycles.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], 
                                color=color, linewidth=2.5, alpha=0.6, linestyle='-')
        
        # Draw epicycles with enhanced styling
        for i, (epicycle, pos) in enumerate(zip(self.epicycles, positions[1:])):
            center = positions[i]
            radius = epicycle['radius']
            color = epicycle_colors[i % len(epicycle_colors)]
            
            # Draw circle with enhanced styling
            circle = patches.Circle(center, radius, fill=False, color=color, 
                                  linewidth=2.5, alpha=0.8, linestyle='-')
            self.ax_epicycles.add_patch(circle)
            
            # Draw radius line from center to current position with thicker line
            self.ax_epicycles.plot([center[0], pos[0]], [center[1], pos[1]], 
                                color=color, linewidth=3, alpha=0.9, zorder=5)
            
            # Draw center point with larger, more visible marker
            self.ax_epicycles.plot(center[0], center[1], 'o', color=color, 
                                 markersize=6, alpha=0.9, markeredgecolor='white', 
                                 markeredgewidth=1, zorder=6)
            
            # Draw current position point
            self.ax_epicycles.plot(pos[0], pos[1], 'o', color=color, 
                                 markersize=5, alpha=0.8, zorder=7)
        
        # Draw final point with special highlighting
        if positions:
            final_pos = positions[-1]
            # Multi-layered final point for emphasis
            self.ax_epicycles.plot(final_pos[0], final_pos[1], 'o', color='white', 
                                 markersize=12, alpha=0.9, zorder=8)
            self.ax_epicycles.plot(final_pos[0], final_pos[1], 'o', color='#FF0040', 
                                 markersize=10, alpha=1.0, zorder=9)
            self.ax_epicycles.plot(final_pos[0], final_pos[1], 'o', color='#FFFFFF', 
                                 markersize=4, alpha=1.0, zorder=10)
            
            # Add traced point with color information
            self.traced_points.append((self.current_time, final_pos[1]))
            
            # Limit traced points for performance
            if len(self.traced_points) > 1000:
                self.traced_points = self.traced_points[-1000:]
        
        # Track individual epicycle traces for each position
        for i, pos in enumerate(positions[1:]):  # Skip origin position
            if i < len(self.individual_traces):
                # Store y-component for each epicycle
                self.individual_traces[i].append((self.current_time, pos[1]))
                
                # Limit individual traces for performance
                if len(self.individual_traces[i]) > 1000:
                    self.individual_traces[i] = self.individual_traces[i][-1000:]
        
        # Update curve plot
        if self.traced_points:
            times, values = zip(*self.traced_points)
            
            # Clear and redraw curve
            self.ax_curve.clear()
            self.ax_curve.set_xlim(0, self.max_time)
            
            if values:
                y_range = max(abs(max(values)), abs(min(values))) if values else 1
                self.ax_curve.set_ylim(-y_range * 1.2, y_range * 1.2)
            
            self.ax_curve.grid(True, alpha=0.3)
            concept_type = self.current_concept.get('type', 'Unknown') if self.current_concept else 'Unknown'
            self.ax_curve.set_title(f'{concept_type}: {concept_name}', fontsize=14, fontweight='bold')
            self.ax_curve.set_xlabel('Time (t)')
            self.ax_curve.set_ylabel('Amplitude')            # Plot traced curve with gradient colors
            if len(times) > 1:
                # Get gradient colors from theme configuration
                from config.themes import get_curve_gradient_colors
                gradient_colors = get_curve_gradient_colors()
                
                # Draw curve with gradient effect
                n_segments = min(len(times) - 1, 100)  # Limit for performance
                segment_size = max(1, len(times) // n_segments)
                
                for i in range(0, len(times) - segment_size, segment_size):
                    end_idx = min(i + segment_size, len(times))
                    segment_times = times[i:end_idx]
                    segment_values = values[i:end_idx]
                    
                    # Choose color based on position in curve
                    color_idx = (i // segment_size) % len(gradient_colors)
                    color = gradient_colors[color_idx]
                    
                    # Calculate alpha for fade effect (newer points more opaque)
                    alpha = 0.4 + 0.6 * (i / len(times))
                    
                    self.ax_curve.plot(segment_times, segment_values, color=color, 
                                     linewidth=2.5, alpha=alpha, zorder=3)
                
                # Draw main curve with semi-transparent overlay
                self.ax_curve.plot(times, values, '#FFFFFF', linewidth=1, alpha=0.3, zorder=4)
                
                # Highlight recent portion of curve
                if len(times) > 20:
                    recent_times = times[-20:]
                    recent_values = values[-20:]
                    self.ax_curve.plot(recent_times, recent_values, '#FF0040', 
                                     linewidth=3, alpha=0.8, zorder=5)
            
            # Plot current position with enhanced styling
            if times:
                current_time = times[-1]
                current_value = values[-1]
                
                # Multi-layered current position marker
                self.ax_curve.plot(current_time, current_value, 'o', color='white', 
                                 markersize=12, alpha=0.9, zorder=8)
                self.ax_curve.plot(current_time, current_value, 'o', color='#FF0040', 
                                 markersize=10, alpha=1.0, zorder=9)
                self.ax_curve.plot(current_time, current_value, 'o', color='#FFFFFF', 
                                 markersize=4, alpha=1.0, zorder=10)
                
                # Add vertical line from current point to x-axis
                self.ax_curve.axvline(x=current_time, color='#FF0040', 
                                    linewidth=1, alpha=0.4, linestyle='--', zorder=1)
                
                # Add horizontal line from current point to y-axis
                self.ax_curve.axhline(y=current_value, color='#FF0040', 
                                    linewidth=1, alpha=0.4, linestyle='--', zorder=1)
        
        # Update time
        self.current_time += self.time_step
        if self.current_time > self.max_time:
            self.current_time = 0
            self.traced_points = []
        
        # Apply theme colors
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
        self.stop_animation()
        
        # Redraw static state
        self.ax_epicycles.clear()
        self.ax_curve.clear()
        self.setup_plots()
        
        if self.current_concept:
            concept_name = self.current_concept.get('name', 'Unknown')
            concept_type = self.current_concept.get('type', 'Unknown')
            self.ax_epicycles.set_title(f'Epicycles: {concept_name}', fontsize=14, fontweight='bold')
            self.ax_curve.set_title(f'{concept_type}: {concept_name}', fontsize=14, fontweight='bold')
        
        self.draw()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mathematical Series Visualizer")
        self.setGeometry(100, 100, 1400, 900)
        
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
        """Initialize the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Animation canvas
        self.canvas = AnimationCanvas(self)
        main_layout.addWidget(self.canvas)
          # Status bar
        status_bar = self.statusBar()
        if status_bar:
            status_bar.showMessage("Ready - Select a mathematical concept to visualize")
    
    def create_control_panel(self) -> QGroupBox:
        """Create the control panel with buttons and dropdowns"""
        group = QGroupBox("Controls")
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
          # Theme selection
        layout.addWidget(QLabel("Theme:"), 3, 0)
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(["Dark", "Light", "Colorful", "Rainbow", "Ocean", "Sunset"])
        self.theme_dropdown.currentTextChanged.connect(self.on_theme_changed)
        layout.addWidget(self.theme_dropdown, 3, 1)
        
        # Color palette selection
        layout.addWidget(QLabel("Epicycle Colors:"), 3, 2)
        self.palette_dropdown = QComboBox()
        self.palette_dropdown.addItems(["Vibrant", "Neon", "Pastel", "Ocean"])
        self.palette_dropdown.currentTextChanged.connect(self.on_palette_changed)
        layout.addWidget(self.palette_dropdown, 3, 3)
        
        return group
    
    def on_concept_changed(self):
        """Handle concept selection change"""
        selected = self.concept_dropdown.currentText()
        concept = parse_dropdown_selection(selected)
        
        if concept:
            n_terms = self.terms_spinbox.value()
            self.canvas.set_concept_data(concept, n_terms)
            
            # Update status bar
            concept_name = concept.get('name', 'Unknown')
            equation = concept.get('equation', 'No equation')
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage(f"Loaded: {concept_name} | {equation}")
        else:
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage("Error: Could not load selected concept")
    
    def on_terms_changed(self):
        """Handle change in number of terms"""
        self.on_concept_changed()  # Reload with new number of terms
    
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
            
            filename = os.path.join(assets_dir, f"{concept_name}_visualization.png")
            
            # Save the figure
            self.canvas.fig.savefig(filename, dpi=300, bbox_inches='tight', 
                                  facecolor=self.canvas.fig.get_facecolor())
            
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage(f"Image saved: {filename}")
            
            # Show success message
            QMessageBox.information(self, "Save Successful", 
                                  f"Image saved successfully to:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", 
                               f"Failed to save image:\n{str(e)}")
            status_bar = self.statusBar()
            if status_bar:
                status_bar.showMessage("Error saving image")
    
    def on_palette_changed(self):
        """Handle color palette change"""
        # Update will happen automatically on next animation frame
        pass
