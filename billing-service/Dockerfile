FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY ./billing-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./billing-service /app/billing_service
COPY ./shared /app/shared

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "billing_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
