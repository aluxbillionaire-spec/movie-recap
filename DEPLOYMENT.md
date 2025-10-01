# Movie Recap Pipeline - Deployment Guide

This guide covers deployment of the Movie Recap Pipeline to various cloud providers and local development setup.

## Quick Start (Local Development)

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Git
- At least 8GB RAM
- 50GB available disk space

### Local Setup

1. **Clone Repository**
```bash
git clone <repository-url>
cd movie-recap-pipeline
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start Services**
```bash
docker-compose up -d
```

4. **Initialize Database**
```bash
docker-compose exec backend python -m alembic upgrade head
```

5. **Access Services**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- n8n: http://localhost:5678 (admin/password)
- Grafana: http://localhost:3000 (admin/grafana_admin_password)
- Flower: http://localhost:5555

## Cloud Deployment Options

### Option 1: DigitalOcean App Platform

**Estimated Cost**: $50-200/month depending on usage

1. **Create DigitalOcean Account and Install CLI**
```bash
# Install doctl
snap install doctl
# or: brew install doctl

# Authenticate
doctl auth init
```

2. **Create App Spec**
```yaml
# .do/app.yaml
name: movie-recap-pipeline
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-username/movie-recap-pipeline
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 2
  instance_size_slug: basic-xxs
  http_port: 8080
  health_check:
    http_path: /health
  envs:
  - key: DATABASE_URL
    scope: RUN_AND_BUILD_TIME
    type: SECRET
  - key: REDIS_URL
    scope: RUN_AND_BUILD_TIME
    type: SECRET

- name: worker
  source_dir: /backend
  run_command: celery -A app.workers.celery_app worker --loglevel=info
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xs

databases:
- name: postgres
  engine: PG
  version: "15"
  production: true
- name: redis
  engine: REDIS
  version: "7"
```

3. **Deploy**
```bash
doctl apps create --spec .do/app.yaml
```

### Option 2: Google Cloud Platform

**Estimated Cost**: $100-400/month

1. **Setup GCP Project**
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize and authenticate
gcloud init
gcloud auth login

# Create project
gcloud projects create movie-recap-pipeline-prod
gcloud config set project movie-recap-pipeline-prod

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

2. **Create GKE Cluster**
```bash
# Create cluster
gcloud container clusters create movie-recap-cluster \
    --zone=us-central1-a \
    --num-nodes=3 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=10 \
    --machine-type=e2-standard-2

# Get credentials
gcloud container clusters get-credentials movie-recap-cluster --zone=us-central1-a
```

3. **Create Cloud SQL Instance**
```bash
gcloud sql instances create movie-recap-db \
    --database-version=POSTGRES_15 \
    --tier=db-g1-small \
    --region=us-central1

gcloud sql databases create movierecap --instance=movie-recap-db
gcloud sql users create movierecap_user --instance=movie-recap-db --password=secure_password
```

4. **Deploy with Kubernetes**
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmaps.yaml
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/ingress.yaml
```

### Option 3: AWS ECS with Fargate

**Estimated Cost**: $75-300/month

1. **Setup AWS CLI and ECS CLI**
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Install ECS CLI
sudo curl -Lo /usr/local/bin/ecs-cli https://amazon-ecs-cli.s3.amazonaws.com/ecs-cli-linux-amd64-latest
sudo chmod +x /usr/local/bin/ecs-cli
```

2. **Create ECS Cluster**
```bash
# Create cluster
ecs-cli configure --cluster movie-recap-cluster --region us-east-1 --default-launch-type FARGATE --config-name movie-recap

