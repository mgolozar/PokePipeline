.PHONY: install fmt lint test clean run docker-build docker-up docker-down help

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  run          - Run the pipeline"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up    - Start Docker containers"
	@echo "  docker-down  - Stop Docker containers"

install:
	pip install -e .[dev]

test:
	python -m pytest tests/ -v

run:
	python -m pokepipeline.cli

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

