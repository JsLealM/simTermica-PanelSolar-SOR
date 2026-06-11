"""
CAPA 5 - Servicios
Exportación, gráficas y visualización.
Sin lógica de negocio, solo generación de outputs.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import csv


def _reducir_para_visualizacion(malla: np.ndarray, max_dim: int = 900) -> tuple[np.ndarray, int]:
    """
    Reduce solo para pintar en pantalla/PNG interactivo.
    Los datos originales siguen completos en memoria y exportación.
    """
    alto, ancho = malla.shape[:2]
    paso = max(1, int(np.ceil(max(alto, ancho) / max_dim)))
    return malla[::paso, ::paso], paso


def guardar_mapa_calor(
    malla: np.ndarray,
    ruta: str,
    T_min: float = 25.0,
    T_max: float = 75.0
) -> None:
    """
    Genera y guarda imagen PNG del mapa de calor.
    
    Args:
        malla: array (N, N) de temperaturas.
        ruta: ruta destino para guardar PNG.
        T_min: temperatura mínima para normalizar colorbar (°C).
        T_max: temperatura máxima para normalizar colorbar (°C).
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    
    im = ax.imshow(malla, cmap="hot", vmin=T_min, vmax=T_max, origin="upper")
    ax.set_title("Mapa de Calor — Panel Solar Fotovoltaico", fontsize=14, fontweight="bold")
    ax.set_xlabel("Columna")
    ax.set_ylabel("Fila")
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Temperatura (°C)", fontsize=12)
    
    fig.tight_layout()
    fig.savefig(ruta, dpi=100, bbox_inches="tight")
    plt.close(fig)


def exportar_csv(historial_error: list, ruta: str) -> None:
    """
    Exporta historial de convergencia a CSV.
    Columnas: iteracion, error
    
    Args:
        historial_error: list[float] de errores por iteración.
        ruta: ruta destino para guardar CSV.
    """
    with open(ruta, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["iteracion", "error"])
        for idx, error in enumerate(historial_error, start=1):
            writer.writerow([idx, error])


def exportar_csv_pixeles(
    malla_temperatura: np.ndarray,
    malla_potencia: np.ndarray,
    ruta: str
) -> None:
    """
    Exporta temperatura y potencia estimada para cada pixel.
    Columnas: fila, columna, temperatura_C, potencia_W
    """
    filas, columnas = malla_temperatura.shape
    with open(ruta, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["fila", "columna", "temperatura_C", "potencia_W"])
        for i in range(filas):
            for j in range(columnas):
                writer.writerow([i, j, float(malla_temperatura[i, j]), float(malla_potencia[i, j])])


def guardar_grafica_convergencia(
    historial_error: list,
    ruta: str,
    iteraciones: int,
    tolerancia: float = 1e-6
) -> None:
    """
    Genera y guarda gráfica de convergencia (error vs iteración).
    Eje Y en escala logarítmica.
    
    Args:
        historial_error: list[float] de errores.
        ruta: ruta destino para PNG.
        iteraciones: número de iteraciones realizadas.
        tolerancia: valor de tolerancia a marcar como línea horizontal.
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    iterations_x = np.arange(1, len(historial_error) + 1)
    ax.semilogy(iterations_x, historial_error, "b-", linewidth=2, label="Error")
    
    # Línea de tolerancia
    ax.axhline(y=tolerancia, color="r", linestyle="--", linewidth=1.5, label=f"Tolerancia ε={tolerancia:.0e}")
    
    ax.set_xlabel("Iteración", fontsize=12)
    ax.set_ylabel("Error (escala log)", fontsize=12)
    ax.set_title("Convergencia SOR", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    fig.tight_layout()
    fig.savefig(ruta, dpi=100, bbox_inches="tight")
    plt.close(fig)


def generar_figura_doble(
    imagen_grises: np.ndarray,
    malla_resultado: np.ndarray,
    T_min: float = 25.0,
    T_max: float = 75.0
) -> Figure:
    """
    Genera Figure matplotlib con dos subplots lado a lado:
    - Izquierda: imagen original en grises
    - Derecha: mapa de calor con colorbar en °C
    
    Args:
        imagen_grises: array de imagen original (uint8 [0-255] o float [0-1]).
        malla_resultado: array de temperaturas finales.
        T_min: temperatura mínima para colorbar (°C).
        T_max: temperatura máxima para colorbar (°C).
    
    Returns:
        Figure matplotlib lista para embeber en tkinter (FigureCanvasTkAgg).
    """
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(8, 5), dpi=100)
    
    # Subplot izquierda: imagen original en grises
    if imagen_grises.dtype == np.uint8:
        imagen_norm = imagen_grises / 255.0
    else:
        imagen_norm = imagen_grises
    
    imagen_vista, paso_img = _reducir_para_visualizacion(imagen_norm)
    ax_left.imshow(imagen_vista, cmap="gray", vmin=0, vmax=1)
    ax_left.set_title("Imagen Original (Grises)", fontsize=12, fontweight="bold")
    ax_left.set_xlabel("Columna")
    ax_left.set_ylabel("Fila")
    
    # Subplot derecha: mapa de calor
    malla_vista, paso_heat = _reducir_para_visualizacion(malla_resultado)
    im = ax_right.imshow(
        malla_vista,
        cmap="hot",
        vmin=T_min,
        vmax=T_max,
        extent=(0, malla_resultado.shape[1] - 1, malla_resultado.shape[0] - 1, 0),
        aspect="auto",
    )
    ax_right.set_title("Mapa de Calor", fontsize=12, fontweight="bold")
    ax_right.set_xlabel("Columna")
    ax_right.set_ylabel("Fila")
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax_right)
    cbar.set_label("Temperatura (°C)", fontsize=10)
    
    fig.tight_layout()
    return fig


def generar_figura_individual(
    imagen_grises: np.ndarray,
    malla_resultado: np.ndarray,
    modo: str,
    T_min: float = 25.0,
    T_max: float = 75.0
) -> Figure:
    """Genera una figura grande para ver solo la imagen gris o solo el mapa."""
    fig, ax = plt.subplots(figsize=(10, 7), dpi=100)

    if modo == "gris":
        imagen_norm = imagen_grises / 255.0 if imagen_grises.dtype == np.uint8 else imagen_grises
        imagen_vista, _ = _reducir_para_visualizacion(imagen_norm, max_dim=1200)
        ax.imshow(imagen_vista, cmap="gray", vmin=0, vmax=1)
        ax.set_title("Imagen en escala de grises", fontsize=13, fontweight="bold")
    else:
        malla_vista, _ = _reducir_para_visualizacion(malla_resultado, max_dim=1200)
        im = ax.imshow(
            malla_vista,
            cmap="hot",
            vmin=T_min,
            vmax=T_max,
            extent=(0, malla_resultado.shape[1] - 1, malla_resultado.shape[0] - 1, 0),
            aspect="auto",
        )
        ax.set_title("Mapa de calor - Temperatura calculada", fontsize=13, fontweight="bold")
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label("Temperatura (°C)", fontsize=10)

    ax.set_xlabel("Columna")
    ax.set_ylabel("Fila")
    fig.tight_layout()
    return fig
