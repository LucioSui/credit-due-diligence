FROM mcr.microsoft.com/devcontainers/python:3.12-bullseye

# Install system dependencies for weasyprint and other native modules
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libffi-dev \
        libpango-1.0-0 \
        libharfbuzz0b \
        libpangoft2-1.0-0 \
        libpangocairo-1.0-0 \
        fonts-noto-cjk \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Install backend Python dependencies (layer caching)
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Node.js will be installed via dev container feature

# Set working directory
WORKDIR /workspace
