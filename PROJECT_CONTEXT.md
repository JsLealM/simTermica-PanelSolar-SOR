# PROJECT_CONTEXT.md
# Simulador de Distribución de Temperatura — Panel Solar Fotovoltaico
# Proyecto de Aula · Algoritmos Numéricos para Ingeniería · Corte 3
# Universidad de Pamplona · Docente: Sebastián Echavez Cadena

---

## 1. RESUMEN DEL PROYECTO

Software de escritorio en Python que, dado una imagen de un panel solar fotovoltaico
en escala de grises, resuelve la distribución de temperatura en estado estacionario
usando el método SOR (Successive Over-Relaxation) sobre el sistema lineal generado
por el filtro laplaciano discreto. La salida principal es un mapa de calor superpuesto
a la geometría del panel con métricas numéricas de convergencia.

**Integrantes:** Johan Leal · Wilson Villamizar · Rusbell  
**Repositorio:** https://github.com/wilsonvdev/Algoritmos_numericos_mapa-de-calor

---

## 2. MODELO MATEMÁTICO

### 2.1 Pipeline: imagen → sistema lineal → solución → mapa de calor

```
Imagen JPG/PNG/BMP
        ↓
Convertir a escala de grises (si no lo está ya)
        ↓
Escalar a malla N×N (interpolación bilineal)  ← N configurable, default 30
        ↓
Mapeo píxel → temperatura de frontera (condiciones Dirichlet)
        ↓
Construir sistema Ax = b (filtro laplaciano)
        ↓
Resolver con SOR → vector x de temperaturas interiores
        ↓
Reconstruir malla 2D → mapa de calor con matplotlib
```

### 2.2 Mapeo píxel → temperatura

Cada píxel del borde de la imagen (frame exterior) se convierte en condición de
frontera de tipo Dirichlet:

```
T_frontera[i][j] = T_min + (pixel[i][j] / 255) * (T_max - T_min)
```

Parámetros físicos justificados:
- T_min = 25 °C  → borde sombreado / temperatura ambiente
- T_max = 75 °C  → zona de máxima irradiancia (paneles en verano: 55–75 °C)

Los nodos interiores tienen temperatura inicial = 0 (o promedio de frontera).
Son las incógnitas del sistema.

### 2.3 Ecuación física

Conducción de calor en estado estacionario — ecuación de Poisson 2D:

```
∂²T/∂x² + ∂²T/∂y² = -f(x,y) / k
```

Con f=0 (sin fuentes internas explícitas) se reduce a Laplace. La imagen ya
codifica las condiciones de frontera; no se necesita término fuente separado.

### 2.4 Discretización — Filtro Laplaciano (fórmula del profesor)

Stencil de cinco puntos con parámetro λ, aplicado sobre el nodo interior (i,j):

```
(1 + 4λ)·x[i][j]  −  λ·x[i-1][j]  −  λ·x[i+1][j]  −  λ·x[i][j-1]  −  λ·x[i][j+1]  =  b[i][j]
```

- Cuando λ = 1 → Laplaciano clásico discreto (four-neighbor averaging)
- Los vecinos en el borde pasan al lado derecho → contribuyen a b[i][j]
- Cada nodo interior genera UNA ecuación; malla N×N → sistema N²×N²

**Rango recomendado de λ:**

| λ          | Efecto                                              |
|------------|-----------------------------------------------------|
| 0          | Sin cambio (imagen idéntica a entrada)               |
| 0.1        | Suavizado muy leve                                  |
| 0.2 – 0.4  | Suavizado ligero, reduce ruido sin alterar estructura|
| 0.5 – 0.7  | Equilibrio suavizado/nitidez — mapeo térmico ideal  |
| 0.8 – 1.0  | Suavizado fuerte, λ=1 es el Laplaciano clásico      |
| > 1.0      | Amplifica ruido — evitar                            |
| -0.1 a -0.5| Realce de bordes (zonas térmicas marcadas)          |

**Para la simulación térmica: λ ∈ [0.5, 1.0], default λ = 1.0**

### 2.5 Construcción de A y b

Para malla de (N-2)×(N-2) nodos interiores (los bordes son frontera),
ordenando nodos por filas (row-major):

