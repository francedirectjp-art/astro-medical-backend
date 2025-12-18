# Production Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Platform Deployment](#cloud-platform-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database & Storage](#database--storage)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security Considerations](#security-considerations)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Backend Server:**
- CPU: 2+ cores recommended
- RAM: 4GB minimum, 8GB recommended
- Storage: 10GB minimum
- OS: Linux (Ubuntu 20.04+ recommended)

**Frontend Server:**
- CPU: 1+ core
- RAM: 2GB minimum
- Storage: 5GB minimum

### Software Requirements

- Docker 24.0+ & Docker Compose 2.0+
- Python 3.11+ (if not using Docker)
- Node.js 18+ (for frontend)
- Git
- Nginx or similar reverse proxy (for production)

### API Keys Required

- OpenAI API Key (GPT-4o) OR Google Gemini API Key
- Get OpenAI key: https://platform.openai.com/api-keys
- Get Gemini key: https://makersuite.google.com/app/apikey

---

## Deployment Options

### Option 1: Docker Compose (Recommended)

Best for:
- Quick deployment
- Development & staging environments
- Small to medium scale production

### Option 2: Kubernetes

Best for:
- Large scale production
- High availability requirements
- Auto-scaling needs

### Option 3: Cloud Platform (PaaS)

Best for:
- Managed infrastructure
- Quick deployment
- Reduced operational overhead

Supported platforms:
- AWS (ECS, Elastic Beanstalk)
- Google Cloud (Cloud Run, GKE)
- Azure (Container Apps, AKS)
- Heroku
- Railway
- Render

---

## Docker Deployment

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/anti-gravity.git
cd anti-gravity
```

### Step 2: Configure Environment

Copy and edit environment files:

```bash
# Backend environment
cp .env.example .env
nano .env
```

Required variables in `.env`:
```bash
# AI API Keys (at least one required)
OPENAI_API_KEY=sk-...your-key...
# OR
GOOGLE_API_KEY=...your-key...

# API Configuration
AI_MODEL=gpt-4o
LOG_LEVEL=info
WORKERS=4

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com

# Japanese Font Path (Docker default)
JAPANESE_FONT_PATH=/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttf
```

Frontend environment (optional, for custom build):
```bash
# Frontend .env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Step 3: Build Images

```bash
# Build backend
docker build -t anti-gravity-backend:latest -f Dockerfile .

# Build frontend
docker build -t anti-gravity-frontend:latest -f frontend/Dockerfile ./frontend
```

### Step 4: Deploy with Docker Compose

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Test API
curl -X POST http://localhost:8000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "テスト太郎",
    "birth_date": "1990-05-15",
    "birth_time": "14:30",
    "prefecture": "東京都",
    "city": "渋谷区"
  }'
