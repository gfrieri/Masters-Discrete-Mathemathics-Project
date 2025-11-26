from pydantic import BaseModel, Field

# --- Modelos para el Registro (Server Setup) ---

class RegisterRequest(BaseModel):
    """
    Datos enviados por el cliente para el pre-registro OWL.
    Contiene el identificador y los datos del 'Verifier' generados
    por el cliente a partir de la contraseña.
    """
    username: str = Field(..., example="alice")
    # El 'salt' usado para derivar el Verifier
    salt: str = Field(..., example="Base64(sal_unica)")
    # El Verifier de la contraseña (e.g., hash + elemento público G^w)
    verifier: str = Field(..., example="Base64(datos_de_verificacion_V)")

class RegisterResponse(BaseModel):
    """
    Respuesta simple de éxito para el registro.
    """
    message: str = Field(..., example="Registro de usuario exitoso.")

# --- Modelos para el Intercambio de Claves (PAKE Steps) ---

class PakeStartRequest(BaseModel):
    """
    Paso 1: Datos enviados por el cliente para iniciar el PAKE.
    """
    username: str = Field(..., example="alice")
    # Elemento público inicial del cliente (e.g., X_A en la notación del paper)
    client_public_element: str = Field(..., example="Base64(elemento_publico_1)")

class PakeStartResponse(BaseModel):
    """
    Paso 1: Datos enviados por el servidor al cliente.
    """
    # ID de sesión para mantener el estado del intercambio en el servidor
    session_id: str = Field(..., example="e1f2g3h4i5j6k7l8")
    # Elemento público del servidor (e.g., X_B en la notación del paper)
    server_public_element: str = Field(..., example="Base64(elemento_publico_2)")

class PakeCompleteRequest(BaseModel):
    """
    Paso 2: Datos finales enviados por el cliente.
    """
    # El autenticador o prueba final del cliente
    client_proof: str = Field(..., example="Base64(prueba_de_autenticacion_M1)")

class PakeCompleteResponse(BaseModel):
    """
    Paso 2: Datos finales enviados por el servidor.
    """
    # El autenticador o prueba final del servidor (confirma la clave)
    server_proof: str = Field(..., example="Base64(prueba_de_autenticacion_M2)")
    # Clave de sesión (Session Key) derivada para que el cliente la utilice
    # En un entorno real, solo se envía un mensaje cifrado para probar la SK.
    session_key_derived: str = Field(..., example="Base64(clave_de_sesion_K)")
    message: str = Field(..., example="Intercambio de claves completado exitosamente.")