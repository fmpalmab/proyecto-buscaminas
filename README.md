# Proyecto Buscaminas (Minesweeper)

Este repositorio contiene una implementación clásica del juego Buscaminas, desarrollada en Python 3 utilizando la librería gráfica `Tkinter`.

El proyecto fue desarrollado como parte del **Proyecto N°2** del curso **EL4203-2: Programación Avanzada** de la Facultad de Ciencias Físicas y Matemáticas (FCFM) de la Universidad de Chile.

El objetivo principal es aplicar los principios de la Programación Orientada a Objetos (POO) para separar la lógica del juego de la interfaz de usuario.

---

## 🚀 Cómo Empezar

Sigue estos pasos para ejecutar el juego en tu máquina local.

### 1. Prerrequisitos

* **Python 3:** El juego está escrito en Python 3. Asegúrate de tenerlo instalado (puedes verificar escribiendo `python3 --version` en tu terminal).

* **Tkinter:** Es la librería estándar de GUI de Python. Generalmente, viene preinstalada con Python.
    * Si por alguna razón no la tienes (común en algunas distribuciones de Linux), puedes instalarla:
        ```bash
        # Para Debian/Ubuntu
        sudo apt-get install python3-tk
        ```

* **Imágenes (¡Importante!):** El juego **requiere** la carpeta `images/` con todos los archivos `.gif` (`tile_plain.gif`, `tile_1.gif`, etc.) para funcionar. Asegúrate de que esta carpeta esté en el mismo directorio que `main.py`.

### 2. Instalación y Ejecución

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/fmpalmab/proyecto-buscaminas](https://github.com/fmpalmab/proyecto-buscaminas)
    ```

2.  **Navega a la carpeta del proyecto:**
    ```bash
    cd proyecto-buscaminas
    ```

3.  **Ejecuta el juego:**
    ```bash
    python3 main.py
    ```
    *(O `python main.py` si `python` es tu alias principal para Python 3).*

---

## 📂 Estructura del Proyecto

El código está separado en tres archivos principales para seguir un patrón de diseño Modelo-Vista-Controlador (MVC) simple:

* **`juego_model.py` (Modelo):**
    Contiene toda la lógica pura del juego, el estado del tablero y las reglas (clases `Tablero` y `Celda`). No tiene ninguna dependencia de `Tkinter` y no sabe nada sobre la interfaz gráfica.

* **`interfaz_gui.py` (Vista/Controlador):**
    Maneja toda la lógica de la interfaz de usuario (GUI) con `Tkinter`. Es responsable de crear los botones, cargar las imágenes, manejar los eventos de clic y actualizar la vista. Se comunica con el `juego_model` para procesar las jugadas.

* **`main.py` (Punto de Entrada):**
    El archivo ejecutable principal. Sus únicas responsabilidades son:
    1.  Iniciar la aplicación.
    2.  Crear la ventana raíz de `Tkinter`.
    3.  Instanciar el `Tablero` (modelo) y la `MinesweeperGUI` (vista).
    4.  Conectar ambos y lanzar el bucle principal de la aplicación.

---

## 🎮 Cómo Jugar

* **Clic Izquierdo:** Revela una celda.
* **Clic Derecho:** Coloca o quita una bandera.
* **Objetivo:** ¡Revela todas las celdas que no son minas para ganar!