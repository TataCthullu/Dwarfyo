# © 2025 Khazâd Trading Bot
# Todos los derechos reservados.

import ccxt
from utils import reproducir_sonido
import datetime
#import uuid
from decimal import Decimal, InvalidOperation
from secrets import token_hex

"""Azul (\033[94m) para información general.
Amarillo (\033[93m) para valores clave como precios de ingreso.
Verde (\033[92m) para operaciones exitosas como compras y ventas.
Rojo (\033[91m) para advertencias y errores.
Cian (\033[96m) para detalles adicionales."""

class TradingBot:
    def __init__(self):
        self.exchange = ccxt.binance({ 'timeout': 3000 })

        self.log_fn = None
        self.sound_enabled = True
        self.start_time = None

        self.usdt = Decimal("5000")
        self.inv_ini = self.usdt
        self.btc = Decimal("0")        
        self.btc_comprado = Decimal("0")

        self.precio_actual = self._fetch_precio()
        self.btc_usdt = Decimal("0")

        self.parametro_compra_desde_compra = None
        self.parametro_compra_desde_venta = None
        self.parametro_venta_fantasma = None
        self.precio_ult_venta = None

        self.porc_desde_compra = Decimal("0.005")
        self.porc_desde_venta = Decimal("0.005")
        self.porc_inv_por_compra = Decimal("10")
        self.porc_profit_x_venta = Decimal("0.005")


        self.fixed_buyer = (self.usdt * self.porc_inv_por_compra) / Decimal("100")
        self.running = False
        self.valores_iniciales = {}
        self.precio_ult_comp = None
        self.usdt_mas_btc = Decimal("0")
        
        self.precios_ventas = []
        self.ventas_fantasma = []
        self.compras_fantasma = []
        self.transacciones = []
        self.kant_usdt_vendido = 0       
        self.varCompra = 0
        self.varVenta = 0       
        self.btc_vendido = 0
        self.precio_objetivo_venta = None
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
        
        self.contador_compras_reales = 0
        self.contador_ventas_reales = 0
        self.param_b_enabled = True  
        self.timestamp = None
        

    def log(self, mensaje):
        if self.log_fn:
            self.log_fn(mensaje)  

    def set_valores_iniciales(self, valores):
        self.valores_iniciales = valores  # un dict con los datos iniciales
                        
    def _fetch_precio(self) -> Decimal:
        """Trae el precio BTC/USDT como Decimal exacto."""
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            # Convertir a string para preservar precisión / ceros
            return Decimal(str(ticker['last']))
        except (InvalidOperation, Exception) as e:
            self.log(f"❌ Error obteniendo precio: {e}")
            if self.sound_enabled:
                reproducir_sonido("Sounds/error.wav")
            return None
        
    def actualizar_balance(self):
        
        """Actualiza BTC valorado en USDT y balance total."""
        if isinstance(self.precio_actual, Decimal):
            self.btc_usdt     = self.btc * self.precio_actual
            self.usdt_mas_btc = self.usdt + self.btc_usdt
        else:
            # en caso de error, no modificar balances
            pass

    #Variacion de precio con respecto a ultima compra
    def varpor_compra(self, precio_ult_comp: Decimal, precio_actual: Decimal) -> Decimal:
        if precio_ult_comp is None or precio_actual is None:
            return Decimal("0")
        return (precio_actual - precio_ult_comp) / precio_ult_comp

    def varpor_venta(self, precio_ult_venta: Decimal, precio_actual: Decimal) -> Decimal:
        if precio_ult_venta is None or precio_actual is None:
            return Decimal("0")
        return (precio_actual - precio_ult_venta) / precio_ult_venta

    def varpor_ingreso(self) -> Decimal:
        if self.precio_ingreso is None or self.precio_actual is None:
            return Decimal("0")
        return (self.precio_actual - self.precio_ingreso) / self.precio_ingreso
    
    def _new_id(self):
        # Genera 4 dígitos hex aleatorios
        return token_hex(2)  # e.g. '9f3b'

    def comprar(self):
            nuevo_precio = self._fetch_precio()
            if nuevo_precio is None:
                return
            self.precio_actual = nuevo_precio

            if self.usdt < self.fixed_buyer:
                self.log("⚠️ Usdt insuficiente para comprar.")
                return
            id_op = self._new_id()
            self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.usdt -= self.fixed_buyer             
            self.precio_ult_comp = self.precio_actual
            
            self.btc_comprado = (1/self.precio_actual) * self.fixed_buyer
            self.precio_objetivo_venta = self.precio_ult_comp * (Decimal('1') + self.porc_profit_x_venta)
            self.btc += self.btc_comprado
            self.contador_compras_reales += 1 
            
            self.transacciones.append({
                    "compra": self.precio_ult_comp,
                    "id": id_op,     
                    "venta_obj": self.precio_objetivo_venta,
                    "btc": self.btc_comprado,
                    "invertido_usdt": self.fixed_buyer,
                    "ejecutado": False,
                    "numcompra": self.contador_compras_reales,
                    "timestamp": self.timestamp
                })
                            
            self.actualizar_balance()            
            self.log("✅ Compra realizada.")
            self.log(f"📉 Precio de compra: $ {self.precio_actual}")
            self.log(f"🪙 Btc comprado: ₿ {self.btc_comprado}")
            self.log(f"🪙 Compra id: {id_op}")
            self.log(f"🪙 Compra Num: {self.contador_compras_reales}")
            self.log(f"🎯 Objetivo de venta: $ {self.precio_objetivo_venta}")
            self.log("- - - - - - - - - -")
             
            if self.sound_enabled:          
                reproducir_sonido("Sounds/soundcompra.wav")            
            self.reportado_trabajando = False

    def parametro_compra_A(self):
        #Compra con referencia a la ultima compra
        if self.varCompra <= -self.porc_desde_compra:
            if self.usdt >= self.fixed_buyer:  
                                   
                self.comprar()
                self.log("🔵 [Parametro A].") 
                self.log("- - - - - - - - - -")
                self.precio_ult_comp = self.precio_actual   

            else:                               
                self.compras_fantasma.append(self.precio_actual)
                self.contador_compras_fantasma += 1
                
                self.log(f"📌(A) Sin Usdt para comprar, nueva compra fantasma registrada a {self.precio_actual}, Num: {self.contador_compras_fantasma}.")
                self.log("- - - - - - - - - -")                 
                self.precio_ult_comp = self.precio_actual                                
                self.reportado_trabajando = False
                if self.sound_enabled:
                    reproducir_sonido("Sounds/ghostcom.wav")
              
    def parametro_compra_B(self):
        #Compra con referencia a la ultima venta
        if not self.param_b_enabled:
            return
        if self.varVenta <= -self.porc_desde_venta:            
            if self.usdt >= self.fixed_buyer:                     
                self.comprar()
                self.log("🔵 [Parametro B].")
                self.log("- - - - - - - - - -")
                self.precio_ult_comp = self.precio_actual
                self.param_b_enabled = False  # Deshabilitamos B hasta la próxima venta                                
            else:                          
                self.log(f"⚠️ERROR (B) Fondos insuficientes, nueva compra fantasma registrada a: $ {self.precio_actual}")
                self.log("- - - - - - - - - -")
                self.contador_compras_fantasma += 1                 
                self.param_b_enabled = False       
                self.reportado_trabajando = False
                if self.sound_enabled:
                    reproducir_sonido("Sounds/ghostcom.wav")                                         
                return      
        
    def vender(self):
        # refrescar precio
        nuevo_precio = self._fetch_precio()
        if nuevo_precio is None:
            return
        self.precio_actual = nuevo_precio

        ejecutadas = []
       
        
        for transaccion in self.transacciones:
            venta_obj = transaccion.get('venta_obj')
            # Saltar transacciones sin objetivo válido
            if not isinstance(venta_obj, Decimal):
                continue
            if self.precio_actual >= venta_obj:
                self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # capturamos el id de la compra original
                id_compra = transaccion["id"] 
                
                btc_vender = transaccion["btc"]
                usdt_obtenido = btc_vender * self.precio_actual                              
                self.usdt += usdt_obtenido
                self.btc -= btc_vender
                self.precio_ult_venta = self.precio_actual  
                invertido_usdt = transaccion.get("invertido_usdt", self.fixed_buyer)
                self.ganancia_neta = usdt_obtenido - invertido_usdt
                self.total_ganancia += self.ganancia_neta              
                self.actualizar_balance()
                
                self.contador_ventas_reales += 1
                

                self.precios_ventas.append({
                    "compra": transaccion["compra"],
                    "venta": self.precio_actual,
                    "btc_vendido": btc_vender,
                    "ganancia": self.ganancia_neta,
                    "inverstido_usdt": invertido_usdt,
                    "venta_numero": self.contador_ventas_reales,
                    "timestamp": self.timestamp,
                    "id_compra": id_compra
                })
                
                
                transaccion["ejecutado"] = True

                
                                
                self.log(f"✅ Venta realizada.")
                self.log(f"Fecha y hora: {self.timestamp}")
                self.log(f"🕒 Compra original: {self.precio_ult_comp}")
                self.log(f"🆔 Id: {id_compra}")
                self.log(f"📈 Precio de venta: $ {self.precio_actual}")
                self.log(f"📈 Venta numero: {self.contador_ventas_reales}")
                self.log(f"📤 Btc vendido: ₿ {btc_vender}")
                self.log(f"💹 Ganancia de esta operacion: $ {self.ganancia_neta}")
                self.log("- - - - - - - - - -")
                ejecutadas.append(transaccion)
                if self.sound_enabled:               
                    reproducir_sonido("Sounds/soundventa.wav")
                self.reportado_trabajando = False
                
        # eliminar transacciones ejecutadas y reactivar parámetro B
        for tx in ejecutadas:
            if tx in self.transacciones:
                self.transacciones.remove(tx)
        if ejecutadas:
            self.param_b_enabled = True

        self.venta_fantasma()
        self.actualizar_balance()               

         

    def venta_fantasma(self):
        """Registra una venta fantasma si no hay BTC y supera el umbral."""
        # solo si no hay BTC disponible y ya hubo al menos una venta real
        if self.btc == 0 and self.precio_ult_venta is not None:
             
            if self.varVenta >= self.porc_desde_venta:
                id_f = token_hex(2)
                self.contador_ventas_fantasma += 1
                # actualiza el último precio de venta de referencia
                self.precio_ult_venta = self.precio_actual
                self.ventas_fantasma.append({
                    'id': id_f,
                    'precio': self.precio_actual
                })
                self.log(f"📌 Venta fantasma #{self.contador_ventas_fantasma} a $ {self.precio_actual}")
                if self.sound_enabled:
                    reproducir_sonido("Sounds/ghostven.wav")             
                   
    def calcular_ghost_ratio(self) -> Decimal:
        total = (self.contador_compras_reales + self.contador_ventas_reales +
                 self.contador_compras_fantasma + self.contador_ventas_fantasma)
        if total == 0:
            return Decimal("0")
        return (self.contador_compras_fantasma + self.contador_ventas_fantasma) / Decimal(total)
             
    def realizar_primera_compra(self):
        if self.precio_actual is None or self.precio_actual == 0:
            self.log("❌ Precio actual no válido, no se puede realizar la compra.")
            self.log("- - - - - - - - - -")
            return
        
        self.comprar()
        
    def iniciar(self):
        # Capturamos precio de ingreso justo al arrancar
        self.precio_actual = self._fetch_precio()
        if self.precio_actual is None:
            return
        self.precio_ingreso = self.precio_actual
        self.precio_ult_comp = self.precio_actual
        self.start_time = datetime.datetime.now()
        
        self.running = True

        self.log("🟡 Khazâd iniciado.")
        self.log("- - - - - - - - - -")
        self.realizar_primera_compra()

    def get_start_time_str(self) -> str:    
        if not self.start_time:
            return "z"
        return self.start_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_runtime_str(self) -> str:
        """
        Devuelve una cadena tipo 'Xd Yh Zm' con
        días, horas y minutos transcurridos desde start_time.
        """
        if not self.start_time:
            return "z"
        delta = datetime.datetime.now() - self.start_time
        days = delta.days
        hours, rem = divmod(delta.seconds, 3600)
        minutes = rem // 60
        parts = []
        if days:
            parts.append(f"{days} día{'s' if days!=1 else ''}")
        if hours:
            parts.append(f"{hours} h")
        if minutes or not parts:
            parts.append(f"{minutes} min")
        return " ".join(parts) 
                                        
    def loop(self, after_fn=None):
            if not self.running:
                return
            self.precio_actual = self._fetch_precio()
            if self.precio_actual is None:
                return             
            else:            
                self.varCompra = self.varpor_compra(self.precio_ult_comp, self.precio_actual) 
                self.varVenta = self.varpor_venta(self.precio_ult_venta, self.precio_actual) 
                self.actualizar_balance()
                self.vender()                
                self.parametro_compra_desde_compra = self.parametro_compra_A()                
                self.parametro_compra_desde_venta = self.parametro_compra_B()  
                self.parametro_venta_fantasma = self.venta_fantasma()              
                self.var_inicio = self.varpor_ingreso()
                            
                if self.reportado_trabajando == False:                        
                    self.log("🟡 Trabajando...")   
                    self.log("- - - - - - - - - -")                   
                    self.reportado_trabajando = True   

            if self.btc < 0:
                self.log("🔴Error: btc negativo")
                self.reportado_trabajando = False
                if self.sound_enabled: 
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
        






