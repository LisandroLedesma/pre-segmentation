"""
Coordinate management utilities.
"""
from typing import List, Dict, Any


def add_point_coordinate(coordinates_list: List[Dict], x: int, y: int, point_type: str) -> Dict[str, Any]:
    """
    Add a point coordinate to the coordinates list.
    
    Args:
        coordinates_list (list): Current coordinates list
        x (int): X coordinate
        y (int): Y coordinate
        point_type (str): "Foreground" or "Background"
        
    Returns:
        dict: The added coordinate dictionary
    """
    point_label = 1 if point_type == "Foreground" else 0
    new_coord = {
        "Tipo": f"Punto {point_type}",
        "X": x,
        "Y": y,
        "Label": point_label,
        "Índice": len(coordinates_list) + 1
    }
    return new_coord


def add_bounding_box_coordinate(coordinates_list: List[Dict], x: int, y: int, width: int, height: int) -> Dict[str, Any]:
    """
    Add a bounding box coordinate to the coordinates list.
    
    Args:
        coordinates_list (list): Current coordinates list
        x (int): X coordinate
        y (int): Y coordinate
        width (int): Box width
        height (int): Box height
        
    Returns:
        dict: The added coordinate dictionary
    """
    new_coord = {
        "Tipo": "Bounding Box",
        "X": x,
        "Y": y,
        "Ancho": width,
        "Alto": height,
        "Índice": len(coordinates_list) + 1
    }
    return new_coord


def clear_coordinates(coordinates_list: List[Dict]) -> List[Dict]:
    """
    Clear all coordinates from the list.
    
    Args:
        coordinates_list (list): Current coordinates list
        
    Returns:
        list: Empty coordinates list
    """
    return []


def get_coordinates_summary(coordinates_list: List[Dict]) -> Dict[str, int]:
    """
    Get a summary of coordinates by type.
    
    Args:
        coordinates_list (list): Current coordinates list
        
    Returns:
        dict: Summary with counts by type
    """
    summary = {
        "Total": len(coordinates_list),
        "Puntos Foreground": 0,
        "Puntos Background": 0,
        "Bounding Boxes": 0
    }
    
    for coord in coordinates_list:
        if "Label" in coord:
            if coord["Label"] == 1:
                summary["Puntos Foreground"] += 1
            else:
                summary["Puntos Background"] += 1
        else:
            summary["Bounding Boxes"] += 1
    
    return summary
