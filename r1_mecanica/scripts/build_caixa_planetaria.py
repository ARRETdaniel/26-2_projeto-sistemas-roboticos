# -*- coding: utf-8 -*-
"""
Caixa planetária de um estágio — modelo paramétrico FreeCAD.

Relatório 1, Projeto de Sistemas Robóticos (DCC/UFMG, 2026/2).

Todo o sólido é dirigido por uma planilha (`Params`). Nenhuma cota é digitada
na geometria: cada propriedade das quatro peças está ligada por expressão a um
alias da planilha. Alterar `modulo`, `Zs`, `Zp`, `n_planetas`, `delta` ou
qualquer diâmetro de furo na planilha e recomputar o documento reconstrói o
conjunto inteiro, sem redesenho manual.

Dentes gerados pela ferramenta de evolvente do CAD (FCGear / freecad.gears),
conforme o enunciado.

Convenção de fase (documentada em pygears/computation.py do FCGear):
    engrenagem externa  -> um DENTE centrado no eixo +x local
    engrenagem interna  -> um VÃO   centrado no eixo +x local
donde, com o porta-satélites em zero:
    fase_anel      = 180 * (Zp + 1) / Zr
    fase_planeta_k = orbita_k * (1 - Zr/Zp) + 180 * (Zp + 1) / Zp

Execução:
    ~/Applications/freecadcmd build_caixa_planetaria.py
"""

import os
import sys

import FreeCAD as App
import Part  # noqa: F401  (registra os tipos Part::* no documento)

from freecad.gears.features import InvoluteGear, InternalInvoluteGear

# --------------------------------------------------------------------------
# Caminhos
# --------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)            # r1_mecanica/
CAD_DIR = os.path.join(ROOT, "cad")
DOC_PATH = os.path.join(CAD_DIR, "caixa_planetaria.FCStd")

