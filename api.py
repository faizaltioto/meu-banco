from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

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

@app.get("/clientes")
def listar_clientes():
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