# NOVA Document Processor

A robust, enterprise-grade document image processing system with beautiful React client and FastAPI backend. Features AI-powered document orientation correction and boundary detection with professional-grade accuracy and performance.

## 🚀 Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- 4GB RAM minimum
- 2GB free disk space

### One-Command Setup

```bash
# Clone and start the entire stack
git clone https://github.com/dPacc/document-processor.git
cd document-processor
docker compose up --build
```

**Access the application:**

- 🌐 **Web Client**: <http://localhost:3050>
- 🔧 **API Server**: <http://localhost:8050>
- 📚 **API Docs**: <http://localhost:8050/docs>

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   React Client  │◄──►│  FastAPI Server │
│   (Port 3050)   │    │   (Port 8050)   │
│                 │    │                 │
│ • Beautiful UI  │    │ • AI Processing │
│ • File Upload   │    │ • Multi-format  │
│ • Drag & Drop   │    │ • Sub-100ms     │
│ • Real-time     │    │ • Enterprise    │
└─────────────────┘    └─────────────────┘
```

## ✨ Features

### 🎯 **Core Processing**

- **Advanced Document Detection**: Sophisticated OpenCV pipeline with multiple edge detection methods
- **Precise Skew Correction**: Uses jdeskew library for sub-degree accuracy angle detection
- **Perspective Correction**: Four-point transformation for document boundary correction
- **Intelligent Fallback**: Full image deskewing when document boundaries aren't detected
- **Multi-format Support**: JPG, JPEG, PNG with batch processing
- **Background-Aware Processing**: Optimized for various background types and textures

### 🎨 **Beautiful Web Interface**

- **Modern React UI**: Professional design with Framer Motion animations
- **Drag & Drop Upload**: Intuitive file handling with visual feedback
- **Real-time Processing**: Live progress indicators and results
- **Responsive Design**: Works on desktop, tablet, and mobile

### 🔧 **Enterprise Features**

- **Docker Ready**: Complete containerization with production configs
- **Health Monitoring**: Built-in health checks and monitoring
- **Batch Processing**: Handle up to 20 files simultaneously
- **Error Handling**: Comprehensive error management and reporting
- **Security**: Content validation and secure file handling

## 🐳 Docker Deployment Options

### Development Mode

```bash
docker compose up --build
```

### Background Mode

```bash
docker compose up --build -d
```

### Stop Services

```bash
docker compose down
```

## 🛠️ Development Setup

### Local Development (without Docker)

**Server (using Poetry - recommended):**

**Note**: Poetry requires Python 3.12+. If you don't have Python 3.12, install it first or use the pip method below.

**Installing Python 3.12 on Ubuntu:**

```bash
# Add deadsnakes PPA
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3.12-dev
```

**Then run Poetry setup:**

```bash
cd server
poetry env use python3.12  # Configure Poetry to use Python 3.12
poetry install  # Installs OpenCV, jdeskew, FastAPI, and all dependencies
poetry run uvicorn src.document_processor.api:app --host 0.0.0.0 --port 8050 --reload
```

**Server (alternative with pip):**

```bash
cd server
pip install -r requirements.txt  # Includes jdeskew, OpenCV, FastAPI, etc.
python -m uvicorn src.document_processor.api:app --host 0.0.0.0 --port 8050 --reload
```

**Or using the local script:**

```bash
./run-local.sh
```

**Client (if running separately):**

```bash
cd client
npm install
REACT_APP_API_URL=http://localhost:8050 npm start
```

## 🖥️ Command Line Interface

### Single Image Processing

```bash
# Process single image with advanced deskew logic (from server directory)
cd server

# Using Poetry (recommended)
poetry run python -m src.document_processor.cli input.jpg -o output_dir/
# Or using Poetry script
poetry run process-document input.jpg -o output_dir/

# Using pip installation
python -m src.document_processor.cli input.jpg -o output_dir/

# Process with verbose output (shows detection and deskew details)
poetry run python -m src.document_processor.cli input.jpg -o output_dir/ --verbose
```

### Bulk Processing (Folder)

```bash
# Process all images in a folder
cd server

# Using Poetry (recommended)
poetry run python -m src.document_processor.cli /path/to/image/folder -o /path/to/output

