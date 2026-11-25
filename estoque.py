from datetime import date

from utils import buscar, numero, obrigatorio


def saldo(dados, codigo):
    buscar(dados["itens"], codigo)
    return numero(dados["estoque"].get(codigo, 0))


def movimentar(dados, codigo, tipo, quantidade, documento, data):
    atual = saldo(dados, codigo)
    if tipo not in ("ENTRADA", "SAIDA", "AJUSTE"):
        raise ValueError("Tipo inválido. Use ENTRADA, SAIDA ou AJUSTE.")
    quantidade = numero(quantidade, None if tipo == "AJUSTE" else 0)
    if not quantidade:
        raise ValueError("A movimentação deve alterar o saldo.")
    documento = obrigatorio(documento)
    try:
        data = date.fromisoformat(data).isoformat()
    except ValueError as erro:
        raise ValueError("Use a data AAAA-MM-DD.") from erro
    variacao = -quantidade if tipo == "SAIDA" else quantidade
    novo = atual + variacao
    if novo < 0:
        raise ValueError(f"Saldo insuficiente de {codigo}. Atual: {atual}.")
    dados["estoque"][codigo] = novo
    dados["movimentos"].append({
        "data": data, "item": codigo, "tipo": tipo, "quantidade": variacao,
        "saldo": novo, "documento": documento,
    })


def kardex(dados, codigo):
    buscar(dados["itens"], codigo)
    return [linha for linha in dados["movimentos"] if linha["item"] == codigo]
