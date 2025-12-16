"""Remove JWT plugins from Kong services - let each microservice handle JWT validation"""
import requests
import time

ADMIN = "http://localhost:8001"

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

def delete_jwt_plugins():
    """Find and delete all JWT plugins"""
    url = f"{ADMIN}/plugins"
    params = {"size": 100}
    
    while url:
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print(f"Failed listing plugins: {r.status_code}")
            return
        
        data = r.json()
        for p in data.get("data", []):
            if p.get("name") == "jwt":
                pid = p.get("id")
                service_id = p.get("service", {}).get("id")
                service_name = p.get("service", {}).get("name") if "service" in p else None
                
                rd = requests.delete(f"{ADMIN}/plugins/{pid}")
                if rd.status_code in (204, 200):
                    print(f"✓ Deleted JWT plugin (id={pid}, service={service_name or service_id})")
                else:
                    print(f"✗ Failed deleting JWT plugin id={pid}: {rd.status_code}")
        
        # pagination
        next_url = data.get("next")
        url = next_url if next_url else None
        params = {}

if __name__ == "__main__":
    if not wait_admin():
        print("Kong admin not ready")
        raise SystemExit(1)
    
    print("\nRemoving JWT plugins from services...")
    delete_jwt_plugins()
    print("\nDone - microservices will now validate JWT directly")
