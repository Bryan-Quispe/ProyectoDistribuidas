# Arquitectura del Sistema de Microservicios

## Diagrama General

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTES/USUARIOS                        │
│                      (Web, Mobile, CLI)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     KONG API GATEWAY (8000)                      │
├─────────────────────────────────────────────────────────────────┤
│  Features:                                                       │
│  ✓ Rate Limiting (100 req/min)                                  │
│  ✓ JWT Validation                                               │
│  ✓ CORS                                                          │
│  ✓ Request Logging                                              │
│  ✓ Load Balancing                                               │
│  ✓ Request/Response Transformation                              │
└────────────────┬──────┬──────────┬────────────┬──────────────┬──┘
                 │      │          │            │              │
        ┌────────▼─┐ ┌──▼────────┐ ┌──▼───┐ ┌──▼────┐ ┌───────▼─┐
        │   Auth   │ │  Pedidos  │ │Fleet │ │Billing│ │ Health  │
        │ Service  │ │ Service   │ │Svc   │ │Svc    │ │ Checks  │
        │  :8001   │ │  :8002    │ │:8003 │ │ :8004 │ │         │
        └────┬─────┘ └──┬────────┘ └──┬───┘ └──┬────┘ └─────────┘
             │          │             │        │
             └──────────┴─────────────┴────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    ┌─────────┐   ┌─────────┐   ┌────────────┐
    │PostgreSQL├───┤ SQLAlchemy ORM   │
    │Database │   │   (ACID)         │
    │         │   │                   │
    │ Users  │   │ Pedidos           │
    │ Tokens │   │ Repartidores      │
    │ Pedidos│   │ Vehículos         │
    │ Facturas   │ Facturas          │
    └─────────┘   └────────────────┘
```

## Componentes Principales

### 1. API Gateway - Kong

**Responsabilidades:**
- Enrutamiento inteligente de requests
- Autenticación JWT en rutas protegidas
- Rate limiting por cliente
- CORS handling
- Logging centralizado
- Health checks de servicios

**Puertos:**
- 8000: Proxy (clientes)
- 8001: Admin API (configuración)
- 8443: HTTPS (futuro)

**Plugins Configurados:**
```
- rate-limiting: 100 req/min por IP
- jwt: Validación de tokens en /api/pedidos, /api/fleet, /api/billing
- cors: Todas las orígenes permitidas
- request-transformer: Headers personalizados
```

### 2. AuthService (Puerto 8001)

**Base de Datos:**
- Tabla `users`: email, username, password_hash, role, is_active
- Tabla `token_blacklist`: tokens revocados

**Endpoints:**
```
POST   /api/auth/register        → Crear usuario
POST   /api/auth/login           → Autenticar (JWT)
POST   /api/auth/token/refresh   → Renovar token
POST   /api/auth/token/revoke    → Revocar token
GET    /api/auth/me              → Información actual
```

**Roles:**
- ADMIN: Acceso total
- SUPERVISOR: Gestión de repartidores y pedidos
- CLIENTE: Crear pedidos, ver sus facturas
- REPARTIDOR: Ver entregas asignadas

**Seguridad:**
- Contraseñas hasheadas con bcrypt
- JWT con expiración (30 min access, 7 días refresh)
- Token blacklist para revocación inmediata

### 3. PedidoService (Puerto 8002)

**Base de Datos:**
```sql
Tabla: pedidos
- id (UUID)
- numero_pedido (único)
- cliente_id (FK)
- repartidor_id (FK, nullable)
- estado (enum: RECIBIDO, CONFIRMADO, EN_PREPARACION, 
         LISTO_PARA_ENTREGA, EN_RUTA, ENTREGADO, CANCELADO)
