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
                    methods: List[str] = None) -> Dict:
        """Crea una ruta para un servicio"""
        data = {
            "name": route_name,
            "paths": paths,
            "methods": methods or ["GET", "POST", "PATCH", "DELETE"]
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
        self.create_service("auth-service", "http://auth-service:8000", ["auth"])
        self.create_service("pedido-service", "http://pedido-service:8000", ["pedidos"])
        self.create_service("fleet-service", "http://fleet-service:8000", ["fleet"])
        self.create_service("billing-service", "http://billing-service:8000", ["billing"])
        
        print("\n=== CREANDO RUTAS - AUTH ===")
        self.create_route("auth-service", "auth-login", ["/api/auth/login"], ["POST"])
        self.create_route("auth-service", "auth-register", ["/api/auth/register"], ["POST"])
        self.create_route("auth-service", "auth-token-refresh", ["/api/auth/token/refresh"], ["POST"])
        self.create_route("auth-service", "auth-token-revoke", ["/api/auth/token/revoke"], ["POST"])
        self.create_route("auth-service", "auth-me", ["/api/auth/me"], ["GET"])
        
        print("\n=== CREANDO RUTAS - PEDIDOS ===")
        self.create_route("pedido-service", "pedidos-create", ["/api/pedidos"], ["POST"])
        self.create_route("pedido-service", "pedidos-list", ["/api/pedidos"], ["GET"])
        self.create_route("pedido-service", "pedidos-detail", ["/api/pedidos/{id}"], ["GET"])
        self.create_route("pedido-service", "pedidos-update", ["/api/pedidos/{id}"], ["PATCH"])
        self.create_route("pedido-service", "pedidos-cancel", ["/api/pedidos/{id}"], ["DELETE"])
        
        print("\n=== CREANDO RUTAS - FLEET ===")
        self.create_route("fleet-service", "fleet-repartidores", ["/api/fleet/repartidores"], ["GET", "POST"])
        self.create_route("fleet-service", "fleet-repartidor", ["/api/fleet/repartidores/{id}"], ["GET", "PATCH"])
        self.create_route("fleet-service", "fleet-vehiculos", ["/api/fleet/vehiculos"], ["GET", "POST"])
        self.create_route("fleet-service", "fleet-vehiculo", ["/api/fleet/vehiculos/{id}"], ["GET"])
        
        print("\n=== CREANDO RUTAS - BILLING ===")
        self.create_route("billing-service", "billing-create", ["/api/billing"], ["POST"])
        self.create_route("billing-service", "billing-list", ["/api/billing"], ["GET"])
        self.create_route("billing-service", "billing-detail", ["/api/billing/{id}"], ["GET"])
        self.create_route("billing-service", "billing-update", ["/api/billing/{id}"], ["PATCH"])
        self.create_route("billing-service", "billing-send", ["/api/billing/{id}/enviar"], ["POST"])
        
        print("\n=== CONFIGURANDO PLUGINS ===")
        
        # Rate Limiting global
        self.create_plugin("rate-limiting", config={
            "minute": 100,
            "policy": "local"
        })
        
        # JWT para rutas protegidas
        self.create_plugin("jwt", "auth-service", {
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
