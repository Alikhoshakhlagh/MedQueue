FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN useradd -m appuser
USER appuser

RUN python manage.py collectstatic --noinput || true

ENV DJANGO_SETTINGS_MODULE=MedQueue.settings

CMD gunicorn MedQueue.wsgi:application --bind 0.0.0.0:8000
