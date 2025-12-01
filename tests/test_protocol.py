import pytest
from fastapi.testclient import TestClient
from app.main import app
from owl_protocol.owl import SERVER_DB, ACTIVE_PAKE_SESSIONS, _simulate_ecc_point_operation

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
# Pruebas del Flujo PAKE (Integración de 3 pasos)
# ======================================================================

def test_pake_full_flow_success():
    """Prueba el flujo completo de PAKE: Registro -> Start -> Complete."""
    username = "pake_user"
    
    # --- PASO 0: Setup (Registro) ---
    register_data = {
        "username": username,
        "salt": "cGFfc2FsdA==",
        "verifier": "cGFfdmVyaWZpZXI="
    }
    client.post("/register", json=register_data)
    
    # --- PASO 1: Iniciar PAKE (/pake/start) ---
    start_data = {
        "username": username,
        "client_public_element": "Q2xpZW50UHVibGljRWxlbWVudA=="
    }
    response_start = client.post("/pake/start", json=start_data)
    
    assert response_start.status_code == 200
    start_response = response_start.json()
    
    session_id = start_response["session_id"]
    
    # Verifica que la sesión se haya guardado en el estado interno
    assert session_id in ACTIVE_PAKE_SESSIONS
    assert ACTIVE_PAKE_SESSIONS[session_id]["username"] == username
    
    # --- PASO 2: Completar PAKE (/pake/complete/{session_id}) ---
    public_element = start_data["client_public_element"]
    client_proof = _simulate_ecc_point_operation(f"proof:{public_element}")

    complete_data = { "client_proof": client_proof }
    response_complete = client.post(f"/pake/complete/{session_id}", json=complete_data)
    
    assert response_complete.status_code == 200
    complete_response = response_complete.json()
    
    # Verifica que el resultado final contenga la clave de sesión y la prueba del servidor
    assert "session_key_derived" in complete_response
    assert len(complete_response["session_key_derived"]) == 64

    assert "server_proof" in complete_response
    assert len(complete_response["server_proof"]) == 64
    assert complete_response["message"] == "Intercambio de claves completado exitosamente."
    
    # Verifica que la sesión activa fue eliminada
    assert session_id not in ACTIVE_PAKE_SESSIONS

# ======================================================================
# Pruebas de Fallo PAKE
# ======================================================================

def test_pake_start_user_not_found_failure():
    """Prueba de fallo si el usuario no existe al iniciar PAKE."""
    start_data = {
        "username": "non_existent_user",
        "client_public_element": "Q2xpZW50UHVibGljRWxlbWVudA=="
    }
    response = client.post("/pake/start", json=start_data)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Usuario no encontrado o error en el inicio del PAKE."

def test_pake_complete_session_not_found_failure():
    """Prueba de fallo si el ID de sesión no existe al completar PAKE."""
    public_element = "Q2xpZW50UHVibGljRWxlbWVudA=="
    client_proof = _simulate_ecc_point_operation(f"proof:{public_element}")

    complete_data = { "client_proof": client_proof }
    
    # Usar un ID de sesión que nunca fue iniciado
    invalid_session_id = "non-existent-session-id-123"
    response = client.post(f"/pake/complete/{invalid_session_id}", json=complete_data)
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Autenticación fallida o ID de sesión inválido/expirado."