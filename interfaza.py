

import threading
from tkinter import *
from tkinter.scrolledtext import ScrolledText
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
btc_en_usdt = StringVar()

varpor_set_venta_str = StringVar()
varpor_set_compra_str = StringVar()
porc_desde_compra_str = StringVar()
porc_desde_venta_str = StringVar()
precio_de_ingreso_str = StringVar()
inv_por_compra_str = StringVar()
var_inicio_str = StringVar()
fixed_buyer_str = StringVar()

# Etiquetas UI
Label(ventana_principal, text="Precio actual BTC/USDT:", bg="DarkGoldenrod").place(x=10, y=10)
Label(ventana_principal, textvariable=precio_act_var, bg="Gold").place(x=200, y=10)

Label(ventana_principal, text="Btc Disponible:", bg="DarkGoldenrod").place(x=10, y=130)
Label(ventana_principal, textvariable=cant_btc_str, bg="Gold").place(x=200, y=130)

Label(ventana_principal, text="Btc en Usdt:", bg="DarkGoldenrod").place(x=10, y=250)
Label(ventana_principal, textvariable=btc_en_usdt, bg="Gold").place(x=200, y=250)

Label(ventana_principal, text="Usdt Disponible:", bg="DarkGoldenrod").place(x=10, y=90)
Label(ventana_principal, textvariable=cant_usdt_str, bg="Gold").place(x=200, y=90)

Label(ventana_principal, text="Usdt + Btc:", bg="DarkGoldenrod").place(x=10, y=50)
Label(ventana_principal, textvariable=balance_var, bg="Gold").place(x=200, y=50)

Label(ventana_principal, text="Variación desde ultima compra:", bg="DarkGoldenrod").place(x=10, y=170)
Label(ventana_principal, textvariable=varpor_set_compra_str, bg="Gold").place(x=200, y=170)

Label(ventana_principal, text="Variación desde ultima venta:", bg="DarkGoldenrod").place(x=10, y=210)
Label(ventana_principal, textvariable=varpor_set_venta_str, bg="Gold").place(x=200, y=210)

Label(ventana_principal, text="Porcentaje para compra:", bg="DarkGoldenrod").place(x=500, y=10)
Label(ventana_principal, textvariable=porc_desde_venta_str, bg="Gold").place(x=640, y=10)

Label(ventana_principal, text="Porcentaje para venta:", bg="DarkGoldenrod").place(x=500, y=40)
Label(ventana_principal, textvariable=porc_desde_compra_str, bg="Gold").place(x=640, y=40)

Label(ventana_principal, text="Precio de ingreso:", bg="DarkGoldenrod").place(x=500, y=70)
Label(ventana_principal, textvariable=precio_de_ingreso_str, bg="Gold").place(x=640, y=70)

Label(ventana_principal, text="Inversión por compra:", bg="DarkGoldenrod").place(x=500, y=100)
Label(ventana_principal, textvariable=inv_por_compra_str, bg="Gold").place(x=640, y=100)

Label(ventana_principal, text="Variación desde inicio:", bg="DarkGoldenrod").place(x=500, y=130)
Label(ventana_principal, textvariable=var_inicio_str, bg="Gold").place(x=640, y=130)

Label(ventana_principal, text="Monto fijo por inversión:", bg="DarkGoldenrod").place(x=500, y=160)
Label(ventana_principal, textvariable=fixed_buyer_str, bg="Gold").place(x=640, y=160)

# Función para actualizar UI
def actualizar_ui():
    if bot.running:
        bot.precio_actual = bot.get_precio_actual()
        precio_act_var.set(f"$ {bot.precio_actual:.4f}")
        cant_btc_str.set(f"₿ {bot.btc:.6f}")
        cant_usdt_str.set(f"$ {bot.usdt:.4f}")
        balance_var.set(f"$ {bot.usdt + (bot.btc * bot.precio_actual):.6f}")
        btc_en_usdt.set(f"$ {bot.btc_usdt:.6f}")
        precio_de_ingreso_str.set(f"$ {bot.precio_ingreso:.4f}")
        inv_por_compra_str.set(f"% {bot.porc_inv_por_compra:.4f}")

        varpor_set_compra_str.set(f"% {bot.varpor_compra(bot.precio_ult_comp, bot.precio_actual):.6f}")
        varpor_set_venta_str.set(f"% {bot.varpor_venta(bot.precio_ult_venta, bot.precio_actual):.6f}")
        porc_desde_compra_str.set(f"% {bot.porc_por_compra:.4f}")   
        porc_desde_venta_str.set(f"% {bot.porc_por_venta:.4f}")
        var_inicio_str.set(f"% {bot.var_inicio:.6f}")
        fixed_buyer_str.set(f"$ {bot.fixed_buyer:.4f}")

    boton_limpiar.place_forget()  # Oculta siempre por defecto
    if not bot.running:
        boton_limpiar.place(x=600, y=300)  # Solo muestra si el bot está detenido

    actualizar_historial_consola()    
    # Reprogramar la actualización cada 3 segundos
    ventana_principal.after(3000, actualizar_ui)




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
historial_box = ScrolledText(ventana_principal, width=50, height=30, bg="Goldenrod", fg="Black", font=("Courier", 10))
historial_box.place(x=750, y=10)

