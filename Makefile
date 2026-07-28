.PHONY: help install run test migrate docker-up docker-down lint

help:
	@echo "Enterprise RAG Makefile Commands:"
	@echo "  make install     Install requirements in active virtualenv"
	@echo "  make run         Start FastAPI development server"
	@echo "  make test        Execute test suite via pytest"
	@echo "  make migrate     Run database migrations using Alembic"
	@echo "  make docker-up   Launch local stack via Docker Compose"
	@echo "  make docker-down Stop local Docker stack"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest tests/ -v

migrate:
	alembic upgrade head

docker-up:
	docker-compose up -d --build

docker-down:
	docker-compose down -v
