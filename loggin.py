# © 2025 Dungeon Market (Loggin)
# Todos los derechos reservados.

import tkinter as tk
from PIL import Image, ImageTk

from database import (
    init_db,
    agregar_usuario,
    validar_usuario,
    usuario_existe,
    guardar_perfil,
    init_wallet,
    cargar_perfil,
    get_wallet,
    set_wallet,
)

from player import DumWindow, depositar_a_bot
from dum import DumTranslator
from codigo_principala import TradingBot
from interfaz import BotInterfaz


# =========================
# Constantes UI
# =========================
ICON_MAIN_PATH = "imagenes/icon/urand_eternal_torment.ico"
ICON_DUM_PATH  = "imagenes/icon/cigotuvis_monster.ico"
BG_PATH        = "imagenes/decoa/wall/catacombs_5.png"

BALROG_LEFT_PATH  = "imagenes/deco/balrug_old.png"
BALROG_RIGHT_PATH = "imagenes/deco/balrug_new.png"


init_db()

ventana_loggin = tk.Tk()
ventana_loggin.title("Loggin")
ventana_loggin.geometry("400x200")
ventana_loggin.config(background="PaleGoldenRod")
ventana_loggin.iconbitmap(ICON_MAIN_PATH)


def cerrar_app():
    ventana_loggin.destroy()

ventana_loggin.protocol("WM_DELETE_WINDOW", cerrar_app)


# flags para evitar duplicar ventana
crear_user_win = False
user_win_ref = None


def crear_user():
    global user_win_ref, crear_user_win

    if user_win_ref is not None and user_win_ref.winfo_exists():
        user_win_ref.lift()
        user_win_ref.focus_force()
        return

    if crear_user_win:
        return

    crear_user_win = True

    user_win = tk.Toplevel(ventana_loggin)
    user_win_ref = user_win
    user_win.geometry("400x200")
    user_win.title("Creación De Usuario - Dungeon Market")
    user_win.config(background="PaleGoldenRod")

    def cerrar_user():
        global user_win_ref, crear_user_win
        crear_user_win = False
        try:
            user_win.destroy()
        except Exception:
            pass
        user_win_ref = None

    user_win.protocol("WM_DELETE_WINDOW", cerrar_user)

    tk.Label(
        user_win,
        text="Saludos!",
        font=("Carolingia", 18),
        background="PaleGoldenRod"
    ).pack(anchor="center", pady=10)

    tk.Label(
        user_win,
        text="Nombre: ",
        font=("Carolingia", 18),
        background="PaleGoldenRod"
    ).pack(anchor="w")

    nombre_entry = tk.Entry(user_win)
    nombre_entry.pack(anchor="w")

    tk.Label(
        user_win,
        text="Contraseña: ",
        font=("Carolingia", 18),
        background="PaleGoldenRod"
    ).pack(anchor="w")

    pass_entry = tk.Entry(user_win)
    pass_entry.pack(anchor="w")

    def guardar_usuario():
        nonlocal user_win
        nombre = nombre_entry.get().strip()
        password = pass_entry.get().strip()

        if not nombre or not password:
            print("Campos vacíos")
            return

        if agregar_usuario(nombre, password):
            print("Usuario creado correctamente")
            init_wallet(nombre)
            guardar_perfil(nombre, {"dum": {"deposito": "0", "slot_used_last": "0"}, "avatar": {}})
            crear_user_win = False
            user_win.destroy()
        else:
            print("Ese usuario ya existe")

    tk.Button(
        user_win,
        text="Crear",
        font=("Carolingia", 18),
        command=guardar_usuario
    ).pack(pady=10)


def rellenar_mosaico(canvas, image_path, escala=1):
    imagen_original = Image.open(image_path)
    ancho, alto = imagen_original.size
    imagen_redimensionada = imagen_original.resize(
        (ancho * escala, alto * escala),
        resample=Image.Resampling.NEAREST
    )

    imagen = ImageTk.PhotoImage(imagen_redimensionada)

    if not hasattr(canvas, 'imagenes'):
        canvas.imagenes = []
    canvas.imagenes.append(imagen)

    width = int(canvas['width'])
    height = int(canvas['height'])

    for x in range(0, width, imagen.width()):
        for y in range(0, height, imagen.height()):
            canvas.create_image(x, y, image=imagen, anchor='nw')


