python -m venv venv

source venv/scripts/activate

pip install -r requirements.txt

uvicorn app.main:app --reload

/register
{
"username": "testuser",
"salt": "dGVzdF9zYWx0",
"verifier": "dmVyaWZpZXJfZGF0YQ=="
}

/pake/start
{
"username": "testuser",
"client_step1": "Y2xpZW50X3N0ZXAxX2RhdGE="
}

/pake/complete/{session_id}
{
"client_step2": "Y2xpZW50X3N0ZXAyX2RhdGE="
}

pytest
