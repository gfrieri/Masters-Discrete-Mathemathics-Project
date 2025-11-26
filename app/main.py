from fastapi import FastAPI, HTTPException

from app.models import (
    RegisterRequest, RegisterResponse,
    PakeStartRequest, PakeStartResponse,
    PakeCompleteRequest, PakeCompleteResponse
)

from owl_protocol.owl import (
    server_register_user,
    pake_step1_start,
    pake_step2_complete,
    SERVER_DB
)

app = FastAPI(
    title="Servidor OWL PAKE (FastAPI)",
    description="Backend para el protocolo Password-Authenticated Key Exchange OWL."
)

@app.get("/", tags=["Health"])
def read_root():
    """Endpoint de verificación de salud."""
    return {"message": "Servidor OWL PAKE operativo. (Base de datos de usuarios simulada: {})".format(list(SERVER_DB.keys()))}

# ----------------------------------------------------------------------
# 1. REGISTRO (SERVER SETUP)
# El cliente envía el Verifier y el Salt pre-calculado.
# ----------------------------------------------------------------------
@app.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    tags=["Registro"]
)
async def register_user(data: RegisterRequest):
    """
    Registra un nuevo usuario almacenando el Salt y el Verifier de la contraseña.
    Esta es la fase de 'Server Setup' del protocolo OWL.
    """
    success = server_register_user(data)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Error de registro. El usuario ya existe o los datos son inválidos."
        )
    return RegisterResponse(message="Registro de usuario exitoso.")

# ----------------------------------------------------------------------
# 2. INICIO DEL INTERCAMBIO PAKE (PAKE Step 1)
# El cliente inicia el proceso y recibe el primer elemento público del servidor.
# ----------------------------------------------------------------------
@app.post(
    "/pake/start",
    response_model=PakeStartResponse,
    tags=["PAKE - Intercambio de Claves"]
)
async def pake_start(data: PakeStartRequest):
    """
    Inicia la sesión PAKE. El servidor realiza el Step 1 y retorna un Session ID
    y su primer elemento público (e.g., X_B).
    """
    result = pake_step1_start(data)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado o error en el inicio del PAKE."
        )
    return PakeStartResponse(**result)

# ----------------------------------------------------------------------
# 3. COMPLETAR INTERCAMBIO PAKE (PAKE Step 2)
# El cliente envía la prueba final y recibe la clave de sesión compartida.
# ----------------------------------------------------------------------
@app.post(
    "/pake/complete/{session_id}",
    response_model=PakeCompleteResponse,
    tags=["PAKE - Intercambio de Claves"]
)
async def pake_complete(session_id: str, data: PakeCompleteRequest):
    """
    Completa la sesión PAKE. El servidor verifica la prueba del cliente,
    deriva la clave de sesión y retorna su propia prueba (M2).
    """
    result = pake_step2_complete(session_id, data.client_proof)
    
    if not result:
        # Puede ser 404 por ID de sesión no encontrado o 401 por prueba (client_proof) fallida
        # Aquí asumimos 401 si no se pudo completar.
        raise HTTPException(
            status_code=401,
            detail="Autenticación fallida o ID de sesión inválido/expirado."
        )
    
    return PakeCompleteResponse(**result, message="Intercambio de claves completado exitosamente.")