from datetime import date

from estoque import movimentar, saldo
from utils import buscar, numero

TRANSICOES = {"FIRME": "PLANEJADA", "LIBERADA": "FIRME"}


def gerar(dados, propostas):
    ordens = dados["ordens"]
    sequencias = dados.setdefault("sequencias", {})
    for codigo, ordem in list(ordens.items()):
        tipo = ordem["tipo"]
        atual = int(codigo.split("-")[1])
        sequencias[tipo] = max(sequencias.get(tipo, 0), atual)
        if ordem["status"] == "PLANEJADA":
            del ordens[codigo]

    for item, quantidade, liberacao, entrega in propostas:
        tipo = "OC" if dados["itens"][item]["tipo"] == "MP" else "OP"
        sequencias[tipo] = sequencias.get(tipo, 0) + 1
        codigo = f"{tipo}-{sequencias[tipo]:04}"
        ordens[codigo] = {
            "tipo": tipo, "item": item, "quantidade": quantidade,
            "liberacao": liberacao, "entrega": entrega,
            "status": "PLANEJADA", "atrasada": liberacao < 1,
        }


def transicionar(dados, codigo, destino):
    ordem = buscar(dados["ordens"], codigo)
    if ordem["status"] != TRANSICOES[destino]:
        raise ValueError(f"A ordem deve estar {TRANSICOES[destino]}.")
    if destino == "LIBERADA" and ordem["tipo"] == "OP":
        buscar(dados["roteiros"], ordem["item"])
    ordem["status"] = destino


def encerrar(dados, codigo):
    ordem = buscar(dados["ordens"], codigo)
    if ordem["status"] != "LIBERADA":
        raise ValueError("A ordem deve estar LIBERADA.")
    item = ordem["item"]
    quantidade = numero(ordem["quantidade"])
    componentes = dados["estrutura"].get(item, {})
    consumo = {
        filho: quantidade * numero(proporcao)
        for filho, proporcao in componentes.items()
    }
    for filho, necessario in consumo.items():
        disponivel = saldo(dados, filho)
        if necessario > disponivel:
            raise ValueError(
                f"Componente {filho}: necessário {necessario}, "
                f"disponível {disponivel}. Ordem mantida aberta."
            )
    hoje = date.today().isoformat()
    for filho, necessario in consumo.items():
        movimentar(dados, filho, "SAIDA", necessario, codigo, hoje)
    movimentar(dados, item, "ENTRADA", quantidade, codigo, hoje)
    ordem["status"] = "ENCERRADA"
