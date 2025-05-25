# © 2025 Dungeon Market Trading Bot
# Todos los derechos reservados.

from tkinter import *
from tkinter.scrolledtext import ScrolledText
from utils import reproducir_sonido, detener_sonido_y_cerrar
from codigo_principala import TradingBot
from calculador import CalculatorWindow
from PIL import ImageGrab, Image, ImageTk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor
from animation_mixin import AnimationMixin
from decimal import Decimal, InvalidOperation

class BotInterfaz(AnimationMixin):
    def __init__(self, bot: TradingBot):
         # Main window setup
        self.root = Tk()
        self.root.title("Dungeon Market")
        
        self.root.configure(bg="white")
        self.root.iconbitmap("imagenes/icokhazad.ico")
        self.root.attributes("-alpha", 0.93)
        # initialize bot and clear only ingreso price until started
        self.bot = bot
        self.bot.log_fn = self.log_en_consola
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.config_ventana = None
        self._font_normal = ("LondonBetween", 15)
        self._font_nd = ("Tolkien Dwarf Runes", 14) 
        self.loop_id = None
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        # Lista de (StringVar, Label) para los No Data
        self.nd_canvas = []
        # UI variables and clear initial values
        self._create_stringvars()         
        self.valores_iniciales = {}
        self.limpiar_visible = False
        self.runa_image = ImageTk.PhotoImage(Image.open("imagenes/deco/rune_tomb.png").resize((28, 28), Image.ANTIALIAS))


        # Frames
        self.left_panel()
        self.center_panel()
        self.right_panel()
        self.right_panel_b()
        self.animation_panel()
        self.various_panel()
        self.historial.tag_configure('venta_tag', foreground='Green')
        self.historial.tag_configure('compra_tag', foreground='SteelBlue')
        
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

    def rellenar_mosaico(self, canvas, image_path, escala=1):

        # Cargar imagen original
        imagen_original = Image.open(image_path)
        ancho, alto = imagen_original.size
        imagen_redimensionada = imagen_original.resize((ancho * escala, alto * escala), Image.NEAREST)
        imagen = ImageTk.PhotoImage(imagen_redimensionada)

        # Guardar referencia en el canvas (evita que se borre de memoria)
        if not hasattr(canvas, 'imagenes'):
            canvas.imagenes = []
        canvas.imagenes.append(imagen)

        # Obtener tamaño del canvas
        width = int(canvas['width'])
        height = int(canvas['height'])

        # Dibujar la imagen en mosaico
        for x in range(0, width, imagen.width()):
            for y in range(0, height, imagen.height()):
                canvas.create_image(x, y, image=imagen, anchor='nw')    
    
        
    #Frames
    def left_panel(self):
        self.left_frame = Frame(self.root)
        self.left_frame.place(x=0, y=0, width=600, height=900)

        self.canvas_uno = Canvas(self.left_frame, width=600, height=900, highlightthickness=0)
        self.canvas_uno.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_uno, "imagenes/decoa/wall/snake_1.png", escala=2)

        y_offset = 10
        row_height = 30

        if not hasattr(self, 'info_canvas'):
            self.info_canvas = {}
        if not hasattr(self, 'nd_canvas'):
            self.nd_canvas = []

        def add(label_text, var, key=None):
            nonlocal y_offset
            # 1) etiqueta fija
            lbl_id = self.canvas_uno.create_text(20, y_offset,
                                                 text=label_text,
                                                 fill="White",
                                                 font=self._font_normal,
                                                 anchor="nw")
            # 2) medir y posicionar valor a la derecha
            bbox = self.canvas_uno.bbox(lbl_id)
            x_val = bbox[2] + 8
            txt_id = self.canvas_uno.create_text(x_val, y_offset,
                                                 text=var.get(),
                                                 fill="gold",
                                                 font=self._font_normal,
                                                 anchor="nw")
            self.nd_canvas.append((var, self.canvas_uno, txt_id, x_val, y_offset))
            if key:
                self.info_canvas[key] = (self.canvas_uno, txt_id)
                y_offset += row_height

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

  
    def center_panel(self):
        self.center_frame = Frame(self.root)
        self.center_frame.place(x=600, y=0, width=500, height=450)

        self.canvas_center = Canvas(self.center_frame, width=500, height=450, highlightthickness=0)
        self.canvas_center.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_center, "imagenes/decoa/wall/wall_vines_1.png", escala=2)

        y_offset = 10
        row_height = 30

        def add(label_text, var, key=None):
            nonlocal y_offset
            # 1) etiqueta fija
            lbl_id = self.canvas_center.create_text(20, y_offset,
                                                    text=label_text,
                                                    fill="White",
                                                    font=self._font_normal,
                                                    anchor="nw")
            # 2) medir y posicionar valor
            bbox = self.canvas_center.bbox(lbl_id)
            x_val = bbox[2] + 8
            txt_id = self.canvas_center.create_text(x_val, y_offset,
                                                    text=var.get(),
                                                    fill="gold",
                                                    font=self._font_normal,
                                                    anchor="nw")
            self.nd_canvas.append((var, self.canvas_center, txt_id, x_val, y_offset))
            if key:
                self.info_canvas[key] = (self.canvas_center, txt_id)
            y_offset += row_height

        add("% Objetivo de venta, desde compra:", self.porc_objetivo_venta_str, "porc_obj_venta")
        add("Usdt Disponible:", self.cant_usdt_str, "usdt")
        add("% Desde compra, para compra:", self.porc_desde_compra_str, "porc_desde_compra")
        add("% Desde venta, para compra:", self.porc_desde_venta_str, "porc_desde_venta")
        add("% Por operacion:", self.inv_por_compra_str, "porc_inv_por_compra")
        add("% Fijo para inversion:", self.fixed_buyer_str, "fixed_buyer")


    def right_panel(self):
        self.right_frame = Frame(self.root)
        self.right_frame.place(x=1100, y=0, width=850, height=450)

        self.canvas_right = Canvas(self.right_frame, width=850, height=450, highlightthickness=0)
        self.canvas_right.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_right, "imagenes/decoa/wall/relief_0.png", escala=2)

        self.historial = ScrolledText(self.canvas_right, bg="Gray", relief="flat", bd=0, font=self._font_normal)

        self.historial.place(x=50, y=50, width=750, height=350)

    def right_panel_b(self):
        self.right_frame_b = Frame(self.root)
        self.right_frame_b.place(x=1300, y=450, width=650, height=650)

        self.canvas_right_b = Canvas(self.right_frame_b, width=650, height=650, highlightthickness=0)
        self.canvas_right_b.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_right_b, "imagenes/decoa/wall/grass_full_new.png", escala=2)

        self.consola = ScrolledText(self.canvas_right_b, bg="DarkGoldenrod", relief="flat", bd=0, font=self._font_normal)
        self.consola.place(x=20, y=20, width=560, height=370)

    def animation_panel(self):
        self.animation_frame = Frame(self.root)
        self.animation_frame.place(x=600, y=450, width=700, height=450)

        self.canvas_animation = Canvas(self.animation_frame, width=700, height=450, highlightthickness=0)
        self.canvas_animation.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_animation, "imagenes/decoa/wall/grass_flowers_yellow_1_old.png", escala=2)

    def various_panel(self):
        self.various_frame = Frame(self.root)
        self.various_frame.place(x=0, y=900, width=2000, height=100)

        self.canvas_various = Canvas(self.various_frame, width=2000, height=100, highlightthickness=0)
        self.canvas_various.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_various, "imagenes/decoa/wall/mesh_3_old.png", escala=2)

        # Crear botones pero solo mostrar "Iniciar" al principio
        self.btn_inicio = Button(self.canvas_various, text="Iniciar", command=self.toggle_bot, bg="Goldenrod", font=self._font_normal, fg="PaleGoldenRod")
        self.btn_inicio_id = self.canvas_various.create_window(100, 50, window=self.btn_inicio)

        self.btn_limpiar = Button(self.canvas_various, text="Limpiar", command=self.clear_bot, bg="Goldenrod", font=self._font_normal, fg="PaleGoldenRod")
        self.btn_limpiar_id = self.canvas_various.create_window(250, 50, window=self.btn_limpiar)
        self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')

        self.btn_calc = Button(self.canvas_various, text="Calculadora", command=self.open_calculator, bg="Goldenrod", font=self._font_normal, fg="PaleGoldenRod")
        self.canvas_various.create_window(400, 50, window=self.btn_calc)

        self.btn_confi = Button(self.canvas_various, text="Configurar Operativa", command=self.abrir_configuracion_subventana, bg="Goldenrod", font=self._font_normal, fg="PaleGoldenRod")
        self.btn_confi_id = self.canvas_various.create_window(600, 50, window=self.btn_confi)

    def toggle_bot(self):
        if self.bot.running:
            self.bot.detener()
            if self.sound_enabled:
                reproducir_sonido("Sounds/detner.wav")

            self.canvas_various.itemconfigure(self.btn_inicio_id, state='hidden')
            self.canvas_various.itemconfigure(self.btn_limpiar_id, state='normal')
            self.canvas_various.itemconfigure(self.btn_confi_id, state='hidden')
        else:
            self.bot.iniciar()
            if self.sound_enabled:
                reproducir_sonido("Sounds/soundinicio.wav")

            self.guard_label.configure(image=self.guard_open_frames[0])
            self.inicializar_valores_iniciales()

            self.btn_inicio.config(text="Detener")
            self.canvas_various.itemconfigure(self.btn_inicio_id, state='normal')
            self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')
            self.canvas_various.itemconfigure(self.btn_confi_id, state='normal')

            self._loop()

    def clear_bot(self):
        if self.bot.running:
            return  # si el bot está activo no limpiamos

        if self.sound_enabled:
            reproducir_sonido("Sounds/limpiar.wav")

        # 1) Limpiar textos
        self.consola.delete('1.0', END)
        self.historial.delete('1.0', END)

        # 2) Reiniciar lógica del bot
        self.bot.reiniciar()
        self.bot.log_fn = self.log_en_consola
        self.bot.sound_enabled = self.sound_enabled

        # 3) Reset all StringVars (incluye btc_en_usdt y var_total_str)
        self.inicializar_valores_iniciales()
        for attr, val in vars(self).items():
            if isinstance(val, StringVar):
                val.set("")
        # repintar runas y colores
        self.reset_stringvars()
        self.reset_colores()
        self.init_animation()

        # 6) Restaurar botones
        self.btn_inicio.config(text="Iniciar")
        self.canvas_various.itemconfigure(self.btn_inicio_id, state='normal')
        self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')
        self.canvas_various.itemconfigure(self.btn_confi_id, state='normal')


        
       

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
            return Decimal(valor)           
        except InvalidOperation:
            return 0  # o lo que quieras como fallback
        
    def reset_stringvars(self):
        for i, entry in enumerate(self.nd_canvas):

            var, canvas, item_id, x, y = entry

            valor = var.get().strip() if var.get() else ""

           # ahora usamos la y original
            y_pos = y
            x_pos = x

            if valor in ("", "None", None, "0", "$ 0", "% 0", "₿ 0"):

               if canvas.type(item_id) == "image":
                    continue



               canvas.delete(item_id)
               image_id = canvas.create_image(x_pos, y_pos, image=self.runa_image, anchor='nw')
               self.nd_canvas[i] = (var, canvas, image_id, x, y)
            else:

                if canvas.type(item_id) == "text":
                    canvas.itemconfig(item_id, text=valor)
                else:
                    # reemplazar imagen por texto

                   canvas.delete(item_id)
                   text_id = canvas.create_text(
                       x_pos, y_pos,
                       text=valor,
                       fill="gold",
                       font=self._font_normal,
                       anchor="nw"
                   )
                   self.nd_canvas[i] = (var, canvas, text_id, x, y)



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
            ("Total Usdt: $", self.bot.inv_inic)
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
                txt_usdt_inic = entries[4].get().strip()
                

                # 2) Construimos Decimal desde cadena (sin pasar por Decimal)
                porc_compra = Decimal(txt_compra)
                porc_venta  = Decimal(txt_venta)
                porc_profit  = Decimal(txt_profit)
                porc_inv = Decimal(txt_porc_inv)
                usdtinit = Decimal(txt_usdt_inic)
                


                # 3) Asignamos al bot (para los cálculos internos)
                self.bot.porc_desde_compra = porc_compra
                self.bot.porc_desde_venta = porc_venta
                self.bot.porc_profit_x_venta = porc_profit
                self.bot.porc_inv_por_compra = porc_inv
                self.bot.inv_inic = usdtinit

                self.bot.fixed_buyer = (
                    self.bot.inv_inic * self.bot.porc_inv_por_compra / Decimal('100')
                )
   

                """self.porc_desde_compra_str.set(f"% {txt_compra}")
                self.porc_desde_venta_str.set(f"% {txt_venta}")
                self.porc_objetivo_venta_str.set(f"% {txt_profit}")
                self.inv_por_compra_str.set(f"% {txt_porc_inv}")
                self.cant_usdt_str.set(f"% {txt_usdt_inic}")
                self.fixed_buyer_str.set(f"% {txt_fixed_buyer}")"""
             

                self.log_en_consola("Configuracion actualizada")
                self.log_en_consola("-------------------------")
                cerrar_config()

            except (InvalidOperation, IndexError):
                self.log_en_consola("Error: ingresa valores numericos validos.")

        Button(self.config_ventana, text="Guardar",
            bg="Goldenrod", command=guardar_config,
            font=self._font_normal, fg="PaleGoldenRod").pack(pady=8)

    """def toggle_bot(self):            
        if self.bot.running:
            self.bot.detener()
            if self.sound_enabled:
                reproducir_sonido("Sounds/detner.wav")
            
            self.btn_inicio.pack_forget()
            self.btn_limpiar.pack(side=LEFT)
            self.btn_confi.place_forget() 
        else:
            self.bot.iniciar()   
            if self.sound_enabled:
                reproducir_sonido("Sounds/soundinicio.wav")

            self.guard_label.configure(image=self.guard_open_frames[0])
            self.inicializar_valores_iniciales()

            self.btn_inicio.config(text="Detener")
            self.btn_inicio.pack(side=LEFT)
            self.btn_limpiar.pack_forget()
            
            self._loop()


    def clear_bot(self):
        if not self.bot.running:
            if self.sound_enabled:
                reproducir_sonido("Sounds/limpiar.wav")
            
            # Limpiar UI
            self.consola.delete('1.0', END)
            self.historial.delete('1.0', END)
            self.bot.reiniciar()
            self.inicializar_valores_iniciales()
            self.reset_stringvars()
            self.reset_colores()
            self.init_animation()
            self.actualizar_ui()

            # Restaurar botones
            self.btn_inicio.config(text="Iniciar")
            self.btn_inicio.pack(side=LEFT)
            self.btn_limpiar.pack_forget()
            self.btn_confi.place(x=50, y=210)"""


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

    def format_var(self, valor, simbolo=""):
        if valor is None:
            return ""
        try:
            if isinstance(valor, (int, float, Decimal)) and valor == 0:
                return ""
            return f"{simbolo} {valor}"
        except:
            return ""
        

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

                   
                # Actualizamos el balance con el precio (que ya cargamos)
                self.bot.actualizar_balance()
                
                precio = self.bot.precio_actual
                self.precio_act_var.set(self.format_var(precio, "$"))
                self.cant_btc_str.set(self.format_var(self.bot.btc, "₿"))
                self.cant_usdt_str.set(self.format_var(self.bot.usdt, "$"))
                self.balance_var.set(self.format_var(self.bot.usdt_mas_btc, "$"))
                self.btc_en_usdt.set(self.format_var(self.bot.btc_usdt, "$"))
                self.precio_de_ingreso_str.set(self.format_var(self.bot.precio_ingreso, "$"))
                self.inv_por_compra_str.set(self.format_var(self.bot.porc_inv_por_compra, "%"))
                self.varpor_set_compra_str.set(self.format_var(self.bot.varCompra, "%"))
                self.varpor_set_venta_str.set(self.format_var(self.bot.varVenta, "%"))
                self.porc_desde_compra_str.set(self.format_var(self.bot.porc_desde_compra, "%"))
                self.porc_desde_venta_str.set(self.format_var(self.bot.porc_desde_venta, "%"))
                self.var_inicio_str.set(self.format_var(self.bot.var_inicio, "%"))
                self.fixed_buyer_str.set(self.format_var(self.bot.fixed_buyer, "$"))
                self.ganancia_total_str.set(self.format_var(self.bot.total_ganancia, "$"))
                self.cont_compras_fantasma_str.set(self.format_var(self.bot.contador_compras_fantasma))
                self.cont_ventas_fantasma_str.set(self.format_var(self.bot.contador_ventas_fantasma))
                self.porc_objetivo_venta_str.set(self.format_var(self.bot.porc_profit_x_venta, "%"))
                self.ghost_ratio_var.set(self.format_var(self.bot.calcular_ghost_ratio()))
                self.compras_realizadas_str.set(self.format_var(self.bot.contador_compras_reales))
                self.ventas_realizadas_str.set(self.format_var(self.bot.contador_ventas_reales))
                self.start_time_str.set(self.bot.get_start_time_str() or "")
                self.runtime_str.set(self.bot.get_runtime_str() or "")


                

                self.actualizar_historial_consola()                
                # — Calcular y pintar variación total + colores de todos
                var_tot = self.bot.variacion_total()
                self.var_total_str.set(f"% {var_tot}" if var_tot else "")
                self.actualizar_color("precio_actual", self.bot.precio_actual)
                self.actualizar_color("balance", self.bot.usdt_mas_btc)
                self.actualizar_color("desde_ult_comp", self.bot.varCompra)
                self.actualizar_color("ult_vent", self.bot.varVenta)
                self.actualizar_color("variacion_desde_inicio", self.bot.var_inicio)
                self.actualizar_color("variacion_total", var_tot)


                # Hold USDT (ya no recibe argumento)
                hold_usdt = self.bot.hold_usdt()
                # formateo fijo, sin exponenciales
                display_hold_usdt = format(hold_usdt, 'f')
                self.hold_usdt_var.set(f"$ {display_hold_usdt}")

                # Hold BTC
                hold_btc = self.bot.hold_btc()
                display_hold_btc = format(hold_btc, 'f')
                self.hold_btc_var.set(f"₿ {display_hold_btc}")

                for idx, (var, canvas, item_id, x, y) in enumerate(self.nd_canvas):
                    texto = var.get().strip()
                    if texto:
                        # Mostrar texto
                        if canvas.type(item_id) != "text":
                            canvas.delete(item_id)
                            nid = canvas.create_text(x, y, text=texto,
                                                     fill="gold", font=self._font_normal, anchor="nw")
                            self.nd_canvas[idx] = (var, canvas, nid, x, y)
                        else:
                            canvas.itemconfig(item_id, text=texto)
                    else:
                        # Mostrar runa
                        if canvas.type(item_id) != "image":
                            canvas.delete(item_id)
                            iid = canvas.create_image(x, y, image=self.runa_image, anchor="nw")
                            self.nd_canvas[idx] = (var, canvas, iid, x, y)

                
                            
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
        inicial = self.valores_iniciales.get(key, 0)
        color = "Gold"
        if valor_actual > inicial:
            color = "Green"
        elif valor_actual < inicial:
            color = "Crimson"

        ci = self.info_canvas.get(key)
        if ci:
            canvas, item_id = ci
            canvas.itemconfig(item_id, fill=color)



    def reset_colores(self):
        for canvas, item_id in self.info_canvas.values():
            try:
                canvas.itemconfig(item_id, fill="Gold")
            except TclError:
                pass

        
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
            'variacion_desde_inicio': self.bot.var_inicio,
            'variacion_total': 0
        }

    def run(self):
        self.root.mainloop()
