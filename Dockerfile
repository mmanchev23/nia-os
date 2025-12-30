FROM python:3.14-slim

RUN apt-get update && apt-get install -y gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /nia-os

COPY pyproject.toml .

RUN pip install uv && uv pip install -r pyproject.toml --system -n

COPY . .

RUN python manage.py compilemessages

RUN python manage.py tailwind setup \
    && python manage.py tailwind build \
    && python manage.py collectstatic --noinput \
    && rm -rf .django_tailwind_cli static pyproject.toml

EXPOSE 80

CMD ["daphne", "-b", "0.0.0.0", "-p", "80", "config.asgi:application"]
