# © 2025 Dungeon Market (Khazâd - Trading Bot)
# Todos los derechos reservados.

import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from utils import reproducir_sonido, detener_sonido_y_cerrar, reproducir_musica_fondo, detener_musica_fondo
from codigo_principala import TradingBot
#from calculador import CalculatorWindow
from PIL import ImageGrab, Image, ImageTk
from tkinter import filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor
from animation_mixin import AnimationMixin
from decimal import Decimal, InvalidOperation
import re
import csv
from datetime import datetime
from dum import DumTranslator

from database import get_wallet, set_wallet, cargar_perfil, guardar_perfil

class BotInterfaz(AnimationMixin):
    def __init__(self, bot: TradingBot, master=None, usuario=None):
         # Main window setup
        self._owns_mainloop = (master is None)
        self.usuario = usuario  # por ahora solo lo guardamos

        if master is None:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(master)
        
        
        self.root.title("Khazad - Dungeon Market")
        #self.root.config(cursor="@imagenes/deco/cursor/stone_arrow_x4.cur")
        self.root.configure(bg="pink")
        #self.root.iconbitmap("imagenes/deco/urand_eternal_torment.png")
        # ---- Icono del bot ----
        try:
            self.root.iconbitmap("imagenes/icon/cigotuvis_monster.ico")
        except Exception as e:
            print("Error cargando icono ICO:", e)

        # Y también mantené el PNG para Tk (opcional pero recomendado)
        try:
            self.img_icon = tk.PhotoImage(file="imagenes/icon/cigotuvis_monster.png")
            self.root.iconphoto(True, self.img_icon)
        except Exception as e:
            print("Error cargando icono PNG:", e)

            
        self.root.attributes("-alpha", 0.93)

                # Abrir la ventana ya maximizada
        try:
            # Windows
            self.root.state("zoomed")
        except Exception:
            # Linux / otros
            self.root.attributes("-zoomed", True)


        # initialize bot and clear only ingreso price until started
        self.bot = bot
        

        # --- DUM Translator (Modelo A) ---
        def _dum_persist_callback(res):
            # res es DumResultado
            if not self.usuario:
                return
            try:
                obs_s, quad_s = get_wallet(self.usuario)
                obs  = Decimal(str(obs_s))
                quad = Decimal(str(quad_s))

                obs  += Decimal(str(getattr(res, "obsidiana_vuelve", "0")))
                quad += Decimal(str(getattr(res, "quad_ganado", "0")))

                set_wallet(self.usuario, obs, quad)
            except Exception:
                pass

        self.dum = DumTranslator(persist_callback=_dum_persist_callback)



        # Encadenar callback existente (por ej. el que setea Dum desde main_menu)
        _old_stop_cb = getattr(self.bot, "ui_callback_on_stop", None)

        def _chained_stop_cb(motivo=None):
            # 1.5) DUM (Modelo A): cerrar run y persistir wallet
            try:
                if getattr(self.bot, "modo_app", "") == "dum" and self.usuario:
                    # motivo puede venir "TP"/"SL"/None
                    m = motivo if motivo else "detener"

                    res = self.dum.cerrar_run(self.usuario, self.bot, motivo=m)

                    # log
                    try:
                        self.log_en_consola(
                            f"🏁 Dum: vuelve {self.format_var(res.obsidiana_vuelve, '$')} obsidiana "
                            f"+ {self.format_var(res.quad_ganado, '$')} quad."
                        )
                        self.log_en_consola("- - - - - - - - - -")
                    except Exception:
                        pass

                    # reset depósito a 0 para la próxima run (Modelo A)
                    try:
                        self.bot.dum_deposito = Decimal("0")
                        self.bot.dum_slot_used = Decimal("0")
                        self.bot.inv_inic = Decimal("0")
                        self.bot.usdt = Decimal("0")
                    except Exception:
                        pass

                    # persistir perfil dum (deposito=0) para que al volver a loguear se vea limpio
                    try:
                        perfil = cargar_perfil(self.usuario)
                        if not isinstance(perfil, dict):
                            perfil = {}
                        di = (perfil.get("dum", {}) or {})
                        di["deposito"] = "0"
                        perfil["dum"] = di
                        guardar_perfil(self.usuario, perfil)
                    except Exception:
                        pass
            except Exception:
                pass

            
            # 1) UI local

            try:
                self._on_bot_stop(motivo)
            except Exception:
                pass
            # 2) callback anterior (Dum/persistencia/etc.)
            try:
                if callable(_old_stop_cb) and _old_stop_cb is not _chained_stop_cb:
                    try:
                        _old_stop_cb(motivo)
                    except TypeError:
                        _old_stop_cb()
            except Exception:
                pass

        self.bot.ui_callback_on_stop = _chained_stop_cb

        
        self.was_offline = False
        self.bot.log_fn = self.logf
        self.operativa_configurada = False
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.config_ventana = None
        # Fuentes específicas para consolas
        self._font_historial = ("LondonBetween", 16)  # o la que quieras
        self._font_consola   = ("LondonBetween", 16)  # o distinta si preferís
        self._consola_buffer = []  # buffer de líneas de consola
        self._consola_last_n = 0   # cuántas entradas del buffer ya fueron pintadas (console incremental)
        # === Consola: posiciones de la línea "📜 Estado:" por compra ===
        self._con_estado_pos_by_id = {}    # id_compra -> "line.start"
        self._con_estado_pos_by_num = {}   # numcompra -> "line.start"

        # cache para detectar cambios y no parchear al pedo
        self._con_estado_cache_by_id = {}
        self._con_estado_cache_by_num = {}
        self._estado_line_by_id = {}
        self._estado_line_by_num = {}

        self._ctx_ultimo_id = None # contexto incremental para corrección de estado
        self._ctx_ultimo_num = None
        self._hist_last_tx_n = 0
        self._hist_last_sell_n = 0
        # indices de la línea "Estado:" por compra
        self._hist_estado_pos_by_id = {}   # id -> "line.start"
        self._hist_estado_pos_by_num = {}  # numcompra -> "line.start"

        # cache para detectar cambios (evita reescribir al pedo)
        self._hist_estado_cache_by_id = {}
        self._hist_estado_cache_by_num = {}
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
            "hold_usdt": "MediumPurple",
            "rebalances": "IndianRed",
            "rebalance_loss_total": "Tomato",
            "total_fees_total": "IndianRed",
            "total_fees_buy": "PaleGoldenRod",
            "total_fees_sell": "MediumSeaGreen",
            "diff_hodl": "MediumTurquoise",
            "total_fees_btc": "IndianRed",
            "variacion_total_inv_usdt": "Orange",
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
        #self.runa_image = ImageTk.PhotoImage(Image.open("imagenes/decoa/runes/rune_dis_old.png").resize((35, 35), Image.ANTIALIAS))
        # Estado de modo de vista (Avanzado por defecto)
        self.modus = tk.StringVar(value='avanzado')
        self.info_labels = {}

        # Conjunto de keys a ocultar en modo Standard
        self._keys_modus_standar = {
            "excedente_compras",
            "excedente_ventas",
            "excedente_total",
            "ghost_ratio",
            "diff_hodl",
            "total_fees_btc",
        }

        # Frames
        self.left_panel()
        self.center_panel()
        self.right_panel()
        self.right_panel_b()
        self.animation_panel()
        self.various_panel()
        self.init_animation()
        self._aplicar_modus()
        # ⬅️ AÑADIR: estado visual inicial de altares
        try:
            self.set_take_profit_state("inactive")
            self.set_stop_loss_state("inactive")
        except Exception:
            pass

        self.historial.tag_configure('venta_tag', foreground='Green')
        self.historial.tag_configure('compra_tag', foreground='Blue')
        # 🎵 Música de fondo — definir estado ANTES de armar los menús
        self._music_path = "Musica/epicbfinal.wav"
        self.music_enabled = False  # estado inicial
        if self.music_enabled:
            reproducir_musica_fondo(self._music_path, loop=-1, volumen=0.25)

        # —————— Barra de menú unificada ——————
        self.menubar = tk.Menu(self.root)
        # Estado de vista: 'decimal' o 'float'
        self.display_mode = tk.StringVar(value='decimal')
        self.float_precision = 2
        self.ajustar_fuente_por_vista()
        # 3) Submenú Vista
        self._crear_menu_vista()
        # Creamos submenu Opciones
        self.config_menu   = tk.Menu(self.menubar, tearoff=0)
        self.config_menu.add_command(label="Silenciar sonido", command=self.toggle_sound)
        self.config_menu.add_command(label="Guardar captura", command=self.save_screenshot)
        self.menubar.add_cascade(label="Opciones", menu=self.config_menu)
        # —— Menú Música (independiente)
        self.music_menu = tk.Menu(self.menubar, tearoff=0)
        self.music_menu.add_command(label="Habilitar", command=self.music_enable)
        self.music_menu.add_command(label="Desabilitar", command=self.music_disable)
        self.menubar.add_cascade(label="Música", menu=self.music_menu)

        # Ajustar coherencia inicial (deshabilitar el que no corresponda)
        if self.music_enabled:
            self.music_menu.entryconfig("Habilitar", state="disabled")
        else:
            self.music_menu.entryconfig("Desabilitar", state="disabled")

        # ——— Menú Archivo ———
        menu_archivo = tk.Menu(self.menubar, tearoff=0)
        menu_archivo.add_command(label="Descargar historial...", command=self.descargar_historial)
        menu_archivo.add_command(label="Descargar consola...", command=self.descargar_consola)
        self.menubar.add_cascade(label="Archivo", menu=menu_archivo)

        # ¡Solo aquí configuramos el menú completo!
        self.root.config(menu=self.menubar) 
        self.actualizar_ui()
        if self.bot.running:
            self.inicializar_valores_iniciales()
        self._aplicar_modus()

        self._prev_price_ui = self.bot.precio_actual
        # Baseline for color comparisons
        self.sound_enabled = True
        self.bot.sound_enabled = True

        # —— Menú Modus ——
        self.modus_menu = tk.Menu(self.menubar, tearoff=0)
        self.modus_menu.add_radiobutton(
            label="Avanzado",
            variable=self.modus,
            value="avanzado",
            command=self._aplicar_modus
        )
        self.modus_menu.add_radiobutton(
            label="Standard",
            variable=self.modus,
            value="standard",
            command=self._aplicar_modus
        )

        self.menubar.add_cascade(label="Modus", menu=self.modus_menu)
        
    def reset_animaciones(self):
            self._animaciones_activas = False
            # Importante: no hay forma de cancelar los after activos a menos que guardes sus IDs.
            # Pero este flag impide que nuevas animaciones se dupliquen.
        
    def _on_bot_stop(self, motivo=None):
        """
        Callback desde TradingBot.detener(motivo)
        motivo: "TP" | "SL" | "TP/SL" (compat) | None/otros
        """
        # 🔁 Siempre resetear botones a un estado "limpio"
        self.btn_inicio.config(text="Iniciar")
        self.canvas_various.itemconfigure(self.btn_inicio_id, state='hidden')
        self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')
        self.canvas_various.itemconfigure(self.btn_confi_id, state='hidden')

        # Parada automática por TP/SL (nuevo y compat con el viejo "TP/SL")
        if motivo in ("TP", "SL", "TP/SL"):
            # mostrar solo 'Limpiar'
            self.canvas_various.itemconfigure(self.btn_limpiar_id, state='normal')

            if motivo == "TP":
                self.log_en_consola("🎯 Take Profit alcanzado. Usa 'Limpiar' antes de reiniciar.")
                try:
                    self.set_take_profit_state("hit")   # altar TP → Gozag
                except Exception:
                    pass

            elif motivo == "SL":
                self.log_en_consola("🛡️ Stop Loss alcanzado. Usa 'Limpiar' antes de reiniciar.")
                try:
                    self.set_stop_loss_state("hit")     # altar SL → Trog
                except Exception:
                    pass

            else:  # "TP/SL" (llamadas antiguas, motivo ambiguo)
                self.log_en_consola("📌 Bot detenido por Take Profit / Stop Loss. Usa 'Limpiar' antes de reiniciar.")
            return

        # Parada manual u otros motivos → mostrar Configurar y (solo si hay config) Iniciar
        if getattr(self, 'operativa_configurada', False):
            self.canvas_various.itemconfigure(self.btn_inicio_id, state='normal')
        else:
            self.canvas_various.itemconfigure(self.btn_inicio_id, state='hidden')
        self.canvas_various.itemconfigure(self.btn_confi_id, state='normal')
        
        
    

    def _crear_menu_vista(self):
        view_menu = tk.Menu(self.menubar, tearoff=0)

        # Decimal (auto, sin ceros basura)
        view_menu.add_radiobutton(
            label="Decimal",
            variable=self.display_mode,
            value="decimal",
            command=self._cambiar_precision  # no pasa prec, solo refresca
        )

        # 4 decimales (corte duro, sin redondeo)
        view_menu.add_radiobutton(
            label="4 decimales (cortar)",
            variable=self.display_mode,
            value="p4",
            command=lambda: self._cambiar_precision(4)
        )

        self.menubar.add_cascade(label="Vista", menu=view_menu)

    def _aplicar_modus(self):
        modus = self.modus.get()

        # Campos cuyo estado (visible/oculto) está controlado por otras lógicas
        # y NO deben ser forzados a 'normal' acá.
        keys_reb = {
            "rebalance_thr",
            "rebalance_pct",
            "rebalances",
            "rebalance_loss_total",
        }

        # 1) Mostrar todo por defecto (labels + valores),
        #    pero SIN tocar los campos de rebalance.
        for key, (canvas, item_id) in getattr(self, "info_canvas", {}).items():
            if key in keys_reb:
                continue  # estos los controla actualizar_ui según rebalance_enabled
            try:
                canvas.itemconfigure(item_id, state='normal')
            except Exception:
                pass

        for key, (canvas, lbl_id) in getattr(self, "info_labels", {}).items():
            if key in keys_reb:
                continue
            try:
                canvas.itemconfigure(lbl_id, state='normal')
            except Exception:
                pass

        # 2) En Standard, ocultar los pedidos (label + valor) definidos en _keys_modus_standar
        if modus == "standard":
            for key in getattr(self, "_keys_modus_standar", set()):
                if key in getattr(self, "info_canvas", {}):
                    canvas, item_id = self.info_canvas[key]
                    try:
                        canvas.itemconfigure(item_id, state='hidden')
                    except Exception:
                        pass
                if key in getattr(self, "info_labels", {}):
                    canvas, lbl_id = self.info_labels[key]
                    try:
                        canvas.itemconfigure(lbl_id, state='hidden')
                    except Exception:
                        pass

    def _hist_patch_estado(self, id_compra=None, numcompra=None, nuevo_estado="vendida"):
        txt = self.historial
        if not hasattr(self, "historial"):
            return

        pos = None
        if id_compra is not None:
            pos = self._hist_estado_pos_by_id.get(str(id_compra))
        if pos is None and numcompra is not None:
            pos = self._hist_estado_pos_by_num.get(str(numcompra))

        if not pos:
            return

        try:
            txt.configure(state="normal")
        except Exception:
            pass

        try:
            # borra SOLO la línea donde está "Estado: ..."
            line_start = pos
            line_end = txt.index(f"{pos} lineend +1c")
            txt.delete(line_start, line_end)
            txt.insert(line_start, f"Estado: {nuevo_estado}\n")
        except Exception:
            pass

        try:
            txt.configure(state="disabled")
        except Exception:
            pass


    def _cambiar_precision(self, prec=None):
        if prec is not None:
            self.float_precision = prec

        self.ajustar_fuente_por_vista()  

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
        self._aplicar_modus()
        self.actualizar_ui()
        # 6) ♻️ Re-render retroactivo de la CONSOLA con la vista nueva
        #    - Limpiamos el widget, reseteamos el puntero incremental
        #      y volvemos a volcar todo el buffer usando el nuevo modo.
        try:
            self.consola.configure(state='normal')
            self.consola.delete("1.0", "end")
            self.consola.configure(state='disabled')
        except Exception:
            pass
        # Reiniciar el índice incremental para que se reescriba todo
        try:
            self._consola_last_n = 0
        except Exception:
            self._consola_last_n = 0
        # Vuelca el buffer completo re-formateando con _reformat_line
        self.actualizar_consola()
        # 7) Rehacer HISTORIAL (ya se formatea con format_var según vista)
        self.actualizar_historial()

    def ajustar_fuente_por_vista(self):
        modo = self.display_mode.get() if hasattr(self, 'display_mode') else 'decimal'
        # default
        size = 16
        self.espaciado_vertical = 35

        if modo == 'p4':
            size = 24           # un poco más grande si querés
            self.espaciado_vertical = 40
            #self.float_precision = 4  # aseguramos 4

        self._font_normal = ("LondonBetween", size)

        # Tamaños FIJOS para consolas según la vista
        if modo == 'p4':
            hist_size = 18
            cons_size = 18
        else:
            hist_size = 16
            cons_size = 16

        self._font_historial = (self._font_normal[0], hist_size)
        self._font_consola   = (self._font_normal[0], cons_size)

        # aplicar inmediatamente a los widgets existentes
        self._aplicar_fuente_consolas()

    def music_enable(self):
        if not self.music_enabled:
            reproducir_musica_fondo("Musica/epicbfinal.wav", loop=-1, volumen=0.25)
            self.music_enabled = True
            self.log_en_consola("🎵 Música habilitada.")
            self.music_menu.entryconfig("Habilitar", state="disabled")
            self.music_menu.entryconfig("Desabilitar", state="normal")

    def music_disable(self):
        if self.music_enabled:
            detener_musica_fondo()
            self.music_enabled = False
            self.log_en_consola("🔇 Música desabilitada.")
            self.log_en_consola("- - - - - - - - - -")
            self.music_menu.entryconfig("Desabilitar", state="disabled")
            self.music_menu.entryconfig("Habilitar", state="normal")

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.bot.sound_enabled = self.sound_enabled
        estado = "🔇 Sonido desactivado" if not self.sound_enabled else "🔊 Sonido activado"
        
        self.log_en_consola(estado)
        self.log_en_consola("- - - - - - - - - -")
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
            self.log_en_consola("- - - - - - - - - -")

    def _exportar_texto(self, widget_text, sugerencia="export"):
        """
        Exporta el contenido de un Text/ScrolledText:
        - .txt (texto tal cual)
        - .csv (una línea por línea; Excel lo abre)
        """
        try:
            contenido = widget_text.get("1.0", "end-1c")
        except Exception as e:
            messagebox.showerror("Error", f"No pude leer el widget: {e}")
            return

        if not contenido.strip():
            messagebox.showinfo("Vacío", f"No hay contenido para exportar en '{sugerencia}'.")
            return

        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname_sugerido = f"{sugerencia}_{fecha}.txt"

        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=fname_sugerido,
            filetypes=[("Texto", "*.txt"), ("CSV (Excel)", "*.csv"), ("Todos", "*.*")],
            title=f"Guardar {sugerencia}"
        )
        if not ruta:
            return

        try:
            if ruta.lower().endswith(".csv"):
                # Guardamos cada línea como una fila CSV (una sola columna)
                lineas = contenido.splitlines()
                with open(ruta, "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    for linea in lineas:
                        w.writerow([linea])
            else:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(contenido)
            messagebox.showinfo("Listo", f"Guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No pude guardar el archivo:\n{e}")

    def descargar_historial(self):
        self._exportar_texto(self.historial, "historial")

    def descargar_consola(self):
        self._exportar_texto(self.consola, "consola")

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
        self.cont_rebalances_str = tk.StringVar() 
        self.rebalance_loss_total_str = tk.StringVar()
        self.rebalance_thr_str = tk.StringVar()
        self.rebalance_pct_str = tk.StringVar()
        self.total_fees_buy_str = tk.StringVar()
        self.total_fees_sell_str = tk.StringVar()
        self.total_fees_total_str = tk.StringVar()
        self.comision_pct_str = tk.StringVar()
        self.diff_hodl_str = tk.StringVar()
        self.total_fees_btc_srt = tk.StringVar()
        self.var_total_usdt_str = tk.StringVar()

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
            
            if key:
                self.info_labels[key] = (self.canvas_uno, lbl_id)
                self.info_canvas[key] = (self.canvas_uno, txt_id)

        add("Usdt + Btc:", self.balance_str, "balance")
        add("Btc en Usdt:", self.btc_en_usdt, "btcnusdt")
        add("Usdt Disponible:", self.cant_usdt_str, "usdt") 
        add("Variación Total invertido ($):", self.var_total_usdt_str, "variacion_total_inv_usdt")
        add("Variación Total invertido (%):", self.var_total_str, "variacion_total_inv")
        add("Variación desde inicio:", self.var_inicio_str, "variacion_desde_inicio")
        add("Precio actual Btc/Usdt:", self.precio_act_str, "precio_actual")    
        add("Ganancia Operativa:", self.ganancia_total_str, "ganancia_neta")
        add("Btc Disponible:", self.cant_btc_str, "btc_dispo")
        add("% Desde ultima compra:", self.varpor_set_compra_str, "desde_ult_comp")
        add("% Desde ultima venta:", self.varpor_set_venta_str, "ult_vent")
        add("Compras Realizadas:", self.compras_realizadas_str, "compras_realizadas")
        add("Ventas Realizadas:", self.ventas_realizadas_str, "ventas_realizadas")
        add("Compras fantasma:", self.cont_compras_fantasma_str, "compras_fantasma")
        add("Ventas fantasma:", self.cont_ventas_fantasma_str, "ventas_fantasma")
        add("Comisiónes de compras:", self.total_fees_buy_str, "total_fees_buy")
        add("Comisiónes de ventas:", self.total_fees_sell_str, "total_fees_sell")
        add("Comisiónes totales:", self.total_fees_total_str, "total_fees_total")
        add("Hold Btc/Usdt Guía:", self.hold_usdt_str, "hold_usdt")
        add("Dif. Hodl:", self.diff_hodl_str, "diff_hodl")
        add("Ghost Ratio:", self.ghost_ratio_var, "ghost_ratio")
        add("Excedente total:",  self.excedente_total_str, "excedente_total")       
        add("Excedente en compras:", self.excedente_compras_str, "excedente_compras")
        add("Excedente en ventas:",  self.excedente_ventas_str, "excedente_ventas")
        add("Total comisiónes en Btc:",  self.total_fees_btc_srt, "total_fees_btc")
        
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
                                                    fill="lime",
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

            if key:
                self.info_labels[key] = (self.canvas_center, lbl_id)
                self.info_canvas[key] = (self.canvas_center, txt_id)

        add("% Objetivo de venta, desde compra:", self.porc_objetivo_venta_str, "porc_obj_venta")    
        add("% Desde compra, para compra:", self.porc_desde_compra_str, "porc_desde_compra")
        add("% Desde venta, para compra:", self.porc_desde_venta_str, "porc_desde_venta")
        add("% Por operacion:", self.inv_por_compra_str, "porc_inv_por_compra")
        add("% Fijo para inversion:", self.fixed_buyer_str, "fixed_buyer")
        add("Take Profit:", self.take_profit_str, "take_profit")
        add("Stop Loss:", self.stop_loss_str, "stop_loss")
        add("Comisión:", self.comision_pct_str, "comision_pct")
    
    def right_panel(self):
        self.right_frame = tk.Frame(self.root, bd=0, relief='flat')
        self.right_frame.place(x=1300, y=0, width=650, height=450)
        self.canvas_right = tk.Canvas(self.right_frame, width=650, height=450, highlightthickness=0)
        self.canvas_right.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_right, "imagenes/decoa/wall/relief_0.png", escala=2)
        self.historial = ScrolledText(self.canvas_right, bg="Gray", relief="flat", bd=0, font=self._font_historial)
        self.historial_window = self.canvas_right.create_window(70, 70, anchor="nw", window=self.historial, width=500, height=310)

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
        # Guarda en buffer
        if not hasattr(self, "_consola_buffer"):
            self._consola_buffer = []
        self._consola_buffer.append(("fmt", tpl, vals))

        # Formateo previo para detectar cambios de estado (sin escribir aún)
        def _fmt(v):
            if isinstance(v, tuple):
                val, sim = v
            else:
                val, sim = v, ""
            return self.format_var(val, sim)

        linea = tpl.format(**{k: _fmt(v) for k, v in vals.items()})
        linea = self._reformat_line(linea)

        # Si el log anuncia un cambio de estado, parchear IN-PLACE la línea vieja
        try:
            m = re.search(
                r"Estado\s+de\s+compra\s*#\s*(\d+)\s*\(id\s*([A-Za-z0-9\-_]+)\)\s*:\s*([^\-]+?)\s*→\s*(\w+)",
                linea, flags=re.IGNORECASE
            )
            if m:
                numc_str, idc, _estado_viejo, estado_nuevo = m.groups()
                numc = int(numc_str)
                self._consola_patch_estado(id_compra=idc,  nuevo_estado=estado_nuevo)
                self._consola_patch_estado(numcompra=numc, nuevo_estado=estado_nuevo)
        except Exception:
            pass

        # NO escribir directo: render lo hace actualizar_consola() (incremental)
        self.actualizar_consola()

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
            if key:
                self.info_labels[key] = (self.canvas_animation, lbl_id)
                self.info_canvas[key] = (self.canvas_animation, txt_id)
        add("Precio de ingreso:", self.precio_de_ingreso_str, "desde_inicio", "$")
        add("Fecha de inicio:", self.start_time_str, "start_time")
        add("Tiempo activo:", self.runtime_str, "runtime")
       
        add("Rebalance — Umbral:", self.rebalance_thr_str, "rebalance_thr")
        add("Rebalance — Porcentaje:", self.rebalance_pct_str, "rebalance_pct")
        add("Rebalances realizados:", self.cont_rebalances_str, "rebalances")
        add("Pérdidas por rebalance:", self.rebalance_loss_total_str, "rebalance_loss_total")
        
        try:
            img_ped = Image.open("imagenes/deco/rebalance/pedestal.png")
            # ⬇️ Escala 2x (cambiá zoom_factor si querés otro tamaño)
            zoom_factor = 2
            w0, h0 = img_ped.size
            img_ped = img_ped.resize((w0 * zoom_factor, h0 * zoom_factor), Image.NEAREST)  # o Image.LANCZOS
            self._pedestal_img = ImageTk.PhotoImage(img_ped)  # mantener referencia
            w = int(self.canvas_animation["width"])
            h = int(self.canvas_animation["height"])
            self.pedestal_it = self.canvas_animation.create_image(
                w // 2 + 85, h - 30, image=self._pedestal_img, anchor="s"
            )
        except Exception as _e:
            pass

    def various_panel(self):
        self.various_frame = tk.Frame(self.root)
        self.various_frame.place(x=0, y=900, width=2000, height=100)
        self.canvas_various = tk.Canvas(self.various_frame, width=2000, height=100, highlightthickness=0)
        self.canvas_various.pack(fill="both", expand=True)
        self.rellenar_mosaico(self.canvas_various, "imagenes/decoa/wall/snake-d_1.png", escala=3)
        # 🧑 Usuario (posición absoluta)
        user_txt = (getattr(self, "usuario", "") or "").strip()
        if user_txt:
            # coordenadas ABSOLUTAS (ajustá si querés)
            x_user = 900
            y_user = 50

            self.usuario_text_id = self.canvas_various.create_text(
                x_user, y_user,
                text=f"👤 {user_txt}",
                fill="PaleGoldenRod",
                font=("LondonBetween", 16),
                anchor="w"
            )

        # Crear botones pero solo mostrar "Iniciar" al principio
        self.btn_inicio = tk.Button(self.canvas_various, text="Iniciar", command=self.toggle_bot, bg="Goldenrod", font=("LondonBetween", 16), fg="PaleGoldenRod")
        self.btn_inicio_id = self.canvas_various.create_window(100, 50, window=self.btn_inicio)
        self.canvas_various.itemconfigure(self.btn_inicio_id, state='hidden')
        self.btn_limpiar = tk.Button(self.canvas_various, text="Limpiar", command=self.clear_bot, bg="Goldenrod", font=("LondonBetween", 16), fg="PaleGoldenRod")
        self.btn_limpiar_id = self.canvas_various.create_window(250, 50, window=self.btn_limpiar)
        self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')
        #self.btn_calc = tk.Button(self.canvas_various, text="Calculadora", command=self.open_calculator, bg="Goldenrod", font=("LondonBetween", 16), fg="PaleGoldenRod")
        #self.canvas_various.create_window(400, 50, window=self.btn_calc)
        self.btn_confi = tk.Button(self.canvas_various, text="Configurar Operativa", command=self.abrir_configuracion_subventana, bg="Goldenrod", font=("LondonBetween", 16), fg="PaleGoldenRod")
        self.btn_confi_id = self.canvas_various.create_window(600, 50, window=self.btn_confi)
        

    def toggle_bot(self):
        if getattr(self.bot, "modo_app", "") == "dum":
            if not hasattr(self.bot, "dum_slot_used") or self.bot.dum_slot_used in (None, "", 0):
                self.bot.dum_slot_used = Decimal(str(getattr(self.bot, "dum_deposito", "0")))

        if self.bot.running:
            self.bot.detener()
            if self.sound_enabled:
                reproducir_sonido("Sounds/detener.wav")
            self.canvas_various.itemconfigure(self.btn_inicio_id, state='hidden')
            self.canvas_various.itemconfigure(self.btn_limpiar_id, state='normal')
            self.canvas_various.itemconfigure(self.btn_confi_id, state='hidden')
        else:
            if getattr(self.bot, "modo_app", "") == "dum":
                try:
                    dep = Decimal(str(getattr(self.bot, "inv_inic", "0")))
                except Exception:
                    dep = Decimal("0")
            



            self.bot.iniciar()
            if not self.bot.running:
                self.log_en_consola("⚠️ El bot no pudo iniciarse. Revisa configuración de operativa y coloca números válidos.")
                return
            if self.sound_enabled:
                reproducir_sonido("Sounds/inicio.wav")

            self.inicializar_valores_iniciales()

            self.btn_inicio.config(text="Detener")
            self.canvas_various.itemconfigure(self.btn_inicio_id, state='normal')
            self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')
            self.canvas_various.itemconfigure(self.btn_confi_id, state='normal')
            # ⬅️ AÑADIR: reflejar configuración actual en altares al iniciar
            if getattr(self.bot, "tp_enabled", False) and (self.bot.take_profit_pct or 0) > 0:
                self.set_take_profit_state("armed")
            else:
                self.set_take_profit_state("inactive")

            if getattr(self.bot, "sl_enabled", False) and (self.bot.stop_loss_pct or 0) > 0:
                self.set_stop_loss_state("armed")
            else:
                self.set_stop_loss_state("inactive")

            self._loop()

    def clear_bot(self):
        if self.bot.running:
            return
        # La limpieza invalida la configuración
        self.operativa_configurada = False
