FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory with proper permissions
RUN mkdir -p /app/session_data && \
    chmod 777 /app/session_data

# Set environment variables
ENV PORT 8080
ENV ENVIRONMENT production
EXPOSE 8080

# Security: run as non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser /app
USER appuser

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run the application
CMD streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0
