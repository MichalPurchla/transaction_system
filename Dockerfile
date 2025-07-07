FROM python:3.13.3-slim as base

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PORT=${PORT}
WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

COPY . .

FROM base as local
ENTRYPOINT python manage.py migrate && python manage.py runserver 0.0.0.0:${PORT}

FROM base as testing
ENTRYPOINT coverage run --source='.' manage.py test && coverage report

