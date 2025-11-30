# Servidor OWL PAKE (Password-Authenticated Key Exchange)

Este proyecto implementa el backend de un esquema OWL (Augmented PAKE) utilizando Python y FastAPI. El objetivo es proporcionar un servidor para el intercambio seguro de claves basado en contraseña, siguiendo la lógica del paper [Owl: An Augmented Password-Authenticated Key Exchange Scheme](https://dl.acm.org/doi/abs/10.1007/978-3-031-78679-2_12).

La lógica criptográfica se encuentra simulada en `owl_protocol/owl.py`.

## 1. Requisitos

Asegúrate de tener instalado Python 3.12.10.

## 2. Instalación

Se recomienda el uso de un entorno virtual para aislar las dependencias del proyecto.

### 2.1. Crear y Activar Entorno Virtual

#### Crear el entorno virtual

```
python -m venv venv
```

#### Activar el entorno virtual

##### En Windows:

```
source venv/scripts/activate
```

##### En Linux o macOS:

```
source venv/bin/activate
```

### 2.2. Instalar Dependencias

Una vez dentro del entorno virtual, instala las dependencias necesarias utilizando pip:

```
pip install -r requirements.txt
```

## 3. Ejecución del Backend

Para levantar el servidor web de FastAPI:

### 3.1 Ejecutar el servidor Uvicorn con recarga automática para desarrollo

```
uvicorn main:app
```

Una vez en ejecución, el servidor estará disponible en http://127.0.0.1:8000.

### 3.2. Documentación y Pruebas Manuales

Puedes acceder a la documentación interactiva (Swagger UI) para probar los endpoints:

http://127.0.0.1:8000/docs.

### 3.3. Ejemplos de Petición HTTP

A continuación, se muestra el flujo de peticiones para una sesión de intercambio de claves, utilizando el usuario testuser.

#### 1. Registro (Server Setup)

##### POST /register

```
{
"username": "testuser",
"salt": "dGVzdF9zYWx0",
"verifier": "dmVyaWZpZXJfZGF0YQ=="
}
```

#### 2. Inicio del PAKE (PAKE Step 1)

##### POST /pake/start

```
{
"username": "testuser",
"client_public_element": "Y2xpZW50X3N0ZXAxX2RhdGE="
}
```

**Respuesta:** Retorna session_id y server_public_element.

#### 3. Completar PAKE (PAKE Step 2)

##### POST /pake/complete/{session_id}

Reemplaza {session_id} con el ID obtenido en el paso anterior.

```
{
"client_proof": "Y2xpZW50X3N0ZXAyX2RhdGE="
}
```

**Respuesta:** Retorna session_key_derived y server_proof.

#### 4. Pruebas Automáticas (Pytest)

Las pruebas automatizadas verifican que los endpoints de la API y el flujo de sesión funcionen correctamente.

##### Ejecutar todas las pruebas

```
pytest
```

#### 5. Pruebas Criptográficas Unitarias

El archivo owl_tests.py está diseñado para probar las funciones de bajo nivel dentro de owl.py en un entorno aislado, asegurando que los componentes criptográficos se comporten según lo esperado.

##### Ejecutar las pruebas unitarias de la lógica criptográfica

```
python owl_test.py
```
