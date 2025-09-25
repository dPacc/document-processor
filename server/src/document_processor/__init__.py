"""
Document Processor - A robust system for document image processing.

This package provides functionality for:
- Document orientation detection and correction
- Document boundary detection and cropping
- Multiple detection algorithms for robustness
"""

from .processor import DocumentProcessor, process_document_image

__version__ = "1.0.0"
__all__ = ["DocumentProcessor", "process_document_image"]