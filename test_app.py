#!/usr/bin/env python3
"""
Test script to verify the mathematical series visualization application works correctly.
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_concept_loader():
    """Test the concept loader functionality"""
    print("Testing concept loader...")
    
    try:
        from utils.concept_loader import load_visualization_concepts, get_dropdown_options
        
        # Load concepts
        concepts = load_visualization_concepts()
        print(f"✓ Loaded {len(concepts)} concept categories")
        
        # Test dropdown options
        options = get_dropdown_options()
        print(f"✓ Generated {len(options)} dropdown options")
        
        # Show first few options
        print("First 5 options:")
        for i, option in enumerate(options[:5]):
            print(f"  {i+1}. {option}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in concept loader: {e}")
        return False

def test_math_utils():
    """Test the mathematical utilities"""
    print("\nTesting mathematical utilities...")
    
    try:
        from utils.math_utils import ConceptMath, generate_curve_from_concept
        from utils.concept_loader import get_concept_by_name
        
        # Test Fourier series calculation
        epicycles = ConceptMath.generate_fourier_epicycles("Square Wave", 5)
        print(f"✓ Generated {len(epicycles)} epicycles for square wave")
        
        # Test concept curve generation
        concept = get_concept_by_name("Square Wave")
        if concept:
            x_curve, y_curve, epi = generate_curve_from_concept(concept, 5, 100)
            print(f"✓ Generated curve with {len(x_curve)} points")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in math utils: {e}")
        return False

def test_themes():
    """Test the theme configuration"""
    print("\nTesting themes...")
    
    try:
        from config.themes import get_theme_colors, get_available_themes
        
        themes = get_available_themes()
        print(f"✓ Available themes: {themes}")
        
        # Test each theme
        for theme in themes:
            colors = get_theme_colors(theme)
            print(f"✓ Theme '{theme}' has {len(colors)} color settings")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in themes: {e}")
        return False

def test_gui_imports():
    """Test GUI imports without creating windows"""
    print("\nTesting GUI imports...")
    
    try:
        # Test PyQt5 imports
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        print("✓ PyQt5 imports successful")
        
        # Test matplotlib imports
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        print("✓ Matplotlib Qt5 backend imports successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in GUI imports: {e}")
        return False

def main():
    """Run all tests"""
    print("Mathematical Series Visualization - Component Tests")
    print("=" * 60)
    
    tests = [
        test_concept_loader,
        test_math_utils,
        test_themes,
        test_gui_imports
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        print("\nTo run the application, use:")
        print("python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
