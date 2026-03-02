from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

def conectar():
    con = sqlite3.connect("banco.db")
    con.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            nome  TEXT,
            saldo REAL
        )
    """)
    con.commit()
    return con

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
    cur.execute("""
        INSERT INTO clientes (nome, saldo)
        VALUES (?, ?)
    """, (cliente.nome, cliente.saldo))
    con.commit()
    con.close()
    return {"mensagem": f"Cliente {cliente.nome} criado!"}
class Deposito(BaseModel):
    id_cliente: int
    valor: float

@app.post("/depositar")
def depositar(deposito: Deposito):
    con = conectar()
    cur = con.cursor()
    cur.execute("UPDATE clientes SET saldo = saldo + ? WHERE id = ?",
                (deposito.valor, deposito.id_cliente))
    con.commit()
    con.close()
    return {"mensagem": f"Depositado: {deposito.valor}"}
class Levantamento(BaseModel):
    id_cliente: int
    valor: float

@app.post("/levantar")
def levantar(levantamento: Levantamento):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT saldo FROM clientes WHERE id = ?",
                (levantamento.id_cliente,))
    cliente = cur.fetchone()

    if not cliente:
        return {"erro": "Cliente não encontrado!"}

    if levantamento.valor > cliente[0]:
        return {"erro": "Saldo insuficiente!"}

    cur.execute("UPDATE clientes SET saldo = saldo - ? WHERE id = ?",
                (levantamento.valor, levantamento.id_cliente))
    con.commit()
    con.close()
    return {"mensagem": f"Levantado: {levantamento.valor}"}
class Transferencia(BaseModel):
    id_origem: int
    id_destino: int
    valor: float

@app.post("/transferir")
def transferir(transferencia: Transferencia):
    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT saldo FROM clientes WHERE id = ?",
                (transferencia.id_origem,))
    origem = cur.fetchone()

    if not origem:
        return {"erro": "Cliente origem não encontrado!"}

    if transferencia.valor > origem[0]:
        return {"erro": "Saldo insuficiente!"}

    cur.execute("UPDATE clientes SET saldo = saldo - ? WHERE id = ?",
                (transferencia.valor, transferencia.id_origem))

    cur.execute("UPDATE clientes SET saldo = saldo + ? WHERE id = ?",
                (transferencia.valor, transferencia.id_destino))

    con.commit()
    con.close()
    return {"mensagem": f"Transferido: {transferencia.valor}"}
