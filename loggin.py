# © 2025 Dungeon Market (Loggin)
# Todos los derechos reservados.

from player import DumWindow
import tkinter as tk
from database import init_db, agregar_usuario, validar_usuario, usuario_existe, guardar_perfil, init_wallet
from PIL import Image, ImageTk
from codigo_principala import TradingBot
from interfaz import BotInterfaz

init_db()
DEBUG_DUM = False

ventana_loggin = tk.Tk()
ventana_loggin.title("Loggin")
ventana_loggin.geometry("400x200")
ventana_loggin.config(background="PaleGoldenRod")
ventana_loggin.iconbitmap(
    "imagenes/icon/urand_eternal_torment.ico"
)
BALROG_LEFT_PATH  = "imagenes/deco/balrug_old.png"
BALROG_RIGHT_PATH = "imagenes/deco/balrug_new.png"


def cerrar_app():
    ventana_loggin.destroy()

ventana_loggin.protocol("WM_DELETE_WINDOW", cerrar_app)

crear_user_win = False
user_win_ref = None

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
            init_wallet(nombre)
            guardar_perfil(nombre, {"dum": {"deposito": "0", "slot_used_last": "0"}, "avatar": {}})
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

    dungeon_win = DumWindow(
        master=main_menu_var,
        usuario=nombre,
        rellenar_mosaico_fn=rellenar_mosaico,
        bg_path="imagenes/decoa/wall/catacombs_5.png",
        icon_path=DUM_ICON_PATH
    )
    def refrescar_menu():
        # ahora el refresco vive en la ventana del jugador
        try:
            dungeon_win.refresh()
        except Exception:
            pass

    # --- Balrogs decorativos ---
    try:
        img_left = Image.open(BALROG_LEFT_PATH).resize((76, 76), resample=Image.Resampling.NEAREST)
        img_right = Image.open(BALROG_RIGHT_PATH).resize((76, 76), resample=Image.Resampling.NEAREST)

        balrog_left = ImageTk.PhotoImage(img_left)
        balrog_right = ImageTk.PhotoImage(img_right)

        # guardar referencias
        canvas_menu.balrog_left = balrog_left
        canvas_menu.balrog_right = balrog_right

        # balrog izquierda
        canvas_menu.create_image(
            120, 550,   # X, Y → tocá solo estos valores
            image=balrog_right,
            anchor="center"
        )

        # balrog derecha
        canvas_menu.create_image(
            630, 550,   # X, Y → tocá solo estos valores
            image=balrog_left,
            anchor="center"
        )

    except Exception as e:
        print("Error cargando balrogs:", e)
    
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
        # si querés marcar modo:
        bot.modo_app = "libre"

        app = BotInterfaz(bot, master=ventana_loggin, usuario=nombre)

        # hook para refrescar HUD del Dungeon (cuando cierres / stop / etc)
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

   
        
   
       
   

    """btn_exchange = tk.Button(main_menu_var, text="Exchange", font=("Carolingia", 16), command=exchange_def)
    canvas_menu.create_window(120, 140, window=btn_exchange, anchor="nw")
""" 
    btn_libre = tk.Button(
        main_menu_var,
        text="Libre",
        font=("Carolingia", 16),
        command=abrir_khazad  # o la función que ABRA el bot libre
    )
    canvas_menu.create_window(280, 140, window=btn_libre, anchor="nw")

    btn_dum = tk.Button(
        main_menu_var,
        text="Dum",
        font=("Carolingia", 16),
        command=dungeon_win.open
    )
    canvas_menu.create_window(400, 140, window=btn_dum, anchor="nw")


  
    

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














