# Movie Recap Service - Complete Multi-Tenant Backend System

A production-ready, scalable backend system for automated movie recap video generation with multi-tenant architecture, comprehensive security, and ethical copyright protection.

## 🏗️ Architecture Overview

This system implements a microservices architecture with:

- **FastAPI Backend**: Modern async Python web framework
- **PostgreSQL Database**: Multi-tenant with row-level security
- **Celery Workers**: Distributed async task processing
- **Redis**: Caching, sessions, and job queues
- **Google Drive**: Cloud storage integration
- **Google Colab**: GPU-accelerated video upscaling
- **n8n Workflows**: Orchestration and automation
- **Docker**: Containerized deployment
- **Prometheus/Grafana**: Monitoring and metrics

## 🔧 Key Features

### Multi-Tenant Architecture
- Complete tenant isolation with row-level security
- Per-tenant rate limiting and quotas
- Tenant-specific configuration and settings

### Security & Authentication
- JWT-based authentication with refresh tokens
- Password policies and secure hashing
- Rate limiting and DDoS protection
- Input validation and sanitization

### Video Processing Pipeline
- FFmpeg-based video processing
- Real-ESRGAN 4K upscaling via Google Colab
- Script-to-video alignment using semantic analysis
- Automated video assembly and editing

### Copyright Protection
- Watermark detection (NO removal capabilities)
- Copyright indicator analysis
- Content moderation and compliance
- Ethical AI practices enforcement

### Monitoring & Observability
- Comprehensive metrics collection
- Health checks and alerting
- Structured logging with correlation IDs
- Performance monitoring

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose
- FFmpeg
- Google Cloud Account (for Drive API)
- Google Colab Pro (for GPU processing)

### Installation

1. **Clone and Setup**
```bash
git clone <repository-url>
cd movie-recap-service
cp .env.example .env
```

2. **Configure Environment**
Edit `.env` file with your configuration:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/movie_recap
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Google Services
GOOGLE_DRIVE_CREDENTIALS_PATH=/path/to/credentials.json
GOOGLE_COLAB_NOTEBOOK_URL=your-colab-notebook-url

# Rate Limiting
DEFAULT_RATE_LIMIT_REQUESTS=1000
DEFAULT_RATE_LIMIT_WINDOW=3600
```

3. **Install Dependencies**
```bash
pip install -r backend/requirements.txt
pip install -r requirements-test.txt
```

4. **Database Setup**
```bash
cd backend
alembic upgrade head
```

5. **Start Services**
```bash
# Development
docker-compose up -d postgres redis
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
docker-compose up -d
```

### Development Workflow

1. **Run Tests**
```bash
python run_tests.py --all
```

2. **Code Quality**
```bash
black backend/app/
isort backend/app/
flake8 backend/app/
mypy backend/app/
```

3. **Load Testing**
```bash
locust -f tests/load_test.py --host=http://localhost:8000
```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json
X-Tenant-ID: your-tenant-id

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json
X-Tenant-ID: your-tenant-id

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

### Project Management

#### Create Project
```http
POST /api/v1/projects
Authorization: Bearer <token>
X-Tenant-ID: your-tenant-id

{
  "name": "My Movie Recap",
  "description": "Action movie recap project",
  "settings": {
    "target_resolution": "4K",
    "quality": "high",
    "enable_watermark": true
  }
}
```

### File Upload

#### Upload Video
```http
POST /api/v1/uploads/video
Authorization: Bearer <token>
X-Tenant-ID: your-tenant-id
Content-Type: multipart/form-data

file: <video-file>
project_id: <project-id>
```

#### Upload Script
```http
POST /api/v1/uploads/script
Authorization: Bearer <token>
X-Tenant-ID: your-tenant-id
Content-Type: multipart/form-data

file: <script-file>
project_id: <project-id>
```

### Job Management

#### Create Processing Job
```http
POST /api/v1/jobs
Authorization: Bearer <token>
X-Tenant-ID: your-tenant-id

