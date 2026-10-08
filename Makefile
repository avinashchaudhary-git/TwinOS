.PHONY: up down migrate seed train test lint demo local-backend local-frontend help

help:
	@echo "TwinOS - Digital Twin Operating System"
	@echo "Available commands:"
	@echo "  make up          - Start all docker containers"
	@echo "  make down        - Stop all docker containers"
	@echo "  make migrate     - Run database migrations"
	@echo "  make seed        - Seed demo data across PostgreSQL, Neo4j, Chroma"
	@echo "  make train       - Train ML risk prediction model"
	@echo "  make test        - Run backend test suite"
	@echo "  make lint        - Run linting (ruff, black, mypy)"
	@echo "  make demo        - Complete demo setup and run"
	@echo "  make local-backend - Run FastAPI locally"
	@echo "  make local-frontend - Run Next.js locally"

up:
	docker compose up -d

down:
	docker compose down -v

migrate:
	cd backend && alembic upgrade head

train:
	cd backend && python -m app.ml.train

seed:
	cd backend && python -m scripts.seed_demo

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check . && black --check .

demo:
	@echo "Starting TwinOS in mock demo mode..."
	python -m backend.scripts.bootstrap_graph || true
	python -m backend.app.ml.train
	python -m backend.scripts.seed_demo
