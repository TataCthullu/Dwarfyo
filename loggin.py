import tkinter as tk
from database import init_db, agregar_usuario, validar_usuario, usuario_existe, guardar_perfil, cargar_perfil
from codigo_principala import TradingBot
from interfaz import BotInterfaz
from PIL import Image, ImageTk
import os

ventana_loggin = tk.Tk()
ventana_loggin.title("Loggin")
ventana_loggin.geometry("400x200")
ventana_loggin.config(background="PaleGoldenRod")
ventana_loggin.iconbitmap(
    "imagenes/icon/urand_eternal_torment.ico"
)


def cerrar_app():
    ventana_loggin.destroy()

ventana_loggin.protocol("WM_DELETE_WINDOW", cerrar_app)

#exchange_win = False
crear_user_win = False
user_win_ref = None

init_db()

def crear_user():
    global user_win_ref

    if user_win_ref is not None and user_win_ref.winfo_exists():
        user_win_ref.lift()
        user_win_ref.focus_force()
        return

    global crear_user_win
    if crear_user_win:
        return
    crear_user_win = True

    user_win = tk.Toplevel(ventana_loggin)
    user_win_ref = user_win
    user_win.geometry("400x200")
    user_win.title("Creación De Usuario - Dungeon Market")
    def cerrar_user():
        global user_win_ref, crear_user_win
        crear_user_win = False
        try:
            user_win.destroy()
        except Exception:
            pass
        user_win_ref = None


    user_win.protocol("WM_DELETE_WINDOW", cerrar_user)
    user_win.config(background="PaleGoldenRod")

    user_win_laba = tk.Label(user_win, text="Saludos!", font=("Carolingia", 18), background="PaleGoldenRod")
    user_win_laba.pack(anchor="center", pady=10)

    nombre_lab = tk.Label(user_win, text="Nombre: ", font=("Carolingia", 18), background="PaleGoldenRod")
    nombre_lab.pack(anchor="w")

    nombre_entry = tk.Entry(user_win)
    nombre_entry.pack(anchor="w")

    pass_lab = tk.Label(user_win, text="Contraseña: ", font=("Carolingia", 18), background="PaleGoldenRod")
    pass_lab.pack(anchor="w")

    pass_entry = tk.Entry(user_win)
    pass_entry.pack(anchor="w")

    def guardar_usuario():
        nombre = nombre_entry.get().strip()
        password = pass_entry.get().strip()

        if not nombre or not password:
            print("Campos vacíos")
            return

        if agregar_usuario(nombre, password):
            print("Usuario creado correctamente")
            global crear_user_win
            crear_user_win = False
            user_win.destroy()
        else:
            print("Ese usuario ya existe")


    btn_crear_pj = tk.Button(user_win, text="Crear", font=("Carolingia", 18), command=guardar_usuario)
    btn_crear_pj.pack(pady=10)

    

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

AVATAR_DIR = os.path.join("imagenes", "deco", "Player", "AvatarBase")

def _listar_avatares():
    if not os.path.isdir(AVATAR_DIR):
        return []
    files = []
    for fn in os.listdir(AVATAR_DIR):
        if fn.lower().endswith((".png", ".jpg", ".jpeg")):
            files.append(os.path.join(AVATAR_DIR, fn))
    files.sort()
    return files

def _cargar_avatar_thumbnail(path, size=(64, 64)):
    try:
        img = Image.open(path)
        img = img.resize(size, resample=Image.Resampling.NEAREST)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def _avatar_name_from_path(path):
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    return name

