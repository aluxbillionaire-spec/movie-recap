# Movie Recap Service - Complete Installation Guide

This guide will help you install and set up the Movie Recap Service on your system, solving all problems and installing all required tools.

## 🚀 Quick Start (Recommended)

### Option 1: Automated Installation
```bash
# Run the comprehensive setup script
python setup.py

# Or use the quick start script
python quickstart.py
```

### Option 2: Docker Installation (Easiest)
```bash
# Start all services with Docker
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🔧 Manual Installation

### Step 1: Prerequisites

#### Python 3.11+
**Windows:**
```bash
# Download from python.org or use winget
winget install Python.Python.3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

**macOS:**
```bash
brew install python@3.11
```

#### Git
**Windows:**
```bash
winget install Git.Git
```

**Linux:**
```bash
sudo apt install git
```

**macOS:**
```bash
brew install git
```

### Step 2: Database (PostgreSQL)

#### Windows
```bash
# Using winget
winget install PostgreSQL.PostgreSQL

# Or download from: https://www.postgresql.org/download/windows/
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql postgresql-server
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

### Step 3: Redis Cache

#### Windows
```bash
# Download from: https://github.com/microsoftarchive/redis/releases
# Or use Windows Subsystem for Linux (WSL)
```

#### Linux
```bash
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS
```bash
brew install redis
brew services start redis
```

### Step 4: Docker & Docker Compose

#### Windows
```bash
# Download Docker Desktop from: https://www.docker.com/products/docker-desktop
```

#### Linux
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### macOS
```bash
# Download Docker Desktop from: https://www.docker.com/products/docker-desktop
```

### Step 5: FFmpeg (Video Processing)

#### Windows
```bash
# Using winget
winget install Gyan.FFmpeg

# Or using Chocolatey
choco install ffmpeg
```

#### Linux
```bash
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

## 📦 Project Setup

### 1. Clone and Setup Environment
```bash
# Navigate to project directory
cd "movie practise"

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Create environment file
cp .env.example .env
```

### 2. Install Python Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install main dependencies
pip install -r backend/requirements.txt

# Install test dependencies
pip install -r requirements-test.txt
```

### 3. Configure Environment
Edit the `.env` file with your settings:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/movie_recap
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Google Services (optional for basic setup)
GOOGLE_DRIVE_CREDENTIALS_PATH=path/to/google/credentials.json

# Development settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### 4. Database Setup
```bash
# Create databases
createdb movie_recap
createdb test_movie_recap

# Run migrations (if available)
cd backend
alembic upgrade head
cd ..
```

## 🚀 Running the Application

### Option 1: Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View API documentation
# Open: http://localhost:8000/docs
```

### Option 2: Manual Start
```bash
# Start database services
# PostgreSQL and Redis should be running

# Start the FastAPI application
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A app.core.celery worker --loglevel=info
```

### Option 3: Development Scripts
```bash
# Windows
start_dev.bat

# Linux/macOS
./start_dev.sh
```

## 🧪 Testing Installation

### 1. Run Basic Tests
```bash
# Run all tests
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit
python run_tests.py --integration
```

### 2. Verify Services
```bash
# Check if services are responding
curl http://localhost:8000/health
curl http://localhost:8000/docs

# Check database connection
python -c "
import asyncio
from backend.app.core.database import engine
async def test_db():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('Database OK:', result.fetchone())
asyncio.run(test_db())
"
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Python Version Issues
**Problem:** `Python 3.11+ required`
**Solution:**
```bash
# Check current version
python --version

# Install Python 3.11+
# Windows: winget install Python.Python.3.11
# Linux: sudo apt install python3.11
# macOS: brew install python@3.11
```

#### 2. Database Connection Issues
**Problem:** `Could not connect to database`
**Solutions:**
```bash
# Check if PostgreSQL is running
# Windows: net start postgresql-x64-14
# Linux: sudo systemctl status postgresql
# macOS: brew services list | grep postgresql

# Create database manually
createdb movie_recap

# Check connection
psql -h localhost -U postgres -d movie_recap
```

#### 3. Redis Connection Issues
**Problem:** `Redis connection failed`
**Solutions:**
```bash
# Check if Redis is running
# Windows: Check Task Manager or use Docker
# Linux: sudo systemctl status redis-server
# macOS: brew services list | grep redis

# Test connection
redis-cli ping
```

#### 4. Import Errors
**Problem:** `ModuleNotFoundError: No module named 'app'`
**Solutions:**
```bash
# Ensure you're in the correct directory
cd backend

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/project/backend"

# Or use relative imports and run from project root
python -m backend.app.main
```

#### 5. Port Already in Use
**Problem:** `Port 8000 already in use`
**Solutions:**
```bash
# Find process using port
# Windows: netstat -ano | findstr :8000
# Linux/macOS: lsof -i :8000

# Kill process or use different port
uvicorn app.main:app --port 8001
```

#### 6. FFmpeg Not Found
**Problem:** `FFmpeg not found in PATH`
**Solutions:**
```bash
# Install FFmpeg
# Windows: winget install Gyan.FFmpeg
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg

# Verify installation
ffmpeg -version
```

### Docker-Specific Issues

#### 1. Docker Not Starting
```bash
# Restart Docker service
# Windows: Restart Docker Desktop
# Linux: sudo systemctl restart docker
# macOS: Restart Docker Desktop

# Check Docker status
docker --version
docker-compose --version
```

#### 2. Container Build Failures
```bash
# Clean Docker cache
docker system prune -a

# Rebuild containers
docker-compose build --no-cache

# Check container logs
docker-compose logs backend
```

#### 3. Database Container Issues
```bash
# Reset database volume
docker-compose down -v
docker-compose up -d postgres

# Check database logs
docker-compose logs postgres
```

## 🎯 Verification Checklist

After installation, verify these components work:

- [ ] **Python 3.11+** - `python --version`
- [ ] **PostgreSQL** - `psql --version` and connection test
- [ ] **Redis** - `redis-cli ping`
- [ ] **Docker** - `docker --version` and `docker-compose --version`
- [ ] **FFmpeg** - `ffmpeg -version`
- [ ] **Dependencies** - `pip list | grep fastapi`
- [ ] **Database** - Can connect to `movie_recap` database
- [ ] **Application** - `http://localhost:8000/health` returns 200
- [ ] **API Docs** - `http://localhost:8000/docs` loads
- [ ] **Tests** - `python run_tests.py --unit` passes

## 🚀 Next Steps

Once installation is complete:

1. **Configure Google Services** (optional):
   - Set up Google Drive API credentials
   - Configure Google Colab notebook access

2. **Production Setup**:
   - Update `.env` with production settings
   - Set up proper SSL certificates
   - Configure monitoring and logging

3. **Development**:
   - Explore API documentation at `/docs`
   - Run tests to ensure everything works
   - Start building your movie recap workflows

## 📞 Getting Help

If you encounter issues not covered here:

1. **Check Logs**: Look in `./logs/` directory for error details
2. **Run Diagnostics**: `python setup.py` includes diagnostic checks
3. **Test Individual Components**: Use the troubleshooting commands above
4. **Docker Fallback**: Use `docker-compose up` if manual setup fails

For additional support, refer to:
- **API Documentation**: `http://localhost:8000/docs`
- **Project README**: `README.md`
- **Test Results**: `python run_tests.py --all`

---

**🎬 Happy movie recap processing!**