"""
FastAPI application for document processing
"""

import io
import base64
import time
from typing import List, Union
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import numpy as np
from PIL import Image
import cv2

from .processor import DocumentProcessor


class ProcessResponse(BaseModel):
    """Response model for single document processing"""
    rotation_angle: float = Field(..., description="Detected rotation angle in degrees")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    image_base64: str = Field(..., description="Processed image as base64 string")
    original_size: tuple = Field(..., description="Original image dimensions (height, width)")
    final_size: tuple = Field(..., description="Final processed image dimensions (height, width)")


class BatchProcessResponse(BaseModel):
    """Response model for batch document processing"""
    total_processed: int = Field(..., description="Number of images processed")
    total_time_ms: float = Field(..., description="Total processing time in milliseconds")
    results: List[ProcessResponse] = Field(..., description="Individual processing results")
    failed_files: List[str] = Field(default=[], description="Names of files that failed to process")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Health check message")
    version: str = Field(..., description="API version")


app = FastAPI(
    title="Document Processor API",
    description="API for document image processing - orientation correction and boundary detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


def image_to_base64(image: np.ndarray) -> str:
    """Convert numpy array to base64 string"""
    # Convert BGR to RGB if needed
    if len(image.shape) == 3 and image.shape[2] == 3:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image
    
    # Convert to PIL Image
    pil_image = Image.fromarray(image_rgb)
    
    # Convert to base64
    buffer = io.BytesIO()
    pil_image.save(buffer, format='JPEG', quality=95)
    img_bytes = buffer.getvalue()
    
    return base64.b64encode(img_bytes).decode('utf-8')


def process_uploaded_file(file: UploadFile) -> tuple:
    """Process an uploaded file and return results"""
    start_time = time.time()
    
    try:
        # Read file contents
        contents = file.file.read()
        
        # Convert to numpy array
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError(f"Could not decode image: {file.filename}")
        
        original_size = image.shape[:2]
        
        # Process the image
        processor = DocumentProcessor(debug=False)
        rotation_angle, processed_image = processor.process(image)
        
        # Convert to base64
        image_base64 = image_to_base64(processed_image)
        
        processing_time = (time.time() - start_time) * 1000
        final_size = processed_image.shape[:2]
        
        return ProcessResponse(
            rotation_angle=rotation_angle,
            processing_time_ms=processing_time,
            image_base64=image_base64,
            original_size=original_size,
            final_size=final_size
        ), None
        
    except Exception as e:
        return None, str(e)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Document processor API is running",
        version="1.0.0"
    )


@app.post("/process", response_model=ProcessResponse)
async def process_document(file: UploadFile = File(..., description="Document image file to process")):
    """
    Process a single document image for orientation correction and boundary detection
    
    Accepts: JPG, JPEG, PNG image files
    Returns: Rotation angle and processed image as base64
    """
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="File must be an image (JPG, JPEG, PNG)"
        )
    
    result, error = process_uploaded_file(file)
    
    if error:
        raise HTTPException(status_code=400, detail=f"Processing failed: {error}")
    
    return result


@app.post("/process-batch", response_model=BatchProcessResponse)
async def process_documents_batch(files: List[UploadFile] = File(..., description="Multiple document image files to process")):
    """
    Process multiple document images in batch
    
    Accepts: List of JPG, JPEG, PNG image files
    Returns: Processing results for all images
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 20:  # Limit batch size
        raise HTTPException(status_code=400, detail="Maximum 20 files allowed per batch")
    
    start_time = time.time()
    results = []
    failed_files = []
    processed_count = 0
    
    for file in files:
        if not file.content_type or not file.content_type.startswith('image/'):
            failed_files.append(f"{file.filename}: Not an image file")
            continue
        
        result, error = process_uploaded_file(file)
        
        if error:
            failed_files.append(f"{file.filename}: {error}")
        else:
            results.append(result)
            processed_count += 1
    
    total_time = (time.time() - start_time) * 1000
    
    return BatchProcessResponse(
        total_processed=processed_count,
        total_time_ms=total_time,
        results=results,
        failed_files=failed_files
    )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Document Processor API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "process_single": "/process",
            "process_batch": "/process-batch",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)