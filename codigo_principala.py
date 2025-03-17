import threading
import time
import ccxt
from tkinter import *

class TradingBot:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.usdt = 10000
        self.btc = 0
        self.btc_comprado = 0
        self.precio_ult_comp = self.get_precio_actual()
        self.precio_ult_venta = 0
        self.porc_por_compra = 0.007
        self.porc_por_venta = 0.007
        self.porc_inv_por_compra = 10
        self.fixed_buyer = self.cant_inv()
        self.running = False

    def get_precio_actual(self):
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            return ticker['last']
        except Exception as e:
            print(f"Error obteniendo el precio: {e}")
            return 


    def cant_inv(self):
        return (self.usdt * self.porc_inv_por_compra) / 100

    def comprar(self):
        if self.usdt < self.fixed_buyer:
            return
        self.usdt -= self.fixed_buyer
        self.btc_comprado = (1 / self.get_precio_actual()) * self.fixed_buyer
        self.btc += self.btc_comprado
        self.precio_ult_comp = self.get_precio_actual()

    def vender(self):
        if self.btc < self.btc_comprado:
            return
        self.precio_ult_venta = self.get_precio_actual()
        kant_usdt_vendido = self.btc_comprado * self.precio_ult_venta
        self.usdt += kant_usdt_vendido
        self.btc -= self.btc_comprado

    def iniciar(self):
        self.running = True
        while self.running:
            precio_actual = self.get_precio_actual()
            varpor_compra = ((precio_actual - self.precio_ult_comp) / self.precio_ult_comp) * 100
            varpor_venta = ((precio_actual - self.precio_ult_venta) / self.precio_ult_venta) * 100

            if varpor_venta <= -self.porc_por_compra:
                self.comprar()
            if varpor_compra >= self.porc_por_venta:
                self.vender()
            time.sleep(3)

    def detener(self):
        self.running = False

# Interfaz Tkinter
ventana_principal = Tk()
ventana_principal.title("Dwarf") 
ventana_principal.minsize(width=1200, height=700)
ventana_principal.iconbitmap("imagenes/miner.ico")
ventana_principal.configure(bg="LightBlue")
ventana_principal.resizable(False, False)
ventana_principal.geometry("1200x700+200+200")
ventana_principal.attributes("-alpha",0.9)

bot = TradingBot()

"""label_balance = Label(ventana_principal, text=f"Balance: {bot.usdt:.2f} USDT", font=("Arial", 14))
label_balance.pack()

label_btc = Label(ventana_principal, text=f"BTC: {bot.btc:.6f}", font=("Arial", 14))
label_btc.pack()"""

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


# Variables UI
precio_act_var = StringVar()
cant_btc_str = StringVar()
cant_usdt_str = StringVar()
balance_var = StringVar()

# Etiquetas UI
Label(ventana_principal, text="Precio actual BTC/USDT:", bg="LightBlue").place(x=10, y=10)
Label(ventana_principal, textvariable=precio_act_var, bg="LightGreen").place(x=200, y=10)
Label(ventana_principal, text="BTC Disponible:", bg="LightBlue").place(x=10, y=50)
Label(ventana_principal, textvariable=cant_btc_str, bg="LightGreen").place(x=200, y=50)
Label(ventana_principal, text="USDT Disponible:", bg="LightBlue").place(x=10, y=90)
Label(ventana_principal, textvariable=cant_usdt_str, bg="LightGreen").place(x=200, y=90)
Label(ventana_principal, text="Balance Total:", bg="LightBlue").place(x=10, y=130)
Label(ventana_principal, textvariable=balance_var, bg="LightGreen").place(x=200, y=130)

#Función para actualizar UI periódicamente
def actualizar_ui():
    if bot.running:
        precio_act_var.set(f"{bot.get_precio_actual():.2f} USDT")
        cant_btc_str.set(f"{bot.btc:.6f} BTC")
        cant_usdt_str.set(f"{bot.usdt:.2f} USDT")
        balance_var.set(f"{bot.usdt + (bot.btc * bot.get_precio_actual()):.2f} USDT")
    ventana_principal.after(3000, actualizar_ui)  # Llama de nuevo cada 3 segundos

# Funciones de control
def iniciar_bot():
    if not bot.running:
        bot.running = True
        threading.Thread(target=bot.iniciar, daemon=True).start()
        actualizar_ui()  # Iniciar la actualización UI al mismo tiempo

def detener_bot():
    bot.detener()

# Botones
Button(ventana_principal, text="Iniciar Bot", command=iniciar_bot).place(x=10, y=180)
Button(ventana_principal, text="Detener Bot", command=detener_bot).place(x=100, y=180)

ventana_principal.mainloop()




