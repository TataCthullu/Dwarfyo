#import threading
import time
import ccxt

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
        
        print("Cantidad fija a invertir por compra: ", self.fixed_buyer)

    def get_precio_actual(self):
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            return ticker['last']
        except Exception as e:
            print(f"Error obteniendo el precio: {e}")
            return
    
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
         
            print(f"EL PORCENTAJE HABILITA A COMPRAR. ({self.varVenta:.3f})")
            self.usdt -= self.fixed_buyer
            self.btc_usdt += ((1/self.precio_actual) * self.fixed_buyer) * self.precio_actual
            self.precio_ult_comp = self.precio_actual
            self.precios_compras.append(self.precio_ult_comp)
            self.btc_comprado = (1/self.precio_actual) * self.fixed_buyer
            self.btc += self.btc_comprado 
            self.usdt_mas_btc = self.usdt + (self.btc * self.precio_actual)
            
            
            print("Precios de compra: USDT: $", self.precios_compras)
                    
            print("BTC comprado: ", (1/self.precio_actual) * self.fixed_buyer) 
            print("BTC comprado representado en USDT: $", self.fixed_buyer)  

    def vender(self):
         
            self.precio_ult_venta = self.precio_actual
            print(f"EL PORCENTAJE HABILITA A VENDER. ({self.varCompra:.3f})")
            self.kant_usdt_vendido = self.btc_comprado * self.precio_actual
            #pdiff_ult = self.kant_usdt_vendido - self.fixed_buyer
            self.usdt += self.kant_usdt_vendido
            self.btc -= self.btc_comprado
            self.btc_usdt -= ((1/self.precio_ult_comp) * self.fixed_buyer) * self.precio_actual
            self.precio_ult_comp = self.precio_actual
            self.precios_ventas.append(self.precio_ult_venta)
            self.usdt_mas_btc = self.usdt + (self.btc * self.precio_actual)
            
            #print("Profit diferencial de la ultima venta: ", pdiff_ult) 
            #print("Profit diferencial total: ", pdiff)
           
            print("Precios de venta: USDT$", self.precios_ventas)
              
            print("BTC vendido: ", self.btc_comprado)   
            print("BTC vendido representado en USDT: $", self.kant_usdt_vendido)                            
            
    def iniciar(self):
        self.running = True
        print("\n... PRIMERA COMPRA ...\n")
        self.usdt -= self.fixed_buyer 
        self.btc_usdt += (((1/self.precio_actual) * (self.fixed_buyer)) * self.precio_actual)
        self.precios_compras.append(self.precio_ult_comp)
        self.precio_ult_comp = self.precio_actual
        self.btc_comprado = (1/self.precio_actual) * (self.fixed_buyer)
        self.btc = self.btc_comprado
        self.usdt_mas_btc = self.usdt + (self.btc * self.precio_actual)
        #PRINTS
        
        print("Precios de compra: USDT: $", self.precios_compras)        
        print("BTC comprado: ",self.btc_comprado) 
        print("BTC comprado representado en USDT: $", (self.fixed_buyer))         

        print("\n... INICIANDO BUCLE ...\n")

        while self.running:
            self.precio_actual = self.get_precio_actual()
            self.varCompra = self.varpor_compra(self.precio_ult_comp, self.precio_actual) 
            self.varVenta = self.varpor_venta (self.precio_ult_venta, self.precio_actual) 
            self.usdt_mas_btc = self.usdt + (self.btc * self.precio_actual)
            
            print("\n- - - - - - - - - - - ")
            print("Valor BTC actual en UDST: ", self.precio_actual)
            print("Valor de la ultima compra en USDT: ", self.precio_ult_comp)
            print(f"Porcentaje de variación del precio desde ultima compra, contra el actual: ({self.varCompra:.3f})")
            print(f"Porcentaje de variación del precio desde ultima venta, contra el actual: ({self.varVenta:.3f})")
            #print(f"EL PORCENTAJE NO ES SUFICIENTE PARA TRADEAR.")
            print("\n---- BALANCE ACTUAL ----")      
            print(f"- USDT: ${self.usdt:.2f}")
            #print(f"- Profit neto: ${pdiff:.2f}")
            print(f"- BTC: {self.btc} (USDT ${self.btc * self.precio_actual:.2f})")
            print(f"- BTC + USDT, en USDT: ${self.usdt_mas_btc:.2f}")
            
            if self.precio_ult_venta > 0:

                if (self.varVenta <= -self.porc_por_compra) and self.usdt >= self.fixed_buyer:
                    self.comprar()
                
                if self.varCompra >= self.porc_por_venta and self.btc >= self.btc_comprado:      
                    self.vender()

            else:

                if self.varCompra >= self.porc_por_venta and self.btc >= self.btc_comprado:
                     self.vender()
                
                if self.varCompra <= -self.porc_por_compra and self.usdt >= self.fixed_buyer:      
                    self.comprar()
                 
            time.sleep(3)
    def detener(self):
        self.running = False

if __name__ == "__main__":
    bot = TradingBot()
    bot.iniciar()



