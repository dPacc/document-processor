#!/usr/bin/env python3
"""
Main Document Processor - Orchestrates all processing components using new logic
"""

import time
import numpy as np
from typing import Tuple, Optional, Union
from pathlib import Path

from .preprocessing import enhanced_preprocess
from .detection import DocumentDetector
from .rotation import RotationDetector, RotationCorrector
from .utils import load_image, save_image, format_output


class DocumentProcessor:
    """
    Document processor with modular architecture using new advanced deskew logic
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.detector = DocumentDetector(debug=debug)
        self.rotation_detector = RotationDetector(debug=debug)
        self.rotation_corrector = RotationCorrector()
        
    def process(self, image: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Process document image with new advanced logic but modular approach
        """
        start_time = time.time()
        
        if image is None or image.size == 0:
            raise ValueError("Invalid input image")
        
        original_shape = image.shape[:2]
        if self.debug:
            print(f"Original image size: {original_shape}")
        
        # Step 1: Preprocess image
        gray = enhanced_preprocess(image)
        
        # Step 2: ALWAYS detect skew angle on full image first (new approach)
        full_image_angle = self.rotation_detector.detect_full_image_angle(image)
        if self.debug:
            print(f"Full image skew angle: {full_image_angle:.3f}°")
        
        # Step 3: Try to detect and crop document (using new advanced detection)
        cropped_document = self.detector.detect_advanced(image, gray)
        
        if cropped_document is not None:
            if self.debug:
                print(f"Cropped document size: {cropped_document.shape[:2]}")
            
            # Step 4: Detect rotation angle on the CROPPED document
            cropped_angle = self.rotation_detector.detect_cropped_angle(cropped_document)
            
            # Step 5: Apply deskewing to cropped document
            corrected_document = self.rotation_corrector.deskew_document(cropped_document, cropped_angle)
            final_angle = cropped_angle
            
            if self.debug:
                print(f"Applied deskewing correction to cropped document: {cropped_angle:.3f}°")
        else:
            # No document detected - deskew full image (fallback)
            if self.debug:
                print("Could not detect document boundaries - deskewing full image")
            
            corrected_document = self.rotation_corrector.deskew_document(image, full_image_angle)
            final_angle = full_image_angle
            
            if self.debug:
                print(f"Applied deskewing correction to full image: {full_image_angle:.3f}°")
        
        if self.debug:
            elapsed = (time.time() - start_time) * 1000
            print(f"Processing completed in {elapsed:.1f}ms")
            print(f"Final result size: {corrected_document.shape[:2]}")
            print(f"Detected rotation: {final_angle:.3f}°")
            print("-" * 60)
        
        return final_angle, corrected_document


def process_document_image(image_path: Union[str, Path], 
                          output_format: str = 'ndarray',
                          save_path: Optional[Path] = None,
                          verbose: bool = False) -> Tuple[float, Union[np.ndarray, str]]:
    """Process document image with modular processor"""
    start_time = time.time()
    
    # Load image
    image = load_image(image_path)
    
    # Process with modular processor
    processor = DocumentProcessor(debug=verbose)
    angle, processed = processor.process(image)
    
    # Save if requested
    save_image(processed, save_path)
    
    # Format output
    result = format_output(processed, output_format)
    
    if verbose:
        elapsed = (time.time() - start_time) * 1000
        print(f"\n{'='*60}")
        print(f"FINAL SUMMARY:")
        print(f"Input: {Path(image_path).name}")
        print(f"Detected rotation: {angle:.3f}°")
        print(f"Original: {image.shape[:2]} -> Final: {processed.shape[:2]}")
        print(f"Processing time: {elapsed:.1f}ms")
        print(f"{'='*60}")
    
    return angle, result