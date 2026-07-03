# 🐳 استفاده از Docker برای Deployment

اگر مایل به استفاده از Docker هستید، می‌توانید از این راهنما استفاده کنید.

## Dockerfile

```dockerfile
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=pouriabaghban3.settings_production

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "pouriabaghban3.wsgi:application"]
```

## docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: pouriabaghban3
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: >
      sh -c "python manage.py migrate --settings=pouriabaghban3.settings_production &&
             gunicorn --bind 0.0.0.0:8000 --workers 3 pouriabaghban3.wsgi:application"
    environment:
      DEBUG: "False"
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS}
      DATABASE_URL: postgresql://appuser:${DB_PASSWORD}@db:5432/pouriabaghban3
      REDIS_URL: redis://redis:6379/0
      EMAIL_HOST_USER: ${EMAIL_HOST_USER}
      EMAIL_HOST_PASSWORD: ${EMAIL_HOST_PASSWORD}
    volumes:
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./staticfiles:/app/staticfiles:ro
      - ./media:/app/media:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web

volumes:
  postgres_data:
```

## پیکربندی .env

```env
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_PASSWORD=your-secure-password
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## دستورات Docker

```bash
# ساخت images
docker-compose build

# شروع services
docker-compose up -d

# مشاهده logs
docker-compose logs -f web

# اجرای دستورات Django
docker-compose exec web python manage.py createsuperuser --settings=pouriabaghban3.settings_production

# متوقف کردن
docker-compose down
```

## یادداشت‌های اضافی

- Docker به راحتی deployment را امکان‌پذیر می‌کند
- تمام وابستگی‌ها در container ایزوله‌شده‌اند
- scaling آسان‌تر است
- Production-ready است
