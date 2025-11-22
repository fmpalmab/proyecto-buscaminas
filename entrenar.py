# entrenar.py
from juego_model import Tablero
from agente import AgenteQLearning
import matplotlib.pyplot as plt
import numpy as np

# CONFIGURACIÓN DE ENTRENAMIENTO
EPISODIOS = 100000        # Aumentado para mejor aprendizaje
SIZE = 4                 # Tablero pequeño (4x4)
MINAS_RATIO = 0.2
SHOW_EVERY = 1000        # Recopilar métricas cada X episodios

def main():
    # 1. Inicializar entorno
    tablero = Tablero(SIZE, SIZE, MINAS_RATIO)
    acciones_posibles = [(x, y) for x in range(SIZE) for y in range(SIZE)]
    
    # 2. Inicializar Agente
    agente = AgenteQLearning(actions=acciones_posibles)
    
    # Listas para métricas
    victorias = []                 # Registro de victoria/derrota por partida (1 o 0)
    
    # Historial para graficar (se llenan cada SHOW_EVERY)
    history_episodios = []
    history_winrate = []
    history_epsilon = []
    history_rewards = []           # Promedio de recompensas cada SHOW_EVERY

    temp_rewards = []              # Para calcular promedio local de recompensas

    print(f"Iniciando entrenamiento en tablero {SIZE}x{SIZE}...")

    for episodio in range(EPISODIOS):
        tablero.reiniciar()
        estado = tablero.get_estado_hashable()
        terminado = False
        total_reward = 0

        while not terminado:
            # a. Agente elige acción
            accion = agente.elegir_accion(estado)
            x, y = accion

            # b. Entorno ejecuta acción
            next_estado, reward, terminado = tablero.step(x, y)

            # c. Agente aprende
            agente.aprender(estado, accion, reward, next_estado)

            estado = next_estado
            total_reward += reward

        # Decaimiento de Epsilon
        if agente.epsilon > 0.05:
            agente.epsilon *= 0.9999 

        # Registro de métricas crudas
        victorias.append(1 if tablero.victoria else 0)
        temp_rewards.append(total_reward)

        # Registro de estadísticas periódicas para el gráfico
        if episodio % SHOW_EVERY == 0 and episodio > 0:
            # Calcular promedios de los últimos SHOW_EVERY episodios
            avg_winrate = sum(victorias[-SHOW_EVERY:]) / SHOW_EVERY
            avg_reward = sum(temp_rewards[-SHOW_EVERY:]) / SHOW_EVERY
            
            history_episodios.append(episodio)
            history_winrate.append(avg_winrate * 100) # En porcentaje
            history_epsilon.append(agente.epsilon)
            history_rewards.append(avg_reward)
            
            print(f"Episodio: {episodio}, Win Rate: {avg_winrate*100:.1f}%, Epsilon: {agente.epsilon:.3f}, Avg Reward: {avg_reward:.1f}")

    # Guardar el agente
    agente.guardar_agente("mi_agente_entrenado.pkl")
    print("Entrenamiento finalizado. Agente guardado.")

    # --- GENERAR GRÁFICOS ---
    fig, axs = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # 1. Gráfico de Win Rate
    axs[0].plot(history_episodios, history_winrate, color="green", label="Win Rate (%)")
    axs[0].set_ylabel("Victorias (%)")
    axs[0].set_title(f"Evolución del Aprendizaje (Tablero {SIZE}x{SIZE})")
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