"""
Calculo energetico aproximado para paneles fotovoltaicos.

Usa el modelo PVWatts DC:
Pdc = (G / 1000) * Pdc0 * (1 + gamma_pdc * (T_cell - 25))
"""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class PanelPreset:
    nombre: str
    gamma_pdc: float
    eficiencia_ref: float


PANELES = {
    "Monocristalino": PanelPreset("Monocristalino", gamma_pdc=-0.0035, eficiencia_ref=0.20),
    "Policristalino": PanelPreset("Policristalino", gamma_pdc=-0.0040, eficiencia_ref=0.17),
    "Pelicula delgada": PanelPreset("Pelicula delgada", gamma_pdc=-0.0025, eficiencia_ref=0.12),
}


def obtener_panel(nombre: str, gamma_personalizado: float | None = None) -> PanelPreset:
    """Devuelve los parametros del panel seleccionado."""
    if nombre == "Personalizado":
        gamma = -0.0035 if gamma_personalizado is None else gamma_personalizado
        return PanelPreset("Personalizado", gamma_pdc=gamma, eficiencia_ref=0.18)
    return PANELES.get(nombre, PANELES["Monocristalino"])


def calcular_potencia_total(
    temperatura_media: float,
    pdc0: float,
    irradiancia: float,
    gamma_pdc: float,
    temp_ref: float = 25.0,
) -> float:
    """Calcula potencia DC total aproximada usando temperatura media del panel."""
    potencia = (irradiancia / 1000.0) * pdc0 * (1.0 + gamma_pdc * (temperatura_media - temp_ref))
    return max(0.0, float(potencia))


def calcular_mapa_potencia(
    malla_temperatura: np.ndarray,
    pdc0: float,
    irradiancia: float,
    gamma_pdc: float,
    temp_ref: float = 25.0,
) -> np.ndarray:
    """Distribuye la potencia nominal por pixel y aplica correccion termica local."""
    num_pixeles = malla_temperatura.size
    potencia_base_pixel = (irradiancia / 1000.0) * (pdc0 / num_pixeles)
    mapa = potencia_base_pixel * (1.0 + gamma_pdc * (malla_temperatura - temp_ref))
    return np.maximum(mapa, 0.0)
