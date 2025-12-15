# Guía de Instalación Rápida

## 1. Requisitos Previos

- **Docker Desktop** instalado y ejecutándose
- **Git** para control de versiones
- **curl** o **Postman** para pruebas
- Puerto 8000 disponible (Kong)

## 2. Clonar o descargar el proyecto

```bash
cd c:\Users\rquis\OneDrive\Escritorio\7mo-Semestre\Distribuidas\Parcial 2\Proyecto
```

## 3. Iniciar servicios con Docker Compose

```bash
docker-compose up -d
```

**Esto levanta:**
- PostgreSQL (Puerto 5432)
- AuthService (Puerto 8001)
- PedidoService (Puerto 8002)
- FleetService (Puerto 8003)
- BillingService (Puerto 8004)
- Kong API Gateway (Puerto 8000)
- Konga UI (Puerto 1337)

## 4. Esperar a que todos estén listos (2-3 minutos)

```bash
# Verificar logs
docker-compose logs -f

# Salir: Ctrl+C
```

## 5. Configurar Kong

### Opción A: Python (Recomendado)

```bash
cd kong-config
pip install requests
python configure_kong.py
```

### Opción B: Script Bash

```bash
bash kong-config/setup-kong.sh
```

## 6. Verificar que todo funciona

```bash
# Health check de Kong
curl http://localhost:8001/status

# Health checks de servicios
curl http://localhost:8001/api/auth/health
curl http://localhost:8002/api/pedidos/health
curl http://localhost:8003/api/fleet/health
curl http://localhost:8004/api/billing/health
```

**Respuesta esperada:**
```json
{"status": "healthy", "service": "auth-service"}
```

## 7. Pruebas Rápidas

### Con Bash (Linux/Mac)

```bash
bash test-services.sh
```

### Con Postman

1. Abrir Postman
2. File → Import → Seleccionar `Microservicios.postman_collection.json`
3. Ejecutar requests en orden

### Con curl manual

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "test1",
    "password": "password123",
    "role": "CLIENTE"
  }'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test1",
    "password": "password123"
  }'

# 3. Crear pedido (reemplazar TOKEN con el access_token)
curl -X POST http://localhost:8000/api/pedidos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "tipo_entrega": "DOMICILIO",
    "direccion": "Calle 123",
    "ciudad": "Bogotá",
    "codigo_postal": "110111",
    "peso_kg": 2.5,
    "valor_declarado": 100000,
    "destinatario_nombre": "Juan"
  }'
```

## 8. Acceso a Interfaces

- **Kong Admin API**: http://localhost:8001
- **Konga UI**: http://localhost:1337
- **API Gateway**: http://localhost:8000

### Crear conexión en Konga

1. Ir a http://localhost:1337
2. Admin API Connection: http://kong:8001
3. Name: Kong (cualquier nombre)
4. Guardar

## 9. Ver Documentación OpenAPI

Cada servicio expone Swagger en:
- Auth: http://localhost:8001/swagger-ui.html
- Pedidos: http://localhost:8002/swagger-ui.html
- Fleet: http://localhost:8003/swagger-ui.html
- Billing: http://localhost:8004/swagger-ui.html

## 10. Logs en Tiempo Real

```bash
# Todos los servicios
docker-compose logs -f

# Un servicio específico
docker-compose logs -f auth-service
docker-compose logs -f pedido-service
docker-compose logs -f fleet-service
docker-compose logs -f billing-service
docker-compose logs -f kong
```

## 11. Parar servicios

```bash
# Sin eliminar volúmenes
docker-compose down

# Eliminando todo (BD incluida)
docker-compose down -v
```

## 12. Troubleshooting

### Puerto 8000 en uso

```bash
# Encontrar proceso
netstat -ano | findstr :8000

# Matar proceso (Windows PowerShell)
taskkill /PID <PID> /F
```

### Kong no enruta correctamente

```bash
# Reiniciar Kong
docker-compose restart kong

# Verificar servicios
curl http://localhost:8001/services

# Verificar rutas
curl http://localhost:8001/routes
```

### Base de datos corrupta

```bash
# Limpiar volúmenes
docker-compose down -v
docker-compose up -d

# Esperar 30 segundos
sleep 30

# Reconfigurar Kong
python kong-config/configure_kong.py
```

### Token JWT inválido

- Verificar formato: `Authorization: Bearer <token>`
- El token expira en 30 minutos
- Usar refresh token: POST /api/auth/token/refresh
- Decodificar token en https://jwt.io para verificar claims

## 13. Estructura de Carpetas

```
Proyecto/
├── auth-service/          # Servicio de autenticación
├── pedido-service/        # Servicio de pedidos
├── fleet-service/         # Servicio de flota
├── billing-service/       # Servicio de facturación
├── shared/               # Código compartido (JWT, BD, logging)
├── kong-config/          # Configuración de Kong
├── docker-compose.yml    # Orquestación de servicios
├── README.md             # Documentación completa
├── QUICKSTART.md         # Esta guía
├── Microservicios.postman_collection.json
└── test-services.sh      # Script de pruebas
```

## 14. Siguiente Paso

Revisar [README.md](README.md) para:
- Documentación detallada de cada servicio
- Ejemplos de uso de API
- Explicación de validaciones
- Criterios de aceptación

## Contacto

Para dudas o problemas, revisar los logs de los servicios:

```bash
docker-compose logs <nombre-servicio>
```

¡Éxito en tu implementación! 🚀
