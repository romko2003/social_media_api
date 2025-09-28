# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev musl-dev netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Collect static files (optional, for prod)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run server
CMD ["gunicorn", "socialapi.wsgi:application", "--bind", "0.0.0.0:8000"]
