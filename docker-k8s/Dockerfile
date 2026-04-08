# Multi-stage build for SCB Data Product Ingestion
FROM python:3.13-slim AS base

WORKDIR /app

# Install system dependencies and uv package manager
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

# Build stage - create virtual environment
FROM base AS builder

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

# Create venv and install dependencies into it using uv
# We'll compile requirements to a temporary file first
RUN /root/.local/bin/uv venv /opt/venv --python python3.13
RUN /root/.local/bin/uv pip compile pyproject.toml > /tmp/requirements.txt && \
    /root/.local/bin/uv pip install --python /opt/venv/bin/python -r /tmp/requirements.txt

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application source code
COPY python/scb_dp_cli.py .
COPY python/scb_types.py .
COPY python/scb_enums.py .
COPY python/scb_atlas/ ./scb_atlas/
COPY python/recreate_data_products_from_workbook.py .
COPY python/create_entities_with_pydantic.py .
COPY python/ingest_workbook_to_atlas.py .
COPY python/clean_up_atlas.py .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ATLAS_SERVER_HOST=localhost \
    ATLAS_SERVER_PORT=21000

# Create directory for mounted excel files
RUN mkdir -p /data/workbooks

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /opt/venv/bin/python -c "import sys; sys.exit(0)" || exit 1

# Set the entrypoint - use python from venv
ENTRYPOINT ["/opt/venv/bin/python", "scb_dp_cli.py", "ingest"]

# Default command - user should provide the workbook path
CMD ["/data/workbooks/metadata.xlsx"]

