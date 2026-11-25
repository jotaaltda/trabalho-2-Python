from decimal import Decimal

from utils import buscar, numero


def custo_padrao(dados, codigo):
    item = buscar(dados["itens"], codigo)
    if item["tipo"] == "MP":
        return numero(item["custo"]), [], None

    linhas = []
    for filho, quantidade in dados["estrutura"].get(codigo, {}).items():
        unitario, _, _ = custo_padrao(dados, filho)
        quantidade = numero(quantidade)
        linhas.append((filho, quantidade, unitario, quantidade * unitario))

    roteiro = dados["roteiros"].get(codigo)
    if roteiro is None:
        raise ValueError(f"Cadastre o roteiro de {codigo}.")
    centro = roteiro["centro"]
    tempo = numero(roteiro["tempo"])
    custo_hora = numero(buscar(dados["centros"], centro)["custo"])
    trabalho = (centro, tempo, custo_hora, tempo * custo_hora)
    total = sum((linha[3] for linha in linhas), Decimal(0)) + trabalho[3]
    return total, linhas, trabalho
