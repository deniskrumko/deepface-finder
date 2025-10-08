IMAGE=deepface-finder:local
# MY_IP=0.0.0.0
MY_IP=192.168.1.139

# DOCKER COMPOSE
# ==============

# Run app in Docker
up:
	docker-compose up --build -d

# Stop app in Docker
down:
	docker-compose down

# DOCKER
# ======

build:
	docker build -t ${IMAGE} .

# LOCAL DEVELOPMENT
# =================

my_ip:
	ipconfig getifaddr en0

run:
	PYTHONBREAKPOINT=ipdb.set_trace \
	PYTHONPATH=src \
	APP_CONFIG=config/test.toml \
	python3 -m uvicorn app.main:app --host ${MY_IP} --port 8080

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

# Collect i18n translation stirngs
collect_translations:
	./scripts/collect_translations.sh

# Compile i18n translations
compile_translations:
	./scripts/compile_translations.sh

find_missing_translations:
	./scripts/find_missing_translations.sh
