import uuid
import hashlib
from typing import Dict, Any, Optional
from app.models import RegisterRequest, PakeStartRequest

# --- Base de Datos Temporal (Simulación) ---
# Almacena el verifier, salt y el estado de la sesión PAKE.
SERVER_DB: Dict[str, Any] = {} # Almacena datos permanentes (username -> {salt, verifier})
ACTIVE_PAKE_SESSIONS: Dict[str, Any] = {} # Almacena sesiones activas (session_id -> {username, estado_interno})

# --- Parámetros de Simulación Criptográfica ---
# Estos son valores fijos que simulan los parámetros de ECC
CURVE_ID = "secp256r1"
GROUP_ORDER = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551 # Orden de la curva P-256
HASH_FUNC = hashlib.sha256

def _simulate_ecc_point_operation(input_data: str) -> str:
    """
    Simula una operación de curva elíptica (e.g., G^x, P + Q, x*P).
    En la implementación real, esto sería aritmética de puntos ECC.
    """
    # Usamos un hash como un placeholder determinista para la operación
    return HASH_FUNC(input_data.encode()).hexdigest()

def _simulate_key_derivation(components: list[str]) -> str:
    """
    Simula la derivación de la clave de sesión (SK).
    En el paper OWL, esto sería una KDF (e.g., HKDF) aplicada a la coordenada x del punto compartido.
    """
    full_input = "|".join(components)
    return HASH_FUNC(full_input.encode()).hexdigest()

def _simulate_schnorr_proof(message: str, secret: str) -> str:
    """
    Simula la generación de una Prueba de Conocimiento Cero de Schnorr (ZKP).
    En OWL, esto es la generación de M1 o M2.
    """
    # En la realidad: h = H(Context || Puntos || Commits), r = v - x*h
    return _simulate_ecc_point_operation(f"proof:{message}:{secret}")

def _simulate_schnorr_verification(proof: str, public_element: str) -> bool:
    """
    Simula la verificación de una ZKP de Schnorr.
    En OWL, esto es la verificación de M1 o M2.
    """
    # En la realidad: Verificar si V' == g^r * X^h
    expected_proof = _simulate_ecc_point_operation(f"proof:{public_element}")
    return proof == expected_proof


# --- Funciones de Implementación OWL ---

def server_register_user(data: RegisterRequest) -> bool:
    """
    Lógica de registro del servidor OWL (Server Setup).

    Implementación requerida (Fase 1: Setup):
    1. Verificar si el usuario ya existe en SERVER_DB.
    2. **Almacenar el 'salt' y el 'verifier' de forma segura.**
       Nota: En OWL, el verifier es V = (g^w, H(v)), donde w es el secreto derivado
       de la contraseña y v es el valor aleatorio para el ZKP en la base de datos.
    """
    if data.username in SERVER_DB:
        # Lógica de manejo de error si el usuario ya existe
        return False

    # ALMACENAMIENTO SEGURO DEL VERIFIER
    # El verifier del cliente ya contiene los datos necesarios para el ZKP del servidor.
    SERVER_DB[data.username] = {
        "salt": data.salt,
        "verifier": data.verifier,
        "curve": CURVE_ID
    }
    print(f"DEBUG: Usuario '{data.username}' registrado.")
    return True