# --------------------------------------------------------------------------
# Parâmetros de projeto (valores iniciais da planilha)
#
# Conjunto recomendado pelo enunciado, adequado a FDM:
#   Zr = Zs + 2*Zp  ->  48 = 12 + 2*18            (condição de engrenamento)
#   (Zs + Zr) % n   ->  60 % 3 == 0               (condição de montagem)
#   i = 1 + Zr/Zs   ->  5                         (anel fixo, saída no porta)
# --------------------------------------------------------------------------
PARAMS = [
    # (alias, valor/fórmula, unidade p/ exibição, comentário)
    ("modulo",        "1.5",                      "mm", "Módulo m, igual para sol, planetas e anel"),
    ("Zs",            "12",                       "",   "Dentes do sol (entrada)"),
    ("Zp",            "18",                       "",   "Dentes de cada planeta"),
    ("n_planetas",    "3",                        "",   "Número de planetas"),
    ("alpha",         "20",                       "°",  "Ângulo de pressão"),
    ("delta",         "0.3",                      "mm", "Folga de dente (backlash) total por engrenamento"),

    # --- derivados das relações do enunciado -------------------------------
    ("Zr",            "=Zs + 2 * Zp",             "",   "Dentes do anel  (Zr = Zs + 2 Zp)"),
    ("razao_i",       "=1 + Zr / Zs",             "",   "Relação de transmissão (anel fixo)"),
    ("checa_montagem", "=mod(Zs + Zr; n_planetas)", "", "Deve ser 0: (Zs+Zr) divisível por n"),
    ("a_centro",      "=modulo * (Zs + Zp) / 2",  "mm", "Distância entre centros sol-planeta"),
    ("a_anel",        "=modulo * (Zr - Zp) / 2",  "mm", "Distância planeta-anel (deve igualar a_centro)"),
    ("backlash_peca", "=delta / 2",               "mm", "Backlash aplicado a CADA peça do par"),

    # --- larguras e espessuras --------------------------------------------
    ("h_engr",        "8",                        "mm", "Largura de face das engrenagens"),
    ("esp_anel",      "5",                        "mm", "Espessura da parede do anel"),
    ("t_porta",       "4",                        "mm", "Espessura do disco do porta-satélites"),
    ("folga_axial",   "0.6",                      "mm", "Folga axial planeta/porta-satélites"),
    ("h_pino",        "=h_engr + folga_axial",    "mm", "Altura dos pinos do porta-satélites"),

    # --- eixos e furos (ajustáveis por parâmetro, item 5 pts do enunciado) --
    ("d_eixo_sol",    "5",                        "mm", "Diâmetro nominal do eixo de entrada"),
    ("d_pino",        "4",                        "mm", "Diâmetro do pino do porta-satélites"),
    ("d_eixo_saida",  "6",                        "mm", "Diâmetro nominal do eixo de saída"),
    ("folga_furo",    "0.35",                     "mm", "Folga diametral de furo em FDM"),
    ("d_furo_sol",    "=d_eixo_sol + folga_furo", "mm", "Furo modelado no sol"),
    ("d_furo_plan",   "=d_pino + folga_furo",     "mm", "Furo modelado no planeta"),
    ("d_furo_saida",  "=d_eixo_saida + folga_furo", "mm", "Furo modelado no porta-satélites"),

    # --- tolerâncias de dente (FCGear) ------------------------------------
    ("clearance",     "0.25",                     "",   "Folga radial pé/topo, fração do módulo"),
    ("head_ext",      "0.0",                      "",   "Fator de addendum, sol e planetas"),
    ("head_anel",     "-0.4",                     "",   "Fator de addendum do anel (evita interferência)"),
    ("numpoints",     "20",                       "",   "Pontos por flanco de evolvente"),

    # --- porta-satélites ---------------------------------------------------
    ("r_porta",       "=modulo * (Zr / 2 - 1) - 1.5", "mm", "Raio do disco do porta-satélites"),

    # --- fases de engrenamento (convenção FCGear) --------------------------
    ("fase_anel",     "=180 * (Zp + 1) / Zr",     "°",  "Rotação do anel para engrenar"),
    ("orbita_1",      "=0 * 360 / n_planetas",    "°",  "Ângulo orbital do planeta 1"),
    ("orbita_2",      "=1 * 360 / n_planetas",    "°",  "Ângulo orbital do planeta 2"),
    ("orbita_3",      "=2 * 360 / n_planetas",    "°",  "Ângulo orbital do planeta 3"),
    ("fase_plan_1",   "=orbita_1 * (1 - Zr / Zp) + 180 * (Zp + 1) / Zp", "°", "Rotação própria do planeta 1"),
    ("fase_plan_2",   "=orbita_2 * (1 - Zr / Zp) + 180 * (Zp + 1) / Zp", "°", "Rotação própria do planeta 2"),
    ("fase_plan_3",   "=orbita_3 * (1 - Zr / Zp) + 180 * (Zp + 1) / Zp", "°", "Rotação própria do planeta 3"),

    # --- posições dos pinos (trig resolvida na planilha) -------------------
    ("px_1", "=a_centro * cos(orbita_1 * 1deg)", "mm", "x do pino 1"),
    ("py_1", "=a_centro * sin(orbita_1 * 1deg)", "mm", "y do pino 1"),
    ("px_2", "=a_centro * cos(orbita_2 * 1deg)", "mm", "x do pino 2"),
    ("py_2", "=a_centro * sin(orbita_2 * 1deg)", "mm", "y do pino 2"),
    ("px_3", "=a_centro * cos(orbita_3 * 1deg)", "mm", "x do pino 3"),
    ("py_3", "=a_centro * sin(orbita_3 * 1deg)", "mm", "y do pino 3"),
]


def log(msg):
    print("[build] {}".format(msg))
    sys.stdout.flush()


# --------------------------------------------------------------------------
# Planilha
# --------------------------------------------------------------------------
def build_spreadsheet(doc):
    sheet = doc.addObject("Spreadsheet::Sheet", "Params")
    sheet.Label = "Params"

    sheet.set("A1", "PARAMETRO")
    sheet.set("B1", "VALOR")
    sheet.set("C1", "UNID")
    sheet.set("D1", "DESCRICAO")

    row = 2
    for alias, value, unit, desc in PARAMS:
        sheet.set("A{}".format(row), alias)
        sheet.set("B{}".format(row), value)
        sheet.set("C{}".format(row), unit)
        sheet.set("D{}".format(row), desc)
        sheet.setAlias("B{}".format(row), alias)
        row += 1

    doc.recompute()
    return sheet


