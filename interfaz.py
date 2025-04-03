from tkinter import *
import pygame
from tkinter.scrolledtext import ScrolledText
from codigo_principala import TradingBot

pygame.mixer.init()

def reproducir_sonido(ruta):
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play()

# Instancia del bot
bot = TradingBot()

# Interfaz Tkinter
ventana_principal = Tk()
ventana_principal.title("Khazâd")
# Puedes ajustar el tamaño o dejar que se ajuste dinámicamente
#ventana_principal.geometry("1200x700")
ventana_principal.configure(bg="DarkGoldenrod")
ventana_principal.iconbitmap("imagenes/dm.ico")
ventana_principal.attributes("-alpha", 0.95)

# Variables UI (para la sección de información)
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

# --- Estructura general de la ventana ---
# main_frame se divide en dos columnas:
#   Columna 0: info_frame (área fija para información, pegada a la izquierda)
#   Columna 1: right_frame (área para consolas, anclada a la derecha y expandible)
# Y en la fila 1 se colocan los botones.
main_frame = Frame(ventana_principal, bg="DarkGoldenrod")
main_frame.grid(row=0, column=0, sticky="nsew")
# Definimos ancho fijo para info y mínimo para consolas:
main_frame.grid_columnconfigure(0, minsize=300, weight=0)  # área de info: ancho fijo
main_frame.grid_columnconfigure(1, minsize=500, weight=1)  # área de consolas: se expande
ventana_principal.grid_rowconfigure(0, weight=1)
ventana_principal.grid_columnconfigure(0, weight=1)

# Frame para la información (izquierda)
info_frame = Frame(main_frame, bg="DarkGoldenrod")
info_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)
info_frame.grid_columnconfigure(0, weight=1)
info_frame.grid_columnconfigure(1, weight=1)
info_frame.config(width=300)

# Frame para el área de consolas (derecha)
# Se ancla a la derecha mediante sticky="e"
right_frame = Frame(main_frame, bg="DarkGoldenrod")
right_frame.grid(row=0, column=1, sticky="e", padx=5, pady=5)
# En right_frame usaremos pack para que sus widgets se expandan.
# No asignamos weight a esta columna para mantener su ancho mínimo fijo.

# Frame para botones (abajo, fila 1 de main_frame)
button_frame = Frame(main_frame, bg="DarkGoldenrod")
button_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
main_frame.grid_rowconfigure(1, weight=0)  # No se expande verticalmente

# Dentro del info_frame, usamos un row_frame para cada línea para mantener etiqueta y valor pegados.
def add_info_row(label_text, variable, font=("CrushYourEnemies", 14)):
    row_frame = Frame(info_frame, bg="DarkGoldenrod")
    row_frame.grid(row=add_info_row.row_index, column=0, sticky="w", padx=0, pady=2)
    add_info_row.row_index += 1
    lbl = Label(row_frame, text=label_text, bg="DarkGoldenrod", font=font)
    lbl.pack(side=LEFT, anchor="w", padx=(0,2))
    val = Label(row_frame, textvariable=variable, bg="Gold", font=font)
    val.pack(side=LEFT, anchor="w", padx=(0,2))
add_info_row.row_index = 0

# Agregar cada línea de información
add_info_row("Precio actual BTC/USDT:", precio_act_var)
add_info_row("Usdt + Btc:", balance_var)
add_info_row("Usdt Disponible:", cant_usdt_str)
add_info_row("Btc Disponible:", cant_btc_str)
add_info_row("Btc en Usdt:", btc_en_usdt)
add_info_row("% Desde ultima compra:", varpor_set_compra_str)
add_info_row("% Desde ultima venta:", varpor_set_venta_str)
add_info_row("% Desde ultima compra, para compra:", porc_desde_venta_str)
add_info_row("% Desde ultima venta, para compra:", porc_desde_compra_str)
add_info_row("Precio de ingreso:", precio_de_ingreso_str)
add_info_row("Inversión por compra:", inv_por_compra_str)
add_info_row("Variación desde inicio:", var_inicio_str)
add_info_row("Monto fijo por inversión:", fixed_buyer_str)
add_info_row("% Para objetivo de venta:", porc_objetivo_venta_str)
add_info_row("Ganancia neta en Usdt:", ganancia_total_str)
add_info_row("Compras fantasma:", contador_compras_fantasma_str)
add_info_row("Ventas fantasma:", contador_ventas_fantasma_str)

