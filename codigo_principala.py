# © 2025 Khazâd Trading Bot
# Todos los derechos reservados.

import ccxt
from utils import reproducir_sonido
import datetime
#import uuid
from decimal import Decimal, InvalidOperation, DivisionByZero
from secrets import token_hex

"""Azul (\033[94m) para información general.
Amarillo (\033[93m) para valores clave como precios de ingreso.
Verde (\033[92m) para operaciones exitosas como compras y ventas.
Rojo (\033[91m) para advertencias y errores.
Cian (\033[96m) para detalles adicionales."""

class TradingBot:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'timeout': 10000,                # 10 segundos
            'options': {'defaultType': 'spot'}
        })

        self.log_fn = None
        self.sound_enabled = True
        self.start_time = None

        self.inv_inic = Decimal("0")
        self.usdt = self.inv_inic
        self.btc = Decimal("0")        
        self.btc_comprado = Decimal("0")
        

        self.precio_actual = self._fetch_precio()
        self.btc_usdt = Decimal("0")

        self.parametro_compra_desde_compra = False
        self.parametro_compra_desde_venta = False
        self.parametro_venta_fantasma = False
        self.precio_ult_venta = Decimal("0")

        self.porc_desde_compra = Decimal("0.5")
        self.porc_desde_venta = Decimal("0.5")
        self.porc_inv_por_compra = Decimal("10")
        self.porc_profit_x_venta = Decimal("0.5")


        self.fixed_buyer = self.cant_inv()
        self.running = False
        self.valores_iniciales = {}
        self.precio_ult_comp = Decimal("0")
        self.usdt_mas_btc = Decimal("0")
        
        self.precios_ventas = []
        self.ventas_fantasma = []
        self.compras_fantasma = []
        self.transacciones = []
        self.kant_usdt_vendido = Decimal("0")       
        self.varCompra = Decimal("0")
        self.varVenta = Decimal("0")       
        self.btc_vendido = Decimal("0")
        self.precio_objetivo_venta = None
        self.precio_ingreso = None
        self.var_inicio = Decimal("0")
        self.log_fn = None
        self.usdt_obtenido = Decimal("0")
        self.contador_compras_fantasma = 0
        self.contador_ventas_fantasma = 0
        self.parametro_compra_fantasma = False
        self.total_ganancia = Decimal("0")
        self.ganancia_neta = Decimal("0")
        self.reportado_trabajando = False 
        self.hold_btc_var = self.hold_btc()
        self.hold_usdt_var = self.hold_usdt()
        self.contador_compras_reales = 0
        self.contador_ventas_reales = 0
        self.param_b_enabled = True  
        self.timestamp = None
        self.ghost_purchase_enabled = False  
        

    def log(self, mensaje):
        if self.log_fn:
            self.log_fn(mensaje)  

    def set_valores_iniciales(self, valores):
        self.valores_iniciales = valores  # un dict con los datos iniciales
                        
    def _fetch_precio(self) -> Decimal:
        try:
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            info = ticker.get('info', {}) or {}

            raw = info.get('lastPrice')
            
            if raw is None:
                # No usamos str(ticker['last']) que es float, sino que fallamos.
                self.log("⚠️ No se encontró lastPrice en la respuesta cruda; precio no actualizado.")
                return None

            # Convertimos directamente el string ("12345.67000000") a Decimal
            try:
                return Decimal(raw)
            
            except InvalidOperation as e:
                self.log(f"⚠️ lastPrice no válido (‘{raw}’): {e}")
                return None
        
        except (ccxt.NetworkError, ccxt.RequestTimeout) as e:
            self.log(f"⚠️ Error de red al obtener precio: {e}")
        except ccxt.ExchangeError as e:
            self.log(f"⚠️ Error del exchange al obtener precio: {e}")
        except Exception as e:
            self.log(f"❌ Error inesperado obteniendo el precio: {e}")
        reproducir_sonido("Sounds/error.wav")
        return None
        
    def actualizar_balance(self):
        """
        Actualiza BTC valorado en USDT y balance total usando Decimal.
        Si btc o precio_actual no son válidos, pone ambos balances a Decimal('0').
        """
        try:
            # Convertir btc y usdt a Decimal si no lo son ya
            btc = self.btc if isinstance(self.btc, Decimal) else Decimal(self.btc)
            usdt = self.usdt if isinstance(self.usdt, Decimal) else Decimal(self.usdt)
            
            # precio_actual puede ser None o float/int; lo convertimos o damos cero
            if self.precio_actual is None:
                precio = Decimal('0')
            else:
                precio = self.precio_actual if isinstance(self.precio_actual, Decimal) else Decimal(self.precio_actual)
            
            # Cálculo principal
            self.btc_usdt     = btc * precio
            self.usdt_mas_btc = usdt + self.btc_usdt

        except (InvalidOperation, TypeError, ValueError):
            # En caso de cualquier error de conversión, reiniciamos a cero
            self.btc_usdt     = Decimal('0')
            self.usdt_mas_btc = Decimal('0')

    def cant_inv(self) -> Decimal:
        """
        Calcula cuánto invertir (inv_inic * porc_inv_por_compra / 100),
        devolviendo 0 en Decimal si hay cualquier problema.
        """
        try:
            inv = self.inv_inic if isinstance(self.inv_inic, Decimal) else Decimal(self.inv_inic)
            pct = self.porc_inv_por_compra if isinstance(self.porc_inv_por_compra, Decimal) \
                else Decimal(self.porc_inv_por_compra)
            return inv * pct / Decimal('100')
        except (InvalidOperation, TypeError, ValueError):
            return Decimal('0')       

    def varpor_compra(self, precio_ult_comp: Decimal, precio_act_btc: Decimal) -> Decimal:
        """Variación porcentual desde la última compra, o 0 si no aplicable."""
        if self.contador_compras_reales == 0:
            return Decimal("0")
        else:
            try:
                # Si alguno es None o cero, devolvemos 0
                if precio_ult_comp is None or precio_act_btc is None or precio_ult_comp == Decimal("0"):
                    return Decimal("0")
                # (nuevo − viejo) / viejo * 100
                else:
                    return (precio_act_btc - precio_ult_comp) / precio_ult_comp * Decimal("100")
            except (InvalidOperation, DivisionByZero) as e:
                self.log(f"❌ Error calculando varpor_compra: {e}")
                return Decimal("0")

    def varpor_venta(self, precio_ult_venta: Decimal, precio_act_btc: Decimal) -> Decimal:
        """Variación porcentual desde la última venta, o 0 si no aplicable."""
        if self.contador_ventas_reales == 0:
            return Decimal("0")
        else:
            try:
                if precio_ult_venta is None or precio_act_btc is None or precio_ult_venta == Decimal("0"):
                    return Decimal("0")
                else:
                    return (precio_act_btc - precio_ult_venta) / precio_ult_venta * Decimal("100")
            except (InvalidOperation, DivisionByZero) as e:
                self.log(f"❌ Error calculando varpor_venta: {e}")
                return Decimal("0")

    def varpor_ingreso(self) -> Decimal:
        """Variación porcentual desde el precio de ingreso, o 0 si no aplicable."""
        if self.contador_compras_reales == 0:
            return Decimal("0")
        else:
            try:
                if self.precio_ingreso is None or self.precio_actual is None or self.precio_ingreso == Decimal("0"):
                    return Decimal("0")
                else:
                    return (self.precio_actual - self.precio_ingreso) / self.precio_ingreso * Decimal("100")
            except (InvalidOperation, DivisionByZero) as e:
                self.log(f"❌ Error calculando varpor_ingreso: {e}")
                return Decimal("0")
    
    def _new_id(self):
        # Genera 4 dígitos hex aleatorios
        return token_hex(2)  # e.g. '9f3b'

    def comprar(self):
            nuevo_precio = self._fetch_precio()
            if nuevo_precio is None:
                return
            self.precio_actual = nuevo_precio
            if self.fixed_buyer <= Decimal('0'):
                self.log("Monto fijo invalido. No se realiza compra")
                return
            if self.usdt < self.fixed_buyer:
                self.log("⚠️ Usdt insuficiente para comprar.")
                return
            id_op = self._new_id()
            self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.usdt -= self.fixed_buyer             
            self.precio_ult_comp = self.precio_actual
            
            self.btc_comprado = self.fixed_buyer / self.precio_actual
            self.precio_objetivo_venta = (self.precio_ult_comp * (Decimal('100') + self.porc_profit_x_venta)) / Decimal('100')
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
             
            if self.sound_enabled:          
                reproducir_sonido("Sounds/soundcompra.wav")            
            self.reportado_trabajando = False

    def parametro_compra_A(self):
        if self.porc_desde_compra <= Decimal('0'):
            return False
        #Compra con referencia a la ultima compra
        if self.varCompra <= -self.porc_desde_compra:
            if self.fixed_buyer > Decimal('0') and self.usdt >= self.fixed_buyer:  
                                   
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
            return False 
    def parametro_compra_B(self):
        if self.porc_desde_venta <= Decimal('0'):
            return False
        #Compra con referencia a la ultima venta
        if not self.param_b_enabled:
            return
        if self.varVenta <= -self.porc_desde_venta:            
            if self.fixed_buyer > Decimal('0') and self.usdt >= self.fixed_buyer:                     
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
        return False
    
    def vender(self):
        # refrescar precio
        nuevo_precio = self._fetch_precio()
        if nuevo_precio is None:
            return
        self.precio_actual = nuevo_precio
        self.actualizar_balance()
        ejecutadas = []
       
        
        for transaccion in self.transacciones:
            if self.btc < transaccion["btc"]:
                    continue  # Evita vender más BTC del disponible  
            venta_obj = transaccion.get('venta_obj')
            # Saltar transacciones sin objetivo válido
            if not isinstance(venta_obj, Decimal):
                continue
            if self.precio_actual >= venta_obj:
                               
                btc_vender = transaccion["btc"]
                
                self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # capturamos el id de la compra original
                id_compra = transaccion["id"]     
                usdt_obtenido = btc_vender * self.precio_actual                              
                self.usdt += usdt_obtenido
                self.btc -= btc_vender
                self.precio_ult_venta = self.precio_actual  
                invertido_usdt = transaccion.get("invertido_usdt", self.fixed_buyer)
                self.ganancia_neta = usdt_obtenido - invertido_usdt
                self.total_ganancia += self.ganancia_neta              
                
                
                self.contador_ventas_reales += 1
                

                self.precios_ventas.append({
                    "compra": transaccion["compra"],
                    "venta": self.precio_actual,
                    "btc_vendido": btc_vender,
                    "ganancia": self.ganancia_neta,
                    "invertido_usdt": invertido_usdt,
                    "venta_numero": self.contador_ventas_reales,
                    "timestamp": self.timestamp,
                    "id_compra": id_compra
                })
                
                precio_compra = transaccion.get('compra', Decimal('0'))
                transaccion["ejecutado"] = True

                
                                
                self.log(f"✅ Venta realizada.")
                self.log(f"Fecha y hora: {self.timestamp}")
                self.log(f"🕒 Compra original: {precio_compra}")
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
                break
        # eliminar transacciones ejecutadas y reactivar parámetro B
        for tx in ejecutadas:
            if tx in self.transacciones:
                self.transacciones.remove(tx)
        if ejecutadas:
            self.param_b_enabled = True
            

        
        self.actualizar_balance()               

         

    def venta_fantasma(self) -> bool:       
        if self.precio_ult_venta is None:
            return False  
        
        self.varVenta = self.varpor_venta(self.precio_ult_venta, self.precio_actual)

       
            # Comprueba si la variación (%) supera el umbral
        if self.btc < self.btc_comprado and self.varVenta >= self.porc_desde_venta:
            id_f = token_hex(2)
            self.contador_ventas_fantasma += 1
                # Actualiza el punto de referencia para el próximo umbral
            self.precio_ult_venta = self.precio_actual
            self.ventas_fantasma.append({
                'id': id_f,
                'precio': self.precio_actual
            })
            self.log(f"📌 Venta fantasma #{self.contador_ventas_fantasma} a $ {self.precio_actual}")
            self.log(f"---------------------------------------------------------")
            if self.sound_enabled:
                reproducir_sonido("Sounds/ghostven.wav")
                
            # ── Si está habilitada, ejecutamos compra automática tras venta fantasma
            if getattr(self, 'ghost_purchase_enabled', False):
                if self.fixed_buyer > Decimal('0') and self.usdt >= self.fixed_buyer:
                    self.log("🔵 Ejecutando compra automática tras venta fantasma.")
                    self.comprar()
                else:
                    self.log("⚠️ Fondos insuficientes para compra automática tras venta fantasma.")
            return True

    def variacion_total(self) -> Decimal:
        """
        % de variación sobre la inversión inicial.
        Si no hay precio de ingreso o inv_inic es cero, devolvemos 0.
        """
        # validaciones iniciales
        if not self.precio_ingreso or self.inv_inic == Decimal('0'):
            return Decimal('0')
        # calculamos el valor actual de la cartera en USDT
        actual = self.usdt + (self.btc * self.precio_actual)
        # porcentaje
        delta = (actual - self.inv_inic) * Decimal('100') / self.inv_inic
        # si por redondeo diera 0, devolvemos explícitamente Decimal('0')
        return delta if delta != 0 else Decimal('0')

    def hold_usdt(self) -> Decimal:
        """
        Cuánto USDT tendrías haciendo HODL vs inversión activa.
        Si falta precio de ingreso o actual, devolvemos 0.
        """
        if not self.precio_ingreso or not self.precio_actual:
            return Decimal('0')
        
        resultado = (self.inv_inic / self.precio_ingreso) * self.precio_actual
        return resultado if resultado != 0 else Decimal('0')

    def hold_btc(self) -> Decimal:
        """
        Cuánto BTC (en sats) tendrías haciendo HODL.
        Si falta precio de ingreso o inv_inic es cero, devolvemos 0.
        """
        if not self.precio_ingreso or self.inv_inic == Decimal('0'):
            return Decimal('0')
        resultado = self.inv_inic / self.precio_ingreso
        return resultado if resultado != 0 else Decimal('0')
                             
                   
    def calcular_ghost_ratio(self) -> Decimal:
        total = (self.contador_compras_reales + self.contador_ventas_reales +
                 self.contador_compras_fantasma + self.contador_ventas_fantasma)
        if total == 0:
            return Decimal("0")
        return (self.contador_compras_fantasma + self.contador_ventas_fantasma) / Decimal(total)
             
    def realizar_primera_compra(self):
        self.comprar()
        
    def iniciar(self):
        # Capturamos precio de ingreso justo al arrancar
        self.precio_actual = self._fetch_precio()
        if self.precio_actual is None:
            return
        if self.fixed_buyer > Decimal('0') and self.usdt >= self.fixed_buyer:
            
            self.precio_ingreso = self.precio_actual
            self.precio_ult_comp = self.precio_actual
            self.inv_inic = self.usdt
            self.start_time = datetime.datetime.now()
            
            self.running = True

            self.log("🟡 Khazâd iniciado.")
            self.log("- - - - - - - - - -")
            self.realizar_primera_compra()

        
        else:
            self.log("No se puede iniciar por montos invalidos")    
            return
        
    def get_start_time_str(self) -> str:    
        if not self.start_time:
            return 
        return self.start_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_runtime_str(self) -> str:
        """
        Devuelve una cadena tipo 'Xd Yh Zm' con
        días, horas y minutos transcurridos desde start_time.
        """
        if not self.start_time:
            return 
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
            try:    
                if not self.running:
                    return
                self.precio_actual = self._fetch_precio()
                if self.precio_actual is None:
                    return             
                else:            
                    self.varCompra = self.varpor_compra(self.precio_ult_comp, self.precio_actual) 
                    self.varVenta = self.varpor_venta(self.precio_ult_venta, self.precio_actual) 
                    self.actualizar_balance()
                    self.hold_btc_var = self.hold_btc()
                    self.hold_usdt_var = self.hold_usdt()
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
            except Exception as e:
                self.log(f"🔴 Excepción en bucle: {e}")
                reproducir_sonido("Sounds/error.wav")    
                    
            finally:                                            
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
        






