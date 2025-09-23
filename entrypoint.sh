#!/usr/bin/env bash
set -e

if [ -n "$DATABASE_URL" ]; then
python - <<'PY'
import os, time, sys
import traceback
url = os.environ.get("DATABASE_URL", "")
# psycopg expects postgresql://; normalize if postgres:// provided
if url.startswith("postgres://"):
    url = "postgresql://" + url[len("postgres://"):]
    os.environ["DATABASE_URL"] = url

# Only try to connect for postgres URLs
if url.startswith("postgresql://"):
    try:
        import psycopg
    except Exception as e:
        print("psycopg not installed yet? Proceeding without explicit wait:", e)
        sys.exit(0)
    max_attempts = 30
    for attempt in range(1, max_attempts + 1):
        try:
            with psycopg.connect(url, connect_timeout=3) as conn:
                print("Database is available.")
                break
        except Exception as e:
            print(f"DB not ready ({e!s}); retry {attempt}/{max_attempts}")
            time.sleep(2)
    else:
        print("Database never became available; exiting.")
        sys.exit(1)
PY
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

exec "$@"
