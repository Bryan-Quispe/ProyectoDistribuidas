# Guía Completa de Rutas - API Gateway (Puerto 8000)

**Base URL:** `http://localhost:8000`

Todas las rutas de los microservicios están disponibles únicamente a través del API Gateway en el puerto 8000. Los servicios individuales NO deben ser accedidos directamente en producción.

---

## 🔐 AUTH SERVICE - `/api/auth`

### 1. Registrar Usuario
**POST** `/api/auth/register`

```powershell
# Registrar Cliente
$body = @{
    email = "cliente@example.com"
    username = "cliente1"
    password = "password123"
    full_name = "Juan Pérez"
    role = "CLIENTE"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/register" `
    -ContentType "application/json" -Body $body
```

```powershell
# Registrar Supervisor
$body = @{
    email = "supervisor@example.com"
    username = "supervisor1"
    password = "password123"
    full_name = "Maria Supervisor"
    role = "SUPERVISOR"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/register" `
    -ContentType "application/json" -Body $body
```

**Roles disponibles:** `CLIENTE`, `REPARTIDOR`, `SUPERVISOR`, `ADMIN`

---

### 2. Login (Autenticación)
**POST** `/api/auth/login`

```powershell
# Login y guardar token
$body = @{
    username = "cliente1"
    password = "password123"
} | ConvertTo-Json

$login = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/login" `
    -ContentType "application/json" -Body $body

# Guardar tokens en variables
$ACCESS_TOKEN = $login.access_token
$REFRESH_TOKEN = $login.refresh_token

Write-Host "Token de acceso: $ACCESS_TOKEN"
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 1800
}
```

---

### 3. Obtener Usuario Actual
**GET** `/api/auth/me`

```powershell
# Requiere Authorization header
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$user = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/auth/me" `
    -Headers $headers

Write-Host "Usuario: $($user.username), ID: $($user.id)"
```

---

### 4. Refrescar Token
**POST** `/api/auth/token/refresh`

```powershell
$body = @{
    refresh_token = $REFRESH_TOKEN
} | ConvertTo-Json

$newToken = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/token/refresh" `
    -ContentType "application/json" -Body $body

$ACCESS_TOKEN = $newToken.access_token
```

---

### 5. Revocar Token (Logout)
**POST** `/api/auth/token/revoke`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/token/revoke" `
    -Headers $headers
```

---

## 📦 PEDIDO SERVICE - `/api/pedidos`

**Todas las rutas requieren autenticación (Authorization header)**

### 1. Crear Pedido
**POST** `/api/pedidos`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$body = @{
    tipo_entrega = "DOMICILIO"
    direccion = "Calle Principal 123, Apartamento 4B"
    ciudad = "Bogotá"
    codigo_postal = "110111"
    latitud = 4.7110
    longitud = -74.0721
    descripcion = "Paquete con documentos"
    peso_kg = 2.5
    dimensiones = "30x20x10 cm"
    valor_declarado = 100000
    destinatario_nombre = "Juan Pérez"
    destinatario_telefono = "+573001234567"
    destinatario_email = "juan@example.com"
} | ConvertTo-Json

$pedido = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/pedidos" `
    -Headers $headers -ContentType "application/json" -Body $body

$PEDIDO_ID = $pedido.id
Write-Host "Pedido creado: $($pedido.numero_pedido), ID: $PEDIDO_ID"
```

**Tipos de entrega:** `DOMICILIO`, `PUNTO_RETIRO`, `LOCKER`
**Ciudades válidas:** `Bogotá`, `Medellín`, `Cali`, `Barranquilla`, `Cartagena`

---

### 2. Listar Pedidos del Cliente
**GET** `/api/pedidos?skip=0&limit=10`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$pedidos = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/pedidos?skip=0&limit=10" `
    -Headers $headers

Write-Host "Total pedidos: $($pedidos.Count)"
$pedidos | Format-Table id, numero_pedido, estado, ciudad
```

---

### 3. Obtener Detalle de Pedido
**GET** `/api/pedidos/{pedido_id}`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$pedido = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/pedidos/$PEDIDO_ID" `
    -Headers $headers

$pedido | ConvertTo-Json -Depth 3
```

---

### 4. Actualizar Pedido (Solo SUPERVISOR/ADMIN)
**PATCH** `/api/pedidos/{pedido_id}`

```powershell
# Requiere token de supervisor
$headers = @{ Authorization = "Bearer $SUPERVISOR_TOKEN" }

$body = @{
    estado = "CONFIRMADO"
    repartidor_id = "550e8400-e29b-41d4-a716-446655440000"
} | ConvertTo-Json

$pedido = Invoke-RestMethod -Method Patch -Uri "http://localhost:8000/api/pedidos/$PEDIDO_ID" `
    -Headers $headers -ContentType "application/json" -Body $body

Write-Host "Pedido actualizado: Estado = $($pedido.estado)"
```