```

### Step 6: Setup Reverse Proxy (Nginx)

Install Nginx:
```bash
sudo apt-get install nginx
```

Create Nginx configuration (`/etc/nginx/sites-available/anti-gravity`):
```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Increase timeout for long AI generation
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/anti-gravity /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Setup SSL (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificates
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Cloud Platform Deployment

### AWS (Elastic Container Service)

#### 1. Push Images to ECR

```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Tag and push backend
docker tag anti-gravity-backend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/anti-gravity-backend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/anti-gravity-backend:latest

# Tag and push frontend
docker tag anti-gravity-frontend:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/anti-gravity-frontend:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/anti-gravity-frontend:latest
```

#### 2. Create ECS Task Definition

See `aws-ecs-task-definition.json` (example provided in repository)

#### 3. Deploy to ECS

```bash
aws ecs create-service \
  --cluster anti-gravity-cluster \
  --service-name anti-gravity-backend \
  --task-definition anti-gravity-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Google Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/anti-gravity-backend

# Deploy backend
gcloud run deploy anti-gravity-backend \
  --image gcr.io/YOUR_PROJECT/anti-gravity-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY,AI_MODEL=gpt-4o \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300s \
  --max-instances 10

# Deploy frontend
gcloud run deploy anti-gravity-frontend \
  --image gcr.io/YOUR_PROJECT/anti-gravity-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=https://anti-gravity-backend-xxx.run.app
```

### Heroku

```bash
# Login to Heroku
heroku login

# Create apps
heroku create anti-gravity-backend
heroku create anti-gravity-frontend

# Set environment variables
heroku config:set OPENAI_API_KEY=your-key --app anti-gravity-backend
heroku config:set AI_MODEL=gpt-4o --app anti-gravity-backend

# Deploy backend
heroku container:login
docker tag anti-gravity-backend:latest registry.heroku.com/anti-gravity-backend/web
docker push registry.heroku.com/anti-gravity-backend/web
heroku container:release web --app anti-gravity-backend

# Deploy frontend
heroku config:set NEXT_PUBLIC_API_URL=https://anti-gravity-backend.herokuapp.com --app anti-gravity-frontend
cd frontend
git push heroku main
```

---

## Environment Configuration

See `ENV_CONFIG.md` for detailed environment variable documentation.

### Critical Environment Variables

**Backend:**
```bash
OPENAI_API_KEY=sk-...           # Required for AI generation
AI_MODEL=gpt-4o                 # gpt-4o or gemini-pro
LOG_LEVEL=info                  # debug, info, warning, error
WORKERS=4                       # Number of worker processes
SESSION_TIMEOUT=3600            # Session timeout in seconds
CORS_ORIGINS=https://yourdomain.com  # Allowed origins
```

**Frontend:**
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com  # Backend API URL
```

### Secrets Management

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name anti-gravity/openai-key \
  --secret-string "sk-your-key-here"
```

**Google Secret Manager:**
```bash
echo -n "sk-your-key-here" | gcloud secrets create openai-api-key --data-file=-
```

---

## Database & Storage

### Session Storage

Current implementation uses **in-memory storage** (development only).

For production, implement persistent storage:

#### Option 1: Redis (Recommended)

```python
# requirements.txt
redis==5.0.0

# session_store.py
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def save_session(session_id: str, data: dict):
    redis_client.setex(
        f"session:{session_id}",
        3600,  # TTL
        json.dumps(data)
    )

def get_session(session_id: str):
    data = redis_client.get(f"session:{session_id}")
    return json.loads(data) if data else None
```

#### Option 2: PostgreSQL

```python
# requirements.txt
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# models.py
from sqlalchemy import create_engine, Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = 'sessions'
    
    session_id = Column(String, primary_key=True)
    birth_data = Column(JSON)
    chart_data = Column(JSON)
    generated_content = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

### PDF Storage

For production, store PDFs in cloud storage:

#### AWS S3

```python
import boto3

s3_client = boto3.client('s3')

def upload_pdf_to_s3(pdf_buffer, session_id):
    key = f"pdfs/{session_id}.pdf"
    s3_client.put_object(
        Bucket='anti-gravity-pdfs',
        Key=key,
        Body=pdf_buffer,
        ContentType='application/pdf'
    )
    return f"https://anti-gravity-pdfs.s3.amazonaws.com/{key}"
```

#### Google Cloud Storage

```python
from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.bucket('anti-gravity-pdfs')

def upload_pdf_to_gcs(pdf_buffer, session_id):
    blob = bucket.blob(f"pdfs/{session_id}.pdf")
    blob.upload_from_file(pdf_buffer, content_type='application/pdf')
    return blob.public_url
```

---

## Monitoring & Logging

### Application Logging

Configure structured logging in production:

```python
# logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Use in api_server.py
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### Health Monitoring

Implement comprehensive health checks:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": await check_db_health(),
            "ai_service": await check_ai_health(),
            "storage": await check_storage_health(),
        }
    }
```

### Prometheus Metrics

```bash
# requirements.txt
prometheus-client==0.19.0

# metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')
active_sessions = Gauge('active_sessions', 'Number of active sessions')
```

### Grafana Dashboard

Create dashboard with:
- Request rate & latency
- Error rate
- Active sessions
- AI generation time
- PDF generation time
- System resources (CPU, memory)

---

## Security Considerations

### 1. API Key Security

- Never commit keys to repository
- Use environment variables or secrets management
- Rotate keys regularly
- Use different keys for dev/prod

### 2. CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

```bash
# requirements.txt
slowapi==0.1.9

# rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/session/create")
@limiter.limit("10/minute")
async def create_session(...):
    ...
```

### 4. Input Validation

Already implemented with Pydantic models. Ensure all user inputs are validated.

### 5. HTTPS Only

In production, enforce HTTPS:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 6. Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# Add security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## Performance Optimization

### 1. Caching

Implement Redis caching for static content:

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)

async def get_master_content_cached():
    cache_key = "master_content"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    with open("anti_gravity_master_content.json") as f:
        data = json.load(f)
    
    redis_client.setex(cache_key, 3600, json.dumps(data))
    return data
```

### 2. Database Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
)
```

### 3. Async AI Generation

Already implemented with async/await patterns.

### 4. CDN for Frontend

Use CDN for static assets:
- CloudFlare
- AWS CloudFront
- Google Cloud CDN
- Azure CDN

### 5. Load Balancing

For high traffic, use load balancer:

**Nginx Load Balancer:**
```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

### 6. PDF Generation Optimization

- Pre-generate common sections
- Use PDF caching for identical requests
- Optimize font loading
- Compress images

---

## Troubleshooting

### Common Issues

#### 1. AI Generation Fails

**Symptoms:**
```
ai_generator: False
```

**Solution:**
- Check API key: `echo $OPENAI_API_KEY`
- Verify key validity
- Check rate limits
- Review logs: `docker-compose logs backend`

#### 2. PDF Generation Error

**Symptoms:**
```
Error: Font not found
```

**Solution:**
```bash
# Install fonts
docker exec -it backend bash
apt-get update && apt-get install fonts-noto-cjk
```

#### 3. CORS Errors

**Symptoms:**
```
Access-Control-Allow-Origin error
```

**Solution:**
- Add frontend URL to CORS_ORIGINS
- Restart backend
- Check Nginx configuration

#### 4. Session Timeout

**Symptoms:**
```
Session not found
```

**Solution:**
- Increase SESSION_TIMEOUT
- Implement Redis session storage
- Check system time synchronization

#### 5. High Memory Usage

**Symptoms:**
- OOM errors
- Slow response times

**Solution:**
- Increase container memory limits
- Implement session cleanup
- Use database storage instead of memory
- Monitor with `docker stats`

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=debug docker-compose up
```

### Performance Profiling

```bash
# Install profiler
pip install py-spy

# Profile API server
py-spy record -o profile.svg -- python api_server.py
```

---

## Maintenance

### Backup

**Database Backup (PostgreSQL):**
```bash
pg_dump -h localhost -U anti_gravity anti_gravity_db > backup.sql
```

**Session Data Backup (Redis):**
```bash
redis-cli SAVE
cp /var/lib/redis/dump.rdb /backup/redis-$(date +%Y%m%d).rdb
```

### Updates

```bash
# Update application
git pull origin main
docker-compose build
docker-compose up -d

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Monitoring Checklist

Daily:
- [ ] Check error logs
- [ ] Monitor API response times
- [ ] Verify AI generation success rate

Weekly:
- [ ] Review security logs
- [ ] Check disk space
- [ ] Verify backups
- [ ] Review performance metrics

Monthly:
- [ ] Update dependencies
- [ ] Rotate API keys
- [ ] Review and optimize costs
- [ ] Load testing

---

## Production Checklist

Before going live:

- [ ] SSL certificates configured
- [ ] Environment variables set
- [ ] API keys secured
- [ ] Database backups configured
- [ ] Monitoring setup
- [ ] Error tracking (Sentry)
- [ ] Log aggregation
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Health checks working
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Disaster recovery plan
- [ ] Support procedures documented

---

## Support & Resources

- **Documentation**: See `README.md`, `ENV_CONFIG.md`, `DEPLOYMENT.md`
- **API Documentation**: http://your-api-url/docs (Swagger UI)
- **Issues**: https://github.com/yourusername/anti-gravity/issues
- **Email**: support@yourdomain.com

---

## License

[Your License Here]

## Contributors

[Your Team Here]

---

**Last Updated**: 2025-12-18
**Version**: 1.0.0
