"""
Image quality assessment utilities.
"""

import cv2
import numpy as np


def is_unusable_quality(image: np.ndarray, debug: bool = False) -> bool:
    """Check if image quality is too poor to process"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
        
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = np.mean(gray)
    
    is_poor = blur_score < 50 or brightness < 20 or brightness > 240
    if debug and is_poor:
        print(f"Poor quality: blur={blur_score:.1f}, brightness={brightness:.1f}")
    
    return is_poor