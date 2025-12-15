# Requisitos Técnicos - Cumplimiento Fase 1

## 1. Microservicios REST con Operaciones CRUD

### ✅ AuthService
**Endpoints implementados:**
- `POST /api/auth/register` - Crear usuario
- `POST /api/auth/login` - Autenticar usuario
- `POST /api/auth/token/refresh` - Renovar token JWT
- `POST /api/auth/token/revoke` - Revocar token (logout)
- `GET /api/auth/me` - Obtener usuario actual

**Persistencia:**
- ✅ Usuario: email, username, password_hash, full_name, role, is_active, created_at, updated_at, last_login
- ✅ TokenBlacklist: para revocación de tokens

**Roles:**
- ADMIN
- CLIENTE
- REPARTIDOR
- SUPERVISOR

---

### ✅ PedidoService
**Operaciones CRUD:**
- `POST /api/pedidos` - **CREATE** pedido
- `GET /api/pedidos` - **READ** lista de pedidos del cliente
- `GET /api/pedidos/{id}` - **READ** detalle de pedido
- `PATCH /api/pedidos/{id}` - **UPDATE** parcial (cambiar estado, asignar repartidor)
- `DELETE /api/pedidos/{id}` - **DELETE** lógico (cancelar pedido)

**Validaciones:**
- ✅ Tipo de entrega: DOMICILIO, PUNTO_RETIRO, LOCKER
- ✅ Cobertura geográfica: Bogotá, Medellín, Cali, Barranquilla, Cartagena
- ✅ Geolocalización dentro de rango permitido
- ✅ Peso mínimo 0.1 kg

**Estados:**
- RECIBIDO (inicial)
- CONFIRMADO
- EN_PREPARACION
- LISTO_PARA_ENTREGA
- EN_RUTA
- ENTREGADO (final)
- CANCELADO (lógicamente deletado)

---

### ✅ FleetService
**Operaciones:**
- `POST /api/fleet/repartidores` - Crear repartidor
- `GET /api/fleet/repartidores` - Listar repartidores
- `GET /api/fleet/repartidores/{id}` - Obtener repartidor
- `PATCH /api/fleet/repartidores/{id}` - Actualizar estado/ubicación
- `POST /api/fleet/vehiculos` - Crear vehículo
- `GET /api/fleet/vehiculos/{id}` - Obtener vehículo

**Gestión de Repartidores:**
- ✅ Alta de repartidores
- ✅ Baja lógica (is_active = false)
- ✅ Actualización de estado: DISPONIBLE, EN_RUTA, MANTENIMIENTO, INACTIVO
- ✅ Seguimiento de ubicación (latitud, longitud, última actualización)
- ✅ Calificación promedio
- ✅ Contador de entregas completadas

**Gestión de Vehículos:**
- ✅ Asignación a repartidor
- ✅ Tipos: MOTO, CARRO, CAMION, BICICLETA
- ✅ Capacidad (kg y volumen)
- ✅ Control de estado

---

### ✅ BillingService
**Operaciones:**
- `POST /api/billing` - Crear factura
- `GET /api/billing` - Listar facturas del cliente
- `GET /api/billing/{id}` - Obtener factura
- `PATCH /api/billing/{id}` - Actualizar factura (solo BORRADOR)
- `POST /api/billing/{id}/enviar` - Cambiar a ENVIADA

**Cálculo de Tarifa:**
- ✅ Tarifa base configurable
- ✅ Tarifa por distancia
- ✅ Tarifa por peso
- ✅ Descuentos
- ✅ IVA automático (19%)
- ✅ Fórmula: `Total = (Base + Distancia + Peso - Descuento) * (1 + IVA)`

**Generación de Factura:**
- ✅ Estado inicial: BORRADOR
- ✅ Editable mientras está en BORRADOR
- ✅ Número único de factura
- ✅ Fecha de emisión y vencimiento (30 días)
- ✅ Transición de estados: BORRADOR → ENVIADA → PAGADA/VENCIDA

---

## 2. API Gateway (Kong)

### ✅ Enrutamiento por Prefijo de Ruta

```
/api/auth/**          → AuthService:8000
/api/pedidos/**       → PedidoService:8000
/api/fleet/**         → FleetService:8000
/api/billing/**       → BillingService:8000
```

**Configuración en Kong:**
```bash
# 4 servicios creados en Kong
curl http://localhost:8001/services
# Retorna todos los servicios registrados

# ~20 rutas configuradas
curl http://localhost:8001/routes
# Mapeo de paths a servicios
```

