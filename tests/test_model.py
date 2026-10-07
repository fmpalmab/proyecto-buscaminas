"""Pruebas unitarias para el modelo del tablero y sus reglas."""

import pytest
import random
from buscaminas.model import (
    Tablero,
    Celda,
    STATE_DEFAULT,
    STATE_CLICKED,
    STATE_FLAGGED,
    REWARDS,
)


def test_tablero_inicializacion():
    tablero = Tablero(size_x=5, size_y=5, mine_ratio=0.2)
    assert tablero.size_x == 5
    assert tablero.size_y == 5
    assert len(tablero.celdas) == 5
    assert tablero.primer_movimiento is True
    assert tablero.juego_terminado is False
    assert tablero.victoria is False
    assert tablero.conteo_reveladas == 0
    assert tablero.conteo_banderas == 0


def test_primer_movimiento_nunca_es_mina():
    rng = random.Random(123)
    tablero = Tablero(size_x=4, size_y=4, mine_ratio=0.3, rng=rng)
    # Clic en (1, 1)
    reveladas = tablero.revelar_celda(1, 1)
    assert tablero.primer_movimiento is False
    assert not tablero.celdas[1][1].es_mina
    assert tablero.celdas[1][1].estado == STATE_CLICKED
    assert len(reveladas) >= 1
    assert not tablero.juego_terminado


def test_banderas_marcar_y_desmarcar():
    tablero = Tablero(size_x=3, size_y=3, mine_ratio=0.1)
    # Marcar
    celda = tablero.marcar_celda(0, 0)
    assert celda.estado == STATE_FLAGGED
    assert tablero.conteo_banderas == 1

    # Desmarcar
    celda = tablero.marcar_celda(0, 0)
    assert celda.estado == STATE_DEFAULT
    assert tablero.conteo_banderas == 0


def test_revelar_mina_termina_juego():
    tablero = Tablero(size_x=3, size_y=3, mine_ratio=0.0)
    # Forzamos una mina manualmente tras inicializar
    tablero.primer_movimiento = False
    tablero.celdas[0][0].es_mina = True
    tablero.minas_totales = 1

    _state, reward, done = tablero.step(0, 0)
    assert done is True
    assert tablero.juego_terminado is True
    assert tablero.victoria is False
    assert reward == REWARDS["lose"]


def test_flood_fill_en_celdas_vacias():
    tablero = Tablero(size_x=3, size_y=3, mine_ratio=0.0)
    tablero.primer_movimiento = False
    # Con 0 minas, al revelar una celda se deben revelar todas
    reveladas = tablero.revelar_celda(1, 1)
    assert len(reveladas) == 9
    assert tablero.conteo_reveladas == 9


def test_auto_flag_deduccion():
    tablero = Tablero(size_x=2, size_y=2, mine_ratio=0.0)
    tablero.primer_movimiento = False
    # Celda (0,0) revelada con 1 mina vecina
    tablero.celdas[0][0].estado = STATE_CLICKED
    tablero.celdas[0][0].minas_vecinas = 1
    # De los 3 vecinos, (0,1) y (1,0) ya están revelados
    tablero.celdas[0][1].estado = STATE_CLICKED
    tablero.celdas[1][0].estado = STATE_CLICKED
    # Queda solo (1,1) oculto
    tablero.celdas[1][1].estado = STATE_DEFAULT

    nuevas = tablero._auto_flag()
    assert nuevas == 1
    assert tablero.celdas[1][1].estado == STATE_FLAGGED
    assert tablero.conteo_banderas == 1


def test_estado_hashable_format():
    tablero = Tablero(size_x=3, size_y=3, mine_ratio=0.0)
    tablero.celdas[0][0].estado = STATE_FLAGGED
    tablero.celdas[0][1].estado = STATE_CLICKED
    tablero.celdas[0][1].minas_vecinas = 2
    state = tablero.get_estado_hashable()
    assert isinstance(state, tuple)
    assert len(state) == 3
    assert state[0][0] == -2  # Bandera
    assert state[0][1] == 2   # Número revelado
    assert state[0][2] == -1  # Oculto
