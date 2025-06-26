"""
Utility functions for loading and parsing mathematical concepts from JSON
"""
import json
import os
from typing import Dict, List, Any, Optional

def load_visualization_concepts(json_path: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Load mathematical concepts from the visualization_concepts.json file
    
    Args:
        json_path: Path to the JSON file. If None, uses default location.
    
    Returns:
        Dictionary containing all mathematical concepts organized by category
    """
    if json_path is None:
        # Default to the JSON file in the project root
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(current_dir, 'visualization_concepts.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Could not find {json_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return {}

def get_all_concepts_flat() -> List[Dict[str, Any]]:
    """
    Get all mathematical concepts as a flat list with category information
    
    Returns:
        List of all concepts with added 'category' field
    """
    concepts_data = load_visualization_concepts()
    flat_concepts = []
    
    for category, concepts in concepts_data.items():
        for concept in concepts:
            concept_with_category = concept.copy()
            concept_with_category['category'] = category
            flat_concepts.append(concept_with_category)
    
    return flat_concepts

def get_concepts_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Get all concepts from a specific category
    
    Args:
        category: Category name (e.g., 'FourierSeries', 'TaylorSeries')
    
    Returns:
        List of concepts in that category
    """
    concepts_data = load_visualization_concepts()
    return concepts_data.get(category, [])

def get_concept_by_name(concept_name: str) -> Dict[str, Any]:
    """
    Find a specific concept by name across all categories
    
    Args:
        concept_name: Name of the concept to find
    
    Returns:
        The concept dictionary if found, empty dict otherwise
    """
    all_concepts = get_all_concepts_flat()
    for concept in all_concepts:
        if concept['name'] == concept_name:
            return concept
    return {}

def get_dropdown_options() -> List[str]:
    """
    Get formatted options for dropdown menu
    
    Returns:
        List of strings formatted as "Category - Concept Name"
    """
    all_concepts = get_all_concepts_flat()
    options = []
    
    for concept in all_concepts:
        category_display = concept['category'].replace('Series', ' Series').replace('Curves', ' Curves')
        option = f"{category_display} - {concept['name']}"
        options.append(option)
    
    return sorted(options)

def parse_dropdown_selection(selection: str) -> Dict[str, Any]:
    """
    Parse a dropdown selection back to the original concept
    
    Args:
        selection: Dropdown selection in format "Category - Concept Name"
    
    Returns:
        The concept dictionary
    """
    if " - " not in selection:
        return {}
    
    parts = selection.split(" - ", 1)
    if len(parts) != 2:
        return {}
    
    concept_name = parts[1]
    return get_concept_by_name(concept_name)
