from decimal import Decimal, InvalidOperation

SEMANAS = range(1, 9)
TIPOS = ("PA", "SA", "MP")


def numero(valor, minimo=0):
    try:
        valor = Decimal(str(valor).strip().replace(",", "."))
    except InvalidOperation as erro:
        raise ValueError("Informe um número válido.") from erro
    if not valor.is_finite() or (minimo is not None and valor < minimo):
        raise ValueError("Número fora do intervalo permitido.")
    return valor


def inteiro(valor, minimo=0):
    valor = numero(valor, minimo)
    if valor != valor.to_integral_value():
        raise ValueError("Informe um número inteiro.")
    return int(valor)


def semana(valor):
    valor = inteiro(valor, 1)
    if valor not in SEMANAS:
        raise ValueError("Informe uma semana de 1 a 8.")
    return valor


def obrigatorio(valor):
    valor = valor.strip()
    if not valor:
        raise ValueError("Campo obrigatório.")
    return valor


def buscar(tabela, codigo):
    if codigo not in tabela:
        raise ValueError(f"Código inexistente: {codigo}.")
    return tabela[codigo]


def fmt(valor):
    if isinstance(valor, Decimal):
        return format(valor.normalize(), "f")
    return str(valor)