**Estados disponibles:** 
- `RECIBIDO`
- `CONFIRMADO`
- `EN_PREPARACION`
- `LISTO_PARA_ENTREGA`
- `EN_RUTA`
- `ENTREGADO`
- `CANCELADO`

---

### 5. Cancelar Pedido
**DELETE** `/api/pedidos/{pedido_id}`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$body = @{
    motivo = "Cliente solicita cancelación del pedido"
} | ConvertTo-Json

Invoke-RestMethod -Method Delete -Uri "http://localhost:8000/api/pedidos/$PEDIDO_ID" `
    -Headers $headers -ContentType "application/json" -Body $body
```

---

## 🚗 FLEET SERVICE - `/api/fleet`

**Todas las rutas requieren autenticación**

### REPARTIDORES

#### 1. Crear Repartidor (Solo SUPERVISOR/ADMIN)
**POST** `/api/fleet/repartidores`

```powershell
$headers = @{ Authorization = "Bearer $SUPERVISOR_TOKEN" }

$body = @{
    nombre = "Carlos García"
    email = "carlos@example.com"
    telefono = "+573001234567"
} | ConvertTo-Json

$repartidor = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/fleet/repartidores" `
    -Headers $headers -ContentType "application/json" -Body $body

$REPARTIDOR_ID = $repartidor.id
Write-Host "Repartidor creado: $($repartidor.nombre), ID: $REPARTIDOR_ID"
```

---

#### 2. Listar Repartidores
**GET** `/api/fleet/repartidores?skip=0&limit=10`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$repartidores = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/fleet/repartidores?skip=0&limit=10" `
    -Headers $headers

$repartidores | Format-Table id, nombre, estado, telefono
```

---

#### 3. Obtener Detalle de Repartidor
**GET** `/api/fleet/repartidores/{repartidor_id}`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$repartidor = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/fleet/repartidores/$REPARTIDOR_ID" `
    -Headers $headers

$repartidor | ConvertTo-Json -Depth 2
```

---

#### 4. Actualizar Repartidor
**PATCH** `/api/fleet/repartidores/{repartidor_id}`

```powershell
$headers = @{ Authorization = "Bearer $SUPERVISOR_TOKEN" }

$body = @{
    estado = "ACTIVO"
    latitud = 4.7110
    longitud = -74.0721
} | ConvertTo-Json

$repartidor = Invoke-RestMethod -Method Patch -Uri "http://localhost:8000/api/fleet/repartidores/$REPARTIDOR_ID" `
    -Headers $headers -ContentType "application/json" -Body $body
```

**Estados de repartidor:** `DISPONIBLE`, `OCUPADO`, `INACTIVO`, `ACTIVO`

---

### VEHÍCULOS

#### 5. Crear Vehículo (Solo SUPERVISOR/ADMIN)
**POST** `/api/fleet/vehiculos`

```powershell
$headers = @{ Authorization = "Bearer $SUPERVISOR_TOKEN" }

$body = @{
    repartidor_id = $REPARTIDOR_ID
    placa = "ABC-123"
    tipo = "CARRO"
    modelo = "Honda Civic"
    marca = "Honda"
    anio = "2022"
    capacidad_kg = 500
    volumen_m3 = 2.5
} | ConvertTo-Json

$vehiculo = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/fleet/vehiculos" `
    -Headers $headers -ContentType "application/json" -Body $body

$VEHICULO_ID = $vehiculo.id
Write-Host "Vehículo creado: $($vehiculo.placa), ID: $VEHICULO_ID"
```

**Tipos de vehículo:** `MOTO`, `CARRO`, `CAMION`, `BICICLETA`

---

#### 6. Obtener Detalle de Vehículo
**GET** `/api/fleet/vehiculos/{vehiculo_id}`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$vehiculo = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/fleet/vehiculos/$VEHICULO_ID" `
    -Headers $headers

$vehiculo | ConvertTo-Json -Depth 2
```

---

## 💰 BILLING SERVICE - `/api/billing`

**Todas las rutas requieren autenticación**

### 1. Crear Factura
**POST** `/api/billing`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$body = @{
    pedido_id = $PEDIDO_ID
    cliente_id = $CLIENTE_ID
    tarifa_base = 10000
    tarifa_distancia = 5000
    tarifa_peso = 2000
    descuento = 1000
    descripcion = "Envío urbano Bogotá"
} | ConvertTo-Json

$factura = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/billing" `
    -Headers $headers -ContentType "application/json" -Body $body

$FACTURA_ID = $factura.id
Write-Host "Factura creada: ID $FACTURA_ID, Total: $($factura.total_final) COP"
```

**Nota:** El impuesto (IVA 19%) se calcula automáticamente si no se especifica.

---

### 2. Listar Facturas del Cliente
**GET** `/api/billing?skip=0&limit=10`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$facturas = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/billing?skip=0&limit=10" `
    -Headers $headers

