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

"""from tkinter import *
import codigo_principala

#Ventana principal
ventana_principal = Tk()
ventana_principal.title("Dwarf") 
ventana_principal.minsize(width=1200, height=700)
ventana_principal.iconbitmap("imagenes/miner.ico")
ventana_principal.configure(bg="LightBlue")
ventana_principal.resizable(False, False)
ventana_principal.geometry("1200x700+200+200")
ventana_principal.attributes("-alpha",0.9)

#Funciones
def abrir_sbv_config():
    sbv_conf = Toplevel(ventana_principal)
    sbv_conf.title("Configuración de operativa")
    sbv_conf.geometry("400x300")

    Label(sbv_conf, text="Configurar operativa", font=("Arial", 14))

def abrir_Compras():
    compras_lst = Toplevel(ventana_principal)
    compras_lst.title("Lista de compras realizadas")
    compras_lst.geometry("600x500")

    Label(compras_lst, text="Lista de compras", font=("Arial", 14))

def abrir_ventas():
    ventas_lst = Toplevel(ventana_principal)
    ventas_lst.title("Lista de ventas")
    ventas_lst.geometry("500x800")






#Variables de control 

varpor_set_venta_str = StringVar()
varpor_set_venta = DoubleVar()

varpor_set_compra_str = StringVar()
varpor_set_compra = DoubleVar()

precio_act_var = StringVar()
precio_act_box = DoubleVar()

cant_btc_str = StringVar()
cant_btc_act = DoubleVar()

cant_usdt_str = StringVar()
cant_usdt = DoubleVar()

porc_desde_compra = DoubleVar()
porc_desde_compra_str = StringVar()

porc_desde_venta = DoubleVar()
porc_desde_venta_str = StringVar()

balance_var = StringVar()
balance_var_box = DoubleVar()

varpor_set_venta_str.set("Variacion de porcentaje por venta")
varpor_set_venta.set("")

varpor_set_compra_str.set("Variacion de porcentaje por compra")
varpor_set_compra.set("")

porc_desde_venta_str.set("Variacion de porcentaje desde ult venta")
porc_desde_venta.set("")

porc_desde_compra_str.set("Porcentaje actual de variacion desde ultima compra")
porc_desde_compra.set("")

cant_usdt_str.set("Cantidad actual de Usdt")
cant_usdt.set("")

cant_btc_str.set("Cantidad actual de Btc")
cant_btc_act.set("")

precio_act_var.set("Precio actual Btc/Usdt")
precio_act_box.set("")

balance_var.set("Balance actual Usdt + Btc, invertidos")
balance_var_box.set("")



#Etiquetas y cajas

#Etiqueta
etiqueta_varpor_set_venta_str = Label(ventana_principal, textvariable=varpor_set_venta_str, font=("Arial", 14), bg="LightBlue")
etiqueta_varpor_set_venta_str.place(x=500, y=90)
#Caja
caja_varpor_set_venta = Entry(ventana_principal, width=20, font=("Arial", 14), textvariable=varpor_set_venta)
caja_varpor_set_venta.place(x=500, y=120)

#Etiqueta
etiqueta_varpor_set_compra_str = Label(ventana_principal, textvariable=varpor_set_compra_str, font=("Arial", 14), bg="LightBlue")
etiqueta_varpor_set_compra_str.place(x=500, y=1)
#Caja
etiqueta_varpor_set_compra = Entry(ventana_principal, width=20, font=("Arial", 14), textvariable=varpor_set_compra)
etiqueta_varpor_set_compra.place(x=500, y=30)

#Etiqueta
etiqueta_porc_desde_compra_str = Label(ventana_principal, textvariable=porc_desde_compra_str, font=("Arial", 14), bg="LightBlue")
etiqueta_porc_desde_compra_str.place(x=1, y=450)
#Caja
caja_porc_desde_compra = Entry(ventana_principal, width=20, font=("Arial", 14), textvariable=porc_desde_compra)
caja_porc_desde_compra.place(x=1, y=480)

#Etiqueta
etiqueta_porc_desde_venta_str = Label(ventana_principal, textvariable=porc_desde_venta_str, font=("Arial", 14), bg="LightBlue")
etiqueta_porc_desde_venta_str.place(x=1, y=360)
#Caja
caja_porc_desde_venta = Entry(ventana_principal, width=20, font=("Arial", 14), textvariable=porc_desde_venta)
caja_porc_desde_venta.place(x=1, y=390)

#Etiqueta
etiqueta_cant_usdt_str = Label(ventana_principal, textvariable=cant_usdt_str, font=("Arial", 14), bg="LightBlue")
etiqueta_cant_usdt_str.place(x=1, y=270)
#Caja
caja_cant_usdt = Entry(ventana_principal, width=20, font=("Arial", 14), textvariable=cant_usdt)
caja_cant_usdt.place(x=1, y=300)

#Etiqueta
etiqueta_cant_btc_str = Label(ventana_principal, textvariable=cant_btc_str, font=("Arial", 14), bg="LightBlue")
etiqueta_cant_btc_str.place(x=1, y=180)
#Caja
caja_cant_btc_act = Entry(ventana_principal, width=20, font=("Arial", 14), textvariable=cant_btc_act)
caja_cant_btc_act.place(x=1, y=210)

#Etiqueta
etiqueta_precio_act = Label(ventana_principal, textvariable=precio_act_var, font=("Arial", 14), bg="LightBlue")
etiqueta_precio_act.place(x=1, y=1)
#Caja
caja_precio_act = Entry(ventana_principal, width=20, font=("Arial", 14), textvariable=precio_act_box, bg="LightGreen")
caja_precio_act.place(x=1, y=30)

#Etiqueta
etiqueta_balance = Label(ventana_principal, textvariable=balance_var, font=("Arial", 14), bg="LightBlue")
etiqueta_balance.place(x=1, y=90)
#Caja
caja_balance = Entry(ventana_principal, textvariable=balance_var_box, width=20, font=("Arial", 14), bg="LightGreen")
caja_balance.place(x=1, y=120) 

#Botones
boton_compras = Button(text="Compras", font=("Arial", 14), command=abrir_Compras)
boton_compras.place(x=1000,y=10)

boton_ventas = Button(text="Ventas", font=("Arial", 14), command=abrir_ventas)
boton_ventas.place(x=1000,y=90)

boton_seteo = Button(text="Seteo de operatoria", font=("Arial", 14), command=abrir_sbv_config)
boton_seteo.place(x=1000,y=170)

#*"""
from tkinter import *
import threading
from codigo_principala import TradingBot
import time
  
bot = TradingBot()
ventana = Tk()
ventana.title("Trading Bot")
ventana.geometry("500x400")

label_balance = Label(ventana, text=f"Balance: {bot.usdt:.2f} USDT", font=("Arial", 14))
label_balance.pack()

label_btc = Label(ventana, text=f"BTC: {bot.btc:.6f}", font=("Arial", 14))
label_btc.pack()

def actualizar_ui():
    while bot.running:
        label_balance.config(text=f"Balance: {bot.usdt:.2f} USDT")
        label_btc.config(text=f"BTC: {bot.btc:.6f}")
        time.sleep(3)

def iniciar_bot():
    threading.Thread(target=bot.iniciar, daemon=True).start()
    threading.Thread(target=actualizar_ui, daemon=True).start()

def detener_bot():
    bot.detener()

boton_iniciar = Button(ventana, text="Iniciar Bot", command=iniciar_bot)
boton_iniciar.pack()

boton_detener = Button(ventana, text="Detener Bot", command=detener_bot)
boton_detener.pack()

ventana.mainloop()
 