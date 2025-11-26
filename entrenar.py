# entrenar.py
from juego_model import Tablero
# IMPORTANTE: Asegúrate de que tu archivo agente.py tenga esta clase (ver respuesta anterior)
from agente import AgenteQLearningAproximado 
import matplotlib.pyplot as plt
import numpy as np

# --- CONFIGURACIÓN DE ENTRENAMIENTO ---
# Aumentamos episodios porque 6x6 requiere más iteraciones, 
# aunque el método aproximado converge más rápido que el tabular.
EPISODIOS = 50000        
SIZE = 6                 
MINAS_RATIO = 0.15       # 15% de minas (un poco más fácil para empezar que 0.2)
SHOW_EVERY = 1000        # Mostrar reporte cada 1000 juegos

def main():
    # 1. Inicializar entorno
    tablero = Tablero(SIZE, SIZE, MINAS_RATIO)
    acciones_posibles = [(x, y) for x in range(SIZE) for y in range(SIZE)]
    
    # 2. Inicializar Agente (Usando la versión Aproximada)
    # alpha=0.01: Una tasa de aprendizaje baja es vital para la estabilidad
    # cuando usamos aproximación de funciones (pesos).
    agente = AgenteQLearningAproximado(actions=acciones_posibles, alpha=0.01, epsilon=0.9)
    
    # Listas para métricas
    victorias = []                 
    
    # Historial para graficar (se llenan cada SHOW_EVERY)
    history_episodios = []
    history_winrate = []
    history_epsilon = []
    history_rewards = []           

    temp_rewards = []              

    print(f"Iniciando entrenamiento (Q-Learning Aproximado) en tablero {SIZE}x{SIZE}...")

    for episodio in range(EPISODIOS):
        tablero.reiniciar()
        # Nota: Asegúrate que tablero.get_estado_hashable() devuelva -2 para banderas
        # como indicamos en los cambios de juego_model.py
        estado = tablero.get_estado_hashable()
        terminado = False
        total_reward = 0

        while not terminado:
            # a. Agente elige acción
            accion = agente.elegir_accion(estado)
            x, y = accion

            # b. Entorno ejecuta acción
            next_estado, reward, terminado = tablero.step(x, y)

            # c. Agente aprende (actualiza sus pesos)
            agente.aprender(estado, accion, reward, next_estado)

            estado = next_estado
            total_reward += reward

        # Decaimiento de Epsilon
        # Hacemos que decaiga más lento (0.9995) para asegurar que siga explorando 
        # lo suficiente dado que el tablero es más grande.
        if agente.epsilon > 0.05:
            agente.epsilon *= 0.9995 

        # Registro de métricas crudas
        victorias.append(1 if tablero.victoria else 0)
        temp_rewards.append(total_reward)

        # Registro de estadísticas periódicas
        if episodio % SHOW_EVERY == 0 and episodio > 0:
            avg_winrate = sum(victorias[-SHOW_EVERY:]) / SHOW_EVERY
            avg_reward = sum(temp_rewards[-SHOW_EVERY:]) / SHOW_EVERY
            
            history_episodios.append(episodio)
            history_winrate.append(avg_winrate * 100) # Porcentaje
            history_epsilon.append(agente.epsilon)
            history_rewards.append(avg_reward)
            
            print(f"Episodio: {episodio}, Win Rate: {avg_winrate*100:.1f}%, Epsilon: {agente.epsilon:.3f}, Avg Reward: {avg_reward:.1f}")
            # Opcional: Imprimir los pesos para ver qué está aprendiendo el agente
            # print(f"   Pesos: {[round(w, 2) for w in agente.weights]}")

    # Guardar el agente (esto guardará la lista de pesos 'weights')
    agente.guardar_agente("mi_agente_entrenado.pkl")
    print("Entrenamiento finalizado. Agente guardado.")

    # --- GENERAR GRÁFICOS ---
    fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # 1. Gráfico de Win Rate
    axs[0].plot(history_episodios, history_winrate, color="green", label="Win Rate (%)")
    axs[0].set_ylabel("Victorias (%)")
    axs[0].set_title(f"Evolución del Aprendizaje (Aproximado {SIZE}x{SIZE})")
    axs[0].grid(True)
    axs[0].legend()

    # 2. Gráfico de Recompensas Promedio
    axs[1].plot(history_episodios, history_rewards, color="blue", label="Recompensa Promedio")
    axs[1].set_ylabel("Puntos")
    axs[1].grid(True)
    axs[1].legend()

    # 3. Gráfico de Epsilon
    axs[2].plot(history_episodios, history_epsilon, color="orange", label="Epsilon (Exploración)")
    axs[2].set_ylabel("Prob. Exploración")
    axs[2].set_xlabel("Episodios")
    axs[2].grid(True)
    axs[2].legend()

    plt.tight_layout()
    plt.savefig("metricas_entrenamiento.png")
    print("Gráfico guardado como 'metricas_entrenamiento.png'")
    plt.close()

if __name__ == "__main__":
    main()