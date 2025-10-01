# Movie Recap Pipeline - System Architecture

## System Overview

This is a multi-tenant, scalable backend system that automates the creation of long-form recap videos from user-supplied source movies/series and scripts. The system integrates multiple components for a complete media processing pipeline.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   Mobile App    │    │   Admin Panel   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Load Balancer  │
                    │   (nginx/ALB)   │
                    └─────────┬───────┘
                              │
                 ┌─────────────────────┐
                 │   FastAPI Backend   │
                 │  (Multiple Pods)    │
                 │                     │
                 │ • Authentication    │
                 │ • Upload Management │
                 │ • Job Orchestration │
                 │ • User Management   │
                 │ • Quota Enforcement │
                 └─────────┬───────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
┌────────▼──────┐ ┌────────▼──────┐ ┌────────▼──────┐
│   PostgreSQL  │ │     Redis     │ │   n8n Server  │
│   Database    │ │  (Job Queue)  │ │ (Orchestrator)│
│               │ │               │ │               │
│ • Users       │ │ • Celery Jobs │ │ • Workflows   │
│ • Projects    │ │ • Session     │ │ • Triggers    │
│ • Jobs        │ │ • Cache       │ │ • Monitoring  │
│ • Assets      │ │               │ │               │
└───────────────┘ └───────────────┘ └───────┬───────┘
                                           │
         ┌─────────────────────────────────┼───────────────────┐
         │                                 │                   │
┌────────▼──────┐                 ┌────────▼──────┐   ┌────────▼──────┐
│ Celery Workers│                 │ Google Drive  │   │ Google Colab  │
│ (Async Tasks) │                 │   Storage     │   │ (GPU Compute) │
│               │                 │               │   │               │
│ • Preprocessing│◄──────────────▲│ • Input Files │◄──┤ • Real-ESRGAN │
│ • Scene Detect│               ││ • Intermediate│   │ • 4K Upscaling│
│ • Transcription│               ││ • Outputs     │   │ • Chunked Proc│
│ • Script Parse│               ││               │   │ • Checkpointing│
│ • Alignment   │               │└───────────────┘   └───────────────┘
│ • Edit Assembly│               │
│ • Post Process│               │
└─────────┬─────┘               │
          │                     │
          └─────────────────────┘

External Services:
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Monitoring    │ │    Logging      │ │   Alerting      │
│                 │ │                 │ │                 │
│ • Prometheus    │ │ • Grafana       │ │ • Sentry        │
│ • Health Checks │ │ • ELK Stack     │ │ • Email/Slack   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Component Details

### 1. FastAPI Backend (API Layer)
- **Purpose**: Main application server handling HTTP requests
- **Responsibilities**:
  - User authentication & authorization (JWT)
  - Upload management with chunked/resumable uploads
  - Job creation and status tracking
  - Quota enforcement and rate limiting
  - Content moderation and compliance
- **Scaling**: Horizontal scaling with multiple pods/instances
- **Tech**: FastAPI, Python 3.11+, Pydantic, SQLAlchemy

### 2. PostgreSQL Database
- **Purpose**: Primary data store for structured data
- **Schema**: Multi-tenant with proper isolation
- **Features**: JSONB for flexible metadata, full-text search
- **Backup**: Automated backups with point-in-time recovery

### 3. Redis (Caching & Queue)
- **Purpose**: Job queue, session storage, and caching
- **Use Cases**:
  - Celery job queue and result backend
  - User session storage
  - API response caching
  - Rate limiting counters

### 4. Celery Workers (Processing Layer)
- **Purpose**: Asynchronous task processing
- **Worker Types**:
  - **Preprocessing Workers**: Media analysis, scene detection
  - **Transcription Workers**: Speech-to-text processing
  - **Alignment Workers**: Script-to-video matching
  - **Assembly Workers**: Video editing and compilation
- **Scaling**: Auto-scaling based on queue depth

