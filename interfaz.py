
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from utils import reproducir_sonido, detener_sonido_y_cerrar

class BotInterface:
    def __init__(self, bot):
        self.bot = bot
        self.bot.log_fn = self.log_en_consola
        self.valores_iniciales = {}
        self.limpiar_visible = False

        # Crear ventana
        self.root = Tk()
        self.root.title("Khazâd")
        self.root.configure(bg="DarkGoldenrod")
        self.root.iconbitmap("imagenes/dm.ico")
        self.root.attributes("-alpha", 0.95)

        # Variables Tkinter
        self._crear_stringvars()
        # Layout frames y widgets
        self._crear_frames()
        self._crear_info_panel()
        self._crear_center_panel()
        self._crear_right_panel()
        self._crear_botones()

        # Inicializar UI
        self._inicializar_baseline()
        self.actualizar_ui()

    def _crear_stringvars(self):
        self.precio_act_var = StringVar()
        self.cant_btc_str = StringVar()
        self.cant_usdt_str = StringVar()
        self.balance_var = StringVar()
        self.btc_en_usdt = StringVar()
        self.varpor_set_venta_str = StringVar()
        self.varpor_set_compra_str = StringVar()
        self.porc_desde_compra_str = StringVar()
        self.porc_desde_venta_str = StringVar()
        self.precio_de_ingreso_str = StringVar()
        self.inv_por_compra_str = StringVar()
        self.var_inicio_str = StringVar()
        self.fixed_buyer_str = StringVar()
        self.ganancia_total_str = StringVar()
        self.contador_compras_fantasma_str = StringVar()
        self.contador_ventas_fantasma_str = StringVar()
        self.porc_objetivo_venta_str = StringVar()
        self.ghost_ratio_var = StringVar()
        self.compras_realizadas_str = StringVar()
        self.ventas_realizadas_str = StringVar()
        self.info_labels = {}

    def _crear_frames(self):
        self.main_frame = Frame(self.root, bg="DarkGoldenrod")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        # columnas
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=350)
        self.main_frame.grid_columnconfigure(1, weight=0, minsize=350)
        self.main_frame.grid_columnconfigure(2, weight=2, minsize=350)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)

    def _crear_info_panel(self):
        self.info_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.info_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        def add_info(label, var, key=None):
            row = Frame(self.info_frame, bg="DarkGoldenrod")
            row.pack(anchor="w", pady=2)
            Label(row, text=label, bg="DarkGoldenrod", font=("CrushYourEnemies", 12)).pack(side=LEFT)
            lbl = Label(row, textvariable=var, bg="Gold", font=("CrushYourEnemies", 12))
            lbl.pack(side=LEFT)
            if key: self.info_labels[key] = lbl

        add_info("Precio actual BTC/USDT:", self.precio_act_var, "precio_actual")
        add_info("Usdt + Btc:", self.balance_var, "balance")
        add_info("Btc Disponible:", self.cant_btc_str, "btc_dispo")
        add_info("Btc en Usdt:", self.btc_en_usdt, "btcnusdt")
        add_info("% Desde ultima compra:", self.varpor_set_compra_str, "desde_ult_comp")
        add_info("% Desde ultima venta:", self.varpor_set_venta_str, "ult_vent")
        add_info("Precio de ingreso:", self.precio_de_ingreso_str, "desde_inicio")
        add_info("Variación desde inicio:", self.var_inicio_str, "variacion_desde_inicio")
        add_info("Ganancia neta en Usdt:", self.ganancia_total_str, "ganancia_neta")
        add_info("Compras fantasma:", self.contador_compras_fantasma_str, "compras_f")
        add_info("Ventas fantasma:", self.contador_ventas_fantasma_str, "ventas_f")
        add_info("Ghost Ratio:", self.ghost_ratio_var, "gr")
        add_info("Compras Realizadas:", self.compras_realizadas_str, "compras_r")
        add_info("Ventas Realizadas:", self.ventas_realizadas_str, "ventas_r")
        # ... repetir para todas las etiquetas necesarias

    def _crear_center_panel(self):          
        self.center_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.center_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
            
        def add_center_info(label, var, key=None):
            row = Frame(self.center_frame, bg="DarkGoldenrod")
            row.pack(anchor="w", pady=2)
            Label(row, text=label, bg="DarkGoldenrod", font=("CrushYourEnemies", 12)).pack(side=LEFT)
            lbl = Label(row, textvariable=var, bg="Gold", font=("CrushYourEnemies", 12))
            lbl.pack(side=LEFT)
            if key:
                self.info_labels[key] = lbl
        
        add_center_info("% Para objetivo de venta:", self.porc_objetivo_venta_str, "porc_obj_venta")
        add_center_info("Usdt Disponible:", self.cant_usdt_str, "usdt_disponible")
        add_center_info("Monto fijo por inversión:", self.fixed_buyer_str, "monto_inversion")
        add_center_info("Inversión por compra:", self.inv_por_compra_str, "inversion_por_compra")

        # Botón de configuración
        Button(self.center_frame, text="Configurar Operativa", bg="Goldenrod", command=self.abrir_config).pack(pady=10)

    def _crear_right_panel(self):
        self.right_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self.historial = ScrolledText(self.right_frame, bg="Goldenrod", font=("CrushYourEnemies", 10))
        self.historial.pack(expand=True, fill=BOTH)
        self.consola = ScrolledText(self.right_frame, bg="Goldenrod", font=("CrushYourEnemies", 10))
        self.consola.pack(expand=True, fill=BOTH)

    def _crear_botones(self):
        frame = Frame(self.main_frame, bg="DarkGoldenrod")
        frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        self.btn_inicio = Button(frame, text="Iniciar", command=self.alternar_bot)
        self.btn_inicio.grid(row=0, column=0, sticky="ew", padx=2)
        self.btn_limpiar = Button(frame, text="Limpiar", command=self.limpiar_bot)
        self.btn_limpiar.grid(row=0, column=1, sticky="ew", padx=2)
        self.btn_limpiar.grid_remove()

    # Métodos de callback:
    def abrir_config(self):
        config_win = Toplevel(self.root)
        config_win.title("Configuración de operativa")
        config_win.configure(bg="DarkGoldenrod")
        config_win.protocol("WM_DELETE_WINDOW", lambda: detener_sonido_y_cerrar(config_win))
        reproducir_sonido("Sounds/antorcha.wav")
        
        # Lista de campos: (etiqueta, atributo bot, StringVar asociada)
        fields = [
            ("Porcentaje desde compra:", 'porc_desde_compra', self.porc_desde_compra_str),
            ("Porcentaje desde venta:", 'porc_desde_venta', self.porc_desde_venta_str),
            ("Profit por venta (%):", 'porc_profit_x_venta', self.porc_objetivo_venta_str),
            ("Porc. inversión por operación:", 'porc_inv_por_compra', self.inv_por_compra_str),
        ]
        
        for text, attr, var in fields:
            frame = Frame(config_win, bg="DarkGoldenrod")
            frame.pack(fill=X, pady=5)
            Label(frame, text=text, bg="DarkGoldenrod", font=("CrushYourEnemies",12)).pack(side=LEFT)
            Entry(frame, textvariable=var, font=("CrushYourEnemies",12), bg="Gold").pack(side=LEFT, padx=5)

    def guardar_config():
        try:
            for _, attr, var in fields:
                val = var.get().replace('%','').replace('$','').strip()
                setattr(self.bot, attr, float(val))
            self.bot.fixed_buyer = (self.bot.usdt * self.bot.porc_inv_por_compra) / 100
            reproducir_sonido("Sounds/soundcompra.wav")
            config_win.destroy()
        except Exception:
            print("Error: ingresa valores válidos.")

    Button(config_win, text="Guardar", bg="Goldenrod", command=guardar_config).pack(pady=10)

