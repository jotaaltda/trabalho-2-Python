from decimal import Decimal

from utils import SEMANAS, buscar, numero, obrigatorio


def cadastrar_centro(dados, codigo, descricao, horas, custo):
    dados["centros"][obrigatorio(codigo)] = {
        "descricao": obrigatorio(descricao), "horas": numero(horas),
        "custo": numero(custo),
    }


def definir_roteiro(dados, item, centro, tempo):
    if buscar(dados["itens"], item)["tipo"] == "MP":
        raise ValueError("Matéria-prima não possui roteiro.")
    buscar(dados["centros"], centro)
    tempo = numero(tempo)
    if not tempo:
        raise ValueError("O tempo por unidade deve ser positivo.")
    dados["roteiros"][item] = {"centro": centro, "tempo": tempo}


def carga_semanal(dados, centro):
    capacidade = numero(buscar(dados["centros"], centro)["horas"])
    cargas = dict.fromkeys(SEMANAS, Decimal(0))
    for ordem in dados["ordens"].values():
        if ordem["tipo"] != "OP" or ordem["status"] != "LIBERADA":
            continue
        roteiro = buscar(dados["roteiros"], ordem["item"])
        periodo = ordem["liberacao"]
        if roteiro["centro"] == centro and periodo in cargas:
            cargas[periodo] += (
                numero(ordem["quantidade"]) * numero(roteiro["tempo"])
            )
    return [
        (periodo, carga, capacidade, carga > capacidade)
        for periodo, carga in cargas.items()
    ]