$facturas | Format-Table id, estado, subtotal, total_final, created_at
```

---

### 3. Obtener Detalle de Factura
**GET** `/api/billing/{factura_id}`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$factura = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/billing/$FACTURA_ID" `
    -Headers $headers

$factura | ConvertTo-Json -Depth 2
```

---

### 4. Actualizar Factura
**PATCH** `/api/billing/{factura_id}`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

$body = @{
    estado = "PAGADA"
    tarifa_base = 12000
} | ConvertTo-Json

$factura = Invoke-RestMethod -Method Patch -Uri "http://localhost:8000/api/billing/$FACTURA_ID" `
    -Headers $headers -ContentType "application/json" -Body $body
```

**Estados de factura:** `BORRADOR`, `ENVIADA`, `PAGADA`, `CANCELADA`
**Nota:** Solo se pueden editar facturas en estado `BORRADOR`

---

### 5. Enviar Factura
**POST** `/api/billing/{factura_id}/enviar`

```powershell
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/billing/$FACTURA_ID/enviar" `
    -Headers $headers
```

---

## 🔄 Flujo Completo de Ejemplo

```powershell
# 1. Registrar y autenticar cliente
$body = @{
    email = "test@example.com"
    username = "testuser"
    password = "password123"
    full_name = "Test User"
    role = "CLIENTE"
} | ConvertTo-Json

$user = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/register" `
    -ContentType "application/json" -Body $body

# 2. Login
$body = @{
    username = "testuser"
    password = "password123"
} | ConvertTo-Json

$login = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/auth/login" `
    -ContentType "application/json" -Body $body

$ACCESS_TOKEN = $login.access_token
$headers = @{ Authorization = "Bearer $ACCESS_TOKEN" }

# 3. Obtener info de usuario
$me = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/auth/me" -Headers $headers
$CLIENTE_ID = $me.id

# 4. Crear pedido
$body = @{
    tipo_entrega = "DOMICILIO"
    direccion = "Carrera 7 # 100-50"
    ciudad = "Bogotá"
    codigo_postal = "110111"
    peso_kg = 3.0
    valor_declarado = 150000
    destinatario_nombre = "Test Destinatario"
} | ConvertTo-Json

$pedido = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/pedidos" `
    -Headers $headers -ContentType "application/json" -Body $body

$PEDIDO_ID = $pedido.id

# 5. Crear factura
$body = @{
    pedido_id = $PEDIDO_ID
    cliente_id = $CLIENTE_ID
    tarifa_base = 15000
    tarifa_distancia = 5000
    tarifa_peso = 3000
    descripcion = "Envío express"
} | ConvertTo-Json

$factura = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/billing" `
    -Headers $headers -ContentType "application/json" -Body $body

# 6. Ver resumen
Write-Host "✓ Usuario: $($me.username) ($CLIENTE_ID)"
Write-Host "✓ Pedido: $($pedido.numero_pedido) - Estado: $($pedido.estado)"
Write-Host "✓ Factura: $($factura.id) - Total: $($factura.total_final) COP"
```

---

## 📊 Verificación de Kong

Para verificar que Kong está ruteando correctamente:

```powershell
# Ver servicios configurados
Invoke-RestMethod -Uri "http://localhost:8001/services" | Select-Object -Expand data | Format-Table name, host, port

# Ver rutas configuradas
Invoke-RestMethod -Uri "http://localhost:8001/routes" | Select-Object -Expand data | Format-Table name, paths, service

# Ver plugins activos
Invoke-RestMethod -Uri "http://localhost:8001/plugins" | Select-Object -Expand data | Format-Table name, service
```

---

## ⚠️ Notas Importantes

1. **Base URL única:** `http://localhost:8000` - Todos los servicios accesibles SOLO por el gateway
2. **Puertos directos (SOLO para desarrollo/debug):**
   - auth-service: 8011 → NO usar en producción
   - pedido-service: 8002 → NO usar en producción
   - fleet-service: 8003 → NO usar en producción
   - billing-service: 8004 → NO usar en producción

3. **Autenticación:**
   - Auth service NO requiere JWT (permite register/login)
   - Todos los demás servicios requieren `Authorization: Bearer <token>`

4. **Rate Limiting:** 100 requests/minuto por cliente

5. **CORS:** Habilitado para todos los orígenes (*)

---

## 🔧 Troubleshooting

### Error: "no Route matched with those values"
- Verifica que la URL comience con `/api/auth`, `/api/pedidos`, `/api/fleet`, o `/api/billing`
- Confirma que Kong está corriendo: `docker ps | grep kong`

### Error: 401 Unauthorized
- Verifica que el token no haya expirado (válido 30 minutos)
- Usa `/api/auth/token/refresh` para renovar

### Error: 403 Forbidden
- Confirma que tu rol tiene permisos (ej: solo SUPERVISOR puede crear repartidores)

### Error: 500 Internal Server Error
- Revisa logs de Kong: `docker logs kong-api-gateway`
- Revisa logs del servicio específico: `docker logs <service-name>`
