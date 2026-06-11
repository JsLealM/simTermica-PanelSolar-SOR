import numpy as np
from traduccion import cargar_imagen_grises, obtener_tamaño_recomendado, imagen_a_malla, aplicar_condiciones_frontera

print('Diagnóstico: Ubicación de T_max')
print('=' * 60)

# Cargar imagen
img = cargar_imagen_grises('imagenes_ejemplo/panel_solar_test.png')
N = obtener_tamaño_recomendado(img)
malla = imagen_a_malla(img, N)
T_inicial = aplicar_condiciones_frontera(malla, T_min=20.0, T_max=100.0)
alto, ancho = N

print(f'Temperatura inicial: [{T_inicial.min():.2f}, {T_inicial.max():.2f}]°C')
print(f'\nBúsqueda de máximo:')

# Encontrar posición de máximo
pos_max = np.unravel_index(np.argmax(T_inicial), T_inicial.shape)
T_max_valor = T_inicial[pos_max]
print(f'  Posición: {pos_max}')
print(f'  Valor: {T_max_valor:.2f}°C')

# Verificar si está en frontera
i, j = pos_max
es_frontera = (i == 0) or (i == alto-1) or (j == 0) or (j == ancho-1)
print(f'  ¿Está en frontera?: {es_frontera}')

# Mostrar distribución de máximos
print(f'\nDistribución espacial del T_max:')
umbral = T_inicial.max() - 1.0  # Dentro de 1°C del máximo
muy_calientes = np.sum(T_inicial > umbral)
print(f'  Píxeles > {umbral:.1f}°C: {muy_calientes}')

# Mostrar valores en cada frontera
print(f'\nValores en cada frontera:')
print(f'  Arriba (fila 0): min={T_inicial[0, :].min():.2f}, max={T_inicial[0, :].max():.2f}')
print(f'  Abajo (fila {alto-1}): min={T_inicial[alto-1, :].min():.2f}, max={T_inicial[alto-1, :].max():.2f}')
print(f'  Izquierda (col 0): min={T_inicial[:, 0].min():.2f}, max={T_inicial[:, 0].max():.2f}')
print(f'  Derecha (col {ancho-1}): min={T_inicial[:, ancho-1].min():.2f}, max={T_inicial[:, ancho-1].max():.2f}')

# Mostrar malla normalizada para comparar
print(f'\nMalla normalizada:')
print(f'  [{malla.min():.4f}, {malla.max():.4f}]')
pos_max_malla = np.unravel_index(np.argmax(malla), malla.shape)
print(f'  Máximo en posición: {pos_max_malla}')
