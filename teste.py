from fastapi.testclient import TestClient
from api import app

cliente_teste = TestClient(app)

def test_inicio():
    resposta = cliente_teste.get("/")
    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Bem-vindo ao Banco!"}

def test_login_correcto():
    resposta = cliente_teste.post("/login",
        data={"username": "faizal", "password": "1234"}
    )
    assert resposta.status_code == 200
    assert "access_token" in resposta.json()

def test_login_errado():
    resposta = cliente_teste.post("/login",
        data={"username": "faizal", "password": "errada"}
    )
    assert resposta.status_code == 401