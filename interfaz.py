# © 2025 Dungeon Market (Khazâd - Trading Bot)
# Todos los derechos reservados.
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from utils import reproducir_sonido, detener_sonido_y_cerrar
from codigo_principala import TradingBot
from calculador import CalculatorWindow
from PIL import ImageGrab, Image, ImageTk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor
from animation_mixin import AnimationMixin
from decimal import Decimal, InvalidOperation
import re


class BotInterfaz(AnimationMixin):
    def __init__(self, bot: TradingBot):
         # Main window setup
        self.root = tk.Tk()
        self.root.title("Dungeon Market")
        self.root.config(cursor="@imagenes/deco/cursor/stone_arrow.cur")
        self.root.configure(bg="pink")
        self.root.iconbitmap("imagenes/deco/urand_eternal_torment.png")
        self.root.attributes("-alpha", 0.93)
        # initialize bot and clear only ingreso price until started
        self.bot = bot
        self.bot.ui_callback_on_stop = self._on_bot_stop
        self.was_offline = False
        self.bot.log_fn = self.logf

        self.executor = ThreadPoolExecutor(max_workers=1)
        self.config_ventana = None
        # Fuentes específicas para consolas
        self._font_historial = ("LondonBetween", 16)  # o la que quieras
        self._font_consola   = ("LondonBetween", 16)  # o distinta si preferís
        
        self.colores_fijos = {
            "usdt": "SpringGreen",
            "btc_dispo": "SkyBlue",
            "btcnusdt": "DodgerBlue",
            "ganancia_neta": "LightSeaGreen",
            "start_time": "Khaki",
            "runtime": "Khaki",
            "compras_realizadas": "LightSteelBlue",
            "ventas_realizadas": "Cyan",
            "compras_fantasma": "Magenta",
            "ventas_fantasma": "MediumSpringGreen",

            "ghost_ratio": "Plum",
            "balance": "Orange",
            "variacion_total_inv": "Lightgreen",
            "variacion_desde_inicio": "LightCoral",
            "precio_actual": "LemonChiffon",
            "desde_ult_comp": "IndianRed",
            "ult_vent": "MediumSeaGreen",
            "excedente_compras": "MediumTurquoise",
            "excedente_ventas": "lightblue",
            "excedente_total": "Pink",
            "hold_usdt": "MediumPurple"
        }
        
        self._consola_buffer = []  # guarda todo lo impreso en consola
        self._font_normal = ("LondonBetween", 16)
        self.espaciado_horizontal = 5
        self.espaciado_vertical = 35
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
        self.ajustar_fuente_por_vista()
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
        self.inicializar_valores_iniciales()
        self._prev_price_ui = self.bot.precio_actual
        # Baseline for color comparisons
        
        
        self.sound_enabled = True
        self.bot.sound_enabled = True
         
        
 
    def reset_animaciones(self):
            self._animaciones_activas = False
            # Importante: no hay forma de cancelar los after activos a menos que guardes sus IDs.
            # Pero este flag impide que nuevas animaciones se dupliquen.
        
    def _on_bot_stop(self, motivo=None):
        # 🔁 Siempre resetear botones a un estado "limpio"
        self.btn_inicio.config(text="Iniciar")
        self.canvas_various.itemconfigure(self.btn_inicio_id, state='hidden')
        self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')
        self.canvas_various.itemconfigure(self.btn_confi_id, state='hidden')

        if motivo == "TP/SL":
            # Caso de parada automática → solo mostrar limpiar
            self.canvas_various.itemconfigure(self.btn_limpiar_id, state='normal')
            self.log_en_consola("📌 Bot detenido por Take Profit / Stop Loss. Usa 'Limpiar' antes de reiniciar.")
        else:
            # Caso manual o error → volver a flujo normal
            self.canvas_various.itemconfigure(self.btn_inicio_id, state='normal')
            self.canvas_various.itemconfigure(self.btn_confi_id, state='normal')

    def _crear_menu_vista(self):
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_radiobutton(
            label="Decimal",
            variable=self.display_mode,
            value="decimal",
            command=self._cambiar_precision
        )
        view_menu.add_radiobutton(
            label="Float (2 decimales)",
            variable=self.display_mode,
            value="float",
            command=lambda: self._cambiar_precision(2)
        )
        view_menu.add_radiobutton(
            label="Float (4 decimales)",
            variable=self.display_mode,
            value="float",
            command=lambda: self._cambiar_precision(4)
        )

        self.menubar.add_cascade(label="Vista", menu=view_menu)


    def _cambiar_precision(self, prec=None):
        if prec is not None:
            self.float_precision = prec

        self.ajustar_fuente_por_vista()  
        #self.reset_animaciones()

        # 🧼 Destruir y recrear paneles para que los textos fijos usen nueva fuente
        try:
            self.left_frame.destroy()
            self.center_frame.destroy()
            self.animation_frame.destroy()
        except Exception:
            pass
        self.left_panel()
        self.center_panel()
        self.animation_panel()
        self.init_animation()  

        #self.bot.set_formatter(self.format_var)
        self.actualizar_ui()
        self.actualizar_consola()
        self.actualizar_historial()

    def ajustar_fuente_por_vista(self):
        modo = self.display_mode.get()

        if modo == 'decimal':
            size = 16
            self.espaciado_vertical = 35
        elif modo == 'float' and self.float_precision == 2:
            size = 28
            self.espaciado_vertical = 40
        elif modo == 'float' and self.float_precision == 4:
            size = 24
            self.espaciado_vertical = 40
        else:
            size = 16  # fallback
            self.espaciado_vertical = 35

        self._font_normal = ("LondonBetween", size)

        # Tamaños FIJOS para consolas según la vista
        if modo == 'decimal':
            hist_size = 16   # ej.: si estabas en 14, pasa a 16
            cons_size = 16
        elif modo == 'float' and self.float_precision == 2:
            hist_size = 20
            cons_size = 20
        elif modo == 'float' and self.float_precision == 4:
            hist_size = 18
            cons_size = 18
        else:
            hist_size = 16
            cons_size = 16

        self._font_historial = (self._font_normal[0], hist_size)
        self._font_consola   = (self._font_normal[0], cons_size)

        # aplicar inmediatamente a los widgets existentes
        self._aplicar_fuente_consolas()
       


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
        self.precio_act_str = tk.StringVar()
        self.balance_str = tk.StringVar()
        self.start_time_str = tk.StringVar()
        self.runtime_str = tk.StringVar()
        self.cant_btc_str = tk.StringVar()
        self.btc_en_usdt = tk.StringVar()
        self.varpor_set_compra_str = tk.StringVar()
        self.varpor_set_venta_str = tk.StringVar()
        self.precio_de_ingreso_str = tk.StringVar()
        self.var_inicio_str = tk.StringVar()
        self.ganancia_total_str = tk.StringVar()
        self.cont_compras_fantasma_str = tk.StringVar()
        self.cont_ventas_fantasma_str = tk.StringVar()
        self.ghost_ratio_var = tk.StringVar()
        self.compras_realizadas_str = tk.StringVar()
        self.ventas_realizadas_str = tk.StringVar()
        self.porc_objetivo_venta_str = tk.StringVar()
        self.cant_usdt_str = tk.StringVar()
        self.porc_desde_compra_str = tk.StringVar()
        self.porc_desde_venta_str = tk.StringVar()
        self.inv_por_compra_str = tk.StringVar()
        self.fixed_buyer_str = tk.StringVar()
        self.hold_usdt_str = tk.StringVar()
        self.hold_btc_str = tk.StringVar()
        self.var_total_str = tk.StringVar() 
        self.excedente_compras_str = tk.StringVar()
        self.excedente_ventas_str = tk.StringVar()
        self.excedente_total_str = tk.StringVar()
        self.take_profit_str = tk.StringVar()
        self.stop_loss_str = tk.StringVar()



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
        self.left_frame = tk.Frame(self.root, bd=0,                 # sin borde
    highlightthickness=0, # sin “resaltado” al enfoque
    relief='flat')
        self.left_frame.place(x=0, y=0, width=600, height=900)

        self.canvas_uno = tk.Canvas(self.left_frame, width=600, height=900, highlightthickness=0)
        self.canvas_uno.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_uno, "imagenes/decoa/wall/catacombs_5.png", escala=2)
        
        y_offset = 10
        row_height = self.espaciado_vertical 


        if not hasattr(self, 'info_canvas'):
            self.info_canvas = {}
        if not hasattr(self, 'nd_canvas'):
            self.nd_canvas = []

        def add(label_text, var, key=None):
            nonlocal y_offset
            # 1) etiqueta fija
            color_etiqueta = self.colores_fijos.get(key, "White") if key else "White"

            lbl_id = self.canvas_uno.create_text(10, y_offset,
                                                 text=label_text,
                                                 fill=color_etiqueta,
                                                 font=self._font_normal,
                                                 anchor="nw")
            # 2) medir y posicionar valor a la derecha
            bbox = self.canvas_uno.bbox(lbl_id)
            x_val = bbox[2] + self.espaciado_horizontal
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
        
        add("Ganancia neta en Usdt:", self.ganancia_total_str, "ganancia_neta")
        add("Usdt Disponible:", self.cant_usdt_str, "usdt")

        
        add("Hold Btc/Usdt Guía:", self.hold_usdt_str, "hold_usdt")
        
        add("Btc Disponible:", self.cant_btc_str, "btc_dispo")
        add("Btc en Usdt:", self.btc_en_usdt, "btcnusdt")
        add("% Desde ultima compra:", self.varpor_set_compra_str, "desde_ult_comp")
        add("% Desde ultima venta:", self.varpor_set_venta_str, "ult_vent")
        add("Compras Realizadas:", self.compras_realizadas_str, "compras_realizadas")
        add("Ventas Realizadas:", self.ventas_realizadas_str, "ventas_realizadas")
        add("Compras fantasma:", self.cont_compras_fantasma_str, "compras_fantasma")
        add("Ventas fantasma:", self.cont_ventas_fantasma_str, "ventas_fantasma")
        add("Ghost Ratio:", self.ghost_ratio_var, "ghost_ratio")
        add("Excedente en compras:", self.excedente_compras_str, "excedente_compras")
        add("Excedente en ventas:",  self.excedente_ventas_str, "excedente_ventas")
        add("Excedente total:",  self.excedente_total_str, "excedente_total")

        
    def center_panel(self):
        self.center_frame = tk.Frame(self.root, bd=0, relief='flat')
        self.center_frame.place(x=600, y=0, width=700, height=450)

        self.canvas_center = tk.Canvas(self.center_frame, width=700, height=450, highlightthickness=0, bd=0, relief='flat')
        self.canvas_center.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_center, "imagenes/decoa/wall/wall_vines_1.png", escala=2)
        

        y_offset = 10
        row_height = self.espaciado_vertical


        def add(label_text, var, key=None):
            nonlocal y_offset
            # 1) etiqueta fija
            lbl_id = self.canvas_center.create_text(10, y_offset,
                                                    text=label_text,
                                                    fill="MediumSpringGreen",
                                                    font=self._font_normal,
                                                    anchor="nw")
            # 2) medir y posicionar valor
            bbox = self.canvas_center.bbox(lbl_id)
            x_val = bbox[2] + self.espaciado_horizontal
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
        
        add("% Desde compra, para compra:", self.porc_desde_compra_str, "porc_desde_compra")
        add("% Desde venta, para compra:", self.porc_desde_venta_str, "porc_desde_venta")
        add("% Por operacion:", self.inv_por_compra_str, "porc_inv_por_compra")
        add("% Fijo para inversion:", self.fixed_buyer_str, "fixed_buyer")
        add("Take Profit:", self.take_profit_str, "take_profit")
        add("Stop Loss:", self.stop_loss_str, "stop_loss")

        

    def right_panel(self):
        self.right_frame = tk.Frame(self.root, bd=0, # sin “resaltado” al enfoque
    relief='flat')
        self.right_frame.place(x=1300, y=0, width=650, height=450)

        self.canvas_right = tk.Canvas(self.right_frame, width=650, height=450, highlightthickness=0)
        self.canvas_right.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_right, "imagenes/decoa/wall/relief_0.png", escala=2)
        

        self.historial = ScrolledText(self.canvas_right, bg="Gray", relief="flat", bd=0, font=self._font_historial)

        self.historial.place(x=70, y=70, width=500, height=310)


   

    def right_panel_b(self):
        self.right_frame_b = tk.Frame(self.root)
        self.right_frame_b.place(x=1300, y=450, width=620, height=450)

        self.canvas_right_b = tk.Canvas(self.right_frame_b, width=640, height=450, highlightthickness=0)
        self.canvas_right_b.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_right_b, "imagenes/decoa/wall/relief_brown_0.png", escala=2)
        

        # Creamos la consola, pero la añadimos al canvas con create_window
        self.consola = ScrolledText(
            self.canvas_right_b,
            bg="DarkGoldenRod",
            relief="flat",
            bd=0,
            font=self._font_consola
        )
        self.consola_window = self.canvas_right_b.create_window(
            70, 70,
            anchor="nw",
            window=self.consola,
            width=500,   # ojo: que quepa dentro de los 650px
            height=310
        )

      
    def logf(self, tpl, **vals):
        # Guarda la entrada como formateable
        self._consola_buffer.append(("fmt", tpl, vals))

        # Pintar ahora mismo usando format_var (mismo criterio que paneles)
        def _fmt(v):
            if isinstance(v, tuple):
                val, sim = v
            else:
                val, sim = v, ""
            return self.format_var(val, sim)

        linea = tpl.format(**{k: _fmt(v) for k, v in vals.items()})
        linea = self._reformat_line(linea)

        try:
            first, last = self.consola.yview()
            estaba_al_fondo = (1.0 - last) < 1e-3
        except Exception:
            estaba_al_fondo = True

        self.consola.configure(state='normal')
        self.consola.insert(tk.END, linea + "\n")
        self.consola.configure(state='disabled')

        if estaba_al_fondo:
            self.consola.see(tk.END)
        else:
            self.consola.yview_moveto(first)

    def _reformat_line(self, s: str) -> str:
        # Reaplica el formateo para $, ₿ y % usando la vista actual
        def sub_money(m):
            try:
                return self.format_var(Decimal(m.group(1)), '$')
            except Exception:
                return m.group(0)

        def sub_btc(m):
            try:
                return self.format_var(Decimal(m.group(1)), '₿')
            except Exception:
                return m.group(0)

        def sub_pct_sufijo(m):
            try:
                return self.format_var(Decimal(m.group(1)), '%')
            except Exception:
                return m.group(0)

        def sub_pct_prefijo(m):
            try:
                return self.format_var(Decimal(m.group(1)), '%')
            except Exception:
                return m.group(0)

        s = re.sub(r'\$ ?(-?\d+(?:\.\d+)?)', sub_money, s)
        s = re.sub(r'₿ ?(-?\d+(?:\.\d+)?)', sub_btc, s)
        s = re.sub(r'(-?\d+(?:\.\d+)?)\s*%', sub_pct_sufijo, s)
        s = re.sub(r'%\s*(-?\d+(?:\.\d+)?)', sub_pct_prefijo, s)
        return s


    def animation_panel(self):
        self.animation_frame = tk.Frame(self.root)
        self.animation_frame.place(x=600, y=450, width=700, height=450)

        self.canvas_animation = tk.Canvas(self.animation_frame, width=700, height=450, highlightthickness=0)
        self.canvas_animation.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_animation, "imagenes/decoa/wall/grass_flowers_yellow_1_old.png", escala=3)

        y_offset = 10
        row_height = 30

        def add(label_text, var, key=None, simbolo=""):
            nonlocal y_offset

            label_var = tk.StringVar(value=label_text)
            val_var = var

            # Texto fijo (etiqueta)
            lbl_id = self.canvas_animation.create_text(
                10, y_offset,
                text=label_var.get(),
                fill="Orange",
                font=self._font_normal,
                anchor="nw"
            )

            self.nd_canvas.append((label_var, self.canvas_animation, lbl_id, 10, y_offset, ""))

            bbox = self.canvas_animation.bbox(lbl_id)
            x_val = bbox[2] + self.espaciado_horizontal

            # Texto dinámico (valor)
            txt_id = self.canvas_animation.create_text(
                x_val, y_offset,
                text=val_var.get(),
                fill="Red",
                font=self._font_normal,
                anchor="nw"
            )

            self.nd_canvas.append((val_var, self.canvas_animation, txt_id, x_val, y_offset, simbolo))
            if key:
                self.info_canvas[key] = (self.canvas_animation, txt_id)

            y_offset += row_height

        add("Precio de ingreso:", self.precio_de_ingreso_str, "desde_inicio", "$")
        add("Fecha de inicio:", self.start_time_str, "start_time")
        add("Tiempo activo:", self.runtime_str, "runtime")
        add("Hold Btc Comparativo:", self.hold_btc_str, "hold_btc", "₿")
        

    def various_panel(self):
        self.various_frame = tk.Frame(self.root)
        self.various_frame.place(x=0, y=900, width=2000, height=100)

        self.canvas_various = tk.Canvas(self.various_frame, width=2000, height=100, highlightthickness=0)
        self.canvas_various.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_various, "imagenes/deco/snake-d_1.png", escala=3)
        
        # Crear botones pero solo mostrar "Iniciar" al principio
        self.btn_inicio = tk.Button(self.canvas_various, text="Iniciar", command=self.toggle_bot, bg="Goldenrod", font=("LondonBetween", 16), fg="PaleGoldenRod")
        self.btn_inicio_id = self.canvas_various.create_window(100, 50, window=self.btn_inicio)

        self.btn_limpiar = tk.Button(self.canvas_various, text="Limpiar", command=self.clear_bot, bg="Goldenrod", font=("LondonBetween", 16), fg="PaleGoldenRod")
        self.btn_limpiar_id = self.canvas_various.create_window(250, 50, window=self.btn_limpiar)
        self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')

        self.btn_calc = tk.Button(self.canvas_various, text="Calculadora", command=self.open_calculator, bg="Goldenrod", font=("LondonBetween", 16), fg="PaleGoldenRod")
        self.canvas_various.create_window(400, 50, window=self.btn_calc)

        self.btn_confi = tk.Button(self.canvas_various, text="Configurar Operativa", command=self.abrir_configuracion_subventana, bg="Goldenrod", font=("LondonBetween", 16), fg="PaleGoldenRod")
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

        # 2) Reiniciar bot y resetear estado lógico
        self.bot.reiniciar()
        

        self.bot.log_fn = self.logf

        #self.bot.sound_enabled = self.sound_enabled
        modo_vista_actual = self.display_mode.get()
        precision_actual = self.float_precision
        self.ajustar_fuente_por_vista()

