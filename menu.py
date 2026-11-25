from datetime import date
from decimal import DecimalException
from pathlib import Path

import capacidade
import custos
import estoque
import estrutura
import graficos
import itens
import mps
import mrp
import ordens
import relatorios
from utils import SEMANAS, buscar, fmt, numero

SAIDA = Path(__file__).resolve().parent / "relatorios"


def codigo(rotulo="Código do item"):
    return input(f"{rotulo}: ").strip().upper()


def submenu(titulo, opcoes):
    while True:
        print(f"\n{titulo}")
        for chave, (rotulo, _) in opcoes.items():
            print(f"{chave}. {rotulo}")
        print("0. Voltar" if titulo != TITULO else "0. Sair")
        escolha = input("Opção: ").strip()
        if escolha == "0":
            return
        if escolha not in opcoes:
            print("Opção inválida.")
            continue
        try:
            opcoes[escolha][1]()
        except (ValueError, OSError, DecimalException) as erro:
            print(f"ERRO: {erro}")


def alterar(base, funcao, *argumentos, **opcoes):
    dados = base.copia()
    resultado = funcao(dados, *argumentos, **opcoes)
    base.salvar(dados)
    print("Dados gravados.")
    return resultado


def editar_item(base, existente=False):
    item = codigo()
    campos = (
        ("descricao", "Descrição"), ("unidade", "Unidade"),
        ("custo", "Custo unitário"), ("prazo", "Lead time (semanas)"),
        ("seguranca", "Estoque de segurança"), ("lote", "Lote mínimo"),
    )
    atual = buscar(base.dados["itens"], item) if existente else {}
    valores = []
    for campo, rotulo in campos:
        anterior = atual.get(campo, "")
        dica = f" [{anterior}]" if existente else ""
        valor = input(f"{rotulo}{dica}: ").strip()
        valores.append(valor if valor else anterior)
    alterar(base, itens.cadastrar, item, *valores, alterar=existente)


def listar_itens(dados):
    for chave, item in sorted(dados["itens"].items()):
        print(
            f"{chave} | {item['descricao']} | {item['tipo']} | "
            f"{item['unidade']} | R$ {item['custo']} | LT {item['prazo']} | "
            f"ES {item['seguranca']} | lote {item['lote']}"
        )


def mostrar_bom(dados):
    for nivel, chave, item, quantidade in estrutura.arvore(dados, codigo()):
        margem = "    " * nivel
        unidade = (
            f" · {fmt(numero(quantidade))} {item['unidade']}"
            if quantidade is not None else ""
        )
        print(f"{margem}[{nivel}] {chave} {item['descricao']}{unidade}")


def mostrar_centros(dados):
    for chave, centro in sorted(dados["centros"].items()):
        print(f"{chave} | {centro['descricao']} | {centro['horas']} h/sem "
              f"| R$ {centro['custo']}/h")
    for item, roteiro in sorted(dados["roteiros"].items()):
        print(f"{item} → {roteiro['centro']} | {roteiro['tempo']} h/unidade")


def cadastros(base):
    submenu("Cadastros", {
        "1": ("Cadastrar item", lambda: editar_item(base)),
        "2": ("Listar itens", lambda: listar_itens(base.dados)),
        "3": ("Alterar item", lambda: editar_item(base, existente=True)),
        "4": ("Definir componente", lambda: alterar(
            base, estrutura.definir_componente, codigo("Item pai"),
            codigo("Componente"), input("Quantidade por unidade: ")
        )),
        "5": ("Exibir BOM", lambda: mostrar_bom(base.dados)),
        "6": ("Cadastrar ou atualizar centro", lambda: alterar(
            base, capacidade.cadastrar_centro, codigo("Centro"),
            input("Descrição: "), input("Horas por semana: "),
            input("Custo por hora: ")
        )),
        "7": ("Definir roteiro", lambda: alterar(
            base, capacidade.definir_roteiro, codigo(), codigo("Centro"),
            input("Horas por unidade: ")
        )),
        "8": ("Centros e roteiros", lambda: mostrar_centros(base.dados)),
    })


