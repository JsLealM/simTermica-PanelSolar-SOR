"""
CAPA 4 - Método SOR
Implementación pura del método de Successive Over-Relaxation (SOR)
para resolver sistemas lineales generados por el discreto laplaciano.
"""

import numpy as np
import time


def resolver(
    malla_inicial: np.ndarray,
    omega: float,
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
        omega: factor de relajación ∈ (0, 2). Típicamente ≈1.81 óptimo.
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
    N = T.shape[0]
    historial = []
    
    # Guardar frontera original para mantenerla fija
    frontera_arriba = T[0, :].copy()
    frontera_abajo = T[N-1, :].copy()
    frontera_izq = T[:, 0].copy()
    frontera_der = T[:, N-1].copy()
    
    t_inicio = time.time()
    factor_vecinos = lambda_val
    divisor = 1.0 + 4.0 * lambda_val
    peso_sor = omega / divisor
    peso_anterior = 1.0 - omega
    
    for k in range(max_iter):
        error = 0.0
        # Iterar sobre nodos interiores (fila y columna de 1 a N-2 inclusive)
        for i in range(1, N - 1):
            fila_actual = T[i]
            fila_arriba = T[i - 1]
            fila_abajo = T[i + 1]
            fila_fuente = fuente[i]

            for j in range(1, N - 1):
                # Fórmula SOR aplicada al stencil laplaciano:
                # a_ii = (1 + 4λ), vecinos = -λ, b_i = fuente[i,j]
                # T_gs es la solución del sistema local (Gauss-Seidel puro)
                valor_anterior = fila_actual[j]
                suma_vecinos = fila_arriba[j] + fila_abajo[j] + fila_actual[j - 1] + fila_actual[j + 1]
                
                # Aplicar relajación SOR: combinación convexa entre iterada anterior y T_gs
                T_new = peso_anterior * valor_anterior + peso_sor * (
                    fila_fuente[j] + factor_vecinos * suma_vecinos
                )
                
                # Actualizar error: norma infinito entre iteradas
                diferencia = T_new - valor_anterior
                if diferencia < 0:
                    diferencia = -diferencia
                if diferencia > error:
                    error = diferencia
                
                # In-place: actualizar malla
                fila_actual[j] = T_new
        
        # MANTENER frontera fija después de cada iteración
        T[0, :] = frontera_arriba
        T[N-1, :] = frontera_abajo
        T[:, 0] = frontera_izq
        T[:, N-1] = frontera_der
        
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
            }
    
    # Si no converge, retornar estado tras max_iter
    return {
        "malla_resultado": T,
        "iteraciones": max_iter,
        "error_final": historial[-1] if historial else float("inf"),
        "tiempo_seg": time.time() - t_inicio,
        "convergio": False,
        "historial_error": historial,
    }
