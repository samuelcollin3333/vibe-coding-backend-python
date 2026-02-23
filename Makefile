.PHONY: test test-quick lint typecheck format openapi

# Run tests (downgrade → migrate → pytest)
test:
	docker compose -f docker-compose.test.yml run --rm backend sh -c \
		"alembic downgrade base && alembic upgrade head && pytest tests/ -v --tb=short"

# Run tests quick (downgrade → migrate → pytest, stop on first failure)
test-quick:
	docker compose -f docker-compose.test.yml run --rm backend sh -c \
		"alembic downgrade base && alembic upgrade head && pytest tests/ -x -q"

# Lint check
lint:
	docker compose -f docker-compose.test.yml run --rm backend ruff check src/ tests/
	docker compose -f docker-compose.test.yml run --rm backend black --check src/ tests/
	docker compose -f docker-compose.test.yml run --rm backend isort --check src/ tests/

# Type check
typecheck:
	docker compose -f docker-compose.test.yml run --rm backend mypy src/

# Format code
format:
	docker compose -f docker-compose.test.yml run --rm backend ruff check --fix src/ tests/
	docker compose -f docker-compose.test.yml run --rm backend black src/ tests/
	docker compose -f docker-compose.test.yml run --rm backend isort src/ tests/

# Generate OpenAPI spec from FastAPI app
openapi:
	docker compose -f docker-compose.test.yml run --rm backend python -c \
		"import yaml; from src.infrastructure.api.app import app; print(yaml.dump(app.openapi(), sort_keys=False))" > openapi.yaml
