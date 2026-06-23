#!/bin/sh

# Skip DB check - just wait a bit for MySQL to be ready
echo "Giving database time to be ready..."
sleep 5

# Run migrations before starting the service.
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files (optional)
if [ "$SKIP_COLLECTSTATIC" != "True" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput 2>&1 || true
else
    echo "Skipping collectstatic..."
fi

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created')
else:
    print('Superuser already exists')
"
fi

if [ "$LOAD_DEMO_DATA" = "True" ]; then
    echo "Loading demo data..."
    python data.py
fi

# Run the appropriate service based on CELERY_COMMAND env var
if [ "$CELERY_COMMAND" = "worker" ]; then
    echo "Starting Celery Worker..."
    exec celery -A src worker -l info
elif [ "$CELERY_COMMAND" = "beat" ]; then
    echo "Starting Celery Beat..."
    exec celery -A src beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
else
    echo "Starting Django Server..."
    exec gunicorn src.wsgi:application --bind 0.0.0.0:${PORT:-8000} --log-file -
fi
