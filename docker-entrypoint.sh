#!/bin/sh

# Skip DB check - just wait a bit for MySQL to be ready
echo "Giving database time to be ready..."
sleep 5

# Try migrations but don't block
echo "Running migrations..."
python manage.py migrate --noinput 2>&1 || true

# Collect static files (optional)
if [ "$SKIP_COLLECTSTATIC" != "True" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput 2>&1 || true
else
    echo "Skipping collectstatic..."
fi

python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created')
else:
    print('Superuser already exists')
"

python data.py

# Run the appropriate service based on CELERY_COMMAND env var
if [ "$CELERY_COMMAND" = "worker" ]; then
    echo "Starting Celery Worker..."
    exec celery -A src worker -l info
elif [ "$CELERY_COMMAND" = "beat" ]; then
    echo "Starting Celery Beat..."
    exec celery -A src beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
else
    echo "Starting Django Server..."
    exec python manage.py runserver 0.0.0.0:8000
fi
