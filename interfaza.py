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
def iniciar_interfaz(bot):
    # Ventana principal
    ventana_principal = Tk()
    ventana_principal.title("Khazâd")
    # ventana_principal.geometry("1200x700")
    ventana_principal.configure(bg="DarkGoldenrod")
    ventana_principal.iconbitmap("imagenes/dm.ico")
    ventana_principal.attributes("-alpha", 0.95)

    # Variables UI (igual que antes)
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
    ghost_ratio_var = StringVar()
    compras_realizadas_str = StringVar()
    ventas_realizadas_str = StringVar()

    # --- main_frame: contenedor principal ---
    main_frame = Frame(ventana_principal, bg="DarkGoldenrod")
    main_frame.grid(row=0, column=0, sticky="nsew")
    ventana_principal.grid_rowconfigure(0, weight=1)
    ventana_principal.grid_columnconfigure(0, weight=1)

    # Configuramos tres columnas en main_frame:
    # Columna 0: info_frame, fija: minsize=300, weight=0
    # Columna 1: center_frame, fija: minsize=300, weight=0
    # Columna 2: right_frame, expandible: minsize=300, weight=2
    main_frame.grid_columnconfigure(0, weight=0, minsize=350)
    main_frame.grid_columnconfigure(1, weight=0, minsize=350)
    main_frame.grid_columnconfigure(2, weight=2, minsize=350)

    # Configuramos la fila 0 (área de contenido) para expandirse y la fila 1 (botones) con peso 0:
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=0)

    # --- Frame izquierdo: info_frame (Columna 0) ---
    info_frame = Frame(main_frame, bg="DarkGoldenrod")
    info_frame.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

    # Función para agregar filas a info_frame usando grid (alineados a la izquierda)
    def add_info_row(label_text, variable, font=("CrushYourEnemies", 12)):
        r_frame = Frame(info_frame, bg="DarkGoldenrod")
        r_frame.grid(sticky="w", padx=5, pady=2)
        lbl = Label(r_frame, text=label_text, bg="DarkGoldenrod", font=font)
        lbl.pack(side=LEFT, anchor="w", padx=(0,5))
        val = Label(r_frame, textvariable=variable, bg="Gold", font=font)
        val.pack(side=LEFT, anchor="w")
        
    # Agregar información al info_frame
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

    # --- Frame para el contenedor central (columna 1) ---
    center_frame = Frame(main_frame, bg="DarkGoldenrod")
    center_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
    # En lugar de usar place para centrar, empacamos center_info_frame en la parte superior:
    center_info_frame = Frame(center_frame, bg="DarkGoldenrod")
    center_info_frame.pack(side=TOP, fill=X, padx=5, pady=5)
    # Si lo deseas, puedes forzar un tamaño mínimo usando center_info_frame.config(width=250)

    # --- Función para agregar filas al contenedor central (center_info_frame) ---
    def add_center_info_row(label_text, variable, font=("CrushYourEnemies", 12)):
        row = Frame(center_info_frame, bg="DarkGoldenrod")
        row.grid(sticky="ew", padx=5, pady=2)
        lbl = Label(row, text=label_text, bg="DarkGoldenrod", font=font, anchor="e")
        lbl.grid(row=0, column=0, sticky="e", padx=5)
        val = Label(row, textvariable=variable, bg="Gold", font=font, anchor="w")
        val.grid(row=0, column=1, sticky="w", padx=5)
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

    # Agregar filas al área central:
    add_center_info_row("Ghost Ratio:", ghost_ratio_var)
    add_center_info_row("Compras Realizadas:", compras_realizadas_str)
    add_center_info_row("Ventas Realizadas:", ventas_realizadas_str)


    # --- Frame derecho: right_frame (Columna 2) ---
    right_frame = Frame(main_frame, bg="DarkGoldenrod")
    right_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
    # Permitir que right_frame se expanda según la columna (weight=2)
    right_frame.grid_rowconfigure(0, weight=1)
    right_frame.grid_rowconfigure(1, weight=1)
    right_frame.grid_columnconfigure(0, weight=1)

    # Usamos grid para colocar los ScrolledText en right_frame
    historial_box = ScrolledText(right_frame, bg="Goldenrod", fg="Black", font=("CrushYourEnemies", 10))
    historial_box.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
    consola = ScrolledText(right_frame, bg="Goldenrod", fg="Black", font=("CrushYourEnemies", 10))
    consola.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

    # --- Botones: button_frame (Fila 1) ---
    button_frame = Frame(main_frame, bg="DarkGoldenrod")
    button_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
    # Configuramos button_frame para que los botones se expandan horizontalmente:
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    boton_estado = Button(button_frame, text="Iniciar", bg="Goldenrod", command=lambda: alternar_bot(), font=("CrushYourEnemies", 7))
    boton_estado.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
    boton_limpiar = Button(button_frame, text="Limpiar", bg="Goldenrod", command=lambda: limpiar_bot(), font=("CrushYourEnemies", 7))
    boton_limpiar.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
    boton_limpiar.grid_remove()
    limpiar_visible = False

    # --- Funciones de actualización y control se mantienen iguales ---
    def actualizar_ui():
        if not ventana_principal.winfo_exists():
            return
        try:
            if bot.running:
                precio_act_var.set(f"$ {bot.precio_actual:.4f}" if bot.precio_actual else "N/D")
                cant_btc_str.set(f"₿ {bot.btc:.6f}")
                cant_usdt_str.set(f"$ {bot.usdt:.6f}")
                balance_var.set(f"$ {bot.usdt + (bot.btc * bot.precio_actual):.6f}" if bot.precio_actual else 0)
                btc_en_usdt.set(f"$ {bot.btc_usdt:.6f}" if bot.precio_actual else "N/D")
                precio_de_ingreso_str.set(f"$ {bot.precio_ingreso:.4f}" if bot.precio_ingreso else "N/D")
                inv_por_compra_str.set(f"% {bot.porc_inv_por_compra:.4f}")
                varpor_set_compra_str.set(f"% {bot.varCompra:.6f}" if bot.varCompra is not None else "N/D")
                varpor_set_venta_str.set(f"% {bot.varVenta:.6f}" if bot.varVenta is not None else "N/D")
                porc_desde_compra_str.set(f"% {bot.porc_desde_compra:.4f}")
                porc_desde_venta_str.set(f"% {bot.porc_desde_venta:.4f}")
                var_inicio_str.set(f"% {bot.var_inicio:.6f}" if bot.var_inicio is not None else "N/D")
                fixed_buyer_str.set(f"$ {bot.fixed_buyer:.2f}")
                ganancia_total_str.set(f"$ {bot.total_ganancia:.6f}")
                contador_compras_fantasma_str.set(f"{bot.contador_compras_fantasma}")
                contador_ventas_fantasma_str.set(f"{bot.contador_ventas_fantasma}")
                porc_objetivo_venta_str.set(f"% {bot.porc_profit_x_venta}")
                ghost_ratio = bot.calcular_ghost_ratio()
                ghost_ratio_var.set(f"{ghost_ratio:.2f}")
                compras_realizadas_str.set(f"{bot.contador_compras_reales}")
                ventas_realizadas_str.set(f"{bot.contador_ventas_reales}")
                actualizar_historial_consola()
            # Si el bot está detenido, mostramos "Limpiar" solo si el flag lo permite
            if limpiar_visible:
                boton_limpiar.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
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

    bot = crear_nuevo_bot()

    def actualizar_historial_consola():
        historial_box.delete('1.0', END)
        for trans in bot.transacciones:
            compra = trans.get('compra', 'N/A')
            venta_obj = trans.get('venta_obj', 'N/A')
            venta_txt = f"$ {venta_obj:.4f} (No ejecutada)"
            compra_numero_txt = trans.get('numcompra', 'N/A')
            historial_box.insert(END, f"Compra: $ {compra:.2f}, numero: {compra_numero_txt} -> Venta: {venta_txt}\n")
        for venta in bot.precios_ventas:
            historial_box.insert(END, f"Venta ejecutada de: $ {venta['compra']:.2f}, numero: {venta['venta_numero']}, a: $ {venta['venta']:.2f} | Ganancia: $ {venta['ganancia']:.4f}\n")

    def alternar_bot():
        global limpiar_visible
        if not bot.running:
            bot.iniciar()
            bot.loop(actualizar_ui, ventana_principal.after)
            reproducir_sonido("Sounds/soundinicio.wav")
            actualizar_ui()
            boton_estado.config(text="Detener") 
            boton_limpiar.grid_remove()       
        else:
            bot.detener()
            reproducir_sonido("Sounds/detner.wav")
            boton_estado.grid_remove()
            limpiar_visible = True
            boton_limpiar.grid(row=0, column=1, sticky="ew", padx=2, pady=2)

    def limpiar_bot():
        if not bot.running:
            reproducir_sonido("Sounds/soundlimpiara.wav")
            consola.delete('1.0', END)
            historial_box.delete('1.0', END)
            bot = crear_nuevo_bot()
            log_en_consola("🔄 Bot reiniciado")
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
            ghost_ratio_var.set("")
            compras_realizadas_str.set("")
            ventas_realizadas_str.set("")
            # Luego de limpiar, ocultamos Limpiar y volvemos a mostrar el botón de Iniciar
            limpiar_visible = False
            boton_limpiar.grid_remove()
            boton_estado.grid(row=0, column=0, sticky="ew", padx=2, pady=2)
            boton_estado.config(text="Iniciar")
        else:
            boton_limpiar.grid_remove()

    actualizar_ui()
    ventana_principal.mainloop()

