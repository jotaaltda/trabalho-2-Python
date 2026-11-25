import csv
import json
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile

TABELAS = ("itens", "estrutura", "estoque", "centros", "roteiros", "mps",
           "ordens")
CAMPOS_MOVIMENTO = ("data", "item", "tipo", "quantidade", "saldo", "documento")


class Base:
    def __init__(self, pasta):
        self.pasta = Path(pasta)
        self.arquivo = self.pasta / "estado.json"
        if self.arquivo.exists():
            self.dados = self.ler(self.arquivo)
        else:
            self.dados = {
                nome: self.ler(self.pasta / f"{nome}.json")
                for nome in TABELAS
            }
            with (self.pasta / "movimentos.csv").open(
                encoding="utf-8", newline=""
            ) as arquivo:
                self.dados["movimentos"] = list(csv.DictReader(arquivo))

    @staticmethod
    def ler(caminho):
        with caminho.open(encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def copia(self):
        return deepcopy(self.dados)

    def salvar(self, dados):
        temporario = None
        try:
            with NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.pasta, delete=False
            ) as arquivo:
                temporario = Path(arquivo.name)
                json.dump(dados, arquivo, default=self.serializar,
                          ensure_ascii=False, indent=2)
            temporario.replace(self.arquivo)
        finally:
            if temporario is not None:
                temporario.unlink(missing_ok=True)
        self.dados = dados

    @staticmethod
    def serializar(valor):
        if isinstance(valor, Decimal):
            return str(valor)
        raise TypeError(f"Tipo não serializável: {type(valor)}")
