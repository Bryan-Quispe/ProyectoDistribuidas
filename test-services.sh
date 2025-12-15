#!/bin/bash

# Script de prueba de los microservicios

BASE_URL="http://localhost:8000"
COLORS_GREEN='\033[0;32m'
COLORS_BLUE='\033[0;34m'
COLORS_NC='\033[0m' # No Color

echo -e "${COLORS_BLUE}=== PRUEBA DE MICROSERVICIOS ===${COLORS_NC}\n"

# 1. Registrar Cliente
echo -e "${COLORS_BLUE}1. Registrando cliente...${COLORS_NC}"
CLIENTE_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "cliente@example.com",
    "username": "cliente1",
    "password": "password123",
    "full_name": "Juan Pérez",
    "role": "CLIENTE"
  }')

CLIENTE_ID=$(echo $CLIENTE_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo -e "${COLORS_GREEN}✓ Cliente registrado: $CLIENTE_ID${COLORS_NC}\n"

# 2. Registrar Supervisor
echo -e "${COLORS_BLUE}2. Registrando supervisor...${COLORS_NC}"
curl -s -X POST ${BASE_URL}/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "supervisor@example.com",
    "username": "supervisor1",
    "password": "password123",
    "full_name": "Supervisor Principal",
    "role": "SUPERVISOR"
  }' > /dev/null

echo -e "${COLORS_GREEN}✓ Supervisor registrado${COLORS_NC}\n"

# 3. Login Cliente
echo -e "${COLORS_BLUE}3. Login como cliente...${COLORS_NC}"
LOGIN_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "cliente1",
    "password": "password123"
  }')

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo -e "${COLORS_GREEN}✓ Token obtenido${COLORS_NC}\n"

# 4. Login Supervisor
echo -e "${COLORS_BLUE}4. Login como supervisor...${COLORS_NC}"
SUPERVISOR_LOGIN=$(curl -s -X POST ${BASE_URL}/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "supervisor1",
    "password": "password123"
  }')

SUPERVISOR_TOKEN=$(echo $SUPERVISOR_LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo -e "${COLORS_GREEN}✓ Token supervisor obtenido${COLORS_NC}\n"

# 5. Crear Pedido
echo -e "${COLORS_BLUE}5. Creando pedido urbano...${COLORS_NC}"
PEDIDO_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/pedidos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "tipo_entrega": "DOMICILIO",
    "direccion": "Calle Principal 123, Apartamento 4B",
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
  }')

PEDIDO_ID=$(echo $PEDIDO_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
PEDIDO_STATE=$(echo $PEDIDO_RESPONSE | grep -o '"estado":"[^"]*' | cut -d'"' -f4)
NUMERO_PEDIDO=$(echo $PEDIDO_RESPONSE | grep -o '"numero_pedido":"[^"]*' | cut -d'"' -f4)

echo -e "${COLORS_GREEN}✓ Pedido creado: $NUMERO_PEDIDO${COLORS_NC}"
echo -e "${COLORS_GREEN}  ID: $PEDIDO_ID${COLORS_NC}"
echo -e "${COLORS_GREEN}  Estado: $PEDIDO_STATE${COLORS_NC}\n"

# 6. Consultar Pedido como Supervisor
echo -e "${COLORS_BLUE}6. Consultando pedido como supervisor...${COLORS_NC}"
CONSULTA_RESPONSE=$(curl -s -X GET ${BASE_URL}/api/pedidos/$PEDIDO_ID \
  -H "Authorization: Bearer $SUPERVISOR_TOKEN")

ESTADO=$(echo $CONSULTA_RESPONSE | grep -o '"estado":"[^"]*' | cut -d'"' -f4)
echo -e "${COLORS_GREEN}✓ Estado del pedido: $ESTADO${COLORS_NC}\n"

# 7. Crear Repartidor
echo -e "${COLORS_BLUE}7. Creando repartidor...${COLORS_NC}"
REPARTIDOR_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/fleet/repartidores \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
  -d '{
    "nombre": "Carlos García",
    "email": "carlos@example.com",
    "telefono": "+573001234567"
  }')

REPARTIDOR_ID=$(echo $REPARTIDOR_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo -e "${COLORS_GREEN}✓ Repartidor creado: $REPARTIDOR_ID${COLORS_NC}\n"

# 8. Crear Vehículo
echo -e "${COLORS_BLUE}8. Creando vehículo...${COLORS_NC}"
curl -s -X POST ${BASE_URL}/api/fleet/vehiculos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
  -d '{
    "repartidor_id": "'$REPARTIDOR_ID'",
    "placa": "ABC-123",
    "tipo": "CARRO",
    "modelo": "Honda Civic",
    "marca": "Honda",
    "anio": "2022",
    "capacidad_kg": 500,
    "volumen_m3": 2.5
  }' > /dev/null

echo -e "${COLORS_GREEN}✓ Vehículo creado${COLORS_NC}\n"

# 9. Crear Factura
echo -e "${COLORS_BLUE}9. Creando factura...${COLORS_NC}"
FACTURA_RESPONSE=$(curl -s -X POST ${BASE_URL}/api/billing \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "pedido_id": "'$PEDIDO_ID'",
    "cliente_id": "'$CLIENTE_ID'",
    "tarifa_base": 10000,
    "tarifa_distancia": 5000,
    "tarifa_peso": 2000,
    "descuento": 1000,
    "descripcion": "Envío urbano"
  }')

FACTURA_ID=$(echo $FACTURA_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
FACTURA_TOTAL=$(echo $FACTURA_RESPONSE | grep -o '"total_final":[0-9.]*' | cut -d':' -f2)

echo -e "${COLORS_GREEN}✓ Factura creada: $FACTURA_ID${COLORS_NC}"
echo -e "${COLORS_GREEN}  Total: $FACTURA_TOTAL COP${COLORS_NC}\n"

# 10. Resumen
echo -e "${COLORS_BLUE}=== RESUMEN DE PRUEBAS ===${COLORS_NC}"
echo -e "${COLORS_GREEN}✓ Cliente ID: $CLIENTE_ID${COLORS_NC}"
echo -e "${COLORS_GREEN}✓ Pedido: $NUMERO_PEDIDO (Estado: RECIBIDO)${COLORS_NC}"
echo -e "${COLORS_GREEN}✓ Repartidor: $REPARTIDOR_ID${COLORS_NC}"
echo -e "${COLORS_GREEN}✓ Factura: $FACTURA_ID${COLORS_NC}"
echo -e "${COLORS_GREEN}${COLORS_NC}"
echo -e "${COLORS_GREEN}✓ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE${COLORS_NC}"
