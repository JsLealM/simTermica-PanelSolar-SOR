"""
CAPA 2 - Controlador
Orquestación del flujo y validación de parámetros.
Coordina traduccion, metodos.sor y servicios.
"""

from dataclasses import dataclass
import numpy as np

from traduccion import cargar_imagen_grises, imagen_a_malla, aplicar_condiciones_frontera, obtener_tamaño_recomendado
from metodos import sor
from energia import obtener_panel, calcular_mapa_potencia, calcular_potencia_total


@dataclass
class ResultadoSOR:
    """Resultado de la ejecución del método SOR."""
    malla_resultado: np.ndarray      # Malla N×N con temperaturas finales
    iteraciones: int                  # Número de iteraciones realizadas
    error_final: float                # Error en la última iteración
    tiempo_seg: float                 # Tiempo de cómputo en segundos
    convergio: bool                   # True si alcanzó tolerancia
    historial_error: list             # Errores por iteración
    T_max_calculada: float            # Temperatura máxima en resultado
    T_min_calculada: float            # Temperatura mínima en resultado
    T_media_calculada: float          # Temperatura media en resultado
    omega_usado: float                # Omega calculado o usado por SOR
    malla_potencia: np.ndarray        # Potencia estimada por pixel
    potencia_total: float             # Potencia DC total estimada
    potencia_max_pixel: float         # Potencia máxima por pixel
    potencia_min_pixel: float         # Potencia mínima por pixel
    tipo_panel: str                   # Tipo de panel usado
    gamma_pdc: float                  # Coeficiente térmico de potencia
    irradiancia: float                # Irradiancia usada W/m²
    pdc0: float                       # Potencia nominal usada W


