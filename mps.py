from utils import buscar, numero, semana


def definir_demanda(dados, codigo, periodo, quantidade):
    if buscar(dados["itens"], codigo)["tipo"] != "PA":
        raise ValueError("O MPS aceita apenas produtos acabados.")
    periodo = semana(periodo)
    quantidade = numero(quantidade)
    dados["mps"].setdefault(codigo, {})[str(periodo)] = quantidade
