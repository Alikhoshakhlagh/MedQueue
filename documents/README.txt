HI
# How to run this project
## Run with Docker

1) Create `.env` :
        # Django
        DEBUG=True
        SECRET_KEY=change-me

        DATABASE_URL=postgresql://medqueue:medqueue@db:5432/medqueue

        ALLOWED_HOSTS=localhost,127.0.0.1
        CSRF_TRUSTED_ORIGINS=http://localhost:8000

        #OTP option's
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
        EMAIL_HOST="smtp.gmail.com"
        EMAIL_PORT=587
        EMAIL_USE_TLS=True
        EMAIL_HOST_USER=<EMAIL>
        EMAIL_HOST_PASSWORD=<PASS>

        For test only :
        EMAIL_HOST_USER=nslbsknn9649@gmail.com
        EMAIL_HOST_PASSWORD=eslw vtyi vhsn zrwh

2) Build & start:
    docker compose up --build -d

    or if you have Docker Compose v1:
        docker-compose up --build -d

3) Apply migrations:
    docker compose exec web python manage.py migrate
    (optional) docker compose exec web python manage.py createsuperuser
    (optional) docker compose exec web python manage.py collectstatic --noinput


4) Open the app:
    - http://localhost:8000
    - http://127.0.0.1:8000

5) Stop:
    docker compose down

#glhf
