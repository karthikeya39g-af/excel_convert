# Use lightweight official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if any are needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose server port (defaulting to 5000 but overridden by Render/Heroku $PORT)
EXPOSE 5000

# Run using production gunicorn server
CMD gunicorn app:app --bind 0.0.0.0:${PORT:-5000}
