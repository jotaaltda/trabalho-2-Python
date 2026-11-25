import csv

from estoque import saldo
from utils import numero


def escrever_csv(pasta, nome, campos, linhas):
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / nome
    with caminho.open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(campos)
        escritor.writerows(linhas)
    return caminho


def exportar(dados, pasta):
    posicao = []
    for codigo, item in sorted(dados["itens"].items()):
        atual = saldo(dados, codigo)
        seguranca = numero(item["seguranca"])
        posicao.append((codigo, item["descricao"], item["unidade"], atual,
                        seguranca, atual < seguranca))
    campos = ("tipo", "item", "quantidade", "liberacao", "entrega", "status",
              "atrasada")
    linhas = [
        (codigo, *(ordem[campo] for campo in campos))
        for codigo, ordem in sorted(dados["ordens"].items())
    ]
    return (
        escrever_csv(pasta, "estoque.csv",
                     ("item", "descricao", "unidade", "saldo", "seguranca",
                      "abaixo_seguranca"), posicao),
        escrever_csv(pasta, "ordens.csv", ("ordem", *campos), linhas),
    )
