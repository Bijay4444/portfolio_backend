FROM python:3.12-slim-bookworm

# work dir
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    DJANGO_SETTINGS_MODULE=config.settings.prod

# Runtime system deps for Pillow
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        zlib1g \
        libwebp7 \
    && rm -rf /var/lib/apt/lists/*

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# moving lock files into a dir not copied into runtime image
# trailing slash makes COPY create '/_lock/' automatically.
COPY pyproject.toml uv.lock /_lock/

# Synchronize dependencies.
# This layer is cached until uv.lock or pyproject.toml change
RUN --mount=type=cache,target=/root/.cache \
    cd /_lock && \
    uv sync \
    --frozen \
    --no-dev \
    --no-install-project

# copy project
COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Collect static files for whitenoise
RUN DJANGO_SECRET_KEY=build-placeholder DB_NAME=x DB_USER=x DB_PASSWORD=x DB_HOST=x \
    .venv/bin/python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# entrypoint
ENTRYPOINT [ "/entrypoint.sh" ]

# start gunicorn
CMD [".venv/bin/gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "120"]
