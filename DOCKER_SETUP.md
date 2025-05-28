# BEJO Docker Setup Instructions

## Prerequisites

- Docker installed on your system
- Docker Compose installed
- Google AI API key

## Quick Start

### 1. Environment Setup

Copy the environment example file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file and add your Google API key:

```
GOOGLE_API_KEY=your_actual_google_api_key_here
```

### 2. Using Makefile (Recommended)

```bash
# Build and start all services
make build
make up

# Check if services are running
make health

# View logs
make logs

# Stop services
make down
```

### 3. Using Docker Compose Directly

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Service URLs

- **BEJO API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Health Check**: http://localhost:8000/api/v1/health

## Directory Structure

```
project/
├── app/                    # Application code
├── Dockerfile              # API container definition
├── docker-compose.yml      # Services orchestration
├── .dockerignore          # Docker ignore file
├── .env                   # Environment variables
├── .env.example           # Environment template
├── Makefile              # Docker management commands
└── uploads/              # File uploads (mounted volume)
```

## Development Workflow

### Starting Development

```bash
# Start in foreground (see logs immediately)
make dev-up

# Start in background
make up
```

### Making Changes

When you modify code:

```bash
# Rebuild and restart API only
make restart-api

# Or rebuild everything
make build
make restart
```

### Debugging

```bash
# View all logs
make logs

# View API logs only
make logs-api

# View Qdrant logs only
make logs-db

# Access container shell
make shell
```

### File Uploads

The `app/uploads` directory is mounted as a volume, so uploaded files persist between container restarts.

## Production Deployment

### Using Docker Compose

```bash
# Production start (detached)
make prod-up

# Monitor
make health
make logs
```

### Environment Variables for Production

Update your `.env` file for production:

```env
BASE_URL=https://your-domain.com
QDRANT_URL=http://qdrant:6333
LOG_LEVEL=WARNING
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: If ports 6333 or 8000 are in use:

   ```bash
   # Check port usage
   netstat -tulpn | grep :6333
   netstat -tulpn | grep :8000
   ```

2. **Qdrant connection issues**:

   ```bash
   # Check Qdrant health
   curl http://localhost:6333/health

   # Check container logs
   make logs-db
   ```

3. **API startup issues**:

   ```bash
   # Check API logs
   make logs-api

   # Verify environment variables
   docker-compose exec bejo-api env | grep GOOGLE_API_KEY
   ```

### Clean Reset

If you need to start fresh:

```bash
# Stop and remove everything
make clean

# Rebuild from scratch
make build
make up
```

## Maintenance

### Updating Dependencies

1. Update `pyproject.toml`
2. Rebuild images:
   ```bash
   make build
   make restart
   ```

### Backup Qdrant Data

The Qdrant data is stored in a named volume. To backup:

```bash
# Create backup
docker run --rm -v bejo_qdrant_storage:/data -v $(pwd):/backup ubuntu tar czf /backup/qdrant-backup.tar.gz -C /data .

# Restore backup
docker run --rm -v bejo_qdrant_storage:/data -v $(pwd):/backup ubuntu tar xzf /backup/qdrant-backup.tar.gz -C /data
```

## Security Notes

- Never commit `.env` file with real API keys
- Use secrets management in production
- Consider using reverse proxy (nginx) for production
- Enable firewall rules for production deployment