# Create cluster with VPC
ecs-cli up --cluster-config movie-recap --ecs-profile default
```

3. **Deploy Services**
```bash
# Deploy using docker-compose-aws.yml
ecs-cli compose --project-name movie-recap service up --cluster-config movie-recap --ecs-profile default
```

## Production Configuration

### Environment Variables

Create `.env` file with production values:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://host:6379/0
CELERY_BROKER_URL=redis://host:6379/1
CELERY_RESULT_BACKEND=redis://host:6379/2

# Security
SECRET_KEY=your-super-secure-secret-key-256-bits
DEBUG=false
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
ALLOWED_ORIGINS=https://your-domain.com,https://app.your-domain.com

# Google Drive
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials/google-drive-service-account.json

# Monitoring
SENTRY_DSN=https://your-sentry-dsn.ingest.sentry.io/project-id
PROMETHEUS_ENABLED=true

# Email
EMAIL_ENABLED=true
SMTP_HOST=smtp.sendgrid.net
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

### SSL/TLS Configuration

1. **Using Let's Encrypt with Certbot**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Auto-renewal crontab
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

2. **Nginx Configuration**
```nginx
# /etc/nginx/sites-available/movie-recap
server {
    listen 443 ssl http2;
    server_name api.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Database Optimization

```sql
-- Production PostgreSQL optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
```

## Monitoring Setup

### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'movie-recap-api'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: /metrics

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Grafana Dashboards

Import the provided dashboards:
- `monitoring/grafana/dashboards/api-performance.json`
- `monitoring/grafana/dashboards/job-processing.json`
- `monitoring/grafana/dashboards/system-resources.json`

## Backup and Disaster Recovery

### Database Backups
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/movierecap_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U movierecap_user movierecap > $BACKUP_FILE
gzip $BACKUP_FILE

# Upload to cloud storage
aws s3 cp $BACKUP_FILE.gz s3://your-backup-bucket/postgres/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### Redis Persistence
```bash
# redis.conf additions
save 900 1
save 300 10
save 60 10000
rdbcompression yes
rdbchecksum yes
```

## Performance Tuning

### Backend Scaling
```bash
# Scale backend instances
docker-compose up --scale backend=3

# Or with Kubernetes
kubectl scale deployment backend --replicas=3
```

### Worker Optimization
```bash
# Scale workers by queue type
docker-compose up --scale worker-preprocessing=2 --scale worker-transcription=3
```

### Database Connection Pooling
```python
# app/core/config.py
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 30
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 3600
```

## Cost Optimization

### 1. Use Spot Instances (AWS/GCP)
```bash
# AWS ECS with Spot instances
--capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=100
```

### 2. Auto-scaling Configuration
```yaml
# HPA for Kubernetes
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 3. Storage Lifecycle Policies
```bash
# AWS S3 lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
    --bucket movie-recap-storage \
    --lifecycle-configuration file://lifecycle-policy.json
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check database connectivity
docker-compose exec backend python -c "
from app.core.database import engine
import asyncio
asyncio.run(engine.dispose())
print('Database connection OK')
"
```

2. **Celery Worker Issues**
```bash
# Check worker status
docker-compose exec worker-preprocessing celery -A app.workers.celery_app inspect active
```

3. **Memory Issues**
```bash
# Monitor memory usage
docker stats
# Adjust worker concurrency
celery -A app.workers.celery_app worker --concurrency=1
```

### Log Analysis
```bash
# Centralized logging with ELK stack
docker-compose -f docker-compose.logging.yml up -d

# View aggregated logs
docker-compose logs -f backend worker-preprocessing
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable SSL/TLS for all services
- [ ] Configure firewall rules
- [ ] Set up database SSL connections
- [ ] Enable audit logging
- [ ] Configure rate limiting
- [ ] Set up intrusion detection
- [ ] Regular security scans
- [ ] Backup encryption
- [ ] Access key rotation

## Maintenance

### Regular Tasks
- Database vacuum and analyze (weekly)
- Log rotation and cleanup (daily)
- Security updates (monthly)
- Backup verification (weekly)
- Performance monitoring review (weekly)

### Update Procedure
1. Test updates in staging environment
2. Schedule maintenance window
3. Create database backup
4. Deploy updates with zero-downtime strategy
5. Monitor for issues
6. Rollback plan if needed

## Support

For deployment issues or questions:
- Check the troubleshooting section
- Review application logs
- Contact: support@movierecap.com
- Documentation: https://docs.movierecap.com