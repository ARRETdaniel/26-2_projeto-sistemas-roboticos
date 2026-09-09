# -*- coding: utf-8 -*-
"""
Validação de prontidão para impressão (pré-voo do R1).

Complementa `export_e_valida.py`, que valida o SÓLIDO BRep. Este script valida
o que efetivamente vai para a impressora — a MALHA exportada — mais as
propriedades de engrenamento e de fabricabilidade que o BRep não revela.

  P1  integridade da malha de cada STL (manifold, auto-interseção, sólido)
  P2  escala, origem e orientação dos arquivos exportados
  P3  espessura do topo do dente contra a largura de extrusão
  P4  razão de condução (contact ratio) dos dois engrenamentos
  P5  espessuras mínimas de parede e esbeltez dos pinos
  P6  ocupação de mesa e plano de lotes

Execução:  ~/Applications/freecadcmd valida_impressao.py
"""

import math
import os
import sys

import FreeCAD as App
import Mesh

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
DOC_PATH = os.path.join(ROOT, "cad", "caixa_planetaria.FCStd")
STL_DIR = os.path.join(ROOT, "stl")

# --- premissas de processo -------------------------------------------------
# Máquina real: Creality K1C (fechada, CoreXY, mesa 220x220x250, bico 0,4 mm
# de aço endurecido, até 600 mm/s). Material: Creality Hyper PETG.
LARGURA_EXTRUSAO = 0.42     # mm, largura de trilha típica p/ bico 0,4
MIN_TOPO_DENTE = 2 * LARGURA_EXTRUSAO   # topo do dente deve caber >= 2 trilhas
MIN_PAREDE = 2 * LARGURA_EXTRUSAO
MESA = (220.0, 220.0)       # mm, mesa do K1C
ESBELTEZ_MAX = 6.0          # altura/diâmetro máx. aceitável p/ pino vertical

# NOTA: as verificações de fabricabilidade dependem do BICO, não do material.
# Trocar o bico de 0,4 mm invalida P3 e P5 e obriga a reexecutar este script.

results = []


def check(nome, ok, detalhe="", severidade="BLOQUEIA"):
    results.append((nome, bool(ok), detalhe, severidade))
    tag = "OK " if ok else ("FALHA" if severidade == "BLOQUEIA" else "AVISO")
    print("[{}] {:<46} {}".format(tag, nome, detalhe))
    sys.stdout.flush()


def info(m):
    print("[info] {}".format(m))
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# P1 — integridade da malha exportada
# ---------------------------------------------------------------------------
def valida_malhas():
    info("P1 — integridade das malhas exportadas")
    for nome in ("sol", "planeta", "anel", "porta_satelites"):
        path = os.path.join(STL_DIR, nome + ".stl")
        if not os.path.exists(path):
            check("P1 {} existe".format(nome), False, "arquivo ausente")
            continue

        m = Mesh.Mesh(path)

        # Defeitos que impedem o fatiamento. Um deles presente e o arquivo
        # nao deve ir para a impressora.
        graves = []
        if m.hasNonManifolds():
            graves.append("não-manifold")
        if m.hasSelfIntersections():
            graves.append("auto-interseção")
        if m.hasInvalidPoints():
            graves.append("pontos inválidos")
        if m.hasNonUniformOrientedFacets():
            graves.append("normais não uniformes ({})".format(
                m.countNonUniformOrientedFacets()))
        if not m.isSolid():
            graves.append("não é sólido fechado")
        ncomp = m.countComponents()
        if ncomp != 1:
            graves.append("{} componentes".format(ncomp))

        check("P1 malha '{}' sem defeito grave".format(nome), not graves,
              "{} facetas, vol={:.1f} mm3, sólido={}, comps={}{}".format(
                  m.CountFacets, m.Volume, m.isSolid(), ncomp,
                  "" if not graves else ", DEFEITOS: " + "; ".join(graves)))

        # Junções em T (um vértice repousando sobre a aresta de um triângulo
        # vizinho). Sao subproduto normal da tesselagem independente de faces
        # adjacentes no CAD. NAO afetam o fatiamento: a malha continua
        # estanque, manifold e de componente único. Registrado como aviso
        # apenas para nao passar despercebido numa auditoria da malha.
        if m.hasPointsOnEdge():
            check("P1b malha '{}' sem junções em T".format(nome), False,
                  "junções em T presentes; malha estanque e manifold, "
                  "inofensivo para o fatiador", "AVISO")


