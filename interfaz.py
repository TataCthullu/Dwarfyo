# © 2025 Khazâd Trading Bot
# Todos los derechos reservados.

from tkinter import *
from tkinter.scrolledtext import ScrolledText
from utils import reproducir_sonido, detener_sonido_y_cerrar
from codigo_principala import TradingBot
from calculador import CalculatorWindow
from PIL import ImageGrab
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor
#from tkinter import TclError
#import os
from animation_mixin import AnimationMixin
from decimal import Decimal, InvalidOperation

class BotInterface(AnimationMixin):
    def __init__(self, bot: TradingBot):
         # Main window setup
        self.root = Tk()
        self.root.title("Khazâd")
        self.root.configure(bg="DarkGoldenrod")
        self.root.iconbitmap("imagenes/icokhazad.ico")
        self.root.attributes("-alpha", 0.93)
        # initialize bot and clear only ingreso price until started
        self.bot = bot
        self.bot.log_fn = self.log_en_consola
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.config_ventana = None
        self._font_normal = ("Artford", 14)
        self._font_nd = ("Tolkien Dwarf Runes", 14) 
        self.initial_usdt = bot.usdt
        self.loop_id = None
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.inv_inic = self.initial_usdt
        # Lista de (StringVar, Label) para los No Data
        self.nd_labels = []

        # UI variables and clear initial values
        self._create_stringvars()         
        self.valores_iniciales = {}
        self.limpiar_visible = False
                
        # Layout
        self._create_frames()
        self._create_info_panel()
        
        self._create_center_panel()
        self._create_right_panel()
        self.historial.tag_configure('venta_tag', foreground='Green')
        self.historial.tag_configure('compra_tag', foreground='SteelBlue')
        self._create_buttons()
        self.reset_stringvars()
        self.actualizar_ui()
        # Baseline for color comparisons
        self.inicializar_valores_iniciales()
        self.init_animation()
               
        self.sound_enabled = True
        self.bot.sound_enabled = True

        # BARRA DE MENÚ
        menubar = Menu(self.root)
        self.config_menu = Menu(menubar, tearoff=0)
        self.config_menu.add_command(label="Silenciar sonido", command=self.toggle_sound)
        self.config_menu.add_command(label="Guardar captura", command=self.save_screenshot)
        menubar.add_cascade(label="Opciones", menu=self.config_menu)
        self.root.config(menu=menubar)
  
    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.bot.sound_enabled = self.sound_enabled

        estado = "🔇 Sonido desactivado" if not self.sound_enabled else "🔊 Sonido activado"
        self.log_en_consola(estado)

        # Actualizamos también el texto del menú:
        nuevo_label = "Activar sonido" if not self.sound_enabled else "Silenciar sonido"
        # entryconfig(0, ...) actúa sobre la primera entrada que creamos en config_menu
        self.config_menu.entryconfig(0, label=nuevo_label)
       
    def save_screenshot(self):
        x = self.root.winfo_rootx()
        y = self.root.winfo_rooty()
        w = x + self.root.winfo_width()
        h = y + self.root.winfo_height()
        img = ImageGrab.grab(bbox=(x, y, w, h))
        ruta = filedialog.asksaveasfilename(defaultextension=".png",
                                           filetypes=[("PNG","*.png")])
        if ruta:
            img.save(ruta)
            self.log_en_consola(f"📸 Captura guardada en: {ruta}")

    def _create_stringvars(self):
        # Display and config variables
        self.precio_act_var = StringVar()
        self.balance_var = StringVar()
        self.start_time_str = StringVar()
        self.runtime_str = StringVar()
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
        self.hold_usdt_var = StringVar()
        self.hold_btc_var = StringVar()
        self.var_total_str = StringVar() 
        
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
            Label(row, text=label, bg="DarkGoldenrod", font=self._font_normal, fg="DarkSlateGray").pack(side=LEFT)
            lbl = Label(row, textvariable=var, bg="DarkGoldenrod", font=self._font_normal, fg="Gold"); lbl.pack(side=LEFT)
            # guardamos el par para pintar runas más tarde
            self.nd_labels.append((var, lbl))
            if key:
                self.info_labels[key] = lbl

        add("Usdt + Btc:", self.balance_var, "balance") 
        add("% Variación Total:", self.var_total_str, "variacion_total") 
        add("Variacion desde inicio:", self.var_inicio_str, "variacion_desde_inicio")  
        add("Precio actual Btc/Usdt:", self.precio_act_var, "precio_actual")
        add("Precio de ingreso:", self.precio_de_ingreso_str, "desde_inicio")
        add("Ganancia neta en Usdt:", self.ganancia_total_str, "ganancia_neta")
        add("Fecha de inicio:", self.start_time_str, "start_time")
        add("Tiempo activo:", self.runtime_str, "runtime")
        add("Hold Btc/Usdt Comparativo:", self.hold_usdt_var, "hold_usdt")
        add("Hold Btc Comparativo:", self.hold_btc_var, "hold_btc")
        add("Btc Disponible:", self.cant_btc_str, "btc_dispo")
        add("Btc en Usdt:", self.btc_en_usdt, "btcnusdt")
        add("% Desde ultima compra:", self.varpor_set_compra_str, "desde_ult_comp")
        add("% Desde ultima venta:", self.varpor_set_venta_str, "ult_vent")
        add("Compras Realizadas:", self.compras_realizadas_str, "compras_r")
        add("Ventas Realizadas:", self.ventas_realizadas_str, "ventas_r")      
        add("Compras fantasma:", self.cont_compras_fantasma_str, "compras_f")
        add("Ventas fantasma:", self.cont_ventas_fantasma_str, "ventas_f")
        add("Ghost Ratio:", self.ghost_ratio_var, "ghost_ratio")

        
            
    def _create_center_panel(self):
        self.center_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.center_frame.grid(row=0, column=1, sticky="nsew")

        def add(label, var, key=None):
            row = Frame(self.center_frame, bg="DarkGoldenrod"); row.pack(anchor="w")
            Label(row, text=label, bg="DarkGoldenrod", font=self._font_normal, fg="DarkSlategray").pack(side=LEFT)
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
        self.historial = ScrolledText(self.right_frame, bg="Goldenrod", font=self._font_normal)
        self.historial.grid(row=0, column=0, sticky="e", padx=2, pady=2)

        # Consola abajo
        self.consola = ScrolledText(self.right_frame, bg="Goldenrod", font=self._font_normal)
        self.consola.grid (row=1, column=0, sticky="e", padx=2, pady=2)

    def _create_buttons(self):
        self.buttons_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.buttons_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        self.btn_inicio = Button(self.buttons_frame, text="Iniciar", command=self.toggle_bot, bg="Goldenrod", font=self._font_normal, fg="PaleGoldenRod")
        self.btn_inicio.grid(row=0, column=0, sticky="ew", padx=2)
        self.btn_limpiar = Button(self.buttons_frame, text="Limpiar", command=self.clear_bot, bg="Goldenrod", font=self._font_normal, fg="PaleGoldenRod")
        btn_calc = Button(self.buttons_frame, text="Calculadora", command=self.open_calculator, bg="Goldenrod", font=self._font_normal, fg="PaleGoldenRod")
        btn_calc.grid(row=0, column=2, sticky="e", padx=2)
        self.btn_confi = Button(self.center_frame, text="Configurar Operativa", bg="Goldenrod", command=self.abrir_configuracion_subventana, font=self._font_normal, fg="PaleGoldenRod")
        self.btn_confi.pack()
        self.btn_limpiar.grid(row=0, column=1, sticky="ew", padx=2)
        self.btn_limpiar.grid_remove()

    def _thread_callback(self, future):
        if future.cancelled():
            return
        if exc := future.exception():
            # Lo logueamos en la UI
            if self.root.winfo_exists():
                self.root.after(0, lambda:
                    self.log_en_consola(f"⚠️ Excepcion en hilo: {exc}")
                )
    
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
        except InvalidOperation:
            return 0  # o lo que quieras como fallback

    def abrir_configuracion_subventana(self):
        self.config_ventana = Toplevel(self.root)
        self.config_ventana.title("Configuracion de operativa")
        self.config_ventana.configure(bg="DarkGoldenRod")

        def cerrar_config():
            detener_sonido_y_cerrar(self.config_ventana)
            self.config_ventana.destroy()
            self.config_ventana = None
             

        self.config_ventana.protocol("WM_DELETE_WINDOW", cerrar_config)
        if self.sound_enabled:
            reproducir_sonido("Sounds/antorchab.wav")

        campos = [
            ("% Desde compra, para compra: %", self.bot.porc_desde_compra),
            ("% Desde venta, para compra: %", self.bot.porc_desde_venta),
            ("% Para venta, desde compra: %", self.bot.porc_profit_x_venta),
            ("% A invertir por operaciones: %", self.bot.porc_inv_por_compra),
            ("Total Usdt: $", self.bot.usdt),
        ]
        entries = []

        for etiqueta, valor in campos:
            frame = Frame(self.config_ventana, bg="DarkGoldenRod")
            frame.pack(fill=X, pady=4, padx=8)
            Label(frame, text=etiqueta, bg="DarkGoldenRod",
                font=self._font_normal, fg="DarkSlateGray").pack(side=LEFT)
            var = StringVar(value=str(valor))
            Entry(frame, textvariable=var, bg="DarkGoldenRod",
                font=self._font_normal, fg="Gold").pack(side=LEFT, padx=6)
            entries.append(var)

        def guardar_config():
            try:
                # 1) Leemos la cadena exacta
                txt_compra = entries[0].get().strip()   # p.e. "0.0003234" o "5"
                txt_venta  = entries[1].get().strip()
                txt_profit  = entries[2].get().strip()
                txt_porc_inv = entries[3].get().strip()
                txt_usdt = entries[4].get().strip()
                txt_fixed_buyer = entries[4].get().strip()

                # 2) Construimos Decimal desde cadena (sin pasar por float)
                porc_compra = Decimal(txt_compra)
                porc_venta  = Decimal(txt_venta)
                porc_profit  = Decimal(txt_profit)
                porc_inv = Decimal(txt_porc_inv)
                usdtinit = Decimal(txt_usdt)
                fixed_b = Decimal(txt_fixed_buyer)


                # 3) Asignamos al bot (para los cálculos internos)
                self.bot.porc_desde_compra = porc_compra
                self.bot.porc_desde_venta = porc_venta
                self.bot.porc_profit_x_venta = porc_profit
                self.bot.porc_inv_por_compra = porc_inv
                self.bot.usdt = usdtinit
                self.bot.fixed_buyer = fixed_b   

                self.porc_desde_compra_str.set(f"% {txt_compra}")
                self.porc_desde_venta_str.set(f"% {txt_venta}")
                self.porc_objetivo_venta_str.set(f"% {txt_profit}")
                self.inv_por_compra_str.set(f"% {txt_porc_inv}")
                self.cant_usdt_str.set(f"% {txt_usdt}")
                self.fixed_buyer_str.set(f"% {txt_fixed_buyer}")
             

                self.log_en_consola("Configuracion actualizada")
                self.log_en_consola("-------------------------")
                cerrar_config()

            except InvalidOperation:
                self.log_en_consola("Error: ingresa valores numericos validos.")

        Button(self.config_ventana, text="Guardar",
            bg="Goldenrod", command=guardar_config,
            font=self._font_normal, fg="PaleGoldenRod").pack(pady=8)

    def toggle_bot(self):            
            if self.bot.running:
                self.bot.detener()
                if self.sound_enabled:
                   reproducir_sonido("Sounds/detner.wav")
                
                self.btn_inicio.grid_remove()  # Oculta el botón de estado               
                self.btn_limpiar.grid()        # Muestra el botón limpiar
                self.btn_confi.pack_forget()

            else:
                self.btn_confi.pack_forget()
                self.bot.iniciar()   
                if self.sound_enabled:             
                    reproducir_sonido("Sounds/soundinicio.wav")
                
                self.guard_label.configure(image=self.guard_open_frames[0])
                self.inicializar_valores_iniciales()
                self.btn_inicio.config(text="Detener")
                self.btn_limpiar.grid_remove()
                self.btn_confi.pack()
                self._loop()

    def clear_bot(self):
        if not self.bot.running:
            if self.sound_enabled:
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
            self.init_animation()
            self.actualizar_ui()
            
            # Restaurar botones
            self.btn_confi.pack()
            self.btn_limpiar.grid_remove()
            self.btn_inicio.grid(row=0, column=0, sticky="ew", padx=2)
            self.btn_inicio.config(text="Iniciar")
        else:
            self.btn_limpiar.grid_remove()

    def _on_close(self):
        # 1) cancelar el after programado
        if self.loop_id is not None:
            try:
                self.root.after_cancel(self.loop_id)
            except Exception:
                pass
        # 2) Detener el executor
        self.executor.shutdown(wait=False, cancel_futures=True)
        # 3) cerrar la ventana
        self.root.destroy()
            
    def _loop(self):
        if not self.bot.running:
            return
        # lanzamos la petición en background  
        future = self.executor.submit(self._fetch_price_async)
        future.add_done_callback(self._thread_callback)

        # programamos la siguiente pasada
        self.loop_id = self.root.after(3000, self._loop)
        
    def _on_price_fetched(self, price):
        try:
            if not self.root.winfo_exists():
                return
            # 1. Actualiza el precio en el bot
            self.bot.precio_actual = price
            # 2. Ejecuta la lógica de compra/venta
            self.bot.loop()
            # 3. Refresca la interfaz (también bajo try/except)
            self.actualizar_ui()
        except InvalidOperation:
            # si la ventana ya fue destruida o hubo otro error, simplemente ignoramos
            pass

    def _fetch_price_async(self):
        try:
            # Intentamos recuperar el ticker en el hilo de fondo
            ticker = self.bot.exchange.fetch_ticker('BTC/USDT')
            price = ticker['last']
        except InvalidOperation as e:
            # Re-lanzamos la excepción para que future.exception() la recoja
            pass

        # Si todo fue bien, pasamos el precio al hilo principal
        if self.root.winfo_exists():
            self.root.after(0, lambda: self._on_price_fetched(price))

    def actualizar_ui(self):
        try:
            if self.bot.running:
                # ——— Detectar reconexión de Internet ———
                prev_price = getattr(self.bot, 'precio_actual', None)
                new_price  = self.bot._fetch_precio()
                # Si antes no había precio y ahora sí, reiniciamos todo el loop
                if prev_price is None and new_price is not None:
                    self.log_en_consola("🔄 Conexion restablecida, Khazad reactivado.")
                    self.log_en_consola("--------------------------------------------")
                    #self._loop()
                # Actualizamos el balance con el precio (que ya cargamos)
                self.bot.actualizar_balance()
                precio = self.bot.precio_actual
                self.precio_act_var.set(f"$ {precio}" if precio else "z")
                self.cant_btc_str.set(f"₿ {self.bot.btc}")
                self.cant_usdt_str.set(f"$ {self.bot.usdt}")
                self.balance_var.set(f"$ {self.bot.usdt_mas_btc}" if self.bot.precio_actual else "0")
                self.btc_en_usdt.set(f"$ {self.bot.btc_usdt}" if self.bot.precio_actual else "z")
                self.precio_de_ingreso_str.set(f"$ {self.bot.precio_ingreso}" if self.bot.precio_ingreso else "z")
                self.inv_por_compra_str.set(f"% {self.bot.porc_inv_por_compra}")
                self.varpor_set_compra_str.set(f"% {self.bot.varCompra}" if self.bot.varCompra else "z")
                self.varpor_set_venta_str.set(f"% {self.bot.varVenta}" if self.bot.varVenta else "z")
                self.porc_desde_compra_str.set(f"% {self.bot.porc_desde_compra}")
                self.porc_desde_venta_str.set(f"% {self.bot.porc_desde_venta}")
                self.var_inicio_str.set(f"% {self.bot.var_inicio}" if self.bot.var_inicio else "z")
                self.fixed_buyer_str.set(f"$ {self.bot.fixed_buyer}")
                self.ganancia_total_str.set(f"$ {self.bot.total_ganancia}" if self.bot.total_ganancia else "z")
                self.cont_compras_fantasma_str.set(str(self.bot.contador_compras_fantasma) if self.bot.contador_compras_fantasma else "z")
                self.cont_ventas_fantasma_str.set(str(self.bot.contador_ventas_fantasma) if self.bot.contador_ventas_fantasma else "z")
                self.porc_objetivo_venta_str.set(f"% {self.bot.porc_profit_x_venta}" if self.bot.porc_profit_x_venta else "z")
                self.ghost_ratio_var.set(f"{self.bot.calcular_ghost_ratio()}" if self.bot.calcular_ghost_ratio() else "z")
                self.compras_realizadas_str.set(str(self.bot.contador_compras_reales) if self.bot.contador_compras_reales else "z")
                self.ventas_realizadas_str.set(str(self.bot.contador_ventas_reales) if self.bot.contador_ventas_reales else "z")               
                self.start_time_str.set(self.bot.get_start_time_str())
                self.runtime_str.set(self.bot.get_runtime_str())

                self.actualizar_historial_consola()                
                self.actualizar_color("precio_actual", self.bot.precio_actual)
                self.actualizar_color("balance", self.bot.usdt_mas_btc)
                self.actualizar_color("desde_ult_comp", self.bot.varCompra)
                self.actualizar_color("ult_vent", self.bot.varVenta)
                self.actualizar_color("variacion_desde_inicio", self.bot.var_inicio)
                

                # Total variation from initial balance
                if self.inv_inic:
                    delta = (self.bot.usdt_mas_btc - self.inv_inic) / self.inv_inic * 100
                    self.var_total_str.set(f"{delta}%")
                else:
                    self.var_total_str.set("z")
                self.ganancia_total_str.set(f"$ {self.bot.total_ganancia}" if self.bot.total_ganancia else "z")
                # Cálculo Hold USDT
                if self.bot.precio_ingreso and precio:
                    hold_usdt = (self.inv_inic / self.bot.precio_ingreso) * precio
                    self.hold_usdt_var.set(f"$ {hold_usdt}")
                else:
                    self.hold_usdt_var.set("z")
                
                # Cálculo Hold BTC en sats
                if self.bot.precio_ingreso:
                    sats = (self.inv_inic / self.bot.precio_ingreso)
                    self.hold_btc_var.set(f"₿ {float(sats)}")
                else:
                    self.hold_btc_var.set("z")

                # Repintar fuente según valor real o placeholder
                for var, lbl in self.nd_labels:
                    if var.get() == "z":
                        lbl.configure(font=self._font_nd)
                    else:
                        lbl.configure(font=self._font_normal)
             
        except Exception as e:
            print("Error al actualizar la UI:", e)
            pass
            
    def actualizar_historial_consola(self):
        self.historial.delete('1.0', END)
        for t in self.bot.transacciones:
            ts = t.get("timestamp", "")
            self.historial.insert(END, "Compra desde:", 'compra_tag')
            # el resto de la línea en color por defecto
            resto = f" ${t['compra']} -> Id: {t['id']} -> Num: {t['numcompra']} -> Fecha: {ts} -> Objetivo: ${t['venta_obj']}\n"
            self.historial.insert(END, resto)
            id_op = t.get("id")
            
        for v in self.bot.precios_ventas:
            ts = v.get("timestamp", "")
            self.historial.insert(END, "Venta desde:", 'venta_tag')
            resto = f" $ {v['compra']} -> id: {v['id_compra']}, a: $ {v['venta']} | Ganancia: $ {v['ganancia']}, Num: {v['venta_numero']} -> Fecha: {ts}\n"
            self.historial.insert(END, resto)

    def actualizar_color(self, key, valor_actual):
        if valor_actual is None:
            return
        inicial = self.valores_iniciales[key]
        color = "Gold"
        if valor_actual > inicial:
            color = "Green"
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
