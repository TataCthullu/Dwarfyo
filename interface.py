#Ventana de Login
"""from tkinter import *

ventana_principal = Tk()
ventana_principal.title("Dwarf") 
ventana_principal.minsize(width=300, height=400)
ventana_principal.config(padx=35, pady=35)


etiqueta1 = Label(text="Escribe tu nombre de usuario: ", font=("Arial", 14))
etiqueta1.grid(column=0, row=1)
caja_de_texto = Entry(width=20, font=("Arial", 14))
caja_de_texto.grid(column=0, row=2) 

etiqueta2 = Label(text="Escribe tu contraseña: ", font=("Arial", 14))
etiqueta2.grid(column=0, row=3)
caja_de_texto2 = Entry(width=20, font=("Arial", 14), show="*")
caja_de_texto2.grid(column=0, row=4) 

boton1 = Button(text="Aceptar", font=("Arial", 14))
boton1.grid(column=0, row=6)


ventana_principal.mainloop()"""

import threading
from tkinter import *
from codigo_principala import TradingBot

# Instancia del bot
bot = TradingBot()

# Interfaz Tkinter
ventana_principal = Tk()
ventana_principal.title("Dwarf") 
ventana_principal.geometry("1200x700")
ventana_principal.configure(bg="DarkGoldenrod")
ventana_principal.iconbitmap("imagenes/miner.ico")
ventana_principal.attributes("-alpha",0.95)

# Variables UI
precio_act_var = StringVar()
cant_btc_str = StringVar()
cant_usdt_str = StringVar()
balance_var = StringVar()

varpor_set_venta_str = StringVar()
varpor_set_compra_str = StringVar()
porc_desde_compra_str = StringVar()
porc_desde_venta_str = StringVar()

# Etiquetas UI
Label(ventana_principal, text="Precio actual BTC/USDT:", bg="DarkGoldenrod").place(x=10, y=10)
Label(ventana_principal, textvariable=precio_act_var, bg="Gold").place(x=200, y=10)

Label(ventana_principal, text="BTC Disponible:", bg="DarkGoldenrod").place(x=10, y=50)
Label(ventana_principal, textvariable=cant_btc_str, bg="Gold").place(x=200, y=50)

Label(ventana_principal, text="USDT Disponible:", bg="DarkGoldenrod").place(x=10, y=90)
Label(ventana_principal, textvariable=cant_usdt_str, bg="Gold").place(x=200, y=90)

Label(ventana_principal, text="Balance Total:", bg="DarkGoldenrod").place(x=10, y=130)
Label(ventana_principal, textvariable=balance_var, bg="Gold").place(x=200, y=130)

Label(ventana_principal, text="Variación desde la ultima compra:", bg="DarkGoldenrod").place(x=10, y=170)
Label(ventana_principal, textvariable=varpor_set_compra_str, bg="Gold").place(x=200, y=170)

Label(ventana_principal, text="Variación desde la ultima venta:", bg="DarkGoldenrod").place(x=10, y=210)
Label(ventana_principal, textvariable=varpor_set_venta_str, bg="Gold").place(x=200, y=210)

Label(ventana_principal, text="Porcentaje para compra:", bg="DarkGoldenrod").place(x=500, y=10)
Label(ventana_principal, textvariable=porc_desde_venta_str, bg="Gold").place(x=640, y=10)

Label(ventana_principal, text="Porcentaje para venta:", bg="DarkGoldenrod").place(x=500, y=40)
Label(ventana_principal, textvariable=porc_desde_compra_str, bg="Gold").place(x=640, y=40)

"""etiqueta_varpor_set_venta_str = Label(ventana_principal, textvariable=varpor_set_venta_str, font=("Arial", 14), bg="DarkGoldenrod")
etiqueta_varpor_set_compra_str = Label(ventana_principal, textvariable=varpor_set_compra_str, font=("Arial", 14), bg="DarkGoldenrod")
tiqueta_porc_desde_compra_str = Label(ventana_principal, textvariable=porc_desde_compra_str, font=("Arial", 14), bg="DarkGoldenrod")
tiqueta_porc_desde_venta_str = Label(ventana_principal, textvariable=porc_desde_venta_str, font=("Arial", 14), bg="DarkGoldenrod")
etiqueta_cant_usdt_str = Label(ventana_principal, textvariable=cant_usdt_str, font=("Arial", 14), bg="DarkGoldenrod")
"""
# Función para actualizar UI
def actualizar_ui():
    if bot.running:
        bot.precio_actual = bot.get_precio_actual()
        precio_act_var.set(f"{bot.precio_actual:.2f} USDT")
        cant_btc_str.set(f"{bot.btc:.6f} BTC")
        cant_usdt_str.set(f"{bot.usdt:.2f} USDT")
        balance_var.set(f"{bot.usdt + (bot.btc * bot.precio_actual):.2f} USDT")

        varpor_set_compra_str.set(f"{bot.varpor_compra(bot.precio_ult_comp, bot.precio_actual):.6f}")
        varpor_set_venta_str.set(f"{bot.varpor_venta(bot.precio_ult_venta, bot.precio_actual):.6f}")
        porc_desde_compra_str.set(f"{bot.porc_por_compra}")   
        porc_desde_venta_str.set(f"{bot.porc_por_venta}")

    # Reprogramar la actualización cada 3 segundos
    ventana_principal.after(3000, actualizar_ui)


# Funciones de control
def iniciar_bot():
    if not bot.running:
        bot.running = True
        threading.Thread(target=bot.iniciar, daemon=True).start()
        actualizar_ui()

def detener_bot():
    bot.detener()
    bot.running = False

# Botones
Button(ventana_principal, text="Iniciar Bot", command=iniciar_bot, background="Goldenrod").place(x=500, y=300)
Button(ventana_principal, text="Detener Bot", command=detener_bot, background="Goldenrod").place(x=600, y=300)


# Subventanas
def abrir_sbv_config():
    sbv_conf = Toplevel(ventana_principal)
    sbv_conf.title("Configuración de operativa")
    sbv_conf.geometry("400x300")
    Label(sbv_conf, text="Configurar operativa", font=("Arial", 14)).pack()

def abrir_Compras():
    compras_lst = Toplevel(ventana_principal)
    compras_lst.title("Lista de compras realizadas")
    compras_lst.geometry("600x500")
    Label(compras_lst, text="Lista de compras", font=("Arial", 14)).pack()

def abrir_Ventas():
    ventas_lst = Toplevel(ventana_principal)
    ventas_lst.title("Lista de ventas")
    ventas_lst.geometry("500x800")
    Label(ventas_lst, text="Lista de ventas", font=("Arial", 14)).pack()

Button(text="Compras", command=abrir_Compras, background="Goldenrod").place(x=1000,y=10)
Button(text="Ventas", command=abrir_Ventas, background="Goldenrod").place(x=1000,y=90)
Button(text="Seteo de operatoria", command=abrir_sbv_config, background="Goldenrod").place(x=1000,y=170)



ventana_principal.mainloop()