# 🔒 bloquear cualquier ciclo residual
        try:
            self.bot._stop_flag = True
            self.bot.running = False
        except Exception:
            pass
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
# 🟢 dejarlo “idle listo para iniciar”
        try:
            self.bot._stop_flag = False
            self.bot.running = False
        except Exception:
            pass
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
        # limpiar labels guardados
        for key in list(getattr(self, "info_labels", {}).keys()):
            canvas, lbl_id = self.info_labels[key]
            try:
                canvas.delete(lbl_id)
            except Exception:
                pass
        self.info_labels.clear()
        self.nd_canvas.clear()
        # 4) Reset variables visuales
        self.valores_iniciales.clear()
        self.colores_actuales.clear()

        # 6) Vaciar historial y consola
        try:
            self.historial.delete("1.0", tk.END)
        except Exception:
            pass

        self._hist_last_tx_n = 0
        self._hist_last_sell_n = 0
        self._hist_estado_pos_by_id.clear()
        self._hist_estado_pos_by_num.clear()
        self._hist_estado_cache_by_id.clear()
        self._hist_estado_cache_by_num.clear()

        self._con_estado_pos_by_id.clear()
        self._con_estado_pos_by_num.clear()
        self._con_estado_cache_by_id.clear()
        self._con_estado_cache_by_num.clear()
        self._estado_line_by_id.clear()
        self._estado_line_by_num.clear()

        try:
            # habilitar, borrar y volver a deshabilitar la consola
            self.consola.configure(state='normal')
            self.consola.delete("1.0", tk.END)
            self.consola.configure(state='disabled')
        except Exception:
            pass

        self._consola_buffer.clear()
        # resetear índices/contexto de la consola
        self._consola_last_n = 0
        self._ctx_ultimo_id = None
        self._ctx_ultimo_num = None
        # 7) Guardar la vista actual del usuario
        self.reset_animaciones()

        # 8) Destruir frames viejos
        try:
            self.left_frame.destroy()
            self.center_frame.destroy()
            self.animation_frame.destroy()
        except Exception:
            pass

        # 9) Reconstruir paneles
        self.left_panel()
        self.center_panel()
        self.animation_panel() 
        self.init_animation()
        self._aplicar_modus()
        # ⬅️ AÑADIR: reset visual de altares al limpiar
        try:
            self.set_take_profit_state("inactive")
            self.set_stop_loss_state("inactive")
        except Exception:
            pass

        # 8) Redibujar datos actuales (aunque estén vacíos)
        self.actualizar_ui()

        # 9) Restaurar botones
        self.btn_inicio.config(text="Iniciar")
        # Solo mostrar 'Iniciar' si ya hay operativa configurada
        if getattr(self, 'operativa_configurada', False):
            self.canvas_various.itemconfigure(self.btn_inicio_id, state='normal')
        else:
            self.canvas_various.itemconfigure(self.btn_inicio_id, state='hidden')

        self.canvas_various.itemconfigure(self.btn_limpiar_id, state='hidden')
        self.canvas_various.itemconfigure(self.btn_confi_id, state='normal')
        
        # 10) Forzar primer log de limpieza
        self.log_en_consola("🧹 Bot limpiado.")
        self.log_en_consola("- - - - - - - - - -")


    def _thread_callback(self, future):
        if future.cancelled():
            return
        if exc := future.exception():
            # Lo logueamos en la UI
            if self.root.winfo_exists():
                self.root.after(0, lambda:
                    self.log_en_consola(f"⚠️ Excepcion en hilo: {exc}")
                )
    
    """def open_calculator(self):
         # pasamos los balances actuales
        usdt_avail = self.bot.usdt
        btc_avail  = self.bot.btc
        CalculatorWindow(self.root, usdt_avail, btc_avail)"""

    def abrir_configuracion_subventana(self):
        # Si ya está abierta y no fue destruida, traerla al frente
        if self.config_ventana is not None and self.config_ventana.winfo_exists():
            self.config_ventana.lift()
            self.config_ventana.focus_force()
            return  # No abrir otra
        
        # Mientras estoy configurando, el botón Iniciar NO debe verse
        self.config_ventana = tk.Toplevel(self.root)
        self.config_ventana.title("Configuracion de operativa")
        self.config_ventana.configure(bg="DarkGoldenRod")


        # —— Tamaño de ventana (ajustable en 1 lugar) ——
        win_w, win_h = 900, 700
        self.config_ventana.geometry(f"{win_w}x{win_h}")
        self.config_ventana.resizable(False, False)
        
        def cerrar_config():
            detener_sonido_y_cerrar(self.config_ventana)
            self.config_ventana.destroy()
            self.config_ventana = None
        self.config_ventana.protocol("WM_DELETE_WINDOW", cerrar_config)

        # ===== Canvas principal =====
        pad= 0
        cfg_w, cfg_h = win_w - pad*2, win_h - pad*2
        self.cfg_canvas = tk.Canvas(self.config_ventana, width=cfg_w, height=cfg_h,
                                    highlightthickness=0, bd=0, relief='flat')
        self.cfg_canvas.pack(fill="both", expand=True)
       
                # ===== Fondo tipo mosaico (como los paneles principales) =====
        self.rellenar_mosaico(self.cfg_canvas, "imagenes/decoa/wall/rect_gray_0_new.png", escala=2)

        # ===== Helpers de layout sobre canvas =====
        left_x = 20              # margen izquierdo de etiquetas
        y = 24                   # primer renglón
        row = 42                 # separación vertical por fila
        font_lbl = ("LondonBetween", 18)
        color_lbl = "lime"

        def put_text(ypos, texto, color=color_lbl, size=16):
            return self.cfg_canvas.create_text(
                left_x, ypos, text=texto, anchor="nw",
                fill=color, font=("LondonBetween", size)
            )

        def put_entry_next_to(label_id, textvariable, width=14):
            # coloca el Entry pegado al texto (bbox del label)
            bbox = self.cfg_canvas.bbox(label_id)  # (x1, y1, x2, y2)
            x_entry = (bbox[2] + 12) if bbox else (left_x + 340)  # fallback
            e = tk.Entry(self.config_ventana, textvariable=textvariable,
                        bg="navy", fg="PaleGoldenRod",
                        insertbackground="PaleGoldenRod",
                        relief="flat", bd=0, highlightthickness=0,
                        font=("LondonBetween", 16), width=width)

            self.cfg_canvas.create_window(x_entry, bbox[1], anchor="nw", window=e)
            return e

        def put_check(ypos, text, variable):
            cb = tk.Checkbutton(self.config_ventana, text=text, variable=variable,
                                bg="navy", fg="PaleGoldenRod",
                                activebackground="PaleGoldenRod", activeforeground="PaleGoldenRod",
                                selectcolor="PaleGoldenRod",
                                font=("LondonBetween", 16),
                                highlightthickness=0, bd=0)
            self.cfg_canvas.create_window(left_x, ypos, anchor="nw", window=cb)
            return cb

        self.var_ghost = tk.BooleanVar(value=self.bot.compra_en_venta_fantasma)
        # ===== Checks de comportamiento (label en canvas + check centrado con bbox) =====
        # --- Comisiones ---
        text_id = self.cfg_canvas.create_text(left_x, y, text="Aplicar comisión (%)",
                                            fill="lime", font=("LondonBetween", 16), anchor="nw")
        bbox = self.cfg_canvas.bbox(text_id)
        x_check = bbox[2] + 10 if bbox else (left_x + 350)
        y_center = (bbox[1] + bbox[3]) / 2 if bbox else y
        self.var_comisiones_enabled = tk.BooleanVar(value=getattr(self.bot, "comisiones_enabled", True))
        self.chk_fee = tk.Checkbutton(self.config_ventana, variable=self.var_comisiones_enabled,
                                    text="", bg="navy", activebackground="navy",
                                    relief="flat", bd=0, highlightthickness=0,
                                    selectcolor="PaleGoldenRod", padx=0, pady=0, takefocus=0)
        self.cfg_canvas.create_window(x_check, y_center, anchor="w", window=self.chk_fee)
        y += row

        lbl = self.cfg_canvas.create_text(left_x, y, text="Porcentaje de comisión:",
                                        fill="lime", font=("LondonBetween", 16), anchor="nw")
        self.var_comision_pct = tk.StringVar(value=str(getattr(self.bot, "comision_pct", "0.1")))
        put_entry_next_to(lbl, self.var_comision_pct, width=8)
        y += row

        # --- Ghost ---
        text_id = self.cfg_canvas.create_text(left_x, y, text="Habilitar compra tras venta fantasma",
                                            fill="lime", font=("LondonBetween", 16), anchor="nw")
        bbox = self.cfg_canvas.bbox(text_id)
        x_check = bbox[2] + 10 if bbox else (left_x + 350)
        y_center = (bbox[1] + bbox[3]) / 2 if bbox else y
        self.var_ghost = tk.BooleanVar(value=self.bot.compra_en_venta_fantasma)
        self.chk_ghost = tk.Checkbutton(self.config_ventana, variable=self.var_ghost,
                                        text="", bg="navy", activebackground="navy",
                                        relief="flat", bd=0, highlightthickness=0,
                                        selectcolor="PaleGoldenRod", padx=0, pady=0, takefocus=0)
        self.cfg_canvas.create_window(x_check, y_center, anchor="w", window=self.chk_ghost)
        y += row

        # --- Take Profit ---
        text_id = self.cfg_canvas.create_text(left_x, y, text="Activar Take Profit",
                                            fill="lime", font=("LondonBetween", 16), anchor="nw")
        bbox = self.cfg_canvas.bbox(text_id)
        x_check = bbox[2] + 10 if bbox else (left_x + 350)
        y_center = (bbox[1] + bbox[3]) / 2 if bbox else y
        self.var_tp_enabled = tk.BooleanVar(value=getattr(self.bot, "tp_enabled", False))
        self.chk_tp = tk.Checkbutton(self.config_ventana, variable=self.var_tp_enabled,
                                    text="", bg="navy", activebackground="navy",
                                    relief="flat", bd=0, highlightthickness=0,
                                    selectcolor="PaleGoldenRod", padx=0, pady=0, takefocus=0)
        self.cfg_canvas.create_window(x_check, y_center, anchor="w", window=self.chk_tp)
        y += row

        # --- Stop Loss ---
        text_id = self.cfg_canvas.create_text(left_x, y, text="Activar Stop Loss",
                                            fill="lime", font=("LondonBetween", 16), anchor="nw")
        bbox = self.cfg_canvas.bbox(text_id)
        x_check = bbox[2] + 10 if bbox else (left_x + 350)
        y_center = (bbox[1] + bbox[3]) / 2 if bbox else y
        self.var_sl_enabled = tk.BooleanVar(value=getattr(self.bot, "sl_enabled", False))
        self.chk_sl = tk.Checkbutton(self.config_ventana, variable=self.var_sl_enabled,
                                    text="", bg="navy", activebackground="navy",
                                    relief="flat", bd=0, highlightthickness=0,
                                    selectcolor="PaleGoldenRod", padx=0, pady=0, takefocus=0)
        self.cfg_canvas.create_window(x_check, y_center, anchor="w", window=self.chk_sl)
        y += row + 6

        # --- Rebalance ---
        text_id = self.cfg_canvas.create_text(left_x, y, text="Activar Rebalance",
                                            fill="lime", font=("LondonBetween", 16), anchor="nw")
        bbox = self.cfg_canvas.bbox(text_id)
        x_check = bbox[2] + 10 if bbox else (left_x + 350)
        y_center = (bbox[1] + bbox[3]) / 2 if bbox else y
        self.var_rebalance_enabled = tk.BooleanVar(value=getattr(self.bot, "rebalance_enabled", False))
        self.chk_reb = tk.Checkbutton(self.config_ventana, variable=self.var_rebalance_enabled,
                                    text="", bg="navy", activebackground="navy",
                                    relief="flat", bd=0, highlightthickness=0,
                                    selectcolor="PaleGoldenRod", padx=0, pady=0, takefocus=0)
        self.cfg_canvas.create_window(x_check, y_center, anchor="w", window=self.chk_reb)
        y += row + 6

        # ===== Rebalance =====
        put_text(y, "* Rebalance *", color="PaleGoldenRod", size=18); y += row
        # Compras (umbral)
        lbl = put_text(y, "- - - - Compras Fantasma (umbral):", color="PaleGoldenRod")
        self.var_rebalance_threshold = tk.StringVar(value=str(getattr(self.bot, "rebalance_threshold", 6)))
        put_entry_next_to(lbl, self.var_rebalance_threshold, width=8); y += row

        # Porcentaje a vender
        lbl = put_text(y, "- - - - Porcentaje a vender: -%", color="PaleGoldenRod")
        self.var_rebalance_pct = tk.StringVar(value=str(getattr(self.bot, "rebalance_pct", 50)))
        put_entry_next_to(lbl, self.var_rebalance_pct, width=8); y += row

        # ===== Campos numéricos (MISMO ORDEN; entries intacto) =====
        campos = [
            ("% Desde compra, para compra: -%", self.bot.porc_desde_compra),
            ("% Desde venta, para compra: -%", self.bot.porc_desde_venta),
            ("% Para venta, desde compra: %", self.bot.porc_profit_x_venta),
            ("% A invertir por operaciones: %", self.bot.porc_inv_por_compra),
            ("Total Usdt: $", self.bot.inv_inic),
            ("Take Profit: %", self.bot.take_profit_pct or Decimal("0")),
            ("Stop Loss: -%", self.bot.stop_loss_pct or Decimal("0")),
        ]
        entries = []  # <- tu guardar_config depende de este nombre

        for etiqueta, valor in campos:
            lbl = put_text(y, etiqueta)
            var = tk.StringVar(value=str(valor))
            put_entry_next_to(lbl, var, width=16)
            entries.append(var)
            y += row

        

        # ===== guardar_config =====
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

                # =========================
                # DUM: "Total Usdt" = depósito desde Slot 1
                # =========================
                if getattr(self.bot, "modo_app", "") == "dum":
                    if self.bot.running:
                        self.log_en_consola("⚠️ En Dum no se puede modificar el depósito con el bot corriendo.")
                        self.log_en_consola("- - - - - - - - - -")
                        return

                    else:
                        try:
                            self._dum_aplicar_deposito(usdtinit)
                        except Exception as e:
                            self.log_en_consola(f"⚠️ {e}")
                            self.log_en_consola("- - - - - - - - - -")
                            return

                    # hook main menu (si existe)
                    try:
                        if callable(getattr(self, "_refrescar_main_menu", None)):
                            self._refrescar_main_menu()
                    except Exception:
                        pass

                

                tp = Decimal(txt_tp)
                sl = Decimal(txt_sl)

                # 1) SNAPSHOT de configuración anterior (para detectar cambios)
                old_cfg = {
                    "porc_desde_compra":   getattr(self.bot, "porc_desde_compra", Decimal("0")),
                    "porc_desde_venta":    getattr(self.bot, "porc_desde_venta", Decimal("0")),
                    "porc_profit_x_venta": getattr(self.bot, "porc_profit_x_venta", Decimal("0")),
                    "porc_inv_por_compra": getattr(self.bot, "porc_inv_por_compra", Decimal("0")),
                    "inv_inic":            getattr(self.bot, "inv_inic", Decimal("0")),

                    "tp_enabled":          getattr(self.bot, "tp_enabled", False),
                    "take_profit_pct":     getattr(self.bot, "take_profit_pct", None) or Decimal("0"),
                    "sl_enabled":          getattr(self.bot, "sl_enabled", False),
                    "stop_loss_pct":       getattr(self.bot, "stop_loss_pct", None) or Decimal("0"),

                    "comisiones_enabled":  getattr(self.bot, "comisiones_enabled", False),
                    "comision_pct":        getattr(self.bot, "comision_pct", Decimal("0")),

                    "rebalance_enabled":   getattr(self.bot, "rebalance_enabled", False),
                    "rebalance_threshold": getattr(self.bot, "rebalance_threshold", 0),
                    "rebalance_pct":       getattr(self.bot, "rebalance_pct", 0),

                    "compra_en_venta_fantasma": getattr(self.bot, "compra_en_venta_fantasma", False),
                }

                
                
                self.bot.comisiones_enabled = self.var_comisiones_enabled.get()
                 # porcentaje EXACTO como lo escribió el usuario
                raw = (self.var_comision_pct.get() or "").replace(",", ".")
                try:
                    self.bot.comision_pct = Decimal(raw)   # 4, 0.03, 200, etc. tal cual
                except (InvalidOperation, ValueError):
                    self.bot.comision_pct = Decimal("0")   # fallback
                
                if self.bot.comision_pct < 0:
                    self.bot.comision_pct = Decimal("0")

                # ⬇️ A G R E G A R AQUÍ
                old_tp_enabled = getattr(self.bot, "tp_enabled", False)
                old_tp_pct     = getattr(self.bot, "take_profit_pct", None) or Decimal("0")
                old_sl_enabled = getattr(self.bot, "sl_enabled", False)
                old_sl_pct     = getattr(self.bot, "stop_loss_pct", None) or Decimal("0")

                old_rb_enabled = getattr(self.bot, "rebalance_enabled", False)
                old_rb_thr     = getattr(self.bot, "rebalance_threshold", 0)
                old_rb_pct     = getattr(self.bot, "rebalance_pct", 0)    

                                # Validaciones Rebalance
                rebalance_activo = self.var_rebalance_enabled.get()

                # Parseamos siempre, pero solo mostramos errores si está activado
                try:
                    rb_thr = int(self.var_rebalance_threshold.get())
                except (TypeError, ValueError):
                    if rebalance_activo:
                        self.log_en_consola("⚠️ Umbral de rebalance inválido (debe ser entero).")
                        self.log_en_consola("- - - - - - - - - -")
                        return
                    else:
                        # si está desactivado, usamos el valor que ya tenía el bot (o 0)
                        rb_thr = getattr(self.bot, "rebalance_threshold", 0)

                try:
                    rb_pct = int(self.var_rebalance_pct.get())
                except (TypeError, ValueError):
                    if rebalance_activo:
                        self.log_en_consola("⚠️ % de Rebalance inválido (debe ser entero).")
                        self.log_en_consola("- - - - - - - - - -")
                        return
                    else:
                        rb_pct = getattr(self.bot, "rebalance_pct", 0)

                if rebalance_activo:
                    if rb_thr < 0:
                        self.log_en_consola("⚠️ El umbral de rebalance no puede ser negativo.")
                        self.log_en_consola("- - - - - - - - - -")
                        return
                    if not (1 <= rb_pct <= 100):
                        self.log_en_consola("⚠️ El % de rebalance debe estar entre 1 y 100.")
                        self.log_en_consola("- - - - - - - - - -")
                        return

                
                # 3) Validaciones > 0
                if porc_compra <= 0:
                    self.log_en_consola("⚠️ El porcentaje desde compra debe ser mayor que 0.")
                    self.log_en_consola("- - - - - - - - - -")
                    return
                if porc_venta <= 0:
                    self.log_en_consola("⚠️ El porcentaje desde venta debe ser mayor que 0.")
                    self.log_en_consola("- - - - - - - - - -")
                    return
                if porc_profit <= 0:
                    self.log_en_consola("⚠️ El porcentaje para venta debe ser mayor que 0.")
                    self.log_en_consola("- - - - - - - - - -")
                    return
                if porc_inv <= 0:
                    self.log_en_consola("⚠️ El porcentaje de inversión por compra debe ser mayor que 0.")
                    self.log_en_consola("- - - - - - - - - -")
                    return
                if usdtinit <= 0:
                    self.log_en_consola("⚠️ El capital inicial debe ser mayor que 0.")
                    self.log_en_consola("- - - - - - - - - -")
                    return
                if tp < 0:
                    self.log_en_consola("⚠️ El Take Profit debe ser mayor a 0.")
                    self.log_en_consola("- - - - - - - - - -")
                    return
                if sl < 0:
                    self.log_en_consola("⚠️ El Stop Loss debe mayor a 0.")
                    self.log_en_consola("- - - - - - - - - -")
                    return
                # Si se activan, deben ser > 0 (evitar detener instantáneamente)
                if self.var_tp_enabled.get() and tp <= 0:
                    self.log_en_consola("⚠️ Si activás el Take Profit, debe ser mayor que 0.")
                    self.log_en_consola("- - - - - - - - - -")
                    return
                if self.var_sl_enabled.get() and sl <= 0:
                    self.log_en_consola("⚠️ Si activás el Stop Loss, debe ser mayor que 0.")
                    self.log_en_consola("- - - - - - - - - -")
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
                # ⬅️ reflejar en altares la config recién guardada
                if self.bot.tp_enabled and (self.bot.take_profit_pct or 0) > 0:
                    self.set_take_profit_state("armed")
                else:
                    self.set_take_profit_state("inactive")

                if self.bot.sl_enabled and (self.bot.stop_loss_pct or 0) > 0:
                    self.set_stop_loss_state("armed")
                else:
                    self.set_stop_loss_state("inactive")

                self.bot.rebalance_enabled = self.var_rebalance_enabled.get()
                self.bot.rebalance_threshold = rb_thr
                self.bot.rebalance_pct = rb_pct

                try:
                    self._update_lamp_genie()
                except Exception:
                    pass

                old_inv_inic = old_cfg["inv_inic"]  # Decimal
                # Si estamos en DUM, revalidar cap también en vivo
                if getattr(self.bot, "modo_app", "") == "dum":
                    slot_cap = getattr(self.bot, "dum_slot_cap", Decimal("5000"))
                    disponible = getattr(self.bot, "dum_disponible", slot_cap)
                    maximo = min(Decimal(str(slot_cap)), Decimal(str(disponible)))

                    # Nota: si el bot ya estaba corriendo y querés permitir "aumentar depósito",
                    # esto debería descontar de wallet (obsidiana) y bajar dum_disponible.
                    # Por ahora: cap duro sin aumentar.
                    if usdtinit > self.bot.inv_inic and self.bot.running:
                        self.log_en_consola("⚠️ En Dum no se permite aumentar el depósito con el bot corriendo.")
                        self.log_en_consola("- - - - - - - - - -")
                        return

                    if usdtinit > slot_cap:
                        self.log_en_consola(f"⚠️ Límite Dum: {self.format_var(slot_cap, '$')}.")
                        self.log_en_consola("- - - - - - - - - -")
                        return

                # Ajuste de capital según si el bot está corriendo o no
                if self.bot.running:
                    # En modo normal (no dum) permitís ajuste vivo, si querés
                    if getattr(self.bot, "modo_app", "") != "dum":
                        delta = usdtinit - old_inv_inic
                        if delta != 0:
                            self.bot.usdt += delta
                            self.log_en_consola(
                                f"💰 Capital ajustado en vivo: {self.format_var(delta, '$')} → nuevo USDT: {self.format_var(self.bot.usdt, '$')}"
                            )
                else:
                    # detenido: fijar capital (modo normal)
                    if getattr(self.bot, "modo_app", "") != "dum":
                        self.bot.usdt = usdtinit


                # Recalcular fixed_buyer con el nuevo inv_inic
                self.bot.fixed_buyer = (
                    self.bot.inv_inic * self.bot.porc_inv_por_compra / Decimal('100')
                )

                # 5) Calculamos fixed_buyer y validamos
                #self.bot.fixed_buyer = (self.bot.inv_inic * self.bot.porc_inv_por_compra) / Decimal('100')
                if self.bot.fixed_buyer <= 0:
                    self.log_en_consola("⚠️ El monto de compra fijo debe ser mayor que 0.")
                    return
                
                self.bot.compra_en_venta_fantasma = self.var_ghost.get()

                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cambios = []

                def bool_str(v):
                    return "ON" if v else "OFF"

                def add_change(label, old_val, new_val, simbolo=""):
                    if old_val == new_val:
                        return
                    # Para Decimals / números
                    if isinstance(old_val, (Decimal, int, float)) and isinstance(new_val, (Decimal, int, float)):
                        old_s = self.format_var(old_val, simbolo)
                        new_s = self.format_var(new_val, simbolo)
                    else:
                        # strings / ON-OFF / enteros tipo umbral
                        old_s = str(old_val)
                        new_s = str(new_val)
                    cambios.append(f" · {label}: {old_s} → {new_s}")

                # === Comparar todos los campos importantes ===
                add_change("% desde compra",   old_cfg["porc_desde_compra"],   self.bot.porc_desde_compra, "%")
                add_change("% desde venta",    old_cfg["porc_desde_venta"],    self.bot.porc_desde_venta, "%")
                add_change("% profit venta",   old_cfg["porc_profit_x_venta"], self.bot.porc_profit_x_venta, "%")
                add_change("% por operación",  old_cfg["porc_inv_por_compra"], self.bot.porc_inv_por_compra, "%")
                add_change("Capital inicial",  old_cfg["inv_inic"],            self.bot.inv_inic, "$")

                add_change("TP habilitado",    bool_str(old_cfg["tp_enabled"]), bool_str(self.bot.tp_enabled))
                add_change("TP",             old_cfg["take_profit_pct"],      self.bot.take_profit_pct or Decimal("0"), "%")
                add_change("SL habilitado",    bool_str(old_cfg["sl_enabled"]), bool_str(self.bot.sl_enabled))
                add_change("SL",             old_cfg["stop_loss_pct"],        self.bot.stop_loss_pct or Decimal("0"), "%")

                add_change("Comisión aplicada", bool_str(old_cfg["comisiones_enabled"]), bool_str(self.bot.comisiones_enabled))
                add_change("Comisión",        old_cfg["comision_pct"],          self.bot.comision_pct, "%")

                add_change("Rebalance habilitado", bool_str(old_cfg["rebalance_enabled"]), bool_str(self.bot.rebalance_enabled))
                add_change("Rebalance umbral",     old_cfg["rebalance_threshold"],          self.bot.rebalance_threshold)
                add_change("Rebalance",          old_cfg["rebalance_pct"],               self.bot.rebalance_pct, "%")

                add_change("Compra en venta fantasma",
                           bool_str(old_cfg["compra_en_venta_fantasma"]),
                           bool_str(self.bot.compra_en_venta_fantasma))

                if cambios:
                    self.log_en_consola(f"{ts} · Configuración actualizada:")
                    for linea in cambios:
                        self.log_en_consola(linea)
                    self.log_en_consola("- - - - - - - - - -")
                else:
                    # No cambió nada respecto a la config anterior
                    self.log_en_consola(f"{ts} · Configuración guardada (sin cambios).")
                    self.log_en_consola("- - - - - - - - - -")
                
                # 🔄 Si el bot ya está corriendo, recalibrar baselines para los colores
                if self.bot.running:
                    try:
                        self.inicializar_valores_iniciales()
                        self.actualizar_ui()
                    except Exception as e:
                        self.log_en_consola(f"⚠️ No se pudieron recalibrar los colores: {e}")
                        self.log_en_consola("- - - - - - - - - -")

                self.operativa_configurada = True
                self.canvas_various.itemconfigure(self.btn_inicio_id, state='normal')
                cerrar_config()

            except (InvalidOperation, IndexError):
                self.log_en_consola("Error: ingresa valores numericos validos.")

        # ===== Botón Guardar (centrado abajo; se adapta si la ventana cambia) =====
        def _place_save_btn(event=None):
            # dejar 16 px del borde inferior
            cy = self.cfg_canvas.winfo_height() - 16
            cx = self.cfg_canvas.winfo_width() // 1.5
            try:
                self.cfg_canvas.coords(btn_id, cx, cy)
            except Exception:
                pass

        btn_guardar = tk.Button(self.config_ventana, text="Guardar",
                                bg="Crimson", fg="PaleGoldenRod",
                                font=("LondonBetween", 16),
                                command=guardar_config)
        btn_id = self.cfg_canvas.create_window(cfg_w // 2, cfg_h - 16, anchor="s", window=btn_guardar)
        self.cfg_canvas.bind("<Configure>", _place_save_btn)

    def _on_close(self):
        detener_musica_fondo()
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

    def _dum_aplicar_deposito(self, nuevo_deposito: Decimal):
                
                """
                Dum: mueve obsidiana <-> depósito (USDT) y deja el bot consistente.
                Reglas:
                - Respeta cap del slot (SLOT_1_OBSIDIANA en main menu se lo pasás como dum_slot_cap)
                - Permite cambiar depósito SOLO con bot detenido (pre-run)
                """
                if not self.usuario:
                    raise ValueError("usuario no definido")

                cap = Decimal(str(getattr(self.bot, "dum_slot_cap", "5000")))
                ya  = Decimal(str(getattr(self.bot, "dum_deposito", "0")))

                # wallet actual
                obs_s, quad_s = get_wallet(self.usuario)
                obs  = Decimal(str(obs_s))
                quad = Decimal(str(quad_s))

                # máximo permitido: cap y lo que podés juntar entre (obs disponible + lo ya depositado)
                maximo = min(cap, obs + ya)

                if nuevo_deposito < 0:
                    raise ValueError("El depósito no puede ser negativo")
                
                minimo = Decimal("100")
                if nuevo_deposito != 0 and nuevo_deposito < minimo:
                    raise ValueError(f"Depósito mínimo disponible: {minimo}")

                if nuevo_deposito > maximo:
                    raise ValueError(f"Depósito máximo disponible: {maximo}")

                # delta vs lo ya depositado
                delta = nuevo_deposito - ya

                # aplicar delta al wallet
                if delta > 0:
                    # aumentar depósito: descontar obsidiana
                    if obs < delta:
                        raise ValueError("No tenés suficiente obsidiana para aumentar el depósito")
                    obs -= delta
                elif delta < 0:
                    # reducir depósito: devolver obsidiana
                    obs += (-delta)

                # persistir wallet
                set_wallet(self.usuario, obs, quad)

                # dejar bot consistente
                self.bot.dum_deposito  = nuevo_deposito
                self.bot.dum_slot_used = nuevo_deposito   # slot usado en esta run (al iniciar)

                # en Dum, el capital del bot = depósito
                self.bot.inv_inic = nuevo_deposito
                self.bot.usdt     = nuevo_deposito

                # informativo: disponible actual
                self.bot.dum_disponible = obs

                # persistir perfil dum (deposito)
                perfil = cargar_perfil(self.usuario)
                if not isinstance(perfil, dict):
                    perfil = {}
                di = (perfil.get("dum", {}) or {})
                di["deposito"] = str(nuevo_deposito)
                perfil["dum"] = di
                guardar_perfil(self.usuario, perfil)

    def _loop(self):
        # Si el bot ya no corre o la ventana ya no existe, salimos
        if not self.bot.running:
            return
        if not self.root.winfo_exists():
            return

        # Ejecutamos el ciclo de trading en segundo plano
        future = self.executor.submit(self._run_trading_cycle)

        def _replanear_en_main():
            try:
                if self.root.winfo_exists() and self.bot.running:
                    self.root.after(3000, self._loop)
            except Exception as e:
                print(f"[⚠️ Error after loop]: {e}")

        try:
            self.root.after(0, _replanear_en_main)
        except Exception:
            pass

    def _run_trading_cycle(self):
        try:
            # ⛔️ si ya está detenido, no hacemos nada
            if not self.bot.running or getattr(self.bot, "_stop_flag", False):
                return
            # 1) Intentamos obtener el ticker
            ticker = self.bot.exchange.fetch_ticker('BTC/USDT')
            price = ticker['last']
            if not self.bot.running or getattr(self.bot, "_stop_flag", False):
                return
            # – Si salió bien, guardamos el precio y ejecutamos el ciclo de trading:
            self.bot.precio_actual = price
            self.bot.modus_actual = self.modus.get()
            self.bot.loop()
        except Exception as exc:
            # Si falla, dejamos precio_actual en None para detectar desconexión
            self.bot.precio_actual = None

            if self.sound_enabled:
                reproducir_sonido("Sounds/sin_conexion.wav")

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

        # intenta Decimal siempre, incluso si vino como string
        try:
            d = Decimal(str(valor))
        except Exception:
            s = str(valor).strip()
            return f"{simbolo} {s}" if simbolo and s else s

        if d == 0:
            return f"{simbolo} 0" if simbolo else "0"

        # base en string plano
        s = format(d, "f")  # sin notación científica

        # === modo de vista ===
        modo = self.display_mode.get() if hasattr(self, 'display_mode') else 'decimal'
        prec = self.float_precision if hasattr(self, 'float_precision') else 4

        if modo == 'decimal':
            # limpiar ceros de más, sin redondear
            if "." in s:
                s = s.rstrip("0").rstrip(".") or "0"
        else:
            # cortar decimales a 'prec' (sin redondeo)
            if "." in s and prec >= 0:
                entero, frac = s.split(".", 1)
                s = entero if prec == 0 else f"{entero}.{frac[:prec]}"
                s = s.rstrip("0").rstrip(".") or "0"
                
        if s in ("-0", "-0.0"):
            s = "0"

        return f"{simbolo} {s}" if simbolo else s

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
                "diff_hodl": (self.bot.diff_vs_hold_usdt(), "$"),
                "variacion_total_inv_usdt": (self.bot.variacion_total_usdt(), "$"),
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
                #"hold_btc": (self.bot.hold_btc_var, "₿"),
                "btcnusdt": (self.bot.btc_usdt, "$"),
                "excedente_compras": (self.bot.excedente_total_compras, "%"),
                "excedente_ventas": (self.bot.excedente_total_ventas, "%"),
                "excedente_total": (self.bot.excedente_total_compras + self.bot.excedente_total_ventas, "%"),
                "take_profit": ((self.bot.take_profit_pct, "%") if (getattr(self.bot, "tp_enabled", False) and (self.bot.take_profit_pct or Decimal("0")) > 0) else ("", "")),
                "stop_loss":  ((self.bot.stop_loss_pct, "%")  if (getattr(self.bot, "sl_enabled", False) and (self.bot.stop_loss_pct  or Decimal("0")) > 0) else ("", "")),
                "rebalances": self.bot.rebalance_count,
                "rebalance_loss_total": (getattr(self.bot, "rebalance_loss_total", Decimal("0")), "$"),
                "rebalance_thr": (self.bot.rebalance_threshold if getattr(self.bot, "rebalance_enabled", False) else ""),
                "rebalance_pct": ((self.bot.rebalance_pct, "%") if getattr(self.bot, "rebalance_enabled", False) else ("","")),
                "total_fees_buy": (self.bot.total_fees_buy, "$"),
                "total_fees_sell": (self.bot.total_fees_sell, "$"),
                "total_fees_total": (self.bot.total_fees_buy + self.bot.total_fees_sell, "$"),
                "comision_pct": (self.bot.comision_pct, "%"),
                "total_fees_btc": (getattr(self.bot, "total_fees_btc", Decimal("0")), "₿"),
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
            # ─── Ocultar TP/SL si están desactivados ───
            try:
                if not getattr(self.bot, "tp_enabled", False):
                    if "take_profit" in self.info_canvas:
                        canvas, item_id = self.info_canvas["take_profit"]
                        canvas.itemconfigure(item_id, state='hidden')
                    if "take_profit" in self.info_labels:
                        canvas, lbl_id = self.info_labels["take_profit"]
                        canvas.itemconfigure(lbl_id, state='hidden')
                else:
                    if "take_profit" in self.info_canvas:
                        canvas, item_id = self.info_canvas["take_profit"]
                        canvas.itemconfigure(item_id, state='normal')
                    if "take_profit" in self.info_labels:
                        canvas, lbl_id = self.info_labels["take_profit"]
                        canvas.itemconfigure(lbl_id, state='normal')

                if not getattr(self.bot, "sl_enabled", False):
                    if "stop_loss" in self.info_canvas:
                        canvas, item_id = self.info_canvas["stop_loss"]
                        canvas.itemconfigure(item_id, state='hidden')
                    if "stop_loss" in self.info_labels:
                        canvas, lbl_id = self.info_labels["stop_loss"]
                        canvas.itemconfigure(lbl_id, state='hidden')
                else:
                    if "stop_loss" in self.info_canvas:
                        canvas, item_id = self.info_canvas["stop_loss"]
                        canvas.itemconfigure(item_id, state='normal')
                    if "stop_loss" in self.info_labels:
                        canvas, lbl_id = self.info_labels["stop_loss"]
                        canvas.itemconfigure(lbl_id, state='normal')
                        # ─── Ocultar/mostrar Umbral y % de Rebalance según rebalance_enabled ───
            except Exception:
                pass
                                # ─── Ocultar/mostrar TODO lo relacionado a Rebalance según rebalance_enabled ───
            try:
                reb_on = getattr(self.bot, "rebalance_enabled", False)

                keys_reb = (
                    "rebalance_thr",         # umbral
                    "rebalance_pct",         # porcentaje
                    "rebalances",            # contador de rebalances realizados
                    "rebalance_loss_total",  # pérdidas por rebalance
                )

                for key in keys_reb:
                    if key in self.info_canvas:
                        canvas, item_id = self.info_canvas[key]
                        canvas.itemconfigure(item_id, state='normal' if reb_on else 'hidden')
                    if key in self.info_labels:
                        canvas, lbl_id = self.info_labels[key]
                        canvas.itemconfigure(lbl_id, state='normal' if reb_on else 'hidden')
            except Exception:
                pass


            

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
                    self.log_en_consola("- - - - - - - - - -")
                    
                    if self.sound_enabled:
                        reproducir_sonido("Sounds/reconexion.wav")
                    
                    self.inicializar_valores_iniciales()
                self._prev_price_ui = actual

                # Ya tenemos self.bot.precio_actual cargado desde el hilo de trading
                if actual is None:
                    return
                                
        except Exception as exc_ui:
                self.log_en_consola(f"❌ Error UI: {exc_ui}")       

        self.actualizar_consola()
        # Vuelve a aplicar ocultamiento tras redibujar valores
        try:
            self._aplicar_modus()
        except Exception:
            pass

    def actualizar_historial(self):
        try:
            if not hasattr(self, "historial"):
                return

            try:
                self.historial.configure(state="normal")
            except Exception:
                pass

            # === (A) PARCHEAR ESTADOS YA IMPRESOS (sin reconstruir) ===
            # Recorremos todas las transacciones y actualizamos solo si cambió
            for t in self.bot.transacciones:
                tx_id = str(t.get("id", "")).strip()
                numc  = str(t.get("numcompra", "")).strip()
                estado = t.get("estado", "activa")

                if tx_id:
                    prev = self._hist_estado_cache_by_id.get(tx_id)
                    if prev is not None and prev != estado:
                        self._hist_patch_estado(id_compra=tx_id, nuevo_estado=estado)
                    self._hist_estado_cache_by_id[tx_id] = estado

                if numc:
                    prevn = self._hist_estado_cache_by_num.get(numc)
                    if prevn is not None and prevn != estado:
                        self._hist_patch_estado(numcompra=numc, nuevo_estado=estado)
                    self._hist_estado_cache_by_num[numc] = estado

            # === (B) COMPRAS NUEVAS (solo append) ===
            txs = self.bot.transacciones
            start_tx = getattr(self, "_hist_last_tx_n", 0)
            if start_tx < 0:
                start_tx = 0

            for t in txs[start_tx:]:
                ts = t.get("timestamp", "")
                estado = t.get("estado", "activa")
                tx_id = str(t.get("id", "")).strip()
                numc  = str(t.get("numcompra", "")).strip()

                self.historial.insert(tk.END, "🟦 Compra realizada:\n", "compra_tag")
                self.historial.insert(tk.END, f"Precio de compra: {self.format_var(t.get('compra', ''), '$')}\n")
                self.historial.insert(tk.END, f"Id: {t.get('id','')}\n")
                self.historial.insert(tk.END, f"Número de compra: {t.get('numcompra','')}\n")

                # ✅ guardamos posición EXACTA donde arranca la línea "Estado:"
                estado_pos = self.historial.index(tk.END)
                self.historial.insert(tk.END, f"Estado: {estado}\n")

                # ✅ registramos esa posición para parche futuro
                if tx_id:
                    self._hist_estado_pos_by_id[tx_id] = estado_pos
                    self._hist_estado_cache_by_id[tx_id] = estado
                if numc:
                    self._hist_estado_pos_by_num[numc] = estado_pos
                    self._hist_estado_cache_by_num[numc] = estado

                self.historial.insert(tk.END, f"Fecha y hora: {ts}\n")
                self.historial.insert(tk.END, f"Btc/usdt comprado: {self.format_var(t.get('valor_en_usdt',''), '$')}\n")

                if "fee_usdt" in t:
                    self.historial.insert(tk.END, f"Comisión: {self.format_var(t['fee_usdt'], '$')}\n")
                if "fee_btc" in t:
                    self.historial.insert(tk.END, f"Comisión BTC: {self.format_var(t['fee_btc'], '₿')}\n")
                if "venta_obj" in t:
                    self.historial.insert(tk.END, f"Objetivo de venta: {self.format_var(t['venta_obj'], '$')}\n")

                self.historial.insert(tk.END, "-" * 40 + "\n")

            self._hist_last_tx_n = len(txs)

            # === (C) VENTAS NUEVAS (solo append) ===
            vs = self.bot.precios_ventas
            start_v = getattr(self, "_hist_last_sell_n", 0)
            if start_v < 0:
                start_v = 0

            for v in vs[start_v:]:
                ts = v.get("timestamp", "")
                self.historial.insert(tk.END, "🟩 Venta realizada:\n", "venta_tag")
                self.historial.insert(tk.END, f"Precio de compra: {self.format_var(v.get('compra',''), '$')}\n")
                self.historial.insert(tk.END, f"Precio de venta: {self.format_var(v.get('venta',''), '$')}\n")
                if "fee_usdt" in v:
                    self.historial.insert(tk.END, f"Comisión: {self.format_var(v['fee_usdt'], '$')}\n")
                self.historial.insert(tk.END, f"Id compra: {v.get('id_compra','')}\n")
                if "ganancia" in v:
                    self.historial.insert(tk.END, f"Ganancia: {self.format_var(v['ganancia'], '$')}\n")
                self.historial.insert(tk.END, f"Número de venta: {v.get('venta_numero','')}\n")
                self.historial.insert(tk.END, f"Fecha y hora: {ts}\n")
                self.historial.insert(tk.END, "-" * 40 + "\n")

            self._hist_last_sell_n = len(vs)

            try:
                self.historial.configure(state="disabled")
            except Exception:
                pass

        except Exception:
            pass

    def _consola_patch_estado(self, id_compra=None, numcompra=None, nuevo_estado="vendida"):
        txt = self.consola
        if (not id_compra) and (numcompra in (None, "")):
            return

        try:
            if id_compra:
                idx = self._estado_line_by_id.get(str(id_compra).strip())
                if idx:
                    line_start = idx
                    line_end = f"{int(idx.split('.')[0]) + 1}.0"
                    txt.configure(state="normal")
                    txt.delete(line_start, line_end)
                    txt.insert(line_start, f"📜 Estado: {nuevo_estado}\n")
                    txt.configure(state="disabled")
                    return

            if numcompra not in (None, ""):
                idx = self._estado_line_by_num.get(str(numcompra).strip())
                if idx:
                    line_start = idx
                    line_end = f"{int(idx.split('.')[0]) + 1}.0"
                    txt.configure(state="normal")
                    txt.delete(line_start, line_end)
                    txt.insert(line_start, f"📜 Estado: {nuevo_estado}\n")
                    txt.configure(state="disabled")
                    return
        except Exception:
            pass


    def actualizar_consola(self):
        """
        Incremental append-only:
        - NO borra contenido existente.
        - NO usa see() / yview_*().
        - Corrige '📜 Estado' SOLO en líneas nuevas basándose en estado vivo.
        - Mantiene contexto incremental de Id/Num.
        """
        try:
            def _fmt(v):
                if isinstance(v, tuple):
                    val, sim = v
                else:
                    val, sim = v, ""
                return self.format_var(val, sim)

            # mapa vivo de estados
            estado_por_id = {}
            estado_por_num = {}
            try:
                for t in self.bot.transacciones:
                    tx_id = t.get("id")
                    if tx_id:
                        estado_por_id[str(tx_id).strip()] = t.get("estado", "activa")
                    numc = t.get("numcompra")
                    if numc is not None:
                        estado_por_num[str(numc).strip()] = t.get("estado", "activa")
            except Exception:
                pass

            re_id = re.compile(
                r'(?:🪙\s*)?Compra\s+id\s*:\s*([A-Za-z0-9\-_]+)|\bId(?:\s+compra)?\s*:\s*([A-Za-z0-9\-_]+)',
                re.IGNORECASE
            )
            re_num = re.compile(
                r'(?:🪙\s*)?Compra\s+Num\s*:\s*(\d+)|N[úu]mero\s+de\s+compra\s*:\s*(\d+)',
                re.IGNORECASE
            )
            re_estado = re.compile(r'^\s*📜\s*Estado\s*:\s*(.+)\s*$')
            re_divisor = re.compile(r'^\s*-\s-(?:\s-)+\s*$')

            # Reinicio seguro del puntero de consola (corrige bug tras limpiar)
            start = getattr(self, "_consola_last_n", 0)
            if start > len(self._consola_buffer):
                start = 0  # evita índice fuera de rango si se limpió
            self._consola_last_n = start  # asegura coherencia
            nuevos = self._consola_buffer[start:]
            if not nuevos:
                return

            self.consola.configure(state='normal')

            # contexto incremental previo
            ultimo_id = getattr(self, "_ctx_ultimo_id", None)
            ultimo_num = getattr(self, "_ctx_ultimo_num", None)

            for entry in nuevos:
                kind = entry[0]
                if kind == "raw":
                    _, msg = entry
                    linea = self._reformat_line(msg)
                elif kind == "fmt":
                    _, tpl, vals = entry
                    linea = tpl.format(**{k: _fmt(v) for k, v in vals.items()})
                    linea = self._reformat_line(linea)
                else:
                    continue

                m_id = re_id.search(linea)
                if m_id:
                    ultimo_id = (m_id.group(1) or m_id.group(2) or "").strip() or ultimo_id

                m_num = re_num.search(linea)
                if m_num:
                    ultimo_num = (m_num.group(1) or m_num.group(2) or "").strip() or ultimo_num

                # índice donde empezará la próxima inserción (línea exacta, sin mover scroll)
                line_start_idx = self.consola.index("end-1c linestart")

                if re_estado.match(linea):
                    estado_actual = None
                    if ultimo_id and ultimo_id in estado_por_id:
                        estado_actual = estado_por_id[ultimo_id]
                    elif ultimo_num and ultimo_num in estado_por_num:
                        estado_actual = estado_por_num[ultimo_num]

                    if estado_actual:
                        linea = f"📜 Estado: {estado_actual}"

                        # ✅ guardar dónde quedó esa línea "Estado" para parches futuros
                        if ultimo_id:
                            self._estado_line_by_id[str(ultimo_id)] = line_start_idx
                        if ultimo_num:
                            self._estado_line_by_num[str(ultimo_num)] = line_start_idx


                if re_divisor.match(linea):
                    ultimo_id = None
                    ultimo_num = None

                self.consola.insert(tk.END, linea + "\n")

            self.consola.configure(state='disabled')

            # guardar progreso y contexto
            self._consola_last_n = start + len(nuevos)
            self._ctx_ultimo_id = ultimo_id
            self._ctx_ultimo_num = ultimo_num

        except Exception:
            pass

    def _consola_patch_estado_pos(self, line_start_idx: str, nuevo_estado: str):
        """
        Parchea IN-PLACE la línea exacta donde está '📜 Estado: ...'
        usando el índice guardado (ej: '120.0'). No mueve scroll.
        """
        try:
            if not line_start_idx:
                return

            txt = self.consola
            line_no = int(str(line_start_idx).split(".")[0])
            line_start = f"{line_no}.0"
            line_end   = f"{line_no + 1}.0"

            txt.configure(state="normal")
            txt.delete(line_start, line_end)
            txt.insert(line_start, f"📜 Estado: {nuevo_estado}\n")
            txt.configure(state="disabled")
        except Exception:
            pass

    def actualizar_color(self, key, valor_actual):
        if valor_actual is None or key not in self.info_canvas:
            return

        try:
            # desempaquetar si viene como (valor, simbolo)
            if isinstance(valor_actual, tuple):
                val_act_raw, _ = valor_actual
            else:
                val_act_raw = valor_actual

            # 🔒 si no hay valor numérico, no comparo ni convierto
            if val_act_raw in (None, ""):
                color = "Gold"
            else:
                val_act = Decimal(str(val_act_raw).strip())

                val_ini_raw = self.valores_iniciales.get(key)
                if val_ini_raw in (None, ""):
                    color = "Gold"
                else:
                    val_ini = Decimal(str(val_ini_raw).strip())
                    if val_act > val_ini:
                        color = "lime"
                    elif val_act < val_ini:
                        color = "Crimson"
                    else:
                        color = "Gold"

        except Exception:
            # antes imprimía el error; lo silenciamo s para no ensuciar la consola
            color = "Gold"

        # redibujar el texto con el color decidido
        self.colores_actuales[key] = color
        canvas, item_id = self.info_canvas[key]
        coords = canvas.coords(item_id)
        x, y = coords if coords and len(coords) == 2 else (20, 10)

        canvas.delete(item_id)
        texto = self.format_fijo(key, valor_actual)  # si el valor es None, ya devuelve ""
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
        if not hasattr(self, "_consola_buffer"):
            self._consola_buffer = []

        texto = self._reformat_line(str(msg))

        # Si el mensaje anuncia cambio de estado, parchear IN-PLACE
        try:
            m = re.search(
                r"Estado\s+de\s+compra\s*#\s*(\d+)\s*\(id\s*([A-Za-z0-9\-_]+)\)\s*:\s*([^\-]+?)\s*→\s*(\w+)",
                texto, flags=re.IGNORECASE
            )
            if m:
                numc_str, idc, _estado_viejo, estado_nuevo = m.groups()
                numc = int(numc_str)
                self._consola_patch_estado(id_compra=idc,  nuevo_estado=estado_nuevo)
                self._consola_patch_estado(numcompra=numc, nuevo_estado=estado_nuevo)
        except Exception:
            pass

        # Solo buffer; NO insert directo (para evitar duplicados)
        self._consola_buffer.append(("raw", str(msg)))

        # Render incremental de lo nuevo
        self.actualizar_consola()

    def inicializar_valores_iniciales(self):

        def safe(val):
            try:
                return Decimal(str(val)) if val is not None else Decimal("0")
            except:
                return Decimal("0")

        if self.bot.precio_actual is None:
            return

        self.bot.hold_usdt_var = self.bot.hold_usdt()
        self.bot.hold_btc_var  = self.bot.hold_btc()

        # 🔧 Baselines “intencionales” para el color:
        self.valores_iniciales = {
            # balance se compara contra la inversión inicial (no el balance post-compra)
            'balance':               safe(self.bot.inv_inic),
            # estas comparan contra 0 para pintar por signo (+ verde / - rojo)
            'variacion_total_inv':   Decimal('0'),
            'variacion_desde_inicio':Decimal('0'),
            'desde_ult_comp':        Decimal('0'),
            'ult_vent':              Decimal('0'),
            # Los que son info comparativa: se mantienen por si los usás en color
            'precio_actual':         safe(self.bot.precio_actual),
            'hold_usdt':             safe(self.bot.hold_usdt_var),
            'diff_hodl': Decimal("0"),
            'variacion_total_inv_usdt': Decimal("0"),
            #'hold_btc':              safe(self.bot.hold_btc_var),
        }

    def run(self):
        if self._owns_mainloop:
            try:
                self.root.mainloop()
            except KeyboardInterrupt:
                pass
