# Dockerfile for ai_services_api
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
# The ai_services_api has its code in a 'src' subdirectory and a .env file at the root
COPY src/ src/
COPY .env .env # .env file might contain defaults, but Cloud Run will use environment variables set in service.yaml

# Expose the port the app runs on (as defined in src/main.py, defaults to 5002)
EXPOSE 5002

# Command to run the application using gunicorn for production (recommended)
# Ensure Gunicorn is in requirements.txt if used here. For now, using Flask's dev server.
# For production, you would typically add gunicorn to requirements.txt and use a command like:
# CMD ["gunicorn", "--bind", "0.0.0.0:5002", "src.main:app"]
CMD ["python", "src/main.py"]

