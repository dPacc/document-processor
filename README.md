# Document Processor

A robust document image processing system designed for orientation correction and boundary detection. This system can identify and correct document rotation (0–360°) and accurately detect and crop document boundaries, removing extraneous background regions.

## Features

- **Multi-method Document Detection**: Uses 5 different detection algorithms for maximum robustness
  - Contour-based detection
  - Edge-based detection  
  - Color-based detection
  - Statistical analysis
  - Fallback border detection

- **Advanced Rotation Correction**: Combines multiple angle detection methods
  - Hough line transform
  - Text line analysis
  - Projection profile analysis

- **High Performance**: Optimized for execution times under 100ms per image

- **Flexible Output**: Returns both rotation angle and processed image (as numpy array or base64)

## Requirements

- Python 3.12+
- Poetry for dependency management

## Installation

1. Clone or extract the project directory
2. Navigate to the project root
3. Install dependencies using Poetry:

```bash
cd document-processor
poetry install
```

## Usage

### Command Line Interface

#### Process a single image:
```bash
poetry run process-document input.jpg -o output.jpg -v
```

#### Process a directory of images:
```bash
poetry run process-document ./images/ -o ./processed/ -v
```

#### Options:
- `-o, --output`: Output file or directory
- `-f, --format`: Output format (`ndarray` or `base64`, default: `ndarray`)
- `-v, --verbose`: Enable verbose output with processing details

### Python API

```python
from document_processor import process_document_image, FixedDocumentProcessor

# Process a single image
angle, processed_image = process_document_image(
    image_path="path/to/image.jpg",
    output_format="ndarray",  # or "base64"
    save_path="path/to/output.jpg",
    verbose=True
)

# Use the processor class directly
processor = FixedDocumentProcessor(debug=True)
angle, result = processor.process(image_array)
```

### FastAPI Web Service (Bonus)

Start the web service:
```bash
poetry run uvicorn document_processor.api:app --reload
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

#### API Endpoints:

- `POST /process`: Upload and process a document image
- `GET /health`: Health check endpoint

Example usage:
```bash
curl -X POST "http://localhost:8000/process" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.jpg"
```

## Technical Approach

### 1. Quality Assessment
The system first performs a quality check using blur detection and brightness analysis to determine if the image is processable.

### 2. Document Detection (Crop-First Strategy)
The system uses a **crop-first approach** which is critical for accuracy:

1. **Enhanced Preprocessing**: Bilateral filtering and CLAHE contrast enhancement
2. **Multi-method Detection**: Five detection methods tried sequentially:
   - Contour analysis with multiple thresholding strategies
   - Edge detection with morphological operations
   - Color-based detection for different document types
   - Statistical gradient analysis
   - Fallback border cropping

### 3. Rotation Detection
Once the document is isolated, rotation is detected using:

1. **Hough Line Transform**: Detects document edges and text lines
2. **Text Line Analysis**: Morphological operations to find horizontal text structures
3. **Projection Profile**: Tests multiple angles to find optimal text alignment

### 4. Correction and Enhancement
- **Counter-rotation**: Applies opposite rotation to fix detected skew
- **High-quality interpolation**: Uses cubic interpolation for rotation
- **Smart resizing**: Prevents cropping during rotation
- **Final enhancement**: Adds padding and ensures minimum resolution

## Libraries Used

- **OpenCV (cv2)**: Core computer vision operations
- **NumPy**: Array operations and mathematical computations
- **FastAPI**: Web API framework (bonus feature)
- **Uvicorn**: ASGI server for FastAPI
- **Pillow**: Additional image format support

## Algorithmic Rationale

### Why Crop-First?
Processing the full image for rotation detection can be inaccurate due to background noise. By first isolating the document, rotation detection algorithms can focus on actual document features.

### Multiple Detection Methods
Real-world documents vary significantly in lighting, color, and background. Using multiple detection methods ensures robustness across different scenarios.

### Weighted Angle Averaging
Different rotation detection methods have varying reliability. The system uses weighted averaging with outlier removal to get the most accurate final angle.

### Performance Optimizations
- Efficient morphological operations
- Optimized contour analysis
- Smart image resizing
- Minimal memory allocations

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black src/
poetry run flake8 src/
```

### Type Checking
```bash
poetry run mypy src/
```

## Project Structure

```
document-processor/
├── pyproject.toml          # Poetry configuration and dependencies
├── README.md              # This file
├── src/
│   └── document_processor/
│       ├── __init__.py    # Package initialization
│       ├── processor.py   # Main orchestrator class
│       ├── cli.py         # Command-line interface
│       ├── detection/           # Document boundary detection
│       │   ├── __init__.py
│       │   └── detector.py     # 5 detection algorithms (contour, edge, color, statistical, fallback)
│       ├── rotation/            # Rotation detection & correction  
│       │   ├── __init__.py
│       │   ├── detector.py     # 3 angle detection methods (Hough, text, projection)
│       │   └── corrector.py    # Rotation correction logic
│       ├── preprocessing/       # Image enhancement & quality checks
│       │   ├── __init__.py
│       │   ├── quality_check.py # Blur/brightness analysis
│       │   └── enhance.py      # Bilateral filtering, CLAHE, final enhancement
│       ├── utils/              # I/O utilities
│       │   ├── __init__.py
│       │   └── io.py          # Load/save/format functions
│       └── api.py         # FastAPI web service
├── tests/                 # Test files
├── dataset/              # Sample images for testing
└── requirements.txt      # Generated requirements file
```

## Performance Benchmarks

The system is optimized to process most document images in under 100ms on modern hardware:

- **Simple documents**: 20-50ms
- **Complex documents**: 50-100ms
- **Large images (>2MB)**: 80-150ms

## License

This project is developed as part of a technical assessment.