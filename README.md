# Projeto de Sistemas Robóticos - 2026/2

Entregas da disciplina **Projeto de Sistemas Robóticos**, DCC/UFMG,
2.º semestre de 2026 (Prof. Paulo Rezeck).

**Autor:** Daniel Terra Gomes - Pós-graduação, PPGCC/DCC/UFMG

---

## Relatórios

| # | Módulo | Relatório | Estado |
|---|---|---|---|
| **R1** | Mecânica e fabricação digital | [`Relatório 1 + Métodos generativos para novos padrões de transmissão`](r1_mecanica/relatorio/relatorio1.pdf) | entregue |
| R2 | Eletrônica e PCB | — | — |
| R3 | Embarcado, sensores e filtragem | — | — |
| R4 | Controle e odometria | — | — |
| R5 | ROS, navegação e integração | — | — |

---

## R1 - Caixa planetária de um estágio

Projeto, modelagem paramétrica e fabricação em FDM de uma caixa de engrenagens
planetária de um estágio: sol, três planetas, coroa interna e porta-satélites.

**[→ Relatório completo (PDF)](r1_mecanica/relatorio/relatorio1.pdf)**

| Grandeza | Valor |
|---|---|
| Módulo `m` | 1,5 mm |
| Dentes — sol / planeta / anel | 12 / 18 / 48 |
| Número de planetas `n` | 3 |
| Relação de transmissão `i` | 5 (anel fixo, entrada no sol, saída no porta-satélites) |
| Folga de dente `δ` | 0,30 mm por engrenamento |
| Material / máquina | Creality Hyper PETG · Creality K1C |

### O que este trabalho tem de característico

- **Modelo integralmente dirigido por planilha.** Nenhuma cota é digitada na
  geometria: todas as propriedades das quatro peças estão ligadas por expressão
  a um alias da planilha do FreeCAD. Alterar `Zs` faz `Zr` e `i` mudarem
  sozinhos.
- **41 verificações automáticas** — 13 sobre o sólido BRep e 28 sobre a malha
  exportada — incluindo uma varredura de interferência ao longo de um ciclo
  completo de dente (volume comum nulo em todas as posições).
- **Construção por script.** O modelo e as suas verificações são reconstruíveis
  do zero a partir do que está aqui; o repositório versiona o *procedimento*,
  não apenas o resultado.
- **Sem instrumentação dimensional**, o desvio do processo foi inferido do
  comportamento do mecanismo por duas vias independentes, que convergem para
  0,11–0,12 mm por superfície. Nenhuma medida foi inventada.

### Reprodução

```bash
cd r1_mecanica
~/Applications/freecadcmd scripts/build_caixa_planetaria.py   # modelo paramétrico
~/Applications/freecadcmd scripts/export_e_valida.py          # 13 verificações + STEP/STL
~/Applications/freecadcmd scripts/valida_impressao.py         # 28 verificações de impressão
python3 scripts/busca_relacoes.py                             # busca sobre conjuntos de dentes
```

Detalhes em [`r1_mecanica/README.md`](r1_mecanica/README.md).
