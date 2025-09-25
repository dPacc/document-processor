"""
Input/Output utilities for document processing.
"""

import cv2
import base64
import numpy as np
from pathlib import Path
from typing import Union, Tuple


def load_image(image_path: Union[str, Path]) -> np.ndarray:
    """Load image from file path"""
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Cannot read image: {image_path}")
    return image


def save_image(image: np.ndarray, save_path: Union[str, Path]) -> None:
    """Save image to file path"""
    if save_path:
        cv2.imwrite(str(save_path), image)


def format_output(image: np.ndarray, output_format: str) -> Union[np.ndarray, str]:
    """Format output image according to specified format"""
    if output_format == 'base64':
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        return base64.b64encode(buffer).decode('utf-8')
    else:
        return image