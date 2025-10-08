FROM python:3.12.11-slim-bullseye

RUN mkdir build
WORKDIR /build

# Install dependencies
RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*

# Install python packages
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --ignore-pipfile --system -v && \
    pip uninstall -y pipenv && \
    rm -rf ~/.cache/pip /root/.cache/pipenv /root/.local/share/virtualenvs

# Compile translations
RUN sh scripts/compile_translations.sh

ENV PYTHONPATH=src
EXPOSE 8080

CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
