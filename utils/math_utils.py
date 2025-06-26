"""
Mathematical utility functions for series calculations and geometric operations.
"""

import numpy as np
from typing import List, Tuple, Callable
import cmath
import math


def calculate_fourier_coefficients(func: Callable, n_terms: int, period: float = 2*np.pi) -> List[complex]:
    """
    Calculate Fourier series coefficients for a given function.
    
    Args:
        func: Function to analyze
        n_terms: Number of terms to calculate
        period: Period of the function
        
    Returns:
        List of complex coefficients
    """
    coefficients = []
    N = 1000  # Number of sample points
    
    # Sample the function over one period
    t = np.linspace(0, period, N, endpoint=False)
    f_values = func(t)
    
    # Calculate coefficients using discrete Fourier transform approach
    for n in range(-n_terms//2, n_terms//2 + 1):
        if n == 0:
            # DC component
            coeff = np.mean(f_values)
        else:
            # AC components
            exp_term = np.exp(-1j * 2 * np.pi * n * t / period)
            coeff = np.mean(f_values * exp_term)
        
        coefficients.append(coeff)
    
    return coefficients


def square_wave(t: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
    """Generate square wave function."""
    return amplitude * np.sign(np.sin(t))


def triangle_wave(t: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
    """Generate triangle wave function."""
    return amplitude * (2/np.pi) * np.arcsin(np.sin(t))


def sawtooth_wave(t: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
    """Generate sawtooth wave function."""
    return amplitude * (t % (2*np.pi)) / np.pi - amplitude


def taylor_sin_coefficients(n_terms: int) -> List[float]:
    """
    Calculate Taylor series coefficients for sin(x) around x=0.
    
    Args:
        n_terms: Number of terms
        
    Returns:
        List of coefficients
    """
    coefficients = []
    for n in range(n_terms):
        if n % 2 == 1:  # Odd terms only for sin(x)
            coeff = (-1)**((n-1)//2) / math.factorial(n)
            coefficients.append(coeff)
        else:
            coefficients.append(0.0)
    
    return coefficients


def taylor_cos_coefficients(n_terms: int) -> List[float]:
    """
    Calculate Taylor series coefficients for cos(x) around x=0.
    
    Args:
        n_terms: Number of terms
          Returns:
        List of coefficients
    """
    coefficients = []
    for n in range(n_terms):
        if n % 2 == 0:  # Even terms only for cos(x)
            coeff = (-1)**(n//2) / math.factorial(n)
            coefficients.append(coeff)
        else:
            coefficients.append(0.0)
    
    return coefficients


def taylor_exp_coefficients(n_terms: int) -> List[float]:
    """
    Calculate Taylor series coefficients for e^x around x=0.
    
    Args:
        n_terms: Number of terms
        
    Returns:
        List of coefficients
    """
    return [1.0 / math.factorial(n) for n in range(n_terms)]


def lissajous_params(curve_type: str) -> Tuple[float, float, float]:
    """
    Get parameters for different Lissajous curve types.
    
    Args:
        curve_type: Type of Lissajous curve
        
    Returns:
        Tuple of (freq_x, freq_y, phase_shift)
    """
    curves = {
        'circle': (1, 1, np.pi/2),
        'ellipse': (1, 1, np.pi/4),
        'eight': (1, 2, 0),
        'three_leaf': (2, 3, 0),
        'four_leaf': (3, 4, np.pi/4),
        'complex': (3, 5, np.pi/6)
    }
    
    return curves.get(curve_type, (1, 1, np.pi/2))


def normalize_angle(angle: float) -> float:
    """Normalize angle to [0, 2π] range."""
    return angle % (2 * np.pi)


def complex_to_cartesian(z: complex) -> Tuple[float, float]:
    """Convert complex number to cartesian coordinates."""
    return z.real, z.imag


def cartesian_to_complex(x: float, y: float) -> complex:
    """Convert cartesian coordinates to complex number."""
    return complex(x, y)


def rotate_point(point: Tuple[float, float], angle: float, center: Tuple[float, float] = (0, 0)) -> Tuple[float, float]:
    """
    Rotate a point around a center by a given angle.
    
    Args:
        point: Point to rotate (x, y)
        angle: Rotation angle in radians
        center: Center of rotation (x, y)
        
    Returns:
        Rotated point coordinates
    """
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    x, y = point[0] - center[0], point[1] - center[1]
    
    new_x = x * cos_a - y * sin_a + center[0]
    new_y = x * sin_a + y * cos_a + center[1]
    
    return new_x, new_y


# Additional functions for JSON concept integration
from typing import Dict, Any

class ConceptMath:
    """Mathematical calculations specifically for JSON concept integration"""
    
    @staticmethod
    def generate_fourier_epicycles(concept_name: str, n_terms: int = 10) -> List[Dict[str, float]]:
        """Generate epicycles for Fourier series concepts"""
        epicycles = []
        
        if "Square" in concept_name:
            # Square wave Fourier series: f(x) = (4/π) * Σ (1/n) * sin(n*x), n = 1,3,5,...
            for n in range(1, n_terms + 1, 2):  # Only odd harmonics
                amplitude = 4 / (np.pi * n)
                epicycles.append({
                    'radius': amplitude,
                    'frequency': n,
                    'phase': 0,
                    'direction': 1
                })
        
        elif "Sawtooth" in concept_name:
            # Sawtooth wave: f(x) = (2/π) * Σ (-1)^(n+1)/n * sin(n*x)
            for n in range(1, n_terms + 1):
                amplitude = 2 / (np.pi * n) * ((-1) ** (n + 1))
                epicycles.append({
                    'radius': abs(amplitude),
                    'frequency': n,
                    'phase': 0 if amplitude > 0 else np.pi,
                    'direction': 1
                })
        
        elif "Triangle" in concept_name:
            # Triangle wave: f(x) = (8/π²) * Σ (-1)^((n-1)/2)/n² * sin(n*x), n odd
            for n in range(1, n_terms + 1, 2):  # Only odd harmonics
                amplitude = 8 / (np.pi**2 * n**2) * ((-1) ** ((n - 1) // 2))
                epicycles.append({
                    'radius': abs(amplitude),
                    'frequency': n,
                    'phase': 0 if amplitude > 0 else np.pi,
                    'direction': 1
                })
        
        return epicycles
    
    @staticmethod
    def calculate_epicycle_position(epicycles: List[Dict[str, float]], t: float) -> Tuple[float, float]:
        """Calculate current position of epicycle system"""
        x, y = 0, 0
        
        for epicycle in epicycles:
            radius = epicycle['radius']
            freq = epicycle['frequency']
            phase = epicycle['phase']
            direction = epicycle['direction']
            
            angle = direction * freq * t + phase
            x += radius * np.cos(angle)
            y += radius * np.sin(angle)
        
        return x, y
    
    @staticmethod
    def get_epicycle_chain_positions(epicycles: List[Dict[str, float]], t: float) -> List[Tuple[float, float]]:
        """Get positions of all epicycles in chain for visualization"""
        positions = [(0.0, 0.0)]  # Start at origin
        x, y = 0, 0
        
        for epicycle in epicycles:
            radius = epicycle['radius']
            freq = epicycle['frequency']
            phase = epicycle['phase']
            direction = epicycle['direction']
            
            angle = direction * freq * t + phase
            x += radius * np.cos(angle)
            y += radius * np.sin(angle)
            positions.append((float(x), float(y)))
        
        return positions

def generate_curve_from_concept(concept: Dict[str, Any], n_terms: int = 10, 
                               t_points: int = 1000) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, float]]]:
    """
    Generate curve data and epicycles from a JSON concept
    
    Args:
        concept: Concept dictionary from JSON
        n_terms: Number of terms for series
        t_points: Number of time points for curve
    
    Returns:
        Tuple of (x_curve, y_curve, epicycles)
    """
    concept_name = concept.get('name', '')
    category = concept.get('category', '')
    
    # Time parameter
    t = np.linspace(0, 2 * np.pi, t_points)
    
    if category == 'FourierSeries':
        epicycles = ConceptMath.generate_fourier_epicycles(concept_name, n_terms)
        
        # Generate the curve from epicycles
        x_curve = []
        y_curve = []
        for time in t:
            x, y = ConceptMath.calculate_epicycle_position(epicycles, time)
            x_curve.append(time)  # x-axis is time
            y_curve.append(y)     # y-axis is the function value
        
        return np.array(x_curve), np.array(y_curve), epicycles
    
    elif category == 'ParametricCurves':
        if 'Lissajous' in concept_name:
            # Lissajous curve: x(t) = A*sin(a*t + δ), y(t) = B*sin(b*t)
            a, b = 3, 2  # frequency ratios
            delta = np.pi/2
            A, B = 1, 1  # amplitudes
            
            x_curve = A * np.sin(a * t + delta)
            y_curve = B * np.sin(b * t)
            
            # Create simple epicycles for visualization
            epicycles = [
                {'radius': A, 'frequency': a, 'phase': delta, 'direction': 1},
                {'radius': B, 'frequency': b, 'phase': 0, 'direction': 1}
            ]
        
        elif 'Epicycloid' in concept_name:
            # Epicycloid: x(t) = (R + r)*cos(t) - r*cos((R + r)/r * t)
            R, r = 3, 1  # radii
            ratio = (R + r) / r
            
            x_curve = (R + r) * np.cos(t) - r * np.cos(ratio * t)
            y_curve = (R + r) * np.sin(t) - r * np.sin(ratio * t)
            
            epicycles = [
                {'radius': R + r, 'frequency': 1, 'phase': 0, 'direction': 1},
                {'radius': r, 'frequency': ratio, 'phase': np.pi, 'direction': 1}
            ]
        
        else:
            # Default to simple circle
            x_curve = np.cos(t)
            y_curve = np.sin(t)
            epicycles = [{'radius': 1, 'frequency': 1, 'phase': 0, 'direction': 1}]
        
        return x_curve, y_curve, epicycles
    
    elif category == 'TaylorSeries':
        # For Taylor series, create simplified visualizations
        if 'Exponential' in concept_name:
            x_curve = t
            y_curve = np.exp(t - np.pi)  # Shifted for better visualization
            
            # Create epicycles representing Taylor terms
            epicycles = []
            for n in range(min(n_terms, 8)):  # Limit for performance
                coeff = 1 / math.factorial(n)
                epicycles.append({
                    'radius': coeff * 0.5,  # Scale for visualization
                    'frequency': n + 1,
                    'phase': 0,
                    'direction': 1
                })
        
        elif 'Sine' in concept_name:
            x_curve = t
            y_curve = np.sin(t)
            
            # Sine Taylor series: x - x³/3! + x⁵/5! - ...
            epicycles = []
            for n in range(min(n_terms, 6)):
                power = 2 * n + 1
                sign = (-1) ** n
                coeff = sign / math.factorial(power)
                epicycles.append({
                    'radius': abs(coeff) * 2,  # Scale for visualization
                    'frequency': power,
                    'phase': 0 if coeff > 0 else np.pi,
                    'direction': 1
                })
        
        else:
            # Default case
            x_curve = t
            y_curve = np.sin(t)
            epicycles = [{'radius': 1, 'frequency': 1, 'phase': 0, 'direction': 1}]
        
        return x_curve, y_curve, epicycles
    
    else:
        # Default case - simple sine wave
        x_curve = t
        y_curve = np.sin(t)
        epicycles = [{'radius': 1, 'frequency': 1, 'phase': 0, 'direction': 1}]
        
        return x_curve, y_curve, epicycles
