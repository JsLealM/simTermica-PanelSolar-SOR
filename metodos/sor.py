"""
CAPA 4 - Método SOR
Implementación pura del método de Successive Over-Relaxation (SOR)
para resolver sistemas lineales generados por el discreto laplaciano.
"""

import numpy as np
import time


def calcular_omega_optimo(shape: tuple[int, int]) -> float:
    """
    Calcula omega optimo aproximado para SOR en una malla rectangular.
    Usa el radio espectral teorico de Jacobi para Laplace 2D.
    """
    filas, columnas = shape
    filas_int = max(1, filas - 2)
    columnas_int = max(1, columnas - 2)
    rho = (
        np.cos(np.pi / (columnas_int + 1))
        + np.cos(np.pi / (filas_int + 1))
    ) / 2.0
    omega = 2.0 / (1.0 + np.sqrt(max(0.0, 1.0 - rho * rho)))
    # El valor teorico se acerca demasiado a 2 en mallas grandes.
    # Para este modelo con fuente por pixel, 1.90 mantiene sobrerrelajacion estable.
    return float(min(1.90, max(0.01, omega)))


def resolver(
    malla_inicial: np.ndarray,
    omega: float | None,
    lambda_val: float,
    tolerancia: float,
    max_iter: int
) -> dict:
    """
    Ejecuta SOR sobre la malla 2D de temperaturas.
    
    Los bordes de malla_inicial son las condiciones de Dirichlet fijas —
    NO se modifican durante la iteración.
    
    Args:
        malla_inicial: array numpy shape (N, N) con valores iniciales.
                       Los bordes [0,:], [-1,:], [:,0], [:,-1] son frontera fija.
        omega: factor de relajación ∈ (0, 2). Si es None, se calcula automático.
        lambda_val: parámetro del filtro laplaciano. Típicamente 1.0.
        tolerancia: criterio de parada (norma infinito entre iteraciones).
        max_iter: número máximo de iteraciones.
    
    Returns:
        dict con claves:
            - malla_resultado: array (N, N) con temperaturas finales
            - iteraciones: número de iteraciones realizadas
            - error_final: error en la última iteración
            - tiempo_seg: tiempo de cómputo en segundos
            - convergio: True si alcanzó tolerancia, False si max_iter agotado
            - historial_error: list[float] de errores por iteración
    """
    # La malla inicial ya contiene el mapeo píxel -> temperatura.
    # Se usa como término derecho b para que cada píxel de la imagen influya
    # en el sistema: (1 + 4λ)T_ij - λ(sum vecinos) = b_ij.
    fuente = malla_inicial.copy().astype(np.float64)
    T = fuente.copy()
    historial = []
    filas, columnas = T.shape
    if filas < 3 or columnas < 3:
        return {
            "malla_resultado": T,
            "iteraciones": 0,
            "error_final": 0.0,
            "tiempo_seg": 0.0,
            "convergio": True,
            "historial_error": historial,
            "omega_usado": omega if omega is not None else 1.0,
        }
    omega_usado = calcular_omega_optimo(T.shape) if omega is None else float(omega)
    
    # Guardar frontera original para mantenerla fija
    frontera_arriba = T[0, :].copy()
    frontera_abajo = T[filas-1, :].copy()
    frontera_izq = T[:, 0].copy()
    frontera_der = T[:, columnas-1].copy()

    ii, jj = np.indices((filas - 2, columnas - 2))
    mascara_roja = ((ii + jj) % 2) == 0
    mascara_negra = ~mascara_roja
    
    t_inicio = time.time()
    factor_vecinos = lambda_val
    divisor = 1.0 + 4.0 * lambda_val
    peso_sor = omega_usado / divisor
    peso_anterior = 1.0 - omega_usado
    
    for k in range(max_iter):
        error = 0.0

        for mascara in (mascara_roja, mascara_negra):
            interior = T[1:-1, 1:-1]
            suma_vecinos = (
                T[:-2, 1:-1]
                + T[2:, 1:-1]
                + T[1:-1, :-2]
                + T[1:-1, 2:]
            )
            valores_anteriores = interior[mascara].copy()
            valores_nuevos = peso_anterior * valores_anteriores + peso_sor * (
                fuente[1:-1, 1:-1][mascara] + factor_vecinos * suma_vecinos[mascara]
            )
            interior[mascara] = valores_nuevos
            if valores_nuevos.size:
                error_color = float(np.max(np.abs(valores_nuevos - valores_anteriores)))
                if error_color > error:
                    error = error_color
        
        # MANTENER frontera fija después de cada iteración
        T[0, :] = frontera_arriba
        T[filas-1, :] = frontera_abajo
        T[:, 0] = frontera_izq
        T[:, columnas-1] = frontera_der
        
        # Guardar error de esta iteración
        historial.append(error)
        
        # Criterio de parada: error converge por debajo de tolerancia
        if error < tolerancia:
            return {
                "malla_resultado": T,
                "iteraciones": k + 1,
                "error_final": error,
                "tiempo_seg": time.time() - t_inicio,
                "convergio": True,
                "historial_error": historial,
                "omega_usado": omega_usado,
            }
    
    # Si no converge, retornar estado tras max_iter
    return {
        "malla_resultado": T,
        "iteraciones": max_iter,
        "error_final": historial[-1] if historial else float("inf"),
        "tiempo_seg": time.time() - t_inicio,
        "convergio": False,
        "historial_error": historial,
        "omega_usado": omega_usado,
    }
