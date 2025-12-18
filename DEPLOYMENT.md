# Anti-Gravity Deployment Guide

Complete guide for deploying the Anti-Gravity astrology system to production.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start with Docker](#quick-start-with-docker)
3. [Manual Deployment](#manual-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Production Considerations](#production-considerations)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Docker**: 20.10+ and Docker Compose 2.0+
- **Git**: For cloning the repository

### Optional (for manual deployment)

- **Python**: 3.11+
- **Node.js**: 18+
- **npm**: 9+

### API Keys (at least one required)

- **OpenAI API Key**: For GPT-4o content generation
- **Google Gemini API Key**: Alternative AI provider

Get API keys from:
- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://makersuite.google.com/app/apikey

---

## Quick Start with Docker

### 1. Clone Repository

```bash
git clone https://github.com/francedirectjp-art/astro-medical-backend.git
cd astro-medical-backend
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Minimum required configuration:
```bash
OPENAI_API_KEY=sk-proj-your-key-here
# OR
GOOGLE_API_KEY=your-gemini-key-here
```

### 3. Build and Start

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 5. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Manual Deployment

### Backend Deployment

#### 1. Install Dependencies

```bash
# Install system packages (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    python3.11 \
    python3-pip \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    build-essential

# Install Python packages
pip install -r requirements.txt
```

#### 2. Configure Environment

```bash
export OPENAI_API_KEY=your-key-here
export GOOGLE_API_KEY=your-gemini-key-here
```

#### 3. Run Backend

```bash
# Development
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000

# Production (with Gunicorn)
gunicorn api_server:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -
```

### Frontend Deployment

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

#### 2. Configure Environment

```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

#### 3. Build and Run

```bash
# Build for production
npm run build

# Start production server
npm start

# Or use PM2 for process management
npm install -g pm2
pm2 start npm --name "anti-gravity-frontend" -- start
```

---

## Environment Configuration

### Backend Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | One of two | OpenAI API key | - |
| `GOOGLE_API_KEY` | One of two | Google Gemini API key | - |
| `PYTHONUNBUFFERED` | No | Python output buffering | 1 |

### Frontend Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL | http://localhost:8000 |
| `NODE_ENV` | No | Node environment | production |

### Docker Environment Variables

Set in `.env` file or pass to `docker-compose`:

```bash
# Run with custom environment
OPENAI_API_KEY=your-key docker-compose up -d
```

---

## Production Considerations

### 1. Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/anti-gravity

server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for long AI generation
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/anti-gravity /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 2. SSL/TLS (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

### 3. Firewall Configuration

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# If accessing backend directly (not recommended)
# sudo ufw allow 8000/tcp

sudo ufw enable
```

### 4. System Service (systemd)

#### Backend Service

```ini
# /etc/systemd/system/anti-gravity-backend.service

[Unit]
Description=Anti-Gravity Backend API
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/anti-gravity
Environment="OPENAI_API_KEY=your-key-here"
ExecStart=/usr/local/bin/gunicorn api_server:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 300
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Frontend Service

```ini
# /etc/systemd/system/anti-gravity-frontend.service

[Unit]
Description=Anti-Gravity Frontend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/anti-gravity/frontend
Environment="NODE_ENV=production"
Environment="NEXT_PUBLIC_API_URL=http://localhost:8000"
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable anti-gravity-backend
sudo systemctl enable anti-gravity-frontend
sudo systemctl start anti-gravity-backend
sudo systemctl start anti-gravity-frontend
```

### 5. Database (Optional)

For session persistence, consider adding:

- **PostgreSQL**: For session storage
- **Redis**: For caching and session management

---

## Monitoring and Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Frontend (should return HTML)
curl http://localhost:3000
```

### Logs

#### Docker Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### Manual Deployment Logs

```bash
# Backend (if using systemd)
sudo journalctl -u anti-gravity-backend -f

# Frontend
sudo journalctl -u anti-gravity-frontend -f
```

### Backup

#### Important Files to Backup

```bash
# Configuration
.env
docker-compose.yml

# Generated PDFs
output/

# Swiss Ephemeris data
swe_data/

# Master content
anti_gravity_master_content.json
```

#### Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/var/backups/anti-gravity"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    .env \
    docker-compose.yml \
    anti_gravity_master_content.json

# Backup outputs
tar -czf $BACKUP_DIR/output_$DATE.tar.gz output/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

### Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Or for manual deployment
pip install -r requirements.txt --upgrade
cd frontend && npm install && npm run build
sudo systemctl restart anti-gravity-backend
sudo systemctl restart anti-gravity-frontend
```

---

## Troubleshooting

### Backend Issues

#### API Key Not Working

```bash
# Check if environment variable is set
docker-compose exec backend env | grep API_KEY

# Test API key manually
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
    https://api.openai.com/v1/models
```

#### PDF Generation Fails

```bash
# Check if Japanese fonts are installed
docker-compose exec backend fc-list | grep -i noto

# If missing, rebuild image
docker-compose build --no-cache backend
```

#### Swiss Ephemeris Error

```bash
# Ensure swe_data directory exists and is readable
ls -la swe_data/

# Re-copy ephemeris files
cp -r swe_data/ /path/to/deployment/
```

### Frontend Issues

#### Cannot Connect to Backend

```bash
# Check if NEXT_PUBLIC_API_URL is correct
docker-compose exec frontend env | grep API_URL

# Test backend connection
curl http://backend:8000/health
```

#### Build Fails

```bash
# Clear cache and rebuild
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### Docker Issues

#### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000
sudo lsof -i :3000

# Change ports in docker-compose.yml
# Or stop conflicting service
```

#### Out of Disk Space

```bash
# Remove unused Docker resources
docker system prune -a

# Check disk usage
df -h
docker system df
```

---

## Performance Optimization

### 1. Backend Optimization

```python
# Increase Gunicorn workers
--workers $(( 2 * $(nproc) + 1 ))

# Enable worker timeout
--timeout 300

# Use gevent for async
--worker-class gevent
```

### 2. Frontend Optimization

```bash
# Enable compression in next.config.js
compress: true

# Optimize images
npm install sharp
```

### 3. Caching

- Add Redis for session caching
- Enable Nginx caching for static assets
- Use CDN for frontend assets

### 4. Load Balancing

For high traffic:

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
    # ... rest of config
```

---

## Security Checklist

- [ ] Change default ports in production
- [ ] Use HTTPS with valid SSL certificate
- [ ] Set strong API keys
- [ ] Enable firewall
- [ ] Restrict Docker daemon access
- [ ] Use non-root users
- [ ] Keep dependencies updated
- [ ] Enable rate limiting
- [ ] Monitor logs for suspicious activity
- [ ] Regular backups

---

## Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check GitHub issues: https://github.com/francedirectjp-art/astro-medical-backend/issues

---

**Last Updated**: 2024-12-18  
**Version**: 1.0.0  
**Maintainer**: Anti-Gravity Development Team
