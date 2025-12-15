FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY ./pedido-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./pedido-service /app/pedido_service
COPY ./shared /app/shared

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para iniciar la aplicación
CMD ["uvicorn", "pedido_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