```python
# Índice del nodo (i,j) en el vector x: idx = i * n_cols + j
# donde i,j van de 0 a (N-2)-1 sobre los interiores

# Diagonal principal: (1 + 4λ)
A[idx][idx] = 1 + 4*lambda_val

# Vecinos (si son interiores → entrada en A; si son frontera → van a b)
# Vecino arriba    (i-1, j): A[idx][idx - n_cols] = -lambda_val
# Vecino abajo     (i+1, j): A[idx][idx + n_cols] = -lambda_val
# Vecino izquierda (i, j-1): A[idx][idx - 1]      = -lambda_val
# Vecino derecha   (i, j+1): A[idx][idx + 1]      = -lambda_val

# Si vecino es frontera: b[idx] += lambda_val * T_frontera[vecino]
```

**Propiedades de A** (garantizan convergencia de SOR):
- Dispersa (sparse): ≤ 5 entradas no nulas por fila
- Simétrica y definida positiva
- Diagonalmente dominante: (1+4λ) > 4λ para todo λ > 0
- Para N=30 → A es 784×784 con ~3920 entradas no nulas

**Nota de implementación:** NO construir A como matriz densa. Usar el stencil
directamente en el loop de SOR (in-place sobre la malla 2D) para eficiencia de
memoria. Para matrices pequeñas (N≤50) se puede construir A densa con numpy;
para N grandes, aplicar el stencil directamente.

### 2.6 Parámetros del modelo (tabla completa)

| Parámetro      | Valor / rango     | Justificación                                            |
|----------------|-------------------|----------------------------------------------------------|
| T_min          | 25 °C             | Temperatura ambiente / borde sombreado (STC reference)   |
| T_max          | 75 °C             | Irradiancia máxima en verano (literatura fotovoltaica)   |
| λ (laplaciano) | 1.0 (default)     | Laplaciano clásico; usuario puede ajustar en [−0.5, 1.5] |
| N (malla)      | 30 × 30           | Balance resolución / tiempo de cómputo                   |
| ω (SOR)        | 1.81              | ω_opt = 2 / (1 + sin(π/30)) ≈ 1.81                      |
| ε (tolerancia) | 1 × 10⁻⁶          | Norma infinito entre iteraciones consecutivas            |
| max_iter       | 5000              | Límite de seguridad; si no converge → reportar           |

---

## 3. MÉTODO SOR

### 3.1 Fórmula iterativa (dada por el profesor)

```
x_i^(k+1) = (1 - ω) · x_i^(k)  +  (ω / a_ii) · ( b_i  −  Σ_{j<i} a_ij·x_j^(k+1)  −  Σ_{j>i} a_ij·x_j^(k) )
```

Aplicada al stencil laplaciano en la malla 2D (forma eficiente, sin construir A):

```python
def sor_step(T, T_frontera, lambda_val, omega, N):
    """Una iteración SOR sobre la malla T (incluye bordes fijos)."""
    error = 0.0
    for i in range(1, N-1):           # nodos interiores fila
        for j in range(1, N-1):       # nodos interiores columna
            T_gs = (lambda_val * (T[i-1][j] + T[i+1][j] + T[i][j-1] + T[i][j+1])
                   ) / (1 + 4*lambda_val)   # Gauss-Seidel puro
            T_new = (1 - omega) * T[i][j] + omega * T_gs
            error = max(error, abs(T_new - T[i][j]))
            T[i][j] = T_new
    return error   # norma infinito de la diferencia
```

### 3.2 Criterio de parada

```
‖x^(k+1) − x^(k)‖_∞ < ε   →   CONVERGIÓ
k >= max_iter               →   NO CONVERGIÓ (reportar advertencia)
```

### 3.3 ω óptimo teórico

```
ω_opt = 2 / (1 + sin(π / N))
```

Para N=30: ω_opt ≈ 1.81  
Con ω_opt, SOR converge 3–10× más rápido que Jacobi.  
El usuario puede modificar ω; el software valida que ω ∈ (0, 2).

### 3.4 Registro de convergencia

En cada iteración guardar: `(iteracion, error_actual)` → lista de tuplas.
Se usa para la gráfica error-vs-iteración y para exportar CSV.

---

## 4. ARQUITECTURA — 5 CAPAS

