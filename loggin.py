import tkinter as tk
from database import init_db, agregar_usuario, validar_usuario, usuario_existe

ventana_loggin = tk.Tk()
ventana_loggin.title("Loggin")
ventana_loggin.geometry("400x200")
ventana_loggin.config(background="PaleGoldenRod")

def cerrar_app():
        ventana_loggin.destroy()

ventana_loggin.protocol("WM_DELETE_WINDOW", cerrar_app)

exchange_win = False
crear_user_win = False

init_db()

def crear_user():
    global crear_user_win
    if crear_user_win:
        return
    crear_user_win = True

    user_win = tk.Tk()
    user_win.geometry("400x200")
    user_win.title("Creacion De Usuario - Dungeon Market")
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
            user_win.destroy()
        else:
            print("Ese usuario ya existe")


    btn_crear_pj = tk.Button(user_win, text="Crear", font=("Carolingia", 18), command=guardar_usuario)
    btn_crear_pj.pack(pady=10)

    user_win.mainloop()
# Main Menu
def main_menu(nombre):
    main_menu_var = tk.Toplevel(ventana_loggin)
    main_menu_var.geometry("750x800")
    main_menu_var.config(background="PaleGoldenRod")
    main_menu_var.title("Dungeon Market")
    menu_title = tk.Label(main_menu_var, text = "Dungeon Market", font=("Carolingia", 20), background="PaleGoldenRod")
    menu_title.pack(side="top",anchor="center")
    saludo_label = tk.Label(main_menu_var, text=f"Salve, {nombre}!", font=("Carolingia", 18),fg="Crimson", background="PaleGoldenRod")
    saludo_label.pack()

    btn_exchange = tk.Button(main_menu_var, text="Exchange", font=("Carolingia", 16), command=exchange_def)
    btn_exchange.pack(side="left", anchor="n", padx=10)

    btn_khazad = tk.Button(main_menu_var, text="Khazad", font=("Carolingia", 16))
    btn_khazad.pack(side="left", anchor="n", padx=10)
    
    btn_doom = tk.Button(main_menu_var, text="Doom", font=("Carolingia", 16))
    btn_doom.pack(side="left", anchor="n", padx=10)

    btn_crear_avatar = tk.Button(main_menu_var, text="Crear Avatar", font=("Carolingia", 16), command=crear_avatar)
    btn_crear_avatar.pack()

    def cerrar_todo():
            ventana_loggin.destroy()
          
    main_menu_var.protocol("WM_DELETE_WINDOW", cerrar_todo)

    def cerrar_sesion():
        main_menu_var.destroy()
        ventana_loggin.deiconify()
        login_win()  # ← recrea toda la vista de login (arranca por usuario)

    tk.Button(main_menu_var, text="Cerrar sesión", font=("Carolingia", 12),
            command=cerrar_sesion).pack(side="bottom", anchor="e", padx=20, pady=20)
    
def exchange_def():
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
    fantasy_futures_win.title("Fantasy Futures - Dungeon Market")    

def crear_avatar():
    avatar_win = tk.Toplevel(ventana_loggin)
    avatar_win.geometry("300x50")
    avatar_win.title("Crear Avatar")
    avatar_win.configure(background="PaleGoldenRod")

    label_name = tk.Label(avatar_win, text="Nombre:")
    label_name.pack(side="left", anchor="n")

    entry_name = tk.Entry(avatar_win)
    entry_name.pack(side="left", anchor="n")

    btn_crear_avatar = tk.Button(avatar_win, text="Crear")
    btn_crear_avatar.pack()


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














