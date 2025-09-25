"""
Document rotation correction utilities.
"""

import cv2
import numpy as np


class RotationCorrector:
    """Apply rotation correction to documents"""
    
    @staticmethod
    def rotate_document(document: np.ndarray, detected_angle: float) -> np.ndarray:
        """
        Rotate the document to correct skew
        CRITICAL: Apply counter-rotation to fix the detected skew
        """
        if abs(detected_angle) < 0.1:
            return document.copy()
        
        h, w = document.shape[:2]
        center = (w // 2, h // 2)
        
        # CORRECT THE ROTATION: if document is skewed +5°, rotate by -5° to fix it
        correction_angle = -detected_angle
        
        # Create rotation matrix
        M = cv2.getRotationMatrix2D(center, correction_angle, 1.0)
        
        # Calculate new image size to avoid cropping
        cos_a = abs(M[0, 0])
        sin_a = abs(M[0, 1])
        new_w = int(h * sin_a + w * cos_a)
        new_h = int(h * cos_a + w * sin_a)
        
        # Adjust translation to center the rotated image
        M[0, 2] += (new_w - w) / 2
        M[1, 2] += (new_h - h) / 2
        
        # Apply rotation with high quality interpolation
        rotated = cv2.warpAffine(document, M, (new_w, new_h),
                               flags=cv2.INTER_CUBIC,
                               borderMode=cv2.BORDER_CONSTANT,
                               borderValue=(255, 255, 255))
        
        return rotated