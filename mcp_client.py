import os
import httpx
from dotenv import load_dotenv

load_dotenv()

FIVETRAN_API_KEY    = os.getenv("FIVETRAN_API_KEY")
FIVETRAN_API_SECRET = os.getenv("FIVETRAN_API_SECRET")
BASE_URL            = "https://api.fivetran.com/v1"


def _headers():
    import base64
    token = base64.b64encode(
        f"{FIVETRAN_API_KEY}:{FIVETRAN_API_SECRET}".encode()
    ).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }


def list_connectors() -> dict:
    try:
        r = httpx.get(f"{BASE_URL}/connectors", headers=_headers(), timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "data": {"items": []}}


def get_connector(connector_id: str) -> dict:
    try:
        r = httpx.get(
            f"{BASE_URL}/connectors/{connector_id}",
            headers=_headers(), timeout=15
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def trigger_sync(connector_id: str) -> dict:
    try:
        r = httpx.post(
            f"{BASE_URL}/connectors/{connector_id}/sync",
            headers=_headers(), timeout=15
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def get_sync_status(connector_id: str) -> dict:
    try:
        data = get_connector(connector_id)
        if "error" in data:
            return data
        c = data.get("data", {})
        return {
            "connector_id": connector_id,
            "name":         c.get("schema", "unknown"),
            "status":       c.get("status", {}).get("sync_state", "unknown"),
            "last_sync":    c.get("succeeded_at", "never"),
            "service":      c.get("service", "unknown"),
            "paused":       c.get("paused", False),
        }
    except Exception as e:
        return {"error": str(e)}


def list_groups() -> dict:
    try:
        r = httpx.get(f"{BASE_URL}/groups", headers=_headers(), timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e), "data": {"items": []}}


def list_mcp_tools() -> list:
    return [
        {"name": "list_fivetran_connectors",
         "description": "Lists all data pipeline connectors"},
        {"name": "get_fivetran_connector",
         "description": "Gets status and details for one connector"},
        {"name": "trigger_fivetran_sync",
         "description": "Triggers a manual data sync"},
        {"name": "check_sync_status",
         "description": "Checks real-time pipeline sync state"},
        {"name": "list_fivetran_groups",
         "description": "Lists all Fivetran destinations/groups"},
    ]