class Controlador:
    """Controlador central del flujo de ejecución."""
    
    def __init__(self):
        self.imagen_cargada = None
        self.imagen_grises = None
        self.N_detectada = None
    
    def cargar_imagen(self, ruta: str) -> tuple:
        """
        Carga imagen desde ruta y la convierte a escala de grises.
        Detecta automáticamente el tamaño recomendado de malla.
        
        Args:
            ruta: ruta al archivo de imagen.
        
        Returns:
            tuple (imagen_array, N_detectada)
        
        Raises:
            FileNotFoundError: si la ruta no existe.
            IOError: si no se puede abrir como imagen.
        """
        try:
            self.imagen_grises = cargar_imagen_grises(ruta)
            self.N_detectada = obtener_tamaño_recomendado(self.imagen_grises)
            self.imagen_cargada = True
            return self.imagen_grises, self.N_detectada
        except Exception as e:
            raise RuntimeError(f"Error al cargar imagen: {e}")
    
    def ejecutar(self, params: dict) -> ResultadoSOR:
        """
        Ejecuta el flujo completo: imagen → malla → SOR → resultado.
        
        Args:
            params: diccionario con claves:
                - omega: factor de relajación (0, 2)
                - tolerancia: criterio de parada
                - max_iter: iteraciones máximas
                - N: tamaño de malla
                - lambda_val: parámetro del filtro laplaciano
                - T_min: temperatura mínima en °C
                - T_max: temperatura máxima en °C
        
        Returns:
            ResultadoSOR con resultado completo.
        
        Raises:
            ValueError: si parámetros son inválidos.
            RuntimeError: si no hay imagen cargada.
        """
        # 1. Validar parámetros
        self._validar_parametros(params)
        
        # 2. Verificar que hay imagen cargada
        if self.imagen_grises is None:
            raise RuntimeError("No hay imagen cargada. Cargue una primero.")
        
        # 3. Convertir imagen a malla
        tamaño = params["N"]
        malla_escalada = imagen_a_malla(self.imagen_grises, tamaño)
        
        # 4. Aplicar condiciones de frontera (mapeo de radiancia a temperatura)
        T_min = params["T_min"]
        T_max = params["T_max"]
        malla_con_frontera = aplicar_condiciones_frontera(malla_escalada, T_min, T_max)
        
        panel = obtener_panel(
            params.get("tipo_panel", "Monocristalino"),
            params.get("gamma_pdc")
        )
        pdc0 = float(params.get("pdc0", 450.0))
        irradiancia = float(params.get("irradiancia", 1000.0))

        # 5. Resolver siempre con SOR: es el método obligatorio del proyecto.
        resultado_sor = sor.resolver(
            malla_inicial=malla_con_frontera,
            omega=params.get("omega"),
            lambda_val=params["lambda_val"],
            tolerancia=params["tolerancia"],
            max_iter=params["max_iter"]
        )
        malla_final = resultado_sor["malla_resultado"]
        temperatura_media = float(np.mean(malla_final))
        malla_potencia = calcular_mapa_potencia(
            malla_final,
            pdc0=pdc0,
            irradiancia=irradiancia,
            gamma_pdc=panel.gamma_pdc
        )
        potencia_total = calcular_potencia_total(
            temperatura_media=temperatura_media,
            pdc0=pdc0,
            irradiancia=irradiancia,
            gamma_pdc=panel.gamma_pdc
        )
        
        # 6. Empaquetar resultado
        return ResultadoSOR(
            malla_resultado=malla_final,
            iteraciones=resultado_sor["iteraciones"],
            error_final=resultado_sor["error_final"],
            tiempo_seg=resultado_sor["tiempo_seg"],
            convergio=resultado_sor["convergio"],
            historial_error=resultado_sor["historial_error"],
            T_max_calculada=float(np.max(malla_final)),
            T_min_calculada=float(np.min(malla_final)),
            T_media_calculada=temperatura_media,
            omega_usado=float(resultado_sor.get("omega_usado", params.get("omega", 1.0))),
            malla_potencia=malla_potencia,
            potencia_total=potencia_total,
            potencia_max_pixel=float(np.max(malla_potencia)),
            potencia_min_pixel=float(np.min(malla_potencia)),
            tipo_panel=panel.nombre,
            gamma_pdc=panel.gamma_pdc,
            irradiancia=irradiancia,
            pdc0=pdc0
        )
    
    def _validar_parametros(self, params: dict) -> None:
        """
        Valida parámetros antes de ejecutar.
        
        Raises:
            ValueError: si algún parámetro es inválido.
        """
        # Validar omega ∈ (0, 2) estricto
        omega = params.get("omega")
        if omega is not None and not (0 < omega < 2):
            raise ValueError(f"omega debe estar en (0, 2). Recibido: {omega}")
        
        # Validar tolerancia > 0
        tolerancia = params.get("tolerancia", 1e-6)
        if tolerancia <= 0:
            raise ValueError(f"tolerancia debe ser > 0. Recibido: {tolerancia}")
        
        # Validar N >= 5
        tamaño = params.get("N", (30, 30))
        if isinstance(tamaño, int):
            filas, columnas = tamaño, tamaño
        else:
            filas, columnas = tamaño
        if filas < 5 or columnas < 5:
            raise ValueError(f"La malla debe ser al menos 5x5. Recibido: {filas}x{columnas}")
        
        # Validar lambda_val != 0 (con advertencia en log si es 0)
        lambda_val = params.get("lambda_val", 1.0)
        if lambda_val == 0:
            raise ValueError("lambda_val no puede ser 0 (ecuación trivial)")
        
        # Validar max_iter > 0
        max_iter = params.get("max_iter", 5000)
        if max_iter <= 0:
            raise ValueError(f"max_iter debe ser > 0. Recibido: {max_iter}")
        
        # Validar T_min < T_max
        T_min = params.get("T_min", 25.0)
        T_max = params.get("T_max", 75.0)
        if T_min >= T_max:
            raise ValueError(f"T_min debe ser < T_max. T_min={T_min}, T_max={T_max}")

        pdc0 = params.get("pdc0", 450.0)
        if pdc0 <= 0:
            raise ValueError(f"Pdc0 debe ser > 0. Recibido: {pdc0}")

        irradiancia = params.get("irradiancia", 1000.0)
        if irradiancia < 0:
            raise ValueError(f"Irradiancia debe ser >= 0. Recibido: {irradiancia}")
