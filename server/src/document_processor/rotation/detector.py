"""
Document rotation angle detection using multiple methods.
"""

import cv2
import numpy as np


class RotationDetector:
    """Detect document rotation angle using multiple algorithms"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def detect_angle(self, document: np.ndarray) -> float:
        """
        Detect rotation angle of the cropped document
        """
        if document is None or document.size == 0:
            return 0.0
        
        # Convert to grayscale if needed
        if len(document.shape) == 3:
            gray = cv2.cvtColor(document, cv2.COLOR_BGR2GRAY)
        else:
            gray = document.copy()
        
        angles = []
        weights = []
        
        # Method 1: Hough line detection (most reliable for documents)
        hough_angle = self._hough_line_angle_detection(gray)
        if abs(hough_angle) <= 30:  # Reasonable rotation range
            angles.append(hough_angle)
            weights.append(0.6)
            
        # Method 2: Text line detection
        text_angle = self._text_line_angle_detection(gray)
        if abs(text_angle) <= 30:
            angles.append(text_angle)
            weights.append(0.3)
            
        # Method 3: Projection profile
        projection_angle = self._projection_profile_angle_detection(gray)
        if abs(projection_angle) <= 30:
            angles.append(projection_angle)
            weights.append(0.1)
        
        if not angles:
            return 0.0
        
        # Remove outliers if we have multiple angles
        if len(angles) > 1:
            median_angle = np.median(angles)
            filtered_angles = []
            filtered_weights = []
            
            for angle, weight in zip(angles, weights):
                if abs(angle - median_angle) <= 10:  # Within 10 degrees of median
                    filtered_angles.append(angle)
                    filtered_weights.append(weight)
            
            if filtered_angles:
                angles = filtered_angles
                weights = filtered_weights
        
        # Calculate weighted average
        weights = np.array(weights)
        weights = weights / np.sum(weights)
        final_angle = np.average(angles, weights=weights)
        
        if self.debug:
            print(f"Angle detection - Hough: {hough_angle:.1f}°, Text: {text_angle:.1f}°, Projection: {projection_angle:.1f}° -> Final: {final_angle:.1f}°")
        
        return final_angle
    
    def _hough_line_angle_detection(self, gray: np.ndarray) -> float:
        """Detect rotation using Hough line transform"""
        try:
            # Edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Hough line detection
            lines = cv2.HoughLinesP(edges, 1, np.pi/180,
                                   threshold=max(30, int(min(gray.shape) * 0.3)),
                                   minLineLength=int(min(gray.shape) * 0.2),
                                   maxLineGap=10)
            
            if lines is None:
                return 0.0
            
            # Calculate angles from lines
            valid_angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                
                if length > min(gray.shape) * 0.1:  # Minimum line length
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    
                    # Normalize angle to [-45, 45] range for document orientation
                    while angle > 45:
                        angle -= 90
                    while angle < -45:
                        angle += 90
                    
                    if abs(angle) <= 30:  # Reasonable skew range
                        valid_angles.append(angle)
            
            if valid_angles:
                return np.median(valid_angles)
            
        except Exception:
            pass
        
        return 0.0
    
    def _text_line_angle_detection(self, gray: np.ndarray) -> float:
        """Detect rotation using text line analysis"""
        try:
            # Enhance horizontal text structures
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
            horizontal = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # Get text regions
            _, thresh = cv2.threshold(horizontal, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Find text line contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            angles = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 50:  # Minimum area for text line
                    # Fit line to contour
                    [vx, vy, x, y] = cv2.fitLine(contour, cv2.DIST_L2, 0, 0.01, 0.01)
                    angle = np.arctan2(vy, vx) * 180 / np.pi
                    
                    # Normalize angle
                    while angle > 45:
                        angle -= 90
                    while angle < -45:
                        angle += 90
                    
                    if abs(angle) <= 25:  # Text should be roughly horizontal
                        angles.append(angle)
            
            return np.median(angles) if angles else 0.0
            
        except Exception:
            return 0.0
    
    def _projection_profile_angle_detection(self, gray: np.ndarray) -> float:
        """Detect rotation using projection profile"""
        try:
            angles_to_test = np.arange(-15, 16, 3)
            best_angle = 0
            best_variance = 0
            
            h, w = gray.shape
            center = (w // 2, h // 2)
            
            for angle in angles_to_test:
                # Rotate image slightly
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(gray, M, (w, h), borderValue=255)
                
                # Calculate horizontal projection variance
                h_projection = np.sum(rotated, axis=1)
                variance = np.var(h_projection)
                
                if variance > best_variance:
                    best_variance = variance
                    best_angle = angle
            
            return best_angle
            
        except Exception:
            return 0.0