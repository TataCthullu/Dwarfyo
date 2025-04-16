
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
        btn = Button(self.center_frame, text="Configurar Operativa", bg="Goldenrod", command=self.abrir_config)
        btn.pack(pady=10)

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
        # igual a tu abrir_configuracion_subventana(), pero referenciando self.bot
        pass

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

    def actualizar_ui(self):
        # exactamente tu lógica de actualizar_ui, pero usando self.
        pass

    def actualizar_color(self, key, val):
        # tu lógica de colores
        pass

    def log_en_consola(self, msg):
        self.consola.insert(END, msg + "\n")
        self.consola.see(END)

    def _inicializar_baseline(self):
        # llena valores_iniciales con bot.precio_actual, bot.balance...
        pass

    def run(self):
        self.root.mainloop()


