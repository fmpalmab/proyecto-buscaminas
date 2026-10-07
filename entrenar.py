"""
Script de entrenamiento para el agente de Q-Learning aproximado.
"""

from buscaminas.trainer import entrenar_agente

EPISODIOS = 10000
SIZE = 6
MINAS_RATIO = 0.15
SHOW_EVERY = 1000


def main():
    entrenar_agente(
        episodios=EPISODIOS,
        size=SIZE,
        minas_ratio=MINAS_RATIO,
        show_every=SHOW_EVERY,
        output_weights="mi_agente_entrenado.pkl",
        output_plot="metricas_entrenamiento.png",
    )


if __name__ == "__main__":
    main()