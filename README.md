# Solar Panel Thermal Simulation System

Sistema de simulación térmica de paneles solares utilizando el método SOR (Successive Over-Relaxation) para resolver la ecuación de calor en 2D.

## Requisitos

- Python 3.8+
- Virtual Environment (venv)

## Instalación

### 1. Crear entorno virtual
```bash
python -m venv venv
```

### 2. Activar entorno virtual
**En Windows:**
```bash
venv\Scripts\activate
```

**En Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## Uso

### Ejecutar la aplicación
```bash
python main.py
```

Esto abrirá la interfaz gráfica de tkinter con todos los controles para:
- Cargar imágenes y convertirlas a escala de grises.
- Conservar la resolución real de la imagen (`alto × ancho`), sin forzar `N×N`.
- Configurar tolerancia, máximo de iteraciones, `λ`, `T_min`, `T_max`, tipo de panel, `Pdc0` e irradiancia.
- Calcular `ω` automáticamente para SOR.
- Ejecutar simulación SOR red-black vectorizada.
- Visualizar una sola imagen grande a la vez en el panel central: imagen gris o mapa de calor con flechas.
- Consultar temperatura y potencia por píxel moviendo el cursor sobre el mapa de calor.
- Exportar convergencia CSV, mapa PNG, gráfica PNG y CSV completo por píxel.

## Arquitectura del Proyecto (5 Capas)

```
CAPA 1: Interfaz (interfaz.py)
  ↓ Controlador
CAPA 2: Controlador (controlador.py)
  ↓ Traducción / Servicios
CAPA 3: Traducción (traduccion.py) ← Procesamiento de imágenes
CAPA 5: Servicios (servicios.py) ← Exportación y visualización
  ↓ Método numérico
CAPA 4: Método SOR (metodos/sor.py) ← Solver principal
```

## Componentes

### Archivos principales:
- **main.py**: Punto de entrada de la aplicación
- **interfaz.py**: GUI completa con tkinter
- **controlador.py**: Orquestador de la lógica de negocio
- **traduccion.py**: Manejo de imágenes y conversión a matrices térmicas
- **servicios.py**: Exportación de resultados y visualización
- **metodos/sor.py**: Implementación del solucionador SOR
- **energia.py**: Estimación aproximada de potencia con PVWatts DC

### Directorios:
- **metodos/**: Módulo con métodos numéricos
- **resultados/**: Almacena archivos exportados
- **imagenes_ejemplo/**: Imágenes de prueba (incluye test_image.png)
- **docs/**: Documentación adicional

## Parámetros de la Simulación

| Parámetro | Rango | Descripción |
|-----------|-------|-------------|
| Resolución | ≥ 5×5 | Se toma de la imagen cargada: `alto × ancho` |
| ε (tolerancia) | > 0 | Criterio de convergencia |
| max_iter | > 0 | Máximo de iteraciones, default actual 200 |
| ω (omega) | automático | Calculado por el sistema y limitado a 1.90 |
| λ (lambda) | ≠ 0 | Parámetro del filtro laplaciano |
| T_min | < T_max | Temperatura mínima (°C) |
| T_max | > T_min | Temperatura máxima (°C) |
| Tipo de panel | presets | Monocristalino, policristalino, película delgada |
| Pdc0 | > 0 W | Potencia nominal del panel |
| G | ≥ 0 W/m² | Irradiancia solar |

## Método Numérico

El sistema implementa SOR sobre el filtro laplaciano discreto:

```
(1 + 4λ)T_ij - λ(T_arriba + T_abajo + T_izquierda + T_derecha) = T_pixel
```

El valor tipo Gauss-Seidel se calcula como:

```
T_gs = (T_pixel + λ(vecinos)) / (1 + 4λ)
T_new = (1-ω)·T_old + ω·T_gs
```

Donde:
- `T_pixel` es la temperatura obtenida desde el píxel original
- `T_gs` es la estimación de Gauss-Seidel
- `ω` es el factor de relajación calculado automáticamente
- Las condiciones de frontera (bordes) permanecen fijas

Para rendimiento en imágenes grandes, `metodos/sor.py` usa SOR red-black vectorizado con NumPy.

## Estimación de Watts

La potencia aproximada se calcula con PVWatts DC:

```
P_dc = (G / 1000) * Pdc0 * (1 + gamma_pdc * (T_cell - 25))
```

Esta estimación depende de `Pdc0`, irradiancia, tipo de panel y temperatura media/píxel. La imagen por sí sola no determina la potencia nominal del panel.

## Características

✓ Visualización en tiempo real de la simulación
✓ Gráfico de convergencia en escala logarítmica
✓ Exportación de resultados a CSV
✓ Generación de mapas de calor (PNG)
✓ Exportación CSV por píxel: fila, columna, temperatura y potencia
✓ Consulta de temperatura/potencia por píxel en el mapa de calor
✓ Estimación de potencia con PVWatts DC
✓ Validación de parámetros automática
✓ Threading para prevenir congelamiento de la UI
✓ Indicadores de estado en tiempo real

## Imagen de Prueba

Se incluye `imagenes_ejemplo/test_image.png` para pruebas rápidas.

Para crear otras imágenes de prueba, use el formato PNG/JPG en escala de grises (L-mode).

## Notas Técnicas

- La GUI se ejecuta en el hilo principal.
- Los cálculos SOR se ejecutan en un hilo separado.
- Matplotlib se embebe en tkinter usando `FigureCanvasTkAgg`.
- Para imágenes grandes, la visualización puede reducirse internamente, pero la matriz de resultados conserva la resolución completa.
- La vista central alterna entre imagen en gris y mapa de calor con botones de flecha.

## Documentación Adicional

- Ver `PROJECT_CONTEXT.md` para especificación completa
- Ver `DESIGN.md` para detalles de interfaz de usuario
- Ver `docs/explicacion_traduccion_sor.md` para entender el flujo imagen → temperatura → SOR → watts
- Ver `docs/guia_parametros_watts_panel_solar.md` para rangos recomendados de parámetros fotovoltaicos
