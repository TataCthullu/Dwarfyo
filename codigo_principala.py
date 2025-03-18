#import threading
import time
import ccxt
#import json

"""Azul (\033[94m) para información general.
Amarillo (\033[93m) para valores clave como precios de ingreso.
Verde (\033[92m) para operaciones exitosas como compras y ventas.
Rojo (\033[91m) para advertencias y errores.
Cian (\033[96m) para detalles adicionales."""

class TradingBot:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.usdt = 10000
        self.btc = 0
        self.btc_usdt = 0
        self.btc_comprado = 0
        self.precio_actual = self.get_precio_actual()
        self.precio_ult_venta = 0
        self.porc_por_compra = 0.007
        self.porc_por_venta = 0.007
        self.porc_inv_por_compra = 10
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
        print("\n\033[93mPrecio de ingreso registrado:\033[0m ", self.precio_ingreso)
        print("\nCantidad fija a invertir por compra: ", self.fixed_buyer)

    def get_precio_actual(self):
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            return ticker['last']
        except Exception as e:
            print(f"Error obteniendo el precio: {e}")
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

    def cant_inv(self):
        return (self.usdt * self.porc_inv_por_compra) / 100

    def comprar(self):
            if self.usdt < self.fixed_buyer:
                print("Fondos insuficientes para comprar.")
                return
            else:
                print(f"\n\033[96mEL PORCENTAJE HABILITA A COMPRAR.\033[0m ({self.varVenta:.3f})")
                self.usdt -= self.fixed_buyer
                self.btc_usdt += ((1/self.precio_actual) * self.fixed_buyer) * self.precio_actual
                self.precio_ult_comp = self.precio_actual
                self.precios_compras.append(self.precio_ult_comp)
                self.btc_comprado = (1/self.precio_actual) * self.fixed_buyer
                self.precio_objetivo_venta = self.precio_actual * (1 + self.porc_por_venta / 100)
                self.btc += self.btc_comprado 
                self.transacciones.append({"compra": self.precio_actual, "venta_obj": self.precio_objetivo_venta, "btc": self.btc_comprado})
                
                self.actualizar_balance()
                
                print("Precios de compra: USDT: $", self.precios_compras)  
                print("BTC comprado: ", (1/self.precio_actual) * self.fixed_buyer) 
                print("BTC comprado representado en USDT: $", self.fixed_buyer)  
                print(f"Objetivo de venta: ${self.precio_objetivo_venta:.2f} USDT")

    def vender(self):
            if not self.transacciones:
                print("\nNo hay BTC disponible para vender.")
                return
            transacciones_vendidas = []
            for transaccion in self.transacciones:
                if self.precio_actual >= transaccion["venta_obj"]:
                    self.btc_vendido = transaccion["btc"]
                    usdt_obtenido = self.btc_vendido * self.precio_actual
                    self.usdt += usdt_obtenido
                    self.btc -= self.btc_vendido
                    self.precios_ventas.append(self.precio_actual) 
                    self.precio_ult_venta = self.precio_actual
                    self.actualizar_balance()
                    transacciones_vendidas.append(transaccion)
                            
                    print(f"\n\033[92mVenta realizada:\033[0m {usdt_obtenido:.2f} USDT obtenidos a {self.precio_actual:.2f} USDT")
                    print("Precios de venta: USDT$", self.precios_ventas)
                    print("BTC vendido: ", self.btc_comprado)
                    
            # Eliminar transacciones que ya se vendieron
            for transaccion in transacciones_vendidas:
                self.transacciones.remove(transaccion)

            if not transacciones_vendidas:
                print("Esperando precio objetivo.")
            else:
                print(f"Precios de venta registrados: {self.precios_ventas}")    

    def parametro_rango(self):
        if (self.varVenta <= -self.porc_por_compra) and self.usdt >= self.fixed_buyer:
            self.comprar()

    def parametro_tendencial(self):
        if self.varCompra <= -self.porc_por_compra and self.usdt >= self.fixed_buyer:      
            self.comprar()
                          
                                  
            
    def iniciar(self):
        self.running = True
        print("\n... PRIMERA COMPRA ...\n")
        self.usdt -= self.fixed_buyer 
        self.btc_usdt += (((1/self.precio_actual) * (self.fixed_buyer)) * self.precio_actual)
        self.precios_compras.append(self.precio_ult_comp)
        self.precio_ult_comp = self.precio_actual
        self.btc_comprado = (1/self.precio_actual) * (self.fixed_buyer)
        self.btc = self.btc_comprado
        self.precio_objetivo_venta = self.precio_actual * (1 + self.porc_por_venta / 100)
        self.transacciones.append({"compra": self.precio_actual, "venta_obj": self.precio_objetivo_venta, "btc": self.btc_comprado})
        #print(json.dumps(self.transacciones, indent=4))

        
        #PRINTS
        print("Precios de compra: USDT: $", self.precios_compras)        
        print("BTC comprado: ",self.btc_comprado) 
        print("BTC comprado representado en USDT: $", (self.fixed_buyer))  
        print(f"Precio objetivo de siguiente venta: ${self.precio_objetivo_venta:.3f}")       
        
        print("\n... INICIANDO BUCLE ...\n")

        while self.running:
            self.precio_actual = self.get_precio_actual()
            if self.precio_actual == 0:
                print("Advertencia: No se puede operar sin datos de precios.")
                time.sleep(3)
                continue
            self.varCompra = self.varpor_compra(self.precio_ult_comp, self.precio_actual) 
            self.varVenta = self.varpor_venta (self.precio_ult_venta, self.precio_actual) 
            self.actualizar_balance()
            
            
            print("\n- - - - - - - - - - - ")
            print("Precio de la ultima compra: ", self.precio_ult_comp)
            print(f"Porcentaje de variación del precio desde ultima compra, contra el actual: ({self.varCompra:.3f})")
            print(f"Porcentaje de variación del precio desde ultima venta, contra el actual: ({self.varVenta:.3f})")
            #print(f"EL PORCENTAJE NO ES SUFICIENTE PARA TRADEAR.")
            print("\n---- BALANCE ACTUAL ----")      
            print(f"Btc + Usdt: ${self.usdt_mas_btc:.2f} Usdt")
            print("Usdt: $", self.usdt)
            print("Precio actual:" ,self.precio_actual)
            print(f"Precio objetivo de siguiente venta: ${self.precio_objetivo_venta:.3f}")
            
            if self.btc > 0:
                print(f"Btc: {self.btc:.4f} (En usdt: ${self.btc * self.precio_actual:.2f})")
            else:
                 print("Btc: 0")
            
            if self.precio_ult_venta > 0:
                self.parametro_rango()
            else:
                self.parametro_tendencial()

            self.vender()
            
            time.sleep(5)

    def detener(self):
        self.running = False

if __name__ == "__main__":
    bot = TradingBot()
    bot.iniciar()





