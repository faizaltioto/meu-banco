from fastapi import FastAPI

app = FastAPI()

# Rota 1: Identificação do Produto
@app.get("/produto/{nome}")
def mostrar(nome: str, preco: float):
    return {
        "produto": nome, 
        "preco_base": preco
    }

# Rota 2: Cálculo de Venda
@app.get("/calcular")
def calcular(preco: float, quantidade: int, desconto: float = 0.10):
    total = preco * quantidade
    valor_desconto = total * desconto
    valor_final = total - valor_desconto
    
    return {
        "subtotal": total,
        "desconto_aplicado": round(valor_desconto, 2),
        "total_a_pagar": round(valor_final, 2),
        "moeda": "MZN"
    }

