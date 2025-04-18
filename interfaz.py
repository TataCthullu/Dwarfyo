from tkinter import *
from tkinter.scrolledtext import ScrolledText
from utils import reproducir_sonido, detener_sonido_y_cerrar
from codigo_principala import TradingBot


class BotInterface:
    def __init__(self, bot: TradingBot):
        # initialize bot and clear only ingreso price until started
        self.bot = bot
        self.bot.log_fn = self.log_en_consola
        
        

        # Main window setup
        self.root = Tk()
        self.root.title("Khazâd")
        self.root.configure(bg="DarkGoldenrod")
        self.root.iconbitmap("imagenes/dm.ico")
        self.root.attributes("-alpha", 0.95)

        # UI variables and clear initial values
        self._create_stringvars()
        self.info_labels = {}
        self.valores_iniciales = {}

        # Layout
        self._create_frames()
        self._create_info_panel()
        self._create_center_panel()
        self._create_right_panel()
        self._create_buttons()
        
        self.actualizar_ui()

        # Baseline for color comparisons
        #self._initialize_baseline()
        

    def _create_stringvars(self):
        # Display and config variables
        self.precio_act_var = StringVar()
        self.balance_var = StringVar()
        self.cant_btc_str = StringVar()
        self.btc_en_usdt = StringVar()
        self.varpor_set_compra_str = StringVar()
        self.varpor_set_venta_str = StringVar()
        self.precio_de_ingreso_str = StringVar()
        self.var_inicio_str = StringVar()
        self.ganancia_total_str = StringVar()
        self.cont_compras_fantasma_str = StringVar()
        self.cont_ventas_fantasma_str = StringVar()
        self.ghost_ratio_var = StringVar()
        self.compras_realizadas_str = StringVar()
        self.ventas_realizadas_str = StringVar()
        self.porc_objetivo_venta_str = StringVar()
        self.cant_usdt_str = StringVar()
        self.porc_desde_compra_str = StringVar()
        self.porc_desde_venta_str = StringVar()
        self.inv_por_compra_str = StringVar()
        self.fixed_buyer_str = StringVar()
        

    

    def _create_frames(self):
        self.main_frame = Frame(self.root, bg="DarkGoldenrod")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.main_frame.grid_columnconfigure(i, weight=0 if i<2 else 2, minsize=350)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)

    def _create_info_panel(self):
        self.info_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.info_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        def add(label, var, key=None):
            row = Frame(self.info_frame, bg="DarkGoldenrod"); row.pack(anchor="w", pady=2)
            Label(row, text=label, bg="DarkGoldenrod", font=("CrushYourEnemies",12)).pack(side=LEFT)
            lbl = Label(row, textvariable=var, bg="Gold", font=("CrushYourEnemies",12)); lbl.pack(side=LEFT)
            if key: self.info_labels[key] = lbl
        add("Precio actual BTC/USDT:", self.precio_act_var, "precio_actual")
        add("Usdt + Btc:", self.balance_var, "balance")
        add("Btc Disponible:", self.cant_btc_str, "btc_dispo")
        add("Btc en Usdt:", self.btc_en_usdt, "btcnusdt")
        add("% Desde última compra:", self.varpor_set_compra_str, "desde_ult_comp")
        add("% Desde última venta:", self.varpor_set_venta_str, "ult_vent")
        add("Precio de ingreso:", self.precio_de_ingreso_str, "desde_inicio")
        add("Variación desde inicio:", self.var_inicio_str, "variacion_desde_inicio")
        add("Ganancia neta en Usdt:", self.ganancia_total_str, "ganancia_neta")
        add("Compras fantasma:", self.cont_compras_fantasma_str, "compras_f")
        add("Ventas fantasma:", self.cont_ventas_fantasma_str, "ventas_f")
        add("Ghost Ratio:", self.ghost_ratio_var, "ghost_ratio")
        add("Compras Realizadas:", self.compras_realizadas_str, "compras_r")
        add("Ventas Realizadas:", self.ventas_realizadas_str, "ventas_r")

    def _create_center_panel(self):
        self.center_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.center_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        def add(label, var, key=None):
            row = Frame(self.center_frame, bg="DarkGoldenrod"); row.pack(anchor="w", pady=2)
            Label(row, text=label, bg="DarkGoldenrod", font=("CrushYourEnemies",12)).pack(side=LEFT)
            lbl = Label(row, textvariable=var, bg="Gold", font=("CrushYourEnemies",12)); lbl.pack(side=LEFT)
            if key: self.info_labels[key] = lbl
        add("% Para objetivo de venta:", self.porc_objetivo_venta_str, "porc_obj_venta")
        add("Usdt Disponible:", self.cant_usdt_str, "usdt")
        add("% Desde compra:", self.porc_desde_compra_str, "porc_desde_compra")
        add("% Desde venta:", self.porc_desde_venta_str, "porc_desde_venta")
        add("% nversión/op:", self.inv_por_compra_str, "porc_inv_por_compra")
        add("Monto fijo inversión:", self.fixed_buyer_str, "fixed_buyer")
        Button(self.center_frame, text="Configurar Operativa", bg="Goldenrod", command=self.abrir_configuracion_subventana).pack(pady=10)

    def _create_right_panel(self):
        self.right_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self.historial = ScrolledText(self.right_frame, bg="Gold", font=("CrushYourEnemies",10)); self.historial.pack(expand=True, fill=BOTH)
        self.consola = ScrolledText(self.right_frame, bg="Gold", font=("CrushYourEnemies",10)); self.consola.pack(expand=True, fill=BOTH)

    def _create_buttons(self):
        f = Frame(self.main_frame, bg="DarkGoldenrod"); f.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        f.grid_columnconfigure(0, weight=1); f.grid_columnconfigure(1, weight=1)
        self.btn_inicio = Button(f, text="Iniciar", command=self.alternar_bot, bg="Goldenrod"); self.btn_inicio.grid(row=0, column=0, sticky="ew", padx=2)
        self.btn_limpiar = Button(f, text="Limpiar", command=self.clear_bot, bg="Goldenrod"); self.btn_limpiar.grid(row=0, column=1, sticky="ew", padx=2)

    # Función para obtener el valor sin el símbolo %
    def obtener_valor_limpio(entry_var):
        valor = entry_var.get().replace('%', '').replace('$', '').strip()
        
        try:
            return float(valor)
            
        except ValueError:
            return 0  # o lo que quieras como fallback

    def abrir_configuracion_subventana(self):
        config_ventana = Toplevel(self.root)
        config_ventana.title("Configuración de operativa")
        config_ventana.configure(bg="DarkGoldenrod")
        # Al cerrar la ventana
        def cerrar_config():
            detener_sonido_y_cerrar(config_ventana)
            config_ventana.destroy()
        config_ventana.protocol("WM_DELETE_WINDOW", cerrar_config)
        reproducir_sonido("Sounds/antorcha.wav")

        # Campos configurables: etiqueta y valor actual
        campos = [
            ("% Desde compra:",    self.bot.porc_desde_compra),
            ("% Desde venta:",     self.bot.porc_desde_venta),
            ("Profit venta (%):",  self.bot.porc_profit_x_venta),
            ("% Inversión op:",    self.bot.porc_inv_por_compra),
            ("Total USDT:",        self.bot.usdt),
        ]
        entries = []
        for etiqueta, valor in campos:
            frame = Frame(config_ventana, bg="DarkGoldenrod")
            frame.pack(fill=X, pady=4, padx=8)
            Label(frame, text=etiqueta, bg="DarkGoldenrod", font=("CrushYourEnemies",12)).pack(side=LEFT)
            var = StringVar(value=str(valor))
            Entry(frame, textvariable=var, bg="Gold", font=("CrushYourEnemies",12)).pack(side=LEFT, padx=6)
            entries.append(var)

        def guardar_config():
            try:
                # Asignar los nuevos valores al bot
                self.bot.porc_desde_compra    = float(entries[0].get())
                self.bot.porc_desde_venta     = float(entries[1].get())
                self.bot.porc_profit_x_venta  = float(entries[2].get())
                self.bot.porc_inv_por_compra  = float(entries[3].get())
                self.bot.usdt                  = float(entries[4].get())
                # Recalcular fixed_buyer
                self.bot.fixed_buyer = self.bot.usdt * self.bot.porc_inv_por_compra / 100
                self.log_en_consola("Configuración actualizada.")
                cerrar_config()
            except ValueError:
                self.log_en_consola("Error: ingresa valores numéricos válidos.")

            Button(config_ventana, text="Guardar", bg="Goldenrod", command=guardar_config, font=("CrushYourEnemies",12)).pack(pady=8)


    
           

      

    """def _safe_set(self, var: StringVar, value, fmt: str):
       
        var.set(fmt.format(value) if value is not None else "N/D")"""

    def actualizar_ui(self):
        try:
            if self.bot.running:
                self.precio_act_var.set(f"$ {self.bot.precio_actual:.4f}" if self.bot.precio_actual else "N/D")
                self.cant_btc_str.set(f"₿ {self.bot.btc:.6f}")
                self.cant_usdt_str.set(f"$ {self.bot.usdt:.6f}")
                self.balance_var.set(f"$ {self.bot.usdt_mas_btc:.2f}" if self.bot.precio_actual else "0")
                self.btc_en_usdt.set(f"$ {self.bot.btc_usdt:.6f}" if self.bot.precio_actual else "N/D")
                self.precio_de_ingreso_str.set(f"$ {self.bot.precio_ingreso:.4f}" if self.bot.precio_ingreso else "N/D")
                self.inv_por_compra_str.set(f"% {self.bot.porc_inv_por_compra:.4f}")
                self.varpor_set_compra_str.set(f"% {self.bot.varCompra:.6f}" if self.bot.varCompra else "N/D")
                self.varpor_set_venta_str.set(f"% {self.bot.varVenta:.6f}" if self.bot.varVenta else "N/D")
                self.porc_desde_compra_str.set(f"% {self.bot.porc_desde_compra:.4f}")
                self.porc_desde_venta_str.set(f"% {self.bot.porc_desde_venta:.4f}")
                self.var_inicio_str.set(f"% {self.bot.var_inicio:.6f}" if self.bot.var_inicio else "N/D")
                self.fixed_buyer_str.set(f"$ {self.bot.fixed_buyer:.2f}")
                self.ganancia_total_str.set(f"$ {self.bot.total_ganancia:.6f}")
                self.cont_compras_fantasma_str.set(str(self.bot.contador_compras_fantasma))
                self.cont_ventas_fantasma_str.set(str(self.bot.contador_ventas_fantasma))
                self.porc_objetivo_venta_str.set(f"% {self.bot.porc_profit_x_venta}")
                self.ghost_ratio_var.set(f"{self.bot.calcular_ghost_ratio():.2f}")
                self.compras_realizadas_str.set(str(self.bot.contador_compras_reales))
                self.ventas_realizadas_str.set(str(self.bot.contador_ventas_reales))
        except Exception as e:
            print("Error al actualizar la UI:", e)

    def log_en_consola(self, mensaje):
        self.consola.insert(END, mensaje + "\n")
        self.consola.see(END)

    def alternar_bot(self):
        global limpiar_visible
        if not self.bot.running:
            self.bot.iniciar()
            
            reproducir_sonido("Sounds/soundinicio.wav")
            self.actualizar_ui()
            self.btn_inicio.config(text="Detener") 
                   
        else:
            self.bot.detener()
            reproducir_sonido("Sounds/detner.wav")
            #self.btn_inicio.config(text="Detener") 
            self.btn_inicio.grid_remove()
            limpiar_visible = True
            self.btn_limpiar.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

    def _loop(self):
        if self.bot.running:
            self.bot.loop()
            self.actualizar_ui()
            self.root.after(3000, self._loop)

    def clear_bot(self):
        if not self.bot.running:
            reproducir_sonido("Sounds/soundlimpiara.wav")
            self.bot = TradingBot()
            self.bot.log_fn = self.log_en_consola
            self.historial.delete('1.0', END)
            self.consola.delete('1.0', END)
            self.log_en_consola("\ud83d\udd04 Khazâd reiniciado")
            self.btn_limpiar.grid_remove()
            self.btn_inicio(text="Iniciar")

    def inicializar_valores_iniciales(self):
        if self.bot.precio_actual is not None:
            self.valores_iniciales["precio_actual"] = self.bot.precio_actual
        if self.bot.usdt_mas_btc is not None:
            self.valores_iniciales["balance"] = self.bot.usdt_mas_btc
        if self.bot.varCompra is not None:
            self.valores_iniciales["desde_ult_comp"] = self.bot.varCompra
        if self.bot.varVenta is not None:
            self.valores_iniciales["ult_vent"] = self.bot.varVenta
        if self.bot.var_inicio is not None:
            self.valores_iniciales["variacion_desde_inicio"] = self.bot.var_inicio

    def run(self):
        self.actualizar_ui()
        self.root.mainloop()
