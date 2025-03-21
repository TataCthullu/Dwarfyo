import time
import ccxt
import datetime
from tkinter.scrolledtext import ScrolledText
#import json

"""Azul (\033[94m) para información general.
Amarillo (\033[93m) para valores clave como precios de ingreso.
Verde (\033[92m) para operaciones exitosas como compras y ventas.
Rojo (\033[91m) para advertencias y errores.
Cian (\033[96m) para detalles adicionales."""

class TradingBot:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.usdt = 1000
        self.btc = 0
        
        self.btc_comprado = 0
        self.precio_actual = self.get_precio_actual()
        self.btc_usdt = self.btc * self.precio_actual
        self.parametro_compra_desde_compra = None
        self.parametro_compra_desde_venta = None
        self.precio_ult_venta = 0
        self.porc_por_compra = 0.007
        self.porc_por_venta = 0.007
        self.porc_inv_por_compra = 20
        self.fixed_buyer = self.cant_inv()
        self.running = False
        self.precio_ult_comp = self.precio_actual
        self.usdt_mas_btc = 0
        self.precios_compras = []
        self.precios_ventas = []
        self.kant_usdt_vendido = 0
        self.varCompra = 0
        self.varVenta = 0
        self.transacciones = []
        self.btc_vendido = 0
        self.precio_objetivo_venta = 0
        self.precio_ingreso = self.get_precio_actual()
        self.var_inicio = 0
        self.log_fn = None

    def log(self, mensaje):
        if self.log_fn:
            self.log_fn(mensaje)    
               
    def get_precio_actual(self):
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            return ticker['last']
        except Exception as e:
            self.log(f"❌ Error obteniendo el precio: {e}")
            return
    
    def actualizar_balance(self):
        self.usdt_mas_btc = self.usdt + (self.btc * self.precio_actual)

    #Variacion de precio con respecto a ultima compra
    def varpor_compra(self, precio_ult_comp, precio_act_btc):
                variante = ((precio_act_btc - precio_ult_comp) / precio_ult_comp) * 100
                return variante 

    #Variacion desde ultima venta 
    def varpor_venta(self, precio_ult_venta, precio_act_btc):
        if precio_ult_venta == 0:
            return 0
        variante = ((precio_act_btc - precio_ult_venta) / precio_ult_venta) * 100
        return variante
    
    def varpor_ingreso(self):
        if self.precio_ingreso == 0:
            return 0  # Para evitar división por cero
        variacion = ((self.precio_actual - self.precio_ingreso) / self.precio_ingreso) * 100
        return variacion


    def cant_inv(self):
        return (self.usdt * self.porc_inv_por_compra) / 100

    def comprar(self):
            if self.usdt < self.fixed_buyer:
                self.log("⚠️ Fondos insuficientes para comprar.")
                return
            else:
                print(f"\n\033[96mCompra realizada.\033[0m")
                self.usdt -= self.fixed_buyer
                self.btc_usdt += ((1/self.precio_actual) * self.fixed_buyer) * self.precio_actual
                self.precio_ult_comp = self.precio_actual
                self.precios_compras.append(self.precio_ult_comp)
                self.btc_comprado = (1/self.precio_actual) * self.fixed_buyer
                self.precio_objetivo_venta = self.precio_actual * (1 + self.porc_por_venta / 100)
                self.btc += self.btc_comprado 
                self.transacciones.append({
                    "compra": self.precio_actual,
                    "venta_obj": self.precio_objetivo_venta,
                    "btc": self.btc_comprado,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                self.actualizar_balance()
                self.log("✅ Compra realizada.")
                self.log(f"📉 Precio de compra: {self.precio_actual:.2f} USDT")
                self.log(f"🪙 BTC comprado: {self.btc_comprado:.6f}")
                self.log(f"🎯 Objetivo de venta: {self.precio_objetivo_venta:.2f} USDT")

                #print("\033[94mPrecios de compra: $\033[0m", self.precios_compras)  
                """print("Btc comprado: ", (1/self.precio_actual) * self.fixed_buyer) 
                print("Btc comprado representado en Usdt: $", self.fixed_buyer)  
                print(f"Objetivo de venta: ${self.precio_objetivo_venta:.2f}")
"""
    def vender(self):
            if not self.transacciones:
                self.log("ℹ️ No hay BTC disponible para vender.")
                return
            transacciones_vendidas = []
            for transaccion in self.transacciones:
                if self.precio_actual >= transaccion["venta_obj"]:
                    self.btc_vendido = transaccion["btc"]
                    usdt_obtenido = self.btc_vendido * self.precio_actual
                    self.usdt += usdt_obtenido
                    self.btc -= self.btc_vendido 
                    self.precio_ult_venta = self.precio_actual
                    self.actualizar_balance()

                    transaccion["ejecutado"] = True  # Marcar como ejecutado    
                    self.precios_ventas.append({
                        "venta": self.precio_actual,
                        "btc_vendido": transaccion["btc"],
                        "ganancia": transaccion["btc"] * self.precio_actual,
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    transacciones_vendidas.append(transaccion)

                    self.log(f"✅ Venta realizada: {usdt_obtenido:.2f} USDT a ${self.precio_actual:.2f}")
                    self.log(f"📤 BTC vendido: {self.btc_vendido:.6f}")
            
            # Eliminar las transacciones vendidas para evitar superposición
            for transaccion in transacciones_vendidas:
                self.transacciones.remove(transaccion)
                                                   
                print(f"\n\033[92mVenta realizada:\033[0m {usdt_obtenido:.2f} Usdt obtenidos a ${self.precio_actual:.2f}")
                print("BTC vendido: ", self.btc_comprado)

            if not transacciones_vendidas:
                self.log("⌛ Esperando precio objetivo para venta...")
               

    def parametro_compra_A(self):
        #Compra con referencia a la ultima compra
        if self.varCompra <= -self.porc_por_compra and self.usdt >= self.fixed_buyer:      
            self.comprar()

    def parametro_compra_B(self):
        #Compra con referencia a la ultima venta
        if self.varVenta <= -self.porc_por_compra and self.usdt >= self.fixed_buyer:
            self.comprar()        


        """# Si el precio ha bajado más del doble del porcentaje de venta, comprar 
        if self.usdt >= self.fixed_buyer:
            if self.varVenta <= -2 * self.porc_por_venta:
                print(f"\n\033[96mCondición de sobreventa cumplida: ({self.varVenta:.3f})\033[0m")
                self.comprar()

        # Luego evaluar la compra por bajada normal
        el    

#  Condición 1: Compra si el precio sube más del doble del porcentaje de compra y no ha comprado recientemente
        elif self.varCompra >= 2 * self.porc_por_compra and self.usdt >= self.fixed_buyer:
            if not self.transacciones or self.transacciones[-1]["compra"] < self.precio_actual:
                print(f"\n\033[96mCondición de tendencia alcista cumplida: ({self.varCompra:.3f})\033[0m")
                self.comprar()"""
    
                          
    def realizar_primera_compra(self):
        self.log("🚀 Realizando primera compra")
        self.usdt -= self.fixed_buyer 
        self.btc_usdt += ((1/self.precio_actual) * self.fixed_buyer) * self.precio_actual
        self.precios_compras.append(self.precio_ult_comp)
        self.precio_ult_comp = self.precio_actual
        self.btc_comprado = (1/self.precio_actual) * self.fixed_buyer
        self.btc = self.btc_comprado
        self.precio_objetivo_venta = self.precio_actual * (1 + self.porc_por_venta / 100)
        self.transacciones.append({"compra": self.precio_actual, "venta_obj": self.precio_objetivo_venta, "btc": self.btc_comprado})

        self.log(f"✅ Precio de ingreso registrado: {self.precio_ingreso:.2f} USDT")
        self.log(f"🪙 BTC comprado: {self.btc_comprado:.6f}")
        self.log(f"🎯 Objetivo de venta: {self.precio_objetivo_venta:.2f} USDT")


        """print("Precios de compra: USDT: $", self.precios_compras) 
        print("\n\033[93mPrecio de ingreso registrado:\033[0m", self.precio_ingreso)       
        print("BTC comprado: ", self.btc_comprado) 
        print("BTC comprado representado en USDT: $", self.fixed_buyer)  
        print(f"Precio objetivo de siguiente venta: ${self.precio_objetivo_venta:.3f}")"""  

    """def estado(self):
        print("\033[93mFondos insuficientes para comprar.\033[0m") 
        print(f"\n\033[96mCompra realizada.\033[0m") 
        print(f"\033[91mError obteniendo el precio: {e}\033[0m")
        print("\n\033[94mNo hay BTC disponible para vender.\033[0m") 
        print(f"\n\033[92mVenta realizada:\033[0m")  
        print("\n\033[94m... PRIMERA COMPRA ...\n\033[0m")
        print("\033[93mBot iniciado\033[0m") 
        print("\033[96mEsperando precio objetivo.\033[0m")    
        print("\033[91mAdvertencia: No se puede operar sin datos de precios.\033[0m") """                   
                
    def iniciar(self):
        self.running = True
        self.log("🟡 Bot iniciado.")
        self.realizar_primera_compra()
        self.log("🔄 Iniciando bucle...")
        self.log(f"📌 Monto fijo por compra: {self.fixed_buyer:.2f} USDT")
        
        while self.running:
            self.precio_actual = self.get_precio_actual()
            if self.precio_actual == 0:
                self.log("⚠️ No se puede operar sin datos de precios.")
                time.sleep(3)
                continue
            self.varCompra = self.varpor_compra(self.precio_ult_comp, self.precio_actual) 
            self.varVenta = self.varpor_venta (self.precio_ult_venta, self.precio_actual) 
            self.actualizar_balance()
            self.parametro_compra_desde_compra = self.parametro_compra_A()
            self.parametro_compra_desde_venta = self.parametro_compra_B()
            self.btc_usdt = self.btc * self.precio_actual
            self.var_inicio =self.varpor_ingreso()
            
            self.log("- - - - - - - - - -")
            self.log(f"💰 Última compra: {self.precio_ult_comp:.2f} USDT")
            self.log(f"🎯 Objetivo venta: {self.precio_objetivo_venta:.2f} USDT")
            
            
            if self.btc == 0:
                self.log("ℹ️ No hay BTC disponible.")
            else:
                self.vender()
            time.sleep(3)

    def detener(self):
        self.running = False
        self.log("🔴 Bot detenido.")

if __name__ == "__main__":
    bot = TradingBot()
    bot.iniciar()
    





