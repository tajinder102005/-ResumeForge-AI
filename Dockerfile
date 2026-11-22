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

# Install system dependencies (universal packages without fragile versioned names)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tar \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# Download and install pre-built Tectonic binary for Linux x86_64
RUN curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh && \
    mv tectonic /usr/local/bin/tectonic && \
    chmod +x /usr/local/bin/tectonic

# Pre-warm Tectonic cache so all LaTeX packages, fonts, and TikZ engines are pre-downloaded during docker build
RUN python3 -c "tex = r'''\documentclass{article}\usepackage{geometry,xcolor,graphicx,tikz,enumitem,hyperref,lmodern,helvet}\usepackage[explicit]{titlesec}\begin{document}Warmup\end{document}'''; open('/tmp/warmup.tex', 'w').write(tex)" && \
    tectonic /tmp/warmup.tex && \
    rm -f /tmp/warmup.*

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
