FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    DATABASE_PATH=/app/data/skillswap.db

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Clean up any leftover malformed folders or local caches, and create a persistent data directory
RUN rm -rf "{templates,static" __pycache__ && \
    mkdir -p /app/data && \
    useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

# Initialize & seed DB (idempotent—won't wipe existing users) and launch Gunicorn
CMD ["sh", "-c", "python seed.py && exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 60 app:app"]