# Sensor de distância por infravermelho — TCRT5000

Relatório da Aula 13 de Projeto de Sistemas Robóticos (DCC/UFMG, 2026/2,
Prof. Paulo Rezeck). Trabalho em equipe: Chrystian Martins Soares Costa,
Daniel Terra Gomes, Isabela Saenz Cardoso e Paloma Fernanda Sabino Tavares.

**[→ Relatório (PDF)](relatorio/main.pdf)**

## Resultado

| Grandeza | Valor |
|---|---|
| Modelo | d = g0 + g1/√S, com S = max(0, adc_off − adc_on) |
| Ganhos (ajuste em 20–100 mm, 9 pontos) | g0 = 13,46 ± 2,20 mm · g1 = 308,1 ± 12,5 mm·contagem^½ |
| Erro no ajuste | RMS 2,7 mm |
| Validação (fora do ajuste) | +0,9 mm em 110 mm · +2,4 mm em 120 mm |
| Alcance estimado | 140–150 mm (200 mm está dentro do fundo) |

## Conteúdo

```
relatorio/main.pdf                      o relatório
dados/planilha_tcrt5000.xlsx            planilha com fórmulas: z, d_est, erro, g0 e g1
dados/caracterizacao.csv                distância na régua e sinal médio (12 pontos)
dados/resultados.csv                    z, d_est, erro e mm por contagem, por distância
dados/registro_serial.csv               31 linhas do sketch final, transcritas da captura
firmware/src/main.cpp                   sketch final corrigido: imprime "sinal,mm"
firmware/ensaio_2026-10-06/main.cpp     sketch usado no ensaio de 06/10/2026
firmware/platformio.ini                 Arduino Mega 2560
```

## Gravar o sketch

```bash
cd firmware
pio run -t upload && pio device monitor
```

A versão em `firmware/src/` imprime `sinal,mm`, o formato que o
`plot_serial.py` do roteiro desenha. Ela foi compilada para o ATmega2560, mas
não chegou a ser gravada na placa; o registro do relatório vem da versão de
`ensaio_2026-10-06/` (ver Seção 6 do relatório).