### ✅ Validación de JWT

**Implementación:**
- Kong valida JWT en Authorization header
- Formato: `Authorization: Bearer <token>`
- Validación antes de llegar al servicio
- Rechazo con 401 si no hay token
- Rechazo con 403 si token es inválido

**Rutas protegidas:**
```
POST   /api/pedidos              → Requiere JWT
GET    /api/pedidos              → Requiere JWT
GET    /api/pedidos/{id}         → Requiere JWT
PATCH  /api/pedidos/{id}         → Requiere JWT + SUPERVISOR
DELETE /api/pedidos/{id}         → Requiere JWT
POST   /api/fleet/repartidores   → Requiere JWT + SUPERVISOR
```

**Rutas públicas:**
```
POST /api/auth/register          → Sin autenticación
POST /api/auth/login             → Sin autenticación
```

### ✅ Rate Limiting por Cliente

**Configuración:**
- Límite: 100 requests/minuto por IP
- Plugin: `rate-limiting` en Kong
- Policy: `local`

**Respuesta cuando se excede:**
```
HTTP 429 Too Many Requests
X-RateLimit-Limit-Minute: 100
X-RateLimit-Remaining-Minute: 0
```

### ✅ Logging Centralizado

**Información registrada:**
- ✅ Método HTTP (GET, POST, PATCH, DELETE)
- ✅ URI completa
- ✅ Código de respuesta HTTP
- ✅ User ID (si está autenticado)
- ✅ Timestamp ISO 8601
- ✅ Service name

**Formato JSON:**
```json
{
  "timestamp": "2025-12-15T14:35:00.123456Z",
  "service": "pedido-service",
  "level": "INFO",
  "message": "HTTP POST /api/pedidos - Status: 201",
  "path": "pedido_service/routes.py",
  "line": 45,
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Acceso a logs:**
```bash
docker-compose logs -f <service-name>
docker-compose logs -f kong
```

---

## 3. Requisitos Técnicos Mínimos

### ✅ Transacciones ACID

**Implementación en SQLAlchemy:**

```python
@transactional
def crear_pedido(db: Session, cliente_id: str, pedido_data):
    # Atomicidad: Todo se crea o nada
    pedido = Pedido(...dados...)
    db.add(pedido)
    db.commit()  # Punto de no retorno
    return pedido
```

**Propiedades garantizadas:**
- **Atomicidad**: Crear usuario + hash contraseña + guardar BD = todo o nada
- **Consistencia**: Validaciones antes de guardar (cobertura, tipo entrega, etc.)
- **Aislamiento**: SQLAlchemy maneja niveles de transacción
- **Durabilidad**: PostgreSQL persiste en disco

**Ejemplos transaccionales:**
- Crear pedido: validación + inserción + confirmación
- Login: búsqueda + validación + actualización last_login
- Cambiar estado: verificación de transición válida + actualización
- Crear factura: cálculos + inserción + vinculación a pedido

### ✅ Validación de Esquema

**Framework:** Pydantic v2

**Ejemplos de validaciones:**

**1. Email válido:**
```python
class UserRegister(BaseModel):
    email: EmailStr  # Valida formato email
```

**2. Rangos numéricos:**
```python
class CreatePedidoRequest(BaseModel):
    peso_kg: float = Field(..., ge=0.1)  # >= 0.1
    valor_declarado: float = Field(..., ge=0)  # >= 0
```

**3. Longitud de strings:**
```python
username: str = Field(..., min_length=3, max_length=100)
direccion: str = Field(..., min_length=5, max_length=500)
```

**4. Enums:**
```python
class TipoEntregaEnum(str, Enum):
    DOMICILIO = "DOMICILIO"
    PUNTO_RETIRO = "PUNTO_RETIRO"
    LOCKER = "LOCKER"

tipo_entrega: TipoEntregaEnum  # Solo valores válidos
```

**5. Validaciones custom:**
```python
# En service.py
def validar_cobertura_geografica(ciudad: str, latitud, longitud):
    if ciudad not in CIUDADES_COBERTURA:
        raise ValueError("Ciudad no en cobertura")
    # Verificar coordenadas
