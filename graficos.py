from capacidade import carga_semanal
from estoque import saldo
from mrp import calcular
from utils import SEMANAS, buscar, numero


def posicao(ax, dados):
    itens = sorted(dados["itens"])
    indices = range(len(itens))
    ax.bar([i - 0.2 for i in indices],
           [saldo(dados, item) for item in itens], 0.4, label="Saldo")
    ax.bar([i + 0.2 for i in indices],
           [numero(dados["itens"][item]["seguranca"]) for item in itens],
           0.4, label="Segurança")
    ax.set_xticks(indices, itens, rotation=45, ha="right")
    ax.set(title="Posição de estoque", ylabel="Quantidade na unidade do item")


def projetado(ax, dados, codigo):
    item = buscar(dados["itens"], codigo)
    registros, _ = calcular(dados)
    registro = registros[codigo]["semanas"]
    ax.plot(SEMANAS, [registro[s]["projetado"] for s in SEMANAS],
            marker="o", label="Projetado")
    ax.axhline(numero(item["seguranca"]), linestyle="--", color="tab:red",
               label="Segurança")
    ax.set(title=f"Estoque projetado · {codigo}", ylabel=item["unidade"])


def chegadas(ax, dados):
    totais = {tipo: dict.fromkeys(SEMANAS, 0) for tipo in ("OP", "OC")}
    for ordem in dados["ordens"].values():
        totais[ordem["tipo"]][ordem["entrega"]] += 1
    producao = list(totais["OP"].values())
    ax.bar(SEMANAS, producao, label="OP")
    ax.bar(SEMANAS, list(totais["OC"].values()), bottom=producao, label="OC")
    ax.set(title="Ordens por semana de entrega", ylabel="Número de ordens")


def capacidade(ax, dados, centro):
    linhas = carga_semanal(dados, centro)
    normais = [carga if not alerta else 0 for _, carga, _, alerta in linhas]
    excessos = [carga if alerta else 0 for _, carga, _, alerta in linhas]
    ax.bar(SEMANAS, normais, label="Carga")
    ax.bar(SEMANAS, excessos, color="tab:red", label="Sobrecarga")
    ax.axhline(linhas[0][2], color="black", linestyle="--", label="Capacidade")
    ax.set(title=f"Carga × capacidade · {centro}", ylabel="Horas")


def gerar(dados, pasta, grafico, codigo=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError as erro:
        raise ValueError("Instale o Matplotlib.") from erro
    funcao = {
        "estoque": posicao, "projetado": projetado, "ordens": chegadas,
        "capacidade": capacidade,
    }[grafico]
    fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
    try:
        if codigo is None:
            funcao(ax, dados)
        else:
            funcao(ax, dados, codigo)
        if grafico != "estoque":
            ax.set_xticks(SEMANAS)
            ax.set_xlabel("Semana")
        ax.legend()
        pasta.mkdir(parents=True, exist_ok=True)
        sufixo = f"_{codigo}" if grafico == "projetado" else ""
        caminho = pasta / f"{grafico}{sufixo}.png"
        fig.savefig(caminho, dpi=150)
        plt.show()
        return caminho
    finally:
        plt.close(fig)
