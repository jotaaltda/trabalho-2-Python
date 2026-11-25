# MRP II — Pedal Forte Bicicletas

Sistema de planejamento da produção da Pedal Forte Bicicletas. O menu do terminal reúne os cadastros, o estoque, as ordens e o planejamento de materiais para oito semanas.

## Executar no Linux

Na raiz do projeto, com Python 3.10 ou superior:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Os gráficos requerem um ambiente gráfico com um backend interativo do Matplotlib. Para executar em ambiente sem interface gráfica e salvar os PNGs, use `MPLBACKEND=Agg python main.py`. Os CSVs e PNGs ficam em `relatorios/`.

Para usar uma cópia independente da base de demonstração:

```bash
mkdir -p /tmp/pedal-forte-demo
cp data/{itens,estrutura,estoque,centros,roteiros,mps,ordens}.json /tmp/pedal-forte-demo/
cp data/movimentos.csv /tmp/pedal-forte-demo/
python main.py --data /tmp/pedal-forte-demo
```

## Ciclo de demonstração

1. Em **Cadastros → Exibir BOM**, consulte `PA-001`. Em **Estoque → Consultar kardex**, consulte `MP-202` para ver o alerta de segurança.
2. Em **Plano Mestre de Produção**, consulte o MPS e defina a demanda de `PA-001` na semana 2 como **10**.
3. Em **Executar MRP**, consulte `PA-001` e `SA-020`. A lista de exceções mostra as liberações anteriores à primeira semana. Pressione Enter para voltar.
4. Liste as ordens. Na primeira execução da base original, `OP-0001` corresponde a 10 bicicletas `PA-001`, com liberação em S1 e entrega em S2. Firme e libere essa ordem.
5. Consulte o CRP. O centro `CT-02` terá 5 h de carga em S1 para 4 h disponíveis.
6. Em **Ordens → Apontar produção ou receber compra**, informe `OP-0001`. Consulte o kardex de `PA-001` e `SA-020`. O primeiro passa de 0 a 10 unidades e o segundo, de 48 a 28.
7. Consulte o custo de `PA-001`, exporte os CSVs e abra os gráficos. Para visualizar a sobrecarga no gráfico, gere o gráfico de `CT-02` antes de apontar a produção.

Em uma OC liberada, a mesma opção de encerramento registra o recebimento total. Nos ajustes de estoque, quantidades negativas reduzem o saldo e positivas o aumentam. Use vírgula ou ponto como separador decimal.

## Requisitos e pontos de entrada

| Requisito | Implementação |
|---|---|
| RF01 | Menu principal e navegação em `menu.py`. |
| RF02 | Cadastro, alteração e listagem de itens em **Cadastros**. Validação em `itens.py`. |
| RF03 | Cadastro de componentes e exibição dos níveis 0, 1 e 2 em `estrutura.py`. |
| RF04, RF05 | Movimentações, saldo, kardex e alerta pelo menu **Estoque**. |
| RF06 | Cadastro de centros e roteiros de uma operação em **Cadastros**. |
| RF07 | Consulta e alteração da demanda em **Plano Mestre de Produção**. |
| RF08 | Registro semanal e exceções em **Executar MRP**. |
| RF09, RF10, RF11 | Geração de OPs e OCs pelo MRP e operação no menu **Ordens**. |
| RF12 | Carga de OPs liberadas, capacidade e sobrecarga no menu **Carga × capacidade**. |
| RF13 | Custo recursivo de materiais e mão de obra no menu **Custo padrão**. |
| RF14 | Posição de estoque e ordens no menu **Exportar CSV**. |
| RF15 | Carregamento inicial e gravação automática em `persistencia.py`. |
| RF16 | Quatro gráficos em `graficos.py`, exibidos pelo menu **Gráficos** e gravados em PNG. |

## Onde os dados são salvos

Na primeira alteração, o programa grava `estado.json` na pasta de dados. Nas próximas execuções, ele carrega esse arquivo. Use uma sessão por pasta de dados.

## LINK DA APRESENTAÇÃO!!!!!!!!!!!!!!!!!!!!!!!

https://youtu.be/uMkM88DnuOQ