# Botón guardar
    def guardar():
            # Asignar valores al bot
        try:
            self.bot.porc_desde_compra = float(self.porc_desde_compra_str.get().strip('% '))
            self.bot.porc_desde_venta = float(self.porc_desde_venta_str.get().strip('% '))
            self.bot.porc_profit_x_venta = float(self.porc_objetivo_venta_str.get().strip('% '))
            self.bot.usdt = float(self.usdt.get().strip('$ '))
            reproducir_sonido("Sounds/soundcompra.wav")
            config_win.destroy()
        except ValueError:
            print("Valores inválidos")
    Button(config_win, text="Guardar", command=guardar, bg="Goldenrod").pack(pady=10)    


    def alternar_bot(self):
        if not self.bot.running:
            self.bot.iniciar()
            self.bot.loop(self.actualizar_ui, self.root.after)
            reproducir_sonido("Sounds/soundinicio.wav")
            self.btn_inicio.config(text="Detener")
        else:
            self.bot.detener()
            reproducir_sonido("Sounds/detner.wav")
            self.btn_inicio.grid_remove()
            self.btn_limpiar.grid()

    def limpiar_bot(self):
        if not self.bot.running:
            reproducir_sonido("Sounds/soundlimpiara.wav")
            from codigo_principala import TradingBot
            self.bot = TradingBot()
            self.bot.log_fn = self.log_en_consola
            self.bot.actualizar_balance()
            self.valores_iniciales.clear()
            self.actualizar_ui()
            self.consola.insert(END, "🔄 Khazâd reiniciado\n")
            self.btn_limpiar.grid_remove()
            self.btn_inicio.grid()
            self.btn_inicio.config(text="Iniciar")

    def actualizar_ui(self, bot):
        if not ventana_principal.winfo_exists():
            return
        try:
            if bot.running:
                
                # Actualizamos el precio, usando comprobación explícita (incluso si es 0)
                if bot.precio_actual is not None:
                    self.precio_act_var.set(f"$ {bot.precio_actual:.4f}")
                else:
                    self.precio_act_var.set("N/D")

                self.cant_btc_str.set(f"₿ {bot.btc:.6f}")
                self.cant_usdt_str.set(f"$ {bot.usdt:.6f}")
                self.balance_var.set(f"$ {bot.usdt_mas_btc}" if bot.precio_actual else 0)
                self.btc_en_usdt.set(f"$ {bot.btc_usdt:.6f}" if bot.precio_actual else "N/D")
                self.precio_de_ingreso_str.set(f"$ {bot.precio_ingreso:.4f}" if bot.precio_ingreso else "N/D")
                self.inv_por_compra_str.set(f"% {bot.porc_inv_por_compra:.4f}")
                self.varpor_set_compra_str.set(f"% {bot.varCompra:.6f}" if bot.varCompra is not None else "N/D")
                self.varpor_set_venta_str.set(f"% {bot.varVenta:.6f}" if bot.varVenta is not None else "N/D")
                self.porc_desde_compra_str.set(f"% {bot.porc_desde_compra:.4f}")
                self.porc_desde_venta_str.set(f"% {bot.porc_desde_venta:.4f}")
                self.var_inicio_str.set(f"% {bot.var_inicio:.6f}" if bot.var_inicio is not None else "N/D")
                self.fixed_buyer_str.set(f"$ {bot.fixed_buyer:.2f}")
                self.ganancia_total_str.set(f"$ {bot.total_ganancia:.6f}")
                self.contador_compras_fantasma_str.set(f"{bot.contador_compras_fantasma}")
                self.contador_ventas_fantasma_str.set(f"{bot.contador_ventas_fantasma}")
                self.porc_objetivo_venta_str.set(f"% {bot.porc_profit_x_venta}")
                self.ghost_ratio = bot.calcular_ghost_ratio()
                self.ghost_ratio_var.set(f"{bot.ghost_ratio:.2f}")
                self.compras_realizadas_str.set(f"{bot.contador_compras_reales}")
                self.ventas_realizadas_str.set(f"{bot.contador_ventas_reales}")
                
                        
                self.actualizar_historial_consola()
                self.actualizar_color("precio_actual", bot.precio_actual)
                self.actualizar_color("balance", bot.usdt_mas_btc)
                self.actualizar_color("desde_ult_comp", bot.varCompra)
                self.actualizar_color("ult_vent", bot.varVenta)
                self.actualizar_color("variacion_desde_inicio", bot.var_inicio)        

            # Si el bot está detenido, mostramos "Limpiar" solo si el flag lo permite
            if self.limpiar_visible:
                self.boton_limpiar.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        except Exception as e:
            print("Error al actualizar la interfaz:", e)

        
    def actualizar_color(self, key, valor_actual):
        # Si el valor actual es None, no hacemos nada
        if valor_actual is None:
            return
        
        # Si aun no guardamos el valor inicial, lo guardamos ahora
        if key not in valores_iniciales:
            valores_iniciales[key] = valor_actual
            return  # A la primera actualización no hay comparación
        
        valor_inicial = valores_iniciales[key]
        
        # Determinar el color: verde si es mayor, rojo si es menor.
        if valor_actual > valor_inicial:
            color = "green"  # O "green"
        elif valor_actual < valor_inicial:
            color = "red"  # O "red"
        else:
            color = "black"  # Color por defecto
        
        # Actualizamos el fondo del Label correspondiente (podés actualizar también el foreground si lo prefieres)
        if key in info_labels:
            info_labels[key].configure(fg=color)


    def log_en_consola(self, msg):
        self.consola.insert(END, msg + "\n")
        self.consola.see(END)

    def _inicializar_baseline(self):
        # llena valores_iniciales con bot.precio_actual, bot.balance...
        pass

    def run(self):
        self.root.mainloop()


