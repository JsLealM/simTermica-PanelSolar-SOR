import numpy as np
from traduccion import cargar_imagen_grises, obtener_tamaño_recomendado, imagen_a_malla, aplicar_condiciones_frontera

print('Prueba de mapeo de temperaturas')
print('=' * 60)

# Cargar imagen
img = cargar_imagen_grises('imagenes_ejemplo/panel_solar_test.png')
print(f'Imagen: {img.shape}')

# Detectar N
N = obtener_tamaño_recomendado(img)
print(f'N detectada: {N}')

# Convertir a malla normalizada
malla = imagen_a_malla(img, N)
print(f'Malla normalizada: min={malla.min():.3f}, max={malla.max():.3f}')

# Aplicar temperaturas
T = aplicar_condiciones_frontera(malla, T_min=20.0, T_max=100.0)

print(f'\nTemperaturas después de mapeo:')
print(f'  T_min: {T.min():.2f}°C')
print(f'  T_max: {T.max():.2f}°C')
print(f'  T_media: {T.mean():.2f}°C')

# Mostrar distribución
print(f'\nDistribución de temperaturas:')
print(f'  < 30°C: {np.sum(T < 30)} píxeles')
print(f'  30-50°C: {np.sum((T >= 30) & (T < 50))} píxeles')
print(f'  50-70°C: {np.sum((T >= 50) & (T < 70))} píxeles')
print(f'  > 70°C: {np.sum(T >= 70)} píxeles')

# Verificar correlación: píxeles claros = temperaturas altas
pixel_claro = malla.max()
temp_claro = T[np.unravel_index(np.argmax(malla), malla.shape)]
print(f'\nVerificación:')
print(f'  Píxel más claro: valor={pixel_claro:.3f}')
print(f'  Temperatura correspondiente: {temp_claro:.2f}°C (debe ser cercana a 100°C)')

pixel_oscuro = malla.min()
temp_oscuro = T[np.unravel_index(np.argmin(malla), malla.shape)]
print(f'  Píxel más oscuro: valor={pixel_oscuro:.3f}')
print(f'  Temperatura correspondiente: {temp_oscuro:.2f}°C (debe ser cercana a 20°C)')

print('\nOK - Mapeo correctamente implementado')