{
  "project_id": "project-id",
  "type": "video_processing",
  "settings": {
    "target_resolution": "4K",
    "quality": "high",
    "priority": "normal"
  }
}
```

#### Check Job Status
```http
GET /api/v1/jobs/{job_id}
Authorization: Bearer <token>
X-Tenant-ID: your-tenant-id
```

## 🔄 Processing Pipeline

1. **Video Upload**: User uploads video file to Google Drive
2. **Script Upload**: User uploads script file (txt, pdf, docx)
3. **Content Moderation**: Automatic copyright and watermark detection
4. **Video Processing**: FFmpeg-based video analysis and processing
5. **Script Extraction**: Text extraction from various file formats
6. **Semantic Alignment**: AI-powered script-to-video alignment
7. **Video Assembly**: Automated editing and compilation
8. **4K Upscaling**: GPU-accelerated upscaling via Google Colab
9. **Final Output**: Delivery of processed video to user

## 🛡️ Security Features

### Authentication & Authorization
- JWT tokens with configurable expiry
- Refresh token rotation
- Password strength enforcement
- Account lockout after failed attempts

### Input Validation
- File type and size validation
- Content sanitization
- SQL injection prevention
- XSS protection

### Rate Limiting
- Per-tenant rate limits
- Burst handling
- Gradual backoff
- DDoS protection

### Data Protection
- Encryption at rest and in transit
- Secure file handling
- PII data protection
- GDPR compliance features

## 📊 Monitoring & Metrics

### Application Metrics
- Request/response times
- Error rates and types
- Database query performance
- Job processing statistics

### Business Metrics
- User activity tracking
- Content processing volumes
- Storage usage per tenant
- API quota utilization

### System Metrics
- CPU and memory usage
- Disk I/O and storage
- Network traffic
- Container health

### Alerting
- Configurable alert rules
- Multiple notification channels
- Escalation policies
- Health check failures

## 🧪 Testing

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API and database integration
3. **Load Tests**: Performance and scalability
4. **Security Tests**: Vulnerability scanning
5. **End-to-End Tests**: Complete workflow validation

### Running Tests

```bash
# All tests
python run_tests.py --all

# Specific test categories
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --load

# Code quality checks
python run_tests.py --quality

# Coverage report
python run_tests.py --coverage
```

## 🚢 Deployment

### Development
```bash
docker-compose -f docker-compose.dev.yml up
```

### Staging
```bash
docker-compose -f docker-compose.staging.yml up
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

### CI/CD Pipeline

The system includes GitHub Actions workflows for:
- Automated testing on pull requests
- Security scanning and code quality checks
- Docker image building and pushing
- Deployment to staging and production
- Database migrations

## 🔧 Configuration

### Environment Variables

See `.env.example` for complete configuration options including:

- Database connections
- Redis configuration
- Security settings
- File upload limits
- Google service credentials
- Monitoring endpoints
- Rate limiting parameters

### Multi-Tenant Settings

Per-tenant configuration includes:
- Storage quotas
- Processing limits
- API rate limits
- Feature flags
- Custom branding
- Webhook endpoints

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests
- Update documentation
- Use conventional commit messages
- Ensure security best practices

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **API Reference**: `/docs` endpoint when running
- **Issues**: GitHub Issues
- **Security**: security@yourdomain.com

## 🔮 Roadmap

### Phase 1 (Current)
- ✅ Multi-tenant backend architecture
- ✅ Authentication and authorization
- ✅ File upload and processing
- ✅ Job management system
- ✅ Content moderation
- ✅ Monitoring and metrics

### Phase 2 (Next)
- [ ] Advanced AI features
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app API
- [ ] Advanced caching strategies

### Phase 3 (Future)
- [ ] Machine learning optimization
- [ ] Advanced video effects
- [ ] Collaborative editing
- [ ] Enterprise features
- [ ] Advanced integrations
- [ ] Global CDN deployment

---

**Built with ❤️ for ethical AI and copyright protection**