"""
Document rotation correction using jdeskew library.
"""

import numpy as np
from jdeskew.utility import rotate


class RotationCorrector:
    """Correct document rotation using jdeskew"""
    
    def __init__(self):
        pass
    
    def rotate_document(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Legacy method for backward compatibility"""
        return self.deskew_document(image, angle)
    
    def deskew_document(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        Apply deskewing rotation to document using jdeskew
        
        Args:
            image: Input image (color or grayscale)
            angle: Rotation angle in degrees (from jdeskew)
            
        Returns:
            Deskewed image
        """
        if image is None or image.size == 0:
            return image
        
        try:
            # Use jdeskew's rotate function which handles color preservation
            deskewed = rotate(image, angle)
            return deskewed
        except Exception as e:
            print(f"Error applying deskew rotation: {e}")
            return image