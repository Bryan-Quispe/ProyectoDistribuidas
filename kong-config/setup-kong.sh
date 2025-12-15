#!/bin/bash

# Script para configurar Kong con los servicios

echo "Esperando a Kong..."
sleep 30

# Base URL del Admin API de Kong
KONG_ADMIN="http://kong:8001"

# ==================== Crear SERVICIOS ====================

echo "Creando servicios en Kong..."

# AuthService
curl -X POST ${KONG_ADMIN}/services \
  --data "name=auth-service" \
  --data "url=http://auth-service:8000" \
  --data "tags=auth"

# PedidoService
curl -X POST ${KONG_ADMIN}/services \
  --data "name=pedido-service" \
  --data "url=http://pedido-service:8000" \
  --data "tags=pedidos"

# FleetService
curl -X POST ${KONG_ADMIN}/services \
  --data "name=fleet-service" \
  --data "url=http://fleet-service:8000" \
  --data "tags=fleet"

# BillingService
curl -X POST ${KONG_ADMIN}/services \
  --data "name=billing-service" \
  --data "url=http://billing-service:8000" \
  --data "tags=billing"

# ==================== Crear RUTAS ====================

echo "Creando rutas en Kong..."

# Auth routes
curl -X POST ${KONG_ADMIN}/services/auth-service/routes \
  --data "name=auth-login" \
  --data "paths[]=/api/auth/login" \
  --data "methods=POST"

curl -X POST ${KONG_ADMIN}/services/auth-service/routes \
  --data "name=auth-register" \
  --data "paths[]=/api/auth/register" \
  --data "methods=POST"

curl -X POST ${KONG_ADMIN}/services/auth-service/routes \
  --data "name=auth-token-refresh" \
  --data "paths[]=/api/auth/token/refresh" \
  --data "methods=POST"

curl -X POST ${KONG_ADMIN}/services/auth-service/routes \
  --data "name=auth-token-revoke" \
  --data "paths[]=/api/auth/token/revoke" \
  --data "methods=POST"

curl -X POST ${KONG_ADMIN}/services/auth-service/routes \
  --data "name=auth-me" \
  --data "paths[]=/api/auth/me" \
  --data "methods=GET"

# Pedidos routes
curl -X POST ${KONG_ADMIN}/services/pedido-service/routes \
  --data "name=pedidos-create" \
  --data "paths[]=/api/pedidos" \
  --data "methods=POST"

curl -X POST ${KONG_ADMIN}/services/pedido-service/routes \
  --data "name=pedidos-list" \
  --data "paths[]=/api/pedidos" \
  --data "methods=GET"

curl -X POST ${KONG_ADMIN}/services/pedido-service/routes \
  --data "name=pedidos-get" \
  --data "paths[]=/api/pedidos/~.*" \
  --data "methods=GET"

curl -X POST ${KONG_ADMIN}/services/pedido-service/routes \
  --data "name=pedidos-update" \
  --data "paths[]=/api/pedidos/~.*" \
  --data "methods=PATCH"

curl -X POST ${KONG_ADMIN}/services/pedido-service/routes \
  --data "name=pedidos-cancel" \
  --data "paths[]=/api/pedidos/~.*" \
  --data "methods=DELETE"

# Fleet routes
curl -X POST ${KONG_ADMIN}/services/fleet-service/routes \
  --data "name=fleet-repartidores" \
  --data "paths[]=/api/fleet/repartidores" \
  --data "methods=GET,POST"

curl -X POST ${KONG_ADMIN}/services/fleet-service/routes \
  --data "name=fleet-repartidor" \
  --data "paths[]=/api/fleet/repartidores/~.*" \
  --data "methods=GET,PATCH"

curl -X POST ${KONG_ADMIN}/services/fleet-service/routes \
  --data "name=fleet-vehiculos" \
  --data "paths[]=/api/fleet/vehiculos" \
  --data "methods=GET,POST"

curl -X POST ${KONG_ADMIN}/services/fleet-service/routes \
  --data "name=fleet-vehiculo" \
  --data "paths[]=/api/fleet/vehiculos/~.*" \
  --data "methods=GET"

# Billing routes
curl -X POST ${KONG_ADMIN}/services/billing-service/routes \
  --data "name=billing-create" \
  --data "paths[]=/api/billing" \
  --data "methods=POST"

curl -X POST ${KONG_ADMIN}/services/billing-service/routes \
  --data "name=billing-list" \
  --data "paths[]=/api/billing" \
  --data "methods=GET"

curl -X POST ${KONG_ADMIN}/services/billing-service/routes \
  --data "name=billing-get" \
  --data "paths[]=/api/billing/~.*" \
  --data "methods=GET"

curl -X POST ${KONG_ADMIN}/services/billing-service/routes \
  --data "name=billing-update" \
  --data "paths[]=/api/billing/~.*" \
  --data "methods=PATCH"

curl -X POST ${KONG_ADMIN}/services/billing-service/routes \
  --data "name=billing-send" \
  --data "paths[]=/api/billing/~/enviar" \
  --data "methods=POST"

# ==================== Configurar PLUGINS ====================

echo "Configurando plugins en Kong..."

# Rate Limiting (100 req/min por cliente)
curl -X POST ${KONG_ADMIN}/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=100" \
  --data "config.policy=local"

# JWT - Solo para rutas protegidas
curl -X POST ${KONG_ADMIN}/services/pedido-service/plugins \
  --data "name=jwt" \
  --data "config.key_claim_name=sub" \
  --data "config.secret_is_base64=false"

curl -X POST ${KONG_ADMIN}/services/fleet-service/plugins \
  --data "name=jwt"

curl -X POST ${KONG_ADMIN}/services/billing-service/plugins \
  --data "name=jwt"

# CORS para todos
curl -X POST ${KONG_ADMIN}/plugins \
  --data "name=cors" \
  --data "config.origins[]=*" \
  --data "config.methods[]=GET" \
  --data "config.methods[]=POST" \
  --data "config.methods[]=PATCH" \
  --data "config.methods[]=DELETE" \
  --data "config.headers[]=*"

# Logging
curl -X POST ${KONG_ADMIN}/plugins \
  --data "name=request-transformer" \
  --data "config.add.headers[]=X-Request-ID:req-$(date +%s%N)" \
  --data "config.add.headers[]=X-Forwarded-For:$REMOTE_ADDR"

echo "Configuración de Kong completada!"
