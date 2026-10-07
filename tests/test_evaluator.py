"""Pruebas para el evaluador y benchmark de agentes."""

import pytest
from buscaminas.evaluator import evaluar_agente
from buscaminas.agent import AgenteAleatorio, AgenteHeuristico


def test_evaluacion_partidas_rapidas():
    acciones = [(x, y) for x in range(4) for y in range(4)]
    agente_rnd = AgenteAleatorio(acciones)
    agente_csp = AgenteHeuristico(acciones)

    win_rnd, pasos_rnd = evaluar_agente("Rnd", agente_rnd, n_partidas=30, size=4, minas_ratio=0.1, seed=1)
    win_csp, pasos_csp = evaluar_agente("CSP", agente_csp, n_partidas=30, size=4, minas_ratio=0.1, seed=1)

    assert 0.0 <= win_rnd <= 100.0
    assert 50.0 <= win_csp <= 100.0
    assert pasos_rnd > 0
    assert pasos_csp > 0
