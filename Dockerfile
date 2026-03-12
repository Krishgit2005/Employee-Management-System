FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for building some python packages if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Initialize the SQLite database
# Since it's created automatically by app.py on first run, we don't strictly need a script.
# But it's good practice to set proper permissions if a volume is mounted later.
RUN chmod 777 /app

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run with gunicorn in production ideally, but using flask run for simplicity here
CMD ["python", "app.py"]