# --------------------------------------------------------------------------
# Ligação por expressão, com verificação explícita
# --------------------------------------------------------------------------
_bind_failures = []


def bind(obj, prop, expr):
    """Liga `obj.prop` à expressão `expr`. Registra falhas em vez de silenciá-las."""
    try:
        obj.setExpression(prop, expr)
    except Exception as exc:  # noqa: BLE001
        _bind_failures.append((obj.Name, prop, expr, str(exc)))


# --------------------------------------------------------------------------
# Engrenagens
# --------------------------------------------------------------------------
def build_sun(doc):
    obj = doc.addObject("Part::FeaturePython", "sol")
    InvoluteGear(obj)
    obj.Label = "sol"

    bind(obj, "num_teeth", "Params.Zs")
    bind(obj, "module", "Params.modulo")
    bind(obj, "height", "Params.h_engr")
    bind(obj, "pressure_angle", "Params.alpha * 1deg")
    bind(obj, "backlash", "Params.backlash_peca")
    bind(obj, "clearance", "Params.clearance")
    bind(obj, "head", "Params.head_ext")
    bind(obj, "numpoints", "Params.numpoints")
    obj.axle_hole = True
    bind(obj, "axle_holesize", "Params.d_furo_sol")
    return obj


def build_planet(doc):
    obj = doc.addObject("Part::FeaturePython", "planeta")
    InvoluteGear(obj)
    obj.Label = "planeta"

    bind(obj, "num_teeth", "Params.Zp")
    bind(obj, "module", "Params.modulo")
    bind(obj, "height", "Params.h_engr")
    bind(obj, "pressure_angle", "Params.alpha * 1deg")
    bind(obj, "backlash", "Params.backlash_peca")
    bind(obj, "clearance", "Params.clearance")
    bind(obj, "head", "Params.head_ext")
    bind(obj, "numpoints", "Params.numpoints")
    obj.axle_hole = True
    bind(obj, "axle_holesize", "Params.d_furo_plan")
    return obj


def build_ring(doc):
    obj = doc.addObject("Part::FeaturePython", "anel")
    InternalInvoluteGear(obj)
    obj.Label = "anel"

    bind(obj, "num_teeth", "Params.Zr")
    bind(obj, "module", "Params.modulo")
    bind(obj, "height", "Params.h_engr")
    bind(obj, "thickness", "Params.esp_anel")
    bind(obj, "pressure_angle", "Params.alpha * 1deg")
    bind(obj, "backlash", "Params.backlash_peca")
    bind(obj, "clearance", "Params.clearance")
    bind(obj, "head", "Params.head_anel")
    bind(obj, "numpoints", "Params.numpoints")
    return obj


# --------------------------------------------------------------------------
# Porta-satélites (primitivas Part, todas ligadas à planilha)
# --------------------------------------------------------------------------
def build_carrier(doc):
    disco = doc.addObject("Part::Cylinder", "porta_disco")
    bind(disco, "Radius", "Params.r_porta")
    bind(disco, "Height", "Params.t_porta")

    pinos = []
    for k in (1, 2, 3):
        pino = doc.addObject("Part::Cylinder", "porta_pino_{}".format(k))
        bind(pino, "Radius", "Params.d_pino / 2")
        bind(pino, "Height", "Params.h_pino")
        bind(pino, ".Placement.Base.x", "Params.px_{}".format(k))
        bind(pino, ".Placement.Base.y", "Params.py_{}".format(k))
        bind(pino, ".Placement.Base.z", "Params.t_porta")
        pinos.append(pino)

    uniao = doc.addObject("Part::MultiFuse", "porta_uniao")
    uniao.Shapes = [disco] + pinos

    furo = doc.addObject("Part::Cylinder", "porta_furo")
    bind(furo, "Radius", "Params.d_furo_saida / 2")
    bind(furo, "Height", "Params.t_porta * 3")
    bind(furo, ".Placement.Base.z", "-Params.t_porta")

    corte = doc.addObject("Part::Cut", "porta_satelites")
    corte.Base = uniao
    corte.Tool = furo
    corte.Label = "porta_satelites"
    return corte


