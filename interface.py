#Ventana de Login
"""
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
"""

import threading
from tkinter import *
from codigo_principala import TradingBot
import datetime

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

Label(ventana_principal, text="Balance Total, Usdt + Btc:", bg="DarkGoldenrod").place(x=10, y=130)
Label(ventana_principal, textvariable=balance_var, bg="Gold").place(x=200, y=130)

Label(ventana_principal, text="Variación desde ultima compra:", bg="DarkGoldenrod").place(x=10, y=170)
Label(ventana_principal, textvariable=varpor_set_compra_str, bg="Gold").place(x=200, y=170)

Label(ventana_principal, text="Variación desde ultima venta:", bg="DarkGoldenrod").place(x=10, y=210)
Label(ventana_principal, textvariable=varpor_set_venta_str, bg="Gold").place(x=200, y=210)

Label(ventana_principal, text="Porcentaje para compra:", bg="DarkGoldenrod").place(x=500, y=10)
Label(ventana_principal, textvariable=porc_desde_venta_str, bg="Gold").place(x=640, y=10)

Label(ventana_principal, text="Porcentaje para venta:", bg="DarkGoldenrod").place(x=500, y=40)
Label(ventana_principal, textvariable=porc_desde_compra_str, bg="Gold").place(x=640, y=40)

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

def abrir_historial():
    historial_ventana = Toplevel(ventana_principal)
    historial_ventana.title("Historial de Operaciones")
    historial_ventana.geometry("600x500")

    Label(historial_ventana, text="📜 Historial de Operaciones", font=("Arial", 14, "bold")).pack()

    frame_compras = Frame(historial_ventana)
    frame_compras.pack(pady=10)
    Label(frame_compras, text="📈 Compras con Objetivo de Venta", font=("Arial", 12, "bold"), fg="blue").pack()
    compras_lista = Listbox(frame_compras, width=80, height=10)
    compras_lista.pack()

    frame_ventas = Frame(historial_ventana)
    frame_ventas.pack(pady=10)
    Label(frame_ventas, text="📉 Ventas Realizadas", font=("Arial", 12, "bold"), fg="green").pack()
    ventas_lista = Listbox(frame_ventas, width=80, height=10)
    ventas_lista.pack()

    # Llenar listas y programar actualizaciones
    actualizar_historial(compras_lista, ventas_lista, historial_ventana)
    historial_ventana.after(5000, lambda: actualizar_historial(compras_lista, ventas_lista, historial_ventana))

    Button(historial_ventana, text="Cerrar", command=historial_ventana.destroy, bg="gray").pack(pady=5)

# Botón Historial
Button(ventana_principal, text="📜 Historial", command=abrir_historial, background="Goldenrod").place(x=700, y=300)
#Button(text="Historial", command=historial, background="Goldenrod").place(x=1000,y=10)
Button(text="Seteo de operatoria", command=abrir_sbv_config, background="Goldenrod").place(x=1000,y=170)

def actualizar_historial(compras_lista, ventas_lista, historial_ventana):
    # Verificar si la ventana del historial sigue abierta antes de actualizar
    if not historial_ventana.winfo_exists():
        return

    compras_lista.delete(0, END)
    ventas_lista.delete(0, END)

    for transaccion in bot.transacciones:
        timestamp = transaccion.get('timestamp', 'Sin fecha')
        compras_lista.insert(
            END, 
            f"[{timestamp}] Compra: {transaccion['compra']:.2f} USDT | BTC: {transaccion['btc']:.6f} | Objetivo: {transaccion['venta_obj']:.2f} USDT"
        )

    for venta in bot.precios_ventas:
        timestamp = venta.get('timestamp', 'Sin fecha')
        ventas_lista.insert(
            END, 
            f"[{timestamp}] Venta: {venta['venta']:.2f} USDT | BTC: {venta['btc_vendido']:.6f} | Ganancia: {venta['ganancia']:.2f} USDT"
        )
    
    # Programar la siguiente actualización solo si la ventana del historial sigue abierta
    historial_ventana.after(5000, lambda: actualizar_historial(compras_lista, ventas_lista, historial_ventana))


ventana_principal.mainloop()