- tipo_entrega (enum: DOMICILIO, PUNTO_RETIRO, LOCKER)
- direccion, ciudad, codigo_postal
- latitud, longitud (geolocalización)
- peso_kg, valor_declarado
- cancelled_at (para cancelación lógica)
- created_at, updated_at, cancelled_at
```

**Endpoints:**
```
POST   /api/pedidos                → Crear pedido
GET    /api/pedidos                → Listar (del cliente actual)
GET    /api/pedidos/{id}           → Detalle
PATCH  /api/pedidos/{id}           → Actualizar estado (SUPERVISOR)
DELETE /api/pedidos/{id}           → Cancelar (cliente)
```

**Validaciones:**
- Ciudad en cobertura (Bogotá, Medellín, Cali, Barranquilla, Cartagena)
- Tipo de entrega válido
- Geolocalización dentro de cobertura
- Peso mínimo 0.1 kg
- Solo supervisores pueden cambiar estado y asignar repartidor

**Transacciones ACID:**
- Cada operación es atómica
- Cambios de estado garantizados
- Consistencia de datos asegurada

### 4. FleetService (Puerto 8003)

**Base de Datos:**
```sql
Tabla: repartidores
- id (UUID)
- nombre, email, telefono
- estado (enum)
- latitud, longitud, ultima_ubicacion
- calificacion_promedio
- entregas_completadas
- is_active

Tabla: vehiculos
- id (UUID)
- repartidor_id (FK)
- placa (única)
- tipo (MOTO, CARRO, CAMION, BICICLETA)
- marca, modelo, anio
- capacidad_kg, volumen_m3
- estado
- is_active
```

**Endpoints:**
```
POST   /api/fleet/repartidores           → Crear repartidor
GET    /api/fleet/repartidores           → Listar
GET    /api/fleet/repartidores/{id}      → Detalle
PATCH  /api/fleet/repartidores/{id}      → Actualizar ubicación/estado
POST   /api/fleet/vehiculos              → Crear vehículo
GET    /api/fleet/vehiculos/{id}         → Detalle vehículo
```

**Estados del Repartidor:**
- DISPONIBLE: Listo para entregas
- EN_RUTA: Entregando
- MANTENIMIENTO: Fuera de servicio
- INACTIVO: Dado de baja

### 5. BillingService (Puerto 8004)

**Base de Datos:**
```sql
Tabla: facturas
- id (UUID)
- numero_factura (única)
- pedido_id (FK)
- cliente_id (FK)
- tarifa_base, tarifa_distancia, tarifa_peso
- descuento, total, impuesto, total_final
- estado (enum: BORRADOR, ENVIADA, PAGADA, VENCIDA, CANCELADA)
- concepto (descripción)
- fecha_emision, fecha_vencimiento, fecha_pago
```

**Cálculos:**
```
Subtotal = tarifa_base + tarifa_distancia + tarifa_peso - descuento
IVA (19%) = Subtotal * 0.19
Total Final = Subtotal + IVA
```

**Endpoints:**
```
POST   /api/billing                 → Crear factura (BORRADOR)
GET    /api/billing                 → Listar facturas cliente
GET    /api/billing/{id}            → Detalle factura
PATCH  /api/billing/{id}            → Actualizar (solo BORRADOR)
POST   /api/billing/{id}/enviar     → Cambiar a ENVIADA
```

**Estados de Factura:**
- BORRADOR: Editable, no enviada
- ENVIADA: Enviada al cliente
- PAGADA: Pagada
- VENCIDA: Expirada sin pago
- CANCELADA: Anulada

## Flujos Principales

### 1. Flujo de Registro y Autenticación

```
Cliente
   │
   ├─→ POST /api/auth/register
   │         ├─ Validar email único
   │         ├─ Validar username único
   │         ├─ Hash contraseña con bcrypt
   │         └─ Crear usuario con rol CLIENTE
   │
   ├─→ POST /api/auth/login
   │         ├─ Validar credenciales
   │         ├─ Generar JWT (30 min)
   │         ├─ Generar refresh token (7 días)
   │         └─ Retornar tokens
   │
   └─→ Usar token en Authorization header