# --------------------------------------------------------------------------
# Montagem (App::Link — não duplica geometria, só posiciona)
# --------------------------------------------------------------------------
def build_assembly(doc, sol, planeta, anel, porta):
    grp = doc.addObject("App::DocumentObjectGroup", "Montagem")
    links = []

    l_sol = doc.addObject("App::Link", "m_sol")
    l_sol.LinkedObject = sol

    l_anel = doc.addObject("App::Link", "m_anel")
    l_anel.LinkedObject = anel
    bind(l_anel, ".Placement.Rotation.Angle", "Params.fase_anel * 1deg")
    l_anel.Placement.Rotation.Axis = App.Vector(0, 0, 1)

    links += [l_sol, l_anel]

    for k in (1, 2, 3):
        lp = doc.addObject("App::Link", "m_planeta_{}".format(k))
        lp.LinkedObject = planeta
        bind(lp, ".Placement.Base.x", "Params.px_{}".format(k))
        bind(lp, ".Placement.Base.y", "Params.py_{}".format(k))
        bind(lp, ".Placement.Rotation.Angle", "Params.fase_plan_{} * 1deg".format(k))
        lp.Placement.Rotation.Axis = App.Vector(0, 0, 1)
        links.append(lp)

    l_porta = doc.addObject("App::Link", "m_porta_satelites")
    l_porta.LinkedObject = porta
    bind(l_porta, ".Placement.Base.z", "-Params.t_porta - Params.folga_axial / 2")
    links.append(l_porta)

    grp.Group = links
    return grp


# --------------------------------------------------------------------------
def main():
    if not os.path.isdir(CAD_DIR):
        os.makedirs(CAD_DIR)

    if os.path.exists(DOC_PATH):
        os.remove(DOC_PATH)

    doc = App.newDocument("caixa_planetaria")

    log("planilha de parâmetros...")
    build_spreadsheet(doc)

    log("sol...")
    sol = build_sun(doc)
    log("planeta...")
    planeta = build_planet(doc)
    log("anel...")
    anel = build_ring(doc)
    log("porta-satélites...")
    porta = build_carrier(doc)

    log("recompute das peças...")
    doc.recompute()

    log("montagem...")
    build_assembly(doc, sol, planeta, anel, porta)
    doc.recompute()

    doc.saveAs(DOC_PATH)
    log("salvo em {}".format(DOC_PATH))

    # ---------------- relatório de construção ----------------
    if _bind_failures:
        log("!!! FALHAS DE LIGACAO POR EXPRESSAO ({}):".format(len(_bind_failures)))
        for name, prop, expr, err in _bind_failures:
            log("    {}.{} <- {}   ERRO: {}".format(name, prop, expr, err))
    else:
        log("todas as ligações por expressão foram aceitas")

    sheet = doc.getObject("Params")
    log("--- valores resolvidos ---")
    for alias in ("modulo", "Zs", "Zp", "Zr", "n_planetas", "razao_i",
                  "checa_montagem", "a_centro", "a_anel", "delta",
                  "backlash_peca", "r_porta", "fase_anel",
                  "fase_plan_1", "fase_plan_2", "fase_plan_3"):
        log("    {:<14} = {}".format(alias, sheet.get(alias)))

    log("--- sólidos ---")
    for obj in (sol, planeta, anel, porta):
        sh = obj.Shape
        log("    {:<18} valido={} solidos={} volume={:.1f} mm3  bbox={:.1f}x{:.1f}x{:.1f}".format(
            obj.Name, sh.isValid(), len(sh.Solids), sh.Volume,
            sh.BoundBox.XLength, sh.BoundBox.YLength, sh.BoundBox.ZLength))

    log("OK")


main()
