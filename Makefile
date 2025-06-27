# SecRef Makefile
.PHONY: help install dev build test lint clean docker-build docker-up docker-down backup

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	npm install
	pip install -r requirements.txt
	pip install -r admin/requirements.txt

dev: ## Run Astro development server only
	npm run dev

dev-all: ## Start both Astro site and admin panel
	@./start.sh

admin: ## Run admin panel only
	cd admin && flask run

build: ## Build for production
	npm run build

test: ## Run all tests
	npm test
	python -m pytest tests/

lint: ## Run linters
	npm run lint
	flake8 admin/ scripts/
	black --check admin/ scripts/

format: ## Format code
	prettier --write "src/**/*.{js,jsx,ts,tsx,astro,css,md}"
	black admin/ scripts/

clean: ## Clean build artifacts
	rm -rf dist/ .astro/ node_modules/ __pycache__/ .pytest_cache/

docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

backup: ## Create database backup
	python scripts/backup_database.py

db-init: ## Initialize database
	cd admin && python -c "from app import init_db; init_db()"

db-import: ## Import data from JSON files
	python scripts/import_json.py

security-check: ## Run security checks
	npm audit
	pip-audit -r requirements.txt
	pip-audit -r admin/requirements.txt

pre-commit: ## Install pre-commit hooks
	pre-commit install

deploy: ## Deploy to production (requires setup)
	./scripts/deploy.sh