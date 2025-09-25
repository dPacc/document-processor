"""
Document boundary detection using multiple algorithms.
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class DocumentDetector:
    """Document detection using multiple methods for robustness"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def detect(self, image: np.ndarray, gray: np.ndarray) -> Optional[np.ndarray]:
        """
        Robust document detection using multiple methods
        """
        h, w = gray.shape
        
        # Method 1: Contour-based detection
        document_bounds = self._detect_by_contours(gray)
        
        # Method 2: Edge-based detection
        if document_bounds is None:
            document_bounds = self._detect_by_edges(gray)
        
        # Method 3: Color-based detection (for color images)
        if document_bounds is None and len(image.shape) == 3:
            document_bounds = self._detect_by_color(image)
        
        # Method 4: Statistical detection
        if document_bounds is None:
            document_bounds = self._detect_by_statistics(gray)
        
        # Method 5: Fallback detection
        if document_bounds is None:
            document_bounds = self._fallback_detection(gray)
        
        if document_bounds is None:
            return None
        
        # Extract the document region
        x, y, crop_w, crop_h = document_bounds
        
        # Ensure bounds are within image
        x = max(0, min(x, w-1))
        y = max(0, min(y, h-1))
        crop_w = max(1, min(crop_w, w - x))
        crop_h = max(1, min(crop_h, h - y))
        
        cropped = image[y:y+crop_h, x:x+crop_w]
        
        if self.debug:
            print(f"Detected document at: x={x}, y={y}, w={crop_w}, h={crop_h}")
            area_ratio = (crop_w * crop_h) / (w * h)
            print(f"Document area ratio: {area_ratio:.3f}")
        
        return cropped
    
    def _detect_by_contours(self, gray: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect document using contour analysis"""
        try:
            # Multiple thresholding strategies
            binary_images = []
            
            # Adaptive thresholding with different parameters
            for block_size in [11, 15, 21, 31]:
                for c_val in [2, 5, 8, 12]:
                    try:
                        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                     cv2.THRESH_BINARY, block_size, c_val)
                        binary_images.append(binary)
                    except:
                        continue
            
            # OTSU thresholding
            _, otsu_binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            binary_images.append(otsu_binary)
            
            # Edge-based binary
            edges = cv2.Canny(gray, 30, 100)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            edge_binary = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
            binary_images.append(edge_binary)
            
            best_contour = None
            best_score = 0
            
            for binary in binary_images:
                # Invert binary for document detection (document is darker than background)
                binary_inv = cv2.bitwise_not(binary)
                
                contours, _ = cv2.findContours(binary_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
                    area = cv2.contourArea(contour)
                    total_area = gray.shape[0] * gray.shape[1]
                    area_ratio = area / total_area
                    
                    # Document should occupy reasonable area
                    if 0.15 <= area_ratio <= 0.9:
                        # Check aspect ratio
                        rect = cv2.minAreaRect(contour)
                        w, h = sorted(rect[1])  # width, height (sorted)
                        
                        if w > 0 and h > 0:
                            aspect_ratio = w / h
                            # Document aspect ratio varies, use broader range
                            aspect_score = 1.0 if 0.5 <= aspect_ratio <= 2.0 else 0.5
                            aspect_score = max(0, aspect_score)
                            
                            # Rectangularity check
                            hull = cv2.convexHull(contour)
                            hull_area = cv2.contourArea(hull)
                            rectangularity = area / hull_area if hull_area > 0 else 0
                            
                            # Combined score
                            score = area_ratio * aspect_score * rectangularity
                            
                            if score > best_score and score > 0.05:
                                best_score = score
                                best_contour = contour
            
            if best_contour is not None:
                bounds = cv2.boundingRect(best_contour)
                if self.debug:
                    print(f"Contour detection score: {best_score:.3f}")
                return bounds
                
        except Exception as e:
            if self.debug:
                print(f"Contour detection failed: {e}")
        
        return None
    
    def _detect_by_edges(self, gray: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect document using edge detection"""
        try:
            # Multi-scale edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Morphological operations to connect edges
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
            edges_filled = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=3)
            
            # Find contours in edge image
            contours, _ = cv2.findContours(edges_filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                total_area = gray.shape[0] * gray.shape[1]
                
                if 0.1 <= area/total_area <= 0.85:
                    bounds = cv2.boundingRect(largest_contour)
                    if self.debug:
                        print(f"Edge detection area ratio: {area/total_area:.3f}")
                    return bounds
                    
        except Exception as e:
            if self.debug:
                print(f"Edge detection failed: {e}")
        
        return None
    
    def _detect_by_color(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect document using color analysis"""
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Create masks for different document colors
            masks = []
            
            # Light colored documents (beige/cream/white)
            lower_light = np.array([0, 0, 180])
            upper_light = np.array([180, 80, 255])
            mask_light = cv2.inRange(hsv, lower_light, upper_light)
            masks.append(mask_light)
            
            # Red/burgundy documents
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
            
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
            
            mask_red = cv2.bitwise_or(mask_red1, mask_red2)
            masks.append(mask_red)
            
            # Blue documents
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
            masks.append(mask_blue)
            
            # Combine all masks
            combined_mask = np.zeros_like(mask_light)
            for mask in masks:
                combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Clean up mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Find largest component
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest)
                total_area = image.shape[0] * image.shape[1]
                
                if area / total_area > 0.1:
                    bounds = cv2.boundingRect(largest)
                    if self.debug:
                        print(f"Color detection area ratio: {area/total_area:.3f}")
                    return bounds
                    
        except Exception as e:
            if self.debug:
                print(f"Color detection failed: {e}")
        
        return None
    
    def _detect_by_statistics(self, gray: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect document using statistical analysis"""
        try:
            # Find regions with content (text/images)
            # Use gradient magnitude to find content regions
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Threshold to get content regions
            threshold = np.percentile(gradient_magnitude, 75)
            content_mask = (gradient_magnitude > threshold).astype(np.uint8) * 255
            
            # Clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            content_mask = cv2.morphologyEx(content_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            
            # Find bounding box of content
            coords = cv2.findNonZero(content_mask)
            if coords is not None:
                bounds = cv2.boundingRect(coords)
                x, y, w, h = bounds
                area_ratio = (w * h) / (gray.shape[0] * gray.shape[1])
                
                if 0.1 <= area_ratio <= 0.9:
                    if self.debug:
                        print(f"Statistical detection area ratio: {area_ratio:.3f}")
                    return bounds
                    
        except Exception as e:
            if self.debug:
                print(f"Statistical detection failed: {e}")
        
        return None
    
    def _fallback_detection(self, gray: np.ndarray) -> Tuple[int, int, int, int]:
        """Fallback detection - crop borders"""
        h, w = gray.shape
        
        # Remove 5% border from each side
        border_h = max(1, h // 20)
        border_w = max(1, w // 20)
        
        bounds = (border_w, border_h, w - 2*border_w, h - 2*border_h)
        if self.debug:
            print("Using fallback detection (border crop)")
        return bounds