# ---------------------------------------------------------------------------
# P2 — escala, origem, orientação
# ---------------------------------------------------------------------------
def valida_colocacao(doc):
    info("P2 — escala, origem e orientação")
    esperado = {
        # nome: (dx, dy, dz) aproximados em mm
        "sol": (21.0, 21.0, 8.0),
        "planeta": (30.0, 30.0, 8.0),
        "anel": (82.0, 82.0, 8.0),
        "porta_satelites": (66.0, 66.0, 12.6),
    }
    for nome, (ex, ey, ez) in esperado.items():
        m = Mesh.Mesh(os.path.join(STL_DIR, nome + ".stl"))
        bb = m.BoundBox
        dx, dy, dz = bb.XLength, bb.YLength, bb.ZLength
        escala_ok = (abs(dx - ex) < 0.6 and abs(dy - ey) < 0.6
                     and abs(dz - ez) < 0.2)
        check("P2a escala '{}'".format(nome), escala_ok,
              "{:.2f} x {:.2f} x {:.2f} mm (esperado ~{} x {} x {})".format(
                  dx, dy, dz, ex, ey, ez))
        # a peça deve assentar em z=0 (sem afundar na mesa nem flutuar)
        check("P2b assenta em z=0 '{}'".format(nome), abs(bb.ZMin) < 1e-6,
              "ZMin = {:.6f} mm".format(bb.ZMin))


# ---------------------------------------------------------------------------
# P3 — espessura do topo do dente
# ---------------------------------------------------------------------------
def largura_topo(shape, z, r_topo, tol=0.02):
    """Mede a largura de cada topo de dente na secção z.

    Seleciona os pontos do contorno externo que estão a menos de `tol` do raio
    de topo, agrupa-os por descontinuidade angular e devolve a corda de cada
    grupo.
    """
    melhores = []
    for wire in shape.slice(App.Vector(0, 0, 1), z):
        n = max(2000, int(wire.Length / 0.02))
        pts = [(p.x, p.y) for p in wire.discretize(Number=n)]
        sel = []
        for x, y in pts:
            r = math.hypot(x, y)
            if abs(r - r_topo) <= tol:
                sel.append((math.atan2(y, x), x, y))
        if not sel:
            continue
        sel.sort()
        # agrupa por salto angular
        grupos, atual = [], [sel[0]]
        for k in range(1, len(sel)):
            if sel[k][0] - sel[k - 1][0] > 0.02:      # ~1,1 grau
                grupos.append(atual); atual = [sel[k]]
            else:
                atual.append(sel[k])
        grupos.append(atual)
        # junta o primeiro e o último se forem contíguos em -pi/+pi
        if len(grupos) > 1 and (grupos[0][0][0] + 2 * math.pi
                                - grupos[-1][-1][0]) < 0.02:
            grupos[0] = grupos[-1] + grupos[0]; grupos.pop()
        for g in grupos:
            if len(g) < 2:
                continue
            _, x0, y0 = g[0]
            _, x1, y1 = g[-1]
            melhores.append(math.hypot(x1 - x0, y1 - y0))
    return melhores


def valida_topo_dente(doc, sheet):
    info("P3 — espessura do topo do dente vs largura de extrusão")
    z = float(sheet.get("h_engr")) / 2.0
    for nome, obj_name in (("sol", "sol"), ("planeta", "planeta")):
        obj = doc.getObject(obj_name)
        r_topo = float(obj.addendum_diameter) / 2.0
        larguras = largura_topo(obj.Shape, z, r_topo)
        if not larguras:
            check("P3 topo '{}'".format(nome), False,
                  "não foi possível medir", "AVISO")
            continue
        w = min(larguras)
        m_mod = float(sheet.get("modulo"))
        # Limite MECANICO: topo abaixo de 0,25 m indica dente pontiagudo,
        # que e um erro de projeto. Bloqueia.
        check("P3a topo '{}' >= 0,25 m ({:.3f} mm)".format(nome, 0.25 * m_mod),
              w >= 0.25 * m_mod,
              "menor topo = {:.3f} mm em {} dentes".format(w, len(larguras)))
        # Limite de EXTRUSAO: abaixo de 2 trilhas o topo depende de extrusao
        # de largura variavel (Arachne). Nao bloqueia: e mitigavel no fatiador.
        check("P3b topo '{}' >= 2 trilhas ({:.2f} mm)".format(
                  nome, MIN_TOPO_DENTE),
              w >= MIN_TOPO_DENTE,
              "{:.3f} mm = {:.2f} trilhas de {:.2f} mm; exige fatiador com "
              "largura variável (Arachne)".format(
                  w, w / LARGURA_EXTRUSAO, LARGURA_EXTRUSAO),
              "AVISO")


# ---------------------------------------------------------------------------
# P4 — razão de condução
# ---------------------------------------------------------------------------
def valida_contact_ratio(doc, sheet):
    info("P4 — razão de condução (contact ratio)")
    m = float(sheet.get("modulo"))
    alpha = math.radians(float(sheet.get("alpha")))
    a = float(sheet.get("a_centro"))

    sol, plan, anel = (doc.getObject(n) for n in ("sol", "planeta", "anel"))
    ra_s = float(sol.addendum_diameter) / 2
    ra_p = float(plan.addendum_diameter) / 2
    ra_r = float(anel.addendum_diameter) / 2
    rb_s = float(sol.pitch_diameter) / 2 * math.cos(alpha)
    rb_p = float(plan.pitch_diameter) / 2 * math.cos(alpha)
    rb_r = float(anel.pitch_diameter) / 2 * math.cos(alpha)

    passo_base = math.pi * m * math.cos(alpha)

    # par externo sol-planeta
    eps_sp = (math.sqrt(ra_s**2 - rb_s**2) + math.sqrt(ra_p**2 - rb_p**2)
              - a * math.sin(alpha)) / passo_base
    # par interno planeta-anel
    eps_pa = (math.sqrt(ra_p**2 - rb_p**2) - math.sqrt(ra_r**2 - rb_r**2)
              + a * math.sin(alpha)) / passo_base

    for nome, eps in (("sol-planeta", eps_sp), ("planeta-anel", eps_pa)):
        check("P4 razão de condução {} > 1,2".format(nome), eps > 1.2,
              "epsilon = {:.3f}".format(eps))


