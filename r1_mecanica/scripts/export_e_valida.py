# -*- coding: utf-8 -*-
"""
Exporta STEP/STL e valida a caixa planetária.

Validações:
  V1  relações do enunciado: Zr = Zs + 2 Zp ; (Zs+Zr) mod n = 0 ; i = 1 + Zr/Zs
  V2  coerência das distâncias entre centros: m(Zs+Zp)/2 == m(Zr-Zp)/2
  V3  sólidos válidos, fechados (manifold) e com volume não nulo
  V4  não-interferência entre planetas adjacentes
  V5  não-interferência nos engrenamentos sol-planeta e planeta-anel,
      varrida ao longo de um ciclo completo de dente (prova de que gira)
  V6  espessura de parede do anel e folga do porta-satélites

Execução:
    ~/Applications/freecadcmd export_e_valida.py
"""

import os
import sys

import FreeCAD as App
import Part
import Mesh
import MeshPart

from pygears.computation import planetary_phase_angles

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
DOC_PATH = os.path.join(ROOT, "cad", "caixa_planetaria.FCStd")
STL_DIR = os.path.join(ROOT, "stl")
STEP_DIR = os.path.join(ROOT, "step")

# tesselagem do STL (mm). 0.02 mm é bem abaixo da resolução de uma FDM 0.4 mm.
LINEAR_DEFLECTION = 0.02
ANGULAR_DEFLECTION = 0.15

# Varredura de engrenamento: número de posições dentro de UM passo de dente do sol.
SWEEP_STEPS = 12

# Volume de interferência aceito como ruído numérico do núcleo BRep (mm^3).
EPS_VOL = 1e-6

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print("[{}] {:<52} {}".format("OK " if ok else "FALHA", name, detail))
    sys.stdout.flush()


def info(msg):
    print("[info] {}".format(msg))
    sys.stdout.flush()


def rot_z(shape, angle_deg, dx=0.0, dy=0.0, dz=0.0):
    """Cópia do sólido girada em torno de Z e transladada."""
    s = shape.copy()
    s.Placement = App.Placement(
        App.Vector(dx, dy, dz), App.Rotation(App.Vector(0, 0, 1), angle_deg)
    )
    return s


