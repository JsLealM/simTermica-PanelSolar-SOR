import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from controlador import Controlador, ResultadoSOR
from energia import PANELES

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Simulación Térmica - Panel Solar")
        self.geometry("1600x950")
        self.minsize(1400, 850)
        
        # Colors from DESIGN.md
        self.BG_WINDOW = "#FAFAF8"
        self.ACCENT = "#EF9F27"
        self.TEXT_SECTION = "#BA7517"
        self.TEXT_BODY = "#464641"
        self.BG_SIDEBAR = "#F3F1ED"
        self.BORDER_LIGHT = "#E8E6E0"
        self.BORDER_DARK = "#8B8680"
        self.FRANJA_COLOR = "#EF9F27"
        
        self.configure(bg=self.BG_WINDOW)
        self.resizable(True, True)
        
        self.controlador = Controlador()
        self.imagen_cargada = False
        self.calculando = False
        self.ultimo_resultado = None
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        # Frame principal con franja ámbar izquierda
        main_frame = tk.Frame(self, bg=self.BG_WINDOW)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Franja ámbar (4px left)
        franja = tk.Frame(main_frame, bg=self.FRANJA_COLOR, width=4)
        franja.pack(side=tk.LEFT, fill=tk.Y)
        
        # Contenedor principal
        container = tk.Frame(main_frame, bg=self.BG_WINDOW)
        container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=16)
        
        # HEADER
        self.crear_header(container)
        
        # Body (3 paneles)
        body_frame = tk.Frame(container, bg=self.BG_WINDOW)
        body_frame.pack(fill=tk.BOTH, expand=True, pady=(16, 0))
        
        # Panel izquierdo (260px)
        self.panel_izquierdo = self.crear_panel_izquierdo(body_frame)
        self.panel_izquierdo.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 16))
        
        # Panel derecho (200px)
        self.panel_derecho = self.crear_panel_derecho(body_frame)
        self.panel_derecho.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        # Panel central (matplotlib). Se empaca de último para ocupar solo el espacio disponible.
        self.panel_central = self.crear_panel_central(body_frame)
        self.panel_central.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 16))
        
        # STATUS BAR (24px height)
        self.crear_status_bar(container)
    
    def crear_header(self, parent):
        header = tk.Frame(parent, bg=self.BG_WINDOW, height=40)
        header.pack(fill=tk.X, pady=(0, 16))
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text="Simulación Térmica - Panel Solar",
            font=("Poppins", 16, "bold"),
            fg=self.TEXT_SECTION,
            bg=self.BG_WINDOW
        )
        title_label.pack(side=tk.LEFT, anchor="w")
        
        uni_label = tk.Label(
            header,
            text="Universidad de Pamplona",
            font=("Segoe UI", 9),
            fg=self.TEXT_BODY,
            bg=self.BG_WINDOW
        )
        uni_label.pack(side=tk.RIGHT, anchor="e")
    
    def crear_panel_izquierdo(self, parent):
        panel = tk.Frame(parent, bg=self.BG_SIDEBAR, width=260)
        panel.pack_propagate(False)

        acciones = tk.Frame(panel, bg=self.BG_SIDEBAR)
        acciones.pack(side=tk.BOTTOM, fill=tk.X, padx=12, pady=(8, 12))

        canvas = tk.Canvas(panel, bg=self.BG_SIDEBAR, highlightthickness=0)
        scrollbar = tk.Scrollbar(panel, orient=tk.VERTICAL, command=canvas.yview)
        contenido = tk.Frame(canvas, bg=self.BG_SIDEBAR)

        contenido.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=contenido, anchor="nw", width=242)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _scroll_mouse(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _scroll_mouse))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Dropzone
        self.dropzone = tk.Frame(contenido, bg=self.BORDER_LIGHT, relief=tk.RIDGE, borderwidth=2)
        self.dropzone.pack(fill=tk.X, padx=12, pady=(12, 16))
        
        dropzone_label = tk.Label(
            self.dropzone,
            text="Cargar imagen\n(PNG/JPG grayscale)",
            font=("Segoe UI", 9),
            fg=self.TEXT_BODY,
            bg=self.BORDER_LIGHT,
            justify=tk.CENTER,
            pady=20
        )
        dropzone_label.pack(fill=tk.BOTH, expand=True)
        self.dropzone.bind("<Button-1>", lambda e: self.cargar_imagen())
        dropzone_label.bind("<Button-1>", lambda e: self.cargar_imagen())
        
        # Label para mostrar N detectada
        frame_N = tk.Frame(contenido, bg=self.BG_SIDEBAR)
        frame_N.pack(fill=tk.X, padx=12, pady=(0, 8))
        tk.Label(frame_N, text="Tamaño malla (N)", font=("Segoe UI", 8), fg=self.TEXT_SECTION, bg=self.BG_SIDEBAR).pack(anchor="w")
        self.label_N_value = tk.Label(frame_N, text="(cargue imagen)", font=("Segoe UI", 10, "bold"), fg=self.ACCENT, bg=self.BG_SIDEBAR)
        self.label_N_value.pack(anchor="w", pady=(4, 0))
        
        # Input fields
        self.crear_campo_entrada(contenido, "Tolerancia (e)", "tolerancia", 1e-4, 1e-8, 1e-1)
        self.crear_campo_entrada(contenido, "Máx iteraciones", "max_iter", 200, 20, 10000)
        
        self.crear_omega_auto_label(contenido)
        
        # Lambda field
        self.crear_campo_entrada(contenido, "Lambda (l)", "lambda", 1.0, 0.1, 5.0)
        self.crear_campo_entrada(contenido, "T mín (°C)", "T_min", 20, 0, 100)
        self.crear_campo_entrada(contenido, "T máx (°C)", "T_max", 100, 25, 200)
        self.crear_selector_panel(contenido)
        self.crear_campo_entrada(contenido, "Potencia nominal Pdc0 (W)", "pdc0", 450, 1, 2000)
        self.crear_campo_entrada(contenido, "Irradiancia G (W/m²)", "irradiancia", 1000, 0, 1400)
        
        # Badge SOR
        badge_frame = tk.Frame(contenido, bg=self.ACCENT)
        badge_frame.pack(fill=tk.X, padx=12, pady=12)
        tk.Label(badge_frame, text="Método SOR", font=("Segoe UI", 9, "bold"),
                fg="white", bg=self.ACCENT).pack(pady=4)
        
        self.btn_calcular = tk.Button(
            acciones,
            text="Calcular",
            font=("Segoe UI", 10, "bold"),
            bg=self.ACCENT,
            fg="white",
            relief=tk.FLAT,
            command=self.ejecutar_calculo,
            state=tk.DISABLED
        )
        self.btn_calcular.pack(fill=tk.X, pady=4)
        
        self.btn_limpiar = tk.Button(
            acciones,
            text="Limpiar",
            font=("Segoe UI", 10),
            bg=self.BORDER_LIGHT,
            fg=self.TEXT_BODY,
            relief=tk.FLAT,
            command=self.limpiar
        )
        self.btn_limpiar.pack(fill=tk.X, pady=4)
        
        self.btn_salir = tk.Button(
            acciones,
            text="Salir",
            font=("Segoe UI", 10),
            bg=self.BORDER_LIGHT,
            fg=self.TEXT_BODY,
            relief=tk.FLAT,
            command=self.quit
        )
        self.btn_salir.pack(fill=tk.X)
        
        return panel
    
    def crear_campo_entrada(self, parent, label, key, default, min_val, max_val):
        frame = tk.Frame(parent, bg=self.BG_SIDEBAR)
        frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        tk.Label(frame, text=label, font=("Segoe UI", 8), fg=self.TEXT_SECTION, bg=self.BG_SIDEBAR).pack(anchor="w")
        
        var = tk.StringVar(value=str(default))
        entry = tk.Entry(frame, textvariable=var, font=("Segoe UI", 10), width=20)
        entry.pack(fill=tk.X, pady=(4, 0))
        
        setattr(self, f"var_{key}", var)
    
    def crear_omega_auto_label(self, parent):
        frame = tk.Frame(parent, bg=self.BG_SIDEBAR)
        frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        tk.Label(frame, text="Omega (w) - automático", font=("Segoe UI", 8), fg=self.TEXT_SECTION, bg=self.BG_SIDEBAR).pack(anchor="w")
        self.label_omega_auto = tk.Label(frame, text="Se calcula al ejecutar", font=("Segoe UI", 9, "bold"), fg=self.ACCENT, bg=self.BG_SIDEBAR)
        self.label_omega_auto.pack(anchor="w", pady=(4, 0))

    def crear_selector_panel(self, parent):
        frame = tk.Frame(parent, bg=self.BG_SIDEBAR)
        frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        tk.Label(frame, text="Tipo de panel", font=("Segoe UI", 8), fg=self.TEXT_SECTION, bg=self.BG_SIDEBAR).pack(anchor="w")
        opciones = list(PANELES.keys()) + ["Personalizado"]
        self.var_tipo_panel = tk.StringVar(value="Monocristalino")
        selector = tk.OptionMenu(frame, self.var_tipo_panel, *opciones)
        selector.config(font=("Segoe UI", 9), bg=self.BORDER_LIGHT, fg=self.TEXT_BODY, relief=tk.FLAT)
        selector.pack(fill=tk.X, pady=(4, 0))
    
    def crear_panel_central(self, parent):
        panel = tk.Frame(parent, bg=self.BG_WINDOW)

        barra_nav = tk.Frame(panel, bg=self.BG_SIDEBAR, height=48)
        barra_nav.pack(fill=tk.X, side=tk.TOP)
        barra_nav.pack_propagate(False)

        self.modo_resultado = "gris"
        tk.Button(
            barra_nav,
            text="← Imagen gris",
            font=("Segoe UI", 10, "bold"),
            bg=self.BORDER_LIGHT,
            fg=self.TEXT_BODY,
            relief=tk.FLAT,
            command=lambda: self._cambiar_modo_resultado("gris")
        ).pack(side=tk.LEFT, padx=10, pady=8)

        self.label_modo_resultado = tk.Label(
            barra_nav,
            text="Cargue una imagen y calcule para ver resultados",
            font=("Segoe UI", 11, "bold"),
            fg=self.TEXT_SECTION,
            bg=self.BG_SIDEBAR
        )
        self.label_modo_resultado.pack(side=tk.LEFT, expand=True)

        tk.Button(
            barra_nav,
            text="Mapa de calor →",
            font=("Segoe UI", 10, "bold"),
            bg=self.ACCENT,
            fg="white",
            relief=tk.FLAT,
            command=lambda: self._cambiar_modo_resultado("calor")
        ).pack(side=tk.RIGHT, padx=10, pady=8)

        self.frame_figura_resultado = tk.Frame(panel, bg=self.BG_WINDOW)
        self.frame_figura_resultado.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.label_placeholder_central = tk.Label(
            self.frame_figura_resultado,
            text="Cargue una imagen para comenzar",
            font=("Segoe UI", 14, "bold"),
            fg=self.TEXT_BODY,
            bg=self.BG_WINDOW
        )
        self.label_placeholder_central.pack(expand=True)

        barra_info = tk.Frame(panel, bg=self.BORDER_LIGHT, height=34)
        barra_info.pack(fill=tk.X, side=tk.BOTTOM)
        barra_info.pack_propagate(False)
        self.label_pixel_resultado = tk.Label(
            barra_info,
            text="En el mapa de calor se mostrará fila, columna, temperatura y potencia del píxel",
            font=("Segoe UI", 10),
            fg=self.TEXT_BODY,
            bg=self.BORDER_LIGHT,
            anchor="w"
        )
        self.label_pixel_resultado.pack(fill=tk.X, padx=12)

        self.canvas_matplotlib = None
        self.fig = None
        self.canvas_resultados = None
        
        return panel
    
    def crear_panel_derecho(self, parent):
        panel = tk.Frame(parent, bg=self.BG_SIDEBAR, width=200)
        panel.pack_propagate(False)
        
        # Metric cards
        self.crear_metric_card(panel, "Iteraciones", "iter", "0")
        self.crear_metric_card(panel, "Error final", "error", "0")
        self.crear_metric_card(panel, "Tiempo (s)", "tiempo", "0")
        self.crear_metric_card(panel, "T máx (°C)", "Tmax", "0")
        self.crear_metric_card(panel, "T media (°C)", "Tmedia", "0")
        self.crear_metric_card(panel, "Potencia total (W)", "Ptotal", "0")
        self.crear_metric_card(panel, "P pixel (W)", "Ppixel", "0")
        self.crear_metric_card(panel, "Omega usado", "Omega", "0")
        
        # Badge convergencia
        self.badge_convergencia = tk.Frame(panel, bg=self.BORDER_LIGHT)
        self.badge_convergencia.pack(fill=tk.X, padx=12, pady=(12, 8))
        self.badge_convergencia_label = tk.Label(
            self.badge_convergencia,
            text="Pendiente",
            font=("Segoe UI", 9),
            fg=self.TEXT_BODY,
            bg=self.BORDER_LIGHT,
            pady=8
        )
        self.badge_convergencia_label.pack(fill=tk.X)
        
        # Export buttons
        btn_frame = tk.Frame(panel, bg=self.BG_SIDEBAR)
        btn_frame.pack(fill=tk.X, padx=12, pady=12)
        
        self.btn_exportar_csv = tk.Button(btn_frame, text="CSV", font=("Segoe UI", 9), bg=self.ACCENT, fg="white",
                 relief=tk.FLAT, command=self.exportar_csv, state=tk.DISABLED)
        self.btn_exportar_csv.pack(fill=tk.X, pady=2)

        self.btn_exportar_mapa = tk.Button(btn_frame, text="Mapa Calor", font=("Segoe UI", 9), bg=self.ACCENT, fg="white",
                 relief=tk.FLAT, command=self.exportar_mapa, state=tk.DISABLED)
        self.btn_exportar_mapa.pack(fill=tk.X, pady=2)

        self.btn_exportar_grafica = tk.Button(btn_frame, text="Gráfica", font=("Segoe UI", 9), bg=self.ACCENT, fg="white",
                 relief=tk.FLAT, command=self.exportar_grafica, state=tk.DISABLED)
        self.btn_exportar_grafica.pack(fill=tk.X, pady=2)

        self.btn_exportar_pixeles = tk.Button(btn_frame, text="CSV píxeles", font=("Segoe UI", 9), bg=self.ACCENT, fg="white",
                 relief=tk.FLAT, command=self.exportar_pixeles, state=tk.DISABLED)
        self.btn_exportar_pixeles.pack(fill=tk.X)
        
        return panel
    
    def crear_metric_card(self, parent, title, key, value):
        frame = tk.Frame(parent, bg=self.BORDER_LIGHT)
        frame.pack(fill=tk.X, padx=12, pady=4)
        
        tk.Label(frame, text=title, font=("Segoe UI", 8), fg=self.TEXT_SECTION, bg=self.BORDER_LIGHT).pack(anchor="w", padx=8, pady=(4, 0))
        value_label = tk.Label(frame, text=value, font=("Poppins", 14, "bold"), fg=self.ACCENT, bg=self.BORDER_LIGHT)
        value_label.pack(anchor="w", padx=8, pady=(0, 4))
        
        setattr(self, f"label_{key}", value_label)
    
    def crear_status_bar(self, parent):
        status_frame = tk.Frame(parent, bg=self.BORDER_LIGHT, height=24)
        status_frame.pack(fill=tk.X, pady=(16, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Listo", font=("Segoe UI", 9), fg=self.TEXT_BODY, bg=self.BORDER_LIGHT)
        self.status_label.pack(side=tk.LEFT, padx=12)
        
        self.status_indicator = tk.Label(status_frame, text="o", font=("Segoe UI", 12), fg="#4CAF50", bg=self.BORDER_LIGHT)
        self.status_indicator.pack(side=tk.RIGHT, padx=12)
    
    def cargar_imagen(self):
        archivo = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if archivo:
            try:
                img, N_detectada = self.controlador.cargar_imagen(archivo)
                self.imagen_cargada = True
                self.btn_calcular.config(state=tk.NORMAL)
                self.dropzone.config(bg=self.ACCENT)
                alto, ancho = N_detectada
                self.label_N_value.config(text=f"{alto}x{ancho} píxeles")
                self.status_label.config(text=f"Imagen cargada: {archivo.split(chr(92))[-1]}")
                self.status_indicator.config(fg="#4CAF50")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
    
    def ejecutar_calculo(self):
        if self.calculando:
            return
        
        try:
            # Usar N detectada del controlador
            if not self.controlador.N_detectada:
                messagebox.showerror("Error", "Debe cargar una imagen primero")
                return
                
            N = self.controlador.N_detectada
            tol = float(self.var_tolerancia.get())
            max_iter = int(self.var_max_iter.get())
            omega = None
            lam = float(self.var_lambda.get())
            T_min = float(self.var_T_min.get())
            T_max = float(self.var_T_max.get())
            pdc0 = float(self.var_pdc0.get())
            irradiancia = float(self.var_irradiancia.get())
            tipo_panel = self.var_tipo_panel.get()
            filas, columnas = N
            total_pixeles = filas * columnas
            if total_pixeles >= 1_000_000 and max_iter > 200:
                max_iter = 200
                self.var_max_iter.set("200")
                self.status_label.config(text="Imagen grande: máx. iteraciones ajustado a 200")
            
            self.calculando = True
            self.status_label.config(text=f"Calculando {N[0]}x{N[1]} con SOR...")
            self.status_indicator.config(fg="#FFC107")
            
            error_msg = self._validar_parametros(N, tol, max_iter, omega, lam, T_min, T_max, pdc0, irradiancia)
            if error_msg:
                messagebox.showerror("Error de validación", error_msg)
                self.calculando = False
                self.status_label.config(text="Listo")
                self.status_indicator.config(fg="#4CAF50")
                return
            
            thread = threading.Thread(
                target=self.worker_calculo,
                args=(N, tol, max_iter, omega, lam, T_min, T_max, pdc0, irradiancia, tipo_panel),
                daemon=True
            )
            thread.start()
        except ValueError as e:
            messagebox.showerror("Error", "Verifique los valores de entrada")
            self.calculando = False
            self.status_label.config(text="Listo")
            self.status_indicator.config(fg="#4CAF50")
    
    def _validar_parametros(self, N, tol, max_iter, omega, lam, T_min, T_max, pdc0, irradiancia):
        filas, columnas = N if isinstance(N, tuple) else (N, N)
        if filas < 5 or columnas < 5:
            return "La imagen debe ser al menos 5x5"
        if tol <= 0:
            return "Tolerancia debe ser > 0"
        if max_iter <= 0:
            return "Máx iteraciones debe ser > 0"
        if omega is not None and (omega <= 0 or omega >= 2):
            return "Omega debe estar en el rango (0, 2)"
        if lam == 0:
            return "Lambda no puede ser 0"
        if T_min >= T_max:
            return "T_min debe ser menor que T_max"
        if pdc0 <= 0:
            return "Pdc0 debe ser > 0"
        if irradiancia < 0:
            return "Irradiancia debe ser >= 0"
        return None
    
    def worker_calculo(self, N, tol, max_iter, omega, lam, T_min, T_max, pdc0, irradiancia, tipo_panel):
        error_exception = None
        resultado = None
        try:
            params = {
                "N": N,
                "tolerancia": tol,
                "max_iter": max_iter,
                "omega": omega,
                "lambda_val": lam,
                "T_min": T_min,
                "T_max": T_max,
                "pdc0": pdc0,
                "irradiancia": irradiancia,
                "tipo_panel": tipo_panel
            }
            resultado = self.controlador.ejecutar(params)
        except Exception as e:
            error_exception = str(e)
        finally:
            self.calculando = False
            if error_exception:
                self.after(0, lambda msg=error_exception: messagebox.showerror("Error", f"Error en cálculo: {msg}"))
                self.after(0, self.resetar_estado)
            else:
                self.after(0, lambda res=resultado: self.mostrar_resultado(res))
    
    def resetar_estado(self):
        self.status_label.config(text="Listo")
        self.status_indicator.config(fg="#4CAF50")
    
    def mostrar_resultado(self, resultado):
        if resultado is None:
            return
        
        self.ultimo_resultado = resultado
        self.label_iter.config(text=str(resultado.iteraciones))
        self.label_error.config(text=f"{resultado.error_final:.2e}")
        self.label_tiempo.config(text=f"{resultado.tiempo_seg:.3f}")
        self.label_Tmax.config(text=f"{resultado.T_max_calculada:.2f}")
        self.label_Tmedia.config(text=f"{resultado.T_media_calculada:.2f}")
        self.label_Ptotal.config(text=f"{resultado.potencia_total:.2f}")
        self.label_Ppixel.config(text="Seleccione")
        self.label_Omega.config(text=f"{resultado.omega_usado:.4f}")
        self.label_omega_auto.config(text=f"{resultado.omega_usado:.4f}")
        
        if resultado.convergio:
            self.badge_convergencia.config(bg="#4CAF50")
            self.badge_convergencia_label.config(text="Convergencia OK", fg="white", bg="#4CAF50")
            self.status_label.config(text="Cálculo completado")
            self.status_indicator.config(fg="#4CAF50")
        else:
            self.badge_convergencia.config(bg="#F44336")
            self.badge_convergencia_label.config(text="No convergió", fg="white", bg="#F44336")
            self.status_label.config(text="Cálculo completado (no convergió)")
            self.status_indicator.config(fg="#F44336")

        self.btn_exportar_csv.config(state=tk.NORMAL)
        self.btn_exportar_mapa.config(state=tk.NORMAL)
        self.btn_exportar_grafica.config(state=tk.NORMAL)
        self.btn_exportar_pixeles.config(state=tk.NORMAL)
        
        self.mostrar_graficas()
    
    def mostrar_graficas(self):
        if self.ultimo_resultado is None:
            return

        self.modo_resultado = "gris"
        self._renderizar_resultado_en_panel()

    def _renderizar_resultado_en_panel(self):
        if self.ultimo_resultado is None:
            return

        from servicios import generar_figura_individual
        try:
            escala_T_min = float(self.var_T_min.get())
            escala_T_max = float(self.var_T_max.get())
        except ValueError:
            escala_T_min = self.ultimo_resultado.T_min_calculada
            escala_T_max = self.ultimo_resultado.T_max_calculada

        if self.canvas_resultados:
            self.canvas_resultados.get_tk_widget().destroy()
            self.canvas_resultados = None
        if hasattr(self, "label_placeholder_central") and self.label_placeholder_central.winfo_exists():
            self.label_placeholder_central.destroy()

        self.label_modo_resultado.config(
            text="Imagen en escala de grises" if self.modo_resultado == "gris" else "Mapa de calor - temperatura calculada"
        )

        self.fig = generar_figura_individual(
            imagen_grises=self.controlador.imagen_grises,
            malla_resultado=self.ultimo_resultado.malla_resultado,
            modo=self.modo_resultado,
            T_min=escala_T_min,
            T_max=escala_T_max
        )
        
        self.canvas_resultados = FigureCanvasTkAgg(self.fig, master=self.frame_figura_resultado)
        self.canvas_resultados.draw()
        self.canvas_resultados.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ax_heatmap = self.fig.axes[0] if self.modo_resultado == "calor" else None
        self.canvas_resultados.mpl_connect("motion_notify_event", self._mostrar_pixel_en_cursor)
        self.canvas_resultados.mpl_connect("button_press_event", self._mostrar_pixel_en_cursor)

        self.status_label.config(text="Resultados mostrados en el panel central")

    def _cambiar_modo_resultado(self, modo: str):
        if self.ultimo_resultado is None:
            return

        self.modo_resultado = modo
        self._renderizar_resultado_en_panel()

    def _mostrar_pixel_en_cursor(self, event):
        if self.ultimo_resultado is None or not hasattr(self, "ax_heatmap") or self.ax_heatmap is None:
            return
        if event.inaxes != self.ax_heatmap or event.xdata is None or event.ydata is None:
            return

        fila = int(round(event.ydata))
        columna = int(round(event.xdata))
        filas, columnas = self.ultimo_resultado.malla_resultado.shape
        if not (0 <= fila < filas and 0 <= columna < columnas):
            return

        temperatura = float(self.ultimo_resultado.malla_resultado[fila, columna])
        potencia = float(self.ultimo_resultado.malla_potencia[fila, columna])
        self.label_Ppixel.config(text=f"{potencia:.6f}")
        texto = f"Pixel ({fila}, {columna}) · T={temperatura:.2f} °C · P={potencia:.6f} W"
        self.status_label.config(text=texto)
        if hasattr(self, "label_pixel_resultado") and self.label_pixel_resultado.winfo_exists():
            self.label_pixel_resultado.config(
                text=f"{texto} · Resolución {filas}x{columnas} · Panel {self.ultimo_resultado.tipo_panel}"
            )
    
    def exportar_csv(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if ruta and self.ultimo_resultado:
            try:
                from servicios import exportar_csv
                exportar_csv(self.ultimo_resultado.historial_error, ruta)
                messagebox.showinfo("Éxito", f"Archivo guardado: {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el CSV: {e}")
    
    def exportar_mapa(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if ruta and self.ultimo_resultado:
            try:
                from servicios import guardar_mapa_calor
                guardar_mapa_calor(
                    self.ultimo_resultado.malla_resultado,
                    ruta,
                    T_min=float(self.var_T_min.get()),
                    T_max=float(self.var_T_max.get())
                )
                messagebox.showinfo("Éxito", f"Archivo guardado: {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el mapa de calor: {e}")
    
    def exportar_grafica(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if ruta and self.ultimo_resultado:
            try:
                from servicios import guardar_grafica_convergencia
                guardar_grafica_convergencia(
                    self.ultimo_resultado.historial_error, 
                    ruta,
                    self.ultimo_resultado.iteraciones,
                    tolerancia=float(self.var_tolerancia.get())
                )
                messagebox.showinfo("Éxito", f"Archivo guardado: {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la gráfica: {e}")

    def exportar_pixeles(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if ruta and self.ultimo_resultado:
            try:
                from servicios import exportar_csv_pixeles
                exportar_csv_pixeles(
                    self.ultimo_resultado.malla_resultado,
                    self.ultimo_resultado.malla_potencia,
                    ruta
                )
                messagebox.showinfo("Éxito", f"Archivo guardado: {ruta}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el CSV por píxel: {e}")
    
    def limpiar(self):
        self.imagen_cargada = False
        self.var_tolerancia.set("1e-4")
        self.var_max_iter.set("200")
        self.label_omega_auto.config(text="Se calcula al ejecutar")
        self.var_lambda.set("1.0")
        self.var_T_min.set("20")
        self.var_T_max.set("100")
        self.var_tipo_panel.set("Monocristalino")
        self.var_pdc0.set("450")
        self.var_irradiancia.set("1000")
        self.label_iter.config(text="0")
        self.label_error.config(text="0")
        self.label_tiempo.config(text="0")
        self.label_Tmax.config(text="0")
        self.label_Tmedia.config(text="0")
        self.label_Ptotal.config(text="0")
        self.label_Ppixel.config(text="0")
        self.label_Omega.config(text="0")
        self.ultimo_resultado = None
        self.badge_convergencia.config(bg=self.BORDER_LIGHT)
        self.badge_convergencia_label.config(text="Pendiente", fg=self.TEXT_BODY, bg=self.BORDER_LIGHT)
        self.dropzone.config(bg=self.BORDER_LIGHT)
        self.label_N_value.config(text="(cargue imagen)")
        self.btn_calcular.config(state=tk.DISABLED)
        self.btn_exportar_csv.config(state=tk.DISABLED)
        self.btn_exportar_mapa.config(state=tk.DISABLED)
        self.btn_exportar_grafica.config(state=tk.DISABLED)
        self.btn_exportar_pixeles.config(state=tk.DISABLED)
        self.status_label.config(text="Listo")
        self.status_indicator.config(fg="#4CAF50")
        if self.canvas_resultados:
            self.canvas_resultados.get_tk_widget().destroy()
            self.canvas_resultados = None
        self.ax_heatmap = None
        self.label_modo_resultado.config(text="Cargue una imagen y calcule para ver resultados")
        self.label_pixel_resultado.config(
            text="En el mapa de calor se mostrará fila, columna, temperatura y potencia del píxel"
        )
        if hasattr(self, "label_placeholder_central") and self.label_placeholder_central.winfo_exists():
            self.label_placeholder_central.destroy()
        self.label_placeholder_central = tk.Label(
            self.frame_figura_resultado,
            text="Cargue una imagen para comenzar",
            font=("Segoe UI", 14, "bold"),
            fg=self.TEXT_BODY,
            bg=self.BG_WINDOW
        )
        self.label_placeholder_central.pack(expand=True)

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
