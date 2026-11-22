# ==========================================
# Multi-Stage Dockerfile for ResumeForge AI
# Full-Stack Deployment: React Frontend + FastAPI Backend + Tectonic LaTeX
# ==========================================

# Stage 1: Build Frontend Assets
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Runtime with Tectonic LaTeX
FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tar \
    fontconfig \
    libfontconfig1 \
    libgraphite2-3 \
    libharfbuzz0b \
    && rm -rf /var/lib/apt/lists/*

# Download and install statically-linked Tectonic (zero shared library dependencies)
RUN curl -fsSL -o /tmp/tectonic.tar.gz "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-x86_64-unknown-linux-musl.tar.gz" && \
    tar -xzf /tmp/tectonic.tar.gz -C /usr/local/bin/ && \
    chmod +x /usr/local/bin/tectonic && \
    rm -f /tmp/tectonic.tar.gz && \
    /usr/local/bin/tectonic --version

# Install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend application source
COPY backend/ ./backend/

# Copy compiled frontend distribution from Stage 1 into backend static path
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create storage directory structure
RUN mkdir -p /app/backend/storage/pdfs \
             /app/backend/storage/tex \
             /app/backend/storage/docx \
             /app/backend/storage/db \
             /app/backend/storage/photos

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
