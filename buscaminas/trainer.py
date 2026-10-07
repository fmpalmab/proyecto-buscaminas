"""
Módulo de entrenamiento para el agente de Q-Learning aproximado.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import matplotlib.pyplot as plt

from buscaminas.model import Tablero
from buscaminas.agent import AgenteQLearningAproximado


def entrenar_agente(
    episodios: int = 5000,
    size: int = 6,
    minas_ratio: float = 0.15,
    show_every: int = 500,
    output_weights: str = "mi_agente_entrenado.pkl",
    output_plot: Optional[str] = "metricas_entrenamiento.png",
    seed: Optional[int] = 42,
) -> Tuple[AgenteQLearningAproximado, Dict[str, List[Any]]]:
    """
    Entrena un AgenteQLearningAproximado en partidas masivas de Buscaminas.
    Retorna la instancia del agente y el diccionario con el historial de métricas.
    """
    rng = random.Random(seed)
    tablero = Tablero(size, size, minas_ratio, rng=rng)
    acciones = [(x, y) for x in range(size) for y in range(size)]
    agente = AgenteQLearningAproximado(actions=acciones, alpha=0.01, epsilon=0.9, rng=rng)

    victorias: List[int] = []
    temp_rewards: List[float] = []

    history: Dict[str, List[Any]] = {
        "episodios": [],
        "winrate": [],
        "epsilon": [],
        "rewards": [],
    }

    print(f"Iniciando entrenamiento ({episodios} episodios) en tablero {size}x{size}...")

    for episodio in range(1, episodios + 1):
        tablero.reiniciar()
        estado = tablero.get_estado_hashable()
        terminado = False
        total_reward = 0.0

        while not terminado:
            accion = agente.elegir_accion(estado)
            next_estado, reward, terminado = tablero.step(accion[0], accion[1])
            agente.aprender(estado, accion, reward, next_estado)
            estado = next_estado
            total_reward += reward

        if agente.epsilon > 0.05:
            agente.epsilon *= 0.9995

        victorias.append(1 if tablero.victoria else 0)
        temp_rewards.append(total_reward)

        if episodio % show_every == 0:
            recientes_win = victorias[-show_every:]
            recientes_rew = temp_rewards[-show_every:]
            avg_winrate = (sum(recientes_win) / len(recientes_win)) * 100.0
            avg_reward = sum(recientes_rew) / len(recientes_rew)

            history["episodios"].append(episodio)
            history["winrate"].append(avg_winrate)
            history["epsilon"].append(agente.epsilon)
            history["rewards"].append(avg_reward)

            print(
                f"Episodio: {episodio:5d} | Win Rate: {avg_winrate:5.1f}% | "
                f"Epsilon: {agente.epsilon:.3f} | Avg Reward: {avg_reward:6.1f}"
            )

    # Guardar pesos en pickle y JSON
    agente.guardar_agente(output_weights)
    json_path = Path(output_weights).with_suffix(".json")
    agente.guardar_json(json_path)
    print(f"Agente guardado exitosamente en '{output_weights}' y '{json_path}'.")

    if output_plot:
        fig, axs = plt.subplots(3, 1, figsize=(9, 10), sharex=True)
        axs[0].plot(history["episodios"], history["winrate"], color="#2ca02c", lw=2, label="Win Rate (%)")
        axs[0].set_ylabel("Victorias (%)")
        axs[0].set_title(f"Evolución del Aprendizaje (Q-Learning {size}x{size})")
        axs[0].grid(True, alpha=0.3)
        axs[0].legend(loc="upper left")

        axs[1].plot(history["episodios"], history["rewards"], color="#1f77b4", lw=2, label="Recompensa Prom.")
        axs[1].set_ylabel("Recompensa")
        axs[1].grid(True, alpha=0.3)
        axs[1].legend(loc="upper left")

        axs[2].plot(history["episodios"], history["epsilon"], color="#d62728", lw=2, label="Epsilon (Exploración)")
        axs[2].set_ylabel("Epsilon")
        axs[2].set_xlabel("Episodios")
        axs[2].grid(True, alpha=0.3)
        axs[2].legend(loc="upper right")

        plt.tight_layout()
        plt.savefig(output_plot, dpi=120)
        plt.close(fig)
        print(f"Gráfico guardado en '{output_plot}'.")

    return agente, history
