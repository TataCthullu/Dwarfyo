# © 2025 Dungeon Market Trading Bot
# Todos los derechos reservados.
import tkinter as tk
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
        self.root.config(cursor="@imagenes/deco/cursor/stone_arrow.cur")
        self.root.configure(bg="pink")
        self.root.iconbitmap("imagenes/deco/urand_eternal_torment.png")
        self.root.attributes("-alpha", 0.93)
        # initialize bot and clear only ingreso price until started
        self.bot = bot
        self.was_offline = False
        

        self.bot.log_fn = self.log_en_consola
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.config_ventana = None
        self._font_normal = ("LondonBetween", 16)
        
        self.loop_id = None
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        # Lista de (StringVar, Label) para los No Data
        self.nd_canvas = []
        # UI variables and clear initial values
        self._create_stringvars()         
        self.valores_iniciales = {}
        self.colores_actuales = {}  # key -> "Gold", "Green" o "Crimson"

        self.limpiar_visible = False
        self.runa_image = ImageTk.PhotoImage(Image.open("imagenes/decoa/runes/rune_dis_old.png").resize((35, 35), Image.ANTIALIAS))
        self.valores_a_mostrar = {
            "compras_realizadas": self.bot.contador_compras_reales,
            "ventas_realizadas": self.bot.contador_ventas_reales,
            "compras_fantasma": self.bot.contador_compras_fantasma,
            "ventas_fantasma": self.bot.contador_ventas_fantasma
        }
        
        self.bot.set_formatter(self.format_var)

            

        

        # Frames
        self.left_panel()
        self.center_panel()
        self.right_panel()
        self.right_panel_b()
        self.animation_panel()
        self.various_panel()
        self.init_animation()
        
        
        self.historial.tag_configure('venta_tag', foreground='Green')
        self.historial.tag_configure('compra_tag', foreground='SteelBlue')
        
        
        # —————— Barra de menú unificada ——————
        self.menubar       = tk.Menu(self.root)
        # Estado de vista: 'decimal' o 'float'
        self.display_mode  = tk.StringVar(value='decimal')
        self.float_precision = 2
        # 3) Submenú Vista
        self._crear_menu_vista()
        # Creamos submenu Opciones
        self.config_menu   = tk.Menu(self.menubar, tearoff=0)
        self.config_menu.add_command(label="Silenciar sonido", command=self.toggle_sound)
        self.config_menu.add_command(label="Guardar captura", command=self.save_screenshot)
        self.menubar.add_cascade(label="Opciones", menu=self.config_menu)
        # ¡Solo aquí configuramos el menú completo!
        self.root.config(menu=self.menubar) 

        self.actualizar_ui()
        self._prev_price_ui = self.bot.precio_actual
        # Baseline for color comparisons
        #self.inicializar_valores_iniciales()
        
        self.sound_enabled = True
        self.bot.sound_enabled = True
         
    
    def _crear_menu_vista(self):
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_radiobutton(
            label="Vista Decimal",
            variable=self.display_mode, value='decimal',
            command=self.actualizar_ui  # <-- llamamos actualizar_ui directamente
        )
        view_menu.add_radiobutton(
            label="Float (2 decimales)",
            variable=self.display_mode, value='float',
            command=lambda: self._cambiar_precision_y_actualizar(2)
        )
        view_menu.add_radiobutton(
            label="Float (4 decimales)",
            variable=self.display_mode, value='float',
            command=lambda: self._cambiar_precision_y_actualizar(4)
        )
        self.menubar.add_cascade(label="Vista", menu=view_menu)


    def _cambiar_precision_y_actualizar(self, precision):
        self.float_precision = precision
        self.actualizar_ui()

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
        self.precio_act_str = StringVar()
        self.balance_str = StringVar()
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
        self.hold_usdt_str = StringVar()
        self.hold_btc_str = StringVar()
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
        self.left_frame = Frame(self.root, bd=0,                 # sin borde
    highlightthickness=0, # sin “resaltado” al enfoque
    relief='flat')
        self.left_frame.place(x=0, y=0, width=600, height=900)

        self.canvas_uno = Canvas(self.left_frame, width=600, height=900, highlightthickness=0)
        self.canvas_uno.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_uno, "imagenes/decoa/wall/catacombs_5.png", escala=2)
        
        y_offset = 10
        row_height = 30

        if not hasattr(self, 'info_canvas'):
            self.info_canvas = {}
        if not hasattr(self, 'nd_canvas'):
            self.nd_canvas = []

        def add(label_text, var, key=None):
            nonlocal y_offset
            # 1) etiqueta fija
            lbl_id = self.canvas_uno.create_text(10, y_offset,
                                                 text=label_text,
                                                 fill="White",
                                                 font=self._font_normal,
                                                 anchor="nw")
            # 2) medir y posicionar valor a la derecha
            bbox = self.canvas_uno.bbox(lbl_id)
            x_val = bbox[2] 
            txt_id = self.canvas_uno.create_text(x_val, y_offset,
                                                 text=var.get(),
                                                 fill="gold",
                                                 font=self._font_normal,
                                                 anchor="nw")
            self.nd_canvas.append((var, self.canvas_uno, txt_id, x_val, y_offset))
            if key:
                self.info_canvas[key] = (self.canvas_uno, txt_id)
                y_offset += row_height

        add("Usdt + Btc:", self.balance_str, "balance")
        add("Variación Total invertido:", self.var_total_str, "variacion_total_inv")
        add("Variacion desde inicio:", self.var_inicio_str, "variacion_desde_inicio")
        add("Precio actual Btc/Usdt:", self.precio_act_str, "precio_actual")
        add("Precio de ingreso:", self.precio_de_ingreso_str, "desde_inicio")
        add("Ganancia neta en Usdt:", self.ganancia_total_str, "ganancia_neta")
        add("Fecha de inicio:", self.start_time_str, "start_time")
        add("Tiempo activo:", self.runtime_str, "runtime")
        add("Hold Btc/Usdt Comparativo:", self.hold_usdt_str, "hold_usdt")
        add("Hold Btc Comparativo:", self.hold_btc_str, "hold_btc")
        add("Btc Disponible:", self.cant_btc_str, "btc_dispo")
        add("Btc en Usdt:", self.btc_en_usdt, "btcnusdt")
        add("% Desde ultima compra:", self.varpor_set_compra_str, "desde_ult_comp")
        add("% Desde ultima venta:", self.varpor_set_venta_str, "ult_vent")
        add("Compras Realizadas:", self.compras_realizadas_str, "compras_realizadas")
        add("Ventas Realizadas:", self.ventas_realizadas_str, "ventas_realizadas")
        add("Compras fantasma:", self.cont_compras_fantasma_str, "compras_fantasma")
        add("Ventas fantasma:", self.cont_ventas_fantasma_str, "ventas_fantasma")
        add("Ghost Ratio:", self.ghost_ratio_var, "ghost_ratio")

        
  
    def center_panel(self):
        self.center_frame = Frame(self.root, bd=0, relief='flat')
        self.center_frame.place(x=600, y=0, width=500, height=450)

        self.canvas_center = Canvas(self.center_frame, width=500, height=450, highlightthickness=0, bd=0, relief='flat')
        self.canvas_center.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_center, "imagenes/decoa/wall/wall_vines_1.png", escala=2)
        

        y_offset = 10
        row_height = 30

        def add(label_text, var, key=None):
            nonlocal y_offset
            # 1) etiqueta fija
            lbl_id = self.canvas_center.create_text(10, y_offset,
                                                    text=label_text,
                                                    fill="White",
                                                    font=self._font_normal,
                                                    anchor="nw")
            # 2) medir y posicionar valor
            bbox = self.canvas_center.bbox(lbl_id)
            x_val = bbox[2] 
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
        self.right_frame = Frame(self.root, bd=0, # sin “resaltado” al enfoque
    relief='flat')
        self.right_frame.place(x=1100, y=0, width=850, height=450)

        self.canvas_right = Canvas(self.right_frame, width=850, height=450, highlightthickness=0)
        self.canvas_right.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_right, "imagenes/decoa/wall/relief_0.png", escala=2)
        

        self.historial = ScrolledText(self.canvas_right, bg="Gray", relief="flat", bd=0, font=self._font_normal)

        self.historial.place(x=50, y=50, width=750, height=350)


   

    def right_panel_b(self):
        self.right_frame_b = Frame(self.root)
        self.right_frame_b.place(x=1300, y=450, width=620, height=450)

        self.canvas_right_b = Canvas(self.right_frame_b, width=640, height=450, highlightthickness=0)
        self.canvas_right_b.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_right_b, "imagenes/decoa/wall/relief_brown_0.png", escala=2)
        

        # Creamos la consola, pero la añadimos al canvas con create_window
        self.consola = ScrolledText(
            self.canvas_right_b,
            bg="DarkGoldenRod",
            relief="flat",
            bd=0,
            font=self._font_normal
        )
        self.consola_window = self.canvas_right_b.create_window(
            70, 70,
            anchor="nw",
            window=self.consola,
            width=500,   # ojo: que quepa dentro de los 650px
            height=310
        )

        
        

    def animation_panel(self):
        self.animation_frame = Frame(self.root)
        self.animation_frame.place(x=600, y=450, width=700, height=450)

        self.canvas_animation = Canvas(self.animation_frame, width=700, height=450, highlightthickness=0)
        self.canvas_animation.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_animation, "imagenes/decoa/wall/grass_flowers_yellow_1_old.png", escala=3)

        

    def various_panel(self):
        self.various_frame = Frame(self.root)
        self.various_frame.place(x=0, y=900, width=2000, height=100)

        self.canvas_various = Canvas(self.various_frame, width=2000, height=100, highlightthickness=0)
        self.canvas_various.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_various, "imagenes/deco/snake-d_1.png", escala=3)
        
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
            if not self.bot.running:
                self.log_en_consola("⚠️ El bot no pudo iniciarse. Revisa configuración de operativa y coloca números válidos.")
                return
            if self.sound_enabled:
                reproducir_sonido("Sounds/soundinicio.wav")

            self.inicializar_valores_iniciales()

            self.btn_inicio.config(text="Detener")
            self.canvas_various.itemconfigure(self.btn_inicio_id, state='normal')
            self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')
            self.canvas_various.itemconfigure(self.btn_confi_id, state='normal')

            self._loop()

    def clear_bot(self):
        if self.bot.running:
            return

        # 1) Sonido y reinicio completo del bot
        if self.sound_enabled:
            reproducir_sonido("Sounds/limpiar.wav")
        self.bot.reiniciar()
        self.bot.log_fn = self.log_en_consola
        self.bot.sound_enabled = self.sound_enabled

        # 2) Limpiar todos los StringVars a vacío
        for attr in vars(self).values():
            if isinstance(attr, tk.StringVar):
                attr.set("")

        # 3) Borrar texto de cada canvas (dejamos el mapeo, sólo limpiamos el contenido)
        for canvas, item_id in self.info_canvas.values():
            try:
                canvas.itemconfig(item_id, text="", fill="Gold")
            except Exception:
                pass

        # 4) Vaciar historial y consola
        self.historial.delete("1.0", END)
        self.consola.delete("1.0", END)

        # 5) Resetear baseline de colores y valores
        """self.valores_iniciales.clear()
        self.colores_actuales.clear()"""

        # 6) Botones listos para nuevo inicio
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

    
        
    """def reset_stringvars(self):
        for i, (var, canvas, item_id, x_pos, y_pos) in enumerate(self.nd_canvas):
            valor = var.get()

            # Determinar color asociado si existe
            color = "Gold"
            key = None
            for k, (c, id_old) in self.info_canvas.items():
                if c == canvas and id_old == item_id:
                    key = k
                    color = self.colores_actuales.get(k, "Gold")
                    break

            # Borrar lo anterior y redibujar texto con el valor y color
            canvas.delete(item_id)
            text_id = canvas.create_text(
                x_pos, y_pos,
                text=valor,
                fill=color,
                font=self._font_normal,
                anchor="nw"
            )

            self.nd_canvas[i] = (var, canvas, text_id, x_pos, y_pos)
            if key:
                self.info_canvas[key] = (canvas, text_id)"""





    def abrir_configuracion_subventana(self):
        # Si ya está abierta y no fue destruida, traerla al frente
        if self.config_ventana is not None and self.config_ventana.winfo_exists():
            self.config_ventana.lift()
            self.config_ventana.focus_force()
            return  # No abrir otra

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

        # ── Check para activar compra tras venta fantasma
        self.var_ghost = BooleanVar(value=self.bot.ghost_purchase_enabled)
        cb_frame = Frame(self.config_ventana, bg="DarkGoldenRod")
        cb_frame.pack(fill=X, pady=4, padx=8)
        Checkbutton(cb_frame,
                    text="Habilitar compra tras venta fantasma",
                    variable=self.var_ghost,
                    bg="DarkGoldenRod",
                    font=self._font_normal,
                    fg="DarkSlateGray").pack(side=LEFT)  

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
                
                # 3) Validaciones > 0
                if porc_compra <= 0:
                    self.log_en_consola("⚠️ El porcentaje desde compra debe ser mayor que 0.")
                    return
                if porc_venta <= 0:
                    self.log_en_consola("⚠️ El porcentaje desde venta debe ser mayor que 0.")
                    return
                if porc_profit <= 0:
                    self.log_en_consola("⚠️ El porcentaje de profit por venta debe ser mayor que 0.")
                    return
                if porc_inv <= 0:
                    self.log_en_consola("⚠️ El porcentaje de inversión por compra debe ser mayor que 0.")
                    return
                if usdtinit <= 0:
                    self.log_en_consola("⚠️ El capital inicial debe ser mayor que 0.")
                    return


                # 3) Asignamos al bot (para los cálculos internos)
                self.bot.porc_desde_compra = porc_compra
                self.bot.porc_desde_venta = porc_venta
                self.bot.porc_profit_x_venta = porc_profit
                self.bot.porc_inv_por_compra = porc_inv
                self.bot.inv_inic = usdtinit
                # Aseguramos que el balance inicial coincida con el capital configurado
                self.bot.usdt = usdtinit


                self.bot.fixed_buyer = (
                    self.bot.inv_inic * self.bot.porc_inv_por_compra / Decimal('100')
                )

                 # 5) Calculamos fixed_buyer y validamos
                self.bot.fixed_buyer = (self.bot.inv_inic * self.bot.porc_inv_por_compra) / Decimal('100')
                if self.bot.fixed_buyer <= 0:
                    self.log_en_consola("⚠️ El monto de compra fijo debe ser mayor que 0.")
                    return
                
                self.bot.ghost_purchase_enabled = self.var_ghost.get()
   
                self.log_en_consola("Configuracion actualizada")
                self.log_en_consola("-------------------------")
                cerrar_config()

            except (InvalidOperation, IndexError):
                self.log_en_consola("Error: ingresa valores numericos validos.")

        Button(self.config_ventana, text="Guardar",
            bg="Goldenrod", command=guardar_config,
            font=self._font_normal, fg="PaleGoldenRod").pack(pady=8)

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
        future = self.executor.submit(self._run_trading_cycle)
        future.add_done_callback(
            lambda _: self.root.after(3000, self._loop)
        )

    def _run_trading_cycle(self):
        try:
            # 1) Intentamos obtener el ticker
            ticker = self.bot.exchange.fetch_ticker('BTC/USDT')
            price = ticker['last']
            # – Si salió bien, guardamos el precio y ejecutamos el ciclo de trading:
            self.bot.precio_actual = price
            self.bot.loop()
        except Exception as exc:
            # Si falla, dejamos precio_actual en None para detectar desconexión
            self.bot.precio_actual = None
            self.root.after(0, lambda exc=exc: self.log_en_consola(f"⚠️ Error de trading (sin precio): {exc}"))
        finally:
            # Solo aquí reprogramamos la actualización de la UI (una vez por ciclo)
            self.root.after_idle(self.actualizar_ui)


    def format_var(self, valor, simbolo=""):
        if valor is None:
            return ""
        if isinstance(valor, str):
            return valor
        if self.display_mode.get() == 'decimal':
            # str() completo de Decimal
            texto = format(valor, 'f')
        else:
            # float con los decimales definidos
            fmt = f"{{0:.{self.float_precision}f}}"
            texto = fmt.format(float(valor))
        return f"{simbolo} {texto}"

    
 

    def actualizar_ui(self):
        try:
            # --- Siempre actualizamos la UI, con o sin bot corriendo ---
            # 1) Fetch inicial de datos internos
            #    (si quieres evitar re-fetch dentro de UI, sólo toma valores de self.bot ya guardados)
            # 2) Pintado dinámico (colores) y fijo (texto), sin verificar self.bot.running

            # —— Dinámicos (comparan contra baseline) ——
            pintar = {
                "precio_actual":       self.bot.precio_actual,
                "balance":             self.bot.usdt_mas_btc,
                "desde_ult_comp":      self.bot.varCompra,
                "ult_vent":            self.bot.varVenta,
                "variacion_desde_inicio": self.bot.var_inicio,
                "variacion_total_inv":     self.bot.var_total,
                
                
                "hold_usdt":           self.bot.hold_usdt_var,
            }
            for clave, valor in pintar.items():
                self.actualizar_color(clave, valor)

            # —— Fijos (texto) —— 
            texto_fijo = {
                "start_time":          self.bot.get_start_time_str()  or "",
                "runtime":             self.bot.get_runtime_str()     or "",
                "porc_inv_por_compra": self.bot.porc_inv_por_compra,
                "usdt":                self.bot.usdt,
                "btc_dispo":           self.bot.btc,
                "desde_inicio":        self.bot.precio_ingreso or Decimal("0"),
                # compras/ventas y demás siguen igual:
                "compras_realizadas":  self.bot.contador_compras_reales,
                "ventas_realizadas":   self.bot.contador_ventas_reales,
                "compras_fantasma":    self.bot.contador_compras_fantasma,
                "ventas_fantasma":     self.bot.contador_ventas_fantasma,
                "ghost_ratio":         self.bot.calcular_ghost_ratio(),
                "porc_obj_venta":      self.bot.porc_profit_x_venta,
                "porc_desde_compra":   self.bot.porc_desde_compra,
                "porc_desde_venta":    self.bot.porc_desde_venta,
                "fixed_buyer":         self.bot.fixed_buyer,
                "inv_inicial":         self.bot.inv_inic,
                "ganancia_neta":       self.bot.total_ganancia,
                "btcnusdt":            self.bot.btc_usdt,
            }

            for clave, valor in texto_fijo.items():
                if clave not in self.info_canvas:
                    continue
                canvas, item_id = self.info_canvas[clave]
                coords = canvas.coords(item_id)
                if coords and len(coords) == 2:
                    x, y = coords
                else:
                    # fallback: no pintamos si no hay coords
                    continue

                canvas.delete(item_id)
                # enteros para los contadores
                if clave in (
                    "compras_realizadas","ventas_realizadas",
                    "compras_fantasma","ventas_fantasma"
                ):
                    display = str(int(valor))
                else:
                    display = self.format_var(valor)

                new_id = canvas.create_text(
                    x, y,
                    text=display,
                    fill="Gold",
                    font=self._font_normal,
                    anchor="nw"
                )
                self.info_canvas[clave] = (canvas, new_id)


            # Finalmente, refrescamos historial y consola
            self.actualizar_historial_consola()

        except Exception as e:
            self.log_en_consola(f"❌ Error UI: {e}")
        try:
            # Si el bot está corriendo, procedemos (no volvemos a fetchear en UI)
            if self.bot.running:
                # Detectar reconexión basándose en que precio anterior era None
                prev = getattr(self, "_prev_price_ui", None)
                actual = self.bot.precio_actual
                if prev is None and actual is not None:
                    self.log_en_consola("🔄 Conexión restablecida, Khazad reactivado.")
                    self.log_en_consola("--------------------------------------------")
                    #self.inicializar_valores_iniciales()
                self._prev_price_ui = actual

                # Ya tenemos self.bot.precio_actual cargado desde el hilo de trading
                if actual is None:
                    return
                
                
        except Exception as exc_ui:
                self.log_en_consola(f"❌ Error UI: {exc_ui}")       

    def actualizar_historial_consola(self):
        self.historial.delete('1.0', END)
        for t in self.bot.transacciones:
            ts = t.get("timestamp", "")
            self.historial.insert(END, "Compra desde:", 'compra_tag')
            # el resto de la línea en color por defecto
            resto = (
                f" {self.format_var(t['compra'], '$')} -> "
                f"Id: {t['id']} -> "
                f"Num: {t['numcompra']} -> "
                f"Fecha: {ts} -> "
                f"Objetivo: {self.format_var(t['venta_obj'], '$')}\n"
            )

            self.historial.insert(END, resto)
            id_op = t.get("id")
            
        for v in self.bot.precios_ventas:
            ts = v.get("timestamp", "")
            self.historial.insert(END, "Venta desde:", 'venta_tag')
            resto = (
                f" {self.format_var(v['compra'], '$')} -> "
                f"id: {v['id_compra']}, a: {self.format_var(v['venta'], '$')} | "
                f"Ganancia: {self.format_var(v['ganancia'], '$')}, "
                f"Num: {v['venta_numero']} -> Fecha: {ts}\n"
            )

            self.historial.insert(END, resto)

    def actualizar_color(self, key, valor_actual):
        if valor_actual is None or key not in self.info_canvas:
            return

        inicial = self.valores_iniciales.get(key, 0)
        color = "Gold"
        if valor_actual > inicial:
            color = "Green"
        elif valor_actual < inicial:
            color = "Crimson"
        """else:
            color = "Gold"  """  

        self.colores_actuales[key] = color

        if key not in self.info_canvas:
            return

        canvas, item_id = self.info_canvas[key]

        # Obtener coordenadas anteriores
        coords = canvas.coords(item_id)
        if not coords or len(coords) != 2:
            x, y = 20, 10
        else:
            x, y = coords

        canvas.delete(item_id)

        if key in ["compras_realizadas", "ventas_realizadas", "compras_fantasma", "ventas_fantasma"]:
            texto = str(int(valor_actual))
        else:
            texto = self.format_var(valor_actual)

        text_id = canvas.create_text(
            x, y,
            text=texto,
            fill=color,
            font=self._font_normal,
            anchor="nw"
        )

        self.info_canvas[key] = (canvas, text_id)


        #print(f"[TEXTO DIRECTO] key={key} valor={valor_actual} color={color}")





    """def reset_colores(self):
        for canvas, item_id in self.info_canvas.values():
            try:
                canvas.itemconfig(item_id, fill="Gold")
            except TclError:
                pass"""

        
    def log_en_consola(self, msg):
        self.consola.insert(END, msg+"\n")
        self.consola.see(END)

    def inicializar_valores_iniciales(self):
        self.bot.actualizar_balance()
        if self.bot.precio_actual is None:
            return  # No inicializar con datos vacíos
        # Guarda el primer snapshot para colorear luego
        self.valores_iniciales = {
            'precio_actual': self.bot.precio_actual or 0,
            'balance': self.bot.usdt_mas_btc,
            'desde_ult_comp': self.bot.varCompra,
            'ult_vent': self.bot.varVenta,
            'variacion_desde_inicio': self.bot.var_inicio,
            'variacion_total_inv': self.bot.var_total,
            'hold_usdt': self.bot.hold_usdt_var,
            'hold_btc': self.bot.hold_btc_var,
        }

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            # Puedes optar por destruir la ventana o simplemente ignorar
            pass

