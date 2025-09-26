"""
Document rotation angle detection using jdeskew library.
"""

import cv2
import numpy as np
from jdeskew.estimator import get_angle


class RotationDetector:
    """Detect document rotation angle using jdeskew"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def detect_angle(self, document: np.ndarray) -> float:
        """Legacy method for backward compatibility"""
        return self.detect_cropped_angle(document)
    
    def detect_full_image_angle(self, image: np.ndarray) -> float:
        """
        Detect rotation angle of the full image using jdeskew
        """
        if image is None or image.size == 0:
            return 0.0
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        try:
            angle = get_angle(gray)
            if self.debug:
                print(f"Full image skew angle detected: {angle:.3f}°")
            return angle
        except Exception as e:
            if self.debug:
                print(f"Error detecting full image angle: {e}")
            return 0.0
    
    def detect_cropped_angle(self, document: np.ndarray) -> float:
        """
        Detect rotation angle of the cropped document using jdeskew
        """
        if document is None or document.size == 0:
            return 0.0
        
        # Convert to grayscale if needed
        if len(document.shape) == 3:
            gray = cv2.cvtColor(document, cv2.COLOR_BGR2GRAY)
        else:
            gray = document.copy()
        
        try:
            angle = get_angle(gray)
            if self.debug:
                print(f"Cropped document skew angle detected: {angle:.3f}°")
            return angle
        except Exception as e:
            if self.debug:
                print(f"Error detecting cropped document angle: {e}")
            return 0.0