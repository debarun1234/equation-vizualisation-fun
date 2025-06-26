# Release Notes

## v1.0.0 – Initial Public Release (2025-06-26)

### 🚀 Highlights
- **First public release of the Mathematical Series Visualizer!**
- Interactive, educational, and extensible Python application for visualizing mathematical series and curves.

### ✨ Features
- **Animated Epicycles**: Visualize Fourier, Taylor, and parametric series with rotating vectors.
- **Three-Panel UI**: Epicycles, individual traces, and combined curve, all animated in real time.
- **Concepts Supported**:
  - Fourier Series: Square, Triangle, Sawtooth waves
  - Taylor Series: Exponential, Sine, Cosine
  - Parametric: Lissajous curves, Epicycloids
  - Custom equation input (user-defined functions)
- **Formula Display**: Scientific notation, readable explanations, and physical meaning for each concept.
- **Parameter Controls**: Adjust amplitude, frequency, phase, and number of terms live.
- **Color Themes**: Multiple palettes (dark, light, rainbow, ocean, sunset, etc.)
- **Export**: Save high-quality PNG images and animated GIFs of your visualizations.
- **Individual Traces**: Toggle to see each epicycle’s contribution.
- **Educational Focus**: Designed for teaching, learning, and exploring mathematical series.

### 🛠️ Technical
- **PyQt5** GUI with Matplotlib integration
- **Modular codebase**: Easily add new concepts via JSON and Python
- **Performance**: Optimized for 20+ terms in real time
- **Extensible**: Ready for advanced features (video export, 3D, frequency domain, etc.)

### 📝 How to Use
- Select a concept from the dropdown
- Adjust parameters and watch the animation
- Try different color themes
- Save images or GIFs for presentations or teaching
- Input your own custom equations for instant visualization

### 🐞 Known Issues / Limitations
- Video (MP4) and data (CSV/JSON) export are planned but not yet implemented
- Some advanced features (3D, mouse interaction, side-by-side comparison) are UI stubs for future updates
- Custom equation parser supports basic sin/cos/exp/log only

### 🙏 Thanks
- To the open-source community for PyQt5, Matplotlib, and NumPy
- To educators and students for inspiration and feedback

---

**Enjoy exploring mathematics visually!**
