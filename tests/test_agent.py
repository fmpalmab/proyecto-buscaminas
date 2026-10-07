"""Pruebas unitarias para el agente de RL y guardado/carga de pesos."""

import pytest
import tempfile
from pathlib import Path
from buscaminas.agent import AgenteQLearningAproximado, AgenteAleatorio


def test_agente_qlearning_features():
    acciones = [(0, 0), (0, 1), (1, 0), (1, 1)]
    agente = AgenteQLearningAproximado(actions=acciones)

    # Estado ficticio 2x2
    state = (
        (-1, 1),
        (-2, 0),
    )
    features = agente.get_features(state, 0, 0)
    assert len(features) == 6
    assert features[0] == 1.0  # Bias
    assert isinstance(features[1], float)  # Vecinos ocultos
    assert isinstance(features[2], float)  # Vecinos bandera


def test_agente_qlearning_q_value():
    acciones = [(0, 0)]
    weights = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    agente = AgenteQLearningAproximado(actions=acciones, weights=weights)
    state = ((-1,),)
    q = agente.get_q_value(state, (0, 0))
    # Bias = 1.0, rest = 0.0 -> q = 1.0
    assert abs(q - 1.0) < 1e-6


def test_agente_qlearning_update():
    acciones = [(0, 0), (0, 1)]
    agente = AgenteQLearningAproximado(actions=acciones, alpha=0.1, gamma=0.9, weights=[0.0] * 6)
    state = ((-1, -1),)
    next_state = ((0, -1),)

    error = agente.aprender(state, (0, 0), reward=10.0, next_state=next_state)
    assert error == 10.0  # td_error = 10 + 0 - 0 = 10
    assert agente.weights[0] == pytest.approx(1.0)  # 0 + 0.1 * 10 * 1.0 = 1.0


def test_agente_guardar_y_cargar_pickle():
    with tempfile.TemporaryDirectory() as tmpdir:
        pkl_path = Path(tmpdir) / "test_weights.pkl"
        agente = AgenteQLearningAproximado(actions=[(0, 0)], weights=[1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
        agente.guardar_agente(pkl_path)
        assert pkl_path.exists()

        nuevo_agente = AgenteQLearningAproximado(actions=[(0, 0)])
        cargado = nuevo_agente.cargar_agente(pkl_path)
        assert cargado is True
        assert nuevo_agente.weights == pytest.approx([1.5, 2.5, 3.5, 4.5, 5.5, 6.5])


def test_agente_guardar_y_cargar_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "test_weights.json"
        agente = AgenteQLearningAproximado(actions=[(0, 0)], weights=[10.0, -5.0, 2.0, 0.5, -1.0, 8.0])
        agente.guardar_json(json_path)
        assert json_path.exists()

        nuevo_agente = AgenteQLearningAproximado(actions=[(0, 0)])
        cargado = nuevo_agente.cargar_json(json_path)
        assert cargado is True
        assert nuevo_agente.weights == pytest.approx([10.0, -5.0, 2.0, 0.5, -1.0, 8.0])


def test_agente_aleatorio_solo_elige_ocultas():
    acciones = [(0, 0), (0, 1), (1, 0), (1, 1)]
    agente = AgenteAleatorio(acciones)
    state = (
        (0, -2),
        (1, -1),
    )
    # Solo (1, 1) está oculta (-1)
    accion = agente.elegir_accion(state)
    assert accion == (1, 1)
