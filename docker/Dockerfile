FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies file
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip

# Copy application code
COPY pokepipeline/ ./pokepipeline/
COPY migrations/ ./migrations/

# Copy README if it exists
COPY README.md* ./

# Install the package in editable mode
RUN pip install --no-cache-dir -e .[dev]

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Default command
CMD ["python", "-m", "pokepipeline.cli", "run"]