# Main Menu
def main_menu(nombre):
    main_menu_var = tk.Toplevel(ventana_loggin)
    main_menu_var.geometry("750x800")
    main_menu_var.iconbitmap(
    "imagenes/icon/urand_eternal_torment.ico"
    )
    DUM_ICON_PATH = "imagenes/icon/cigotuvis_monster.ico"
    main_menu_var.title("Dungeon Market - Main Menu")
        # ===== Canvas full para fondo + layout =====
    canvas_menu = tk.Canvas(main_menu_var, width=750, height=800, highlightthickness=0, bd=0)
    canvas_menu.pack(fill="both", expand=True)

    # Fondo mosaico (elegí la textura que quieras)
    rellenar_mosaico(canvas_menu, "imagenes/decoa/wall/catacombs_5.png", escala=2)

    khazad_win = {"open": False, "app": None}  # mini-flag simple

    def abrir_khazad():
        if khazad_win["open"]:
            try:
                khazad_win["app"].root.lift()
                khazad_win["app"].root.focus_force()
            except Exception:
                pass
            return

        bot = TradingBot()
        app = BotInterfaz(bot, master=ventana_loggin, usuario=nombre)
        khazad_win["open"] = True
        khazad_win["app"] = app

        def _al_cerrar():
            khazad_win["open"] = False
            try:
                app.root.destroy()
            except Exception:
                pass

        app.root.protocol("WM_DELETE_WINDOW", _al_cerrar)

    # ---- textos flotantes (SIN fondo) ----
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
   

    perfil = cargar_perfil(nombre)
    avatar_data = (perfil.get("avatar", {}) or {})
    avatar_nombre = avatar_data.get("name", "Sin avatar")
    avatar_img_path = avatar_data.get("img", "")

    # --- imagen arriba del nombre ---
    avatar_img_id = canvas_menu.create_image(
        375, 520,
        image="",
        anchor="center"
    )

    # mantener referencia para que no lo borre el GC
    canvas_menu.avatar_photo = None

    if avatar_img_path and os.path.exists(avatar_img_path):
        ph = _cargar_avatar_thumbnail(avatar_img_path, size=(64, 64))
        if ph:
            canvas_menu.avatar_photo = ph
            canvas_menu.itemconfig(avatar_img_id, image=ph)

    # --- texto del nombre abajo ---
    avatar_text_id = canvas_menu.create_text(
        375, 605,
        text=avatar_nombre,
        fill="PaleGoldenRod",
        font=("Carolingia", 16),
        anchor="center"
    )


    def abrir_modo(modo):
        bot = TradingBot()
        bot.modo_app = modo  # solo guardamos el modo, sin lógica todavía

        app = BotInterfaz(
            bot,
            master=ventana_loggin,
            usuario=nombre
        )

        if modo == "dum":
            app.root.iconbitmap(DUM_ICON_PATH)
        else:
            app.root.iconbitmap("imagenes/icon/urand_eternal_torment.ico")

        def _al_cerrar():
            try:
                app.root.destroy()
            except Exception:
                pass

        app.root.protocol("WM_DELETE_WINDOW", _al_cerrar)

    modo_selector_win_ref = {"win": None}

    def abrir_selector_modo(modo):
        # evitar duplicar ventana
        win = modo_selector_win_ref["win"]
        if win is not None and win.winfo_exists():
            win.lift()
            win.focus_force()
            return

        sel = tk.Toplevel(ventana_loggin)
        modo_selector_win_ref["win"] = sel
        sel.geometry("320x220")
        sel.title(("Libre" if modo == "libre" else "Dum"))
        sel.config(background="PaleGoldenRod")
       
        
        if modo == "dum":
            sel.iconbitmap(DUM_ICON_PATH)
        else:
            sel.iconbitmap("imagenes/icon/urand_eternal_torment.ico")

        def _al_cerrar():
            try:
                sel.destroy()
            except Exception:
                pass
            modo_selector_win_ref["win"] = None

        sel.protocol("WM_DELETE_WINDOW", _al_cerrar)

        titulo = tk.Label(
            sel,
            font=("Carolingia", 16),
            bg="PaleGoldenRod"
        )
        titulo.pack(pady=10)

        def abrir_khazad_bot():
            _al_cerrar()  # cerrar selector
            abrir_modo(modo)  # <-- SOLO acá abrimos el bot

        def abrir_spot():
            print(f"[{modo}] Spot (pendiente)")
            # acá más adelante vas a abrir tu interfaz spot correspondiente

        def abrir_futuros():
            print(f"[{modo}] Futuros (pendiente)")
            # acá más adelante vas a abrir tu interfaz futures correspondiente

        btn_spot = tk.Button(sel, text="Spot", font=("Carolingia", 14), command=abrir_spot)
        btn_spot.pack(pady=5)

        btn_khaz = tk.Button(sel, text="Khazad bot", font=("Carolingia", 14), command=abrir_khazad_bot)
        btn_khaz.pack(pady=5)

        btn_fut = tk.Button(sel, text="Futuros", font=("Carolingia", 14), command=abrir_futuros)
        btn_fut.pack(pady=5)


    """btn_exchange = tk.Button(main_menu_var, text="Exchange", font=("Carolingia", 16), command=exchange_def)
    canvas_menu.create_window(120, 140, window=btn_exchange, anchor="nw")
"""
    btn_libre = tk.Button(
        main_menu_var,
        text="Libre",
        font=("Carolingia", 16),
        command=lambda: abrir_selector_modo("libre")
    )
    canvas_menu.create_window(280, 140, window=btn_libre, anchor="nw")

    btn_dum = tk.Button(
        main_menu_var,
        text="Dum",
        font=("Carolingia", 16),
        command=lambda: abrir_selector_modo("dum")
    )
    canvas_menu.create_window(400, 140, window=btn_dum, anchor="nw")

    # Si el usuario ya eligió avatar, no mostramos el botón
    tiene_avatar = bool((perfil.get("avatar", {}) or {}).get("img"))

    btn_crear_avatar = None
    if not tiene_avatar:
        btn_crear_avatar = tk.Button(
            main_menu_var,
            text="Elegir Avatar",
            font=("Carolingia", 14),
            command=lambda: crear_avatar(nombre, canvas_menu, avatar_text_id, avatar_img_id, btn_crear_avatar)
        )
        canvas_menu.create_window(120, 730, window=btn_crear_avatar, anchor="nw")

    def cerrar_todo():
            ventana_loggin.destroy()
          
    main_menu_var.protocol("WM_DELETE_WINDOW", cerrar_todo)

    def cerrar_sesion():
        main_menu_var.destroy()
        ventana_loggin.deiconify()
        login_win()  # ← recrea toda la vista de login (arranca por usuario)

    btn_cerrar_sesion = tk.Button(
        main_menu_var,
        text="Cerrar sesion",
        font=("Carolingia", 12),
        command=cerrar_sesion
    )
    canvas_menu.create_window(730, 770, window=btn_cerrar_sesion, anchor="se")

