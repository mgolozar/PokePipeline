.PHONY: install fmt lint test clean run docker-build docker-up docker-down help

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies"
	@echo "  fmt          - Format code with black"
	@echo "  lint         - Lint code with ruff"
	@echo "  test         - Run tests"
	@echo "  clean        - Clean build artifacts"
	@echo "  run          - Run the pipeline"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up    - Start Docker containers"
	@echo "  docker-down  - Stop Docker containers"

install:
	pip install -e .[dev]

fmt:
	black pokepipeline/ tests/
	ruff check --fix pokepipeline/ tests/

lint:
	ruff check pokepipeline/ tests/
	black --check pokepipeline/ tests/

test:
	pytest tests/ -v --cov=pokepipeline --cov-report=term-missing

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python -m pokepipeline.cli run

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