def mover(base):
    item = codigo()
    tipo = codigo("Tipo [E]ntrada, [S]aída, [A]juste")
    tipos = {"E": "ENTRADA", "S": "SAIDA", "A": "AJUSTE"}
    tipo = buscar(tipos, tipo)
    quantidade = input("Quantidade (ajuste com sinal): ")
    documento = input("Documento ou motivo: ")
    data = input("AAAA-MM-DD [hoje]: ").strip() or date.today().isoformat()
    alterar(base, estoque.movimentar, item, tipo, quantidade, documento, data)


def mostrar_saldo(dados, historico=False):
    chave = codigo()
    item = buscar(dados["itens"], chave)
    atual = estoque.saldo(dados, chave)
    seguranca = numero(item["seguranca"])
    if historico:
        print("Data | Tipo | Variação | Saldo | Documento")
        for linha in estoque.kardex(dados, chave):
            print(" | ".join(fmt(linha[campo]) for campo in (
                "data", "tipo", "quantidade", "saldo", "documento"
            )))
    print(f"{chave} {item['descricao']} | Saldo {fmt(atual)} "
          f"{item['unidade']} | Segurança {fmt(seguranca)}")
    if atual < seguranca:
        print("ALERTA: saldo abaixo do estoque de segurança.")


def menu_estoque(base):
    submenu("Estoque", {
        "1": ("Registrar movimentação", lambda: mover(base)),
        "2": ("Consultar saldo", lambda: mostrar_saldo(base.dados)),
        "3": ("Consultar kardex", lambda: mostrar_saldo(base.dados, True)),
    })


def mostrar_mps(dados):
    print("Item      " + "".join(f"S{s:<8}" for s in SEMANAS))
    for chave, item in sorted(dados["itens"].items()):
        if item["tipo"] == "PA":
            demanda = dados["mps"].get(chave, {})
            print(f"{chave:<10}" + "".join(
                f"{fmt(numero(demanda.get(str(s), 0))):<9}" for s in SEMANAS
            ))


def menu_mps(base):
    submenu("Plano Mestre de Produção", {
        "1": ("Consultar demanda", lambda: mostrar_mps(base.dados)),
        "2": ("Definir demanda semanal", lambda: alterar(
            base, mps.definir_demanda, codigo(), input("Semana (1–8): "),
            input("Demanda: ")
        )),
    })


def executar_mrp(base):
    registros = alterar(base, mrp.executar)
    atrasadas = [chave for chave, ordem in base.dados["ordens"].items()
                 if ordem["atrasada"] and ordem["status"] == "PLANEJADA"]
    print(f"{len(atrasadas)} exceção(ões) de liberação anterior à semana 1.")
    for chave in atrasadas:
        ordem = base.dados["ordens"][chave]
        print(f"{chave} {ordem['item']} · liberar S{ordem['liberacao']}")
    while True:
        chave = codigo("Item para consultar [Enter para voltar]")
        if not chave:
            return
        if chave not in registros:
            print("Item inexistente.")
            continue
        registro = registros[chave]
        item = base.dados["itens"][chave]
        print(f"\n{chave} {item['descricao']} | LT {item['prazo']} | "
              f"ES {item['seguranca']} | Lote {item['lote']}")
        campos = list(mrp.CAMPOS)
        valores = [
            [fmt(registro["semanas"][s][campo]) for s in SEMANAS]
            for campo in campos
        ]
        largura = max(9, 2 + max(len(v) for linha in valores for v in linha))
        print(f"{'Semana':<28}" + "".join(f"{s:>{largura}}" for s in SEMANAS))
        for campo, linha in zip(campos, valores):
            print(f"{mrp.CAMPOS[campo]:<28}" +
                  "".join(f"{v:>{largura}}" for v in linha))
        for semana, quantidade in sorted(registro["antecipadas"].items()):
            print(f"Liberação atrasada S{semana}: {fmt(quantidade)}")


