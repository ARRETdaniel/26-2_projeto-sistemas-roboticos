# Parâmetros de fatiamento — caixa planetária

Registro dos parâmetros adotados, conforme o item 5 do enunciado ("projeto do
fatiador ou registro dos parâmetros").

**Máquina:** Creality K1C · **Material:** Creality Hyper PETG
**Prioridade declarada:** minimizar tempo de impressão. A caixa é objeto de
demonstração cinemática, sem requisito de torque, de modo que resistência
mecânica foi deliberadamente trocada por tempo.

> **Estado:** plano de fabricação. Os valores efetivamente usados, o tempo e o
> consumo reais devem ser registados na §7 depois da impressão.

## 1. A máquina e o material

| Item | Valor | Fonte |
|---|---|---|
| Impressora | Creality K1C, CoreXY fechada | especificação do fabricante |
| Volume de construção | 220 × 220 × 250 mm | idem |
| Bico | 0,4 mm, ponta de aço endurecido | idem |
| Temperatura máxima do bico | 300 °C | idem |
| Velocidade máxima | 600 mm/s, aceleração 20 000 mm/s² | idem |
| Filamento | Creality Hyper PETG, 1,75 mm | idem |
| Bico (faixa do filamento) | 220–260 °C | rótulo do fabricante |
| Mesa (faixa do filamento) | 60–80 °C | idem |
| Velocidade (faixa do filamento) | 30–600 mm/s | idem |
| Ventoinha | 50 % | idem |

O Hyper PETG é formulado para alta velocidade, o que é conveniente aqui: a
prioridade de tempo não obriga a sair da faixa recomendada pelo fabricante.

## 2. Lista de peças

| Peça | Arquivo STL | Qtd. | Volume do sólido | Altura |
|---|---|---:|---:|---:|
| Sol (entrada) | `sol.stl` | 1 | 1,71 cm³ | 8,0 mm |
| Planeta | `planeta.stl` | **3** | 4,26 cm³ (cada) | 8,0 mm |
| Anel (coroa interna, fixo) | `anel.stl` | 1 | 9,05 cm³ | 8,0 mm |
| Porta-satélites (saída) | `porta_satelites.stl` | 1 | 13,88 cm³ | 12,6 mm |

Volume sólido total **37,4 cm³**, que em PETG (ρ ≈ 1,27 g/cm³) equivaleria a
**47,5 g** se as peças fossem maciças. Com os parâmetros da §4 espera-se algo
entre **15 e 20 g**. Confirmar no fatiador.

Ocupação de mesa: 29 % de 220 × 220 mm com as seis peças — cabem todas num
lote só.

## 3. Orientação

Todas as peças são exportadas **já na orientação de impressão**: eixo de
revolução paralelo a Z, face plana na mesa. Não rodar nada no fatiador.

- O perfil de evolvente fica determinado pelo contorno da camada, não pelo
  escalonamento entre camadas. É a orientação que preserva a função.
- Nenhuma peça exige suporte: pinos e furos são verticais e autoportantes.
- Em contrapartida, as linhas de camada ficam perpendiculares à força
  tangencial no dente. Como não há requisito de torque, essa é precisamente a
  fraqueza que se aceita trocar por tempo.

## 4. Parâmetros — perfil rápido

Base: perfil **K1C + Hyper PETG** do Creality Print. Alterações sobre o
padrão, todas na direção de tempo:

| Parâmetro | Valor | Efeito no tempo | Justificação |
|---|---|---|---|
| Altura de camada | **0,30 mm** | −33 % de camadas | 75 % do bico, limite usual. **Não afeta o dente**: o perfil está no plano XY, e os flancos são verticais |
| Primeira camada | 0,30 mm | — | adesão |
| Perímetros | **2** | grande | 2 × 0,42 = 0,84 mm por flanco; o dente (2,2 mm na primitiva) continua quase sólido |
| Preenchimento | **10 %**, grade ou *lightning* | grande | sem requisito de carga |
| Camadas sólidas topo/base | **3 / 2** | médio | 3 no topo por causa das fotografias |
| Gerador de paredes | **Arachne** | — | obrigatório, ver §5 |
| Bico | **250 °C** | permite vazão alta | dentro da faixa 220–260 |
| Mesa | **70 °C** | — | dentro da faixa 60–80 |
| Ventoinha | **50 %** | — | especificação do filamento |
| Velocidade | perfil Hyper (alta) | — | o filamento é formulado para isso |
| Perímetro externo | ≤ 200 mm/s | pequeno | preserva o flanco do dente |
| Suportes | **não** | — | geometria autoportante |
| Brim | ver §6 | — | — |
| Compensação de pé de elefante | 0,20 mm | — | PETG tende a alargar a 1.ª camada |
| **Compensação XY** | **−0,05 mm** | — | **ver §5, mudou por causa do PETG** |

## 5. As duas decisões que o PETG e a máquina alteraram

### 5.1 Compensação XY passa a −0,05 mm

Esta é a mudança mais importante em relação ao plano original, que era para PLA.

O modelo embute folga de dente δ = 0,30 mm por engrenamento, repartida em
0,15 mm por peça. Um processo FDM produz a parede externa **maior** que o
nominal; em PETG esse desvio é tipicamente maior que em PLA (retração de
0,4–0,6 %, contra ~0,3 % do PLA), e cresce com a velocidade.

O risco é direto e aritmético: se cada flanco sair 0,15 mm maior, os dois
flancos de um par consomem os 0,30 mm de folga e **a caixa trava**. Com PLA a
margem cobria o desvio esperado; com PETG a alta velocidade, não com folga.

Por isso parte-se de **−0,05 mm** em vez de 0,00. O cupom de teste (§6)
confirma ou corrige esse valor antes de comprometer as peças grandes.

Os furos correm menos risco: a folga diametral projetada é 0,35 mm, no topo da
faixa usual de 0,2–0,4 mm para ajuste deslizante, e o estreitamento típico de
furo em PETG (0,1–0,2 mm) ainda deixa margem.

### 5.2 Arachne é obrigatório

O topo do dente do sol mede **0,756 mm**, ou 1,8 larguras de extrusão de
0,42 mm. Sem gerador de paredes de largura variável, o topo sai vazado ou com
vinco. O Creality Print dispõe de Arachne; basta confirmar que está
selecionado em *Wall generator*.

Se por algum motivo não estiver disponível: reduzir a largura do perímetro
externo para 0,38 mm, ou imprimir o sol com 2 perímetros (que já é o valor
adotado).

## 5.3 Onde fatiar

A impressora não fatia: o K1C só executa `.gcode` pronto.

A página oficial de download do K1C marca o **Creality Print como suportado
apenas em Windows e Mac**, e há relatos no fórum da Creality de a build Linux
não trazer o perfil do K1C. Como a estação de trabalho da equipe é Linux,
adotou-se o **OrcaSlicer** (AppImage para Linux, com perfis do K1C e gerador
de paredes Arachne), com o Creality Print num PC Windows como alternativa.

Registrar na §7 qual foi efetivamente usado.

## 6. Estratégia de impressão

**Cupom de teste primeiro — isto economiza tempo, não gasta.**

Com os parâmetros acima, *sol + 1 planeta* saem em poucos minutos. Reimprimir
as seis peças porque a caixa travou custa muito mais do que esse cupom. Com
prazo curto, o cupom é a decisão rápida, não a cautelosa.

1. **Lote 1 — cupom:** `sol` + 1 × `planeta`. Medir (§8 do `IMPRESSAO.md`) e
   fixar a compensação XY.
2. **Lote 2 — resto:** `anel` + `porta_satelites` + 2 × `planeta`, tudo junto.
   Cabem folgadamente na mesa.

**Brim:** o K1C é fechado e o PETG adere bem a PEI texturado, de modo que o
brim provavelmente é dispensável e a sua remoção custa tempo. Recomendação:
sem brim no lote 1; no lote 2, brim de 3 mm **apenas no anel**, que é a peça de
82 mm e a de maior risco de descolamento. Se o lote 1 aderir sem dificuldade,
dispensar o brim também no anel.

**Adesivo:** em placa PEI **texturada**, não usar nada. Em PEI **lisa**, aplicar
uma camada fina de bastão de cola como agente **separador** — PETG adere
demais a PEI lisa e pode arrancar o revestimento ao ser removido.

## 7. Registro da impressão

Preencher após imprimir:

| Item | Planejado | Medido |
|---|---|---|
| Impressora / bico | K1C / 0,4 mm | |
| Material | Hyper PETG | |
| Fatiador e versão | Creality Print | |
| Altura de camada | 0,30 mm | |
| Compensação XY final | −0,05 mm | |
| Tempo do lote 1 | — | |
| Tempo do lote 2 | — | |
| Massa de filamento | ≈ 15–20 g | |
| Falhas observadas | — | |
