import pytest
from fastapi.testclient import TestClient
from app.main import app
from owl_protocol.owl import SERVER_DB, ACTIVE_PAKE_SESSIONS
import json

# Inicializa el cliente de pruebas de FastAPI
client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_database():
    """
    Fixture que se ejecuta automáticamente antes de cada prueba
    para limpiar las bases de datos simuladas. Esto asegura que
    las pruebas son independientes entre sí.
    """
    SERVER_DB.clear()
    ACTIVE_PAKE_SESSIONS.clear()
    yield

# ======================================================================
# Pruebas del Endpoint de Salud
# ======================================================================

def test_read_root():
    """Prueba de la ruta raíz (Health Check)."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Servidor OWL PAKE operativo" in response.json()["message"]
    # La base de datos debe estar vacía al inicio de la prueba
    assert "simulada: []" in response.json()["message"]