def pake_step1_start(data: PakeStartRequest) -> Optional[Dict[str, str]]:
    """
    Lógica del Paso 1 del intercambio PAKE (Client -> Server).

    Implementación requerida (Fase 2: Intercambio):
    1. Buscar el 'verifier' del usuario en SERVER_DB.
    2. **Generar el secreto ephimeral del servidor (s)**: s <- [0, q-1].
    3. **Calcular el elemento público del servidor (X_B)**: X_B = g^s.
       Nota: En OWL, esto es más complejo e involucra el elemento público A del cliente
       y el verifier V del servidor. Se calcula un término G_B o X_B que incluye V.
    4. **Guardar el estado interno** (s, X_A, V) en ACTIVE_PAKE_SESSIONS.
    5. Retornar el ID de sesión y el elemento público del servidor.
    """
    if data.username not in SERVER_DB:
        return None # Usuario no encontrado

    user_data = SERVER_DB[data.username]
    session_id = str(uuid.uuid4())

    # --- LÓGICA CRIPTOGRÁFICA DEL PASO 1 (OWL: PAKE A -> B) ---
    # Simulación de generación del secreto efímero 's' y el elemento público
    server_ephemeral_secret = str(uuid.uuid4()) # s (escalar)
    
    # X_B = Simulación de G^s + Puntos derivados del verifier
    # El verifier incluye el elemento G^w, que debe ser usado aquí.
    input_for_public_element = f"{server_ephemeral_secret}:{user_data['verifier']}:{data.client_public_element}"
    server_public_element = _simulate_ecc_point_operation(input_for_public_element)

    internal_state = {
        "username": data.username,
        "client_element_A": data.client_public_element,
        "server_ephemeral_secret": server_ephemeral_secret, # Clave privada efímera
        "verifier": user_data["verifier"],
        "server_public_element": server_public_element,
        "salt": user_data["salt"]
    }
    # -------------------------------------------------------------

    ACTIVE_PAKE_SESSIONS[session_id] = internal_state
    print(f"DEBUG: Sesión PAKE iniciada para '{data.username}' con ID: {session_id}")

    return {
        "session_id": session_id,
        "server_public_element": server_public_element
    }

def pake_step2_complete(session_id: str, client_proof: str) -> Optional[Dict[str, str]]:
    """
    Lógica del Paso 2 del intercambio PAKE (Client -> Server, final).

    Implementación requerida (Fase 3: Autenticación y Derivación):
    1. Recuperar el estado de la sesión de ACTIVE_PAKE_SESSIONS.
    2. **Derivar la clave de sesión compartida (SK)**: SK = KDF(Coordenada_X(Punto_Compartido)).
       El punto compartido se calcula usando el secreto 's' y el elemento X_A del cliente.
    3. **Verificar la prueba del cliente (client_proof)**: Verificar M1 (ZKP de Schnorr).
    4. **Generar la prueba del servidor (server_proof)**: Generar M2 (ZKP de Schnorr).
    5. Limpiar la sesión de ACTIVE_PAKE_SESSIONS.
    6. Retornar la clave de sesión y la prueba del servidor.
    """
    session_state = ACTIVE_PAKE_SESSIONS.get(session_id)
    if not session_state:
        return None # Sesión no encontrada o expirada

    # --- LÓGICA CRIPTOGRÁFICA DEL PASO 2 (OWL: PAKE B -> A) ---
    
    # 1. CÁLCULO DEL PUNTO COMPARTIDO Y CLAVE DE SESIÓN
    shared_point_input = (
        session_state["server_ephemeral_secret"],
        session_state["client_element_A"],
        session_state["verifier"]
    )
    # Simula la derivación del punto compartido J
    shared_secret_component = _simulate_ecc_point_operation(":".join(shared_point_input))
    
    # Derivación de la Session Key (SK) usando KDF
    # Incluye todos los elementos públicos (A, B, X_A, X_B, Verifier, etc.)
    kdf_input = [
        shared_secret_component,
        session_state["client_element_A"],
        session_state["server_public_element"],
        session_state["username"],
        session_state["salt"]
    ]
    session_key = _simulate_key_derivation(kdf_input)
    
    # 2. VERIFICACIÓN DEL client_proof (M1)
    is_proof_valid = _simulate_schnorr_verification(
        proof=client_proof, 
        public_element=session_state["client_element_A"]
    )
    
    if not is_proof_valid:
        # La autenticación del cliente falló
        del ACTIVE_PAKE_SESSIONS[session_id]
        print(f"DEBUG: Sesión PAKE fallida y eliminada: {session_id}")
        return None

    # 3. GENERACIÓN DEL server_proof (M2)
    # M2 es un ZKP sobre el conocimiento de la clave de sesión derivada
    server_proof = _simulate_schnorr_proof(
        message=session_key, 
        secret=session_state["server_ephemeral_secret"]
    )
    # -------------------------------------------------------------

    # Limpiar la sesión activa
    del ACTIVE_PAKE_SESSIONS[session_id]
    print(f"DEBUG: Sesión PAKE completada y eliminada: {session_id}")

    return {
        "session_key_derived": session_key,
        "server_proof": server_proof
    }