```
proyecto_panel_solar/
├── main.py                  # Punto de entrada — instancia interfaz y arranca mainloop
├── interfaz.py              # CAPA 1 — GUI (tkinter + matplotlib embebido)
├── controlador.py           # CAPA 2 — Coordinación y validación
├── traduccion.py            # CAPA 3 — Imagen → matriz numérica → Ax=b
├── servicios.py             # CAPA 5 — Exportación, gráficas, mensajes
├── metodos/
│   ├── __init__.py
│   └── sor.py               # CAPA 4 — Implementación SOR pura (solo cálculo)
├── resultados/
│   ├── convergencia_sor.csv
│   └── mapa_calor.png
├── imagenes_ejemplo/
│   └── panel_solar.png
└── docs/
    ├── entregable_semana1.docx
    └── boceto_interfaz.png
```

---

## 5. RESPONSABILIDAD DE CADA CAPA

### CAPA 1 — interfaz.py
**Tecnología:** tkinter + matplotlib (FigureCanvasTkAgg)  
**Responsabilidad EXCLUSIVA:** todo lo visual, cero lógica de negocio.

Widgets que debe contener:
- Panel izquierdo (controles):
  - Label + botón "Cargar Imagen" → abre filedialog, llama controlador
  - Entry: N (tamaño malla), default 30, validación solo enteros
  - Entry: Tolerancia ε, default 1e-6
  - Entry: Máx. iteraciones, default 5000
  - Entry + Slider: ω ∈ (0, 2), default 1.81
  - Entry: λ (filtro laplaciano), default 1.0
  - Label fijo "SOR" con badge visual "activo"
  - Botón "Calcular" → llama controlador.ejecutar()
  - Botón "Limpiar" → resetea estado
  - Botón "Salir" → cierra ventana
- Panel central:
  - FigureCanvas matplotlib: imagen en grises (izquierda) + mapa de calor (derecha)
  - FigureCanvas matplotlib: gráfica error-vs-iteración
- Panel derecho:
  - Labels de métricas: iteraciones, error final, tiempo (s), T_max (°C), convergió S/N
  - Botón "Guardar mapa calor" → llama servicios
  - Botón "Exportar CSV" → llama servicios
  - Botón "Guardar gráfica PNG" → llama servicios
- Status bar inferior con texto de estado

**NO debe:** importar numpy directamente para cálculos, leer imágenes, hacer math.

---

### CAPA 2 — controlador.py
**Responsabilidad EXCLUSIVA:** orquestar el flujo, validar entradas, manejar errores.

```python
class Controlador:
    def cargar_imagen(self, ruta: str) -> np.ndarray:
        # 1. Llama traduccion.cargar_imagen_grises(ruta)
        # 2. Devuelve la imagen a interfaz para mostrarla
        
    def ejecutar(self, params: dict) -> ResultadoSOR:
        # Valida params:
        #   - omega en (0, 2) estricto → error si no
        #   - tolerancia > 0 → error si no
        #   - lambda != 0 → advertencia si es 0
        #   - N >= 5 → error si menor
        # 1. traduccion.imagen_a_malla(imagen, N)
        # 2. traduccion.construir_condiciones_frontera(malla, T_min, T_max)
        # 3. metodos.sor.resolver(malla_con_frontera, params)
        # 4. Devuelve ResultadoSOR a interfaz
```

**Parámetros que recibe del form (dict):**
```python
{
    "omega": float,       # factor de relajación
    "tolerancia": float,  # ε criterio de parada
    "max_iter": int,      # iteraciones máximas
    "N": int,             # tamaño de malla
    "lambda_val": float,  # parámetro del filtro laplaciano
    "T_min": float,       # temperatura mínima (°C)
    "T_max": float,       # temperatura máxima (°C)
}
```

**Objeto ResultadoSOR que devuelve:**
```python
@dataclass
class ResultadoSOR:
    malla_resultado: np.ndarray      # malla N×N con temperaturas finales
    iteraciones: int                  # cuántas iteraciones se hicieron
    error_final: float                # error en la última iteración
    tiempo_seg: float                 # tiempo de cómputo en segundos
    convergio: bool                   # True si alcanzó ε, False si agotó max_iter
    historial_error: list[float]      # error por iteración (para la gráfica)
    T_max_calculada: float            # temperatura máxima en la malla resultado
    T_min_calculada: float            # temperatura mínima en la malla resultado
```

---

### CAPA 3 — traduccion.py
**Responsabilidad EXCLUSIVA:** conversión de datos. Cero GUI, cero SOR.