# Using pip installation
python -m src.document_processor.cli /path/to/image/folder -o /path/to/output

# Process folder with default output location (creates 'processed' subfolder)
poetry run python -m src.document_processor.cli /path/to/image/folder
```

**CLI Options:**

- `-o, --output`: Output directory for processed images
- `-f, --format`: Output format (`ndarray` or `base64`)
- `-v, --verbose`: Enable verbose output

**Example Output:**

```
Processing 5 images with document processor...
Output directory: /path/to/output
[ 1/ 5] image1.jpg                     +2.45°   82ms ✓
[ 2/ 5] image2.png                     -1.23°   95ms ✓
[ 3/ 5] image3.jpg                     +0.67°   78ms ✓

======================================================================
BATCH PROCESSING COMPLETE
Successful: 5/5
Failed: 0/5
Average time: 85ms
Max time: 95ms
======================================================================
```

## 📖 API Documentation

### Health Check

```bash
curl http://localhost:8050/health
```

### Single Document Processing

```bash
curl -X POST "http://localhost:8050/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.jpg"
```

### Batch Processing

```bash
curl -X POST "http://localhost:8050/process-batch" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@doc1.jpg" \
  -F "files=@doc2.png" \
  -F "files=@doc3.jpeg"
```

**Response Format:**

```json
{
  "rotation_angle": -0.5,
  "processing_time_ms": 892.1,
  "image_base64": "base64_encoded_string",
  "original_size": [1200, 800],
  "final_size": [1180, 820]
}
```

## 🎯 Technical Specifications

### Advanced Processing Pipeline

- **Document Detection**: Multi-step OpenCV pipeline with adaptive thresholding and multiple Canny edge detection approaches
- **Perspective Correction**: Four-point transformation with automatic corner detection using Douglas-Peucker algorithm
- **Skew Detection**: jdeskew library for precise angle detection on both full images and cropped documents
- **Fallback Processing**: Intelligent fallback to full-image deskewing when document boundaries aren't detected

### Background Optimization

Based on extensive testing, the system performs optimally with:
- **Best**: Solid dark backgrounds (black, navy, dark green)
- **Good**: High-contrast solid colors  
- **Poor**: Textured surfaces (wood, fabric, concrete)
- **Worst**: Similar colors to document

### Libraries Used

- **OpenCV**: Advanced computer vision and document detection
- **jdeskew**: Specialized library for precise skew angle detection and correction
- **NumPy**: Array processing and mathematical computations
- **FastAPI**: Modern Python web framework
- **React**: Frontend user interface
- **Docker**: Containerization and deployment

## 📂 Project Structure

```
nova-it-document-processor/
├── server/                 # FastAPI Backend
│   ├── src/
│   │   └── document_processor/
│   │       ├── api.py              # FastAPI application
│   │       ├── processor.py        # Main orchestrator
│   │       ├── detection/          # Document detection
│   │       ├── rotation/           # Rotation correction
│   │       ├── preprocessing/      # Image enhancement
│   │       └── utils/              # Utilities
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
├── client/                 # React Frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── services/               # API services
│   │   └── styles/                 # CSS styles
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml      # Docker setup
├── run-local.sh           # Local development script
└── README.md
```

## 🧪 Testing

### API Testing

```bash
# Test health endpoint
curl http://localhost:8050/health

# Test with sample image
curl -X POST http://localhost:8050/process \
  -F "file=@dataset/Canada.jpg"
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test concurrent requests
ab -n 100 -c 10 http://localhost:8050/health
```

## 🔒 Security Features

- **Input Validation**: File type and size validation
- **Content Security**: Image format verification
- **Error Isolation**: Secure error handling without information leakage
- **Resource Limits**: Memory and processing constraints
- **CORS Configuration**: Controlled cross-origin requests

## 📈 Monitoring & Logging

### Health Checks

- **Server**: `/health` endpoint with detailed status
- **Client**: React development server health check
- **Docker**: Built-in container health monitoring

### Logging

- **Structured Logging**: JSON format for production
- **Request Tracing**: API request/response logging
- **Error Tracking**: Comprehensive error logging with context

## 🚀 Deployment

### Environment Variables

```bash
# Client
REACT_APP_API_URL=http://localhost:8050

# Server
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```
