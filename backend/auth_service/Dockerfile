# Dockerfile for auth_service
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies that might be needed by psycopg2 or other libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# The auth_service has its code in a 'src' subdirectory and a .env file at the root of auth_service
COPY src/ src/
COPY .env .env

# Expose the port the app runs on (as defined in src/main.py, defaults to 5001)
EXPOSE 5001

# Command to run the application using gunicorn for production (recommended)
# Or python src/main.py for development
# Ensure Gunicorn is in requirements.txt if used here
# For now, using the development server as per main.py
CMD ["python", "src/main.py"]

