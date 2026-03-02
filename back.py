from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    # Página inicial simples com link pro frontend
    return """
    <h2>Backend ligado ✅</h2>
    <p>Abra o arquivo <b>frontend.html</b> no navegador.</p>
    <p>Depois que enviar o formulário, o FastAPI vai processar e mostrar o resultado.</p>
    """

@app.post("/processar", response_class=HTMLResponse)
def processar(nome: str = Form(...), senha: str = Form(...)):
    # Aqui é onde o backend "pega" as variáveis vindas do HTML
    nome = nome.strip()

    if not nome:
        return "<h3>Erro: nome vazio</h3><a href='/'>Voltar</a>"

    # Lógica simples só para ver funcionar
    if senha == "1234":
        return f"""
        <h2>Login OK ✅</h2>
        <p>Bem-vindo, <b>{nome}</b>!</p>
        <a href="/">Voltar</a>
        """
    else:
        return f"""
        <h2>Login falhou ❌</h2>
        <p>Nome: <b>{nome}</b></p>
        <p>Senha errada (tente <b>1234</b>).</p>
        <a href="/">Voltar</a>
        """