def actualizar_historial_consola():
    historial_box.delete('1.0', END)
    for trans in bot.transacciones:
        compra = trans.get('compra', 'N/A')
        venta_obj = trans.get('venta_obj', 'N/A')
        ejecutado = trans.get('ejecutado', False)
        venta_txt = f"{venta_obj:.2f} USDT" if ejecutado else "(no vendida)"
        historial_box.insert(END, f"Compra: {compra:.2f} USDT  -> Venta: {venta_txt}\n")
    for venta in bot.precios_ventas:
        historial_box.insert(END, f"Venta ejecutada a: {venta['venta']:.2f} USDT\n")
    

# === LÓGICA DE BOTONES ===

def alternar_bot():
    if bot.running:
        bot.detener()
        boton_estado.config(text="Iniciar Bot")
    else:
        threading.Thread(target=bot.iniciar, daemon=True).start()
        actualizar_ui()
        boton_estado.config(text="Detener Bot")

def limpiar_bot():
    global bot
    if not bot.running:
        consola.delete('1.0', END)
        bot = crear_nuevo_bot()
        log_en_consola("🔄 Bot reiniciado")
        boton_limpiar.place_forget()
        boton_estado.config(text="Iniciar Bot")
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
    

# Botones
boton_estado = Button(ventana_principal, text="Iniciar Bot", background="Goldenrod", command=alternar_bot)
boton_estado.place(x=500, y=300)

boton_limpiar = Button(ventana_principal, text="Limpiar", background="Goldenrod", command=limpiar_bot)


# Subventanas
def abrir_sbv_config():
    sbv_conf = Toplevel(ventana_principal)
    sbv_conf.title("Configuración de operativa")
    sbv_conf.geometry("400x300")
    Label(sbv_conf, text="Configurar operativa").pack()

# Consola para mostrar estado
consola = ScrolledText(ventana_principal, width=50, height=15, bg="Goldenrod", fg="Black", font=("Courier", 10))
consola.place(x=10, y=400)    

"""def abrir_historial():
    historial_ventana = Toplevel(ventana_principal)
    historial_ventana.title("Historial de Operaciones")
    historial_ventana.geometry("600x500")
    historial_ventana.configure(bg="DarkGoldenrod")

    Label(historial_ventana, text="📜 Historial de Operaciones", bg="DarkGoldenrod").pack()

    frame_compras = Frame(historial_ventana)
    frame_compras.pack(pady=10)
    Label(frame_compras, text="📈 Compras con Objetivo de Venta", fg="blue", bg="DarkGoldenrod").pack()
    compras_lista = Listbox(frame_compras, width=80, height=10, bg="DarkGoldenrod")
    compras_lista.pack()

    frame_ventas = Frame(historial_ventana)
    frame_ventas.pack(pady=10)
    Label(frame_ventas, text="📉 Ventas Realizadas", fg="green", bg="DarkGoldenrod").pack()
    ventas_lista = Listbox(frame_ventas, width=80, height=10, bg="DarkGoldenrod")
    ventas_lista.pack()

    # Llenar listas y programar actualizaciones
    actualizar_historial(compras_lista, ventas_lista, historial_ventana)
    historial_ventana.after(5000, lambda: actualizar_historial(compras_lista, ventas_lista, historial_ventana))

    Button(historial_ventana, text="Cerrar", command=historial_ventana.destroy, bg="Goldenrod").pack(pady=5)"""

"""# Botón Historial
Button(ventana_principal, text="📜 Historial", command=abrir_historial, background="Goldenrod").place(x=700, y=300)
#Button(text="Historial", command=historial, background="Goldenrod").place(x=1000,y=10)
Button(text="Seteo de operatoria", command=abrir_sbv_config, background="Goldenrod").place(x=1000,y=170)"""



"""def actualizar_historial(compras_lista, ventas_lista, historial_ventana):
    # Verificar si la ventana del historial sigue abierta antes de actualizar
    if not historial_ventana.winfo_exists():
        return

    compras_lista.delete(0, END)
    ventas_lista.delete(0, END)

    for transaccion in bot.transacciones:
        timestamp = transaccion.get('timestamp', 'Sin fecha')
        estado = "✅ Ejecutado" if transaccion.get('ejecutado', False) else "⏳ Pendiente"
        compras_lista.insert(
            END, 
            f"[{timestamp}] Compra: {transaccion['compra']:.6f} USDT | BTC: {transaccion['btc']:.6f} | Objetivo: {transaccion['venta_obj']:.6f} USDT | {estado}"
        )

    for venta in bot.precios_ventas:
        timestamp = venta.get('timestamp', 'Sin fecha')
        ventas_lista.insert(
            END, 
            f"[{timestamp}] Venta: {venta['venta']:.2f} USDT | BTC: {venta['btc_vendido']:.6f} | Ganancia: {venta['ganancia']:.2f} USDT ✅ Ejecutado"
        )
    
    # Programar la siguiente actualización solo si la ventana del historial sigue abierta
    historial_ventana.after(5000, lambda: actualizar_historial(compras_lista, ventas_lista, historial_ventana))"""


actualizar_ui()
ventana_principal.mainloop()