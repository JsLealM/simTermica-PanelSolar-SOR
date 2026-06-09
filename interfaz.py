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

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Simulación Térmica - Panel Solar")
        self.geometry("1400x850")
        
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
        self.resizable(False, False)
        
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
        
        # Dropzone
        self.dropzone = tk.Frame(panel, bg=self.BORDER_LIGHT, relief=tk.RIDGE, borderwidth=2)
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
        frame_N = tk.Frame(panel, bg=self.BG_SIDEBAR)
        frame_N.pack(fill=tk.X, padx=12, pady=(0, 8))
        tk.Label(frame_N, text="Tamaño malla (N)", font=("Segoe UI", 8), fg=self.TEXT_SECTION, bg=self.BG_SIDEBAR).pack(anchor="w")
        self.label_N_value = tk.Label(frame_N, text="(cargue imagen)", font=("Segoe UI", 10, "bold"), fg=self.ACCENT, bg=self.BG_SIDEBAR)
        self.label_N_value.pack(anchor="w", pady=(4, 0))
        
        # Input fields
        self.crear_campo_entrada(panel, "Tolerancia (e)", "tolerancia", 1e-4, 1e-8, 1e-1)
        self.crear_campo_entrada(panel, "Máx iteraciones", "max_iter", 1000, 100, 10000)
        
        # Omega slider
        self.crear_slider_omega(panel)
        
        # Lambda field
        self.crear_campo_entrada(panel, "Lambda (l)", "lambda", 1.0, 0.1, 5.0)
        self.crear_campo_entrada(panel, "T mín (°C)", "T_min", 20, 0, 100)
        self.crear_campo_entrada(panel, "T máx (°C)", "T_max", 100, 25, 200)
        
        # Badge SOR
        badge_frame = tk.Frame(panel, bg=self.ACCENT)
        badge_frame.pack(fill=tk.X, padx=12, pady=12)
        tk.Label(badge_frame, text="Método SOR", font=("Segoe UI", 9, "bold"),
                fg="white", bg=self.ACCENT).pack(pady=4)
        
        # Buttons
        btn_frame = tk.Frame(panel, bg=self.BG_SIDEBAR)
        btn_frame.pack(fill=tk.X, padx=12, pady=12)
        
        self.btn_calcular = tk.Button(
            btn_frame,
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
            btn_frame,
            text="Limpiar",
            font=("Segoe UI", 10),
            bg=self.BORDER_LIGHT,
            fg=self.TEXT_BODY,
            relief=tk.FLAT,
            command=self.limpiar
        )
        self.btn_limpiar.pack(fill=tk.X, pady=4)
        
        self.btn_salir = tk.Button(
            btn_frame,
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
    
    def crear_slider_omega(self, parent):
        frame = tk.Frame(parent, bg=self.BG_SIDEBAR)
        frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        tk.Label(frame, text="Omega (w) - SOR", font=("Segoe UI", 8), fg=self.TEXT_SECTION, bg=self.BG_SIDEBAR).pack(anchor="w")
        
        self.var_omega = tk.DoubleVar(value=1.81)
        self.omega_label = tk.Label(frame, text="1.81", font=("Segoe UI", 9, "bold"), fg=self.ACCENT, bg=self.BG_SIDEBAR)
        self.omega_label.pack(anchor="e", pady=4)
        
        slider = tk.Scale(
            frame,
            from_=0.01,
            to=1.99,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.var_omega,
            bg=self.BORDER_LIGHT,
            fg=self.TEXT_BODY,
            command=lambda v: self.omega_label.config(text=f"{float(v):.2f}")
        )
        slider.pack(fill=tk.X)
    
    def crear_panel_central(self, parent):
        panel = tk.Frame(parent, bg=self.BG_WINDOW)
        
        self.canvas_matplotlib = None
        self.fig = None
        
        return panel
    
    def crear_panel_derecho(self, parent):
        panel = tk.Frame(parent, bg=self.BG_SIDEBAR, width=200)
        panel.pack_propagate(False)
        
        # Metric cards
        self.crear_metric_card(panel, "Iteraciones", "iter", "0")
        self.crear_metric_card(panel, "Error final", "error", "0")
        self.crear_metric_card(panel, "Tiempo (s)", "tiempo", "0")
        self.crear_metric_card(panel, "T máx (°C)", "Tmax", "0")
        
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
        self.btn_exportar_grafica.pack(fill=tk.X)
        
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
                self.label_N_value.config(text=f"{N_detectada}x{N_detectada} píxeles")
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
            omega = self.var_omega.get()
            lam = float(self.var_lambda.get())
            T_min = float(self.var_T_min.get())
            T_max = float(self.var_T_max.get())
            
            self.calculando = True
            self.status_label.config(text="Calculando... (en progreso)")
            self.status_indicator.config(fg="#FFC107")
            
            error_msg = self._validar_parametros(N, tol, max_iter, omega, lam, T_min, T_max)
            if error_msg:
                messagebox.showerror("Error de validación", error_msg)
                self.calculando = False
                self.status_label.config(text="Listo")
                self.status_indicator.config(fg="#4CAF50")
                return
            
            thread = threading.Thread(
                target=self.worker_calculo,
                args=(N, tol, max_iter, omega, lam, T_min, T_max),
                daemon=True
            )
            thread.start()
        except ValueError as e:
            messagebox.showerror("Error", "Verifique los valores de entrada")
            self.calculando = False
            self.status_label.config(text="Listo")
            self.status_indicator.config(fg="#4CAF50")
    
    def _validar_parametros(self, N, tol, max_iter, omega, lam, T_min, T_max):
        if N < 5:
            return "N debe ser >= 5"
        if tol <= 0:
            return "Tolerancia debe ser > 0"
        if max_iter <= 0:
            return "Máx iteraciones debe ser > 0"
        if omega <= 0 or omega >= 2:
            return "Omega debe estar en el rango (0, 2)"
        if lam == 0:
            return "Lambda no puede ser 0"
        if T_min >= T_max:
            return "T_min debe ser menor que T_max"
        return None
    
    def worker_calculo(self, N, tol, max_iter, omega, lam, T_min, T_max):
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
                "T_max": T_max
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
        
        self.mostrar_graficas()
    
    def mostrar_graficas(self):
        if self.canvas_matplotlib:
            self.canvas_matplotlib.get_tk_widget().destroy()
        
        if self.ultimo_resultado is None:
            return
        
        from servicios import generar_figura_doble
        try:
            escala_T_min = float(self.var_T_min.get())
            escala_T_max = float(self.var_T_max.get())
        except ValueError:
            escala_T_min = self.ultimo_resultado.T_min_calculada
            escala_T_max = self.ultimo_resultado.T_max_calculada

        self.fig = generar_figura_doble(
            imagen_grises=self.controlador.imagen_grises,
            malla_resultado=self.ultimo_resultado.malla_resultado,
            T_min=escala_T_min,
            T_max=escala_T_max
        )
        
        self.canvas_matplotlib = FigureCanvasTkAgg(self.fig, master=self.panel_central)
        self.canvas_matplotlib.draw()
        self.canvas_matplotlib.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
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
    
    def limpiar(self):
        self.imagen_cargada = False
        self.var_tolerancia.set("1e-4")
        self.var_max_iter.set("1000")
        self.var_omega.set(1.81)
        self.var_lambda.set("1.0")
        self.var_T_min.set("20")
        self.var_T_max.set("100")
        self.label_iter.config(text="0")
        self.label_error.config(text="0")
        self.label_tiempo.config(text="0")
        self.label_Tmax.config(text="0")
        self.ultimo_resultado = None
        self.badge_convergencia.config(bg=self.BORDER_LIGHT)
        self.badge_convergencia_label.config(text="Pendiente", fg=self.TEXT_BODY, bg=self.BORDER_LIGHT)
        self.dropzone.config(bg=self.BORDER_LIGHT)
        self.label_N_value.config(text="(cargue imagen)")
        self.btn_calcular.config(state=tk.DISABLED)
        self.btn_exportar_csv.config(state=tk.DISABLED)
        self.btn_exportar_mapa.config(state=tk.DISABLED)
        self.btn_exportar_grafica.config(state=tk.DISABLED)
        self.status_label.config(text="Listo")
        self.status_indicator.config(fg="#4CAF50")
        if self.canvas_matplotlib:
            self.canvas_matplotlib.get_tk_widget().destroy()
            self.canvas_matplotlib = None

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
