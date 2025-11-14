.PHONY: help install test lint format clean build run stop

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run all tests"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo "  make build         - Build Docker image"
	@echo "  make run           - Start development"
	@echo "  make stop          - Stop all services"
	@echo "  make staging-up    - Start staging"
	@echo "  make prod-up       - Start production"

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=app --cov-report=html

lint:
	flake8 app.py tests/
	pylint app.py --disable=C0111,R0903

format:
	black app.py tests/

clean:
	rm -rf __pycache__ .pytest_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

build:
	docker build -t flask-task-api:latest .

run:
	docker-compose up -d

stop:
	docker-compose down

staging-up:
	docker-compose -f docker-compose.staging.yml up -d

staging-down:
	docker-compose -f docker-compose.staging.yml down

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

logs:
	docker-compose logs -f app

health:
	@curl -s http://localhost:5000/health | python -m json.tool
