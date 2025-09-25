#!/usr/bin/env python3
"""
Main Document Processor - Orchestrates all processing components
"""

import time
import numpy as np
from typing import Tuple, Optional, Union
from pathlib import Path

from .preprocessing import is_unusable_quality, enhanced_preprocess, enhance_final_result, minimal_process
from .detection import DocumentDetector
from .rotation import RotationDetector, RotationCorrector
from .utils import load_image, save_image, format_output


class DocumentProcessor:
    """
    Document processor with modular architecture for corrected rotation and cropping logic
    """
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.detector = DocumentDetector(debug=debug)
        self.rotation_detector = RotationDetector(debug=debug)
        self.rotation_corrector = RotationCorrector()
        
    def process(self, image: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Process document image with modular approach
        """
        start_time = time.time()
        
        if image is None or image.size == 0:
            raise ValueError("Invalid input image")
        
        original_shape = image.shape[:2]
        if self.debug:
            print(f"Original image size: {original_shape}")
        
        # Step 1: Quick quality check
        if is_unusable_quality(image, self.debug):
            if self.debug:
                print("Low quality detected - using minimal processing")
            return 0.0, minimal_process(image)
        
        # Step 2: Preprocess for better detection
        gray = enhanced_preprocess(image)
        
        # Step 3: CROP THE DOCUMENT FIRST (this is critical)
        cropped_document = self.detector.detect(image, gray)
        
        if cropped_document is None:
            if self.debug:
                print("No document detected - using minimal processing")
            return 0.0, minimal_process(image)
        
        if self.debug:
            print(f"Cropped document size: {cropped_document.shape[:2]}")
        
        # Step 4: Detect rotation angle on the CROPPED document only
        rotation_angle = self.rotation_detector.detect_angle(cropped_document)
        
        # Step 5: Rotate ONLY the cropped document (if needed)
        if abs(rotation_angle) > 0.5:
            corrected_document = self.rotation_corrector.rotate_document(cropped_document, rotation_angle)
            if self.debug:
                print(f"Applied rotation correction: {-rotation_angle:.1f}° to fix {rotation_angle:.1f}° skew")
        else:
            corrected_document = cropped_document
            if self.debug:
                print("No rotation needed")
        
        # Step 6: Final enhancement
        final_result = enhance_final_result(corrected_document)
        
        if self.debug:
            elapsed = (time.time() - start_time) * 1000
            print(f"Processing completed in {elapsed:.1f}ms")
            print(f"Final result size: {final_result.shape[:2]}")
            print(f"Detected rotation: {rotation_angle:.2f}°")
            print("-" * 60)
        
        return rotation_angle, final_result


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
        print(f"Detected rotation: {angle:.2f}°")
        print(f"Original: {image.shape[:2]} -> Final: {processed.shape[:2]}")
        print(f"Processing time: {elapsed:.1f}ms")
        print(f"{'='*60}")
    
    return angle, result