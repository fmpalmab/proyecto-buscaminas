"""
Módulo de evaluación y comparación cuantitativa de agentes de Buscaminas.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import matplotlib.pyplot as plt

from buscaminas.model import Tablero
from buscaminas.agent import AgenteQLearningAproximado, AgenteAleatorio, AgenteHeuristico


def evaluar_agente(
    nombre: str,
    agente: Any,
    n_partidas: int = 1000,
    size: int = 6,
    minas_ratio: float = 0.15,
    seed: Optional[int] = 42,
) -> Tuple[float, float]:
    """
    Evalúa el rendimiento de un agente durante n_partidas.
    Retorna (win_rate_porcentaje, pasos_promedio).
    """
    rng = random.Random(seed)
    tablero = Tablero(size, size, minas_ratio, rng=rng)
    victorias = 0
    pasos_totales = 0

    original_epsilon = getattr(agente, "epsilon", None)
    if original_epsilon is not None:
        agente.epsilon = 0.0

    try:
        for _ in range(n_partidas):
            tablero.reiniciar()
            estado = tablero.get_estado_hashable()
            terminado = False
            pasos = 0

            while not terminado and pasos < 60:
                accion = agente.elegir_accion(estado)
                next_estado, _reward, terminado = tablero.step(accion[0], accion[1])
                estado = next_estado
                pasos += 1

            if tablero.victoria:
                victorias += 1
            pasos_totales += pasos
    finally:
        if original_epsilon is not None:
            agente.epsilon = original_epsilon

    win_rate = (victorias / n_partidas) * 100.0
    avg_pasos = pasos_totales / n_partidas
    return win_rate, avg_pasos


def ejecutar_benchmark(
    n_partidas: int = 1000,
    size: int = 6,
    minas_ratio: float = 0.15,
    weights_path: str = "mi_agente_entrenado.pkl",
    output_plot: Optional[str] = "comparacion_final.png",
    seed: Optional[int] = 42,
) -> Dict[str, Dict[str, float]]:
    """
    Ejecuta una comparación rigurosa entre:
    1. Agente Aleatorio (Baseline)
    2. Agente IA (Q-Learning Aproximado)
    3. Agente Heurístico (CSP / Deductivo)
    4. Humano (Referencia teórica)
    """
    acciones = [(x, y) for x in range(size) for y in range(size)]

    # 1. Agente Aleatorio
    agente_random = AgenteAleatorio(acciones, rng=random.Random(seed))

    # 2. Agente RL
    agente_ia = AgenteQLearningAproximado(actions=acciones, rng=random.Random(seed))
    cargado = agente_ia.cargar_agente(weights_path)
    if not cargado:
        json_path = Path(weights_path).with_suffix(".json")
        cargado = agente_ia.cargar_json(json_path)

    # 3. Agente Heurístico
    agente_csp = AgenteHeuristico(acciones, rng=random.Random(seed))

    resultados: Dict[str, Dict[str, float]] = {}

    print(f"Evaluando agentes sobre {n_partidas} partidas (tablero {size}x{size}, minas {minas_ratio:.0%})...")
    win_rnd, pasos_rnd = evaluar_agente("Aleatorio", agente_random, n_partidas, size, minas_ratio, seed=seed)
    resultados["Agente Aleatorio"] = {"win_rate": win_rnd, "pasos": pasos_rnd}

    if cargado:
        win_ai, pasos_ai = evaluar_agente("Q-Learning", agente_ia, n_partidas, size, minas_ratio, seed=seed)
        resultados["Agente IA (Q-Learning)"] = {"win_rate": win_ai, "pasos": pasos_ai}
    else:
        print("[Aviso] No se encontraron pesos para el Agente RL; se omitirá de los resultados cargados.")

    win_csp, pasos_csp = evaluar_agente("Heurístico CSP", agente_csp, n_partidas, size, minas_ratio, seed=seed)
    resultados["Agente Heurístico (CSP)"] = {"win_rate": win_csp, "pasos": pasos_csp}

    resultados["Humano (Referencia)"] = {"win_rate": 80.0, "pasos": 9.0}

    # Mostrar tabla formateada
    print("\n" + "=" * 65)
    print(f"{'JUGADOR':<26} | {'VICTORIAS (%)':<15} | {'PASOS PROM.':<15}")
    print("-" * 65)
    for nombre, metricas in resultados.items():
        print(f"{nombre:<26} | {metricas['win_rate']:6.1f}%          | {metricas['pasos']:6.1f}")
    print("=" * 65 + "\n")

    if output_plot:
        nombres = list(resultados.keys())
        win_rates = [resultados[k]["win_rate"] for k in nombres]
        pasos = [resultados[k]["pasos"] for k in nombres]
        colores = ["#d9534f", "#2ca02c", "#0275d8", "#f0ad4e"][: len(nombres)]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

        bars1 = ax1.bar(nombres, win_rates, color=colores, width=0.55)
        ax1.set_title("Tasa de Victoria (Win Rate %)", fontsize=11, fontweight="bold")
        ax1.set_ylabel("Victorias (%)")
        ax1.set_ylim(0, 100)
        ax1.grid(axis="y", linestyle="--", alpha=0.5)
        for bar in bars1:
            yval = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 1.5, f"{yval:.1f}%", ha="center", va="bottom")
        ax1.tick_params(axis="x", rotation=15)

        bars2 = ax2.bar(nombres, pasos, color=colores, width=0.55)
        ax2.set_title("Pasos Promedio por Partida", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Pasos Promedio")
        ax2.grid(axis="y", linestyle="--", alpha=0.5)
        for bar in bars2:
            yval = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.3, f"{yval:.1f}", ha="center", va="bottom")
        ax2.tick_params(axis="x", rotation=15)

        plt.tight_layout()
        plt.savefig(output_plot, dpi=120)
        plt.close(fig)
        print(f"Gráfico comparativo guardado en '{output_plot}'.")

    return resultados