# 5) Reset StringVars
        for attr in vars(self).values():
            if isinstance(attr, tk.StringVar):
                attr.set("")

        # 10) Restaurar la vista del usuario
        self.display_mode.set(modo_vista_actual)
        self.float_precision = precision_actual

        for key in list(self.info_canvas.keys()):
            canvas, item_id = self.info_canvas[key]
            try:
                canvas.delete(item_id)
            except Exception:
                pass
        self.info_canvas.clear()

        self.nd_canvas.clear()

        # 4) Reset variables visuales
        self.valores_iniciales.clear()
        self.colores_actuales.clear()

        # 6) Vaciar historial y consola
        self.historial.delete("1.0", tk.END)
        self.consola.delete("1.0", tk.END)
       
        self._consola_buffer.clear()

        # 7) Guardar la vista actual del usuario
        self.reset_animaciones()


        # 8) Destruir frames viejos
        try:
            self.left_frame.destroy()
            self.center_frame.destroy()
        except Exception:
            pass

        # 9) Reconstruir paneles
        self.left_panel()
        self.center_panel()
        self.init_animation()
        # 8) Redibujar datos actuales (aunque estén vacíos)
        self.actualizar_ui()

        # 9) Restaurar botones
        self.btn_inicio.config(text="Iniciar")
        self.canvas_various.itemconfigure(self.btn_inicio_id, state='normal')
        self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')
        self.canvas_various.itemconfigure(self.btn_confi_id, state='normal')

        # 10) Forzar primer log de limpieza
        self.log_en_consola("🧹 Bot limpiado.")


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

    def abrir_configuracion_subventana(self):
        # Si ya está abierta y no fue destruida, traerla al frente
        if self.config_ventana is not None and self.config_ventana.winfo_exists():
            self.config_ventana.lift()
            self.config_ventana.focus_force()
            return  # No abrir otra

        self.config_ventana = tk.Toplevel(self.root)
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
            ("Total Usdt: $", self.bot.inv_inic),
            ("Take Profit Global (%):", self.bot.take_profit_pct or Decimal("0")),
            ("Stop Loss Global (%):", self.bot.stop_loss_pct or Decimal("0")),
        ]

        # ── Check para activar compra tras venta fantasma
        self.var_ghost = tk.BooleanVar(value=self.bot.compra_en_venta_fantasma)
        cb_frame = tk.Frame(self.config_ventana, bg="DarkGoldenRod")
        cb_frame.pack(fill=tk.X, pady=4, padx=8)
        tk.Checkbutton(cb_frame,
                    text="Habilitar compra tras venta fantasma",
                    variable=self.var_ghost,
                    bg="DarkGoldenRod",
                    font=("LondonBetween", 16),
                    fg="DarkSlateGray").pack(side=tk.LEFT)  
        
        # ── Checks para activar/desactivar TP y SL globales
        self.var_tp_enabled = tk.BooleanVar(value=getattr(self.bot, "tp_enabled", False))
        self.var_sl_enabled = tk.BooleanVar(value=getattr(self.bot, "sl_enabled", False))
        cb_frame_tp_sl = tk.Frame(self.config_ventana, bg="DarkGoldenRod")
        cb_frame_tp_sl.pack(fill=tk.X, pady=2, padx=8)
        tk.Checkbutton(cb_frame_tp_sl,
                    text="Activar Take Profit",
                    variable=self.var_tp_enabled,
                    bg="DarkGoldenRod",
                    font=("LondonBetween", 16),
                    fg="DarkSlateGray").pack(side=tk.LEFT, padx=(0,12))
        tk.Checkbutton(cb_frame_tp_sl,
                    text="Activar Stop Loss",
                    variable=self.var_sl_enabled,
                    bg="DarkGoldenRod",
                    font=("LondonBetween", 16),
                    fg="DarkSlateGray").pack(side=tk.LEFT)
        
        # ── Check para activar/desactivar Rebalance (reequilibrio)
        self.var_rebalance_enabled = tk.BooleanVar(
            value=getattr(self.bot, "rebalance_enabled", False)
        )
        cb_frame_reb = tk.Frame(self.config_ventana, bg="DarkGoldenRod")
        cb_frame_reb.pack(fill=tk.X, pady=2, padx=8)
        tk.Checkbutton(cb_frame_reb,
                    text="Activar Rebalance",
                    variable=self.var_rebalance_enabled,
                    bg="DarkGoldenRod",
                    font=("LondonBetween", 16),
                    fg="DarkSlateGray").pack(side=tk.LEFT)

        # ── Rebalance: umbral de compras y % a vender
        frm_rb = tk.LabelFrame(self.config_ventana, text="Rebalance", bg="DarkGoldenRod",
                               fg="DarkSlateGray", font=("LondonBetween", 16))
        frm_rb.pack(fill=tk.X, padx=8, pady=6)

        tk.Label(frm_rb, text="Compras (umbral):", bg="DarkGoldenRod",
                 font=("LondonBetween", 14), fg="DarkSlateGray").grid(row=0, column=0, padx=4, pady=4, sticky="w")
        self.var_rebalance_threshold = tk.StringVar(value=str(getattr(self.bot, "rebalance_threshold", 6)))
        tk.Entry(frm_rb, textvariable=self.var_rebalance_threshold, width=8,
                 font=("LondonBetween", 14)).grid(row=0, column=1, padx=4, pady=4, sticky="w")

        tk.Label(frm_rb, text="Porcentaje a vender (%):", bg="DarkGoldenRod",
                 font=("LondonBetween", 14), fg="DarkSlateGray").grid(row=0, column=2, padx=12, pady=4, sticky="w")
        self.var_rebalance_pct = tk.StringVar(value=str(getattr(self.bot, "rebalance_pct", 50)))
        tk.Entry(frm_rb, textvariable=self.var_rebalance_pct, width=8,
                 font=("LondonBetween", 14)).grid(row=0, column=3, padx=4, pady=4, sticky="w")

        entries = []

        for etiqueta, valor in campos:
            frame = tk.Frame(self.config_ventana, bg="DarkGoldenRod")
            frame.pack(fill=tk.X, pady=4, padx=8)
            tk.Label(frame, text=etiqueta, bg="DarkGoldenRod",
                font=("LondonBetween", 16), fg="DarkSlateGray").pack(side=tk.LEFT)
            var = tk.StringVar(value=str(valor))
            tk.Entry(frame, textvariable=var, bg="DarkGoldenRod",
                font=("LondonBetween", 16), fg="Gold").pack(side=tk.LEFT, padx=6)
            entries.append(var)

        def guardar_config():
            try:
                # 1) Leemos la cadena exacta
                txt_compra = entries[0].get().strip()   # p.e. "0.0003234" o "5"
                txt_venta  = entries[1].get().strip()
                txt_profit  = entries[2].get().strip()
                txt_porc_inv = entries[3].get().strip()
                txt_usdt_inic = entries[4].get().strip()
                txt_tp  = entries[5].get().strip()
                txt_sl  = entries[6].get().strip()

                # 2) Construimos Decimal desde cadena (sin pasar por Decimal)
                porc_compra = Decimal(txt_compra)
                porc_venta  = Decimal(txt_venta)
                porc_profit  = Decimal(txt_profit)
                porc_inv = Decimal(txt_porc_inv)
                usdtinit = Decimal(txt_usdt_inic)
                tp = Decimal(txt_tp)
                sl = Decimal(txt_sl)

                # Validaciones Rebalance
                try:
                    rb_thr = int(self.var_rebalance_threshold.get())
                except (TypeError, ValueError):
                    self.log_en_consola("⚠️ Umbral de rebalance inválido (debe ser entero).")
                    return
                try:
                    rb_pct = int(self.var_rebalance_pct.get())
                except (TypeError, ValueError):
                    self.log_en_consola("⚠️ % de rebalance inválido (debe ser entero).")
                    return
                if rb_thr < 0:
                    self.log_en_consola("⚠️ El umbral de rebalance no puede ser negativo.")
                    return
                if not (1 <= rb_pct <= 100):
                    self.log_en_consola("⚠️ El % de rebalance debe estar entre 1 y 100.")
                    return
                
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
                if tp < 0:
                    self.log_en_consola("⚠️ El Take Profit debe ser 0 o mayor.")
                    return
                if sl < 0:
                    self.log_en_consola("⚠️ El Stop Loss debe ser 0 o mayor.")
                    return
                # Si se activan, deben ser > 0 (evitar detener instantáneamente)
                if self.var_tp_enabled.get() and tp <= 0:
                    self.log_en_consola("⚠️ Si activás el Take Profit, debe ser mayor que 0.")
                    return
                if self.var_sl_enabled.get() and sl <= 0:
                    self.log_en_consola("⚠️ Si activás el Stop Loss, debe ser mayor que 0.")
                    return

                # 3) Asignamos al bot (para los cálculos internos)
                self.bot.porc_desde_compra = porc_compra
                self.bot.porc_desde_venta = porc_venta
                self.bot.porc_profit_x_venta = porc_profit
                self.bot.porc_inv_por_compra = porc_inv
                self.bot.inv_inic = usdtinit
                self.bot.take_profit_pct = (tp if tp > 0 else None)
                self.bot.stop_loss_pct = (sl if sl > 0 else None)
                self.bot.tp_enabled = self.var_tp_enabled.get()
                self.bot.sl_enabled = self.var_sl_enabled.get()
                self.bot.rebalance_enabled = self.var_rebalance_enabled.get()
                self.bot.rebalance_threshold = rb_thr
                self.bot.rebalance_pct = rb_pct

                if not self.bot.running:
                    self.bot.usdt = usdtinit

                self.bot.fixed_buyer = (
                    self.bot.inv_inic * self.bot.porc_inv_por_compra / Decimal('100'))
                

                 # 5) Calculamos fixed_buyer y validamos
                self.bot.fixed_buyer = (self.bot.inv_inic * self.bot.porc_inv_por_compra) / Decimal('100')
                if self.bot.fixed_buyer <= 0:
                    self.log_en_consola("⚠️ El monto de compra fijo debe ser mayor que 0.")
                    return
                
                self.bot.compra_en_venta_fantasma = self.var_ghost.get()
   
                tp_txt     = self.format_var(self.bot.take_profit_pct or Decimal('0'), '%')
                sl_txt     = self.format_var(self.bot.stop_loss_pct  or Decimal('0'), '%')
                rb_pct_txt = self.format_var(self.bot.rebalance_pct, '%')

                self.logf(
                    "Configuracion actualizada · TP: {tp_state} ({tp}) · SL: {sl_state} ({sl})",
                    tp_state='ON' if self.bot.tp_enabled else 'OFF',
                    tp=(self.bot.take_profit_pct or Decimal('0'), '%'),
                    sl_state='ON' if self.bot.sl_enabled else 'OFF',
                    sl=(self.bot.stop_loss_pct or Decimal('0'), '%'),
                )
                self.logf(
                    " · Rebalance: {rb_state} (umbral={thr}, pct={pct})",
                    rb_state='ON' if self.bot.rebalance_enabled else 'OFF',
                    thr=self.bot.rebalance_threshold,
                    pct=(self.bot.rebalance_pct, '%'),
                )


                self.log_en_consola("-------------------------")
                cerrar_config()

            except (InvalidOperation, IndexError):
                self.log_en_consola("Error: ingresa valores numericos validos.")

        tk.Button(self.config_ventana, text="Guardar",
            bg="Goldenrod", command=guardar_config,
            font=("LondonBetween", 16), fg="PaleGoldenRod").pack(pady=8)

    def _on_close(self):
        # 1) Cancelar after programado si existe
        if hasattr(self, 'loop_id') and self.loop_id is not None:
            try:
                self.root.after_cancel(self.loop_id)
            except Exception:
                pass

        # 2) Detener el bot si sigue corriendo
        try:
            if self.bot.running:
                self.bot.detener()
        except Exception:
            pass

        # 3) Apagar el ThreadPoolExecutor
        try:
            self.executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass

        # 4) Cerrar ventana
        try:
            self.root.destroy()
        except Exception:
            pass

            
    def _loop(self):
        # Si el bot ya no corre o la ventana ya no existe, salimos
        if not self.bot.running:
            return
        if not self.root.winfo_exists():
            return

        # Ejecutamos el ciclo de trading en segundo plano
        future = self.executor.submit(self._run_trading_cycle)

        # Cuando termine, planificamos el próximo _loop (solo si root sigue viva)
        def replanear(_):
            try:
                if self.root.winfo_exists() and self.bot.running:
                    self.root.after(3000, self._loop)
            except Exception as e:
                print(f"[⚠️ Error after loop]: {e}")

        future.add_done_callback(replanear)


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
            try:
                if self.root.winfo_exists():
                    self.root.after_idle(self.actualizar_ui)
            except:
                pass  # la ventana ya no existe

    

    def format_var(self, valor, simbolo=""):
        if valor is None:
            return ""
        if isinstance(valor, str):
            s = valor.strip()
            return f"{simbolo} {s}" if simbolo and s else s

        modo = self.display_mode.get() if hasattr(self, 'display_mode') else 'decimal'
        prec = self.float_precision if hasattr(self, 'float_precision') else 2

        if modo == 'decimal':
            # Mostrar “inteligente” con Decimal, sin ceros basura
            if not isinstance(valor, Decimal):
                valor = Decimal(str(valor))
            texto = format(valor.normalize(), 'f')
            if '.' in texto:
                texto = texto.rstrip('0').rstrip('.')
        else:
            # Mostrar HASTA 'prec' decimales y recortar ceros sobrantes
            try:
                v = float(valor)
            except Exception:
                v = float(str(valor))
            texto = f"{v:.{prec}f}"
            if '.' in texto:
                texto = texto.rstrip('0').rstrip('.')

        # Normalizar -0 → 0
        try:
            if float(texto) == 0.0:
                texto = "0"
        except Exception:
            pass

        return f"{simbolo} {texto}" if simbolo else texto


    def format_fijo(self, clave, valor):
        if isinstance(valor, tuple):
            valor_real, simbolo = valor
        else:
            valor_real, simbolo = valor, ""
        return self.format_var(valor_real, simbolo)



    def actualizar_ui(self):
        try:
            # --- Siempre actualizamos la UI, con o sin bot corriendo ---
            # 1) Fetch inicial de datos internos
            #    (si quieres evitar re-fetch dentro de UI, sólo toma valores de self.bot ya guardados)
            # 2) Pintado dinámico (colores) y fijo (texto), sin verificar self.bot.running

            # —— Dinámicos (comparan contra baseline) ——
            pintar = {
                "precio_actual": (self.bot.precio_actual, "$"),
                "balance": (self.bot.usdt_mas_btc, "$"),
                "desde_ult_comp": (self.bot.varCompra, "%"),
                "ult_vent": (self.bot.varVenta, "%"),
                "variacion_desde_inicio": (self.bot.var_inicio, "%"),
                "variacion_total_inv": (self.bot.var_total, "%"),
                "hold_usdt": (self.bot.hold_usdt_var, "$"),
            }
            for clave, valor in pintar.items():
                self.actualizar_color(clave, valor)

            # —— Fijos (texto) —— 
            texto_fijo = {
                "start_time": self.bot.get_start_time_str() or "",
                "runtime": self.bot.get_runtime_str() or "",
                "porc_inv_por_compra": (self.bot.porc_inv_por_compra, "%"),
                "usdt": (self.bot.usdt, "$"),
                "btc_dispo": (self.bot.btc, "₿"),
                "desde_inicio": (self.bot.precio_ingreso or Decimal("0"), "$"), 
                # compras/ventas y demás siguen igual:
                "compras_realizadas": self.bot.contador_compras_reales,
                "ventas_realizadas": self.bot.contador_ventas_reales,
                "compras_fantasma": self.bot.contador_compras_fantasma,
                "ventas_fantasma": self.bot.contador_ventas_fantasma,
                "ghost_ratio": (self.bot.calcular_ghost_ratio(), "%"),
                "porc_obj_venta": (self.bot.porc_profit_x_venta, "%"),
                "porc_desde_compra": (self.bot.porc_desde_compra, "%"),
                "porc_desde_venta": (self.bot.porc_desde_venta, "%"),
                "fixed_buyer": (self.bot.fixed_buyer, "$"),
                "inv_inicial": (self.bot.inv_inic, "$"),
                "ganancia_neta": (self.bot.total_ganancia, "$"),
                "hold_btc": (self.bot.hold_btc_var, "₿"),
                "btcnusdt": (self.bot.btc_usdt, "$"),
                "excedente_compras": (self.bot.excedente_total_compras, "%"),
                "excedente_ventas": (self.bot.excedente_total_ventas, "%"),
                "excedente_total": (self.bot.excedente_total_compras + self.bot.excedente_total_ventas, "%"),
                "take_profit": (self.bot.take_profit_pct or Decimal("0"), "%"),
                "stop_loss": (self.bot.stop_loss_pct or Decimal("0"), "%"),

            }

            

            for clave, valor in texto_fijo.items():
                if clave not in self.info_canvas:
                    continue
                canvas, item_id = self.info_canvas[clave]
                coords = canvas.coords(item_id)
                if coords and len(coords) == 2:
                    x, y = coords
                else:
                    continue  # No redibujar si no hay coordenadas

                # 🔁 Redibujar sólo el nuevo texto (valor) pero no cambiar el color aquí
                canvas.delete(item_id)
                texto = self.format_fijo(clave, valor)

                # Usamos el color actual ya calculado o default oro (evita colisiones)
                color = self.colores_actuales.get(clave, "Gold")

                # Reescribimos sólo el valor
                new_id = canvas.create_text(
                    x, y,
                    text=texto,
                    fill=color,
                    font=self._font_normal,
                    anchor="nw"
                )

                # Actualizamos la referencia
                self.info_canvas[clave] = (canvas, new_id)

            self.actualizar_historial()

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
                    self.inicializar_valores_iniciales()
                self._prev_price_ui = actual

                # Ya tenemos self.bot.precio_actual cargado desde el hilo de trading
                if actual is None:
                    return
                
                
        except Exception as exc_ui:
                self.log_en_consola(f"❌ Error UI: {exc_ui}")       



    def actualizar_historial(self):
        # recordar scroll
        first, last = self.historial.yview()
        estaba_al_fondo = (1.0 - last) < 1e-3

        self.historial.delete('1.0', tk.END)

        # ——— COMPRAS ———
        for t in self.bot.transacciones:
            ts = t.get("timestamp", "")
            self.historial.insert(tk.END, "🟦 Compra realizada:\n", 'compra_tag')
            self.historial.insert(tk.END, f"Precio de compra: {self.format_var(t['compra'], '$')}\n")
            self.historial.insert(tk.END, f"Id: {t['id']}\n")
            self.historial.insert(tk.END, f"Número de compra: {t['numcompra']}\n")
            self.historial.insert(tk.END, f"Fecha y hora: {ts}\n")
            if "venta_obj" in t:
                self.historial.insert(tk.END, f"Objetivo de venta: {self.format_fijo('venta_obj', t['venta_obj'])}\n")
            self.historial.insert(tk.END, "-"*40 + "\n")

        # ——— VENTAS ———
        for v in self.bot.precios_ventas:
            ts = v.get("timestamp", "")
            self.historial.insert(tk.END, "🟩 Venta realizada:\n", 'venta_tag')
            self.historial.insert(tk.END, f"Precio de compra: {self.format_fijo('compra', v['compra'])}\n")
            self.historial.insert(tk.END, f"Precio de venta: {self.format_fijo('venta', v['venta'])}\n")
            self.historial.insert(tk.END, f"Id compra: {v['id_compra']}\n")
            if 'ganancia' in v:
                self.historial.insert(tk.END, f"Ganancia: {self.format_fijo('ganancia', v['ganancia'])}\n")
            self.historial.insert(tk.END, f"Número de venta: {v['venta_numero']}\n")
            self.historial.insert(tk.END, f"Fecha y hora: {ts}\n")
            self.historial.insert(tk.END, "-"*40 + "\n")

        # restaurar scroll
        if estaba_al_fondo:
            self.historial.see(tk.END)
        else:
            self.historial.yview_moveto(first)

    def actualizar_consola(self):
        try:
            first, last = self.consola.yview()
            estaba_al_fondo = (1.0 - last) < 1e-3
        except Exception:
            estaba_al_fondo, first = True, 0.0

        def _fmt(v):
            if isinstance(v, tuple):
                val, sim = v
            else:
                val, sim = v, ""
            return self.format_var(val, sim)

        self.consola.configure(state='normal')
        self.consola.delete("1.0", tk.END)

        for entry in self._consola_buffer:
            kind = entry[0]
            if kind == "raw":
                _, msg = entry
                self.consola.insert(tk.END, self._reformat_line(msg) + "\n")
            elif kind == "fmt":
                _, tpl, vals = entry
                linea = tpl.format(**{k: _fmt(v) for k, v in vals.items()})
                linea = self._reformat_line(linea)
                self.consola.insert(tk.END, linea + "\n")

        self.consola.configure(state='disabled')

        if estaba_al_fondo:
            self.consola.see(tk.END)
        else:
            self.consola.yview_moveto(first)

    def actualizar_color(self, key, valor_actual):
        if valor_actual is None or key not in self.info_canvas:
            return
    
        try:
            if isinstance(valor_actual, tuple):
                val_act_raw, _ = valor_actual
            else:
                val_act_raw = valor_actual

            val_act = Decimal(str(val_act_raw).strip())

            val_ini_raw = self.valores_iniciales.get(key)
            if val_ini_raw is None:
                color = "Gold"
            else:
                val_ini = Decimal(str(val_ini_raw).strip())
                
                if val_ini is None:
                    color = "Gold"
                else:
                    if val_act > val_ini:
                        color = "lime"
                    elif val_act < val_ini:
                        color = "Crimson"
                    else:
                        color = "Gold"


        except Exception as e:
            print(f"[ERROR COLOR] key={key}, error={e}, val_act_raw={valor_actual}")
            color = "Gold"


        self.colores_actuales[key] = color

        canvas, item_id = self.info_canvas[key]
        coords = canvas.coords(item_id)
        x, y = coords if coords and len(coords) == 2 else (20, 10)

        canvas.delete(item_id)
        texto = self.format_fijo(key, valor_actual)
        text_id = canvas.create_text(
            x, y,
            text=texto,
            fill=color,
            font=self._font_normal,
            anchor="nw"
        )

        self.info_canvas[key] = (canvas, text_id)

    def _aplicar_fuente_consolas(self):
        try:
            self.consola.configure(font=self._font_consola)
        except Exception:
            pass
        try:
            self.historial.configure(font=self._font_historial)
        except Exception:
            pass

        
    def log_en_consola(self, msg):
        self._consola_buffer.append(("raw", msg))  # registrar sin tocar el texto

        first, last = self.consola.yview()
        estaba_al_fondo = (1.0 - last) < 1e-3

        self.consola.configure(state='normal')
        self.consola.insert(tk.END, self._reformat_line(msg) + "\n")
        self.consola.configure(state='disabled')

        if estaba_al_fondo:
            self.consola.see(tk.END)
        else:
            self.consola.yview_moveto(first)


            
    

    def inicializar_valores_iniciales(self):
        self.bot.actualizar_balance()

        def safe(val):
            try:
                return Decimal(str(val)) if val is not None else Decimal("0")
            except:
                return Decimal("0")

        if self.bot.precio_actual is None:
            return  # No inicializar con datos vacíos
        self.bot.hold_usdt_var = self.bot.hold_usdt()
        self.bot.hold_btc_var = self.bot.hold_btc()
        self.valores_iniciales = {
            'precio_actual':         safe(self.bot.precio_actual),
            'balance':               safe(self.bot.usdt_mas_btc),
            'desde_ult_comp':        safe(self.bot.varCompra),
            'ult_vent':              safe(self.bot.varVenta),
            'variacion_desde_inicio': safe(self.bot.var_inicio),
            'variacion_total_inv':   safe(self.bot.var_total),
            'hold_usdt':             safe(self.bot.hold_usdt_var),
            'hold_btc':              safe(self.bot.hold_btc_var),
        }

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            # Puedes optar por destruir la ventana o simplemente ignorar
            pass