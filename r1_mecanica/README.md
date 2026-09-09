# Relatório 1 — Mecânica e fabricação digital

Caixa planetária de um estágio, modelada de forma paramétrica em FreeCAD 1.1.3
e fabricada em FDM (Creality K1C, Creality Hyper PETG).

Disciplina: Projeto de Sistemas Robóticos (DCC/UFMG, 2026/2) — Prof. Paulo Rezeck.
Autor: Daniel Terra Gomes — Pós-graduação, PPGCC/DCC/UFMG.

**[→ Relatório (PDF)](relatorio/relatorio1.pdf)**

## Especificação atendida

| Grandeza | Valor |
|---|---|
| Módulo `m` | 1,5 mm |
| Dentes do sol `Zs` | 12 |
| Dentes do planeta `Zp` | 18 |
| Dentes do anel `Zr` | 48 (= `Zs + 2 Zp`) |
| Planetas `n` | 3 (`(Zs+Zr) mod n = 0`) |
| Relação `i` | 5 (= `1 + Zr/Zs`) |
| Folga de dente `δ` | 0,30 mm por engrenamento |
| Compensação de contorno no fatiador | −0,05 mm |

Resultado: o conjunto monta e **gira**, com movimento apertado. Sem
instrumentação dimensional disponível, o desvio do processo foi inferido do
comportamento do mecanismo por duas vias independentes (folga de dente e ajuste
pino–furo), que convergem para 0,11–0,12 mm por superfície. Ver Seção 5 do
relatório.

## Conteúdo da entrega

Conforme a Seção 5 do enunciado:

```
relatorio/relatorio1.pdf     o relatório, 19 páginas
cad/caixa_planetaria.FCStd   modelo nativo, dirigido por planilha
step/caixa_planetaria.step   intercâmbio STEP
stl/                         as quatro peças, em orientação de impressão
slicer/                      registro dos parâmetros de fatiamento
4_TUDO_005.gcode             o g-code efetivamente usado na impressão
stl/anel.3mf                 projeto do fatiador (uma peça, como amostra)
figuras/                     figuras do relatório, geradas a partir do BRep
fotos/                       fotografias das peças e da impressão
scripts/                     construção do modelo, verificações e busca
```

## Os scripts

O sólido não é desenhado a cliques: é construído por script a partir de uma
planilha de parâmetros. Nenhuma cota é digitada na geometria — cada propriedade
das quatro peças está ligada por expressão a um alias da planilha, de modo que
alterar `Zs` faz `Zr` e `i` mudarem sozinhos.

| Script | O que faz |
|---|---|
| `build_caixa_planetaria.py` | Constrói `cad/caixa_planetaria.FCStd` do zero |
| `export_e_valida.py` | 13 verificações sobre o sólido + exporta STEP e STL |
| `valida_impressao.py` | 28 verificações sobre a malha exportada e a fabricabilidade |
| `busca_relacoes.py` | Busca sobre conjuntos de dentes válidos (Seção 8 do relatório) |

Execução (FreeCAD 1.1.3 em modo console; `busca_relacoes.py` é Python puro):

```bash
~/Applications/freecadcmd scripts/build_caixa_planetaria.py
~/Applications/freecadcmd scripts/export_e_valida.py
~/Applications/freecadcmd scripts/valida_impressao.py
python3 scripts/busca_relacoes.py
```

As 41 verificações (13 + 28) falham explicitamente se alguma condição não for
satisfeita. Entre elas está uma varredura de interferência ao longo de um ciclo
completo de dente, que posiciona sol, três planetas e anel segundo a cinemática
exata do mecanismo e calcula o volume de interseção booleana de cada par
engrenado — nulo em todas as posições avaliadas.

O complemento `freecad.gears` (FCGear) é necessário para os dentes de evolvente
e para a coroa interna.
