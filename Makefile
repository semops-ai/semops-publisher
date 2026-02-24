# Blog Generator Development Commands

.PHONY: help build up down logs shell test lint format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf " %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the Docker containers
	docker-compose build

up: ## Start the development environment
	docker-compose up -d

down: ## Stop the development environment
	docker-compose down

logs: ## View container logs
	docker-compose logs -f blog-generator

shell: ## Open a shell in the blog-generator container
	docker-compose exec blog-generator bash

test: ## Run tests
	docker-compose exec blog-generator python -m pytest

lint: ## Run linting
	docker-compose exec blog-generator ruff check .
	docker-compose exec blog-generator black --check .

format: ## Format code
	docker-compose exec blog-generator black .
	docker-compose exec blog-generator ruff --fix .

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

# Development shortcuts
dev-setup: build up ## Build and start development environment
	@echo "Development environment is ready!"
	@echo "Streamlit dashboard: http://localhost:8501"
	@echo "PostgreSQL: localhost:5432"

dev-reset: down clean build up ## Reset the entire development environment