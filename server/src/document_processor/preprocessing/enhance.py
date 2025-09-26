"""
Simplified image preprocessing for new advanced logic.
"""

import cv2
import numpy as np


def enhanced_preprocess(image: np.ndarray) -> np.ndarray:
    """Simplified preprocessing for document detection"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply bilateral filter to reduce noise while preserving edges
    # This matches the new advanced_deskew approach
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)
    
    return filtered


# Simplified versions - remove complex quality checks since new approach is more robust
def is_unusable_quality(image: np.ndarray, debug: bool = False) -> bool:
    """Simplified quality check - new approach is more robust"""
    # Basic size check only
    if image is None or image.size == 0:
        return True
    
    h, w = image.shape[:2]
    if h < 100 or w < 100:  # Very small images
        if debug:
            print(f"Image too small: {w}x{h}")
        return True
    
    return False


def minimal_process(image: np.ndarray) -> np.ndarray:
    """Return original image for minimal processing"""
    return image


def enhance_final_result(image: np.ndarray) -> np.ndarray:
    """Return processed image as-is since jdeskew handles enhancement"""
    return image