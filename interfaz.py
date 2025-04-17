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
        self.info_labels = {}

    

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
        Button(self.center_frame, text="Configurar Operativa", bg="Goldenrod", command=self.abrir_config).pack(pady=10)

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

    def abrir_config(self):
        
        cw = Toplevel(self.root); cw.title("Configuración de operativa"); cw.configure(bg="DarkGoldenrod")
        cw.protocol("WM_DELETE_WINDOW", lambda: detener_sonido_y_cerrar(cw))
        reproducir_sonido("Sounds/antorcha.wav")
        fields = [
            ("% Desde compra:", 'porc_desde_compra', self.porc_desde_compra_str),
            ("% Desde venta:", 'porc_desde_venta', self.porc_desde_venta_str),
            ("Profit venta (%):", 'porc_profit_x_venta', self.porc_objetivo_venta_str),
            ("% Inversión:", 'porc_inv_por_compra', self.inv_por_compra_str),
            ("Total USDT:", 'usdt', self.cant_usdt_str)
        ]
        for txt, attr, var in fields:
            r = Frame(cw, bg="DarkGoldenrod"); r.pack(fill=X, pady=5)
            Label(r, text=txt, bg="DarkGoldenrod", font=("CrushYourEnemies",12)).pack(side=LEFT)
            Entry(r, textvariable=var, font=("CrushYourEnemies",12), bg="Gold").pack(side=LEFT, padx=5)
        def save():
            try:
                for _, attr, var in fields:
                    v = var.get().replace('%','').replace('$','').strip()
                    setattr(self.bot, attr, float(v))
                
                reproducir_sonido("Sounds/soundcompra.wav")
                cw.destroy()
            except:
                print("Valores inválidos")
        Button(cw, text="Guardar", bg="Goldenrod", command=save).pack(pady=10)

    def toggle_bot(self):
        if not self.bot.running:
            self.bot.iniciar()
            #self.bot.precio_ingreso = self.bot.precio_actual
            reproducir_sonido("Sounds/soundinicio.wav")
            self.btn_inicio.config(text="Detener"); self.btn_limpiar.grid_remove()
        else:
            self.bot.detener(); reproducir_sonido("Sounds/detner.wav")
            self.btn_inicio.grid_remove(); self.btn_limpiar.grid()

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

    def actualizar_ui(self):
        if not self.root.winfo_exists():
            return

        # Precios y balances
        self._safe_set(self.precio_act_var,     self.bot.precio_actual,     "$ {:.4f}")
        self._safe_set(self.balance_var,         self.bot.usdt_mas_btc,       "$ {:.6f}")
        self._safe_set(self.cant_btc_str,        self.bot.btc,               "₿ {:.6f}")
        self._safe_set(self.cant_usdt_str,       self.bot.usdt,              "$ {:.6f}")
        self._safe_set(self.btc_en_usdt,         self.bot.btc_usdt,          "$ {:.6f}")

        # Variaciones desde última compra/venta
        self._safe_set(self.varpor_set_compra_str, self.bot.varCompra, "% {:.3f}")
        self._safe_set(self.varpor_set_venta_str,  self.bot.varVenta,  "% {:.3f}")

        # Precio de ingreso y variación desde inicio
        if self.bot.precio_ingreso is not None:
            self.precio_de_ingreso_str.set(f"$ {self.bot.precio_ingreso:.4f}")
            self.var_inicio_str.set(f"% {self.bot.varpor_ingreso():.3f}")
        else:
            self.precio_de_ingreso_str.set("N/D")
            self.var_inicio_str.set("N/D")

        # Otras métricas
        self._safe_set(self.ganancia_total_str,      self.bot.total_ganancia,          "$ {:.6f}")
        self._safe_set(self.cont_compras_fantasma_str, self.bot.contador_compras_fantasma, "{}")
        self._safe_set(self.cont_ventas_fantasma_str,  self.bot.contador_ventas_fantasma,  "{}")
        self._safe_set(self.ghost_ratio_var,           self.bot.calcular_ghost_ratio(),    "{:.2f}")
        self._safe_set(self.compras_realizadas_str,    self.bot.contador_compras_reales,   "{}")
        self._safe_set(self.ventas_realizadas_str,     self.bot.contador_ventas_reales,    "{}")
        self._safe_set(self.porc_objetivo_venta_str,   self.bot.porc_profit_x_venta,       "% {:.2f}")
        self._safe_set(self.inv_por_compra_str,        self.bot.porc_inv_por_compra,        "% {:.2f}")
        self._safe_set(self.fixed_buyer_str,           self.bot.fixed_buyer,               "$ {:.2f}")

        # Historial de operaciones
        self.historial.delete('1.0', END)
        for t in self.bot.transacciones:
            self.historial.insert(END, f"Compra: ${t['compra']:.2f} -> Obj venta: ${t['venta_obj']:.2f}\n")
        for v in self.bot.precios_ventas:
            self.historial.insert(END, f"Venta: ${v['venta']:.2f} Ganancia: ${v['ganancia']:.4f}\n")


    def log_en_consola(self, msg):
        self.consola.insert(END, msg+"\n"); self.consola.see(END)

    
    

    def run(self):
        
        self.root.mainloop()
