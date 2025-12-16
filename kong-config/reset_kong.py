"""Reset minimal Kong configuration created by this project.
This script deletes services, routes and plugins created by `configure_kong.py`.
Use with Kong Admin API available at http://localhost:8001.
"""
import requests
import time

ADMIN = "http://localhost:8001"
SERVICES = ["auth-service", "pedido-service", "fleet-service", "billing-service"]
ROUTES = [
    "auth-base", "auth-login", "auth-register", "auth-token-refresh", "auth-token-revoke", "auth-me",
    "pedidos-base", "pedidos-create", "pedidos-list", "pedidos-detail", "pedidos-update", "pedidos-cancel",
    "fleet-base", "fleet-repartidores", "fleet-repartidor", "fleet-vehiculos", "fleet-vehiculo",
    "billing-base", "billing-create", "billing-list", "billing-detail", "billing-update", "billing-send",
]
PLUGIN_NAMES = ["rate-limiting", "jwt", "cors", "request-transformer"]


def wait_admin(timeout: int = 30):
    for i in range(timeout):
        try:
            r = requests.get(f"{ADMIN}/status", timeout=2)
            if r.status_code == 200:
                print("Kong admin ready")
                return True
        except requests.RequestException:
            pass
        print(f"Waiting Kong admin... ({i+1}/{timeout})")
        time.sleep(1)
    return False


def delete_service(name: str):
    url = f"{ADMIN}/services/{name}"
    r = requests.delete(url)
    if r.status_code in (204, 200):
        print(f"Deleted service: {name}")
    elif r.status_code == 404:
        print(f"Service not found: {name}")
    else:
        print(f"Failed deleting service {name}: {r.status_code} {r.text}")


def delete_route(name: str):
    url = f"{ADMIN}/routes/{name}"
    r = requests.delete(url)
    if r.status_code in (204, 200):
        print(f"Deleted route: {name}")
    elif r.status_code == 404:
        print(f"Route not found: {name}")
    else:
        print(f"Failed deleting route {name}: {r.status_code} {r.text}")


def delete_plugins_by_name(plugin_name: str):
    # iterate pages (size=100)
    params = {"size": 100}
    url = f"{ADMIN}/plugins"
    while url:
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(f"Failed listing plugins: {r.status_code} {r.text}")
            return
        data = r.json()
        for p in data.get("data", []):
            if p.get("name") == plugin_name:
                pid = p.get("id")
                rd = requests.delete(f"{ADMIN}/plugins/{pid}")
                if rd.status_code in (204, 200):
                    print(f"Deleted plugin {plugin_name} (id={pid})")
                else:
                    print(f"Failed deleting plugin {plugin_name} id={pid}: {rd.status_code} {rd.text}")
        # pagination
        next_url = data.get("next")
        url = next_url if next_url else None
        params = {}


if __name__ == "__main__":
    if not wait_admin():
        print("Kong admin not ready, aborting")
        raise SystemExit(1)

    print("\nDeleting plugins (global and service-specific)")
    for pn in PLUGIN_NAMES:
        delete_plugins_by_name(pn)

    print("\nDeleting routes")
    for r in ROUTES:
        delete_route(r)

    print("\nDeleting services")
    for s in SERVICES:
        delete_service(s)

    print("\nReset completed")
