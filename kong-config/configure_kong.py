"""Script Python para configurar Kong declarativamente"""
import requests
import json
import time
from typing import Dict, List, Any

KONG_ADMIN_URL = "http://localhost:8001"


class KongConfigurator:
    """Configura Kong de forma programática"""
    
    def __init__(self, admin_url: str = KONG_ADMIN_URL):
        self.admin_url = admin_url
        self.wait_for_kong()
    
    def wait_for_kong(self, max_retries: int = 30):
        """Espera a que Kong esté disponible"""
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.admin_url}/status")
                if response.status_code == 200:
                    print("✓ Kong está disponible")
                    return
            except requests.ConnectionError:
                pass
            print(f"Esperando Kong... ({i+1}/{max_retries})")
            time.sleep(1)
        raise Exception("Kong no está disponible")
    
    def create_service(self, name: str, url: str, tags: List[str] = None) -> Dict:
        """Crea un servicio en Kong"""
        data = {
            "name": name,
            "url": url,
            "tags": tags or []
        }
        response = requests.post(f"{self.admin_url}/services", json=data)
        if response.status_code in [200, 201]:
            print(f"✓ Servicio '{name}' creado")
            return response.json()
        print(f"✗ Error creando servicio '{name}': {response.text}")
        return None
    
    def create_route(self, service_name: str, route_name: str, paths: List[str], 
                    methods: List[str] = None, strip_path: bool = False) -> Dict:
        """Crea una ruta para un servicio"""
        data = {
            "name": route_name,
            "paths": paths,
            "methods": methods or ["GET", "POST", "PATCH", "DELETE"],
            "strip_path": strip_path
        }
        response = requests.post(
            f"{self.admin_url}/services/{service_name}/routes",
            json=data
        )
        if response.status_code in [200, 201]:
            print(f"✓ Ruta '{route_name}' creada")
            return response.json()
        print(f"✗ Error creando ruta '{route_name}': {response.text}")
        return None
    
    def create_plugin(self, plugin_name: str, service_name: str = None, 
                     config: Dict = None) -> Dict:
        """Crea un plugin en Kong"""
        data = {
            "name": plugin_name,
            "config": config or {}
        }
        
        if service_name:
            url = f"{self.admin_url}/services/{service_name}/plugins"
        else:
            url = f"{self.admin_url}/plugins"
        
        response = requests.post(url, json=data)
        if response.status_code in [200, 201]:
            print(f"✓ Plugin '{plugin_name}' configurado")
            return response.json()
        print(f"✗ Error configurando plugin '{plugin_name}': {response.text}")
        return None
    
    def configure_all(self):
        """Configura todos los servicios, rutas y plugins"""
        print("\n=== CREANDO SERVICIOS ===")
        # Los contenedores exponen puerto 8000 internamente (no confundir con puertos mapeados en docker-compose)
        self.create_service("auth-service", "http://auth-service:8000", ["auth"])
        self.create_service("pedido-service", "http://pedido-service:8000", ["pedidos"])
        self.create_service("fleet-service", "http://fleet-service:8000", ["fleet"])
        self.create_service("billing-service", "http://billing-service:8000", ["billing"])
        
        print("\n=== CREANDO RUTAS - AUTH ===")
        # Ruta base para todo el prefijo /api/auth (login, register, me, etc.)
        self.create_route("auth-service", "auth-base", ["/api/auth"], ["GET", "POST", "PATCH", "DELETE"], strip_path=False)
        # Rutas específicas (opcionales)
        self.create_route("auth-service", "auth-login", ["/api/auth/login"], ["POST"], strip_path=False)
        self.create_route("auth-service", "auth-register", ["/api/auth/register"], ["POST"], strip_path=False)
        self.create_route("auth-service", "auth-token-refresh", ["/api/auth/token/refresh"], ["POST"], strip_path=False)
        self.create_route("auth-service", "auth-token-revoke", ["/api/auth/token/revoke"], ["POST"], strip_path=False)
        self.create_route("auth-service", "auth-me", ["/api/auth/me"], ["GET"], strip_path=False)
        
        print("\n=== CREANDO RUTAS - PEDIDOS ===")
        # Ruta base para todo el prefijo /api/pedidos
        self.create_route("pedido-service", "pedidos-base", ["/api/pedidos"], ["GET", "POST", "PATCH", "DELETE"], strip_path=False)
        # Rutas específicas (opcionales)
        self.create_route("pedido-service", "pedidos-create", ["/api/pedidos"], ["POST"], strip_path=False)
        self.create_route("pedido-service", "pedidos-list", ["/api/pedidos"], ["GET"], strip_path=False)
        # Para ids, preferible path base y que pase todo el sufijo
        self.create_route("pedido-service", "pedidos-detail", ["/api/pedidos"], ["GET"], strip_path=False)
        self.create_route("pedido-service", "pedidos-update", ["/api/pedidos"], ["PATCH"], strip_path=False)
        self.create_route("pedido-service", "pedidos-cancel", ["/api/pedidos"], ["DELETE"], strip_path=False)
        
        print("\n=== CREANDO RUTAS - FLEET ===")
        # Ruta base para todo el prefijo /api/fleet
        self.create_route("fleet-service", "fleet-base", ["/api/fleet"], ["GET", "POST", "PATCH", "DELETE"], strip_path=False)
        # Rutas específicas (opcionales)
        self.create_route("fleet-service", "fleet-repartidores", ["/api/fleet/repartidores"], ["GET", "POST"], strip_path=False)
        self.create_route("fleet-service", "fleet-repartidor", ["/api/fleet/repartidores"], ["GET", "PATCH"], strip_path=False)
        self.create_route("fleet-service", "fleet-vehiculos", ["/api/fleet/vehiculos"], ["GET", "POST"], strip_path=False)
        self.create_route("fleet-service", "fleet-vehiculo", ["/api/fleet/vehiculos"], ["GET"], strip_path=False)
        
        print("\n=== CREANDO RUTAS - BILLING ===")
        # Ruta base para todo el prefijo /api/billing
        self.create_route("billing-service", "billing-base", ["/api/billing"], ["GET", "POST", "PATCH"], strip_path=False)
        # Rutas específicas (opcionales)
        self.create_route("billing-service", "billing-create", ["/api/billing"], ["POST"], strip_path=False)
        self.create_route("billing-service", "billing-list", ["/api/billing"], ["GET"], strip_path=False)
        self.create_route("billing-service", "billing-detail", ["/api/billing"], ["GET"], strip_path=False)
        self.create_route("billing-service", "billing-update", ["/api/billing"], ["PATCH"], strip_path=False)
        self.create_route("billing-service", "billing-send", ["/api/billing"], ["POST"], strip_path=False)
        
        print("\n=== CONFIGURANDO PLUGINS ===")
        
        # Rate Limiting global
        self.create_plugin("rate-limiting", config={
            "minute": 100,
            "policy": "local"
        })
        
        # JWT para rutas protegidas (NO en auth-service)
        self.create_plugin("jwt", "pedido-service", {
            "key_claim_name": "sub",
            "secret_is_base64": False
        })
        self.create_plugin("jwt", "fleet-service", {
            "key_claim_name": "sub",
            "secret_is_base64": False
        })
        self.create_plugin("jwt", "billing-service", {
            "key_claim_name": "sub",
            "secret_is_base64": False
        })
        
        # CORS global
        self.create_plugin("cors", config={
            "origins": ["*"],
            "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
            "headers": ["*"],
            "credentials": True
        })
        
        # Request transformer para headers
        self.create_plugin("request-transformer", config={
            "add": {
                "headers": ["X-Request-ID:$(date +%s%N)"]
            }
        })
        
        print("\n✓ Configuración de Kong completada!")


if __name__ == "__main__":
    configurator = KongConfigurator()
    configurator.configure_all()
