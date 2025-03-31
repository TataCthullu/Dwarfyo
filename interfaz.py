
from tkinter import *

import pygame
pygame.mixer.init()

def reproducir_sonido(ruta):
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play()


from tkinter.scrolledtext import ScrolledText
from codigo_principala import TradingBot

# Instancia del bot
bot = TradingBot()
bot_iniciado = False

# Interfaz Tkinter
ventana_principal = Tk()
ventana_principal.title("Khazâd") 
ventana_principal.geometry("1200x700")
ventana_principal.configure(bg="DarkGoldenrod")
ventana_principal.iconbitmap("imagenes/miner.ico")
ventana_principal.attributes("-alpha",0.95)

# Variables UI
precio_act_var = StringVar()
cant_btc_str = StringVar()
cant_usdt_str = StringVar()
balance_var = StringVar()
btc_en_usdt = StringVar()
varpor_set_venta_str = StringVar()
varpor_set_compra_str = StringVar()
porc_desde_compra_str = StringVar()
porc_desde_venta_str = StringVar()
precio_de_ingreso_str = StringVar()
inv_por_compra_str = StringVar()
var_inicio_str = StringVar()
fixed_buyer_str = StringVar()
ganancia_total_str = StringVar()
contador_compras_fantasma_str = StringVar()
contador_ventas_fantasma_str = StringVar()
porc_objetivo_venta_str = StringVar()

