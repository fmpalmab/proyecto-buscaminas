# ver_agente.py
import tkinter as tk
import time
from juego_model import Tablero
from interfaz_gui import MinesweeperGUI
from agente import AgenteQLearning

# --- CONFIGURACIÓN ---
# ¡IMPORTANTE! Debe ser el MISMO tamaño usado en el entrenamiento (ej. 4)
SIZE = 6       
MINAS_RATIO = 0.2
VELOCIDAD = 500  # Milisegundos entre cada movimiento (500ms = 0.5 seg)

class AgenteGUI(MinesweeperGUI):
    """
    Versión modificada de la GUI que permite al agente jugar automáticamente.
    """
    def __init__(self, root, tablero, agente):
        super().__init__(root, tablero)
        self.agente = agente
        self.jugando_auto = False

    def iniciar_demo(self):
        """Arranca el bucle del agente."""
        self.jugando_auto = True
        self.siguiente_movimiento()

    def siguiente_movimiento(self):
        """Pide al agente una acción y la ejecuta en la GUI."""
        if not self.jugando_auto or self.tablero.juego_terminado:
            return

        # 1. Obtener estado actual del tablero
        estado = self.tablero.get_estado_hashable()
        
        # 2. Desactivar exploración temporalmente (modo 'Explotación')
        epsilon_original = self.agente.epsilon
        self.agente.epsilon = 0 
        
        # 3. El agente decide coordenadas (x, y)
        x, y = self.agente.elegir_accion(estado)
        
        # Restaurar epsilon
        self.agente.epsilon = epsilon_original

        # 4. Imprimir en consola qué decidió (opcional)
        print(f"🤖 Agente decide click en: ({x}, {y})")

        # 5. Ejecutar el click en la GUI
        # Llamamos directamente al método onClick de la clase padre
        self.onClick(x, y)

        # 6. Programar el siguiente paso si el juego sigue vivo
        if not self.tablero.juego_terminado:
            self.root.after(VELOCIDAD, self.siguiente_movimiento)

    def restart(self):
        """Sobrescribimos reiniciar para que el agente siga jugando tras el Game Over."""
        super().restart()
        if self.jugando_auto:
            # Esperar un poco antes de empezar la nueva partida
            self.root.after(1000, self.siguiente_movimiento)

def main():
    # 1. Configurar Ventana
    root = tk.Tk()
    root.title(f"Demo Agente Buscaminas ({SIZE}x{SIZE})")

    # 2. Inicializar Tablero y Agente
    tablero = Tablero(SIZE, SIZE, MINAS_RATIO)
    acciones_posibles = [(x, y) for x in range(SIZE) for y in range(SIZE)]
    
    agente = AgenteQLearning(actions=acciones_posibles)
    
    # 3. Cargar Cerebro
    nombre_archivo = "mi_agente_entrenado.pkl"
    try:
        agente.cargar_agente(nombre_archivo)
        print(f"✅ {nombre_archivo} cargado exitosamente.")
    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró '{nombre_archivo}'.")
        print("   Asegúrate de ejecutar 'entrenar.py' primero.")
        return

    # 4. Iniciar la GUI Especial
    app = AgenteGUI(root, tablero, agente)
    
    # Darle 1 segundo al usuario para ver la ventana antes de empezar
    root.after(1000, app.iniciar_demo)

    root.mainloop()

if __name__ == "__main__":
    main()