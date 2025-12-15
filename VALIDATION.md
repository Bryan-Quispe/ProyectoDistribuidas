# Guía de Validación - Criterio de Aceptación

Este documento valida que se cumple el **Criterio de Aceptación** de Fase 1.

## Criterio de Aceptación Oficial

> "Un cliente autenticado puede crear un pedido urbano, y un supervisor puede consultarlo y ver su estado en RECIBIDO, usando únicamente endpoints REST y el API Gateway."

## Validación Paso a Paso

### Paso 1: Iniciar Infraestructura

```bash
# Terminal 1: Clonar/abrir proyecto
cd c:\Users\rquis\OneDrive\Escritorio\7mo-Semestre\Distribuidas\Parcial 2\Proyecto

# Terminal 2: Levantar Docker Compose
docker-compose up -d

# Esperar 30 segundos a que todo esté listo
```

**Verificar que los servicios estén saludables:**

```bash
curl http://localhost:8001/status

# Debe retornar algo como:
# {"status":"healthy"}
```

### Paso 2: Configurar Kong

```bash
# Terminal 3: Configurar enrutamiento y plugins
cd kong-config
pip install requests  # si aún no lo tienes
python configure_kong.py

# Output esperado:
# ✓ Kong está disponible
# ✓ Servicio 'auth-service' creado
# ✓ Servicio 'pedido-service' creado
# ... más servicios ...
# ✓ Configuración de Kong completada!
```

### Paso 3: Registrar Usuario Cliente

**Método 1: Con curl**

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cliente@example.com",
    "username": "cliente_test",
    "password": "password123",
    "full_name": "Juan Pérez Cliente",
    "role": "CLIENTE"
  }'
```

**Respuesta esperada (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "cliente@example.com",
  "username": "cliente_test",
  "full_name": "Juan Pérez Cliente",
  "role": "CLIENTE",
  "is_active": true,
  "created_at": "2025-12-15T14:30:00"
}
```

✅ **Validación:** Cliente registrado exitosamente en AuthService via Kong

### Paso 4: Login del Cliente

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "cliente_test",
    "password": "password123"
  }'
```

**Respuesta esperada (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

✅ **Validación:** Cliente autenticado con JWT

**GUARDAR el access_token como variable:**
```bash
export CLIENT_TOKEN="<copiar access_token aqui>"
```

### Paso 5: Crear Pedido Urbano

```bash
curl -X POST http://localhost:8000/api/pedidos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -d '{
    "tipo_entrega": "DOMICILIO",
    "direccion": "Carrera 7 No. 100-50, Piso 10",
    "ciudad": "Bogotá",
    "codigo_postal": "110111",
    "latitud": 4.7110,
    "longitud": -74.0721,
    "descripcion": "Documento importante",
    "peso_kg": 0.5,
    "valor_declarado": 50000,
    "destinatario_nombre": "Carlos Rodríguez",
    "destinatario_telefono": "+573001234567",
    "destinatario_email": "carlos@example.com"
  }'
```

**Respuesta esperada (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "numero_pedido": "PED-1734344600-A1B2C3D4",
  "cliente_id": "550e8400-e29b-41d4-a716-446655440000",
  "estado": "RECIBIDO",
  "tipo_entrega": "DOMICILIO",
  "ciudad": "Bogotá",
  "peso_kg": 0.5,
  "valor_declarado": 50000,
  "destinatario_nombre": "Carlos Rodríguez",
  "created_at": "2025-12-15T14:35:00",
  ...
}
```

**✅ Validaciones completadas:**
- ✓ Cliente autenticado (JWT válido)
- ✓ Petición a través de Kong API Gateway (puerto 8000)
- ✓ Pedido creado en estado RECIBIDO
- ✓ Tipo de entrega válido (DOMICILIO)
- ✓ Ciudad en cobertura (Bogotá)
- ✓ Geolocalización dentro de límites

**GUARDAR el pedido_id:**
```bash
export PEDIDO_ID="550e8400-e29b-41d4-a716-446655440001"
```

### Paso 6: Registrar Usuario Supervisor

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "supervisor@example.com",
    "username": "supervisor_test",
    "password": "password123",
    "full_name": "María Supervisor",
    "role": "SUPERVISOR"
  }'
```

**Respuesta esperada (201):** Usuario supervisor registrado

### Paso 7: Login del Supervisor

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "supervisor_test",
    "password": "password123"
  }'
```

**GUARDAR el access_token del supervisor:**
```bash
export SUPERVISOR_TOKEN="<copiar access_token aqui>"
```

### Paso 8: Consultar Pedido como Supervisor

```bash
curl -X GET http://localhost:8000/api/pedidos/$PEDIDO_ID \
  -H "Authorization: Bearer $SUPERVISOR_TOKEN"
```

