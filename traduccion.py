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


def obtener_tamaño_recomendado(imagen: np.ndarray) -> int:
    """
    Obtiene el tamaño recomendado de malla basado en el tamaño de la imagen.
    Usa la dimensión menor de la imagen como N.
    Asegura que N sea >= 5.
    
    Args:
        imagen: array uint8 de la imagen.
    
    Returns:
        int N para usar como tamaño de malla.
    """
    altura, ancho = imagen.shape
    N = min(altura, ancho)
    # Asegurar N >= 5 y <= 200 para evitar sistemas muy grandes
    N = max(5, min(N, 200))
    return N


def imagen_a_malla(imagen: np.ndarray, N: int) -> np.ndarray:
    """
    Redimensiona la imagen a N×N usando interpolación bilineal.
    Normaliza a [0.0, 1.0].
    
    Args:
        imagen: array uint8 de la imagen original.
        N: tamaño de malla deseado (N×N).
    
    Returns:
        array float64 de shape (N, N) con valores en [0, 1].
    """
    pil_image = Image.fromarray(imagen, mode="L")
    # Redimensionar con interpolación bilineal (BILINEAR)
    pil_resized = pil_image.resize((N, N), Image.Resampling.BILINEAR)
    # Convertir a numpy y normalizar a [0, 1]
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
    N = malla.shape[0]
    
    # Mapear TODA la imagen a temperaturas
    # Valores claros (1) → T_max
    # Valores oscuros (0) → T_min
    T = T_min + malla * (T_max - T_min)
    
    return T
