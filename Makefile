# Project Variables
PYTHON=python
PIP=pip
APP=main:app
HOST=127.0.0.1
PORT=8000

# Run the FastAPI app
run:
	uvicorn $(APP) --host $(HOST) --port $(PORT) --reload

# Install dependencies
install:
	$(PIP) install -r requirements.txt

# Freeze current environment packages
freeze:
	$(PIP) freeze > requirements.txt

# Run tests (assumes pytest)
test:
	pytest tests/

# Lint using flake8
lint:
	flake8 .

# Format code with black
format:
	black .

# Check typing with mypy
type-check:
	mypy .

# Clean __pycache__ and *.pyc files
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +; \
	find . -type f -name "*.pyc" -delete

# Help
help:
	@echo "Makefile commands:"
	@echo "  make run         - Run FastAPI server"
	@echo "  make install     - Install dependencies"
	@echo "  make freeze      - Freeze dependencies to requirements.txt"
	@echo "  make test        - Run tests with pytest"
	@echo "  make lint        - Lint code with flake8"
	@echo "  make format      - Format code with black"
	@echo "  make type-check  - Run mypy for static typing checks"
	@echo "  make clean       - Remove __pycache__ and .pyc files"
