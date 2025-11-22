# evaluar.py
import random
import matplotlib.pyplot as plt
import numpy as np
from juego_model import Tablero, REWARDS
from agente_qlearning import AgenteQLearning

# --- CONFIGURACIÓN DE EVALUACIÓN ---
CANTIDAD_PARTIDAS = 1000  # Cantidad de pruebas por jugador
SIZE = 4                  # ¡Debe ser el mismo tamaño del entrenamiento!
MINAS_RATIO = 0.2

# --- AGENTE ALEATORIO (BASELINE) ---
class AgenteAleatorio:
    def __init__(self, acciones_posibles):
        self.acciones = acciones_posibles
    
    def elegir_accion(self, estado):
        return random.choice(self.acciones)

# --- FUNCIÓN DE PRUEBA ---
def ejecutar_prueba(nombre, agente, n_partidas):
    print(f"Evaluando a: {nombre}...")
    tablero = Tablero(SIZE, SIZE, MINAS_RATIO)
    victorias = 0
    pasos_totales = 0
    
    for i in range(n_partidas):
        tablero.reiniciar()
        estado = tablero.get_estado_hashable()
        terminado = False
        pasos = 0
        
        # Desactivar exploración para el agente entrenado (solo explotar)
        if hasattr(agente, 'epsilon'):
            original_epsilon = agente.epsilon
            agente.epsilon = 0 

        while not terminado:
            # Obtener acción
            accion = agente.elegir_accion(estado)
            x, y = accion
            
            # Ejecutar paso
            # Nota: El tablero maneja internamente si es inválido o mina
            next_estado, reward, terminado = tablero.step(x, y)
            
            estado = next_estado
            pasos += 1
            
            # Evitar bucles infinitos si el agente aleatorio se queda atascado
            if pasos > 50: 
                break

        # Restaurar epsilon
        if hasattr(agente, 'epsilon'):
            agente.epsilon = original_epsilon

        if tablero.victoria:
            victorias += 1
        pasos_totales += pasos

    win_rate = (victorias / n_partidas) * 100
    avg_pasos = pasos_totales / n_partidas
    return win_rate, avg_pasos

# --- MAIN ---
def main():
    # 1. Cargar Agente Entrenado
    acciones = [(x, y) for x in range(SIZE) for y in range(SIZE)]
    agente_ia = AgenteQLearning(actions=acciones)
    try:
        agente_ia.cargar_agente("mi_agente_entrenado.pkl")
        print(">> IA Cargada Exitosamente.")
    except:
        print("!! ERROR: No se encontró 'mi_agente_entrenado.pkl'. Ejecuta entrenar.py primero.")
        return

    # 2. Inicializar Agente Aleatorio
    agente_random = AgenteAleatorio(acciones)

    # 3. Ejecutar Comparaciones
    win_ai, pasos_ai = ejecutar_prueba("Agente IA (Q-Learning)", agente_ia, CANTIDAD_PARTIDAS)
    win_rnd, pasos_rnd = ejecutar_prueba("Agente Aleatorio", agente_random, CANTIDAD_PARTIDAS)

    # 4. Datos Humanos (Simulados o ingresa los tuyos reales aquí)
    # Si juegas 10 partidas y ganas 8, pon 80.0
    win_human = 85.0  
    pasos_human = 5.0 

    # 5. Mostrar Tabla
    print("\n" + "="*60)
    print(f"{'JUGADOR':<25} | {'VICTORIAS (%)':<15} | {'PASOS PROM.':<15}")
    print("-" * 60)
    print(f"{'Agente Aleatorio':<25} | {win_rnd:6.1f}%          | {pasos_rnd:6.1f}")
    print(f"{'Agente IA (Q-Learning)':<25} | {win_ai:6.1f}%          | {pasos_ai:6.1f}")
    print(f"{'Humano (Referencia)':<25} | {win_human:6.1f}%          | {pasos_human:6.1f}")
    print("="*60)

    # 6. Generar Gráfico
    nombres = ['Aleatorio', 'IA Q-Learning', 'Humano']
    valores = [win_rnd, win_ai, win_human]
    colores = ['#95a5a6', '#3498db', '#2ecc71'] # Gris, Azul, Verde

    plt.figure(figsize=(8, 6))
    barras = plt.bar(nombres, valores, color=colores)
    
    plt.ylabel('Tasa de Victorias (%)')
    plt.title(f'Comparación de Rendimiento (Tablero {SIZE}x{SIZE})')
    plt.ylim(0, 100)
    
    # Poner el valor encima de cada barra
    for bar in barras:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}%", ha='center', fontweight='bold')

    plt.savefig("comparacion_final.png")
    print("\nGráfico guardado como 'comparacion_final.png'")
    # plt.show() # Descomenta si quieres ver la ventana

if __name__ == "__main__":
    main()