def main():
    for d in (STL_DIR, STEP_DIR):
        if not os.path.isdir(d):
            os.makedirs(d)

    doc = App.openDocument(DOC_PATH)
    doc.recompute()
    sheet = doc.getObject("Params")

    g = lambda a: float(sheet.get(a))  # noqa: E731
    modulo = g("modulo")
    Zs, Zp, Zr = int(g("Zs")), int(g("Zp")), int(g("Zr"))
    n = int(g("n_planetas"))
    razao_i = g("razao_i")
    a_centro = g("a_centro")
    delta = g("delta")

    sol = doc.getObject("sol")
    planeta = doc.getObject("planeta")
    anel = doc.getObject("anel")
    porta = doc.getObject("porta_satelites")

    info("m={} Zs={} Zp={} Zr={} n={} i={} a={} delta={}".format(
        modulo, Zs, Zp, Zr, n, razao_i, a_centro, delta))

    # ------------------------------------------------------------------
    # V1 / V2 — relações do enunciado
    # ------------------------------------------------------------------
    check("V1a  Zr = Zs + 2*Zp", Zr == Zs + 2 * Zp,
          "{} == {}".format(Zr, Zs + 2 * Zp))
    check("V1b  (Zs+Zr) divisivel por n", (Zs + Zr) % n == 0,
          "({}+{}) mod {} = {}".format(Zs, Zr, n, (Zs + Zr) % n))
    check("V1c  i = 1 + Zr/Zs", abs(razao_i - (1 + Zr / Zs)) < 1e-9,
          "i = {:.4f}".format(razao_i))
    check("V2   a(sol-plan) == a(plan-anel)",
          abs(modulo * (Zs + Zp) / 2 - modulo * (Zr - Zp) / 2) < 1e-9,
          "{:.3f} mm".format(a_centro))

    # ------------------------------------------------------------------
    # V3 — sólidos
    # ------------------------------------------------------------------
    pecas = [("sol", sol), ("planeta", planeta), ("anel", anel),
             ("porta_satelites", porta)]
    for nome, obj in pecas:
        sh = obj.Shape
        ok = sh.isValid() and len(sh.Solids) == 1 and sh.Volume > 0 and sh.isClosed()
        check("V3   solido '{}' valido/fechado/unico".format(nome), ok,
              "vol={:.1f} mm3, solidos={}, fechado={}".format(
                  sh.Volume, len(sh.Solids), sh.isClosed()))

    # ------------------------------------------------------------------
    # V4 — planetas adjacentes
    # ------------------------------------------------------------------
    d_tip_plan = modulo * (Zp + 2)
    d_entre_planetas = 2 * a_centro * __import__("math").sin(__import__("math").pi / n)
    folga_pp = d_entre_planetas - d_tip_plan
    check("V4   planetas adjacentes nao colidem", folga_pp > 0,
          "distancia={:.2f} mm, topo-a-topo={:.2f} mm, folga={:.2f} mm".format(
              d_entre_planetas, d_tip_plan, folga_pp))

    # ------------------------------------------------------------------
    # V6 — parede do anel e folga do porta-satélites
    # ------------------------------------------------------------------
    r_ext_anel = anel.Shape.BoundBox.XLength / 2.0
    r_raiz_anel = float(anel.root_diameter) / 2.0
    parede = r_ext_anel - r_raiz_anel
    check("V6a  parede do anel >= 2.0 mm", parede >= 2.0,
          "parede={:.2f} mm (ext={:.2f}, raiz={:.2f})".format(
              parede, r_ext_anel, r_raiz_anel))

    r_topo_anel = float(anel.addendum_diameter) / 2.0
    r_porta = g("r_porta")
    check("V6b  porta-satelites nao raspa no anel", r_porta < r_topo_anel,
          "r_porta={:.2f} < r_topo_anel={:.2f} (folga {:.2f} mm)".format(
              r_porta, r_topo_anel, r_topo_anel - r_porta))

    # ------------------------------------------------------------------
    # V5 — varredura de engrenamento
    # ------------------------------------------------------------------
    info("varredura de engrenamento em {} posicoes...".format(SWEEP_STEPS))
    sol_sh, plan_sh, anel_sh = sol.Shape, planeta.Shape, anel.Shape

    # Um passo de dente do sol = 360/Zs. O porta gira i vezes menos.
    passo_sol = 360.0 / Zs
    carrier_span = passo_sol / razao_i

    pior_sp, pior_pa = 0.0, 0.0
    orbitas = [k * 360.0 / n for k in range(n)]

    for step in range(SWEEP_STEPS):
        ca = carrier_span * step / float(SWEEP_STEPS)
        ph = planetary_phase_angles(Zs, Zp, Zr, orbitas, ca)

        s = rot_z(sol_sh, ph["sun_angle"])
        r = rot_z(anel_sh, ph["ring_angle"])

        for k in range(n):
            ang = ph["planet_orbits"][k]
            rad = __import__("math").radians(ang)
            p = rot_z(plan_sh, ph["planet_angles"][k],
                      a_centro * __import__("math").cos(rad),
                      a_centro * __import__("math").sin(rad))
            v_sp = s.common(p).Volume
            v_pa = r.common(p).Volume
            pior_sp = max(pior_sp, v_sp)
            pior_pa = max(pior_pa, v_pa)

    check("V5a  sol x planeta sem interferencia", pior_sp <= EPS_VOL,
          "pior volume comum = {:.3e} mm3".format(pior_sp))
    check("V5b  planeta x anel sem interferencia", pior_pa <= EPS_VOL,
          "pior volume comum = {:.3e} mm3".format(pior_pa))

    # ------------------------------------------------------------------
    # Exportação
    # ------------------------------------------------------------------
    info("exportando STEP...")
    Part.export([sol, planeta, anel, porta],
                os.path.join(STEP_DIR, "caixa_planetaria.step"))

    info("exportando STL (orientacao de impressao: eixo em Z, face na mesa)...")
    for nome, obj in pecas:
        mesh = MeshPart.meshFromShape(
            Shape=obj.Shape,
            LinearDeflection=LINEAR_DEFLECTION,
            AngularDeflection=ANGULAR_DEFLECTION,
            Relative=False,
        )
        path = os.path.join(STL_DIR, "{}.stl".format(nome))
        mesh.write(path)
        info("  {:<18} {:>7} facetas  {:>8.0f} kB".format(
            nome, mesh.CountFacets, os.path.getsize(path) / 1024.0))

    # ------------------------------------------------------------------
    n_falhas = sum(1 for _, ok, _ in results if not ok)
    print("")
    print("=" * 68)
    print("RESUMO: {} verificacoes, {} falha(s)".format(len(results), n_falhas))
    print("=" * 68)
    if n_falhas:
        for name, ok, detail in results:
            if not ok:
                print("  FALHA: {} -> {}".format(name, detail))


main()
