"""
Image enhancement and preprocessing utilities.
"""

import cv2
import numpy as np


def enhanced_preprocess(image: np.ndarray) -> np.ndarray:
    """Enhanced preprocessing for document detection"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Noise reduction while preserving edges
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Enhance contrast for better detection
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    return gray


def enhance_final_result(document: np.ndarray) -> np.ndarray:
    """Final enhancement of the processed document"""
    if document is None or document.size == 0:
        return document
    
    # Add clean white border
    padding = 30
    result = cv2.copyMakeBorder(document, padding, padding, padding, padding,
                              cv2.BORDER_CONSTANT, value=(255, 255, 255))
    
    # Ensure reasonable minimum size
    h, w = result.shape[:2]
    min_size = 600
    if h < min_size or w < min_size:
        scale_factor = max(min_size/h, min_size/w, 1.0)
        if scale_factor > 1.0:
            new_h, new_w = int(h * scale_factor), int(w * scale_factor)
            result = cv2.resize(result, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    # Optional: subtle noise reduction while preserving details
    if len(result.shape) == 3:
        result = cv2.bilateralFilter(result, 3, 20, 20)
    
    return result


def minimal_process(image: np.ndarray) -> np.ndarray:
    """Minimal processing for fallback cases"""
    padding = 40
    return cv2.copyMakeBorder(image, padding, padding, padding, padding,
                            cv2.BORDER_CONSTANT, value=(255, 255, 255))