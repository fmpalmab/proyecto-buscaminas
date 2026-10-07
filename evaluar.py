"""
Script de evaluación y benchmarking de agentes para Buscaminas.
"""

from buscaminas.evaluator import ejecutar_benchmark

CANTIDAD_PARTIDAS = 1000
SIZE = 6
MINAS_RATIO = 0.15


def main():
    ejecutar_benchmark(
        n_partidas=CANTIDAD_PARTIDAS,
        size=SIZE,
        minas_ratio=MINAS_RATIO,
        weights_path="mi_agente_entrenado.pkl",
        output_plot="comparacion_final.png",
    )


if __name__ == "__main__":
    main()