```

### 2. Flujo de Creación de Pedido

```
Cliente autenticado
   │
   ├─→ POST /api/pedidos
   │         ├─ Kong: Validar JWT
   │         ├─ PedidoService:
   │         │  ├─ Validar ciudad en cobertura
   │         │  ├─ Validar geolocalización
   │         │  ├─ Crear registro en BD (ACID)
   │         │  └─ Estado: RECIBIDO
   │         │
   │         └─ Respuesta con número_pedido
   │
   └─→ Supervisor consulta en tiempo real
       ├─→ GET /api/pedidos/{id}
       │    └─ Estado: RECIBIDO
       │
       └─→ PATCH /api/pedidos/{id}
            ├─ Cambiar estado a CONFIRMADO
            ├─ Asignar repartidor_id
            └─ Crear factura automáticamente
```

### 3. Flujo de Facturación

```
Supervisor asigna pedido
   │
   ├─→ Crear factura automática o manual
   │    ├─ Tarifa base: $10,000
   │    ├─ Tarifa distancia: $5,000
   │    ├─ Tarifa peso: $2,000
   │    ├─ Descuento: $1,000
   │    ├─ IVA (19%): $2,736
   │    └─ Total: $17,736
   │
   ├─→ Estado inicial: BORRADOR (editable)
   │
   └─→ Cliente paga
       ├─ Cambiar estado a PAGADA
       ├─ Registrar fecha_pago
       └─ Notificar
```

## Seguridad

### Niveles de Autenticación

1. **Sin autenticación:**
   - POST /api/auth/register
   - POST /api/auth/login

2. **Con JWT (cualquier rol):**
   - GET /api/auth/me

3. **Solo CLIENTE:**
   - POST /api/pedidos
   - GET /api/pedidos (propios)
   - DELETE /api/pedidos/{id}

4. **Solo SUPERVISOR/ADMIN:**
   - PATCH /api/pedidos/{id}
   - POST /api/fleet/repartidores
   - POST /api/fleet/vehiculos

### Validaciones

- **Schema Validation**: Pydantic en entrada
- **Business Logic Validation**: Cobertura geográfica, estados válidos
- **Data Integrity**: Constraints SQL + SQLAlchemy
- **Authorization**: Verificación de rol en rutas protegidas

## Performance y Escalabilidad

### Optimizaciones Actuales

- Connection pooling a BD
- Índices en búsquedas frecuentes (email, username, numero_pedido)
- Rate limiting: 100 req/min por cliente
- Health checks de servicios
- Logging JSON para análisis

### Para Producción

```
Considerar:
- Caché con Redis
- Búsquedas full-text en Elasticsearch
- Message queue (RabbitMQ/Kafka) para operaciones asincrónicas
- Réplicas de BD
- Load balancing automático
- Circuit breaker entre servicios
- Distributed tracing (Jaeger)
```

## Monitoreo y Logging

### Logging Centralizado

Formato JSON con:
- Timestamp ISO 8601
- Service name
- Log level
- Message
- User ID (si aplica)
- Request path
- HTTP status code

### Endpoints de Salud

```
GET /health → {"status": "healthy", "service": "..."}
```

### Kong Admin

```
GET http://localhost:8001/status
GET http://localhost:8001/services
GET http://localhost:8001/routes
GET http://localhost:8001/plugins
```

## Datos de Ejemplo

### Ciudades Permitidas

```
- Bogotá (4.5°N a 4.9°N, 74.3°O a 73.8°O)
- Medellín (6.1°N a 6.3°N, 75.6°O a 75.4°O)
- Cali (3.3°N a 3.5°N, 76.6°O a 76.4°O)
- Barranquilla (10.9°N a 11.1°N, 74.8°O a 74.6°O)
- Cartagena (10.3°N a 10.5°N, 75.5°O a 75.3°O)
```

### Tipos de Entrega

```
- DOMICILIO: Entrega a domicilio
- PUNTO_RETIRO: Centro de distribución
- LOCKER: Casillero automatizado
```

### Estados de Pedido

```
RECIBIDO → CONFIRMADO → EN_PREPARACION → 
LISTO_PARA_ENTREGA → EN_RUTA → ENTREGADO

En cualquier momento puede pasar a CANCELADO
```

## Próximas Fases (Fase 2+)

- Tracking en tiempo real
- Notificaciones (Email, SMS, Push)
- Pagos integrados
- Reportes y analytics
- Mobile app
- Integraciones externas (Mapas, Pagos)
