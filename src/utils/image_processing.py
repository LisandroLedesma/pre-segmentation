"""
Image processing utilities for the pre-segmentation tool.
"""
import cv2
import numpy as np
from PIL import Image


def draw_points_on_image(img, coordinates_list):
    """
    Draw points on an image with different colors for foreground/background.
    
    Args:
        img (PIL.Image): The original image
        coordinates_list (list): List of coordinate dictionaries
        
    Returns:
        PIL.Image: Image with points drawn on it
    """
    # Convertir PIL a OpenCV
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # Dibujar puntos existentes
    for coord in coordinates_list:
        if "Label" in coord:  # Es un punto
            x, y = int(coord["X"]), int(coord["Y"])
            color = (0, 255, 0) if coord["Label"] == 1 else (0, 0, 255)  # Verde para foreground, rojo para background
            cv2.circle(img_cv, (x, y), 8, color, -1)
            cv2.circle(img_cv, (x, y), 10, (255, 255, 255), 2)  # Borde blanco
            # Agregar número de índice
            cv2.putText(img_cv, str(coord["Índice"]), (x+12, y-12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Convertir de vuelta a PIL
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb)


def validate_coordinates(x, y, image_width, image_height):
    """
    Validate that coordinates are within image bounds.
    
    Args:
        x (int): X coordinate
        y (int): Y coordinate
        image_width (int): Image width
        image_height (int): Image height
        
    Returns:
        bool: True if coordinates are valid
    """
    return 0 <= x < image_width and 0 <= y < image_height


def get_image_info(image):
    """
    Get basic information about an image.
    
    Args:
        image (PIL.Image): The image to analyze
        
    Returns:
        dict: Dictionary with image information
    """
    return {
        "width": image.width,
        "height": image.height,
        "format": image.format,
        "mode": image.mode
    }