def listar_ordens(dados):
    print("Ordem | Tipo | Item | Quantidade | Liberação | Entrega | Status")
    for chave, ordem in sorted(dados["ordens"].items()):
        atraso = " (ATRASADA)" if ordem["atrasada"] else ""
        print(f"{chave} | {ordem['tipo']} | {ordem['item']} | "
              f"{fmt(numero(ordem['quantidade']))} | S{ordem['liberacao']} | "
              f"S{ordem['entrega']} | {ordem['status']}{atraso}")


def menu_ordens(base):
    submenu("Ordens", {
        "1": ("Listar ordens", lambda: listar_ordens(base.dados)),
        "2": ("Firmar", lambda: alterar(
            base, ordens.transicionar, codigo("Ordem"), "FIRME"
        )),
        "3": ("Liberar", lambda: alterar(
            base, ordens.transicionar, codigo("Ordem"), "LIBERADA"
        )),
        "4": ("Apontar produção ou receber compra", lambda: alterar(
            base, ordens.encerrar, codigo("Ordem")
        )),
    })


def mostrar_crp(dados):
    for chave, centro in sorted(dados["centros"].items()):
        print(f"\n{chave} {centro['descricao']}")
        print("Semana | Carga (h) | Capacidade (h) | Uso")
        for periodo, carga, limite, alerta in capacidade.carga_semanal(
            dados, chave
        ):
            uso = f"{carga / limite:.0%}" if limite else "—"
            print(f"S{periodo} | {fmt(carga)} | {fmt(limite)} | {uso}"
                  + (" | SOBRECARGA" if alerta else ""))


def mostrar_custo(dados):
    chave = codigo()
    item = buscar(dados["itens"], chave)
    if item["tipo"] == "MP":
        raise ValueError("Selecione um item fabricado (PA ou SA).")
    total, componentes, trabalho = custos.custo_padrao(dados, chave)
    print(f"{chave} {item['descricao']}")
    print("Componente | Quantidade | Custo unitário | Subtotal")
    for filho, quantidade, unitario, subtotal in componentes:
        descricao = dados["itens"][filho]["descricao"]
        print(f"{filho} {descricao} | {fmt(quantidade)} | "
              f"R$ {unitario:.2f} | R$ {subtotal:.2f}")
    centro, horas, taxa, subtotal = trabalho
    print(f"Mão de obra {centro} | {fmt(horas)} h | "
          f"R$ {taxa:.2f}/h | R$ {subtotal:.2f}")
    print(f"Custo padrão: R$ {total:.2f}")


def exportar(dados):
    for caminho in relatorios.exportar(dados, SAIDA):
        print(f"Gravado: {caminho}")


def exibir_grafico(dados, nome, chave=None):
    print(f"Gravado: {graficos.gerar(dados, SAIDA, nome, chave)}")


def menu_graficos(base):
    submenu("Gráficos", {
        "1": ("Posição de estoque", lambda: exibir_grafico(
            base.dados, "estoque"
        )),
        "2": ("Estoque projetado", lambda: exibir_grafico(
            base.dados, "projetado", codigo()
        )),
        "3": ("Ordens por semana de entrega", lambda: exibir_grafico(
            base.dados, "ordens"
        )),
        "4": ("Carga × capacidade", lambda: exibir_grafico(
            base.dados, "capacidade", codigo("Centro")
        )),
    })


TITULO = "MRP II — PEDAL FORTE BICICLETAS"


def iniciar(base):
    submenu(TITULO, {
        "1": ("Cadastros", lambda: cadastros(base)),
        "2": ("Estoque", lambda: menu_estoque(base)),
        "3": ("Plano Mestre de Produção", lambda: menu_mps(base)),
        "4": ("Executar MRP", lambda: executar_mrp(base)),
        "5": ("Ordens de produção e compra", lambda: menu_ordens(base)),
        "6": ("Carga × capacidade", lambda: mostrar_crp(base.dados)),
        "7": ("Custo padrão", lambda: mostrar_custo(base.dados)),
        "8": ("Exportar CSV", lambda: exportar(base.dados)),
        "9": ("Gráficos", lambda: menu_graficos(base)),
    })
