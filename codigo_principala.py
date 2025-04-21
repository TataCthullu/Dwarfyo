import ccxt
from utils import reproducir_sonido
import datetime

"""Azul (\033[94m) para información general.
Amarillo (\033[93m) para valores clave como precios de ingreso.
Verde (\033[92m) para operaciones exitosas como compras y ventas.
Rojo (\033[91m) para advertencias y errores.
Cian (\033[96m) para detalles adicionales."""

class TradingBot:
    def __init__(self):
        self.exchange = ccxt.binance()
        self.log_fn = None
        self.usdt = 5000
        self.btc = 0        
        self.btc_comprado = 0
        self.precio_actual = self.get_precio_actual()
        self.btc_usdt = 0
        self.parametro_compra_desde_compra = None
        self.parametro_compra_desde_venta = None
        self.parametro_venta_fantasma = None
        self.precio_ult_venta = None
        self.porc_desde_compra = 0.5
        self.porc_desde_venta = 0.5
        self.porc_inv_por_compra = 10
        self.fixed_buyer = self.cant_inv()
        self.running = False
        self.valores_iniciales = {}
        self.precio_ult_comp = None
        self.usdt_mas_btc = 0
        self.precios_compras = []
        self.precios_ventas = []
        self.ventas_fantasma = []
        self.compras_fantasma = []
        self.transacciones = []
        self.kant_usdt_vendido = 0       
        self.varCompra = 0
        self.varVenta = 0       
        self.btc_vendido = 0
        self.precio_objetivo_venta = 0
        self.precio_ingreso = None
        self.var_inicio = 0
        self.log_fn = None
        self.usdt_obtenido = 0
        self.contador_compras_fantasma = 0
        self.contador_ventas_fantasma = 0
        self.parametro_compra_fantasma = None
        self.total_ganancia = 0
        self.ganancia_neta = 0
        self.reportado_trabajando = False 
        self.porc_profit_x_venta = 0.5
        self.contador_compras_reales = 0
        self.contador_ventas_reales = 0
        self.param_b_enabled = True  
        #self.bot_iniciado = False
        

    def log(self, mensaje):
        if self.log_fn:
            self.log_fn(mensaje)  

    def set_valores_iniciales(self, valores):
        self.valores_iniciales = valores  # un dict con los datos iniciales
                        
    def get_precio_actual(self):
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            return ticker['last']
        except Exception as e:
            self.log(f"❌ Error obteniendo el precio: {e}")
            self.log("- - - - - - - - - -")
            self.reportado_trabajando = False 
            reproducir_sonido("Sounds/error.wav")
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
        if precio_ult_venta is None or precio_act_btc is None:
            return 0
        return ((precio_act_btc - precio_ult_venta) / precio_ult_venta) * 100
    
    def varpor_ingreso(self):
        if self.precio_ingreso is None or self.precio_actual is None:
            return 0
        return ((self.precio_actual - self.precio_ingreso) / self.precio_ingreso) * 100

        

    def cant_inv(self):
        return (self.usdt * self.porc_inv_por_compra) / 100

    def comprar(self):
            if self.usdt < self.fixed_buyer:
                self.log("⚠️ Usdt insuficiente para comprar.")
                return
            
            self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.usdt -= self.fixed_buyer             
            self.precio_ult_comp = self.precio_actual
            self.precios_compras.append(self.precio_ult_comp)
            self.btc_comprado = (1/self.precio_actual) * self.fixed_buyer
            self.precio_objetivo_venta = self.precio_ult_comp * (1 + self.porc_profit_x_venta / 100)
            self.btc += self.btc_comprado
            self.contador_compras_reales += 1 
            
            self.transacciones.append({
                    "compra": self.precio_ult_comp,                  
                    "venta_obj": self.precio_objetivo_venta,
                    "btc": self.btc_comprado,
                    "invertido_usdt": self.fixed_buyer,
                    "ejecutado": False,
                    "numcompra": self.contador_compras_reales,
                    "timestamp": self.timestamp
                })
                            
            self.actualizar_balance()            
            self.log("✅ Compra realizada.")
            self.log(f"📉 Precio de compra: $ {self.precio_actual:.6f}")
            self.log(f"🪙 Btc comprado: ₿ {self.btc_comprado:.6f}")
            self.log(f"🪙 Compra numero: {self.contador_compras_reales}")
            self.log(f"🎯 Objetivo de venta: $ {self.precio_objetivo_venta:.2f}")
            self.log("- - - - - - - - - -")           
            reproducir_sonido("Sounds/soundcompra.wav")            
            self.reportado_trabajando = False

    def parametro_compra_A(self):
        #Compra con referencia a la ultima compra
        if self.varCompra <= -self.porc_desde_compra:
            if self.usdt >= self.fixed_buyer:  
                   
                self.log("🔵 [Parametro A].") 
                
                self.comprar()
                self.precio_ult_comp = self.precio_actual                                
            else:                               
                self.compras_fantasma.append(self.precio_actual)
                self.contador_compras_fantasma += 1
                
                self.log(f"📌(A) Sin Usdt para comprar, nueva compra fantasma registrada a {self.precio_actual:.2f}, Id: {self.contador_compras_fantasma}.")
                self.log("- - - - - - - - - -")                 
                self.precio_ult_comp = self.precio_actual                                
                self.reportado_trabajando = False
                reproducir_sonido("Sounds/ghostcom.wav")
              
    def parametro_compra_B(self):
        #Compra con referencia a la ultima venta
        if not self.param_b_enabled:
            return
        if self.varVenta <= -self.porc_desde_venta:
            
            if self.usdt >= self.fixed_buyer: 
                
                self.log("🔵 [Parametro B].")     
                self.comprar()
                self.precio_ult_venta = self.precio_actual
                self.precio_ult_comp = self.precio_actual
                self.param_b_enabled = False  # Deshabilitamos B hasta la próxima venta                                
            else:  
                            
                self.log(f"⚠️ (B) Fondos insuficientes, nueva compra fantasma registrada a $ {self.precio_actual:.2f}")
                self.log("- - - - - - - - - -")
                self.contador_compras_fantasma += 1                 
                self.param_b_enabled = False       
                self.reportado_trabajando = False
                reproducir_sonido("Sounds/ghostcom.wav")                                         
                return      
        
    def vender(self):
        transacciones_vendidas = []
        sale_executed = False

        for transaccion in self.transacciones:
            if self.btc < transaccion["btc"]:
                continue  # Evita vender más BTC del disponible            
            elif self.precio_actual >= transaccion["venta_obj"]:
                self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                btc_vender = transaccion["btc"]
                usdt_obtenido = btc_vender * self.precio_actual                              
                self.usdt += usdt_obtenido
                self.btc -= btc_vender
                self.precio_ult_venta = self.precio_actual  
                invertido_usdt = transaccion.get("invertido_usdt", self.fixed_buyer)
                self.ganancia_neta = usdt_obtenido - invertido_usdt
                self.total_ganancia += self.ganancia_neta              
                self.actualizar_balance()
                sale_executed = True
                self.contador_ventas_reales += 1
                transaccion["ejecutado"] = True

                self.precios_ventas.append({
                    "compra": transaccion["compra"],
                    "venta": self.precio_actual,
                    "btc_vendido": btc_vender,
                    "ganancia": self.ganancia_neta,
                    "inverstido_usdt": invertido_usdt,
                    "venta_numero": self.contador_ventas_reales,
                    "timestamp": self.timestamp
                })
                
                transacciones_vendidas.append(transaccion)
                
                
                self.log(f"✅ Venta realizada.")
                self.log(f"Fecha: {self.timestamp}")
                self.log(f"🕒 Compra original: {self.precio_ult_comp:.2f}")
                self.log(f"📈 Precio de venta: $ {self.precio_actual:.2f}")
                self.log(f"📈 Venta numero: {self.contador_ventas_reales}")
                self.log(f"📤 Btc vendido: ₿ {btc_vender:.6f}")
                self.log(f"💹 Ganancia de esta operacion: $ {self.ganancia_neta:.8f}")
                self.log("- - - - - - - - - -")
                                
                reproducir_sonido("Sounds/soundventa.wav")
                self.reportado_trabajando = False
                
        # Eliminar las vendidas después del bucle
        for trans in transacciones_vendidas:
            self.transacciones.remove(trans)

        if sale_executed:
            # Tras una venta, reactivamos el parámetro B             
            self.param_b_enabled = True 

    def parametro_venta_B(self):
        #Venta fantasma
        if self.btc < self.btc_comprado and self.varVenta >= self.porc_desde_venta:                       
            self.ventas_fantasma.append(self.precio_actual)
            self.contador_ventas_fantasma += 1            
            self.precio_ult_venta = self.precio_actual           
            
            self.log(f"📌 Sin BTC para vender, nueva venta fantasma registrada a: $ {self.precio_actual:.2f}, Id: {self.contador_ventas_fantasma}.")
            self.log("- - - - - - - - - -")
            self.reportado_trabajando = False 
            reproducir_sonido("Sounds/ghostven.wav")               
                   
    def calcular_ghost_ratio(self):
        total_signals = (self.contador_compras_fantasma + self.contador_ventas_fantasma +
                         self.contador_compras_reales + self.contador_ventas_reales)
        if total_signals == 0:
            return 0
        return (self.contador_compras_fantasma + self.contador_ventas_fantasma) / total_signals
                          
    def realizar_primera_compra(self):
        if self.precio_actual is None or self.precio_actual == 0:
            self.log("❌ Precio actual no válido, no se puede realizar la compra.")
            self.log("- - - - - - - - - -")
            return
        self.log(f"🚀 Realizando primera compra a: $ {self.precio_actual:.6f}")        
        self.usdt -= self.fixed_buyer 
        self.actualizar_balance()        
        self.precio_ult_comp = self.precio_actual
        self.precios_compras.append(self.precio_ult_comp)
        self.btc_comprado = (1/self.precio_actual) * self.fixed_buyer
        self.btc = self.btc_comprado
        self.contador_compras_reales += 1
        self.precio_objetivo_venta = self.precio_actual * (1 + self.porc_profit_x_venta / 100)
        self.transacciones.append({"compra": self.precio_actual, "venta_obj": self.precio_objetivo_venta, "btc": self.btc_comprado, "numcompra": self.contador_compras_reales})
        self.log(f" Btc comprado: ₿ {self.btc_comprado:.6f}")
        self.log("- - - - - - - - - -")
                        
    def iniciar(self):
        # Capturamos precio de ingreso justo al arrancar
        self.precio_actual = self.get_precio_actual()
        self.precio_ingreso = self.precio_actual
        self.precio_ult_comp = self.precio_actual
        
        self.running = True

        self.log("🟡 Khazâd iniciado.")
        self.log("- - - - - - - - - -")
        self.realizar_primera_compra()
                                     
    def loop(self, after_fn=None):
            if not self.running:
                return
            self.precio_actual = self.get_precio_actual()
            if not self.precio_actual:
                self.log("⚠️ No se puede operar sin datos de precios.") 
                self.log("- - - - - - - - - -") 
                self.reportado_trabajando = False 
                #reproducir_sonido("Sounds/error.wav")             
            else:            
                self.varCompra = self.varpor_compra(self.precio_ult_comp, self.precio_actual) 
                self.varVenta = self.varpor_venta (self.precio_ult_venta, self.precio_actual) 
                self.actualizar_balance()
                self.vender()
                self.parametro_venta_fantasma = self.parametro_venta_B()
                self.parametro_compra_desde_compra = self.parametro_compra_A()                
                self.parametro_compra_desde_venta = self.parametro_compra_B()                
                self.var_inicio = self.varpor_ingreso()
                            
                if self.reportado_trabajando == False:                        
                    self.log("🟡 Trabajando...")   
                    self.log("- - - - - - - - - -")                   
                    self.reportado_trabajando = True   

            if self.btc < 0:
                self.log("🔴Error: btc negativo")
                self.reportado_trabajando = False 
                reproducir_sonido("Sounds/error.wav")
                self.detener()
                                                       
            if after_fn:
                after_fn(3000, lambda: self.loop(after_fn))

    def detener(self):
        self.running = False
        
        
        self.log("🔴 Khazâd detenido.")
        self.log("- - - - - - - - - -")

    def reiniciar(self):
        # 1) Guarda lo que queremos preservar
        _exchange = self.exchange
        _logfn    = self.log_fn

        # 2) Re-inicializa 
        self.__init__()

        # 3) Restaura exchange y callback
        self.exchange = _exchange
        self.log_fn   = _logfn

        # 4) Anota el reinicio
        if self.log_fn:
            self.log("🔄 Khazâd reiniciado")
            self.log("- - - - - - - - - -")
        






