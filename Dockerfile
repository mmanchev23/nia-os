FROM python:3.14-slim

ENV PATH="/nia-os/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /nia-os

COPY pyproject.toml uv.lock ./

RUN --mount=type=bind,from=ghcr.io/astral-sh/uv:latest,source=/uv,target=/bin/uv \
    uv sync --compile --frozen --no-dev --no-install-project

COPY . .

RUN python manage.py compilemessages

RUN python manage.py tailwind setup \
    && python manage.py tailwind build \
    && python manage.py collectstatic --noinput \
    && rm -rf .django_tailwind_cli static pyproject.toml uv.lock

RUN chown -R 1000:1000 /nia-os

USER 1000

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
