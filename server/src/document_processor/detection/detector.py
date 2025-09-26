"""
Document boundary detection using advanced OpenCV pipeline.
"""

import cv2
import numpy as np
from typing import Optional


def order_points(pts):
    """Order points in clockwise order: top-left, top-right, bottom-right, bottom-left"""
    rect = np.zeros((4, 2), dtype="float32")
    
    # Sum and difference to find corners
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    
    # Top-left has smallest sum, bottom-right has largest sum
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right
    
    # Top-right has smallest difference, bottom-left has largest difference
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    
    return rect


def four_point_transform(image, pts):
    """Apply perspective transformation to get bird's eye view"""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    # Compute width and height of new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    # Define destination points for perspective transform
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    
    # Apply perspective transformation
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    
    return warped


class DocumentDetector:
    """Advanced document detector using new OpenCV pipeline"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def detect(self, image: np.ndarray, gray: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """Legacy method for backward compatibility"""
        return self.detect_advanced(image, gray)
    
    def detect_advanced(self, image: np.ndarray, gray: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """Advanced document detection using OpenCV pipeline"""
        original = image.copy()
        h, w = image.shape[:2]
        image_area = h * w
        
        # Convert to grayscale if not provided
        if gray is None:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
        
        # Step 1: Try adaptive thresholding approach for documents
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # Step 2: Multiple edge detection approaches with better parameters
        edges_list = []
        
        # Apply Gaussian blur first
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Canny with different parameters - more conservative
        edges1 = cv2.Canny(blurred, 50, 150, apertureSize=3)
        edges2 = cv2.Canny(blurred, 75, 225, apertureSize=3)
        edges3 = cv2.Canny(adaptive_thresh, 50, 150, apertureSize=3)
        
        edges_list = [edges1, edges2, edges3]
        
        # Step 3: Find contours and score them better
        best_contour = None
        best_score = 0
        
        for i, edges in enumerate(edges_list):
            # Dilate and erode to close gaps
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                continue
                
            # Sort contours by area
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            
            # Check contours for rectangular shapes
            for j, contour in enumerate(contours[:8]):  # Check more contours
                area = cv2.contourArea(contour)
                
                # More flexible area threshold based on image size
                min_area = max(20000, image_area * 0.1)  # At least 10% of image
                max_area = image_area * 0.9  # At most 90% of image
                
                if area < min_area or area > max_area:
                    continue
                    
                # Try multiple epsilon values
                best_approx = None
                for eps_factor in [0.01, 0.015, 0.02, 0.025, 0.03, 0.04]:
                    epsilon = eps_factor * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    if len(approx) == 4:
                        best_approx = approx
                        break
                
                if best_approx is not None and len(best_approx) == 4:
                    # Calculate better scoring
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    rectangularity = area / hull_area if hull_area > 0 else 0
                    
                    # Get the bounding rectangle
                    x, y, w_rect, h_rect = cv2.boundingRect(best_approx)
                    bounding_area = w_rect * h_rect
                    filling_ratio = area / bounding_area if bounding_area > 0 else 0
                    
                    # Calculate aspect ratio (should be reasonable for documents)
                    aspect_ratio = min(w_rect/h_rect, h_rect/w_rect) if h_rect > 0 and w_rect > 0 else 0
                    
                    # Check if it's not too close to image borders (likely not a document edge)
                    border_distance = min(x, y, w - (x + w_rect), h - (y + h_rect))
                    border_penalty = 1.0 if border_distance > 20 else 0.5
                    
                    # Combined score with area normalization
                    area_score = area / image_area  # Normalize by image size
                    score = (area_score * rectangularity * filling_ratio * aspect_ratio * border_penalty * 1000000)
                    
                    # Better thresholds
                    if (score > best_score and 
                        rectangularity > 0.75 and 
                        filling_ratio > 0.7 and 
                        aspect_ratio > 0.3 and
                        area_score > 0.15):  # At least 15% of image
                        
                        best_score = score
                        best_contour = best_approx
        
        # Step 4: If no good contour found, don't crop (return None)
        # This prevents bad cropping like we saw with Canada.jpg
        if best_contour is None:
            if self.debug:
                print("No suitable document contour found")
            return None
        
        # Step 5: Final validation - make sure the contour makes sense
        if best_contour is not None:
            x, y, w_rect, h_rect = cv2.boundingRect(best_contour)
            
            # If the detected region is too small relative to image, skip it
            detected_area = w_rect * h_rect
            if detected_area < image_area * 0.15:  # Less than 15% of image
                if self.debug:
                    print(f"Detected area too small: {detected_area/image_area:.1%} of image")
                return None
        
        if self.debug and best_contour is not None:
            print(f"Document detected with score: {best_score}")
            debug_img = original.copy()
            cv2.drawContours(debug_img, [best_contour], -1, (0, 255, 0), 3)
            # Note: In production, you might want to save this debug image
        
        # Apply perspective transformation to get the cropped document
        if best_contour is not None:
            if len(best_contour.shape) == 3:
                best_contour = best_contour.reshape(4, 2)
            
            # Apply perspective transformation
            warped = four_point_transform(original, best_contour)
            return warped
        
        return None