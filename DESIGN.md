# DESIGN.md
# Simulador Térmico — Panel Solar Fotovoltaico
# Guía de diseño visual para implementación en tkinter (Python)
# Referencia visual: boceto SVG + captura de interfaz del entregable

---

## 0. ADVERTENCIA IMPORTANTE SOBRE TKINTER

tkinter NO soporta de forma nativa:
- border-radius / esquinas redondeadas en widgets estándar
- gradientes de color en fondos
- fuentes externas (Google Fonts, etc.) sin instalación adicional
- sombras o efectos de elevación
- animaciones CSS

Todo el diseño trabaja DENTRO de esas limitaciones usando:
- ttk.Style() para skinear widgets nativos
- Canvas() de tkinter para elementos visuales personalizados (badge SOR, indicador)
- Matplotlib embebido (FigureCanvasTkAgg) para gráficas y mapa de calor
- Composición por color y espaciado como herramientas principales

---

## 1. DIRECCIÓN ESTÉTICA

**Concepto:** Instrumental científico en tono claro — como un datasheet técnico
bien impreso. Fondo crema/hueso, panel lateral arena, acento ámbar solar.

**Referencia directa:** el boceto SVG generado durante el diseño del proyecto.
Mantener EXACTAMENTE esa paleta: no cambiar a dark theme, no cambiar el acento.

**Layout de referencia (del PNG en el entregable):**
- Columna izquierda: controles (imagen, parámetros, método, acciones)
- Columna central: mapa de calor ARRIBA (protagonista) + gráfica convergencia ABAJO
- Columna derecha: métricas numéricas + botones de exportación

