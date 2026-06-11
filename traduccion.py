"""
CAPA 3 - Traducción
Conversión de datos: imagen → matriz numérica → sistema lineal.
Sin lógica de GUI ni SOR. Solo manipulación de datos con PIL y numpy.
"""

import numpy as np
from PIL import Image


def cargar_imagen_grises(ruta: str) -> np.ndarray:
    """
    Abre imagen en cualquier formato (JPG, PNG, BMP).
    Convierte a escala de grises (modo 'L' de Pillow).
    
    Args:
        ruta: ruta a archivo de imagen.
    
    Returns:
        array numpy uint8 de shape (altura, ancho).
    
    Raises:
        FileNotFoundError: si la ruta no existe.
        IOError: si no se puede abrir como imagen.
    """
    imagen = Image.open(ruta).convert("L")  # 'L' = escala de grises
    return np.array(imagen, dtype=np.uint8)


def obtener_tamaño_recomendado(imagen: np.ndarray) -> tuple[int, int]:
    """
    Obtiene el tamaño recomendado de malla basado en el tamaño real de la imagen.
    Conserva la resolución original para no perder detalle.
    
    Args:
        imagen: array uint8 de la imagen.
    
    Returns:
        tuple (alto, ancho) para usar como tamaño de malla.
    """
    altura, ancho = imagen.shape
    return altura, ancho


def imagen_a_malla(imagen: np.ndarray, tamaño: int | tuple[int, int] | None = None) -> np.ndarray:
    """
    Convierte la imagen a malla normalizada [0.0, 1.0].
    Si se entrega un tamaño, redimensiona; si no, conserva resolución original.
    
    Args:
        imagen: array uint8 de la imagen original.
        tamaño: int para N×N, tuple (alto, ancho), o None para conservar resolución.
    
    Returns:
        array float64 con valores en [0, 1].
    """
    if tamaño is None or tuple(imagen.shape) == tuple(tamaño if isinstance(tamaño, tuple) else (tamaño, tamaño)):
        return imagen.astype(np.float64) / 255.0

    if isinstance(tamaño, int):
        alto, ancho = tamaño, tamaño
    else:
        alto, ancho = tamaño

    pil_image = Image.fromarray(imagen, mode="L")
    pil_resized = pil_image.resize((ancho, alto), Image.Resampling.BILINEAR)
    malla = np.array(pil_resized, dtype=np.float64) / 255.0
    return malla


def aplicar_condiciones_frontera(
    malla: np.ndarray,
    T_min: float,
    T_max: float
) -> np.ndarray:
    """
    Mapea TODA la imagen a temperaturas reales.
    - Valores oscuros (0) → T_min
    - Valores claros (1) → T_max
    
    Los bordes permanecen fijos (condición Dirichlet).
    Los interiores se inicializan con el mapeo de imagen y luego SOR los resuelve.
    
    Mapeo:
        T[i,j] = T_min + valor_normalizado[i,j] * (T_max - T_min)
    
    Args:
        malla: array (N, N) con valores en [0, 1] (de imagen_a_malla).
        T_min: temperatura mínima en °C (típicamente 25).
        T_max: temperatura máxima en °C (típicamente 75).
    
    Returns:
        array (N, N) float64 con temperaturas en °C.
        Toda la malla mapeada de imagen; bordes serán fijos en SOR.
    """
    # Mapear TODA la imagen a temperaturas
    # Valores claros (1) → T_max
    # Valores oscuros (0) → T_min
    T = T_min + malla * (T_max - T_min)
    
    return T
