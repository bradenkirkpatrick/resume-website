.PHONY: all install test test-backend test-frontend test-coverage lint lint-fix \
        start-local stop-local start-prod stop-prod clean setup

# Default target: run tests
all: test lint

# Install all dependencies
install:
	@echo "Installing backend dependencies..."
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -q -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install --silent
	@echo "All dependencies installed."

# Run all tests
test: test-backend test-frontend

# Run backend tests with coverage
test-backend:
	@echo "Running backend tests..."
	cd backend && source venv/bin/activate && python3 -m pytest -v --cov=app --cov-report=term-missing --cov-fail-under=90

# Run frontend tests
test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npx vitest run --coverage

# Run tests with coverage (alias for test)
test-coverage: test

# Lint all code
lint:
	@echo "Linting backend..."
	cd backend && source venv/bin/activate && flake8 app tests && black --check app tests && isort --check app tests
	@echo "Linting frontend..."
	cd frontend && npm run lint

# Auto-fix lint issues
lint-fix:
	@echo "Fixing backend lint issues..."
	cd backend && source venv/bin/activate && black app tests && isort app tests
	@echo "Fixing frontend lint issues..."
	cd frontend && npx eslint --fix src && npx prettier --write "src/**/*.{js,jsx,css}"

# Start local development servers
start-local:
	npm run start-local -- $(ARGS)

# Stop local development servers
stop-local:
	npm run stop-local

# Start production servers
start-prod:
	npm run start-prod -- $(ARGS)

# Stop production servers
stop-prod:
	npm run stop-prod

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf backend/venv
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf .pytest_cache
	rm -rf __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete."

# Full setup from scratch
setup: clean install
	@echo "Setup complete. Run 'make start-local' to start the development servers."
