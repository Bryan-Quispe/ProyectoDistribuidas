# Sistema de Microservicios para Distribución de Paquetes

Arquitectura de microservicios basada en Python (FastAPI) con Kong como API Gateway.

## Componentes

### Microservicios
- **AuthService** (Puerto 8001): Autenticación, registro y gestión de tokens JWT
- **PedidoService** (Puerto 8002): Gestión de pedidos (CRUD, PATCH)
- **FleetService** (Puerto 8003): Gestión de repartidores y vehículos
- **BillingService** (Puerto 8004): Facturación y cálculo de tarifas

### Infraestructura
- **Kong API Gateway** (Puerto 8000): Enrutamiento, rate limiting, JWT validation
- **PostgreSQL**: Base de datos compartida
- **Konga** (Puerto 1337): Interfaz admin para Kong

## Requisitos Previos

- Docker & Docker Compose
- Python 3.11+ (para desarrollo local)
- curl o Postman

## Iniciación Rápida

### 1. Levantar servicios con Docker Compose

```bash
docker-compose up -d
```

Esto iniciará:
- PostgreSQL
- AuthService, PedidoService, FleetService, BillingService
- Kong y su base de datos
- Konga UI

### 2. Esperar a que todos los servicios estén listos

```bash
# Verificar health de Kong
curl http://localhost:8001/status

# Verificar cada servicio
curl http://localhost:8001/api/auth/health
curl http://localhost:8002/api/pedidos/health
curl http://localhost:8003/api/fleet/health
curl http://localhost:8004/api/billing/health
```

### 3. Configurar Kong

```bash
# Opción 1: Con Python
cd kong-config
pip install requests
python configure_kong.py

# Opción 2: Con script bash
bash kong-config/setup-kong.sh
```

## Flujo de Uso

### 1. Registro de Usuario

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cliente@example.com",
    "username": "cliente1",
    "password": "password123",
    "full_name": "Juan Pérez",
    "role": "CLIENTE"
  }'
```

**Respuesta:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "cliente@example.com",
  "username": "cliente1",
  "full_name": "Juan Pérez",
  "role": "CLIENTE",
  "is_active": true,
  "created_at": "2025-12-15T10:30:00"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "cliente1",
    "password": "password123"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Crear Pedido

```bash
curl -X POST http://localhost:8000/api/pedidos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "tipo_entrega": "DOMICILIO",
    "direccion": "Calle Principal 123, Apt 4B",
    "ciudad": "Bogotá",
    "codigo_postal": "110111",
    "latitud": 4.7110,
    "longitud": -74.0721,
    "descripcion": "Paquete con documentos",
    "peso_kg": 2.5,
    "valor_declarado": 100000,
    "destinatario_nombre": "Juan Pérez",
    "destinatario_telefono": "+573001234567",
    "destinatario_email": "juan@example.com"
  }'
```

**Estado esperado: RECIBIDO**

### 4. Consultar Pedido (Como Supervisor)

Registrar primero como SUPERVISOR:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "supervisor@example.com",
    "username": "supervisor1",
    "password": "password123",
    "full_name": "Supervisor",
    "role": "SUPERVISOR"
  }'
```

Login y obtener token, luego:

```bash
curl -X GET http://localhost:8000/api/pedidos/{pedido_id} \
  -H "Authorization: Bearer <supervisor_token>"
```

## Estructura del Proyecto

```
.
├── auth-service/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   ├── service.py
│   ├── requirements.txt
│   └── Dockerfile
├── pedido-service/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   ├── service.py
│   ├── requirements.txt
│   └── Dockerfile
├── fleet-service/
├── billing-service/
├── shared/
│   ├── jwt_utils.py
│   ├── logger.py
│   └── database.py
├── kong-config/
│   ├── configure_kong.py
│   └── setup-kong.sh
└── docker-compose.yml
```

## Validaciones y Características

### AuthService
✓ Validación de email (Pydantic EmailStr)
✓ Contraseñas hasheadas con bcrypt
✓ JWT con expiración de 30 minutos
✓ Refresh token válido por 7 días
✓ Token blacklist para revocación

### PedidoService
✓ Validación de cobertura geográfica
✓ Estados: RECIBIDO, CONFIRMADO, EN_PREPARACION, LISTO_PARA_ENTREGA, EN_RUTA, ENTREGADO, CANCELADO
✓ Cancelación lógica con timestamp
✓ Validación de tipo de entrega
✓ Transacciones ACID con SQLAlchemy

### FleetService
✓ Gestión de repartidores
✓ Gestión de vehículos con capacidades
✓ Estados: DISPONIBLE, EN_RUTA, MANTENIMIENTO, INACTIVO
✓ Seguimiento de ubicación (latitud/longitud)

### BillingService
✓ Cálculo automático de IVA (19%)
✓ Subtotal con tarifa base + distancia + peso - descuento
✓ Estados de factura: BORRADOR, ENVIADA, PAGADA, VENCIDA, CANCELADA
✓ Validación de que solo se editen facturas en BORRADOR

## Kong - Rate Limiting y JWT

- **Rate Limiting**: 100 requests/minuto por cliente
- **JWT Validation**: Requerido en rutas protegidas (/api/pedidos, /api/fleet, /api/billing)
- **CORS**: Habilitado para todas las orígenes
- **Logging**: Headers con X-Request-ID y X-Forwarded-For

## Documentación OpenAPI

Cada servicio tiene documentación Swagger:

- Auth: http://localhost:8001/swagger-ui.html
- Pedidos: http://localhost:8002/swagger-ui.html
- Fleet: http://localhost:8003/swagger-ui.html
- Billing: http://localhost:8004/swagger-ui.html

## Admin Kong

Acceder a Konga UI: http://localhost:1337

Crear conexión a Kong Admin:
- Host: kong
- Port: 8001

## Solución de Problemas

### Los servicios no se conectan a BD
```bash
# Verificar BD
docker-compose logs postgres

# Reiniciar todo
docker-compose down -v
docker-compose up -d
```

### Kong no enruta correctamente
```bash
# Verificar servicios en Kong
curl http://localhost:8001/services

# Verificar rutas
curl http://localhost:8001/routes

# Verificar plugins
curl http://localhost:8001/plugins
```

### Token JWT inválido
- Verificar que el token no haya expirado
- Usar refresh token: POST /api/auth/token/refresh
- Verificar formato: "Authorization: Bearer <token>"

## Criterio de Aceptación

✓ Un cliente autenticado puede crear un pedido urbano  
✓ Un supervisor puede consultarlo y ver su estado en RECIBIDO  
✓ Utilizando únicamente endpoints REST y el API Gateway Kong  
✓ Todas las operaciones son ACID  
✓ Validación de esquema implementada  
✓ Documentación OpenAPI 3.0 accesible  

## Variables de Entorno

```
JWT_SECRET=your-secret-key-change-in-production
DATABASE_URL=postgresql://admin:admin123@postgres:5432/microservices
SERVICE_NAME=<service-name>
```

## Contacto y Soporte

Para problemas o preguntas, revisar los logs:

```bash
docker-compose logs -f <service-name>
```