"""def exchange_def():
    global exchange_win
    if exchange_win:
        return
    exchange_win = True
    exchange_var = tk.Toplevel(ventana_loggin) 
    exchange_var.geometry("400x400")
    exchange_var.title("Exchange - Dungeon Market")

    btn_fantasy_spt = tk.Button(exchange_var, text="Fantasy Spot", command=fantasy_spot)
    btn_fantasy_spt.pack()

    btn_fantasy_futures = tk.Button(exchange_var, text="Fantasy Futures", command=fantasy_futures)
    btn_fantasy_futures.pack()

    def on_close():
        global exchange_win
        exchange_win = False
        exchange_var.destroy()
        
    exchange_var.protocol("WM_DELETE_WINDOW", on_close)    

def fantasy_spot():
    fantasy_spot_win = tk.Toplevel(ventana_loggin)
    fantasy_spot_win.geometry("200x200")
    fantasy_spot_win.title("Fantasy Spot - Dungeon Market")

def fantasy_futures():
    fantasy_futures_win = tk.Toplevel(ventana_loggin)
    fantasy_futures_win.geometry("200x200")
    fantasy_futures_win.title("Fantasy Futures - Dungeon Market") """   

def crear_avatar(usuario, canvas_menu, avatar_text_id, avatar_img_id, btn_crear_avatar):
    avatar_win = tk.Toplevel(ventana_loggin)
    avatar_win.title("Elegir Avatar")
    avatar_win.configure(background="PaleGoldenRod")

    # lista de avatares
    paths = _listar_avatares()
    if not paths:
        lab = tk.Label(avatar_win, text=f"No hay avatares en:\n{AVATAR_DIR}", bg="PaleGoldenRod")
        lab.pack(padx=10, pady=10)
        return

    # --- nombre obligatorio ---
    lab_nombre = tk.Label(avatar_win, text="Nombre del avatar:", bg="PaleGoldenRod", font=("Carolingia", 12))
    lab_nombre.pack(padx=10, pady=(10, 0), anchor="w")

    nombre_var = tk.StringVar()
    entry_nombre = tk.Entry(avatar_win, textvariable=nombre_var)
    entry_nombre.pack(padx=10, pady=(0, 10), anchor="w")
    entry_nombre.focus_force()

    # contenedor de botones
    frame = tk.Frame(avatar_win, bg="PaleGoldenRod")
    frame.pack(padx=10, pady=10)

    # refs de thumbnails para que no se borren
    avatar_win.thumbs = []
    avatar_win.avatar_buttons = []  # para habilitar/deshabilitar

    def _update_buttons_state(*_):
        ok = bool(nombre_var.get().strip())
        state = "normal" if ok else "disabled"
        for b in avatar_win.avatar_buttons:
            try:
                b.configure(state=state)
            except Exception:
                pass

    nombre_var.trace_add("write", _update_buttons_state)


    def _select(path):
        nombre_avatar = nombre_var.get().strip()
        if not nombre_avatar:
            return  # por seguridad

        perfil = cargar_perfil(usuario)
        perfil["avatar"] = {"name": nombre_avatar, "img": path}
        guardar_perfil(usuario, perfil)

        # actualizar UI (texto + imagen)
        canvas_menu.itemconfig(avatar_text_id, text=nombre_avatar)

        ph = _cargar_avatar_thumbnail(path, size=(64, 64))
        if ph:
            canvas_menu.avatar_photo = ph
            canvas_menu.itemconfig(avatar_img_id, image=ph)

        # borrar el botón de crear avatar
        try:
            btn_crear_avatar.destroy()
        except Exception:
            pass

        avatar_win.destroy()


    # grilla simple
    cols = 4
    r = c = 0
    for p in paths:
        thumb = _cargar_avatar_thumbnail(p, size=(64, 64))
        if not thumb:
            continue
        avatar_win.thumbs.append(thumb)

        name = _avatar_name_from_path(p)

        b = tk.Button(
            frame,
            image=thumb,
            text=name,
            compound="top",
            command=lambda pp=p: _select(pp),
            state="disabled"  # arranca bloqueado hasta que pongan nombre
        )
        b.grid(row=r, column=c, padx=6, pady=6)

        avatar_win.avatar_buttons.append(b)

        c += 1
        if c >= cols:
            c = 0
            r += 1

    _update_buttons_state()


