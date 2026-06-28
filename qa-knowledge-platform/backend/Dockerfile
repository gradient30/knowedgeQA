FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.5

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* README.md ./
RUN poetry install --only main --no-root

COPY . .
RUN poetry install --only main

RUN mkdir -p uploads/images uploads/documents uploads/thumbnails logs

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