### 5. n8n Orchestration
- **Purpose**: Workflow automation and external service coordination
- **Functions**:
  - Google Drive monitoring
  - Colab job triggering
  - Multi-step pipeline coordination
  - External notifications

### 6. Google Drive Storage
- **Purpose**: User-facing file storage and transfer
- **Structure**:
  ```
  /movie-recap-pipeline/
  ├── inputs/{user_id}/{project_id}/
  ├── intermediate/{job_id}/
  ├── upscale_inputs/{job_id}/
  ├── upscale_outputs/{job_id}/
  └── outputs/{job_id}/
  ```

### 7. Google Colab (GPU Processing)
- **Purpose**: GPU-accelerated 4K upscaling
- **Features**:
  - Real-ESRGAN implementation
  - Chunked processing for memory efficiency
  - Checkpointing for resume capability
  - Drive integration for I/O

## Data Flow

### Upload Process
1. User initiates upload through web client
2. Backend generates signed upload URL
3. Client uploads directly to Google Drive
4. n8n detects new file and triggers backend
5. Backend validates file and creates job
6. Processing pipeline begins

### Processing Pipeline
1. **Preprocessing**: Extract metadata, create preview
2. **Scene Detection**: Identify cuts and transitions
3. **Transcription**: Convert audio to text with timestamps
4. **Script Parsing**: Extract scenes from user scripts
5. **Alignment**: Match script scenes to video segments
6. **Moderation**: Check for copyright/watermark issues
7. **Assembly**: Edit and compile matched segments
8. **Upscaling** (optional): 4K enhancement via Colab
9. **Finalization**: Add intro/outro, generate thumbnails
10. **Delivery**: Save to outputs, notify user

## Security Architecture

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Multi-tenant isolation at database level
- API rate limiting and quota enforcement

### Content Security
- Automated watermark/logo detection
- Copyright compliance workflow
- User consent and legal documentation
- Content moderation queue

### Data Protection
- Encryption at rest and in transit
- Secure file handling with virus scanning
- Privacy-compliant logging
- GDPR/CCPA compliance features

## Scalability Design

### Horizontal Scaling
- Stateless API servers behind load balancer
- Worker pools that auto-scale based on demand
- Database read replicas for query scaling
- CDN for static content delivery

### Performance Optimization
- Async processing for long-running tasks
- Intelligent caching strategies
- Database query optimization
- Media processing optimization

### Resource Management
- Per-tenant quotas and limits
- Cost controls and usage monitoring
- Graceful degradation under load
- Circuit breakers for external services

## Compliance & Legal

### Copyright Protection
- No watermark removal capabilities
- Mandatory moderation for copyrighted content
- User education on fair use
- Legal compliance audit trail

### Data Governance
- User data retention policies
- Right to deletion (GDPR Article 17)
- Data portability features
- Privacy impact assessments

## Monitoring & Observability

### Health Monitoring
- Application health checks
- Database connection monitoring
- External service availability
- Resource utilization tracking

### Performance Metrics
- API response times
- Job processing times
- Queue depths and throughput
- Error rates and patterns

### Business Metrics
- User engagement
- Processing success rates
- Cost per job
- Revenue attribution

## Disaster Recovery

### Backup Strategy
- Database: Automated daily backups with point-in-time recovery
- Storage: Google Drive inherent redundancy + periodic exports
- Configuration: Infrastructure as Code (Terraform)

### Failure Scenarios
- Single server failure: Load balancer routes to healthy instances
- Database failure: Automated failover to standby
- Storage failure: Google Drive redundancy + backup exports
- Regional failure: Multi-region deployment capability

## Cost Management

### Resource Optimization
- Right-sized compute instances
- Spot instances for batch processing
- Storage lifecycle policies
- Compression and deduplication

### Usage Controls
- Per-user quotas and limits
- Job prioritization queues
- Auto-scaling policies
- Cost alerting and reporting