```

**Errores rechazados automáticamente:**
```
400 Bad Request si:
- Email inválido
- Username < 3 caracteres
- Peso < 0.1 kg
- Tipo de entrega no en enum
- Ciudad no en cobertura
```

---

### ✅ Documentación OpenAPI 3.0

**Endpoints de documentación:**

**Auth Service:**
```
http://localhost:8001/swagger-ui.html
http://localhost:8001/openapi.json
```

**Pedido Service:**
```
http://localhost:8002/swagger-ui.html
http://localhost:8002/openapi.json
```

**Fleet Service:**
```
http://localhost:8003/swagger-ui.html
http://localhost:8003/openapi.json
```

**Billing Service:**
```
http://localhost:8004/swagger-ui.html
http://localhost:8004/openapi.json
```

**Contenido de la documentación:**
- ✅ Descripción de cada endpoint
- ✅ Parámetros requeridos y opcionales
- ✅ Esquema de entrada (request body)
- ✅ Esquema de respuesta (response body)
- ✅ Códigos de error (401, 403, 404, 500)
- ✅ Ejemplos de uso
- ✅ Headers requeridos (Authorization, Content-Type)

**Metadata en código:**
```python
@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica un usuario y retorna tokens JWT.
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Retorna:
    - **access_token**: Token JWT para acceso a recursos
    - **refresh_token**: Token para renovar el access_token
    """
```

---

## 4. Criterio de Aceptación

✅ **"Un cliente autenticado puede crear un pedido urbano"**
- Cliente se registra en `/api/auth/register`
- Cliente hace login en `/api/auth/login`
- Cliente crea pedido en `POST /api/pedidos` con JWT token
- Pedido es de tipo urbano (DOMICILIO en Bogotá)

✅ **"Un supervisor puede consultarlo y ver su estado en RECIBIDO"**
- Supervisor se registra con role SUPERVISOR
- Supervisor hace login
- Supervisor consulta `GET /api/pedidos/{id}`
- Response contiene `"estado": "RECIBIDO"`

✅ **"Usando únicamente endpoints REST"**
- Todos los endpoints son REST (GET, POST, PATCH, DELETE)
- Content-Type: application/json
- Métodos HTTP estándar

✅ **"Y el API Gateway"**
- Todas las llamadas van a `http://localhost:8000`
- Kong enruta a los microservicios internamente
- Usuarios no conocen direcciones internas (8001, 8002, etc.)

---

## 5. Extras Implementados

### 🎁 Rate Limiting
```
100 requests/minuto por cliente IP
Kong retorna 429 si se excede
```

### 🎁 Logging Centralizado
```
Formato JSON con timestamp, servicio, usuario, método, código
Accesible via docker-compose logs
```

### 🎁 Health Checks
```
GET /health en cada servicio
Kubernetes-ready
```

### 🎁 Token Refresh
```
Tokens expiran en 30 minutos (access) y 7 días (refresh)
Endpoint para renovar sin hacer login nuevamente
```

### 🎁 Token Revoke
```
Logout: POST /api/auth/token/revoke
Añade token a blacklist
```

### 🎁 CORS Habilitado
```
Todas las orígenes permitidas
Necesario para frontend integrado
```

### 🎁 Documentación Postman
```
Colección JSON importable en Postman
15+ requests pre-configuradas
Variables para tokens y IDs
```

### 🎁 Scripts de Testing
```
test-services.sh - Prueba completa end-to-end
VALIDATION.md - Guía paso a paso de validación
```

---

## Resumen de Cumplimiento

| Requisito | Tipo | Estado |
|-----------|------|--------|
| AuthService CRUD | Obligatorio | ✅ Completo |
| PedidoService CRUD | Obligatorio | ✅ Completo |
| FleetService CRUD | Obligatorio | ✅ Completo |
| BillingService mínimo | Obligatorio | ✅ Completo |
| Kong API Gateway | Obligatorio | ✅ Completo |
| Enrutamiento por prefijo | Obligatorio | ✅ Completo |
| JWT Validation | Obligatorio | ✅ Completo |
| Rate Limiting | Obligatorio | ✅ Completo |
| Logging centralizado | Obligatorio | ✅ Completo |
| Transacciones ACID | Obligatorio | ✅ Completo |
| Validación de esquema | Obligatorio | ✅ Pydantic |
| OpenAPI 3.0 | Obligatorio | ✅ Swagger UI |
| Criterio de aceptación | Obligatorio | ✅ Cumplido |

---

**Fase 1: ✅ COMPLETADA AL 100%**

Próximas fases incluirán:
- Notificaciones
- Tracking en tiempo real
- Pagos integrados
- Mobile app
- Integraciones externas
