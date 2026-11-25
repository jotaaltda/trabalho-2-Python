import re

from utils import inteiro, numero, obrigatorio


def cadastrar(dados, codigo, descricao, unidade, custo, prazo, seguranca,
              lote, alterar=False):
    if not re.fullmatch(r"(PA|SA|MP)-[0-9]+", codigo):
        raise ValueError("Use o formato Tipo-Número, como PA-001.")
    if alterar and codigo not in dados["itens"]:
        raise ValueError("Item inexistente.")
    if not alterar and codigo in dados["itens"]:
        raise ValueError("Código já cadastrado.")
    dados["itens"][codigo] = {
        "descricao": obrigatorio(descricao), "tipo": codigo.split("-")[0],
        "unidade": obrigatorio(unidade), "custo": numero(custo),
        "prazo": inteiro(prazo), "seguranca": numero(seguranca),
        "lote": numero(lote),
    }
