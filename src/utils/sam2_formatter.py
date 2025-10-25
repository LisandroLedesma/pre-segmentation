"""
SAM2 formatting utilities for coordinate export.
"""
import json


def format_coordinates_for_sam2(coordinates_list):
    """
    Format coordinates list for SAM2 input format.
    
    Args:
        coordinates_list (list): List of coordinate dictionaries
        
    Returns:
        dict: Formatted data for SAM2 with consolidated point_coords and point_labels
    """
    point_coords = []
    point_labels = []
    boxes = []
    
    for coord in coordinates_list:
        if "Label" in coord:  # Punto
            point_coords.append([coord["X"], coord["Y"]])
            point_labels.append(coord["Label"])
        else:  # Bounding box
            boxes.append([coord["X"], coord["Y"], coord["X"] + coord["Ancho"], coord["Y"] + coord["Alto"]])
    
    result = {}
    if point_coords:
        result["point_coords"] = point_coords
        result["point_labels"] = point_labels
    if boxes:
        result["boxes"] = boxes
    
    return result


def export_sam2_json(coordinates_list, filename="sam2_coordinates.json"):
    """
    Export coordinates in SAM2 JSON format.
    
    Args:
        coordinates_list (list): List of coordinate dictionaries
        filename (str): Output filename
        
    Returns:
        tuple: (json_string, filename)
    """
    sam2_data = format_coordinates_for_sam2(coordinates_list)
    json_str = json.dumps(sam2_data, indent=2)
    return json_str, filename


def get_sam2_preview(coordinates_list):
    """
    Get a preview of SAM2 formatted data.
    
    Args:
        coordinates_list (list): List of coordinate dictionaries
        
    Returns:
        str: Formatted string for copy-paste
    """
    sam2_data = format_coordinates_for_sam2(coordinates_list)
    
    # Crear formato de texto para copiar
    lines = []
    if "point_coords" in sam2_data:
        coords_str = str(sam2_data["point_coords"]).replace(" ", "")
        lines.append(f"point_coords = {coords_str}")
    if "point_labels" in sam2_data:
        labels_str = str(sam2_data["point_labels"]).replace(" ", "")
        lines.append(f"point_labels = {labels_str}")
    if "boxes" in sam2_data:
        boxes_str = str(sam2_data["boxes"]).replace(" ", "")
        lines.append(f"boxes = {boxes_str}")
    
    return "\n".join(lines)
