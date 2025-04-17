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
        add("% Desde compra:", self.bot.porc_desde_compra, "porc_desde_compra")
        add("% Desde venta:", self.bot.porc_desde_venta, "porc_desde_venta")
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
        self.btn_inicio = Button(f, text="Iniciar", command=self.toggle_bot, bg="Goldenrod"); self.btn_inicio.grid(row=0, column=0, sticky="ew", padx=2)
        self.btn_limpiar = Button(f, text="Limpiar", command=self.clear_bot, bg="Goldenrod"); self.btn_limpiar.grid(row=0, column=1, sticky="ew", padx=2); self.btn_limpiar.grid_remove()

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


    def toggle_bot(self):
        if not self.bot.running:
            self.bot.iniciar()
            #self.bot.precio_ingreso = self.bot.precio_actual
            reproducir_sonido("Sounds/soundinicio.wav")
            self.btn_inicio.config(text="Detener"); self.btn_limpiar.grid_remove()
            self.root.after(0, self._periodic)
        else:
            self.bot.detener(); reproducir_sonido("Sounds/detner.wav")
            self.btn_inicio.grid_remove(); self.btn_limpiar.grid()

    def _periodic(self):
        # Ejecuta una iteración de lógica y UI
        if self.bot.running:
            self.bot.loop()
            self.actualizar_ui()
            # Reagenda
            self.root.after(3000, self._periodic)        

    def clear_bot(self):
        if not self.bot.running:
            reproducir_sonido("Sounds/soundlimpiara.wav")
            
            self.bot = TradingBot(); self.bot.log_fn = self.log_en_consola
            
            #self._initialize_baseline() 
            self.historial.delete('1.0', END); self.consola.delete('1.0', END)
            self.consola.insert(END, "🔄 Khazâd reiniciado\n")
            self.btn_limpiar.grid_remove(); self.btn_inicio.grid(); self.btn_inicio.config(text="Iniciar")

    """def _initialize_baseline(self):
        self.bot.valores_iniciales"""     

    def _safe_set(self, var: StringVar, value, fmt: str):
       
        var.set(fmt.format(value) if value is not None else "N/D")

    def actualizar_ui():
        if not root.winfo_exists():
            return
        try:
            if self.bot.running:
                
                # Actualizamos el precio, usando comprobación explícita (incluso si es 0)
                if self.bot.precio_actual is not None:
                    self.precio_act_var.set(f"$ {self.bot.precio_actual:.4f}")
                else:
                    precio_act_var.set("N/D")

                cant_btc_str.set(f"₿ {bot.btc:.6f}")
                cant_usdt_str.set(f"$ {bot.usdt:.6f}")
                balance_var.set(f"$ {bot.usdt_mas_btc}" if bot.precio_actual else 0)
                btc_en_usdt.set(f"$ {bot.btc_usdt:.6f}" if bot.precio_actual else "N/D")
                precio_de_ingreso_str.set(f"$ {bot.precio_ingreso:.4f}" if bot.precio_ingreso else "N/D")
                inv_por_compra_str.set(f"% {bot.porc_inv_por_compra:.4f}")
                varpor_set_compra_str.set(f"% {bot.varCompra:.6f}" if bot.varCompra is not None else "N/D")
                varpor_set_venta_str.set(f"% {bot.varVenta:.6f}" if bot.varVenta is not None else "N/D")
                porc_desde_compra_str.set(f"% {bot.porc_desde_compra:.4f}")
                porc_desde_venta_str.set(f"% {bot.porc_desde_venta:.4f}")
                var_inicio_str.set(f"% {bot.var_inicio:.6f}" if bot.var_inicio is not None else "N/D")
                fixed_buyer_str.set(f"$ {bot.fixed_buyer:.2f}")
                ganancia_total_str.set(f"$ {bot.total_ganancia:.6f}")
                contador_compras_fantasma_str.set(f"{bot.contador_compras_fantasma}")
                contador_ventas_fantasma_str.set(f"{bot.contador_ventas_fantasma}")
                porc_objetivo_venta_str.set(f"% {bot.porc_profit_x_venta}")
                ghost_ratio = bot.calcular_ghost_ratio()
                ghost_ratio_var.set(f"{ghost_ratio:.2f}")
                compras_realizadas_str.set(f"{bot.contador_compras_reales}")
                ventas_realizadas_str.set(f"{bot.contador_ventas_reales}")
                
                        
                actualizar_historial_consola()
                actualizar_color("precio_actual", bot.precio_actual)
                actualizar_color("balance", bot.usdt_mas_btc)
                actualizar_color("desde_ult_comp", bot.varCompra)
                actualizar_color("ult_vent", bot.varVenta)
                actualizar_color("variacion_desde_inicio", bot.var_inicio)        

            # Si el bot está detenido, mostramos "Limpiar" solo si el flag lo permite
            if limpiar_visible:
                boton_limpiar.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        except Exception as e:
            print("Error al actualizar la interfaz:", e)

        
    def actualizar_color(key, valor_actual):
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


    def log_en_consola(mensaje):
        consola.insert(END, mensaje + "\n")
        consola.see(END)

    bot.log_fn = log_en_consola


    def actualizar_historial_consola():
        historial_box.delete('1.0', END)
        for trans in bot.transacciones:
            compra = trans.get('compra', 'N/A')
            venta_obj = trans.get('venta_obj', 'N/A')
            venta_txt = f"$ {venta_obj:.4f} (No ejecutada)"
            compra_numero_txt = trans.get('numcompra', 'N/A')
            historial_box.insert(END, f"Compra: $ {compra:.2f}, numero: {compra_numero_txt} -> Venta: {venta_txt}\n")
        for venta in bot.precios_ventas:
            historial_box.insert(END, f"Venta ejecutada de: $ {venta['compra']:.2f}, numero: {venta['venta_numero']}, a: $ {venta['venta']:.2f} | Ganancia: $ {venta['ganancia']:.4f}\n")

    def alternar_bot():
        global limpiar_visible
        if not bot.running:
            bot.iniciar()
            bot.loop(actualizar_ui, ventana_principal.after)
            reproducir_sonido("Sounds/soundinicio.wav")
            actualizar_ui()
            boton_estado.config(text="Detener") 
            boton_limpiar.grid_remove()       
        else:
            bot.detener()
            reproducir_sonido("Sounds/detner.wav")
            boton_estado.grid_remove()
            limpiar_visible = True
            boton_limpiar.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

    # Función para inicializar los valores iniciales
    def inicializar_valores_iniciales(self):
        if bot.precio_actual is not None:
            valores_iniciales["precio_actual"] = bot.precio_actual
        if bot.usdt_mas_btc is not None:
            valores_iniciales["balance"] = bot.usdt_mas_btc
        if bot.varCompra is not None:
            valores_iniciales["desde_ult_comp"] = bot.varCompra
        if bot.varVenta is not None:
            valores_iniciales["ult_vent"] = bot.varVenta
        if bot.var_inicio is not None:
            valores_iniciales["variacion_desde_inicio"] = bot.var_inicio  
        

    def limpiar_bot(self):
        global limpiar_visible
        
        if not bot.running:
            reproducir_sonido("Sounds/soundlimpiara.wav")
            from codigo_principala import TradingBot  
            bot = TradingBot()
            bot.log_fn = log_en_consola  # Vincula el callback de log a la nueva instancia
            valores_iniciales.clear()
            bot.actualizar_balance()
            actualizar_ui()            
            log_en_consola("🔄 Khazâd reiniciado")
              
            # Luego de limpiar, ocultamos Limpiar y volvemos a mostrar el botón de Iniciar
            limpiar_visible = False
            boton_limpiar.grid_remove()
            boton_estado.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
            boton_estado.config(text="Iniciar")
            
        else:
            boton_limpiar.grid_remove()

    

    inicializar_valores_iniciales()   
    actualizar_ui()     
    ventana_principal.mainloop()

    def run(self):       
        self.root.mainloop()
