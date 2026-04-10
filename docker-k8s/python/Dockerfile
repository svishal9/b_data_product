FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install only runtime dependencies needed by the catalog API.
RUN pip install --no-cache-dir \
    "fastapi>=0.116.1" \
    "uvicorn>=0.35.0" \
    "apache-atlas>=0.0.16" \
    "pydantic>=2.12.5" \
    "httpx>=0.28.1" \
    "pandas>=3.0.1" \
    "openpyxl>=3.1.5"

COPY scb_atlas ./scb_atlas

EXPOSE 8000

CMD ["uvicorn", "scb_atlas.api.catalog_api:app", "--host", "0.0.0.0", "--port", "8000"]