def main_menu(nombre: str):
    main_menu_var = tk.Toplevel(ventana_loggin)
    main_menu_var.geometry("750x800")
    main_menu_var.title("Dungeon Market - Main Menu")
    main_menu_var.iconbitmap(ICON_MAIN_PATH)

    canvas_menu = tk.Canvas(main_menu_var, width=750, height=800, highlightthickness=0, bd=0)
    canvas_menu.pack(fill="both", expand=True)

    rellenar_mosaico(canvas_menu, BG_PATH, escala=2)

    # =========================
    # 1) Crear primero la ventana Dum (HUD)
    # =========================
    dungeon_win = None  # se asigna abajo

    def refrescar_menu():
        # refresco manual (lo llama el bot vía hook)
        try:
            if dungeon_win is not None:
                dungeon_win.refresh()
        except Exception:
            pass

    # =========================
    # 2) Bot Khazad (Libre) + Bot Khazad (Dum)
    # =========================
    khazad_win = {"open": False, "app": None}
    khazad_dum_win = {"open": False, "app": None}

    def abrir_khazad():
        if khazad_win["open"]:
            try:
                khazad_win["app"].root.lift()
                khazad_win["app"].root.focus_force()
            except Exception:
                pass
            return

        bot = TradingBot()
        bot.modo_app = "libre"

        app = BotInterfaz(bot, master=ventana_loggin, usuario=nombre)

        try:
            app.root.iconbitmap(ICON_MAIN_PATH)
        except Exception:
            pass

        app._refrescar_main_menu = refrescar_menu

        khazad_win["open"] = True
        khazad_win["app"] = app

        def _al_cerrar():
            khazad_win["open"] = False
            try:
                app.root.destroy()
            except Exception:
                pass

        app.root.protocol("WM_DELETE_WINDOW", _al_cerrar)

    def abrir_khazad_dum():
        if khazad_dum_win["open"]:
            try:
                khazad_dum_win["app"].root.lift()
                khazad_dum_win["app"].root.focus_force()
            except Exception:
                pass
            return

        bot = TradingBot()
        bot.modo_app = "dum"
        # =========================
        # Dum: depositar slot desde wallet -> bot
        # =========================
        deposito = depositar_a_bot(nombre, bot)
        
        if deposito <= 0:
            print("No hay obsidiana disponible para depositar en Dum.")
            return

        # Guardar estado dum en perfil (para HUD)
        perfil = cargar_perfil(nombre)
        if not isinstance(perfil, dict):
            perfil = {}
        dum_state = (perfil.get("dum", {}) or {})
        dum_state["deposito"] = str(deposito)
        dum_state["slot_used_last"] = str(deposito)  # lo usado en esta run al inicio
        perfil["dum"] = dum_state
        guardar_perfil(nombre, perfil)
        refrescar_menu()

        # =========================
        # Dum: translator + persistencia a wallet
        # =========================
        dum_persistido = {"ok": False}  # evita doble persistencia

        def persistir_dum(resultado):
            # Evitar doble ejecución
            if dum_persistido["ok"]:
                return
            dum_persistido["ok"] = True

            # 1) devolver a wallet lo que corresponde
            obs_actual, quad_actual = get_wallet(resultado.usuario)
            nuevo_obs = obs_actual + resultado.obsidiana_vuelve
            nuevo_quad = quad_actual + resultado.quad_ganado
            set_wallet(resultado.usuario, nuevo_obs, nuevo_quad)

            # 2) actualizar perfil dum para HUD (deposito vuelve a 0)
            perfil = cargar_perfil(resultado.usuario)
            if not isinstance(perfil, dict):
                perfil = {}
            dum_state = (perfil.get("dum", {}) or {})
            dum_state["deposito"] = "0"
            dum_state["slot_used_last"] = str(resultado.slot)
            perfil["dum"] = dum_state
            guardar_perfil(resultado.usuario, perfil)
            refrescar_menu()

        dum_translator = DumTranslator(persist_callback=persistir_dum)


        app = BotInterfaz(bot, master=ventana_loggin, usuario=nombre)

        try:
            app.root.iconbitmap(ICON_DUM_PATH)
        except Exception:
            pass

        app._refrescar_main_menu = refrescar_menu

        khazad_dum_win["open"] = True
        khazad_dum_win["app"] = app
        cerrando = {"ok": False}

        def _al_cerrar():
            # Dum: cerrar run y persistir (una sola vez)
            if cerrando["ok"]:
                return
            cerrando["ok"] = True

            try:
                dum_translator.cerrar_run(nombre, bot, motivo="cerrar_ui")
            except Exception as e:
                print("Error DumTranslator.cerrar_run:", e)

            khazad_dum_win["open"] = False
            
            try:
                app.root.destroy()
            except Exception:
                pass
            
            refrescar_menu()


        app.root.protocol("WM_DELETE_WINDOW", _al_cerrar)

    # =========================
    # 3) Ahora sí: instanciar DumWindow una sola vez
    # =========================
    dungeon_win = DumWindow(
        master=main_menu_var,
        usuario=nombre,
        rellenar_mosaico_fn=rellenar_mosaico,
        bg_path=BG_PATH,
        icon_path=ICON_DUM_PATH,
        open_khazad_dum_fn=abrir_khazad_dum,  # <-- callback correcto
    )

    # =========================
    # Decoración Balrogs
    # =========================
    try:
        img_left = Image.open(BALROG_LEFT_PATH).resize((76, 76), resample=Image.Resampling.NEAREST)
        img_right = Image.open(BALROG_RIGHT_PATH).resize((76, 76), resample=Image.Resampling.NEAREST)

        balrog_left = ImageTk.PhotoImage(img_left)
        balrog_right = ImageTk.PhotoImage(img_right)

        canvas_menu.balrog_left = balrog_left
        canvas_menu.balrog_right = balrog_right

        canvas_menu.create_image(120, 550, image=balrog_right, anchor="center")
        canvas_menu.create_image(630, 550, image=balrog_left, anchor="center")

    except Exception as e:
        print("Error cargando balrogs:", e)

    # =========================
    # Títulos
    # =========================
    canvas_menu.create_text(
        375, 30,
        text="Dungeon Market",
        fill="Gold",
        font=("Carolingia", 20),
        anchor="center"
    )

    canvas_menu.create_text(
        375, 70,
        text=f"Salve, {nombre}!",
        fill="GoldenRod",
        font=("Carolingia", 18),
        anchor="center"
    )

    # =========================
    # Selector "Libre"
    # =========================
    libre_selector_ref = {"win": None}

    def abrir_selector_libre():
        win = libre_selector_ref["win"]
        if win is not None and win.winfo_exists():
            win.lift()
            win.focus_force()
            return

        sel = tk.Toplevel(main_menu_var)
        libre_selector_ref["win"] = sel
        sel.geometry("320x220")
        sel.title("Libre")
        sel.config(background="PaleGoldenRod")

        try:
            sel.iconbitmap(ICON_MAIN_PATH)
        except Exception:
            pass

        def _al_cerrar():
            try:
                sel.destroy()
            except Exception:
                pass
            libre_selector_ref["win"] = None

        sel.protocol("WM_DELETE_WINDOW", _al_cerrar)

        tk.Label(sel, text="Modo Libre", font=("Carolingia", 16), bg="PaleGoldenRod").pack(pady=10)

        def abrir_khazad_bot():
            _al_cerrar()
            abrir_khazad()

        tk.Button(sel, text="Khazad bot", font=("Carolingia", 14), command=abrir_khazad_bot).pack(pady=8)
        tk.Button(sel, text="Spot", font=("Carolingia", 14), command=lambda: print("[libre] Spot (pendiente)")).pack(pady=5)
        tk.Button(sel, text="Futuros", font=("Carolingia", 14), command=lambda: print("[libre] Futuros (pendiente)")).pack(pady=5)

    # =========================
    # Botones principales
    # =========================
    btn_libre = tk.Button(main_menu_var, text="Libre", font=("Carolingia", 16), command=abrir_selector_libre)
    canvas_menu.create_window(280, 140, window=btn_libre, anchor="nw")

    btn_dum = tk.Button(main_menu_var, text="Dum", font=("Carolingia", 16), command=dungeon_win.open)
    canvas_menu.create_window(400, 140, window=btn_dum, anchor="nw")



