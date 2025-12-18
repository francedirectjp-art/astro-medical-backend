# Environment Configuration Guide

## Overview

This guide explains all environment variables required for the Anti-Gravity astrology web application.

## Backend Environment Variables

### Required Variables

#### AI API Keys (Choose one or both)

**OpenAI API Key** (Recommended for production)
```bash
OPENAI_API_KEY=sk-...your-key-here...
```
- Used for GPT-4o based content generation
- High quality, reliable Japanese output
- Required for dynamic AI content blocks
- Get your key from: https://platform.openai.com/api-keys

**Google Gemini API Key** (Alternative)
```bash
GOOGLE_API_KEY=...your-key-here...
```
- Used for Gemini Pro based content generation
- Free tier available for testing
- Good for development/testing
- Get your key from: https://makersuite.google.com/app/apikey

**Model Selection**
```bash
AI_MODEL=gpt-4o  # Options: gpt-4o, gemini-pro
```
- Default: gpt-4o (if OPENAI_API_KEY is set)
- Falls back to gemini-pro if only GOOGLE_API_KEY is set

### Optional Variables

**API Server Configuration**
```bash
# Server host and port
API_HOST=0.0.0.0
API_PORT=8000

# CORS settings (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Log level
LOG_LEVEL=info  # Options: debug, info, warning, error
```

**PDF Generation**
```bash
# Custom font path for Japanese text
JAPANESE_FONT_PATH=/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttf

# PDF output directory
PDF_OUTPUT_DIR=./output

# Maximum PDF file size (MB)
MAX_PDF_SIZE=50
```

**Session Management**
```bash
# Session timeout (seconds)
SESSION_TIMEOUT=3600

# Maximum concurrent sessions
MAX_SESSIONS=100

# Session cleanup interval (seconds)
SESSION_CLEANUP_INTERVAL=600
```

**Swiss Ephemeris**
```bash
# Path to Swiss Ephemeris data files
SWISSEPH_PATH=./swe_data

# Default ephemeris path (if not specified, uses built-in)
# EPHE_PATH=/usr/share/swisseph/ephe
```

**AI Generation Settings**
```bash
# Maximum retries for AI API calls
AI_MAX_RETRIES=3

# Timeout for AI API calls (seconds)
AI_TIMEOUT=60

# Temperature for AI generation (0.0-1.0)
AI_TEMPERATURE=0.7

# Maximum tokens for AI generation
AI_MAX_TOKENS=4096

# Enable streaming for AI responses
AI_STREAMING=true
```

**Performance**
```bash
# Number of worker processes (for production)
WORKERS=4

# Worker timeout (seconds)
WORKER_TIMEOUT=120

# Keep-alive timeout (seconds)
KEEPALIVE_TIMEOUT=5
```

## Frontend Environment Variables

### Required Variables

**API Endpoint**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```
- Backend API base URL
- Must be accessible from the browser
- For production: use your deployed backend URL

### Optional Variables

**Application Settings**
```bash
# Application title
NEXT_PUBLIC_APP_TITLE=Anti-Gravity Strategic Life Navigation

# Default locale
NEXT_PUBLIC_DEFAULT_LOCALE=ja

# Enable debug mode
NEXT_PUBLIC_DEBUG=false
```

**UI Configuration**
```bash
# Animation speed (ms)
NEXT_PUBLIC_ANIMATION_SPEED=50

# Auto-scroll speed
NEXT_PUBLIC_AUTOSCROLL_SPEED=100

# Progress update interval (ms)
NEXT_PUBLIC_PROGRESS_INTERVAL=1000
```

**Feature Flags**
```bash
# Enable PDF preview
NEXT_PUBLIC_ENABLE_PDF_PREVIEW=true

# Enable content streaming
NEXT_PUBLIC_ENABLE_STREAMING=true

# Enable analytics
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

## Environment File Setup

### Development

Create `.env.local` in the backend directory:
```bash
# Backend .env.local
OPENAI_API_KEY=sk-...your-key-here...
AI_MODEL=gpt-4o
LOG_LEVEL=debug
SESSION_TIMEOUT=7200
```

