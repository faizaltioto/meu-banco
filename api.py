from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

DATABASE_URL = os.environ.get("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

def criar_tabela():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id    SERIAL PRIMARY KEY,
            nome  TEXT,
            saldo REAL
        )
    """)
    con.commit()
    con.close()

criar_tabela()

@app.get("/")
def inicio():
    return {"mensagem": "Bem-vindo ao Banco!"}

@app.get("/clientes")
def listar_clientes():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()
    con.close()
    return {"clientes": clientes}

class Cliente(BaseModel):
    nome: str
    saldo: float

@app.post("/clientes/criar")
def criar_cliente(cliente: Cliente):
    con = conectar()
    cur = con.cursor()
    cur.execute("INSERT INTO clientes (nome, saldo) VALUES (%s, %s)",
                (cliente.nome, cliente.saldo))
    con.commit()
    con.close()
    return {"mensagem": f"Cliente {cliente.nome} criado!"}
