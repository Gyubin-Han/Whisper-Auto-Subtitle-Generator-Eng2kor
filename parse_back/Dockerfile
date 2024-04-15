FROM python:3.12

WORKDIR /code

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock .env ./

RUN poetry install --no-root