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
# Pruebas del Endpoint de REGISTRO (/register)
# ======================================================================

def test_register_user_success():
    """Prueba de registro exitoso de un nuevo usuario."""
    register_data = {
        "username": "testuser",
        "salt": "dGVzdF9zYWx0",
        "verifier": "dmVyaWZpZXJfZGF0YQ=="
    }
    response = client.post("/register", json=register_data)
    
    # Verifica el código de estado y el mensaje de respuesta
    assert response.status_code == 201
    assert response.json() == {"message": "Registro de usuario exitoso."}
    
    # Verifica que el usuario fue agregado a la base de datos simulada
    assert "testuser" in SERVER_DB
    assert SERVER_DB["testuser"]["salt"] == register_data["salt"]

def test_register_user_already_exists_failure():
    """Prueba de fallo al intentar registrar un usuario que ya existe."""
    # 1. Registrar el usuario una vez
    initial_data = {
        "username": "existing_user",
        "salt": "c2FsdF8x",
        "verifier": "dmVyaWZpZXJfMQ=="
    }
    client.post("/register", json=initial_data)

    # 2. Intentar registrarlo de nuevo
    response = client.post("/register", json=initial_data)
    
    # Debe fallar con el código 400 (Bad Request)
    assert response.status_code == 400
    assert response.json()["detail"] == "Error de registro. El usuario ya existe o los datos son inválidos."