IMAGE=deepface-finder:local

# DOCKER COMPOSE
# ==============

# Run app in Docker
up:
	docker-compose up --build -d

# Stop app in Docker
down:
	docker-compose down

# LOCAL DEVELOPMENT
# =================

run:
	PYTHONBREAKPOINT=ipdb.set_trace \
	PYTHONPATH=src \
	python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Install all dependencies
deps: pipenv

# Install py dependencies
pipenv:
	pip install pipenv
	pipenv install --dev

# Open Deepface Finder UI
ui:
	open http://localhost:8080

# Run tests
tests:
	PYTHONPATH=src pytest --cov

# Run tests with coverage
coverage:
	PYTHONPATH=src pytest --cov --cov-report=html:htmlcov --disable-warnings || true
	open htmlcov/index.html

# Formatting
fmt:
	black .
	isort .

# Linting
lint:
	flake8 .
	mypy .

# Run all checks
check: fmt lint gitleaks

gitleaks:
	gitleaks git -v
