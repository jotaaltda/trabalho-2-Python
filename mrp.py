from decimal import Decimal

from estoque import saldo
from ordens import gerar
from utils import SEMANAS, TIPOS, numero

CAMPOS = {
    "bruta": "Necessidade bruta",
    "programado": "Recebimentos programados",
    "projetado": "Estoque projetado",
    "liquida": "Necessidade líquida",
    "planejado": "Recebimentos planejados",
    "liberacao": "Liberações planejadas",
}


def calcular(dados):
    zero = Decimal(0)
    brutas = {codigo: dict.fromkeys(SEMANAS, zero)
              for codigo in dados["itens"]}
    programados = {codigo: dict.fromkeys(SEMANAS, zero)
                   for codigo in dados["itens"]}
    for codigo, demandas in dados["mps"].items():
        for periodo, quantidade in demandas.items():
            brutas[codigo][int(periodo)] += numero(quantidade)
    for ordem in dados["ordens"].values():
        if ordem["status"] in ("FIRME", "LIBERADA"):
            programados[ordem["item"]][ordem["entrega"]] += numero(
                ordem["quantidade"]
            )

    propostas = []
    registros = {}
    for tipo in TIPOS:
        for codigo, item in dados["itens"].items():
            if item["tipo"] != tipo:
                continue
            semanas = {
                periodo: dict.fromkeys(CAMPOS, zero) for periodo in SEMANAS
            }
            antecipadas = {}
            projetado = saldo(dados, codigo)
            seguranca, lote = numero(item["seguranca"]), numero(item["lote"])
            for periodo, registro in semanas.items():
                bruta = brutas[codigo][periodo]
                programado = programados[codigo][periodo]
                liquida = max(zero, bruta + seguranca - projetado - programado)
                planejado = max(liquida, lote) if liquida else zero
                projetado += programado + planejado - bruta
                registro.update(
                    bruta=bruta, programado=programado, projetado=projetado,
                    liquida=liquida, planejado=planejado,
                )
                if planejado:
                    liberar = periodo - item["prazo"]
                    propostas.append((codigo, planejado, liberar, periodo))
                    if liberar in semanas:
                        semanas[liberar]["liberacao"] += planejado
                    else:
                        antecipadas[liberar] = (
                            antecipadas.get(liberar, zero) + planejado
                        )
                    for filho, proporcao in dados["estrutura"].get(
                        codigo, {}
                    ).items():
                        brutas[filho][max(1, liberar)] += (
                            planejado * numero(proporcao)
                        )
            registros[codigo] = {
                "semanas": semanas, "antecipadas": antecipadas
            }
    return registros, propostas


def executar(dados):
    registros, propostas = calcular(dados)
    gerar(dados, propostas)
    return registros
