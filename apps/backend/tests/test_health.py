from app.main import app
from fastapi.testclient import TestClient

# Starlette's TestClient currently exposes incomplete type information to Pyright.
# The runtime test remains fully typed at the response assertion boundary.
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

client = TestClient(app)


def test_health_endpoint_is_safe_without_provider_secrets() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Proof of Work Backend",
        "environment": "development",
        "convex_configured": False,
    }