# Etiquetas UI
Label(ventana_principal, text="Precio actual BTC/USDT:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=10, y=10)
Label(ventana_principal, textvariable=precio_act_var, bg="Gold").place(x=200, y=10)

Label(ventana_principal, text="Btc Disponible:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=10, y=130)
Label(ventana_principal, textvariable=cant_btc_str, bg="Gold").place(x=200, y=130)

Label(ventana_principal, text="Btc en Usdt:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=10, y=250)
Label(ventana_principal, textvariable=btc_en_usdt, bg="Gold").place(x=200, y=250)

Label(ventana_principal, text="Ganancia neta en Usdt:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=10, y=290)
Label(ventana_principal, textvariable=ganancia_total_str, bg="Gold").place(x=200, y=290)

Label(ventana_principal, text="Compras fantasma:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=10, y=330)
Label(ventana_principal, textvariable=contador_compras_fantasma_str, bg="Gold").place(x=200, y=330)

Label(ventana_principal, text="Ventas fantasma:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=10, y=370)
Label(ventana_principal, textvariable=contador_ventas_fantasma_str, bg="Gold").place(x=200, y=370)

Label(ventana_principal, text="Usdt Disponible:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=10, y=90)
Label(ventana_principal, textvariable=cant_usdt_str, bg="Gold").place(x=200, y=90)

Label(ventana_principal, text="Usdt + Btc:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=10, y=50)
Label(ventana_principal, textvariable=balance_var, bg="Gold").place(x=200, y=50)

Label(ventana_principal, text="% " "Desde ultima compra:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=10, y=170)
Label(ventana_principal, textvariable=varpor_set_compra_str, bg="Gold").place(x=200, y=170)

Label(ventana_principal, text="% " "Desde ultima venta:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=10, y=210)
Label(ventana_principal, textvariable=varpor_set_venta_str, bg="Gold").place(x=200, y=210)

Label(ventana_principal, text="% " "Desde ultima compra, para compra:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=400, y=10)
Label(ventana_principal, textvariable=porc_desde_venta_str, bg="Gold").place(x=600, y=10)

Label(ventana_principal, text="% " "Desde ultima venta, para compra:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=400, y=40)
Label(ventana_principal, textvariable=porc_desde_compra_str, bg="Gold").place(x=600, y=40)

Label(ventana_principal, text="Precio de ingreso:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=400, y=70)
Label(ventana_principal, textvariable=precio_de_ingreso_str, bg="Gold").place(x=600, y=70)

Label(ventana_principal, text="Inversión por compra:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=400, y=100)
Label(ventana_principal, textvariable=inv_por_compra_str, bg="Gold").place(x=600, y=100)

Label(ventana_principal, text="Variación desde inicio:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=400, y=130)
Label(ventana_principal, textvariable=var_inicio_str, bg="Gold").place(x=600, y=130)

Label(ventana_principal, text="Monto fijo por inversión:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=350, y=160)
Label(ventana_principal, textvariable=fixed_buyer_str, bg="Gold").place(x=600, y=160)

Label(ventana_principal, text="% " "Para objetivo de venta:", bg="DarkGoldenrod", font=("CrushYourEnemies", 7)).place(x=350, y=200)
Label(ventana_principal, textvariable=porc_objetivo_venta_str, bg="Gold").place(x=600, y=200)

# Función para actualizar UI
def actualizar_ui():
    if bot.running:
        #bot.precio_actual = bot.get_precio_actual()
        precio_act_var.set(f"$ {bot.precio_actual:.4f}" if bot.precio_actual else "N/D")
        cant_btc_str.set(f"₿ {bot.btc:.6f}")
        cant_usdt_str.set(f"$ {bot.usdt:.4f}")
        balance_var.set(f"$ {bot.usdt + (bot.btc * bot.precio_actual):.6f}" if bot.precio_actual else 0)
        btc_en_usdt.set(f"$ {bot.btc_usdt:.6f}" if bot.precio_actual else "N/D")
        precio_de_ingreso_str.set(f"$ {bot.precio_ingreso:.4f}" if bot.precio_ingreso else "N/D")
        inv_por_compra_str.set(f"% {bot.porc_inv_por_compra:.4f}")
        varpor_set_compra_str.set(f"% {bot.varCompra:.6f}" if bot.varCompra is not None else "N/D")
        varpor_set_venta_str.set(f"% {bot.varVenta:.6f}" if bot.varVenta is not None else "N/D")
        porc_desde_compra_str.set(f"% {bot.porc_desde_compra:.4f}")   
        porc_desde_venta_str.set(f"% {bot.porc_desde_venta:.4f}")
        var_inicio_str.set(f"% {bot.var_inicio:.6f}" if bot.var_inicio is not None else "N/D")
        fixed_buyer_str.set(f"$ {bot.fixed_buyer:.4f}")
        ganancia_total_str.set(f"$ {bot.total_ganancia:.8f}")
        contador_compras_fantasma_str.set(f"{bot.contador_compras_fantasma}")
        contador_ventas_fantasma_str.set(f"{bot.contador_ventas_fantasma}")
        porc_objetivo_venta_str.set(f"% {bot.porc_profit_x_venta}")


    if not bot.running and not boton_limpiar.winfo_ismapped() and bot_iniciado:
        boton_limpiar.place(x=600, y=300)  
    actualizar_historial_consola()     
  
def log_en_consola(mensaje):
    consola.insert(END, mensaje + "\n")
    consola.see(END)

bot.log_fn = log_en_consola  # Función que imprime en la consola de Tkinter

# Función para crear una nueva instancia limpia del bot
def crear_nuevo_bot():
    nuevo_bot = TradingBot()
    nuevo_bot.log_fn = log_en_consola
    return nuevo_bot

# Instancia global del bot
bot = crear_nuevo_bot()

# === Consola Historial a la derecha ===
historial_box = ScrolledText(ventana_principal, width=35, height=25, bg="Goldenrod", fg="Black", font=("carolingia", 15))
historial_box.place(x=720, y=10)

def actualizar_historial_consola():
    global ganancia_txt
    historial_box.delete('1.0', END)
    for trans in bot.transacciones:
        compra = trans.get('compra', 'N/A')
        venta_obj = trans.get('venta_obj', 'N/A')
        ejecutado = trans.get('ejecutado', False)
        venta_txt = f"$ {venta_obj:.6f}" if ejecutado else "(no vendida)"
        ganancia = trans.get('ganancia', None)
        ganancia_txt = f" | Ganancia: $ {ganancia:.6f}" if ganancia is not None else ""
        historial_box.insert(END, f"Compra: $ {compra:.6f} -> Venta: {venta_txt}\n")
    for venta in bot.precios_ventas:
        historial_box.insert(END, f"Venta ejecutada a: $ {venta['venta']:.4f} | Ganancia: $ {venta['ganancia']:.6f}\n")


# === LÓGICA DE BOTONES ===

def alternar_bot():
    global bot_iniciado
    if bot.running:
        bot.detener()
        reproducir_sonido("Sounds/detner.wav")
        boton_estado.config(text="Iniciar")
    else:
        bot.iniciar()
        bot.loop(actualizar_ui)

        bot_iniciado = True
        reproducir_sonido("Sounds/soundinicio.wav")
        actualizar_ui()
        boton_estado.config(text="Detener")

def limpiar_bot():
    global bot_iniciado
    global bot
    if not bot.running:
        reproducir_sonido("Sounds/soundlimpiara.wav")
        consola.delete('1.0', END)        
        bot = crear_nuevo_bot()
        log_en_consola("🔄 Bot reiniciado")
        boton_limpiar.place_forget()
        boton_estado.config(text="Iniciar")
        bot_iniciado = False
        # Resetear valores UI
        precio_act_var.set("")
        cant_btc_str.set("")
        cant_usdt_str.set("")
        balance_var.set("")
        btc_en_usdt.set("")
        precio_de_ingreso_str.set("")
        inv_por_compra_str.set("")
        varpor_set_compra_str.set("")
        varpor_set_venta_str.set("")
        porc_desde_compra_str.set("")
        porc_desde_venta_str.set("")
        var_inicio_str.set("")
        fixed_buyer_str.set("")
        ganancia_total_str.set("")
        contador_compras_fantasma_str.set("")
        contador_ventas_fantasma_str.set("")
        porc_objetivo_venta_str.set("")

# Botones
boton_estado = Button(ventana_principal, text="Iniciar", background="Goldenrod", command=alternar_bot)
boton_estado.place(x=500, y=300)

boton_limpiar = Button(ventana_principal, text="Limpiar", background="Goldenrod", command=limpiar_bot)


# Subventanas
"""def abrir_sbv_config():
    sbv_conf = Toplevel(ventana_principal)
    sbv_conf.title("Configuración de operativa")
    sbv_conf.geometry("400x300")
    Label(sbv_conf, text="Configurar operativa").pack()"""

# Consola para mostrar estado
consola = ScrolledText(ventana_principal, width=35, height=15, bg="Goldenrod", fg="Black", font=("carolingia", 15))
consola.place(x=10, y=450)    


actualizar_ui()
ventana_principal.mainloop()