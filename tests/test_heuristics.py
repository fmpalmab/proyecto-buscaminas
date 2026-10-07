"""Pruebas unitarias para el agente heurístico deductivo (CSP)."""

import pytest
from buscaminas.agent import AgenteHeuristico


def test_agente_heuristico_elige_seguro_por_vecino_satisfecho():
    # Tablero 3x1: [1, -2 (bandera), -1 (oculto)]
    acciones = [(0, 0), (0, 1), (0, 2)]
    agente = AgenteHeuristico(acciones)

    state = (
        (1, -2, -1),
    )
    # El 1 en (0,0) ya tiene una bandera en (0,1), por tanto (0,2) es 100% segura
    accion = agente.elegir_accion(state)
    assert accion == (0, 2)


def test_agente_heuristico_fallback_accion_valida():
    acciones = [(0, 0), (0, 1)]
    agente = AgenteHeuristico(acciones)
    state = ((-1, -1),)
    accion = agente.elegir_accion(state)
    assert accion in acciones
