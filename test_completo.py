import numpy as np
from traduccion import cargar_imagen_grises, obtener_tamaño_recomendado, imagen_a_malla, aplicar_condiciones_frontera
from metodos import sor

print('Prueba completa: Imagen -> Mapeo -> SOR')
print('=' * 60)

# Cargar imagen
img = cargar_imagen_grises('imagenes_ejemplo/panel_solar_test.png')
N = obtener_tamaño_recomendado(img)
print(f'Imagen cargada: {img.shape}, N detectada: {N}')

# Mapear a malla
malla = imagen_a_malla(img, N)
print(f'Malla normalizada: [{malla.min():.3f}, {malla.max():.3f}]')

# Aplicar temperaturas
T_inicial = aplicar_condiciones_frontera(malla, T_min=20.0, T_max=100.0)
print(f'Temperatura inicial: [{T_inicial.min():.2f}, {T_inicial.max():.2f}]°C')
print(f'Temperatura media inicial: {T_inicial.mean():.2f}°C')

# Resolver con SOR
print('\nResolviendo con SOR...')
resultado = sor.resolver(
    malla_inicial=T_inicial,
    omega=1.81,
    lambda_val=1.0,
    tolerancia=1e-4,
    max_iter=1000
)

print(f'Iteraciones: {resultado["iteraciones"]}')
print(f'Error final: {resultado["error_final"]:.2e}')
print(f'Convergio: {resultado["convergio"]}')
print(f'Tiempo: {resultado["tiempo_seg"]:.4f}s')

T_final = resultado['malla_resultado']
print(f'\nTemperatura final: [{T_final.min():.2f}, {T_final.max():.2f}]°C')
print(f'Temperatura media final: {T_final.mean():.2f}°C')

# Diferencia
print(f'\nDiferencia antes/después SOR:')
print(f'  Cambio en T_min: {T_inicial.min():.2f} -> {T_final.min():.2f} (diferencia: {T_final.min() - T_inicial.min():.2f}°C)')
print(f'  Cambio en T_max: {T_inicial.max():.2f} -> {T_final.max():.2f} (diferencia: {T_final.max() - T_inicial.max():.2f}°C)')
print(f'  Cambio en media: {T_inicial.mean():.2f} -> {T_final.mean():.2f} (diferencia: {T_final.mean() - T_inicial.mean():.2f}°C)')

# Distribución
print(f'\nDistribución de temperaturas finales:')
print(f'  < 30°C: {np.sum(T_final < 30)} píxeles')
print(f'  30-50°C: {np.sum((T_final >= 30) & (T_final < 50))} píxeles')
print(f'  50-70°C: {np.sum((T_final >= 50) & (T_final < 70))} píxeles')
print(f'  70-90°C: {np.sum((T_final >= 70) & (T_final < 90))} píxeles')
print(f'  > 90°C: {np.sum(T_final >= 90)} píxeles')

print('\nOK - Sistema funcionando correctamente')