Create `.env.local` in the frontend directory:
```bash
# Frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEBUG=true
```

### Production

Create `.env` in the backend directory:
```bash
# Backend .env (production)
OPENAI_API_KEY=sk-...your-production-key...
AI_MODEL=gpt-4o
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=info
SESSION_TIMEOUT=3600
WORKERS=4
JAPANESE_FONT_PATH=/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttf
```

Create `.env` in the frontend directory:
```bash
# Frontend .env (production)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_DEBUG=false
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

## Docker Configuration

When using Docker, environment variables can be set in:

1. **docker-compose.yml** (recommended for local development)
2. **.env file** (loaded automatically by docker-compose)
3. **Command line** (-e flag)

### Example docker-compose.yml

```yaml
services:
  backend:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AI_MODEL=gpt-4o
      - LOG_LEVEL=info
      - WORKERS=4
  
  frontend:
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
```

### Example .env file for Docker

```bash
# .env (for docker-compose)
OPENAI_API_KEY=sk-...your-key-here...
GOOGLE_API_KEY=...your-key-here...
```

## Security Best Practices

### 1. Never Commit API Keys

Add to `.gitignore`:
```
.env
.env.local
.env.production
*.env
```

### 2. Use Environment-Specific Files

- `.env.local` - Local development (not committed)
- `.env.development` - Development environment
- `.env.production` - Production environment
- `.env.test` - Testing environment

### 3. Rotate Keys Regularly

- Change API keys every 3-6 months
- Immediately rotate if compromised
- Use different keys for dev/staging/production

### 4. Use Secret Management

For production, consider:
- AWS Secrets Manager
- Google Secret Manager
- HashiCorp Vault
- Azure Key Vault

## Validation

### Check Backend Configuration

```bash
cd backend
python3 -c "
from api_server import app
import os

print('Environment Check:')
print(f'OPENAI_API_KEY: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}')
print(f'GOOGLE_API_KEY: {'✅' if os.getenv('GOOGLE_API_KEY') else '❌'}')
print(f'AI_MODEL: {os.getenv('AI_MODEL', 'gpt-4o')}')
print(f'LOG_LEVEL: {os.getenv('LOG_LEVEL', 'info')}')
"
```

### Check Frontend Configuration

```bash
cd frontend
npm run env:check
```

Or manually:
```bash
echo "NEXT_PUBLIC_API_URL: $NEXT_PUBLIC_API_URL"
```

## Troubleshooting

### AI Generator Not Working

```
⚠️ ai_generator: False
```

**Solution**: Set either `OPENAI_API_KEY` or `GOOGLE_API_KEY`

### PDF Generation Fails

```
Error: Font not found
```

**Solution**: 
1. Install Japanese fonts: `apt-get install fonts-noto-cjk`
2. Set `JAPANESE_FONT_PATH` environment variable

### CORS Errors in Frontend

```
Access-Control-Allow-Origin error
```

**Solution**: Add frontend URL to `CORS_ORIGINS`:
```bash
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Session Timeout Issues

**Solution**: Increase `SESSION_TIMEOUT`:
```bash
SESSION_TIMEOUT=7200  # 2 hours
```

## Quick Start

### Minimal Configuration (Development)

**Backend** (`.env.local`):
```bash
OPENAI_API_KEY=sk-...your-key...
```

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Full Configuration (Production)

Use the `.env.example` file as a template:
```bash
cp .env.example .env
# Edit .env with your production values
```

## Additional Resources

- [FastAPI Environment Variables](https://fastapi.tiangolo.com/advanced/settings/)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)
- [Docker Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [12-Factor App Config](https://12factor.net/config)

## Support

For issues with environment configuration:
1. Check logs: `docker-compose logs -f backend`
2. Verify file permissions: `ls -la .env`
3. Test API health: `curl http://localhost:8000/health`
4. Review documentation: `DEPLOYMENT.md`
