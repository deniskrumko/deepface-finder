FROM python:3.12.11-slim-bullseye

# Set the user to root (optional, as it's the default)
USER root

RUN mkdir build
WORKDIR /build

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --ignore-pipfile --system -v && \
    pip uninstall -y pipenv && \
    rm -rf ~/.cache/pip /root/.cache/pipenv /root/.local/share/virtualenvs

# Compile translations
COPY scripts ./scripts
COPY locale ./locale
COPY babel.cfg ./
RUN sh scripts/compile_translations.sh

COPY src ./src
ENV PYTHONPATH=src

ENV YOLO_CONFIG_DIR=/yolo_config
RUN mkdir /yolo_config

EXPOSE 8080

CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