# ---------------------------------------------------------------------------
# P5 — paredes e pinos
# ---------------------------------------------------------------------------
def valida_paredes(doc, sheet):
    info("P5 — paredes mínimas e esbeltez dos pinos")
    g = lambda a: float(sheet.get(a))  # noqa: E731

    anel = doc.getObject("anel")
    parede_anel = anel.Shape.BoundBox.XLength / 2 - float(anel.root_diameter) / 2
    check("P5a parede do anel >= {:.2f} mm".format(MIN_PAREDE),
          parede_anel >= MIN_PAREDE, "{:.2f} mm".format(parede_anel))

    sol = doc.getObject("sol")
    parede_sol = (float(sol.root_diameter) - g("d_furo_sol")) / 2
    check("P5b parede sol furo->raiz >= {:.2f} mm".format(MIN_PAREDE),
          parede_sol >= MIN_PAREDE, "{:.2f} mm".format(parede_sol))

    plan = doc.getObject("planeta")
    parede_plan = (float(plan.root_diameter) - g("d_furo_plan")) / 2
    check("P5c parede planeta furo->raiz >= {:.2f} mm".format(MIN_PAREDE),
          parede_plan >= MIN_PAREDE, "{:.2f} mm".format(parede_plan))

    esb = g("h_pino") / g("d_pino")
    check("P5d esbeltez do pino <= {:.1f}".format(ESBELTEZ_MAX),
          esb <= ESBELTEZ_MAX,
          "h/d = {:.2f}/{:.2f} = {:.2f}".format(g("h_pino"), g("d_pino"), esb))

    # folga real pino->furo do planeta
    folga = g("d_furo_plan") - g("d_pino")
    check("P5e folga diametral pino-planeta em [0,25; 0,50] mm",
          0.25 <= folga <= 0.50, "{:.2f} mm".format(folga))


# ---------------------------------------------------------------------------
# P6 — mesa
# ---------------------------------------------------------------------------
def valida_mesa():
    info("P6 — ocupação de mesa (referência {} x {} mm)".format(*MESA))
    dims = {}
    for nome in ("sol", "planeta", "anel", "porta_satelites"):
        bb = Mesh.Mesh(os.path.join(STL_DIR, nome + ".stl")).BoundBox
        dims[nome] = (bb.XLength, bb.YLength)

    maior = max(max(d) for d in dims.values())
    check("P6a maior peça cabe na mesa", maior + 10 <= min(MESA),
          "maior dimensão = {:.1f} mm".format(maior))

    # lote único: anel + porta lado a lado, sol e 3 planetas na faixa restante
    larg = dims["anel"][0] + dims["porta_satelites"][0] + 3 * 5.0
    check("P6b anel + porta lado a lado cabem", larg <= MESA[0],
          "{:.1f} mm de largura necessária".format(larg))

    area_total = sum(d[0] * d[1] for n, d in dims.items()
                     if n != "planeta") + 3 * dims["planeta"][0] * dims["planeta"][1]
    check("P6c área ocupada < 60% da mesa",
          area_total < 0.60 * MESA[0] * MESA[1],
          "{:.0f} mm2 de {:.0f} mm2 ({:.0f}%)".format(
              area_total, MESA[0] * MESA[1],
              100 * area_total / (MESA[0] * MESA[1])), "AVISO")


def main():
    doc = App.openDocument(DOC_PATH)
    doc.recompute()
    sheet = doc.getObject("Params")

    valida_malhas()
    valida_colocacao(doc)
    valida_topo_dente(doc, sheet)
    valida_contact_ratio(doc, sheet)
    valida_paredes(doc, sheet)
    valida_mesa()

    bloqueios = [r for r in results if not r[1] and r[3] == "BLOQUEIA"]
    avisos = [r for r in results if not r[1] and r[3] == "AVISO"]
    print("")
    print("=" * 70)
    print("RESUMO: {} verificações · {} bloqueio(s) · {} aviso(s)".format(
        len(results), len(bloqueios), len(avisos)))
    print("=" * 70)
    for nome, _, detalhe, sev in bloqueios + avisos:
        print("  {}: {} -> {}".format(sev, nome, detalhe))
    if not bloqueios:
        print("  PRONTO PARA IMPRESSÃO (nenhum bloqueio)")


main()