```python
def cargar_imagen_grises(ruta: str) -> np.ndarray:
    """
    Abre imagen en cualquier formato (JPG, PNG, BMP).
    Convierte a escala de grises (modo 'L' de Pillow).
    Devuelve array numpy uint8 de shape (H, W).
    """

def imagen_a_malla(imagen: np.ndarray, N: int) -> np.ndarray:
    """
    Redimensiona la imagen a N×N usando interpolación bilineal (PIL.BILINEAR).
    Convierte a float64 normalizado [0.0, 1.0].
    Devuelve array N×N.
    """

def aplicar_condiciones_frontera(malla: np.ndarray, T_min: float, T_max: float) -> np.ndarray:
    """
    Mapea los valores de borde (frame exterior) a temperaturas reales.
    T_frontera = T_min + valor_normalizado * (T_max - T_min)
    Los nodos interiores se inicializan con el promedio de la frontera.
    Devuelve malla N×N con float64 en °C (bordes fijos, interiores inicializados).
    """
```

**Librerías permitidas:** Pillow (PIL), numpy. Nada más.

---

### CAPA 4 — metodos/sor.py
**Responsabilidad EXCLUSIVA:** cálculo numérico del método SOR. Sin imports de GUI, sin Pillow.

```python
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
    Ejecuta SOR sobre la malla.
    Los bordes de malla_inicial son las condiciones de Dirichlet fijas —
    NO se modifican durante la iteración.
    
    Retorna dict con claves:
        malla_resultado: np.ndarray  — malla final con temperaturas
        iteraciones: int
        error_final: float
        tiempo_seg: float
        convergio: bool
        historial_error: list[float]
    """
    T = malla_inicial.copy().astype(np.float64)
    N = T.shape[0]
    historial = []
    t_inicio = time.time()
    
    for k in range(max_iter):
        error = 0.0
        for i in range(1, N-1):
            for j in range(1, N-1):
                # Fórmula del profesor aplicada al stencil laplaciano:
                # a_ii = (1 + 4λ),  vecinos = −λ
                T_gs = (lambda_val * (T[i-1][j] + T[i+1][j] +
                                      T[i][j-1] + T[i][j+1])) / (1 + 4*lambda_val)
                T_new = (1 - omega) * T[i][j] + omega * T_gs
                error = max(error, abs(T_new - T[i][j]))
                T[i][j] = T_new
        
        historial.append(error)
        if error < tolerancia:
            return {
                "malla_resultado": T,
                "iteraciones": k + 1,
                "error_final": error,
                "tiempo_seg": time.time() - t_inicio,
                "convergio": True,
                "historial_error": historial,
            }
    
    return {
        "malla_resultado": T,
        "iteraciones": max_iter,
        "error_final": historial[-1] if historial else float("inf"),
        "tiempo_seg": time.time() - t_inicio,
        "convergio": False,
        "historial_error": historial,
    }
```

**Optimización opcional (numpy vectorizado):**
```python
# Reemplaza el doble for con operaciones numpy por color de tablero (red-black SOR)
# Solo si se necesita performance para N > 100
```

---

### CAPA 5 — servicios.py
**Responsabilidad EXCLUSIVA:** exportación y visualización. Sin lógica de negocio.

```python
def guardar_mapa_calor(malla: np.ndarray, ruta: str, T_min: float, T_max: float) -> None:
    """
    Genera imagen PNG del mapa de calor con colormap 'hot' o 'plasma'.
    Incluye colorbar con escala en °C.
    """

def exportar_csv(historial_error: list, ruta: str) -> None:
    """
    Exporta columnas: iteracion, error
    Formato CSV estándar, separador coma, header incluido.
    """

def guardar_grafica_convergencia(historial_error: list, ruta: str, iteraciones: int) -> None:
    """
    Gráfica matplotlib: eje X = iteraciones, eje Y = error (escala log).
    Línea de tolerancia marcada. Guarda como PNG.
    """

def generar_figura_doble(imagen_grises: np.ndarray, malla_resultado: np.ndarray,
                          T_min: float, T_max: float) -> plt.Figure:
    """
    Devuelve Figure matplotlib con dos subplots lado a lado:
    - Izquierda: imagen original en grises (cmap='gray')
    - Derecha: mapa de calor (cmap='hot') con colorbar en °C
    Para embeber en la interfaz tkinter.
    """
```

---

## 6. FLUJO DE DATOS COMPLETO (request → response)

