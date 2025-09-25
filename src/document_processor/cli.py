#!/usr/bin/env python3
"""
Command-line interface for the document processor.
"""

import argparse
import time
from pathlib import Path
import numpy as np

from .processor import process_document_image


def main():
    parser = argparse.ArgumentParser(description="Fixed Document Processor")
    parser.add_argument("input", help="Input image or directory")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("-f", "--format", choices=['ndarray', 'base64'], default='ndarray')
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: {input_path} does not exist")
        return
    
    if input_path.is_file():
        # Single file processing
        output_path = None
        if args.output:
            output_path = Path(args.output)
            if output_path.is_dir():
                output_path = output_path / f"fixed_{input_path.name}"
        
        try:
            angle, result = process_document_image(input_path, args.format, output_path, args.verbose)
            print(f"✓ Successfully processed: {input_path.name}")
            print(f"  Rotation corrected: {angle:.2f}°")
            if output_path:
                print(f"  Saved to: {output_path}")
                
        except Exception as e:
            print(f"✗ Error processing {input_path.name}: {e}")
    
    elif input_path.is_dir():
        # Directory processing
        extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        images = [f for f in input_path.iterdir() if f.suffix.lower() in extensions]
        
        if not images:
            print(f"No images found in {input_path}")
            return
        
        output_dir = Path(args.output) if args.output else input_path / "processed"
        output_dir.mkdir(exist_ok=True, parents=True)
        
        print(f"Processing {len(images)} images with document processor...")
        print(f"Output directory: {output_dir}")
        
        successful = 0
        failed = 0
        times = []
        
        for i, img_path in enumerate(images, 1):
            try:
                output_path = output_dir / f"processed_{img_path.name}"
                
                start = time.time()
                angle, _ = process_document_image(img_path, 'ndarray', output_path, False)
                elapsed = (time.time() - start) * 1000
                
                times.append(elapsed)
                successful += 1
                
                print(f"[{i:2d}/{len(images)}] {img_path.name:30s} "
                      f"{angle:+6.2f}° {elapsed:5.0f}ms ✓")
                
            except Exception as e:
                failed += 1
                print(f"[{i:2d}/{len(images)}] {img_path.name:30s} ERROR: {str(e)[:50]}")
        
        # Final summary
        print(f"\n{'='*70}")
        print(f"BATCH PROCESSING COMPLETE")
        print(f"Successful: {successful}/{len(images)}")
        print(f"Failed: {failed}/{len(images)}")
        if times:
            print(f"Average time: {np.mean(times):.0f}ms")
            print(f"Max time: {np.max(times):.0f}ms")
        print(f"Output directory: {output_dir}")
        print(f"{'='*70}")


if __name__ == "__main__":
    main()