from utils import buscar, numero


def definir_componente(dados, pai, filho, quantidade):
    tipo_pai = buscar(dados["itens"], pai)["tipo"]
    tipo_filho = buscar(dados["itens"], filho)["tipo"]
    permitidos = {"PA": {"SA", "MP"}, "SA": {"MP"}, "MP": set()}
    if tipo_filho not in permitidos[tipo_pai]:
        raise ValueError("PA aceita SA ou MP. SA aceita MP.")
    quantidade = numero(quantidade)
    if not quantidade:
        raise ValueError("A quantidade por unidade deve ser positiva.")
    dados["estrutura"].setdefault(pai, {})[filho] = quantidade


def arvore(dados, codigo, nivel=0, quantidade=None):
    yield nivel, codigo, buscar(dados["itens"], codigo), quantidade
    for filho, quantidade in dados["estrutura"].get(codigo, {}).items():
        yield from arvore(dados, filho, nivel + 1, quantidade)
