import argparse
from pathlib import Path

from menu import iniciar
from persistencia import Base


def main():
    parser = argparse.ArgumentParser(description="MRP II — Pedal Forte")
    parser.add_argument("--data", type=Path,
                        default=Path(__file__).resolve().parent / "data",
                        help="pasta com os arquivos de dados")
    argumentos = parser.parse_args()
    try:
        base = Base(argumentos.data)
    except (OSError, ValueError) as erro:
        parser.exit(1, f"Erro ao carregar a base: {erro}\n")
    try:
        iniciar(base)
    except (EOFError, KeyboardInterrupt):
        print("\nSessão encerrada.")


if __name__ == "__main__":
    main()
