# Relatório 2 — Eletrônica e PCB

Conversor CC-CC elevador (*boost*) de uma célula Li-ion 1S (3,0–4,2 V) para
5,0 V, ≥ 0,5 A, com o CI MT3608. Esquemático e placa de duas camadas no
KiCad 10.0.6.

Disciplina: Projeto de Sistemas Robóticos (DCC/UFMG, 2026/2) — Prof. Paulo Rezeck.
Autor: Daniel Terra Gomes — Pós-graduação, PPGCC/DCC/UFMG.

**[Relatório (PDF)](relatorio/relatorio2.pdf)**

## Especificação atendida

| Grandeza | Valor |
|---|---|
| Entrada | 3,0–4,2 V (Li-ion 1S), contida na faixa 2–24 V do MT3608 |
| Saída | 5,000 V nominais (divisor E96 110 kΩ / 15,0 kΩ) |
| Corrente de projeto | 0,5 A contínuos |
| Ciclo de trabalho | 0,40 → 0,16 ideal; 0,487 → 0,254 com perdas (pior caso) |
| Incerteza de V_out | σ ≈ 68 mV; ±3σ em 4,834–5,163 V (dentro de ±5 %) |
| Placa | 36 × 20 mm, 2 camadas, plano de terra contínuo na inferior |
| Verificações | ERC 0 · DRC 0 · paridade esquemático–placa 0 — pela linha de comando e no editor |

## Conteúdo da entrega

Conforme a Seção 5 do enunciado:

```
relatorio/relatorio2.pdf              o relatório
kicad/boost_mt3608.kicad_pro          projeto nativo do KiCad 10
kicad/boost_mt3608.kicad_sch          esquemático
kicad/boost_mt3608.kicad_pcb          placa
bom/bom_kicad.csv                     lista de materiais
exports/esquematico/                  esquemático: etapas (símbolos, ligações) e final (PDF)
exports/pcb/                          placa: etapas, camadas superior e inferior, todas as camadas (PDF)
exports/3d/                           vista 3D (isométrica, superior, inferior)
exports/boost_mt3608_gerber.zip       Gerber + furação
exports/relatorios/                   ERC e DRC: linha de comando e editor (antes e depois da correção, ver relatório §5)
capturas/                             capturas do editor KiCad (inclui ERC/DRC antes da correção)
```

## Componentes e datasheets

| Ref. | Peça | Datasheet |
|---|---|---|
| U1 | Aerosemi MT3608 (CI de referência) | [MT3608.pdf](https://www.olimex.com/Products/Breadboarding/BB-PWR-3608/resources/MT3608.pdf) |
| L1 | Abracon ASPI-4030S-7R5M, 7,5 µH | [ASPI-4030S.pdf](https://abracon.com/Magnetics/power/ASPI-4030S.pdf) |
| D1 | Diodes Inc. B340A, Schottky 40 V 3 A, SMA | [DS30891](https://www.diodes.com/assets/Datasheets/ds30891.pdf) |
| C1–C3 | Murata GRM31CR61C226ME15, 22 µF 16 V X5R 1206 | [especificação](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM31CR61C226ME15-01.pdf) |
| J1 | JST B2B-PH-K-S | [catálogo PH](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf) |

Alternativa avaliada: TI TPS61023 ([datasheet](https://www.ti.com/lit/ds/symlink/tps61023.pdf)).

## Abrir o projeto

KiCad 10 (os arquivos não abrem em versões anteriores). Abra
`kicad/boost_mt3608.kicad_pro`.

> O modelo 3D do footprint `L_Abracon_ASPI-4030S` não existe na biblioteca do
> KiCad 10.0.6; a placa usa o do Sunlord SWPA4030S, de dimensões idênticas
> (4,0 × 4,0 × 3,0 mm), apenas para a visualização.
