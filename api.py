from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
import sqlite3

app = FastAPI()

CHAVE_SECRETA = "minha-chave-secreta-123"
ALGORITMO = "HS256"

contexto_senha = CryptContext(schemes=["bcrypt"])
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

utilizadores = {
    "faizal": {
        "nome": "faizal",
        "senha": contexto_senha.hash("1234")
    }
}

def verificar_senha(senha, senha_encriptada):
    return contexto_senha.verify(senha, senha_encriptada)

def criar_token(dados: dict):
    return jwt.encode(dados, CHAVE_SECRETA, algorithm=ALGORITMO)

def obter_utilizador_actual(token: str = Depends(oauth2)):
    try:
        dados = jwt.decode(token, CHAVE_SECRETA, algorithms=[ALGORITMO])
        nome = dados.get("sub")
        if nome is None:
            raise HTTPException(status_code=401, detail="Token inválido!")
        return nome
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido!")

def conectar():
    conexao = sqlite3.connect("banco.db")
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            nome  TEXT,
            saldo REAL
        )
    """)
    conexao.commit()
    return conexao

@app.get("/")
def inicio():
    return {"mensagem": "Bem-vindo ao Banco!"}

@app.post("/login")
def login(formulario: OAuth2PasswordRequestForm = Depends()):
    utilizador = utilizadores.get(formulario.username)
    if not utilizador:
        raise HTTPException(status_code=401, detail="Utilizador não encontrado!")
    if not verificar_senha(formulario.password, utilizador["senha"]):
        raise HTTPException(status_code=401, detail="Senha incorrecta!")
    token = criar_token({"sub": formulario.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/clientes")
def listar_clientes(utilizador: str = Depends(obter_utilizador_actual)):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM clientes")
    lista_clientes = cursor.fetchall()
    conexao.close()
    return {"clientes": lista_clientes}

class Cliente(BaseModel):
    nome: str
    saldo: float

@app.post("/clientes/criar")
def criar_cliente(cliente: Cliente):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO clientes (nome, saldo) VALUES (?, ?)",
        (cliente.nome, cliente.saldo)
    )
    conexao.commit()
    conexao.close()
    return {"mensagem": f"Cliente {cliente.nome} criado!"}