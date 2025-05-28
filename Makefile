.PHONY: help build up down restart logs clean health

# Default target
help:
	@echo "Available commands:"
	@echo "  build     - Build Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  restart   - Restart all services"
	@echo "  logs      - Show logs"
	@echo "  logs-api  - Show API logs only"
	@echo "  logs-db   - Show Qdrant logs only"
	@echo "  clean     - Remove containers and volumes"
	@echo "  health    - Check service health"
	@echo "  shell     - Access API container shell"

# Build Docker images
build:
	docker-compose build --no-cache

# Start all services
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Restart all services
restart:
	docker-compose restart

# Show logs for all services
logs:
	docker-compose logs -f

# Show API logs only
logs-api:
	docker-compose logs -f bejo-api

# Show Qdrant logs only
logs-db:
	docker-compose logs -f qdrant

# Clean up containers and volumes
clean:
	docker-compose down -v
	docker system prune -f

# Check service health
health:
	@echo "Checking Qdrant health..."
	@curl -s http://localhost:6333/health || echo "Qdrant not accessible"
	@echo ""
	@echo "Checking API health..."
	@curl -s http://localhost:8000/api/v1/health || echo "API not accessible"

# Access API container shell
shell:
	docker-compose exec bejo-api /bin/bash

# Development commands
dev-up:
	docker-compose up

dev-build:
	docker-compose build

# Production commands (without rebuild)
prod-up:
	docker-compose -f docker-compose.yml up -d

# Quick restart API only
restart-api:
	docker-compose restart bejo-api