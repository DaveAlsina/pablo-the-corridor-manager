.PHONY: help setup start stop reset populate test clean install sync

help:
	@echo "Corridor Bot - Available Commands (using uv):"
	@echo ""
	@echo "  make setup      - Initial setup (create .env, start database)"
	@echo "  make install    - Install dependencies with uv"
	@echo "  make sync       - Sync dependencies (after updating pyproject.toml)"
	@echo "  make start      - Start the bot"
	@echo "  make db-up      - Start PostgreSQL container"
	@echo "  make db-down    - Stop PostgreSQL container"
	@echo "  make populate   - Populate database with initial data"
	@echo "  make reset      - Reset database (WARNING: deletes all data)"
	@echo "  make test       - Run setup verification tests"
	@echo "  make clean      - Remove Python cache files"
	@echo ""

setup:
	@echo "Setting up Corridor Bot..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file - please edit it with your tokens"; \
	else \
		echo "⚠️  .env already exists"; \
	fi
	@echo "Starting PostgreSQL..."
	docker-compose up -d
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file with your bot token and chat ID"
	@echo "2. Run: make install"
	@echo "3. Run: make populate"
	@echo "4. Run: make test"
	@echo "5. Run: make start"

install:
	@echo "Installing dependencies with uv..."
	uv sync
	@echo "✅ Dependencies installed"

sync:
	@echo "Syncing dependencies..."
	uv sync
	@echo "✅ Dependencies synced"

start:
	@echo "Starting Corridor Bot..."
	uv run python src/bot.py

db-up:
	@echo "Starting PostgreSQL container..."
	docker-compose up -d
	@echo "✅ PostgreSQL is running"
	@echo "   pgAdmin: http://localhost:5050"

db-down:
	@echo "Stopping PostgreSQL container..."
	docker-compose down

populate:
	@echo "Populating database..."
	uv run python scripts/populate_db.py

reset:
	@echo "Resetting database..."
	uv run python scripts/reset_db.py

test:
	@echo "Running setup verification..."
	uv run python scripts/test_setup.py

clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✅ Cleanup complete"

logs:
	@echo "Showing PostgreSQL logs..."
	docker-compose logs -f postgres