import httpx
import time

API_URL = "http://localhost:8000"


def register(email, password, tenant_name):
    print(f"Registering {email} for {tenant_name}")
    resp = httpx.post(
        f"{API_URL}/auth/register",
        json={
            "email": email,
            "password": password,
            "tenant_name": tenant_name,
            "tenant_description": f"Tenant {tenant_name}",
        },
    )

    if resp.status_code == 400 and "already registered" in resp.text:
        print("Already registered")
        return None
    resp.raise_for_status()
    print("Registered successfully:", resp.json())
    return resp.json()


def login(email, password):
    print(f"Logging in {email}")
    resp = httpx.post(
        f"{API_URL}/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]
    return token


def test_multi_tenancy():
    # Register two tenants
    try:
        register("admin@tenanta.com", "password123", "Tenant A")
    except Exception:
        pass
    try:
        register("admin@tenantb.com", "password123", "Tenant B")
    except Exception:
        pass

    # Login
    token_a = login("admin@tenanta.com", "password123")
    token_b = login("admin@tenantb.com", "password123")

    print("\n--- Testing Ingest as Tenant A ---")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Ingest dummy repo
    ingest_resp = httpx.post(
        f"{API_URL}/ingest/",
        headers=headers_a,
        json={"repo_path": r"d:\AIEKP\dummy_repo"},
        timeout=30,
    )

    print("Ingest Resp:", ingest_resp.status_code, ingest_resp.text)

    # Wait a bit for async ingest
    time.sleep(2)

    print("\n--- Testing Search as Tenant A ---")
    search_a = httpx.post(
        f"{API_URL}/search/", headers=headers_a, json={"query": "vault code"}
    )
    print("Search A Status:", search_a.status_code)
    results_a_body = search_a.json()
    results_a = results_a_body.get("results", [])
    print(f"Results for A: {len(results_a)}")
    if len(results_a) > 0:
        print("  Found:", results_a[0].get("content", ""))

    print("\n--- Testing Search as Tenant B ---")
    headers_b = {"Authorization": f"Bearer {token_b}"}
    search_b = httpx.post(
        f"{API_URL}/search/", headers=headers_b, json={"query": "vault code"}
    )
    print("Search B Status:", search_b.status_code)
    results_b_body = search_b.json()
    results_b = results_b_body.get("results", [])
    print(f"Results for B: {len(results_b)}")


if __name__ == "__main__":
    test_multi_tenancy()