**Respuesta esperada (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "numero_pedido": "PED-1734344600-A1B2C3D4",
  "cliente_id": "550e8400-e29b-41d4-a716-446655440000",
  "estado": "RECIBIDO",
  "tipo_entrega": "DOMICILIO",
  "ciudad": "Bogotá",
  "peso_kg": 0.5,
  "valor_declarado": 50000,
  "destinatario_nombre": "Carlos Rodríguez",
  "created_at": "2025-12-15T14:35:00",
  ...
}
```

✅ **Validación final:**
- ✓ Supervisor autenticado (JWT válido)
- ✓ Puede consultar pedido creado por cliente
- ✓ **Estado es RECIBIDO** ✨
- ✓ Usando API Gateway Kong (puerto 8000)
- ✓ Endpoint REST GET /api/pedidos/{id}

## ✅ CRITERIO DE ACEPTACIÓN CUMPLIDO

| Requerimiento | Estado | Evidencia |
|---------------|--------|-----------|
| Cliente autenticado | ✅ | JWT obtenido en login |
| Crear pedido urbano | ✅ | POST /api/pedidos con tipo_entrega=DOMICILIO |
| Pedido en cobertura | ✅ | Ciudad Bogotá con geolocalización válida |
| Supervisor consulta | ✅ | GET /api/pedidos/{id} con supervisor_token |
| Estado RECIBIDO | ✅ | Campo "estado": "RECIBIDO" en respuesta |
| Vía REST | ✅ | HTTP POST, GET usando JSON |
| Vía API Gateway | ✅ | URL base: http://localhost:8000 (Kong) |
| Sin estado 400+ | ✅ | Todas respuestas 200-201 |

## Validaciones Adicionales Implementadas

### Esquema (Schema Validation)

```python
# Validaciones automáticas en crear pedido:
- Email válido (Pydantic EmailStr)
- Ciudad en cobertura conocida
- Peso mínimo 0.1 kg
- Geolocalización dentro de límites
- Tipo entrega válido
```

### Transacciones ACID

```python
# Cada operación es transaccional:
- Crear usuario: @transactional
- Crear pedido: @transactional
- Cambiar estado: @transactional
```

### Documentación OpenAPI 3.0

```bash
# Accesible en:
http://localhost:8001/swagger-ui.html  # Auth
http://localhost:8002/swagger-ui.html  # Pedidos
http://localhost:8003/swagger-ui.html  # Fleet
http://localhost:8004/swagger-ui.html  # Billing
```

### Rate Limiting

```bash
# Kong limita a 100 requests/minuto por cliente
# Probar excediendo el límite:
for i in {1..101}; do
  curl -X GET http://localhost:8000/api/pedidos \
    -H "Authorization: Bearer $CLIENT_TOKEN"
done

# Request 101+ retornará 429 Too Many Requests
```

### Logging Centralizado

```bash
# Ver logs en tiempo real:
docker-compose logs -f pedido-service

# Formato JSON con:
# - timestamp ISO 8601
# - service name
# - method (POST, GET, PATCH, DELETE)
# - uri
# - status_code
# - user_id (si aplica)
```

## Testing Automático

**Script disponible:**

```bash
bash test-services.sh

# Output:
# ✓ Cliente registrado
# ✓ Supervisor registrado
# ✓ Token obtenido
# ✓ Pedido creado: PED-...
# ✓ Estado del pedido: RECIBIDO
# ✓ Repartidor creado
# ✓ Factura creada
# ✓ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE
```

## Solución de Problemas

### Token inválido en consulta supervisor

```bash
# Verificar formato correcto:
Authorization: Bearer <token>

# El token incluye:
# - sub: user_id
# - username: nombre
# - role: SUPERVISOR
# - exp: timestamp expiración
```

### Pedido rechazado por cobertura

```bash
# Ciudades permitidas:
- Bogotá (4.5° a 4.9°N, 74.3° a 73.8°O)
- Medellín (6.1° a 6.3°N, 75.6° a 75.4°O)
- Cali (3.3° a 3.5°N, 76.6° a 76.4°O)
- Barranquilla (10.9° a 11.1°N, 74.8° a 74.6°O)
- Cartagena (10.3° a 10.5°N, 75.5° a 75.3°O)

# O usar latitud/longitud en rango válido
```

### Kong no enruta correctamente

```bash
# Reiniciar Kong:
docker-compose restart kong

# Reconfigurar:
cd kong-config
python configure_kong.py
```

## Conclusión

La **Fase 1** está **completamente implementada** con:

✅ 4 Microservicios REST (Auth, Pedidos, Fleet, Billing)
✅ Kong API Gateway con rate limiting y JWT
✅ PostgreSQL con transacciones ACID
✅ Validación de esquema con Pydantic
✅ Logging centralizado en JSON
✅ Documentación OpenAPI 3.0
✅ Docker Compose para orquestación
✅ Criterio de aceptación cumplido al 100%

**Ready for Phase 2! 🚀**