def login_win():
    # limpiar ventana
    for child in ventana_loggin.winfo_children():
        child.destroy()

    tk.Label(
        ventana_loggin,
        text="Dungeon Market",
        font=("Carolingia", 14),
        bg="PaleGoldenRod"
    ).pack(anchor="center", pady=5)

    nombre_label = tk.Label(ventana_loggin, text="Nombre: ", font=("Carolingia", 12), bg="PaleGoldenRod")
    nombre_label.pack(side="left", padx=5, pady=10)

    nombre_entry = tk.Entry(ventana_loggin)
    nombre_entry.pack(side="left", padx=5, pady=10)

    pass_label = tk.Label(ventana_loggin, text="Contraseña: ", font=("Carolingia", 12), bg="PaleGoldenRod")
    pass_entry = tk.Entry(ventana_loggin, show="*")

    def validar_pass(nombre, passw):
        if validar_usuario(nombre, passw):
            print("Login correcto")
            ventana_loggin.withdraw()
            main_menu(nombre)
        else:
            print("Contraseña incorrecta")

    def validar_nombre():
        nombre = nombre_entry.get().strip()
        if usuario_existe(nombre):
            nombre_label.pack_forget()
            nombre_entry.pack_forget()
            boton.pack_forget()

            pass_label.pack(side="left", padx=5, pady=10)
            pass_entry.pack(side="left", padx=5, pady=10)

            boton_pass = tk.Button(
                ventana_loggin,
                text="Ingresar",
                command=lambda: validar_pass(nombre, pass_entry.get())
            )
            boton_pass.pack(side="left", padx=10)
        else:
            print("No registrado")

    boton = tk.Button(ventana_loggin, text="Validar", command=validar_nombre)
    boton.pack(side="left", padx=10)

    tk.Button(ventana_loggin, text="Crear cuenta", command=crear_user).pack(side="bottom", pady=10)


# arranque
login_win()
ventana_loggin.mainloop()
