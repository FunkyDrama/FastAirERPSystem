FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock /app/

RUN pip install --no-cache-dir poetry \
 && poetry install --no-interaction --no-root

COPY . /app/
