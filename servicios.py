"""
CAPA 5 - Servicios
Exportación, gráficas y visualización.
Sin lógica de negocio, solo generación de outputs.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import csv


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
    
    ax_left.imshow(imagen_norm, cmap="gray", vmin=0, vmax=1)
    ax_left.set_title("Imagen Original (Grises)", fontsize=12, fontweight="bold")
    ax_left.set_xlabel("Columna")
    ax_left.set_ylabel("Fila")
    
    # Subplot derecha: mapa de calor
    im = ax_right.imshow(malla_resultado, cmap="hot", vmin=T_min, vmax=T_max)
    ax_right.set_title("Mapa de Calor", fontsize=12, fontweight="bold")
    ax_right.set_xlabel("Columna")
    ax_right.set_ylabel("Fila")
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax_right)
    cbar.set_label("Temperatura (°C)", fontsize=10)
    
    fig.tight_layout()
    return fig
