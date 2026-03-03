from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
import hashlib
import sqlite3

app = FastAPI()

CHAVE_SECRETA = "minha-chave-secreta-123"
ALGORITMO = "HS256"

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

def encriptar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

utilizadores = {
    "admin": {
        "nome": "admin",
        "senha": encriptar_senha("1234")
    }
}

def verificar_senha(senha, senha_encriptada):
    return encriptar_senha(senha) == senha_encriptada

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
    conexao.execute("""
        CREATE TABLE IF NOT EXISTS transaccoes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo      TEXT,
            valor     REAL,
            cliente   TEXT,
            data      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conexao.commit()
    return conexao

@app.get("/")
def inicio():
    return {"mensagem": "Bem-vindo ao Banco!"}

@app.get("/pagina")
def pagina():
    return FileResponse("index.html")

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
def criar_cliente(cliente: Cliente, utilizador: str = Depends(obter_utilizador_actual)):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO clientes (nome, saldo) VALUES (?, ?)",
        (cliente.nome, cliente.saldo)
    )
    conexao.commit()
    conexao.close()
    return {"mensagem": f"Cliente {cliente.nome} criado!"}

class Deposito(BaseModel):
    id_cliente: int
    valor: float

@app.post("/depositar")
def depositar(deposito: Deposito, utilizador: str = Depends(obter_utilizador_actual)):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT nome FROM clientes WHERE id = ?", (deposito.id_cliente,))
    cliente = cursor.fetchone()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado!")
    cursor.execute("UPDATE clientes SET saldo = saldo + ? WHERE id = ?",
                (deposito.valor, deposito.id_cliente))
    cursor.execute("INSERT INTO transaccoes (tipo, valor, cliente) VALUES (?, ?, ?)",
                ("depósito", deposito.valor, cliente[0]))
    conexao.commit()
    conexao.close()
    return {"mensagem": f"Depositado MZN {deposito.valor}!"}

class Levantamento(BaseModel):
    id_cliente: int
    valor: float

@app.post("/levantar")
def levantar(levantamento: Levantamento, utilizador: str = Depends(obter_utilizador_actual)):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, saldo FROM clientes WHERE id = ?", (levantamento.id_cliente,))
    cliente = cursor.fetchone()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado!")
    if levantamento.valor > cliente[1]:
        raise HTTPException(status_code=400, detail="Saldo insuficiente!")
    cursor.execute("UPDATE clientes SET saldo = saldo - ? WHERE id = ?",
                (levantamento.valor, levantamento.id_cliente))
    cursor.execute("INSERT INTO transaccoes (tipo, valor, cliente) VALUES (?, ?, ?)",
                ("levantamento", levantamento.valor, cliente[0]))
    conexao.commit()
    conexao.close()
    return {"mensagem": f"Levantado MZN {levantamento.valor}!"}

class Transferencia(BaseModel):
    id_origem: int
    id_destino: int
    valor: float

@app.post("/transferir")
def transferir(transferencia: Transferencia, utilizador: str = Depends(obter_utilizador_actual)):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, saldo FROM clientes WHERE id = ?", (transferencia.id_origem,))
    origem = cursor.fetchone()
    if not origem:
        raise HTTPException(status_code=404, detail="Cliente origem não encontrado!")
    if transferencia.valor > origem[1]:
        raise HTTPException(status_code=400, detail="Saldo insuficiente!")
    cursor.execute("SELECT nome FROM clientes WHERE id = ?", (transferencia.id_destino,))
    destino = cursor.fetchone()
    if not destino:
        raise HTTPException(status_code=404, detail="Cliente destino não encontrado!")
    cursor.execute("UPDATE clientes SET saldo = saldo - ? WHERE id = ?",
                (transferencia.valor, transferencia.id_origem))
    cursor.execute("UPDATE clientes SET saldo = saldo + ? WHERE id = ?",
                (transferencia.valor, transferencia.id_destino))
    cursor.execute("INSERT INTO transaccoes (tipo, valor, cliente) VALUES (?, ?, ?)",
                ("transferência", transferencia.valor, origem[0]))
    conexao.commit()
    conexao.close()
    return {"mensagem": f"Transferido MZN {transferencia.valor} para {destino[0]}!"}

@app.get("/transaccoes")
def listar_transaccoes(utilizador: str = Depends(obter_utilizador_actual)):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM transaccoes ORDER BY data DESC")
    lista = cursor.fetchall()
    conexao.close()
    return {"transaccoes": lista}