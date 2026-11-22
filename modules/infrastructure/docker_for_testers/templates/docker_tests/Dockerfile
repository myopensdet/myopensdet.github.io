# Template from myOpenSDET: https://myopensdet.github.io/
# The test runner: your tests and their packages in one image.
#
#   docker build -t books-tests:local .                      build it
#   docker run --rm -e API_URL=http://... books-tests:local  run the tests
#
# docker-compose.yml builds and runs it for you: docker compose run --rm tests
FROM python:3.13.18-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /tests

# Packages first: this layer is reused until requirements.txt changes.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run as a normal user, never as root. reports/ is where pytest writes its files.
RUN useradd --create-home --uid 10001 tester \
    && mkdir reports \
    && chown tester:tester reports

# Your tests change most often, so they are copied last.
COPY pytest.ini .
COPY tests ./tests
USER tester

# The container runs pytest. Anything after the image name is passed to pytest.
# No cache: it is thrown away with the container, and /tests is read-only for tester.
ENTRYPOINT ["python", "-m", "pytest", "-p", "no:cacheprovider"]
