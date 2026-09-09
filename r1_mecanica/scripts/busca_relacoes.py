#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca exaustiva sobre conjuntos de dentes válidos para a caixa planetária.

Exploração paramétrica generativa no sentido de Krish (2011): a topologia é
fixa (planetária de um estágio) e varre-se o espaço de parâmetros discretos
(Zs, Zp, n), filtrando por envelopes de viabilidade e de manufaturabilidade.

Restrições aplicadas, em ordem:
  R1  engrenamento   Zr = Zs + 2 Zp
  R2  montagem       (Zs + Zr) mod n == 0
  R3  planetas adjacentes não colidem:  2 a sin(pi/n) > m (Zp + 2)
  R4  Zs >= ZS_MIN   (limite prático de fabricação do pinhão em FDM)
  R5  envelope       diametro externo do anel <= OD_MAX

Objetivo: maximizar i = 1 + Zr/Zs.

Saída: tabela dos conjuntos válidos, fronteira de Pareto (i x diâmetro) e a
taxa de sobrevivência a cada restrição — que é o resultado mais informativo
de uma busca restrita.

Execução:  python3 busca_relacoes.py
"""

import json
import math
import os

MODULO = 1.5          # mm, fixo (mesmo gerador de dentes do modelo)
ESP_ANEL = 5.0        # mm, espessura nominal da parede do anel
OD_MAX = 82.0         # mm, diâmetro externo do conjunto atual
ZS_MIN, ZS_MAX = 10, 30
ZP_MIN, ZP_MAX = 8, 40
N_OPCOES = (3, 4, 5)

# Limite teórico de talhe para dentado normal de 20 graus. Abaixo dele há
# adelgaçamento de pé; NÃO é um critério de exclusão aqui, apenas anotado,
# porque o conjunto de referência do enunciado (Zs = 12) já está abaixo.
Z_SEM_TALHE = 17

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
OUT_JSON = os.path.join(ROOT, "figuras", "busca_relacoes.json")
OUT_TEX = os.path.join(ROOT, "relatorio", "tab_busca.tex")


def main():
    contadores = {"gerados": 0, "R2": 0, "R3": 0, "R5": 0}
    validos = []

    for zs in range(ZS_MIN, ZS_MAX + 1):
        for zp in range(ZP_MIN, ZP_MAX + 1):
            zr = zs + 2 * zp                      # R1 por construção
            for n in N_OPCOES:
                contadores["gerados"] += 1

                if (zs + zr) % n != 0:            # R2
                    continue
                contadores["R2"] += 1

                a = MODULO * (zs + zp) / 2.0      # R3
                if 2 * a * math.sin(math.pi / n) <= MODULO * (zp + 2):
                    continue
                contadores["R3"] += 1

                od = MODULO * zr + 2 * ESP_ANEL   # R5
                if od > OD_MAX:
                    continue
                contadores["R5"] += 1

                validos.append({
                    "Zs": zs, "Zp": zp, "Zr": zr, "n": n,
                    "i": 1 + zr / zs,
                    "od": od,
                    "a": a,
                    "talhe": zs < Z_SEM_TALHE,
                })

    validos.sort(key=lambda d: (-d["i"], d["od"]))

    # Fronteira de Pareto: maximizar i, minimizar diâmetro externo.
    pareto = []
    melhor_od = float("inf")
    for c in validos:                              # já ordenado por i decrescente
        if c["od"] < melhor_od:
            pareto.append(c)
            melhor_od = c["od"]

    print("=" * 74)
    print("BUSCA SOBRE CONJUNTOS DE DENTES  (m = {} mm, OD <= {} mm)".format(
        MODULO, OD_MAX))
    print("=" * 74)
    print("candidatos gerados                     : {:6d}".format(contadores["gerados"]))
    print("  sobrevivem a R2 (montagem)           : {:6d}  ({:.1f} %)".format(
        contadores["R2"], 100.0 * contadores["R2"] / contadores["gerados"]))
    print("  sobrevivem a R3 (planetas adjacentes): {:6d}  ({:.1f} %)".format(
        contadores["R3"], 100.0 * contadores["R3"] / contadores["gerados"]))
    print("  sobrevivem a R5 (envelope)           : {:6d}  ({:.1f} %)".format(
        contadores["R5"], 100.0 * contadores["R5"] / contadores["gerados"]))
    print("")
    print("FRONTEIRA DE PARETO (maior i, menor diametro):")
    print("  {:>4} {:>4} {:>4} {:>3} {:>7} {:>8}  {}".format(
        "Zs", "Zp", "Zr", "n", "i", "OD(mm)", "talhe(Zs<17)"))
    for c in pareto:
        print("  {:>4} {:>4} {:>4} {:>3} {:>7.3f} {:>8.1f}  {}".format(
            c["Zs"], c["Zp"], c["Zr"], c["n"], c["i"], c["od"],
            "sim" if c["talhe"] else "nao"))

    atual = next((c for c in validos
                  if c["Zs"] == 12 and c["Zp"] == 18 and c["n"] == 3), None)
    print("")
    if atual:
        print("conjunto adotado no relatorio: Zs=12 Zp=18 Zr=48 n=3 "
              "i={:.3f} OD={:.1f} mm".format(atual["i"], atual["od"]))
        melhor = pareto[0]
        print("melhor i encontrado          : Zs={} Zp={} Zr={} n={} "
              "i={:.3f} OD={:.1f} mm".format(
                  melhor["Zs"], melhor["Zp"], melhor["Zr"], melhor["n"],
                  melhor["i"], melhor["od"]))
        print("ganho relativo em i          : {:+.1f} %".format(
            100.0 * (melhor["i"] / atual["i"] - 1)))
        print("variacao de diametro         : {:+.1f} mm".format(
            melhor["od"] - atual["od"]))

    with open(OUT_JSON, "w") as fh:
        json.dump({"contadores": contadores, "validos": validos,
                   "pareto": pareto}, fh, indent=1)

    # ---- tabela LaTeX pronta para \input ---------------------------------
    linhas = []
    for c in pareto:
        marca = r"\textbf{" if (c["Zs"] == 12 and c["Zp"] == 18) else "{"
        linhas.append(
            "    {}{}}} & {} & {} & {} & {:.2f} & {:.1f} & {} \\\\".format(
                marca, c["Zs"], c["Zp"], c["Zr"], c["n"], c["i"], c["od"],
                "sim" if c["talhe"] else "não"))
    if atual and not any(c["Zs"] == 12 and c["Zp"] == 18 for c in pareto):
        linhas.append(r"    \midrule")
        linhas.append(
            "    \\textbf{{12}} & 18 & 48 & 3 & {:.2f} & {:.1f} & sim \\\\".format(
                atual["i"], atual["od"]))

    with open(OUT_TEX, "w") as fh:
        fh.write("% gerado por scripts/busca_relacoes.py — não editar à mão\n")
        fh.write("\n".join(linhas) + "\n")
    print("\nescrito {}".format(OUT_TEX))
    print("escrito {}".format(OUT_JSON))


if __name__ == "__main__":
    main()
