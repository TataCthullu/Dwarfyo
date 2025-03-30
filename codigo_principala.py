import time


import ccxt
import pygame
pygame.mixer.init()
#import datetime
#import json


def reproducir_sonido(ruta):
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play()

"""Azul (\033[94m) para información general.
Amarillo (\033[93m) para valores clave como precios de ingreso.
Verde (\033[92m) para operaciones exitosas como compras y ventas.
Rojo (\033[91m) para advertencias y errores.
Cian (\033[96m) para detalles adicionales."""

class TradingBot:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.usdt = 5000
        self.btc = 0        
        self.btc_comprado = 0
        self.precio_actual = self.get_precio_actual()
        self.btc_usdt = 0
        self.parametro_compra_desde_compra = None
        self.parametro_compra_desde_venta = None
        self.parametro_venta_fantasma = None
        self.precio_ult_venta = 0
        self.porc_desde_compra = 0.5
        self.porc_desde_venta = 0.5
        self.porc_inv_por_compra = 5
        self.fixed_buyer = self.cant_inv()
        self.running = False
        self.precio_ult_comp = self.precio_actual
        self.usdt_mas_btc = 0
        self.precios_compras = []
        self.precios_ventas = []
        self.ventas_fantasma = []
        self.compras_fantasma = []
        #self.compras_fantasma_E = []
        self.transacciones = []
        self.kant_usdt_vendido = 0       
        self.varCompra = 0
        self.varVenta = 0       
        self.btc_vendido = 0
        self.precio_objetivo_venta = 0
        self.precio_ingreso = self.get_precio_actual()
        self.var_inicio = 0
        self.log_fn = None
        self.usdt_obtenido = 0
        self.contador_compras_fantasma = 0
        self.contador_ventas_fantasma = 0
        #self.parametro_compra_fantasma = 0
        self.total_ganancia = 0
        self.ganancia_neta = 0
        self.reportado_trabajando = False 
        self.porc_profit_x_venta = 0.6

    def log(self, mensaje):
        if self.log_fn:
            self.log_fn(mensaje)    
               
    def get_precio_actual(self):
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            return ticker['last']
        except Exception as e:
            self.log(f"\n❌ Error obteniendo el precio: {e}\n")
            return None
    
    def actualizar_balance(self):
        self.btc_usdt = self.btc * self.precio_actual
        self.usdt_mas_btc = self.usdt + self.btc_usdt


    #Variacion de precio con respecto a ultima compra
    def varpor_compra(self, precio_ult_comp, precio_act_btc):
        if precio_ult_comp is None or precio_act_btc is None:
            return 0
        return ((precio_act_btc - precio_ult_comp) / precio_ult_comp) * 100

    #Variacion de precio con respecto a ultima venta
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
                reproducir_sonido("Sounds/soundsinusdt.wav")
                self.log("\n⚠️ Usdt insuficiente para comprar.\n")
                return
            self.usdt -= self.fixed_buyer             
            self.precio_ult_comp = self.precio_actual
            self.precios_compras.append(self.precio_ult_comp)
            self.btc_comprado = (1/self.precio_actual) * self.fixed_buyer
            self.precio_objetivo_venta = self.precio_actual * (1 + self.porc_profit_x_venta / 100)
            self.btc += self.btc_comprado 
            
            self.transacciones.append({
                    "compra": self.precio_actual,                  
                    "venta_obj": self.precio_objetivo_venta,
                    "btc": self.btc_comprado,
                    "ejecutado": False
                    #"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
            self.actualizar_balance()
            self.log("\n- - - - - - - - - -")
            self.log("\n✅ Compra realizada.")
            self.log(f"\n📉 Precio de compra: $ {self.precio_actual:.6f}")
            #self.log(f"🕒 Hora: {self.transacciones['timestamp']}")
            self.log(f"\n🪙 BTC comprado: ₿ {self.btc_comprado:.6f}")
            self.log(f"\n🎯 Objetivo de venta: $ {self.precio_objetivo_venta:.2f}")
            self.log("\n- - - - - - - - - -\n")           
            reproducir_sonido("Sounds/soundcompra.wav")
            self.reportado_trabajando = False
    
         

    def vender(self):
        transacciones_vendidas = []

        for transaccion in self.transacciones:
            if self.btc < transaccion["btc"]:
                continue  # Evita vender más BTC del disponible
            
            if self.precio_actual >= transaccion["venta_obj"]:
                btc_vender = transaccion["btc"]
                usdt_obtenido = btc_vender * self.precio_actual               
                #timestamp = transaccion["timestamp"]               
                self.usdt += usdt_obtenido
                self.btc -= btc_vender
                self.precio_ult_venta = self.precio_actual  
                invertido_usdt = transaccion.get("invertido_usdt", self.fixed_buyer)
                self.ganancia_neta = usdt_obtenido - invertido_usdt
                self.total_ganancia += self.ganancia_neta              
                self.actualizar_balance()
                transaccion["ejecutado"] = True
                self.precios_ventas.append({
                    "venta": self.precio_actual,
                    "btc_vendido": btc_vender,
                    "ganancia": self.ganancia_neta,
                    "inverstido_usdt": invertido_usdt,
                    #"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                transacciones_vendidas.append(transaccion)
                self.log("\n- - - - - - - - - -")
                self.log(f"\n✅ Venta realizada.")
                #self.log(f"🕒 Compra original: {timestamp}")
                self.log(f"\n📈 Precio de venta: $ {self.precio_actual:.2f}")
                self.log(f"\n💰 Usdt obtenido: $ {usdt_obtenido:.4f}")
                self.log(f"\n📤 Btc vendido: ₿ {btc_vender:.6f}")
                self.log(f"\n💹 Ganancia de esta operación: $ {self.ganancia_neta:.8f}")
                self.log(f"\n💹 Ganancia total acumulada: $ {self.total_ganancia:.8f}")
                self.log("\n- - - - - - - - - -\n")
                reproducir_sonido("Sounds/soundventa.wav")
                self.reportado_trabajando = False

        # Eliminar las vendidas después del bucle
        for trans in transacciones_vendidas:
            self.transacciones.remove(trans)


    def parametro_compra_A(self):
        #Compra con referencia a la ultima compra
        if self.varCompra <= -self.porc_desde_compra:
            if self.usdt >= self.fixed_buyer:      
                self.comprar()              
            else:               
                self.log("\n⚠️ Intento de compra: parámetro (A). Fondos insuficientes\n")                 
                self.reportado_trabajando = False
                return 
              
              
    def parametro_compra_B(self):
        #Compra con referencia a la ultima venta
        if self.varVenta <= -self.porc_desde_compra:
            if self.usdt >= self.fixed_buyer:      
                self.comprar()
            else:               
                self.log("\n⚠️ Intento de compra: parámetro (B). Fondos insuficientes\n")                 
                self.reportado_trabajando = False 
                return      
        

    def parametro_compra_C(self):
        if self.btc < self.btc_comprado and self.varVenta >= self.porc_desde_venta:
            reproducir_sonido("Sounds/ghostventab.wav")
            self.precio_ult_venta = self.precio_actual
            self.ventas_fantasma.append(self.precio_actual)
            self.contador_ventas_fantasma += 1
            self.log("\n📌 Parámetro C: Sin BTC para vender, nueva venta fantasma registrada.")
            self.reportado_trabajando = False
            
          
    
    def parametro_compra_D(self):
        if self.usdt < self.fixed_buyer and self.varCompra <= self.porc_desde_compra:
            reproducir_sonido("Sounds/ghostcomprad.wav")
            #self.precio_ult_comp = self.precio_actual
            self.compras_fantasma.append(self.precio_actual)
            self.contador_compras_fantasma += 1
            self.log("\n📌 Parámetro D: Sin Usdt para comprar, nueva compra fantasma registrada.")
            
            self.reportado_trabajando = False
            

    """def parametro_compra_E(self):
        if self.precio_actual == self.precio_ult_comp:
            
            self.compras_fantasma_E.append(self.precio_actual)
            self.log("\n📌 Parámetro E: Precio no varió desde última compra. Actualizando con compra fantasma tipo E.")
            self.sin_evento_counter = 0  """      
                          
    def realizar_primera_compra(self):
        self.log(f"\n🚀 Realizando primera compra a: $ {self.precio_actual:.6f}")
        self.usdt -= self.fixed_buyer 
        self.actualizar_balance()

        self.precios_compras.append(self.precio_ult_comp)
        self.precio_ult_comp = self.precio_actual
        self.btc_comprado = (1/self.precio_actual) * self.fixed_buyer
        self.btc = self.btc_comprado
        self.precio_objetivo_venta = self.precio_actual * (1 + self.porc_desde_venta / 100)
        self.transacciones.append({"compra": self.precio_actual, "venta_obj": self.precio_objetivo_venta, "btc": self.btc_comprado})
        self.log(f"\n🪙 Btc comprado: ₿ {self.btc_comprado:.6f}\n")
        
        
        #self.log(f"\n🎯 Objetivo de venta: $ {self.precio_objetivo_venta:.2f}")
         
                
    def iniciar(self):
        self.running = True
        self.log("\n🟡 Bot iniciado.")
        self.realizar_primera_compra()
        self.log(f"\n✅ Precio de ingreso registrado: {self.precio_ingreso:.4f} USDT")
        self.log("\n🔄 Iniciando bucle...\n")
        
             
        while self.running:
            self.precio_actual = self.get_precio_actual()
            if not self.precio_actual:
                self.log("\n⚠️ No se puede operar sin datos de precios.\n")
                
                continue
            
            self.varCompra = self.varpor_compra(self.precio_ult_comp, self.precio_actual) 
            self.varVenta = self.varpor_venta (self.precio_ult_venta, self.precio_actual) 
            self.actualizar_balance()
            self.parametro_compra_desde_compra = self.parametro_compra_A()
            self.parametro_compra_desde_venta = self.parametro_compra_B()
            self.parametro_venta_fantasma = self.parametro_compra_C()
            self.parametro_compra_fantasma = self.parametro_compra_D()
            #self.parametro_compra_fantasma_E = self.parametro_compra_E()
            self.var_inicio = self.varpor_ingreso()
            

            if self.reportado_trabajando == False:    
                self.log("\n- - - - - - - - - -")
                self.log("\n🟡 Bot Trabajando...")
                self.log(f"\n💰 Última compra a: $ {self.precio_ult_comp:.4f}")
                self.log(f"\n🎯 Objetivo de venta: $ {self.precio_objetivo_venta:.4f}")
                self.log(f"\n🎯 Precio Actual: $ {self.precio_actual:.4f}")
                self.log("\n- - - - - - - - - -\n")  
                self.reportado_trabajando = True             
                
            if self.btc < self.btc_comprado:
                
                    self.log("\nℹ️ Sin Btc para vender\n")
                    self.reportado_trabajando = False
            else:               
                self.vender()

            time.sleep(3)

    def detener(self):
        self.running = False
        self.log("\n🔴 Bot detenido.\n")

if __name__ == "__main__":
    bot = TradingBot()
    bot.iniciar()
    