# --- Área de consolas (derecha) ---
# Usamos pack para que los widgets se mantengan anclados a la derecha y se expandan.
historial_box = ScrolledText(right_frame, width=45, height=10, bg="Goldenrod", fg="Black", font=("CrushYourEnemies", 14))
historial_box.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
consola = ScrolledText(right_frame, width=50, height=10, bg="Goldenrod", fg="Black", font=("CrushYourEnemies", 14))
consola.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)

# --- Botones en button_frame ---
boton_estado = Button(button_frame, text="Iniciar", background="Goldenrod", command=lambda: alternar_bot(), font=("CrushYourEnemies", 7))
boton_estado.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
boton_limpiar = Button(button_frame, text="Limpiar", background="Goldenrod", command=lambda: limpiar_bot(), font=("CrushYourEnemies", 7))
boton_limpiar.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)

# --- Funciones de actualización y control ---
def actualizar_ui():
    # Evita actualizar si la ventana ya se destruyó
    if not ventana_principal.winfo_exists():
        return
    try:
        if bot.running:
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
            ganancia_total_str.set(f"$ {bot.total_ganancia:.6f}")
            contador_compras_fantasma_str.set(f"{bot.contador_compras_fantasma}")
            contador_ventas_fantasma_str.set(f"{bot.contador_ventas_fantasma}")
            porc_objetivo_venta_str.set(f"% {bot.porc_profit_x_venta}")
            actualizar_historial_consola()
        else:
            # Si el bot no está corriendo, se muestra el botón de limpiar
            boton_limpiar.grid()
    except Exception as e:
        print("Error al actualizar la interfaz:", e)

def log_en_consola(mensaje):
    consola.insert(END, mensaje + "\n")
    consola.see(END)

bot.log_fn = log_en_consola

def crear_nuevo_bot():
    nuevo_bot = TradingBot()
    nuevo_bot.log_fn = log_en_consola
    return nuevo_bot

# Reasigna la instancia global del bot
bot = crear_nuevo_bot()

def actualizar_historial_consola():
    historial_box.delete('1.0', END)
    for trans in bot.transacciones:
        compra = trans.get('compra', 'N/A')
        venta_obj = trans.get('venta_obj', 'N/A')
        ejecutado = trans.get('ejecutado', False)
        venta_txt = f"$ {venta_obj:.4f} (No ejecutada)" 
        ganancia = trans.get('ganancia', None)
        historial_box.insert(END, f"Compra: $ {compra:.2f} -> Venta: {venta_txt}\n")
    for venta in bot.precios_ventas:
        historial_box.insert(END, f"Venta ejecutada a: $ {venta['venta']:.2f} | Ganancia: $ {venta['ganancia']:.6f}\n")

def alternar_bot():
    if bot.running:
        bot.detener()
        reproducir_sonido("Sounds/detner.wav")
        boton_estado.config(text="Iniciar")
    else:
        bot.iniciar()
        bot.loop(actualizar_ui, ventana_principal.after)
        reproducir_sonido("Sounds/soundinicio.wav")
        actualizar_ui()
        boton_estado.config(text="Detener")

def limpiar_bot():
    global bot
    if not bot.running:
        reproducir_sonido("Sounds/soundlimpiara.wav")
        consola.delete('1.0', END)
        historial_box.delete('1.0', END)
        bot = crear_nuevo_bot()
        log_en_consola("🔄 Bot reiniciado")
        # Resetear variables UI
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
        boton_estado.config(text="Iniciar")
    else:
        boton_limpiar.grid_remove()

# Inicializa la actualización de la interfaz y arranca el mainloop
actualizar_ui()
ventana_principal.mainloop()