**Lo memorable:** el header oscuro (#2C2C2A) con franja ámbar de 4px en el borde
izquierdo, contrastando con el cuerpo claro de la ventana. Y la barra de color
del mapa de calor (azul frío → verde → naranja → rojo) que atraviesa el centro.

---

## 2. PALETA DE COLORES
## (extraída directamente del SVG de referencia)

Todos los valores son hexadecimales, listos para usar en tkinter como strings "#RRGGBB".

### Fondos
```
BG_WINDOW     = "#FAFAF8"   # Fondo principal de la ventana — blanco cálido/crema
BG_PANEL      = "#F4F2EC"   # Panel lateral izquierdo y derecho — arena claro
BG_CARD       = "#FFFFFF"   # Tarjetas de métricas, entries — blanco puro
BG_HEADER     = "#2C2C2A"   # Header superior — casi negro cálido
BG_STATUSBAR  = "#2C2C2A"   # Status bar inferior — mismo que header
BG_INPUT      = "#FFFFFF"   # Fondo de Entry / campos de texto
BG_DROPZONE   = "#FAEEDA"   # Área de carga de imagen — ámbar muy suave
BG_BADGE      = "#FAEEDA"   # Fondo del badge SOR activo
```

### Texto
```
TEXT_HEADER    = "#FAF8F4"   # Texto sobre header oscuro — blanco cálido
TEXT_PRIMARY   = "#2C2C2A"   # Texto principal sobre fondo claro
TEXT_SECONDARY = "#888780"   # Labels secundarios, hints, unidades
TEXT_SECTION   = "#BA7517"   # Títulos de sección — ámbar oscuro (del SVG)
TEXT_MONO      = "#2C2C2A"   # Valores numéricos (monoespaciado)
TEXT_DISABLED  = "#C8C6C0"   # Campos y botones deshabilitados
TEXT_CAPTION   = "#888780"   # Status bar, captions pequeños
```

### Acento — Ámbar solar
```
ACCENT         = "#EF9F27"   # Acento principal (del SVG, franja del header)
ACCENT_DARK    = "#BA7517"   # Acento oscuro — títulos de sección, hover
ACCENT_SUBTLE  = "#FAEEDA"   # Fondo ámbar suave — dropzone, badge, notas
ACCENT_BTN     = "#2C2C2A"   # Fondo botón primario "Calcular" (oscuro, del SVG)
```

### Bordes y separadores
```
BORDER         = "#D3D1C7"   # Bordes entre secciones y widgets (del SVG)
BORDER_FOCUS   = "#BA7517"   # Borde de campo con foco
BORDER_HEADER  = "#EF9F27"   # Franja de 4px en borde izquierdo del header
```

### Estado
```
SUCCESS        = "#1D9E75"   # Verde — convergió (del SVG, badge verde)
WARNING        = "#EF9F27"   # Ámbar — advertencia
ERROR_BG       = "#FCEBEB"   # Fondo rojo suave — error en tabla (del SVG)
ERROR_TEXT     = "#A32D2D"   # Texto rojo — "No convergió" (del SVG)
SUCCESS_BG     = "#EAF3DE"   # Fondo verde suave — convergió (del SVG)
SUCCESS_TEXT   = "#3B6D11"   # Texto verde — "Sí" en tabla (del SVG)
```

### Colormap matplotlib — Mapa de calor
```python
# Gradiente de referencia del SVG (de fría a caliente):
#   #042C53  → azul noche    (25 °C)
#   #1D9E75  → verde agua    (40 °C)
#   #EF9F27  → ámbar         (55 °C)
#   #D85A30  → naranja rojo  (65 °C)
#   #993556  → rojo vino     (75 °C)

# En matplotlib usar:
CMAP_HEATMAP = "plasma"    # morado→azul→naranja→amarillo — más cercano al SVG
# Alternativa manual si se quiere exactamente el gradiente del SVG:
from matplotlib.colors import LinearSegmentedColormap
CMAP_CUSTOM = LinearSegmentedColormap.from_list("thermal_panel", [
    "#042C53", "#1D9E75", "#EF9F27", "#D85A30", "#993556"
])
```

---

## 3. TIPOGRAFÍA EN TKINTER

Fuentes disponibles sin instalación en Windows/Linux/macOS:

```python
# Definir al inicio de Aplicacion.__init__():

FONT_LABEL     = ("Segoe UI", 9)              # Labels, descripciones
FONT_LABEL_SM  = ("Segoe UI", 8)              # Labels secundarios, hints
FONT_SECTION   = ("Segoe UI", 8, "bold")      # Títulos de sección (uppercase)
FONT_BUTTON    = ("Segoe UI", 10, "bold")     # Texto de botón primario
FONT_BTN_SM    = ("Segoe UI", 9)              # Texto de botones secundarios
FONT_MONO      = ("Courier New", 10)          # Valores numéricos, entries
FONT_MONO_LG   = ("Courier New", 14, "bold")  # Métricas grandes (iters, error)
FONT_TITLE     = ("Segoe UI", 11, "bold")     # Título en el header
FONT_SUBTITLE  = ("Segoe UI", 8)              # Subtítulo en header
FONT_CAPTION   = ("Courier New", 8)           # Status bar, captions

# Fallback Linux (si Segoe UI no está disponible):
# "DejaVu Sans" o "Liberation Sans" en lugar de "Segoe UI"
# "DejaVu Sans Mono" en lugar de "Courier New"
```

### Jerarquía
```
TÍTULO SECCIÓN   → FONT_SECTION,  TEXT_SECTION (#BA7517),  texto.upper() + letter-spacing visual
valor métrica    → FONT_MONO_LG,  TEXT_PRIMARY (#2C2C2A),  alineado derecha
label métrica    → FONT_CAPTION,  TEXT_SECONDARY (#888780)
botón primario   → FONT_BUTTON,   TEXT_HEADER (#FAF8F4) sobre ACCENT_BTN (#2C2C2A)
botón secundario → FONT_BTN_SM,   TEXT_SECONDARY sobre BG_CARD
entry            → FONT_MONO,     TEXT_MONO sobre BG_INPUT
status bar       → FONT_CAPTION,  TEXT_CAPTION sobre BG_STATUSBAR
header título    → FONT_TITLE,    TEXT_HEADER sobre BG_HEADER
header subtítulo → FONT_SUBTITLE, TEXT_SECONDARY sobre BG_HEADER
```

---

## 4. LAYOUT — ESTRUCTURA DE LA VENTANA

### Dimensiones
```
Ventana mínima:  1100 × 680 px
Ventana default: 1280 × 780 px
Ventana.minsize(1100, 680)
Redimensionable: Sí — columna central crece (weight=1), laterales fijas
```

### Grid principal (usando grid() en la ventana raíz)
```
┌──────────────────────────────────────────────────────────────────────┐
│  HEADER  40px — BG_HEADER (#2C2C2A) — franja 4px ACCENT izquierda   │
├──────────────┬───────────────────────────────────┬───────────────────┤
│              │                                   │                   │
│  PANEL       │   ÁREA CENTRAL                    │   PANEL           │
│  IZQUIERDO   │   (column weight=1, crece)        │   DERECHO         │
│              │                                   │                   │
│  260px fijo  │                                   │   200px fijo      │
│  BG_PANEL    │   BG_WINDOW                       │   BG_PANEL        │
│  #F4F2EC     │   #FAFAF8                         │   #F4F2EC         │
│              │                                   │                   │
├──────────────┴───────────────────────────────────┴───────────────────┤
│  STATUS BAR  24px — BG_STATUSBAR (#2C2C2A)                           │
└──────────────────────────────────────────────────────────────────────┘
```

### Área central (PanedWindow vertical o grid con rowconfigure)
```
┌─────────────────────────────────────────────────┐
│  FILA SUPERIOR — 58% de altura                  │
│  ┌──────────────────┬──────────────────────────┐│
│  │ Imagen en grises │  Mapa de calor           ││
│  │ (matplotlib)     │  (matplotlib + colorbar) ││
│  │ cmap="gray"      │  cmap=CMAP_CUSTOM        ││
│  └──────────────────┴──────────────────────────┘│
│  Título flotante:                               │
│  "IMAGEN CARGADA (escala de grises)"  izquierda │
│  "MAPA DE CALOR — T(°C) · SOR · ω=X" derecha   │
│  font=FONT_CAPTION, fg=TEXT_SECONDARY           │
├─────────────────────────────────────────────────┤
│  FILA INFERIOR — 42% de altura                  │
│  Gráfica convergencia — ancho completo          │
│  Título: "CONVERGENCIA SOR — ERROR VS ITERS"    │
│  font=FONT_CAPTION, fg=TEXT_SECONDARY           │
└─────────────────────────────────────────────────┘
```

---

## 5. COMPONENTES — ESPECIFICACIÓN EXACTA

### 5.1 Header
```python
# Frame(root, height=40, bg=BG_HEADER) — pack(fill=X)
# Dentro, dos sub-frames: izquierdo (título) y derecho (info)

# Franja ámbar izquierda:
franja = Frame(header, width=4, bg=ACCENT)   # "#EF9F27"
franja.pack(side=LEFT, fill=Y)

# Título (pack left, padx=16):
Label(header, text="SIMULACIÓN TÉRMICA · PANEL SOLAR FOTOVOLTAICO",
      font=FONT_TITLE, fg=TEXT_HEADER, bg=BG_HEADER)

# Info derecha (pack right, padx=16):
Label(header, text="Universidad de Pamplona",
      font=FONT_SUBTITLE, fg=TEXT_SECONDARY, bg=BG_HEADER)
Label(header, text="Métodos Numéricos · 2025",
      font=FONT_SUBTITLE, fg=TEXT_SECONDARY, bg=BG_HEADER)

# Ícono solar (opcional, pack right):
Label(header, text="☀", font=("Courier New", 14),
      fg=ACCENT, bg=BG_HEADER, padx=12)
```

### 5.2 Panel izquierdo — Controles (260px)
```python
# Frame(root, width=260, bg=BG_PANEL) con borde derecho:
# Simular borde: Frame(root, width=1, bg=BORDER) entre panel y central

# Padding global del panel: padx=16 en cada widget

# ── SECCIÓN 01 / IMAGEN DEL PANEL ──────────────────────────
# Label sección (patrón para TODOS los títulos de sección):
Label(panel_izq, text="01 / IMAGEN DEL PANEL",
      font=FONT_SECTION, fg=TEXT_SECTION,    # #BA7517
      bg=BG_PANEL, anchor=W)
# pady=(12, 6) arriba, (0, 4) abajo

# Dropzone / preview:
Canvas(panel_izq, width=228, height=72,
       bg=BG_DROPZONE,              # #FAEEDA
       highlightthickness=1,
       highlightbackground=BORDER)  # #D3D1C7
# Dibujar borde punteado dentro del canvas:
canvas.create_rectangle(4, 4, 224, 68,
    dash=(4, 3), outline=ACCENT_DARK, width=1)  # #BA7517
# Texto centrado:
canvas.create_text(114, 30,
    text="Cargar imagen del panel",
    font=FONT_LABEL, fill=ACCENT_DARK)
canvas.create_text(114, 48,
    text="JPG · PNG · BMP → escala de grises",
    font=FONT_CAPTION, fill=TEXT_SECONDARY)

# Botón cargar (estilo SECUNDARIO, ancho completo):
ttk.Button(panel_izq, text="↑  Cargar imagen",
           style="Secondary.TButton")
# pack(fill=X, pady=(6, 0))

# Separador:
Frame(panel_izq, height=1, bg=BORDER).pack(fill=X, pady=12)

# ── SECCIÓN 02 / PARÁMETROS ─────────────────────────────────
# Patrón de campo (repetir para cada parámetro):
#   Label(panel_izq, text="Tamaño de malla N×N",
#         font=FONT_LABEL_SM, fg=TEXT_SECONDARY, bg=BG_PANEL, anchor=W)
#   Entry(panel_izq, font=FONT_MONO, bg=BG_INPUT, fg=TEXT_MONO,
#         relief="flat", bd=0,
#         insertbackground=ACCENT_DARK,
#         highlightthickness=1,
#         highlightbackground=BORDER,
#         highlightcolor=BORDER_FOCUS)  # #BA7517 al hacer foco

# Campos en orden:
#   "Tamaño de malla N×N"     default: "30"
#   "Tolerancia ε"            default: "1e-6"
#   "Máx. iteraciones"        default: "5000"
#   "Factor ω  ∈ (0, 2)"     default: "1.81"   ← incluye slider debajo
#   "Parámetro λ"             default: "1.0"
#   "T_min (°C)"              default: "25"
#   "T_max (°C)"              default: "75"

# Slider para ω (debajo del entry, misma fila ancho):
ttk.Scale(panel_izq, from_=0.01, to=1.99,
          orient=HORIZONTAL, style="Thermal.TScale")
# Sincronizar con entry_omega (ver sección 9)

# Nota ámbar (para ω):
Frame fondo ACCENT_SUBTLE → Label dentro:
#   "ω > 1 → sobrerrelajación (recomendado)"
#   "ω = 1 → equivale a Gauss-Seidel"
#   font=FONT_CAPTION, fg=ACCENT_DARK, bg=ACCENT_SUBTLE

# Separador:
Frame(panel_izq, height=1, bg=BORDER).pack(fill=X, pady=12)

# ── SECCIÓN 03 / MÉTODO ─────────────────────────────────────
# Badge SOR (Frame con borde simulado):
badge_frame = Frame(panel_izq, bg=ACCENT_SUBTLE,  # #FAEEDA
                    highlightthickness=1,
                    highlightbackground=BORDER)
# Dentro del badge:
Frame(badge_frame, width=3, bg=ACCENT_DARK).pack(side=LEFT, fill=Y)  # franja izq
Label(badge_frame, text="SOR",
      font=("Courier New", 12, "bold"),
      fg=ACCENT_DARK, bg=ACCENT_SUBTLE)           # #BA7517
Label(badge_frame, text="Successive Over-Relaxation",
      font=FONT_CAPTION, fg=TEXT_SECONDARY, bg=ACCENT_SUBTLE)
# Mini badge "activo" (pack right):
Label(badge_frame, text="activo",
      font=FONT_CAPTION, fg=TEXT_HEADER,
      bg=ACCENT_DARK, padx=6, pady=2)             # fondo #BA7517

# Separador:
Frame(panel_izq, height=1, bg=BORDER).pack(fill=X, pady=12)

# ── SECCIÓN 04 / ACCIONES ───────────────────────────────────
# Botón CALCULAR (primario, ancho completo):
ttk.Button(panel_izq, text="▶  CALCULAR",
           style="Primary.TButton")
# pack(fill=X, pady=(0, 8))

# Fila Limpiar + Salir (mitad de ancho cada uno):
fila = Frame(panel_izq, bg=BG_PANEL)
ttk.Button(fila, text="Limpiar", style="Secondary.TButton")  # pack(side=LEFT, ...)
ttk.Button(fila, text="✕  Salir", style="Danger.TButton")    # pack(side=RIGHT, ...)
```

### 5.3 Área central — Matplotlib embebido
```python
# ── FILA SUPERIOR: imagen grises + mapa de calor ────────────
fig_top, (ax_gris, ax_heat) = plt.subplots(
    1, 2,
    figsize=(8, 4),
    facecolor=BG_WINDOW     # "#FAFAF8"
)
fig_top.subplots_adjust(left=0.02, right=0.88, top=0.88, bottom=0.02, wspace=0.12)

# Imagen en grises:
ax_gris.set_facecolor(BG_WINDOW)
ax_gris.set_title("IMAGEN CARGADA (escala de grises)",
    fontsize=7, color=TEXT_SECONDARY,
    fontfamily="Courier New", pad=6)
ax_gris.axis("off")

# Mapa de calor:
ax_heat.set_facecolor(BG_WINDOW)
ax_heat.set_title("MAPA DE CALOR — T(°C) · SOR · ω=1.81",
    fontsize=7, color=TEXT_SECONDARY,
    fontfamily="Courier New", pad=6)
ax_heat.axis("off")
# Colorbar:
cbar = fig_top.colorbar(im_heat, ax=ax_heat, fraction=0.046, pad=0.04)
cbar.set_label("Temperatura (°C)", fontsize=7, color=TEXT_SECONDARY)
cbar.ax.tick_params(labelsize=7, colors=TEXT_SECONDARY)
cbar.outline.set_edgecolor(BORDER)

# Embedding:
canvas_top = FigureCanvasTkAgg(fig_top, master=frame_central_top)
canvas_top.get_tk_widget().pack(fill=BOTH, expand=True)

# ── FILA INFERIOR: convergencia ─────────────────────────────
fig_bot, ax_conv = plt.subplots(figsize=(8, 2.5), facecolor=BG_WINDOW)
fig_bot.subplots_adjust(left=0.08, right=0.97, top=0.82, bottom=0.2)

ax_conv.set_facecolor("#F8F6F0")          # fondo ligeramente más oscuro que window
ax_conv.set_yscale("log")
ax_conv.set_title("CONVERGENCIA SOR — ERROR VS. ITERACIONES",
    fontsize=7, color=TEXT_SECONDARY,
    fontfamily="Courier New", loc="left", pad=6)
ax_conv.set_xlabel("Iteraciones", fontsize=7, color=TEXT_SECONDARY)
ax_conv.set_ylabel("Error (norma ∞)", fontsize=7, color=TEXT_SECONDARY)
ax_conv.tick_params(colors=TEXT_SECONDARY, labelsize=7)
ax_conv.spines["top"].set_visible(False)
ax_conv.spines["right"].set_visible(False)
ax_conv.spines["bottom"].set_color(BORDER)
ax_conv.spines["left"].set_color(BORDER)
ax_conv.grid(True, color=BORDER, linestyle="--", alpha=0.5)

# Curva SOR — color ACCENT_DARK:
ax_conv.plot(historial, color=ACCENT_DARK, linewidth=2.0,
             label=f"SOR ω={omega}")
# Área bajo la curva — sombra suave:
ax_conv.fill_between(range(len(historial)), historial,
                     alpha=0.07, color=ACCENT_DARK)
# Marcadores cada N iteraciones:
ax_conv.plot(indices_marcadores, errores_marcadores,
             "o", color=ACCENT_DARK, markersize=4)
# Línea de tolerancia:
ax_conv.axhline(y=tolerancia, color=ERROR_TEXT, linewidth=0.8,
                linestyle="--", label=f"ε = {tolerancia:.0e}")
# Badge en el punto de convergencia:
ax_conv.annotate(f"{iters} iters.",
    xy=(iters, historial[-1]),
    xytext=(iters - 15, historial[-1] * 5),
    fontsize=7, color=TEXT_HEADER,
    fontfamily="Courier New",
    bbox=dict(boxstyle="round,pad=0.3", fc=ACCENT_DARK, ec="none"))
ax_conv.legend(fontsize=7, facecolor=BG_WINDOW,
               edgecolor=BORDER, labelcolor=TEXT_PRIMARY)

canvas_bot = FigureCanvasTkAgg(fig_bot, master=frame_central_bot)
canvas_bot.get_tk_widget().pack(fill=BOTH, expand=True)
```

### 5.4 Panel derecho — Métricas (200px)
```python
# Frame(root, width=200, bg=BG_PANEL)
# Borde izquierdo: Frame(root, width=1, bg=BORDER)

# ── SECCIÓN: RESULTADOS ─────────────────────────────────────
# 4 tarjetas apiladas (patrón):
def crear_tarjeta_metrica(parent, nombre, valor_inicial="—"):
    card = Frame(parent, bg=BG_CARD,
                 highlightthickness=1,
                 highlightbackground=BORDER)
    card.pack(fill=X, pady=(0, 6))
    Label(card, text=nombre,
          font=FONT_CAPTION, fg=TEXT_SECONDARY,
          bg=BG_CARD, anchor=W,
          padx=10, pady=(6,0)).pack(fill=X)
    lbl_val = Label(card, text=valor_inicial,
                    font=FONT_MONO_LG, fg=TEXT_PRIMARY,
                    bg=BG_CARD, anchor=E,
                    padx=10, pady=(0,6))
    lbl_val.pack(fill=X)
    return lbl_val   # retornar para actualizar después

# Crear las 4 métricas:
lbl_iters  = crear_tarjeta_metrica(panel_der, "ITERACIONES")
lbl_error  = crear_tarjeta_metrica(panel_der, "ERROR FINAL")
lbl_tiempo = crear_tarjeta_metrica(panel_der, "TIEMPO")
lbl_tmax   = crear_tarjeta_metrica(panel_der, "T. MÁXIMA")

# Cuando hay resultado, T. MÁXIMA cambia a color ACCENT_DARK:
lbl_tmax.config(fg=ACCENT_DARK)   # #BA7517 — caliente

# Badge de convergencia (Frame debajo de tarjetas):
# Estado convergió:
badge_ok = Frame(panel_der, bg=SUCCESS_BG,    # #EAF3DE
                 highlightthickness=1,
                 highlightbackground=SUCCESS)
Label(badge_ok, text="✓  Convergió",
      font=FONT_LABEL, fg=SUCCESS_TEXT,        # #3B6D11
      bg=SUCCESS_BG, padx=10, pady=6)

# Estado no convergió:
badge_err = Frame(panel_der, bg=ERROR_BG,     # #FCEBEB
                  highlightthickness=1,
                  highlightbackground=ERROR_TEXT)
Label(badge_err, text="✗  No convergió",
      font=FONT_LABEL, fg=ERROR_TEXT,          # #A32D2D
      bg=ERROR_BG, padx=10, pady=6)

# ── SEPARADOR ───────────────────────────────────────────────
Frame(panel_der, height=1, bg=BORDER).pack(fill=X, pady=12)

# ── SECCIÓN: EXPORTAR ───────────────────────────────────────
# 3 botones apilados, SECUNDARIO, ancho completo:
btn_guardar_mapa   = ttk.Button(panel_der, text="Guardar mapa de calor",
                                style="Secondary.TButton")
btn_exportar_csv   = ttk.Button(panel_der, text="Exportar datos CSV",
                                style="Secondary.TButton")
btn_guardar_graf   = ttk.Button(panel_der, text="Guardar gráfica",
                                style="Secondary.TButton")
# Estado inicial: DISABLED — habilitar tras convergencia exitosa
for btn in (btn_guardar_mapa, btn_exportar_csv, btn_guardar_graf):
    btn.config(state="disabled")
    btn.pack(fill=X, pady=(0, 6))
```

### 5.5 Status bar (24px)
```python
# Separador antes de la barra:
Frame(root, height=1, bg=BORDER).pack(fill=X, side=BOTTOM)

# Frame status:
status_bar = Frame(root, height=24, bg=BG_STATUSBAR)
status_bar.pack(fill=X, side=BOTTOM)

# Indicador circular (Canvas 18×24):
canvas_ind = Canvas(status_bar, width=18, height=24,
                    bg=BG_STATUSBAR, highlightthickness=0)
canvas_ind.pack(side=LEFT, padx=(8, 0))
# Dibujar círculo:
ind_oval = canvas_ind.create_oval(4, 7, 14, 17, fill="#555550", outline="")

# Texto de estado:
lbl_status = Label(status_bar,
    text="Listo · Cargue una imagen para comenzar",
    font=FONT_CAPTION, fg=TEXT_CAPTION, bg=BG_STATUSBAR)
lbl_status.pack(side=LEFT, padx=6)

# Función para actualizar:
def set_status(texto, color_ind="#555550"):
    canvas_ind.itemconfig(ind_oval, fill=color_ind)
    lbl_status.config(text=texto)

# Llamadas:
set_status("Listo · Cargue una imagen para comenzar", "#555550")
set_status("Imagen cargada · 640×480px · Listo para calcular", ACCENT)
set_status("Ejecutando SOR...", ACCENT)
set_status(f"Convergió · {iters} iters · ε={error:.2e} · {t:.2f}s", SUCCESS)
set_status(f"No convergió en {max_iter} iteraciones", ERROR_TEXT)
```

---

## 6. ESTILOS DE BOTONES (ttk.Style)

```python
# En Aplicacion.__init__(), antes de crear widgets:
style = ttk.Style()
style.theme_use("clam")   # OBLIGATORIO para poder skinear en todas las plataformas

# ── PRIMARIO — botón Calcular ───────────────────────────────
style.configure("Primary.TButton",
    background="#2C2C2A",      # ACCENT_BTN — casi negro (del SVG)
    foreground="#FAF8F4",      # TEXT_HEADER — blanco cálido
    font=("Segoe UI", 10, "bold"),
    relief="flat",
    borderwidth=0,
    padding=(0, 10),
    anchor=CENTER,
)
style.map("Primary.TButton",
    background=[("active",   "#444441"),    # hover — un tono más claro
                ("disabled", "#D3D1C7")],
    foreground=[("disabled", "#888780")],
)

# ── SECUNDARIO — Cargar imagen, exportar, limpiar ───────────
style.configure("Secondary.TButton",
    background="#F4F2EC",      # BG_PANEL
    foreground="#888780",      # TEXT_SECONDARY
    font=("Segoe UI", 9),
    relief="flat",
    borderwidth=1,
    padding=(0, 8),
)
style.map("Secondary.TButton",
    background=[("active",   "#E8E6E0"),    # hover — más oscuro que panel
                ("disabled", "#F4F2EC")],
    foreground=[("disabled", "#C8C6C0")],
)

# ── PELIGRO — botón Salir ───────────────────────────────────
style.configure("Danger.TButton",
    background="#F4F2EC",      # BG_PANEL (mismo fondo que panel)
    foreground="#A32D2D",      # ERROR_TEXT — rojo
    font=("Segoe UI", 9),
    relief="flat",
    borderwidth=1,
    padding=(0, 8),
)
style.map("Danger.TButton",
    background=[("active", "#FCEBEB")],     # hover — fondo rojizo suave
)

# ── SLIDER ─────────────────────────────────────────────────
style.configure("Thermal.Horizontal.TScale",
    background="#F4F2EC",      # BG_PANEL
    troughcolor="#D3D1C7",     # BORDER — riel gris
    sliderthickness=14,
    sliderrelief="flat",
)
```

---

## 7. MATPLOTLIB — CONFIGURACIÓN GLOBAL

```python
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    # Fondos — claro, consistente con la UI
    "figure.facecolor":      "#FAFAF8",    # BG_WINDOW
    "axes.facecolor":        "#F8F6F0",    # ligeramente más oscuro

    # Texto
    "text.color":            "#2C2C2A",    # TEXT_PRIMARY
    "axes.labelcolor":       "#888780",    # TEXT_SECONDARY
    "xtick.color":           "#888780",
    "ytick.color":           "#888780",
    "axes.titlecolor":       "#888780",

    # Grilla
    "grid.color":            "#D3D1C7",    # BORDER
    "grid.linestyle":        "--",
    "grid.alpha":            0.5,

    # Spines
    "axes.spines.top":       False,
    "axes.spines.right":     False,
    "axes.edgecolor":        "#D3D1C7",    # BORDER

    # Tipografía
    "font.family":           "monospace",
    "font.size":             8,
    "axes.titlesize":        8,
    "axes.labelsize":        8,

    # Leyenda
    "legend.facecolor":      "#FAFAF8",
    "legend.edgecolor":      "#D3D1C7",
    "legend.fontsize":       7,
})
```

---

## 8. ESPACIADO — REGLAS FIJAS

```
Padding externo panel lateral:        padx=16
Padding vertical entre secciones:     pady=12 (separador) + pady=(12,6) en título
Padding label → entry:                pady=(0, 4)
Padding entre campos consecutivos:    pady=(8, 0)
Padding interno tarjeta métrica:      padx=10, pady=6
Ancho separador horizontal:           height=1, bg=BORDER
Padding botón primario:               pady=10 vertical, fill=X
Padding botones secundarios:          pady=(0,6) vertical, fill=X
Padding fila Limpiar+Salir:           entre botones: padx=4
```

---

## 9. COMPORTAMIENTO DINÁMICO

### Estados de la UI

```
ESTADO: INICIAL
  - Canvas central: placeholder con texto centrado
      text="☀  Cargue una imagen del panel para comenzar"
      font=FONT_MONO, fill=TEXT_SECONDARY (#888780)
  - Botón Calcular: state=DISABLED
  - Botones exportar: state=DISABLED
  - Badge convergencia: oculto (pack_forget)
  - Indicador status: gris (#555550)

ESTADO: IMAGEN CARGADA
  - ax_gris actualiza con la imagen en grises
  - Botón Calcular: state=NORMAL
  - Status: "Imagen cargada · {W}×{H}px · Listo para calcular", ACCENT (#EF9F27)

ESTADO: CALCULANDO
  - Botón Calcular: state=DISABLED, text="Calculando..."
  - Status: "Ejecutando SOR...", ACCENT
  - UI NO se congela → usar threading (ver sección 10)

ESTADO: CONVERGIÓ
  - ax_heat: muestra mapa de calor con CMAP_CUSTOM
  - ax_conv: muestra curva de convergencia
  - Métricas: actualizan con valores reales
  - lbl_tmax.config(fg=ACCENT_DARK)    ← temperatura máxima en ámbar
  - badge_err.pack_forget()
  - badge_ok.pack(fill=X)
  - Botones exportar: state=NORMAL
  - Status: f"Convergió · {iters} iters · ε={error:.2e} · {t:.2f}s", SUCCESS

ESTADO: NO CONVERGIÓ
  - Igual que CONVERGIÓ pero:
  - badge_ok.pack_forget()
  - badge_err.pack(fill=X)
  - Status: f"No convergió en {max_iter} iters · error={error:.2e}", ERROR_TEXT
  - Botones exportar: NORMAL (datos parciales siguen siendo exportables)

ESTADO: ERROR VALIDACIÓN
  - Entry inválido: highlightbackground=ERROR_TEXT (#A32D2D)
  - Label error rojo debajo: font=FONT_CAPTION, fg=ERROR_TEXT
  - Status: descripción del error, ERROR_TEXT
  - No se ejecuta el cálculo
  - Al corregir el campo: highlightbackground vuelve a BORDER
```

### Sincronización slider ↔ entry de ω
```python
def _on_slider_change(self, val):
    omega = round(float(val), 3)
    self.entry_omega.delete(0, "end")
    self.entry_omega.insert(0, str(omega))

def _on_omega_entry_focusout(self, event):
    try:
        val = float(self.entry_omega.get())
        val = max(0.01, min(1.99, val))    # clamp al rango válido
        self.slider_omega.set(val)
        self.entry_omega.config(highlightbackground=BORDER)
    except ValueError:
        self.entry_omega.config(highlightbackground=ERROR_TEXT)
```

---

## 10. THREADING — NO CONGELAR LA UI

```python
import threading

def _on_calcular(self):
    params = self._leer_params()
    if not self._validar_params(params):
        return                              # validación falló, no ejecutar

    self._set_estado("calculando")

    def _worker():
        resultado = self.controlador.ejecutar(params)
        # Devolver al hilo principal con after():
        self.after(0, lambda: self._mostrar_resultado(resultado))

    threading.Thread(target=_worker, daemon=True).start()

def _mostrar_resultado(self, resultado):
    """Siempre se ejecuta en el hilo principal de tkinter."""
    self._actualizar_figuras(resultado)
    self._actualizar_metricas(resultado)
    if resultado.convergio:
        self._set_estado("convergido")
    else:
        self._set_estado("no_convergido")
```

---

## 11. CHECKLIST ANTES DE ENTREGAR

- [ ] `root.configure(bg=BG_WINDOW)` — sin fondo gris tkinter default
- [ ] Todos los `Label` tienen `bg=` configurado (sin gris tkinter)
- [ ] Todos los `Frame` separadores tienen `bg=BORDER` y `height=1`
- [ ] Todos los `Entry` tienen `relief="flat"`, `highlightthickness=1`
- [ ] Botón Calcular usa `Primary.TButton` (fondo #2C2C2A, texto blanco)
- [ ] `style.theme_use("clam")` antes de configurar estilos
- [ ] `matplotlib.use("TkAgg")` antes de importar pyplot
- [ ] `plt.rcParams.update(...)` con fondo `#FAFAF8` (no blanco puro)
- [ ] Mapa de calor usa `CMAP_CUSTOM` (gradiente del SVG) o `"plasma"`
- [ ] Colorbar muestra escala 25–75 °C con etiqueta "Temperatura (°C)"
- [ ] Eje Y de convergencia en escala logarítmica (`set_yscale("log")`)
- [ ] Curva SOR en color `#BA7517` (ACCENT_DARK), linewidth=2
- [ ] Línea de tolerancia en rojo punteado con label `ε = {valor}`
- [ ] Slider ω sincronizado con Entry, clampeado a (0.01, 1.99)
- [ ] Botones exportar deshabilitados antes del primer cálculo
- [ ] Status bar actualiza color del indicador según estado
- [ ] Cálculo SOR en hilo separado con `threading.Thread`
- [ ] `root.minsize(1100, 680)`
- [ ] Franja ámbar de 4px en borde izquierdo del header
