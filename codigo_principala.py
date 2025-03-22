import time
import ccxt
import datetime

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
        self.btc_usdt = 0
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
        self.usdt_obtenido = 0
        

    def log(self, mensaje):
        if self.log_fn:
            self.log_fn(mensaje)    
               
    def get_precio_actual(self):
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            return ticker['last']
        except Exception as e:
            self.log(f"\n❌ Error obteniendo el precio: {e}")
            return None
    
    def actualizar_balance(self):
        self.usdt_mas_btc = self.usdt + (self.btc * self.precio_actual)

    #Variacion de precio con respecto a ultima compra
    def varpor_compra(self, precio_ult_comp, precio_act_btc):
        if precio_ult_comp is None or precio_act_btc is None:
            return 0
        return ((precio_act_btc - precio_ult_comp) / precio_ult_comp) * 100


    def varpor_venta(self, precio_ult_venta, precio_act_btc):
        if precio_ult_venta == 0 or precio_act_btc is None:
            return 0
        return ((precio_act_btc - precio_ult_venta) / precio_ult_venta) * 100
    
    def varpor_ingreso(self):
        if self.precio_ingreso == 0 or self.precio_actual is None:
            return 0
        return ((self.precio_actual - self.precio_ingreso) / self.precio_ingreso) * 100

    def cant_inv(self):
        return (self.usdt * self.porc_inv_por_compra) / 100

    def comprar(self):
            if self.usdt < self.fixed_buyer:
                self.log("\n⚠️ Usdt insuficiente para comprar.")
                return
            
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
            self.log("\n✅ Compra realizada.")
            self.log(f"\n📉 Precio de compra: $ {self.precio_actual:.6f}")
            self.log(f"\n🪙 BTC comprado: ₿ {self.btc_comprado:.6f}")
            self.log(f"\n🎯 Objetivo de venta: $ {self.precio_objetivo_venta:.2f}")           

    def vender(self):
            if not self.transacciones:
                self.log("\nℹ️ No hay BTC disponible para vender.")
                return
            transacciones_vendidas = []
            for transaccion in self.transacciones:
                if self.precio_actual >= transaccion["venta_obj"]:
                    self.btc_vendido = transaccion["btc"]
                    self.usdt_obtenido = self.btc_vendido * self.precio_actual
                    self.usdt += self.usdt_obtenido
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

                    self.log(f"\n✅ Venta realizada: $ {self.usdt_obtenido:.2f} a $ {self.precio_actual:.2f}")
                    self.log(f"\n📤 Btc vendido: ₿ {self.btc_vendido:.6f}")

    def parametro_compra_A(self):
        #Compra con referencia a la ultima compra
        if self.varCompra <= -self.porc_por_compra:
            if self.usdt >= self.fixed_buyer():      
                self.comprar()
            else:
                self.log("⚠️ Fondos insuficientes para comprar (A).") 
                return   

    def parametro_compra_B(self):
        #Compra con referencia a la ultima venta
        if self.varVenta <= -self.porc_por_compra:
            if self.usdt >= self.fixed_buyer():      
                self.comprar()
            else:
                self.log("⚠️ Fondos insuficientes para comprar (A).")  
                return      


        """

#  Condición 1: Compra si el precio sube más del doble del porcentaje de compra y no ha comprado recientemente
        elif self.varCompra >= 2 * self.porc_por_compra and self.usdt >= self.fixed_buyer:
            if not self.transacciones or self.transacciones[-1]["compra"] < self.precio_actual:
                print(f"\n\033[96mCondición de tendencia alcista cumplida: ({self.varCompra:.3f})\033[0m")
                self.comprar()"""
    
                          
    def realizar_primera_compra(self):
        self.log(f"\n🚀 Realizando primera compra a: $ {self.precio_actual:.6f}")
        self.usdt -= self.fixed_buyer 
        self.btc_usdt += ((1/self.precio_actual) * self.fixed_buyer) * self.precio_actual
        self.precios_compras.append(self.precio_ult_comp)
        self.precio_ult_comp = self.precio_actual
        self.btc_comprado = (1/self.precio_actual) * self.fixed_buyer
        self.btc = self.btc_comprado
        self.precio_objetivo_venta = self.precio_actual * (1 + self.porc_por_venta / 100)
        self.transacciones.append({"compra": self.precio_actual, "venta_obj": self.precio_objetivo_venta, "btc": self.btc_comprado})
       
        self.log(f"\n🪙 Btc comprado: ₿ {self.btc_comprado:.6f}")
        self.log(f"\nBtc comprado representado en Usdt: $ {self.fixed_buyer:.2f}")
        self.log(f"\n🎯 Objetivo de venta: $ {self.precio_objetivo_venta:.2f}")
         
                
    def iniciar(self):
        self.running = True
        self.log("\n🟡 Bot iniciado.")
        self.realizar_primera_compra()
        self.log(f"\n✅ Precio de ingreso registrado: {self.precio_ingreso:.6f} USDT")
        self.log("\n🔄 Iniciando bucle...")
              
        while self.running:
            self.precio_actual = self.get_precio_actual()
            if not self.precio_actual:
                self.log("\n⚠️ No se puede operar sin datos de precios.")
                time.sleep(3)
                continue
            self.varCompra = self.varpor_compra(self.precio_ult_comp, self.precio_actual) 
            self.varVenta = self.varpor_venta (self.precio_ult_venta, self.precio_actual) 
            self.actualizar_balance()
            self.parametro_compra_desde_compra = self.parametro_compra_A()
            self.parametro_compra_desde_venta = self.parametro_compra_B()
            self.btc_usdt = self.btc * self.precio_actual
            self.var_inicio =self.varpor_ingreso()
            self.log("\n- - - - - - - - - -")
            self.log("\n🟡 Bot Trabajando...")
            self.log(f"\n💰 Última compra a: $ {self.precio_ult_comp:.4f}")
            self.log(f"\n🎯 Objetivo de venta: $ {self.precio_objetivo_venta:.4f}")
            self.log(f"\n🎯 Precio Actual: $ {self.precio_actual:.4f}")
            
            
            if self.btc == 0:
                self.log("\nℹ️No hay Btc disponible para vender")
            else:               
                self.vender()
            time.sleep(3)

    def detener(self):
        self.running = False
        self.log("\n🔴 Bot detenido.")

if __name__ == "__main__":
    bot = TradingBot()
    bot.iniciar()
    





