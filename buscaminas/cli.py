"""
Interfaz de línea de comandos (CLI) unificada para Buscaminas.
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from buscaminas.model import Tablero
from buscaminas.agent import AgenteQLearningAproximado, AgenteHeuristico
from buscaminas.trainer import entrenar_agente
from buscaminas.evaluator import ejecutar_benchmark


def run_ascii_game(size: int = 6, mine_ratio: float = 0.15, autoplay: bool = False) -> None:
    """Modo consola ASCII/terminal para jugar o ver resolver sin GUI."""
    tablero = Tablero(size, size, mine_ratio)
    acciones = [(x, y) for x in range(size) for y in range(size)]
    agente = AgenteHeuristico(acciones) if autoplay else None

    print(f"\n--- Buscaminas Terminal ({size}x{size}) ---")
    print("Controles: 'r x y' para revelar, 'f x y' para marcar/desmarcar bandera, 'q' para salir.")

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    while not tablero.juego_terminado:
        print("\n" + tablero.to_ascii())
        print(f"Banderas: {tablero.conteo_banderas} | Reveladas: {tablero.conteo_reveladas}")

        if autoplay and agente is not None:
            estado = tablero.get_estado_hashable()
            x, y = agente.elegir_accion(estado)
            print(f"[IA] Agente auto-revela: ({x}, {y})")
            _state, _reward, done = tablero.step(x, y)
            if done:
                break
            continue

        try:
            line = input("Acción > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            return

        if line == "q":
            return
        parts = line.split()
        if len(parts) != 3 or parts[0] not in ("r", "f"):
            print("Formato inválido. Ejemplo: 'r 0 1' o 'f 2 3'")
            continue

        cmd, sx, sy = parts[0], parts[1], parts[2]
        if not (sx.isdigit() and sy.isdigit()):
            print("Coordenadas deben ser números enteros.")
            continue
        x, y = int(sx), int(sy)

        if cmd == "r":
            tablero.step(x, y)
        elif cmd == "f":
            tablero.marcar_celda(x, y)

    print("\n" + tablero.to_ascii())
    if tablero.victoria:
        print("\n[VICTORIA] Felicitaciones, has ganado la partida.")
    else:
        print("\n[DERROTA] Has pisado una mina. Fin del juego.")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="buscaminas",
        description="Buscaminas Clásico + Agentes de Inteligencia Artificial (RL & Heurísticos)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--play", action="store_true", help="Jugar manualmente en interfaz gráfica (Tkinter)")
    group.add_argument("--ascii", action="store_true", help="Jugar en modo terminal ASCII sin ventana")
    group.add_argument("--train", action="store_true", help="Entrenar el agente Q-Learning aproximado")
    group.add_argument("--eval", action="store_true", help="Evaluar y comparar agentes contra línea base")
    group.add_argument("--demo", action="store_true", help="Ver al agente IA resolver el tablero en la GUI")
    group.add_argument("--auto-ascii", action="store_true", help="Ver resolución automática en terminal ASCII")

    parser.add_argument("--size", type=int, default=6, help="Tamaño del tablero N x N (default: 6)")
    parser.add_argument("--mines", type=float, default=0.15, help="Proporción de minas 0.0 - 0.5 (default: 0.15)")
    parser.add_argument("--episodes", type=int, default=5000, help="Episodios de entrenamiento (default: 5000)")
    parser.add_argument("--eval-games", type=int, default=1000, help="Partidas de evaluación (default: 1000)")
    parser.add_argument("--weights", type=str, default="mi_agente_entrenado.pkl", help="Ruta de pesos del agente")

    args = parser.parse_args(argv)

    if args.train:
        entrenar_agente(
            episodios=args.episodes,
            size=args.size,
            minas_ratio=args.mines,
            output_weights=args.weights,
        )
        return 0

    if args.eval:
        ejecutar_benchmark(
            n_partidas=args.eval_games,
            size=args.size,
            minas_ratio=args.mines,
            weights_path=args.weights,
        )
        return 0

    if args.ascii:
        run_ascii_game(size=args.size, mine_ratio=args.mines, autoplay=False)
        return 0

    if args.auto_ascii:
        run_ascii_game(size=args.size, mine_ratio=args.mines, autoplay=True)
        return 0

    if args.demo:
        import tkinter as tk
        from buscaminas.gui import AgenteGUI

        root = tk.Tk()
        root.title(f"Demo Agente Buscaminas ({args.size}x{args.size})")
        tablero = Tablero(args.size, args.size, args.mines)
        acciones = [(x, y) for x in range(args.size) for y in range(args.size)]
        agente = AgenteQLearningAproximado(actions=acciones)
        agente.cargar_agente(args.weights)
        app = AgenteGUI(root, tablero, agente)
        root.after(800, app.iniciar_demo)
        root.mainloop()
        return 0

    # Por defecto o con --play: GUI
    try:
        import tkinter as tk
        from buscaminas.gui import MinesweeperGUI

        root = tk.Tk()
        root.title(f"Buscaminas ({args.size}x{args.size})")
        tablero = Tablero(args.size, args.size, args.mines)
        MinesweeperGUI(root, tablero)
        root.mainloop()
        return 0
    except Exception as e:
        print(f"[Error arrancando GUI]: {e}")
        print("Iniciando en modo terminal ASCII como fallback...")
        run_ascii_game(size=args.size, mine_ratio=args.mines, autoplay=False)
        return 0


if __name__ == "__main__":
    sys.exit(main())
