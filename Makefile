# FileGuard Makefile
# Convenient commands for development and deployment

.PHONY: help setup start stop restart logs clean test lint format install-backend install-frontend migrate seed

# Colors for output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(GREEN)FileGuard - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ==========================================
# Setup & Installation
# ==========================================

setup: ## Initial project setup (run once)
	@echo "$(GREEN)Setting up FileGuard...$(NC)"
	@cp -n .env.example .env || true
	@echo "$(YELLOW)Please edit .env with your configuration$(NC)"
	@echo "$(YELLOW)Generate a secret key with: make generate-secret$(NC)"
	@docker-compose pull
	@echo "$(GREEN)Setup complete! Run 'make start' to launch.$(NC)"

generate-secret: ## Generate a secure secret key
	@echo "SECRET_KEY=$$(openssl rand -hex 32)"

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install Python backend dependencies
	@echo "$(GREEN)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt

install-frontend: ## Install Node.js frontend dependencies
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	cd frontend && npm install

# ==========================================
# Docker Commands
# ==========================================

start: ## Start all services with Docker Compose
	@echo "$(GREEN)Starting FileGuard...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started!$(NC)"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "MinIO Console: http://localhost:9001"

stop: ## Stop all services
	@echo "$(YELLOW)Stopping FileGuard...$(NC)"
	docker-compose stop
	@echo "$(GREEN)Services stopped.$(NC)"

restart: stop start ## Restart all services

down: ## Stop and remove all containers
	@echo "$(RED)Removing all containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)Containers removed.$(NC)"

clean: ## Remove all containers, volumes, and images
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --rmi all; \
		echo "$(GREEN)Cleanup complete.$(NC)"; \
	fi

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

logs-celery: ## View Celery worker logs
	docker-compose logs -f celery-worker

ps: ## Show running containers
	docker-compose ps

# ==========================================
# Development Commands
# ==========================================

dev-backend: ## Run backend in development mode (outside Docker)
	@echo "$(GREEN)Starting backend in development mode...$(NC)"
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend in development mode (outside Docker)
	@echo "$(GREEN)Starting frontend in development mode...$(NC)"
	cd frontend && npm run dev

dev-celery: ## Run Celery worker in development mode
	@echo "$(GREEN)Starting Celery worker...$(NC)"
	cd backend && celery -A celery_app worker --loglevel=info

shell-backend: ## Open Python shell in backend container
	docker-compose exec backend python

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U fileguard -d fileguard_db

shell: ## Open bash shell in backend container
	docker-compose exec backend bash

# ==========================================
# Database Commands
# ==========================================

migrate: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
	docker-compose exec backend alembic upgrade head
	@echo "$(GREEN)Migrations complete.$(NC)"

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="your message")
	@echo "$(GREEN)Creating new migration...$(NC)"
	docker-compose exec backend alembic revision --autogenerate -m "$(MESSAGE)"

migrate-down: ## Rollback one migration
	@echo "$(YELLOW)Rolling back one migration...$(NC)"
	docker-compose exec backend alembic downgrade -1

migrate-history: ## Show migration history
	docker-compose exec backend alembic history

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "$(RED)WARNING: This will delete all database data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v postgres; \
		docker-compose up -d postgres; \
		sleep 5; \
		make migrate; \
		echo "$(GREEN)Database reset complete.$(NC)"; \
	fi

seed: ## Seed database with sample data (if available)
	@echo "$(GREEN)Seeding database...$(NC)"
	docker-compose exec backend python scripts/seed_data.py

# ==========================================
# Testing
# ==========================================

test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	@make test-backend
	@make test-frontend

test-backend: ## Run backend tests
	@echo "$(GREEN)Running backend tests...$(NC)"
	docker-compose exec backend pytest

test-backend-cov: ## Run backend tests with coverage
	@echo "$(GREEN)Running backend tests with coverage...$(NC)"
	docker-compose exec backend pytest --cov=. --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests
	@echo "$(GREEN)Running frontend tests...$(NC)"
	docker-compose exec frontend npm test -- --watchAll=false

test-frontend-cov: ## Run frontend tests with coverage
	@echo "$(GREEN)Running frontend tests with coverage...$(NC)"
	docker-compose exec frontend npm test -- --coverage --watchAll=false