```
Usuario presiona "Calcular"
         │
         ▼
interfaz.py  →  lee campos del form  →  dict params
         │
         ▼
controlador.py.ejecutar(params)
    │    ├─ valida omega, epsilon, N, lambda
    │    ├─ traduccion.imagen_a_malla(imagen_cargada, N)
    │    ├─ traduccion.aplicar_condiciones_frontera(malla, T_min, T_max)
    │    └─ metodos.sor.resolver(malla, omega, lambda, tol, max_iter)
    │              │
    │              └─ retorna dict crudo
    │
    ├─ empaqueta ResultadoSOR
    └─ retorna a interfaz
         │
         ▼
interfaz.py
    ├─ servicios.generar_figura_doble()  →  actualiza canvas matplotlib
    ├─ actualiza labels métricas (iters, error, tiempo, T_max)
    ├─ servicios.guardar_mapa_calor()    →  (si usuario lo pide)
    └─ servicios.exportar_csv()          →  (si usuario lo pide)
```

---

## 7. DEPENDENCIAS Y ENTORNO

```python
# requirements.txt
numpy>=1.24
Pillow>=10.0
matplotlib>=3.7
# tkinter viene incluido en Python estándar — NO necesita pip install
```

```bash
# Instalación
pip install numpy Pillow matplotlib

# Ejecución
python main.py
```

**Python:** 3.10+  
**SO compatible:** Windows, Linux, macOS (tkinter en todas)

---

## 8. RESTRICCIONES ESTRICTAS DEL PROYECTO

1. **No mezclar responsabilidades entre capas** — el profesor lo verificará
2. **Solo SOR como método** — no implementar Jacobi, GS ni SSOR
3. **Escala de grises obligatoria** — la imagen siempre se convierte a gris
4. **ω validado en (0, 2) estricto** — rechazar valores fuera del intervalo
5. **λ validado ≠ 0** — con λ=0 la ecuación es trivial (imagen = entrada)
6. **Comentarios en todo el código** — nombres de variables en español o inglés claro
7. **Los bordes de la malla son inmutables durante SOR** — solo se actualizan interiores
8. **No usar scipy.linalg.solve** — el punto es implementar SOR manualmente

---

## 9. CASOS DE PRUEBA ESPERADOS

| Caso                        | Comportamiento esperado                                  |
|-----------------------------|----------------------------------------------------------|
| ω = 1.0                     | Equivale a Gauss-Seidel; converge más lento              |
| ω = 1.81, N = 30            | Convergencia óptima, ~60–200 iters según imagen          |
| ω = 0.5                     | Sub-relajación, converge pero más lento que GS           |
| ω = 1.99                    | Límite superior, puede oscilar en algunas imágenes       |
| λ = 1.0                     | Laplaciano clásico, comportamiento estándar              |
| λ = 0.5                     | Suavizado moderado                                       |
| λ = -0.2                    | Realce de bordes térmicos                                |
| Imagen uniforme (gris 128)  | Distribución de temperatura uniforme ≈ 50 °C             |
| Imagen con punto negro      | Zona fría localizada visible en el mapa de calor         |
| Imagen con punto blanco     | Zona caliente localizada visible en el mapa de calor     |

---

## 10. NOTAS PARA EL DESARROLLADOR

- **El loop doble de SOR es O(N²) por iteración.** Para N=30 con ~100 iters son
  90.000 operaciones — perfectamente rápido en Python puro. No sobre-optimizar.

- **La malla incluye los bordes:** `T` es de shape `(N, N)`. Los índices `[1:-1, 1:-1]`
  son los interiores. Los bordes `[0,:], [-1,:], [:,0], [:,-1]` son Dirichlet fijos.

- **Matplotlib dentro de tkinter:** usar `FigureCanvasTkAgg`. La figura se actualiza
  con `canvas.draw()` después de cada cálculo. No abrir ventanas matplotlib separadas.

- **Colormap para el mapa de calor:** `'hot'` (negro→rojo→amarillo→blanco) o
  `'plasma'` — ambos son perceptualmente uniformes y transmiten temperatura bien.

- **Gráfica de convergencia:** eje Y en escala logarítmica (`ax.set_yscale('log')`).
  Añadir línea horizontal punteada en y=tolerancia.

- **El CSV de convergencia** tiene dos columnas: `iteracion,error`. Sin índice.
  Una fila por iteración realizada.

- **main.py** es mínimo:
  ```python
  from interfaz import Aplicacion
  if __name__ == "__main__":
      app = Aplicacion()
      app.mainloop()
  ```
