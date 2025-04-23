from tkinter import *
from tkinter.scrolledtext import ScrolledText
from utils import reproducir_sonido, detener_sonido_y_cerrar
from codigo_principala import TradingBot
from calculador import CalculatorWindow



class BotInterface:
    def __init__(self, bot: TradingBot):
        # initialize bot and clear only ingreso price until started
        self.bot = bot
        self.bot.log_fn = self.log_en_consola
        
        self._font_normal = ("Carolingia", 22)
        self._font_nd     = ("Tolkien Dwarf Runes", 14) 
        
        # Lista de (StringVar, Label) para los No Data
        self.nd_labels = []
        # Main window setup
        self.root = Tk()
        self.root.title("Khazâd")
        self.root.configure(bg="DarkGoldenrod")
        self.root.iconbitmap("imagenes/dm.ico")
        self.root.attributes("-alpha", 0.93)

        # UI variables and clear initial values
        self._create_stringvars()
        
        
        self.valores_iniciales = {}
        self.limpiar_visible = False
        
        # Layout
        self._create_frames()
        self._create_info_panel()
        self._create_center_panel()
        self._create_right_panel()
        self._create_buttons()
        self.reset_stringvars()
        self.actualizar_ui()

        # Baseline for color comparisons
        self.inicializar_valores_iniciales()
        

    def _create_stringvars(self):
        # Display and config variables
        self.precio_act_var = StringVar()
        self.balance_var = StringVar()
           # <--- nueva var
        self.start_time_str = StringVar()
        self.runtime_str    = StringVar()
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
        

    def reset_stringvars(self):

        for attr, val in self.__dict__.items():
            if isinstance(val, StringVar):
                val.set("z")

        for var, lbl in self.nd_labels:
            lbl.config(font=self._font_nd)     

        


    def _create_frames(self):
        self.main_frame = Frame(self.root, bg="DarkGoldenrod")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.main_frame.grid_columnconfigure(i, weight=0 if i<2 else 2)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)

    def _create_info_panel(self):
        self.info_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.info_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.info_labels = {}
        def add(label, var, key=None):
            row = Frame(self.info_frame, bg="DarkGoldenrod"); row.pack(anchor="w", pady=2)
            Label(row, text=label, bg="DarkGoldenrod", font=self._font_normal, fg="PaleGoldenRod").pack(side=LEFT)
            lbl = Label(row, textvariable=var, bg="DarkGoldenrod", font=self._font_normal, fg="Gold"); lbl.pack(side=LEFT)
            # guardamos el par para pintar runas más tarde
            self.nd_labels.append((var, lbl))
            if key:
                self.info_labels[key] = lbl
            
        add("Precio actual Btc/Usdt:", self.precio_act_var, "precio_actual")
        add("Usdt + Btc:", self.balance_var, "balance")
        add("Btc Disponible:", self.cant_btc_str, "btc_dispo")
        add("Btc en Usdt:", self.btc_en_usdt, "btcnusdt")
        add("% Desde ultima compra:", self.varpor_set_compra_str, "desde_ult_comp")
        add("% Desde ultima venta:", self.varpor_set_venta_str, "ult_vent")
        add("Precio de ingreso:", self.precio_de_ingreso_str, "desde_inicio")
        add("Variacion desde inicio:", self.var_inicio_str, "variacion_desde_inicio")
        add("Ganancia neta en Usdt:", self.ganancia_total_str, "ganancia_neta")
        add("Compras fantasma:", self.cont_compras_fantasma_str, "compras_f")
        add("Ventas fantasma:", self.cont_ventas_fantasma_str, "ventas_f")
        add("Ghost Ratio:", self.ghost_ratio_var, "ghost_ratio")
        add("Compras Realizadas:", self.compras_realizadas_str, "compras_r")
        add("Ventas Realizadas:", self.ventas_realizadas_str, "ventas_r")      
        add("Fecha de inicio:", self.start_time_str, "start_time")
        add("Tiempo activo:", self.runtime_str,    "runtime")



    def _create_center_panel(self):
        self.center_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.center_frame.grid(row=0, column=1, sticky="n", padx=5, pady=5)
        def add(label, var, key=None):
            row = Frame(self.center_frame, bg="DarkGoldenrod"); row.pack(anchor="w", pady=2)
            Label(row, text=label, bg="DarkGoldenrod", font=self._font_normal, fg="PaleGoldenRod").pack(side=LEFT)
            lbl = Label(row, textvariable=var, bg="DarkGoldenrod", font=self._font_normal, fg="Gold"); lbl.pack(side=LEFT)
            # guardamos el par para pintar runas más tarde
            self.nd_labels.append((var, lbl))
            if key:
                self.info_labels[key] = lbl
        add("% Objetivo de venta, desde compra:", self.porc_objetivo_venta_str, "porc_obj_venta")
        add("Usdt Disponible:", self.cant_usdt_str, "usdt")
        add("% Desde compra, para compra:", self.porc_desde_compra_str, "porc_desde_compra")
        add("% Desde venta, para compra:", self.porc_desde_venta_str, "porc_desde_venta")
        add("% Por operacion:", self.inv_por_compra_str, "porc_inv_por_compra")
        add("% Fijo para inversion:", self.fixed_buyer_str, "fixed_buyer")
        
    def _create_right_panel(self):
        self.right_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        # Dividimos right_frame en 2 filas iguales
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # Historial arriba
        self.historial = ScrolledText(self.right_frame, bg="Goldenrod", font=("Carolingia", 17))
        self.historial.grid(row=0, column=0, sticky="e", padx=2, pady=2)

        # Consola abajo
        self.consola = ScrolledText(self.right_frame, bg="Goldenrod", font=("Carolingia", 18))
        self.consola.grid (row=1, column=0, sticky="e", padx=2, pady=2)



    def _create_buttons(self):
        self.buttons_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.buttons_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        self.btn_inicio = Button(self.buttons_frame, text="Iniciar", command=self.toggle_bot, bg="Goldenrod", font=("Carolingia", 14), fg="DarkSlateGray")
        self.btn_inicio.grid(row=0, column=0, sticky="ew", padx=2)
        self.btn_limpiar = Button(self.buttons_frame, text="Limpiar", command=self.clear_bot, bg="Goldenrod", font=("Carolingia", 14), fg="DarkSlateGray")
        btn_calc = Button(self.buttons_frame, text="Calculadora", command=self.open_calculator, bg="Goldenrod", font=("Carolingia", 14), fg="DarkSlateGray")
        btn_calc.grid(row=0, column=2, sticky="e", padx=2)
        self.btn_confi = Button(self.center_frame, text="Configurar Operativa", bg="Goldenrod", command=self.abrir_configuracion_subventana, font=("Carolingia",14), fg="DarkSlateGray")
        self.btn_confi.pack(pady=10)

        
        self.btn_limpiar.grid(row=0, column=1, sticky="ew", padx=2)
        self.btn_limpiar.grid_remove()

    def open_calculator(self):
         # pasamos los balances actuales
        usdt_avail = self.bot.usdt
        btc_avail  = self.bot.btc
        CalculatorWindow(self.root, usdt_avail, btc_avail)

        

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
        reproducir_sonido("Sounds/antorchab.wav")

        # Campos configurables: etiqueta y valor actual
        campos = [
            ("% Desde compra, para compra: %", self.bot.porc_desde_compra),
            ("% Desde venta, para compra: %", self.bot.porc_desde_venta),
            ("% Para venta, desde compra: %", self.bot.porc_profit_x_venta),
            ("% A invertir por operaciones: %", self.bot.porc_inv_por_compra),
            ("Total Usdt: $", self.bot.usdt),
        ]
        entries = []
        for etiqueta, valor in campos:
            frame = Frame(config_ventana, bg="DarkGoldenrod")
            frame.pack(fill=X, pady=4, padx=8)
            Label(frame, text=etiqueta, bg="DarkGoldenrod", font=self._font_normal, fg="DarkSlateGray").pack(side=LEFT)
            var = StringVar(value=str(valor))
            Entry(frame, textvariable=var, bg="DarkGoldenrod", font=self._font_normal, fg="Gold").pack(side=LEFT, padx=6)
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
                
                self.log_en_consola("Configuracion actualizada.")
                self.log_en_consola("- - - - - - - - - -")
                cerrar_config()
            except ValueError:
                self.log_en_consola("Error: ingresa valores numericos validos.")
                self.log_en_consola("- - - - - - - - - -")

        Button(config_ventana, text="Guardar", bg="Goldenrod", command=guardar_config, font=("Carolingia",14), fg="PaleGoldenRod").pack(pady=8)


    def toggle_bot(self):
            if self.bot.running:
                self.bot.detener()
                reproducir_sonido("Sounds/detner.wav")
                
                self.btn_inicio.grid_remove()  # Oculta el botón de estado
                
                self.btn_limpiar.grid()        # Muestra el botón limpiar
                self.btn_confi.pack_forget()
            else:
                self.btn_confi.pack_forget()
                self.bot.iniciar()
                
                reproducir_sonido("Sounds/soundinicio.wav")
                self.inicializar_valores_iniciales()
                self.btn_inicio.config(text="Detener")
                self.btn_limpiar.grid_remove()
                self.btn_confi.pack(pady=10)
                self._loop()

    def clear_bot(self):

        if not self.bot.running:
            reproducir_sonido("Sounds/limpiar.wav")
            # Limpiar UI
            self.consola.delete('1.0', END)
            self.historial.delete('1.0', END)
            
            # Reiniciar lógica del bot
            self.bot.reiniciar()
            self.inicializar_valores_iniciales() 

            # 3) Reset automático de todos los StringVar
            for attr, val in self.__dict__.items():
                if isinstance(val, StringVar):
                    val.set("z")

            for var, lbl in self.nd_labels:
                lbl.config(font=self._font_nd) 

            self.reset_colores()
            self.actualizar_ui()
            
            # Restaurar botones
            self.btn_confi.pack(pady=10)
            self.btn_limpiar.grid_remove()
            self.btn_inicio.grid(row=0, column=0, sticky="ew", padx=2)
            self.btn_inicio.config(text="Iniciar")
        else:
            self.btn_limpiar.grid_remove()

    def _loop(self):
        if self.bot.running:
            self.bot.loop()
            self.actualizar_ui()
            self.root.after(3000, self._loop)

    def actualizar_ui(self):
        try:
            if self.bot.running:
                precio = self.bot.precio_actual
                self.precio_act_var.set(f"$ {precio:.4f}" if precio else "z")
                self.cant_btc_str.set(f"₿ {self.bot.btc:.6f}")
                self.cant_usdt_str.set(f"$ {self.bot.usdt:.6f}")
                self.balance_var.set(f"$ {self.bot.usdt_mas_btc:.6f}" if self.bot.precio_actual else "0")
                self.btc_en_usdt.set(f"$ {self.bot.btc_usdt:.6f}" if self.bot.precio_actual else "z")
                self.precio_de_ingreso_str.set(f"$ {self.bot.precio_ingreso:.4f}" if self.bot.precio_ingreso else "z")
                self.inv_por_compra_str.set(f"% {self.bot.porc_inv_por_compra:.2f}")
                self.varpor_set_compra_str.set(f"% {self.bot.varCompra:.6f}" if self.bot.varCompra else "z")
                self.varpor_set_venta_str.set(f"% {self.bot.varVenta:.6f}" if self.bot.varVenta else "z")
                self.porc_desde_compra_str.set(f"% {self.bot.porc_desde_compra:.4f}")
                self.porc_desde_venta_str.set(f"% {self.bot.porc_desde_venta:.4f}")
                self.var_inicio_str.set(f"% {self.bot.var_inicio:.6f}" if self.bot.var_inicio else "z")
                self.fixed_buyer_str.set(f"$ {self.bot.fixed_buyer:.2f}")
                self.ganancia_total_str.set(f"$ {self.bot.total_ganancia:.6f}" if self.bot.total_ganancia else "z")
                self.cont_compras_fantasma_str.set(str(self.bot.contador_compras_fantasma) if self.bot.contador_compras_fantasma else "z")
                self.cont_ventas_fantasma_str.set(str(self.bot.contador_ventas_fantasma) if self.bot.contador_ventas_fantasma else "z")
                self.porc_objetivo_venta_str.set(f"% {self.bot.porc_profit_x_venta}" if self.bot.porc_profit_x_venta else "z")
                self.ghost_ratio_var.set(f"{self.bot.calcular_ghost_ratio():.2f}" if self.bot.calcular_ghost_ratio() else "z")
                self.compras_realizadas_str.set(str(self.bot.contador_compras_reales) if self.bot.contador_compras_reales else "z")
                self.ventas_realizadas_str.set(str(self.bot.contador_ventas_reales) if self.bot.contador_ventas_reales else "z")               
                self.start_time_str.set(self.bot.get_start_time_str())
                self.runtime_str.set(self.bot.get_runtime_str())
                
                # ——— ahora repintamos la fuente según si es "z" o un valor real ———
                for var, lbl in self.nd_labels:
                    if var.get() == "z":
                        lbl.configure(font=self._font_nd)
                    else:
                        lbl.configure(font=self._font_normal)

                self.actualizar_historial_consola()                
                self.actualizar_color("precio_actual", self.bot.precio_actual)
                self.actualizar_color("balance", self.bot.usdt_mas_btc)
                self.actualizar_color("desde_ult_comp", self.bot.varCompra)
                self.actualizar_color("ult_vent", self.bot.varVenta)
                self.actualizar_color("variacion_desde_inicio", self.bot.var_inicio)
              
        except Exception as e:
            print("Error al actualizar la UI:", e)
            
    def actualizar_historial_consola(self):
        self.historial.delete('1.0', END)
        for t in self.bot.transacciones:
            ts = t.get("timestamp", "")
            id_op = t.get("id")
            self.historial.insert(END, f"Compra desde: ${t['compra']:.2f} -> Id: {t['id']} -> Num: {t['numcompra']} -> {ts} -> Objetivo de venta: ${t['venta_obj']:.2f}\n")
        for v in self.bot.precios_ventas:
            ts = v.get("timestamp", "")
            self.historial.insert(END, f"Venta desde: $ {v['compra']:.2f} -> id compra: {v['id_compra']}, a: $ {v['venta']:.2f} | Ganancia: $ {v['ganancia']:.4f}, Num: {v['venta_numero']} -> {ts}\n")

    def actualizar_color(self, key, valor_actual):
        if valor_actual is None:
            return
        
        inicial = self.valores_iniciales[key]
        color = "Gold"
        if valor_actual > inicial:
            color = "green"
        elif valor_actual < inicial:
            color = "Crimson"
        lbl = self.info_labels.get(key)
        if lbl:
            lbl.configure(fg=color)

    def reset_colores(self):
        for lbl in self.info_labels.values():
            lbl.configure(fg="Gold")        
        
    def log_en_consola(self, msg):
        self.consola.insert(END, msg+"\n")
        self.consola.see(END)

    def inicializar_valores_iniciales(self):
        self.bot.actualizar_balance()
        # Guarda el primer snapshot para colorear luego
        self.valores_iniciales = {
            'precio_actual': self.bot.precio_actual or 0,
            'balance': self.bot.usdt_mas_btc,
            'desde_ult_comp': self.bot.varCompra,
            'ult_vent': self.bot.varVenta,
            'variacion_desde_inicio': self.bot.var_inicio
        }

    def run(self):
        self.root.mainloop()
