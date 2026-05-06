FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project (backend + frontend for static files)
COPY backend/src ./backend/src
COPY frontend ./frontend

# Create static files directory
RUN mkdir -p /app/backend/src/staticfiles

# Expose port
EXPOSE 8000

# Set working directory to Django project
WORKDIR /app/backend/src

# Create entrypoint script
COPY docker-entrypoint.sh /app/

RUN chmod +x /app/docker-entrypoint.sh

# Run Django app (default)
ENTRYPOINT ["/app/docker-entrypoint.sh"]