# ==========================================
# Code Quality
# ==========================================

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend code
	@echo "$(GREEN)Linting backend...$(NC)"
	cd backend && flake8 .
	cd backend && mypy .

lint-frontend: ## Lint frontend code
	@echo "$(GREEN)Linting frontend...$(NC)"
	cd frontend && npm run lint

format: format-backend format-frontend ## Format all code

format-backend: ## Format backend code with black
	@echo "$(GREEN)Formatting backend code...$(NC)"
	cd backend && black .
	cd backend && isort .

format-frontend: ## Format frontend code with prettier
	@echo "$(GREEN)Formatting frontend code...$(NC)"
	cd frontend && npx prettier --write .

# ==========================================
# Security
# ==========================================

security-scan: ## Run security vulnerability scan
	@echo "$(GREEN)Running security scan...$(NC)"
	cd backend && pip-audit
	cd frontend && npm audit

security-fix: ## Fix security vulnerabilities
	@echo "$(GREEN)Fixing security vulnerabilities...$(NC)"
	cd backend && pip-audit --fix
	cd frontend && npm audit fix

# ==========================================
# Build & Deployment
# ==========================================

build: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose build

build-prod: ## Build production Docker images
	@echo "$(GREEN)Building production images...$(NC)"
	docker-compose -f docker-compose.prod.yml build

deploy: ## Deploy to production (customize as needed)
	@echo "$(RED)Deployment script not configured.$(NC)"
	@echo "Edit Makefile to add your deployment commands."

# ==========================================
# Monitoring
# ==========================================

health: ## Check health of all services
	@echo "$(GREEN)Checking service health...$(NC)"
	@curl -f http://localhost:8000/health && echo "$(GREEN)Backend: OK$(NC)" || echo "$(RED)Backend: FAIL$(NC)"
	@curl -f http://localhost:3000 && echo "$(GREEN)Frontend: OK$(NC)" || echo "$(RED)Frontend: FAIL$(NC)"

stats: ## Show Docker stats
	docker stats $$(docker-compose ps -q)

# ==========================================
# Backup & Restore
# ==========================================

backup-db: ## Backup PostgreSQL database
	@echo "$(GREEN)Backing up database...$(NC)"
	@mkdir -p backups
	docker-compose exec -T postgres pg_dump -U fileguard fileguard_db > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Database backed up to backups/$(NC)"

restore-db: ## Restore database from backup (usage: make restore-db FILE=backup.sql)
	@echo "$(YELLOW)Restoring database from $(FILE)...$(NC)"
	docker-compose exec -T postgres psql -U fileguard -d fileguard_db < $(FILE)
	@echo "$(GREEN)Database restored.$(NC)"

# ==========================================
# Utilities
# ==========================================

update: ## Update all dependencies
	@echo "$(GREEN)Updating dependencies...$(NC)"
	cd backend && pip install --upgrade -r requirements.txt
	cd frontend && npm update
	@echo "$(GREEN)Dependencies updated.$(NC)"

ports: ## Show which ports are being used
	@echo "$(GREEN)Service Ports:$(NC)"
	@echo "Frontend:    3000"
	@echo "Backend:     8000"
	@echo "PostgreSQL:  5432"
	@echo "Redis:       6379"
	@echo "MinIO:       9000"
	@echo "MinIO UI:    9001"
	@echo "ClamAV:      3310"

docs: ## Open API documentation in browser
	@echo "$(GREEN)Opening API documentation...$(NC)"
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs || echo "Open http://localhost:8000/docs in your browser"

version: ## Show version information
	@echo "$(GREEN)FileGuard Version Information:$(NC)"
	@echo "App Version: 2.0.0"
	@echo "Python: $$(python --version 2>&1)"
	@echo "Node: $$(node --version 2>&1)"
	@echo "Docker: $$(docker --version 2>&1)"

# ==========================================
# Quick Start
# ==========================================

quickstart: setup start migrate ## Quick start for new users
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)  FileGuard is ready!$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "🌐 Frontend:  http://localhost:3000"
	@echo "📡 Backend:   http://localhost:8000"
	@echo "📚 API Docs:  http://localhost:8000/docs"
	@echo "💾 MinIO UI:  http://localhost:9001"
	@echo ""
	@echo "Next steps:"
	@echo "1. Create an account at http://localhost:3000"
	@echo "2. Upload your first file"
	@echo "3. Explore the features!"
	@echo ""