def login_win():
    """(Re)arma la vista de login completa y limpia."""
    # 1) limpiar ventana
    for child in ventana_loggin.winfo_children():
        child.destroy()

    # 2) título
    label_title = tk.Label(ventana_loggin, text="Dungeon Market",
                           font=("Carolingia", 14), bg="PaleGoldenRod")
    label_title.pack(anchor="center", pady=5)

    # 3) etapa usuario
    nombre_label = tk.Label(ventana_loggin, text="Nombre: ",
                            font=("Carolingia", 12), bg="PaleGoldenRod")
    nombre_label.pack(side="left", padx=5, pady=10)

    nombre_entry = tk.Entry(ventana_loggin)
    nombre_entry.pack(side="left", padx=5, pady=10)

    # 4) widgets de contraseña (creados pero ocultos al inicio)
    pass_label = tk.Label(ventana_loggin, text="Contraseña: ",
                          font=("Carolingia", 12), bg="PaleGoldenRod")
    pass_entry = tk.Entry(ventana_loggin, show="*")

    def validar_nombre():
        nombre = nombre_entry.get().strip()

        # 1) Solo verificamos si el usuario EXISTE
        if usuario_existe(nombre):
            # ocultar etapa usuario
            nombre_label.pack_forget()
            nombre_entry.pack_forget()
            boton.pack_forget()

            # mostrar etapa contraseña
            pass_label.pack(side="left", padx=5, pady=10)
            pass_entry.pack(side="left", padx=5, pady=10)

            # botón para validar contraseña
            boton_pass = tk.Button(
                ventana_loggin,
                text="Ingresar",
                command=lambda: validar_pass(nombre, pass_entry.get())
            )
            boton_pass.pack(side="left", padx=10)
        else:
            print("No registrado")

    def validar_pass(nombre, passw):
        if validar_usuario(nombre, passw):
            print("Login correcto")
            ventana_loggin.withdraw()
            main_menu(nombre)
        else:
            print("Contraseña incorrecta")

    # 6) botón validar usuario
    boton = tk.Button(ventana_loggin, text="Validar", command=validar_nombre)
    boton.pack(side="left", padx=10)
    
    crear_user_btn = tk.Button(ventana_loggin, text="Crear cuenta", command=crear_user)
    crear_user_btn.pack(side="bottom", pady=10)
# ---- arranque ----
login_win()
ventana_loggin.mainloop()














