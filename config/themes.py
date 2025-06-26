"""
Theme configurations and color presets for the mathematical series visualization application.
"""

# Color themes for the application
THEMES = {
    'dark': {
        'background': '#2b2b2b',
        'canvas_bg': '#1e1e1e',
        'primary_curve': '#00ff88',
        'secondary_curve': '#ff6b6b',
        'epicycle_line': '#4ecdc4',
        'epicycle_point': '#ffe66d',
        'text': '#ffffff',
        'grid': '#404040'
    },
    'light': {
        'background': '#ffffff',
        'canvas_bg': '#f8f9fa',
        'primary_curve': '#007bff',
        'secondary_curve': '#dc3545',
        'epicycle_line': '#17a2b8',
        'epicycle_point': '#ffc107',
        'text': '#000000',
        'grid': '#dee2e6'
    },
    'ocean': {
        'background': '#0d1b2a',
        'canvas_bg': '#1b263b',
        'primary_curve': '#00d4ff',
        'secondary_curve': '#ff6b9d',
        'epicycle_line': '#4ade80',
        'epicycle_point': '#fbbf24',
        'text': '#e2e8f0',
        'grid': '#334155'
    },
    'sunset': {
        'background': '#1a1a2e',
        'canvas_bg': '#16213e',
        'primary_curve': '#ff9500',
        'secondary_curve': '#ff006e',
        'epicycle_line': '#8338ec',
        'epicycle_point': '#ffbe0b',
        'text': '#f1faee',
        'grid': '#457b9d'
    },
    'colorful': {
        'background': '#1a1a2e',
        'canvas_bg': '#16213e',
        'primary_curve': '#ff6b6b',
        'secondary_curve': '#4ecdc4',
        'epicycle_line': '#45b7d1',
        'epicycle_point': '#feca57',
        'text': '#ffffff',
        'grid': '#384466'
    },
    'rainbow': {
        'background': '#0a0a0f',
        'canvas_bg': '#1a1a2e',
        'primary_curve': '#ff0080',
        'secondary_curve': '#00ff80',
        'epicycle_line': '#8000ff',
        'epicycle_point': '#ffff00',
        'text': '#ffffff',
        'grid': '#2a2a4e'
    }
}

# Animation settings
ANIMATION_CONFIG = {
    'interval': 50,  # milliseconds between frames
    'speed': 1.0,    # animation speed multiplier
    'trail_length': 200,  # number of points in the drawn curve trail
    'epicycle_radius_scale': 0.8  # scale factor for epicycle display
}

# Mathematical constants and defaults
MATH_CONFIG = {
    'default_terms': 10,
    'max_terms': 50,
    'min_terms': 1,
    'precision': 1000,  # number of points for curve calculation
    'time_range': 4 * 3.14159,  # 2π for one complete cycle
}

# Canvas dimensions and layout
CANVAS_CONFIG = {
    'width': 800,
    'height': 600,
    'dpi': 100,
    'margins': {'left': 0.1, 'right': 0.9, 'top': 0.9, 'bottom': 0.1}
}

# Predefined color palettes for epicycles
EPICYCLE_COLOR_PALETTES = {
    'vibrant': [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', 
        '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
        '#10AC84', '#EE5A24', '#0ABDE3', '#C44569', '#F8B500',
        '#6C5CE7', '#A29BFE', '#FD79A8', '#00B894', '#FDCB6E'
    ],
    'neon': [
        '#FF0080', '#00FF80', '#8000FF', '#FF8000', '#0080FF',
        '#FF0040', '#40FF00', '#4000FF', '#FF4000', '#0040FF',
        '#FF00C0', '#C0FF00', '#C000FF', '#FFC000', '#00C0FF'
    ],
    'pastel': [
        '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF',
        '#FFBAFF', '#FFBABA', '#BAFFFF', '#C9BAFF', '#FFCBA4'
    ],
    'ocean': [
        '#00D4FF', '#0080FF', '#4000FF', '#8000FF', '#C000FF',
        '#FF0080', '#FF0040', '#FF4000', '#FF8000', '#FFC000'
    ]
}

def get_theme_colors(theme_name: str = 'dark') -> dict:
    """
    Get color configuration for a specific theme.
    
    Args:
        theme_name: Name of the theme ('dark', 'light', 'ocean', 'sunset')
        
    Returns:
        Dictionary containing color values for the theme
    """
    theme_name = theme_name.lower()
    
    if theme_name not in THEMES:
        theme_name = 'dark'  # Default fallback
    
    colors = THEMES[theme_name].copy()
    
    # Add derived colors for consistency
    colors['plot_background'] = colors['canvas_bg']
    colors['axes'] = colors['text']
    
    return colors

def get_animation_config() -> dict:
    """Get animation configuration settings."""
    return ANIMATION_CONFIG.copy()

def get_math_config() -> dict:
    """Get mathematical configuration settings."""
    return MATH_CONFIG.copy()

def get_canvas_config() -> dict:
    """Get canvas configuration settings."""
    return CANVAS_CONFIG.copy()

def get_available_themes() -> list:
    """Get list of available theme names."""
    return list(THEMES.keys())

def get_epicycle_colors(palette_name: str = 'vibrant') -> list:
    """Get color palette for epicycles"""
    return EPICYCLE_COLOR_PALETTES.get(palette_name, EPICYCLE_COLOR_PALETTES['vibrant'])

def get_curve_gradient_colors() -> list:
    """Get gradient colors for curve drawing"""
    return [
        '#FF6B6B', '#FF8A5B', '#FFA94D', '#FFD93D', 
        '#6BCF7F', '#4ECDC4', '#45B7D1', '#5A67D8',
        '#9F7AEA', '#ED8796', '#F093FB', '#F5576C'
    ]
