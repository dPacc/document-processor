# NOVA Document Processor - Deployment Guide

## 🚀 Quick Start Options

### Option 1: Local Development (Recommended for Testing)

```bash
# Ensure you have Python 3.11+ and Node.js installed
# Run the convenient startup script
./run-local.sh
```

**Access points:**

- 🌐 **Web Client**: <http://localhost:3050>
- 🔧 **API Server**: <http://localhost:8050>
- 📚 **API Docs**: <http://localhost:8050/docs>

### Option 2: Manual Setup

#### Server Setup

```bash
cd server
pip install -r requirements.txt
uvicorn src.document_processor.api:app --host 0.0.0.0 --port 8050 --reload
```

#### Client Setup (New Terminal)

```bash
cd client
npm install
export REACT_APP_API_URL=http://localhost:8050
npm start
```

### Option 3: Docker (If Network Access Available)

If your network allows access to Docker repositories:

```bash
docker-compose up --build
```

## 🐛 Docker Issues & Solutions

### Common Docker Build Problems

#### 1. Repository Access Issues (403 Forbidden)

**Problem**: `403  Forbidden [IP: 199.232.46.132 80]`

**Solutions**:

```bash
# Try different Dockerfile variants
docker-compose -f docker-compose.yml up --build  # Uses Dockerfile.simple
# OR
docker build -f server/Dockerfile.offline server/  # Offline build
```

#### 2. Network/Firewall Restrictions

**Problem**: Cannot reach Debian/Ubuntu repositories

**Solution**: Use the offline Dockerfile:

```bash
# Update docker-compose.yml to use offline Dockerfile
services:
  server:
    build:
      context: ./server
      dockerfile: Dockerfile.offline
```

#### 3. Corporate Network Issues

**Problem**: Corporate firewall blocking Docker Hub or repositories

**Solutions**:

- Use local development setup (`./run-local.sh`)
- Configure Docker proxy settings
- Use internal Docker registry if available

## 🔧 Production Deployment Options

### 1. Traditional Server Deployment

#### On Ubuntu/Debian Server

```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv nodejs npm nginx

# Setup Python virtual environment
cd server
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build React client
cd ../client
npm install
npm run build

# Configure Nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/nova-it
sudo ln -s /etc/nginx/sites-available/nova-it /etc/nginx/sites-enabled/
sudo systemctl reload nginx

# Start services
cd ../server
uvicorn src.document_processor.api:app --host 127.0.0.1 --port 8050
```

### 2. Docker with Pre-built Images

If you can build images offline:

```bash
# Build images offline
docker build -t nova-it-server:latest -f server/Dockerfile.offline server/
docker build -t nova-it-client:latest client/

# Run with pre-built images
docker run -d -p 8050:8000 --name nova-server nova-it-server:latest
docker run -d -p 3050:80 --name nova-client nova-it-client:latest
```

### 3. Cloud Deployment

#### AWS ECS/Fargate

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t nova-it-server -f server/Dockerfile.offline server/
docker tag nova-it-server:latest <account>.dkr.ecr.us-east-1.amazonaws.com/nova-it-server:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/nova-it-server:latest
```

#### Google Cloud Run

```bash
# Deploy to Cloud Run
gcloud run deploy nova-it-server \
  --source ./server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🧪 Testing Your Deployment

### Health Checks

```bash
# Test server health
curl http://localhost:8050/health

# Test client
curl http://localhost:3050/health

# Test document processing
curl -X POST "http://localhost:8050/process" \
  -F "file=@dataset/Canada.jpg"
```

### Load Testing

```bash
# Install Apache Bench (if available)
sudo apt-get install apache2-utils

# Test API performance
ab -n 100 -c 10 http://localhost:8050/health

# Test file upload
ab -n 10 -c 2 -p dataset/Canada.jpg -T image/jpeg http://localhost:8050/process
```

## 🛠️ Troubleshooting

### Server Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep -E "(fastapi|uvicorn|opencv)"

# Check port availability
lsof -i :8050
```

### Client Won't Start

```bash
# Check Node version
node --version  # Should be 14+
npm --version

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check port availability
lsof -i :3050
```

### Performance Issues

```bash
# Monitor resource usage
htop
docker stats  # If using Docker

# Check logs
tail -f server/logs/app.log
journalctl -u nova-it-server  # If using systemd
```

## 🔒 Security Considerations

### Production Security

- Use HTTPS/TLS certificates
- Configure proper firewall rules
- Set up authentication if required
- Regular security updates
- Monitor logs for suspicious activity

### Network Security

```bash
# Recommended firewall rules
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw deny 8050   # Block direct API access
sudo ufw deny 3050   # Block direct client access
```

## 📈 Monitoring & Logging

### Application Monitoring

```bash
# Setup log rotation
sudo logrotate -d /etc/logrotate.d/nova-it

# Monitor with systemd
sudo systemctl status nova-it-server
sudo systemctl status nova-it-client
```

### Performance Metrics

- Response times: <100ms for document processing
- Memory usage: <1GB per container
- CPU usage: <50% under normal load
- Disk usage: Monitor processed images storage
