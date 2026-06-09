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
- Cargar imágenes en escala de grises
- Configurar parámetros (N, tolerancia, máx iteraciones, ω, λ, T_min, T_max)
- Ejecutar simulación SOR
- Visualizar resultados (heatmap y gráfica de convergencia)
- Exportar resultados (CSV, PNG)

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

### Directorios:
- **metodos/**: Módulo con métodos numéricos
- **resultados/**: Almacena archivos exportados
- **imagenes_ejemplo/**: Imágenes de prueba (incluye test_image.png)
- **docs/**: Documentación adicional

## Parámetros de la Simulación

| Parámetro | Rango | Descripción |
|-----------|-------|-------------|
| N | ≥ 5 | Tamaño de la matriz NxN |
| ε (tolerancia) | > 0 | Criterio de convergencia |
| max_iter | > 0 | Máximo de iteraciones |
| ω (omega) | (0, 2) | Factor de relajación SOR |
| λ (lambda) | ≠ 0 | Parámetro de anisotropía térmica |
| T_min | < T_max | Temperatura mínima (K) |
| T_max | > T_min | Temperatura máxima (K) |

## Método Numérico

El sistema implementa el método SOR con la fórmula:

```
T_new[i,j] = (1-ω)·T_old[i,j] + ω·T_gs[i,j]
```

Donde:
- `T_gs` es la estimación de Gauss-Seidel de los vecinos
- `ω` es el factor de relajación (omega)
- Las condiciones de frontera (bordes) permanecen fijas

## Características

✓ Visualización en tiempo real de la simulación
✓ Gráfico de convergencia en escala logarítmica
✓ Exportación de resultados a CSV
✓ Generación de mapas de calor (PNG)
✓ Validación de parámetros automática
✓ Threading para prevenir congelamiento de la UI
✓ Indicadores de estado en tiempo real

## Imagen de Prueba

Se incluye `imagenes_ejemplo/test_image.png` para pruebas rápidas.

Para crear otras imágenes de prueba, use el formato PNG/JPG en escala de grises (L-mode).

## Notas Técnicas

- La GUI se ejecuta en el hilo principal
- Los cálculos SOR se ejecutan en un hilo separado
- Matplotlib se embebe en tkinter usando FigureCanvasTkAgg
- Color palette personalizado según especificación de diseño

## Documentación Adicional

- Ver `PROJECT_CONTEXT.md` para especificación completa
- Ver `DESIGN.md` para detalles de interfaz de usuario
