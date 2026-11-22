# Template from myOpenSDET: https://myopensdet.github.io/
# The app under test: a small book API. docker compose builds it as books-api:local.
# The base image is pinned to a version and a digest, so every build starts the same.
FROM python:3.13.18-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run as a normal user, never as root.
RUN useradd --create-home --uid 10001 app
COPY main.py .
USER app

EXPOSE 8000
# 0.0.0.0 inside the container. docker-compose.yml keeps the port on 127.0.0.1 outside it.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
