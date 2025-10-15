IMAGE=deepface-finder:local
CUDA_IMAGE=deepface-finder-cuda116:local
# MY_IP=0.0.0.0
MY_IP=192.168.1.139
CONFIG=config/kolesa.toml
# CONFIG=config/birthday.toml

# DOCKER COMPOSE
# ==============

# Run app in Docker
up:
	docker-compose up --build

# Stop app in Docker
down:
	docker-compose down

# DOCKER
# ======

build:
	docker build -t ${IMAGE} .

build-cuda:
	docker build -f Dockerfile.cuda -t ${CUDA_IMAGE} .

# LOCAL DEVELOPMENT
# =================

my_ip:
	ipconfig getifaddr en0

run:
	PYTHONBREAKPOINT=ipdb.set_trace \
	PYTHONPATH=src \
	APP_CONFIG=${CONFIG} \
	python3 -m uvicorn app.main:app --host ${MY_IP} --port 8080

# Install all dependencies
deps: pipenv

# Install py dependencies
pipenv:
	pip install pipenv
	pipenv install --dev --pipfile=Pipfile.cpu

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
