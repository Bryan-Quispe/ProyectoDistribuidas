FROM python:3.11-slim

WORKDIR /app

# Instalar solo lo necesario
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY ./auth-service/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación (empaquetado con nombre de módulo)
COPY ./auth-service /app/auth_service
COPY ./shared /app/shared

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para iniciar la aplicación
CMD ["uvicorn", "auth_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
