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
from tkinter import TclError
import os

class BotInterface:
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
        self._font_normal = ("CrushYourEnemies", 10)
        self._font_nd = ("Tolkien Dwarf Runes", 14) 
        self.initial_usdt = bot.usdt
        self.loop_id = None
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        MAX_CABEZAS = 10
        # Lista de (StringVar, Label) para los No Data
        self.nd_labels = []

        
        
    
        # UI variables and clear initial values
        self._create_stringvars() 
        
        self.valores_iniciales = {}
        self.limpiar_visible = False
        
        self.root.after(100, self._animate_torch)
        self.root.after(100, self._animate_guard)
                 # ——— frames del guardián ———
        self.guard_open_frames = [
            PhotoImage(file=f"imagenes/deco/guardian-eyeopen-flame_{i}.png").zoom(2,2)
            for i in range(1,5)
        ]
        self.guard_closed_frames = [
            PhotoImage(file=f"imagenes/deco/guardian-eyeclosed-flame_{i}.png").zoom(2,2)
            for i in range(1,5)
        ]
        self.guard_frame_index = 0

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
        
       

        
        self.sound_enabled = True
        self.bot.sound_enabled = True

        # BARRA DE MENÚ
        menubar = Menu(self.root)
        self.config_menu = Menu(menubar, tearoff=0)
        self.config_menu.add_command(label="Silenciar sonido", command=self.toggle_sound)
        self.config_menu.add_command(label="Guardar captura", command=self.save_screenshot)
        menubar.add_cascade(label="Opciones", menu=self.config_menu)
        self.root.config(menu=menubar)

        self.torch_frames = [
            PhotoImage(file=f"imagenes/deco/torch_{i}.png").zoom(3, 3)
            for i in range(1, 5)
        ]
        self.torch_frame_index = 0
        self.torch_label = None

        # Secuencia de montones de oro: 1–10, luego 16, 19, 23, 25
        piles = list(range(1,11)) + [16,19,23,25]
        self.sales_frames = [
            PhotoImage(file=f"imagenes/deco/gold_pile_{n}.png").zoom(2,2)
            for n in piles
        ]
        
        self.sales_label = Label(self.center_frame, bg="DarkGoldenrod")
        self.sales_label.pack(pady=5)

        # Definimos en disco qué bottom frames tienes:
        bottom_indices = [1,5,7,8,9]
        self.hydra_bottom_frames = {
            n: PhotoImage(file=f"imagenes/deco/lernaean_hydra_{n}_bottom.png").zoom(2,2)
            for n in bottom_indices
        }
        
        self.hydra_top_frames = []  
        for i in range(1, MAX_CABEZAS+1):
            path = f"imagenes/deco/lernaean_hydra_{i}_top.png"
            if not os.path.exists(path):
                break    # si no está, dejamos de buscar más
            try:
                img = PhotoImage(file=path).zoom(2,2)
                self.hydra_top_frames.append(img)
            except TclError:
                break    # si hay otro problema al cargar, también rompemos

        # Creamos dos Labels, uno sobre el otro
        
        self.hydra_top_label    = Label(self.center_frame, bg="DarkGoldenrod")
        self.hydra_top_label.pack(side="top", pady=(0))
        self.hydra_bottom_label = Label(self.center_frame, bg="DarkGoldenrod")
        self.hydra_bottom_label.pack(side="top", pady=0)
        
        # Asegúrate de llamar a esto en tu actualizar_ui() o justo tras cada venta fantasma:
        self._update_hydra_image()

    def _update_hydra_image(self):
        count = self.bot.contador_ventas_fantasma

        if count < 1:
            # no hay hydra todavía
            self.hydra_bottom_label.pack_forget()
            self.hydra_top_label.pack_forget()
            return

        # ——— Bottom: escogemos el mayor índice disponible ≤ count
        available = sorted(self.hydra_bottom_frames.keys())
        # filtramos los ≤ count
        lower = [n for n in available if n <= count]
        if lower:
            chosen_bottom = lower[-1]
        else:
            chosen_bottom = available[0]  # por si acaso

        # ——— Top: limitamos a la lista de top_frames
        idx_top = min(count-1, len(self.hydra_top_frames)-1)

        # Mostramos ambos Labels (por si estaban ocultos)
        
        self.hydra_top_label.pack(pady=(0))
        
        self.hydra_bottom_label.pack(pady=(0))
        

        # Configuramos las imágenes
        self.hydra_top_label.configure(image=self.hydra_top_frames[idx_top])
        self.hydra_bottom_label.configure(image=self.hydra_bottom_frames[chosen_bottom])
        

    def _update_sales_image(self):
        count = self.bot.contador_ventas_reales
        if count < 1:
            # nada aún
            self.sales_label.configure(image='')
            return

        thresholds = list(range(1,11)) + [16,19,23,25]
        idx = 0
        for i, th in enumerate(thresholds):
            if count >= th:
                idx = i

        # Asegurarnos de no pasarnos del último índice disponible
        idx = min(idx, len(self.sales_frames) - 1)        

        self.sales_label.configure(image=self.sales_frames[idx])
   
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
        self.var_inicio_str = StringVar()

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

                # colocamos el guardián en la esquina superior derecha del info_frame
        self.guard_label = Label(self.info_frame,
                                image=self.guard_closed_frames[0],
                                bg="DarkGoldenrod")
        self.guard_label.pack(side="left", anchor="e", padx=5, pady=5)

            
    def _create_center_panel(self):
        self.center_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.center_frame.grid(row=0, column=1, sticky="n")

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
        self.historial = ScrolledText(self.right_frame, bg="Goldenrod", font=("Carolingia", 14))
        self.historial.grid(row=0, column=0, sticky="e", padx=2, pady=2)

        # Consola abajo
        self.consola = ScrolledText(self.right_frame, bg="Goldenrod", font=("Carolingia", 14))
        self.consola.grid (row=1, column=0, sticky="e", padx=2, pady=2)

    def _create_buttons(self):
        self.buttons_frame = Frame(self.main_frame, bg="DarkGoldenrod")
        self.buttons_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        self.btn_inicio = Button(self.buttons_frame, text="Iniciar", command=self.toggle_bot, bg="Goldenrod", font=("Carolingia", 14), fg="PaleGoldenRod")
        self.btn_inicio.grid(row=0, column=0, sticky="ew", padx=2)
        self.btn_limpiar = Button(self.buttons_frame, text="Limpiar", command=self.clear_bot, bg="Goldenrod", font=("Carolingia", 14), fg="PaleGoldenRod")
        btn_calc = Button(self.buttons_frame, text="Calculadora", command=self.open_calculator, bg="Goldenrod", font=("Carolingia", 14), fg="PaleGoldenRod")
        btn_calc.grid(row=0, column=2, sticky="e", padx=2)
        self.btn_confi = Button(self.center_frame, text="Configurar Operativa", bg="Goldenrod", command=self.abrir_configuracion_subventana, font=("Carolingia",14), fg="PaleGoldenRod")
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
        except ValueError:
            return 0  # o lo que quieras como fallback

    def abrir_configuracion_subventana(self):
        # Si ya existe y no fue destruida, la traemos al frente y salimos
        if self.config_ventana is not None and self.config_ventana.winfo_exists():
            self.config_ventana.lift()
            return

        # Si no existe, la creamos
        self.config_ventana = Toplevel(self.root)
        self.config_ventana.title("Configuracion de operativa")
        self.config_ventana.configure(bg="DarkGoldenRod")

        if not (self.torch_label and self.torch_label.winfo_exists()):
            self.torch_label = Label(self.config_ventana, bg="DarkGoldenrod")
            self.torch_label.pack(pady=(8, 0))

        self._animate_torch()

       # Al cerrar, destruye y pone la referencia a None
        def cerrar_config():
            detener_sonido_y_cerrar(self.config_ventana)
            self.config_ventana.destroy()
            self.config_ventana = None
            self.torch_label = None 

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
                self.bot.porc_desde_compra    = float(entries[0].get())
                self.bot.porc_desde_venta     = float(entries[1].get())
                self.bot.porc_profit_x_venta  = float(entries[2].get())
                self.bot.porc_inv_por_compra  = float(entries[3].get())
                self.bot.usdt                 = float(entries[4].get())
                self.bot.fixed_buyer = (self.bot.usdt *
                    self.bot.porc_inv_por_compra / 100)

                self.log_en_consola("Configuracion actualizada")
                self.log_en_consola("-------------------------")
                cerrar_config()
            except ValueError:
                self.log_en_consola("Error: ingresa valores numericos validos.")

        Button(self.config_ventana, text="Guardar",
            bg="Goldenrod", command=guardar_config,
            font=("Carolingia", 12), fg="PaleGoldenRod").pack(pady=8)

    def _animate_torch(self):
        # si la ventana de config existe y la etiqueta está creada, actualiza la imagen
        if (self.config_ventana and self.config_ventana.winfo_exists()
            and self.torch_label and self.torch_label.winfo_exists()):
            frame = self.torch_frames[self.torch_frame_index]
            self.torch_label.configure(image=frame)
            self.torch_frame_index = (self.torch_frame_index + 1) % len(self.torch_frames)

        # reprograma siempre el siguiente frame sobre la raíz
        self.root.after(100, self._animate_torch)

    def _animate_guard(self):
        # escogemos la secuencia abierta o cerrada
        frames = (self.guard_open_frames if self.bot.running
                  else self.guard_closed_frames)

        # actualizamos el frame
        frame = frames[self.guard_frame_index % len(frames)]
        self.guard_label.configure(image=frame)

        # avanzamos índice
        self.guard_frame_index = (self.guard_frame_index + 1) % len(frames)

        # reprogramamos sobre la raíz cada 100 ms
        self.root.after(100, self._animate_guard)
  

    def toggle_bot(self):            
            if self.bot.running:

                self.bot.detener()
                if self.sound_enabled:
                   reproducir_sonido("Sounds/detner.wav")
                # ahora mostramos el ojo cerrado
                self.guard_label.configure(image=self.guard_closed_frames[0])
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
                self.btn_confi.pack(pady=10)
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
            self._update_sales_image()
            self._update_hydra_image()
            self.actualizar_ui()
            
            # Restaurar botones
            self.btn_confi.pack(pady=10)
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
        except Exception:
            # si la ventana ya fue destruida o hubo otro error, simplemente ignoramos
            pass

    def _fetch_price_async(self):
        try:
            # Intentamos recuperar el ticker en el hilo de fondo
            ticker = self.bot.exchange.fetch_ticker('BTC/USDT')
            price = ticker['last']
        except Exception as e:
            # Re-lanzamos la excepción para que future.exception() la recoja
            raise RuntimeError(f"Error al obtener precio: {e}") from e

        # Si todo fue bien, pasamos el precio al hilo principal
        if self.root.winfo_exists():
            self.root.after(0, lambda: self._on_price_fetched(price))


    def actualizar_ui(self):
        try:
            if self.bot.running:
                # ——— Detectar reconexión de Internet ———
                prev_price = getattr(self.bot, 'precio_actual', None)
                new_price  = self.bot.get_precio_actual()
                # Si antes no había precio y ahora sí, reiniciamos todo el loop
                if prev_price is None and new_price is not None:
                    self.log_en_consola("🔄 Conexion restablecida, Khazad reactivado.")
                    self.log_en_consola("--------------------------------------------")
                    #self._loop()
                # Actualizamos el balance con el precio (que ya cargamos)
                self.bot.actualizar_balance()
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

                self.actualizar_historial_consola()                
                self.actualizar_color("precio_actual", self.bot.precio_actual)
                self.actualizar_color("balance", self.bot.usdt_mas_btc)
                self.actualizar_color("desde_ult_comp", self.bot.varCompra)
                self.actualizar_color("ult_vent", self.bot.varVenta)
                self.actualizar_color("variacion_desde_inicio", self.bot.var_inicio)

                # Total variation from initial balance
                if self.initial_usdt:
                    delta = (self.bot.usdt_mas_btc - self.initial_usdt) / self.initial_usdt * 100
                    self.var_total_str.set(f"{delta:.8f}%")
                else:
                    self.var_total_str.set("z")
                self.ganancia_total_str.set(f"$ {self.bot.total_ganancia:.6f}" if self.bot.total_ganancia else "z")
                # Cálculo Hold USDT
                if self.bot.precio_ingreso and precio:
                    hold_usdt = (self.initial_usdt / self.bot.precio_ingreso) * precio
                    self.hold_usdt_var.set(f"$ {hold_usdt:.4f}")
                else:
                    self.hold_usdt_var.set("z")
                
                # Cálculo Hold BTC en sats
                if self.bot.precio_ingreso:
                    sats = (self.initial_usdt / self.bot.precio_ingreso)
                    self.hold_btc_var.set(f"₿ {float(sats):.8f}")
                else:
                    self.hold_btc_var.set("z")

                # Repintar fuente según valor real o placeholder
                for var, lbl in self.nd_labels:
                    if var.get() == "z":
                        lbl.configure(font=self._font_nd)
                    else:
                        lbl.configure(font=self._font_normal)

                self._update_sales_image()
                self._update_hydra_image()

        except Exception as e:
            print("Error al actualizar la UI:", e)
            pass
            
    def actualizar_historial_consola(self):
        self.historial.delete('1.0', END)
        for t in self.bot.transacciones:
            ts = t.get("timestamp", "")
            self.historial.insert(END, "Compra desde:", 'compra_tag')
            # el resto de la línea en color por defecto
            resto = f" ${t['compra']:.2f} -> Id: {t['id']} -> Num: {t['numcompra']} -> Fecha: {ts} -> Objetivo: ${t['venta_obj']:.2f}\n"
            self.historial.insert(END, resto)
            id_op = t.get("id")
            
        for v in self.bot.precios_ventas:
            ts = v.get("timestamp", "")
            self.historial.insert(END, "Venta desde:", 'venta_tag')
            resto = f" $ {v['compra']:.2f} -> id: {v['id_compra']}, a: $ {v['venta']:.2f} | Ganancia: $ {v['ganancia']:.4f}, Num: {v['venta_numero']} -> Fecha: {ts}\n"
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
