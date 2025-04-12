
FROM python:3.10-alpine

WORKDIR /app

# Install Docker client and dependencies (Alpine version)
RUN apk add --no-cache \
    docker \
    curl \
    gcc \
    libc-dev \
    linux-headers

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app .

# Run the application
CMD ["python", "executor.py"]
