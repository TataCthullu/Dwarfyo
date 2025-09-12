# © 2025 Dungeon Market (Khazâd - Trading Bot)
# Todos los derechos reservados.

import ccxt
from utils import reproducir_sonido
import datetime
from decimal import Decimal, InvalidOperation, DivisionByZero, localcontext
from secrets import token_hex

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
        self.run_time = self.get_runtime_str()
        self.inv_inic = Decimal("5000")
        self.usdt = self.inv_inic
        self.btc = Decimal('0')      
        self.btc_comprado = Decimal('0')
        self.take_profit_pct = Decimal("3")   # % de ganancia total donde cerrar
        self.stop_loss_pct   = Decimal("1")            # lo dejamos para más adelante
        self.ui_callback_on_stop = None
        self.precio_actual = self._fetch_precio()
        self.btc_usdt = Decimal('0')
        self.parametro_compra_desde_compra = False
        self.parametro_compra_desde_venta = False
        self.parametro_compra_desde_venta_fantasma = False
        self.parametro_venta_fantasma = False
        self.param_a_enabled = True 
        self.precio_ult_venta = Decimal('0')
        self.porc_desde_compra = Decimal("0.005")
        self.porc_desde_venta = Decimal("0.005")
        self.porc_inv_por_compra = Decimal("10")
        self.porc_profit_x_venta = Decimal("0.005")
        self.rebalance_threshold = int(6)
        self.rebalance_pct = int(50)  # porcentaje del BTC a vender
        self.fixed_buyer = self.cant_inv()
        self.running = False
        self._stop_flag = False  # flag de parada “dura”
        self.valores_iniciales = {}
        self.precio_ult_comp = None
        self.usdt_mas_btc = Decimal('0')
        self.estado_compra = self.estado_compra_func()
        self.precios_ventas = []
        self.ventas_fantasma = []
        self.compras_fantasma = []
        self.transacciones = []
        self.kant_usdt_vendido = Decimal('0')       
        self.varCompra = Decimal('0')
        self.varVenta = Decimal('0')       
        self.btc_vendido = Decimal('0')
        self.precio_objetivo_venta = Decimal('0')
        self.precio_ingreso = Decimal('0')
        self.var_inicio = Decimal('0')
        self.log_fn = None
        self.usdt_obtenido = Decimal('0')
        self.contador_compras_fantasma = 0
        self.contador_ventas_fantasma = 0
        self.parametro_compra_fantasma = False
        self.total_ganancia = Decimal('0')
        self.ganancia_neta = Decimal('0')
        self.reportado_trabajando = False 
        self.hold_btc_var = Decimal('0')
        self.hold_usdt_var = Decimal('0')
        self.contador_compras_reales = 0
        self.contador_ventas_reales = 0
        self.param_b_enabled = True  
        self.excedente_total_compras = Decimal('0')
        self.excedente_total_ventas = Decimal('0')
        self.timestamp = None
        self.compra_en_venta_fantasma = False
        self.activar_compra_tras_vta_fantasma = False
        self.venta_fantasma_ocurrida = False
        self.var_total = Decimal('0')
        self.ghost_ratio = Decimal('0')
        self.sl_enabled = False
        self.tp_enabled = False
        self.rebalance_enabled = False
        self.rebalance_count = 0 
        self.rebalance_loss_total = Decimal('0')  # pérdidas acumuladas por rebalances
        self.ultimo_evento = None

    def format_fn(self, valor, simbolo=""):
        if valor is None:
            return ""
        if isinstance(valor, str):
            return valor.strip()
        if valor == 0:
            return f"{simbolo} 0" if simbolo else "0"

        try:
            if not isinstance(valor, Decimal):
                valor = Decimal(str(valor))

            with localcontext():
                valor = +valor

            # Si es entero exacto, no mostrar parte decimal
            if valor == valor.to_integral():
                texto = f"{valor:.0f}"  # fuerza entero sin decimales
            else:
                texto = format(valor, 'f').rstrip('0').rstrip('.')
            return f"{simbolo} {texto}" if simbolo else texto
        
        except (InvalidOperation, ValueError):
            return f"{simbolo} {valor}" if simbolo else str(valor)

    def estado_compra_func(self):
        return "activa"
    
    def es_activa(self, tx) -> bool:
        try:
            return tx.get("estado", "activa") == "activa" and tx.get("btc", Decimal("0")) > 0
        except Exception:
            return False


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

        return None
        
    def actualizar_balance(self):
        """
        Actualiza BTC valorado en USDT y balance total usando Decimal.
        Si btc o precio_actual no son válidos, pone ambos balances a Decimal('0').
        """
        try:
            # Convertir btc y usdt a Decimal si no lo son ya
            btc = self.btc if isinstance(self.btc, Decimal) else Decimal(self.btc or "0")
            usdt = self.usdt if isinstance(self.usdt, Decimal) else Decimal(self.usdt or "0")
            # precio_actual puede ser None o float/int; lo convertimos o damos cero
            if self.precio_actual is None:
                precio = Decimal('0')
            else:
                precio = self.precio_actual if isinstance(self.precio_actual, Decimal) else Decimal(self.precio_actual)
            # Cálculo principal
            self.btc_usdt = btc * precio
            self.usdt_mas_btc = usdt + self.btc_usdt

        except (InvalidOperation, TypeError, ValueError):
            # En caso de cualquier error de conversión, reiniciamos a cero
            self.btc_usdt = Decimal('0')
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
    
    def check_rebalance(self):
        if not getattr(self, "rebalance_enabled", False):
            self.log("⚖️ Rebalance: desactivado.")
            return
        
        if not self.running or self._stop_flag:
            return
        
        if self.contador_compras_fantasma < self.rebalance_threshold or not self.precio_actual:
            return

        # usar SOLO compras activas con BTC > 0
        activos = [tx for tx in self.transacciones
                if self.es_activa(tx) and tx.get("btc", Decimal("0")) > 0]
        n_total = len(activos)
        rebalance_loss_event = Decimal("0")  # 🔻 pérdida total SOLO de este rebalance

        if n_total == 0:
            self.log("⚖️ Rebalance: no hay transacciones activas. Se omite.")
            self.contador_compras_fantasma = 0  # evita loops
            return
        
        _rebalance_done = False
        
        if n_total > 1:
            # purgar % de las más antiguas
            n_a_vender = int(n_total * (self.rebalance_pct / Decimal("100")))
            if n_a_vender <= 0:
                n_a_vender = 1

            activos_ordenados = sorted(activos, key=lambda tx: tx.get("numcompra", 0))
            a_vender = activos_ordenados[:n_a_vender]

            total_btc_vendido = Decimal("0")
            total_usdt_obtenido = Decimal("0")
            for tx in a_vender:
                btc_vender = tx.get("btc", Decimal("0"))
                if btc_vender <= 0:
                    continue
                usdt_obtenido = btc_vender * self.precio_actual
                self.usdt += usdt_obtenido
                self.btc  -= btc_vender
                # marcar estado y vaciar btc
                
                tx["estado"] = "anulada"
                tx["btc"]    = Decimal("0")
                self.log(f"📝 Estado de compra #{tx.get('numcompra')} (id {tx.get('id')}): activa → anulada")
                self.log("- - - - - - - - - -")
            # 🔻 Pérdida de esta compra
                precio_compra_tx = tx.get("compra", None)
                if isinstance(precio_compra_tx, Decimal) and btc_vender > 0:
                    costo_base = btc_vender * precio_compra_tx
                    perdida = costo_base - usdt_obtenido
                    rebalance_loss_event += perdida
                    self.log(
                        f"   • Pérdida por rebalance en esta compra: "
                        f"{self.format_fn(perdida, '$')} (base {self.format_fn(costo_base, '$')} → "
                    )

                total_btc_vendido += btc_vender
                total_usdt_obtenido += usdt_obtenido
                _rebalance_done = True
            self.log(f"   • Estado actualizado: anulada")
            self.log(f"⚖️ Rebalance: purga {n_a_vender}/{n_total} compras antiguas.")
            self.log(f"📉 BTC vendido: {self.format_fn(total_btc_vendido, '₿')}")
            self.log(f"💰 USDT recibido: {self.format_fn(total_usdt_obtenido, '$')}")
            self.log("- - - - - - - - - -")

            if self.sound_enabled:
                reproducir_sonido("Sounds/rebalance.wav")

        else:
            # una sola compra activa: vender % de esa compra
            tx = activos[0]
            btc_total_tx = tx.get("btc", Decimal("0"))
            if btc_total_tx > 0:
                cantidad_a_vender = (btc_total_tx * self.rebalance_pct) / Decimal("100")
                usdt_obtenido = cantidad_a_vender * self.precio_actual

                self.usdt += usdt_obtenido
                self.btc  -= cantidad_a_vender
                tx["btc"]   = btc_total_tx - cantidad_a_vender

                
            # 🔻 NUEVO: pérdida parcial
            precio_compra_tx = tx.get("compra", None)
            if isinstance(precio_compra_tx, Decimal) and cantidad_a_vender > 0:
                costo_base = cantidad_a_vender * precio_compra_tx
                perdida = costo_base - usdt_obtenido
                rebalance_loss_event += perdida
                self.log(
                    f" • Pérdida por rebalance (parcial): "
                    f"{self.format_fn(perdida, '$')} (base {self.format_fn(costo_base, '$')} → "
                )
                
                self.log(f"   • Estado se mantiene: activa (parcialmente reducida)")
                self.log(f"⚖️ Rebalance: vendiendo {self.rebalance_pct}% de la única compra activa.")
                self.log(f"📉 BTC vendido: {self.format_fn(cantidad_a_vender, '₿')}")
                self.log(f"💰 USDT recibido: {self.format_fn(usdt_obtenido, '$')}")
                self.log("- - - - - - - - - -")
                _rebalance_done = True

                if self.sound_enabled:
                    reproducir_sonido("Sounds/rebalance.wav")

        # reset del trigger para no rebotar
        self.fixed_buyer = (self.usdt * self.porc_inv_por_compra) / Decimal('100')
        self.contador_compras_fantasma = 0
        # ✅ actualizar balances y dejar constancia
        self.actualizar_balance()
        self.log(f"💼 Balance tras rebalance → USDT: {self.format_fn(self.usdt, '$')}\n · BTC: {self.format_fn(self.btc, '₿')}")
        self.log("- - - - - - - - - -")
        
        if '_rebalance_done' in locals() and _rebalance_done:
            self.rebalance_count += 1
            self.log(f"📊 Rebalance #{self.rebalance_count} ejecutado")
    # 🔻 NUEVO: totales de pérdida
        if rebalance_loss_event > 0:
            self.rebalance_loss_total = (self.rebalance_loss_total or Decimal("0")) + rebalance_loss_event
            self.log(f"🔻 Pérdida total en este rebalance: {self.format_fn(rebalance_loss_event, '$')}")
            self.log(f"📉 Pérdida acumulada por rebalances: {self.format_fn(self.rebalance_loss_total, '$')}")
            self.log("- - - - - - - - - -")
    def hay_base_rebalance(self):
        return any(self.es_activa(tx) and tx.get("btc", Decimal("0")) > 0 for tx in self.transacciones)

    def comprar(self, trigger=None):
            if not self.running or self._stop_flag:
                return
            nuevo_precio = self._fetch_precio()

            if nuevo_precio is None:
                return
            
            self.precio_actual = nuevo_precio
            
            if not self.condiciones_para_comprar():
                self.log("Condiciones inválidas. No se realiza compra")
                return
            
            if self.usdt is None or self.usdt < self.fixed_buyer:
                self.log("⚠️ Usdt insuficiente para comprar.")
                return
            
            if self.precio_actual is None or self.precio_actual == 0:
                self.log("⚠️ Precio actual inválido para calcular BTC comprado.")
                return
            
            id_op = self._new_id()
            self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.usdt -= self.fixed_buyer             
            self.precio_ult_comp = self.precio_actual       
            self.btc_comprado = self.fixed_buyer / self.precio_actual
            self.precio_objetivo_venta = (self.precio_ult_comp * (Decimal('100') + self.porc_profit_x_venta)) / Decimal('100')
            self.btc = (self.btc or Decimal("0")) + self.btc_comprado
            self.contador_compras_reales += 1 

            self.transacciones.append({
                    "compra": self.precio_ult_comp,
                    "id": id_op,     
                    "venta_obj": self.precio_objetivo_venta,
                    "btc": self.btc_comprado,
                    "invertido_usdt": self.fixed_buyer,
                    "ejecutado": False,
                    "numcompra": self.contador_compras_reales,
                    "timestamp": self.timestamp,
                    "estado": self.estado_compra_func()
                })
                            
            self.actualizar_balance()            
            self.log("✅ Compra realizada.")
            self.log(f"📉 Precio de compra: {self.format_fn(self.precio_actual, '$')}")
            self.log(f"🪙 Btc comprado: {self.format_fn(self.btc_comprado, '₿')}")
            self.log(f"🪙 Compra id: {id_op}")
            self.log(f"🪙 Compra Num: {self.contador_compras_reales}")
            self.log(f"📜 Estado: {self.transacciones[-1].get('estado', 'activa')}")
            self.log(f"🎯 Objetivo de venta: {self.format_fn(self.precio_objetivo_venta, '$')}")
            
            

            # Excedente de bajada 
            if trigger == 'A':
                exceso = abs(self.varCompra) - self.porc_desde_compra
                if exceso > 0:               
                    self.excedente_total_compras += exceso
                    self.log(f"📊 Excedente de bajada: {self.format_fn(exceso, '%')}")
            elif trigger == 'B':
                exceso = abs(self.varVenta) - self.porc_desde_venta
                if exceso > 0:
                    self.excedente_total_compras += exceso
                    self.log(f"📊 Excedente de bajada: {self.format_fn(exceso, '%')}")

            if self.sound_enabled:          
                reproducir_sonido("Sounds/compra.wav")   
            
            self.ultimo_evento = datetime.datetime.now()         
            self.reportado_trabajando = False

    def parametro_compra_A(self):
        if not self.param_a_enabled:
            return False
    
        if self.porc_desde_compra <= Decimal('0'):
            return False
        #Compra con referencia a la ultima compra
        if self.varCompra <= -self.porc_desde_compra:
            if self.condiciones_para_comprar():                                   
                self.comprar(trigger='A')
                self.log("🔵 [Parametro A].") 
                self.log("- - - - - - - - - -")
                self.precio_ult_comp = self.precio_actual   
            else:                               
                self.compras_fantasma.append(self.precio_actual)
                self.contador_compras_fantasma += 1
                self.log(f"📌(A) Sin Usdt para comprar, nueva compra fantasma registrada a {self.format_fn(self.precio_actual, '$')}, Num: {self.contador_compras_fantasma}.")
                self.log("- - - - - - - - - -")                 
                self.precio_ult_comp = self.precio_actual   
                self.ultimo_evento = datetime.datetime.now()                             
                self.reportado_trabajando = False
                if self.sound_enabled:
                    reproducir_sonido("Sounds/compra_fantasma.wav")
            return False 
    def parametro_compra_B(self):
        if self.porc_desde_venta <= Decimal('0'):
            return False
        #Compra con referencia a la ultima venta
        if not self.param_b_enabled:
            return
        if self.varVenta <= -self.porc_desde_venta:            
            if self.condiciones_para_comprar():                     
                self.comprar(trigger='B')
                self.log("🔵 [Parametro B].")
                self.log("- - - - - - - - - -")
                self.precio_ult_comp = self.precio_actual
                self.param_a_enabled = True
                self.param_b_enabled = False  # Deshabilitamos B hasta la próxima venta                                
            else:                          
                self.log(f"⚠️ERROR (B) Fondos insuficientes, nueva compra fantasma registrada a: {self.format_fn(self.precio_actual, '$')}")
                self.log("- - - - - - - - - -")
                self.contador_compras_fantasma += 1                 
                self.param_b_enabled = False  
                self.ultimo_evento = datetime.datetime.now()     
                self.reportado_trabajando = False
                if self.sound_enabled:
                    reproducir_sonido("Sounds/compra_fantasma.wav")                                         
                return      
        return False
    
    def vender(self):
        if not self.running or self._stop_flag:
            return
        # refrescar precio
        nuevo_precio = self._fetch_precio()
       
        if nuevo_precio is None:
            return
       
        self.precio_actual = nuevo_precio
        self.actualizar_balance()
        ejecutadas = []
       
        for transaccion in self.transacciones:
            #  Aseguramos que haya BTC válido
            if self.btc is None or self.btc <= Decimal('0'):
                continue
#  Solo transacciones ACTIVAS
            if transaccion.get("estado", "activa") != "activa":
                continue

            #  Validamos también que la transacción tenga BTC válido
            if "btc" not in transaccion or not isinstance(transaccion["btc"], Decimal):
                continue

            if self.btc < transaccion["btc"]:
                continue  # Evita vender más BTC del disponible  

            venta_obj = transaccion.get('venta_obj')
            if not isinstance(venta_obj, Decimal):
                continue

            if self.precio_actual >= venta_obj:                        
                btc_vender = transaccion["btc"]
                self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # capturamos el id de la compra original
                id_compra = transaccion["id"]     
                usdt_obtenido = btc_vender * self.precio_actual                              
                self.usdt = (self.usdt or Decimal("0")) + usdt_obtenido
                self.btc = (self.btc or Decimal("0")) - btc_vender
                self.precio_ult_venta = self.precio_actual  
                invertido_usdt = transaccion.get("invertido_usdt", self.fixed_buyer)
                self.ganancia_neta = usdt_obtenido - invertido_usdt
                
                if self.total_ganancia is None:
                    self.total_ganancia = Decimal("0")

                self.total_ganancia += self.ganancia_neta
                excedente_pct = Decimal("0")

                if self.precio_actual > venta_obj:
                    try:
                        excedente_pct = ((self.precio_actual - venta_obj) / venta_obj) * Decimal("100")
                        self.excedente_total_ventas += excedente_pct
                    except (InvalidOperation, DivisionByZero):
                        excedente_pct = Decimal("0")

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
                self.log(f"🕒 Compra original: {self.format_fn(precio_compra, '$')}")
                self.log(f"🆔 Id: {id_compra}")
                self.log(f"🪙 Compra Num: {transaccion.get('numcompra')}")
                self.log(f"📈 Precio de venta: {self.format_fn(self.precio_actual, '$')}")
                self.log(f"📈 Venta numero: {self.contador_ventas_reales}")
                self.log(f"📤 Btc vendido: {self.format_fn(btc_vender, '₿')}")
                self.log(f"💹 Ganancia de esta operacion: {self.format_fn(self.ganancia_neta, '$')}")
                
                

                if excedente_pct > 0:
                    self.log(f"📊 Excedente sobre objetivo: {self.format_fn(excedente_pct, '%')}")
                
                self.log("- - - - - - - - - -")

                # marcar y luego remover fuera del loop
                
                transaccion["estado"] = "vendida"
                transaccion["btc"]    = Decimal("0")
                self.log(f"📝 Estado de compra #{transaccion.get('numcompra')} (id {transaccion.get('id')}): activa → vendida")
                self.log("- - - - - - - - - -")
                ejecutadas.append(transaccion)
                
                if self.sound_enabled:               
                    reproducir_sonido("Sounds/venta.wav")

                self.ultimo_evento = datetime.datetime.now()
                self.reportado_trabajando = False
                break

         # ----- remover transacciones vendidas (FUERA DEL LOOP) -----
        """for transaccion in ejecutadas:
            if transaccion in self.transacciones:
                self.transacciones.remove(transaccion)"""

        if ejecutadas:
            self.param_b_enabled = True
            self.param_a_enabled = False

        self.actualizar_balance()             

    def venta_fantasma(self) -> bool:
        if self.precio_ult_venta is None:
            return False

        self.varVenta = self.varpor_venta(self.precio_ult_venta, self.precio_actual)

        # Comprueba si la variación (%) supera el umbral
        if self.btc is not None and self.btc_comprado is not None and self.btc < self.btc_comprado and self.varVenta >= self.porc_desde_venta:
            id_f = token_hex(2)
            self.contador_ventas_fantasma += 1
            self.venta_fantasma_ocurrida = True
            self.activar_compra_tras_vta_fantasma = True
            # Actualiza el punto de referencia para el próximo umbral
            self.precio_ult_venta = self.precio_actual
            self.ventas_fantasma.append({
                'id': id_f,
                'precio': self.precio_actual
            })
            self.log(f"📌 Venta fantasma #{self.contador_ventas_fantasma} a {self.format_fn(self.precio_actual, '$')}")
            self.log("- - - - - - - - - -")
            self.ultimo_evento = datetime.datetime.now()
            self.reportado_trabajando = False

            if self.sound_enabled:
                reproducir_sonido("Sounds/venta_fantasma.wav")
            return True

        # Aseguramos que no quede activa si no se cumplió la condición
        self.activar_compra_tras_vta_fantasma = False
        self.venta_fantasma_ocurrida = False
        return False

    def variacion_total(self) -> Decimal:
        """
        % de variación sobre la inversión inicial.
        Si no hay precio de ingreso o inv_inic es cero, devolvemos 0.
        """
        # validaciones iniciales
        if not self.precio_ingreso or self.inv_inic == Decimal('0'):
            return Decimal('0')
        
        # calculamos el valor actual de la cartera en USDT
        usdt = self.usdt or Decimal("0")
        btc = self.btc or Decimal("0")
        precio = self.precio_actual or Decimal("0")
        actual = usdt + (btc * precio)
        # porcentaje
        delta = (actual - self.inv_inic) * Decimal('100') / self.inv_inic
        # si por redondeo diera 0, devolvemos explícitamente Decimal('0')
        return delta if delta != 0 else Decimal('0')
    
    def condiciones_para_comprar(self) -> bool:
        try:
            if any(x is None for x in [self.fixed_buyer, self.usdt, self.precio_actual]):
                return False
            if self.fixed_buyer <= Decimal('0'):
                return False
            if self.usdt < self.fixed_buyer:
                return False
            if not isinstance(self.precio_actual, (int, float, Decimal)):
                return False
            if Decimal(self.precio_actual) <= 0:
                return False
            return True

        except Exception as e:
            self.log(f"❌ Error en condiciones_para_comprar: {e}")
            return False

    def hold_usdt(self):
        try:
            if not self.running or self.contador_compras_reales == 0:
                return Decimal("0")
            if not self.precio_ingreso or not self.precio_actual or not self.inv_inic:
                return Decimal("0")

            btc_hold = self.inv_inic / self.precio_ingreso
            return btc_hold * self.precio_actual

        except (InvalidOperation, ZeroDivisionError, TypeError):
            return Decimal("0")

    def hold_btc(self) -> Decimal:
        """
        Devuelve cuánto BTC habrías comprado con la inversión inicial y el precio de ingreso.
        """
        try:
            if not self.precio_ingreso or self.inv_inic == Decimal("0"):
                return Decimal("0")

            ingreso = self.precio_ingreso if isinstance(self.precio_ingreso, Decimal) else Decimal(str(self.precio_ingreso))
            inv     = self.inv_inic       if isinstance(self.inv_inic, Decimal)       else Decimal(str(self.inv_inic))
            btc_resultado = inv / ingreso
            return btc_resultado if btc_resultado != 0 else Decimal("0")

        except (InvalidOperation, ZeroDivisionError, TypeError, ValueError) as e:
            self.log(f"❌ Error en hold_btc: {e}")
            return Decimal("0")    
                   
    def calcular_ghost_ratio(self) -> Decimal:
        total = (self.contador_compras_reales + self.contador_ventas_reales +
                 self.contador_compras_fantasma + self.contador_ventas_fantasma)
        if total == 0:
            return Decimal("0")
        return (self.contador_compras_fantasma + self.contador_ventas_fantasma) / Decimal(total)
             
    def realizar_primera_compra(self):
        if self.condiciones_para_comprar():
            self.comprar()
            self.log("- - - - - - - - - -")
        else:
            self.log("No cumple las condiciones para comprar")

    def iniciar(self):
        # Capturamos precio de ingreso justo al arrancar
        self.precio_actual = self._fetch_precio()
        if self.precio_actual is None:
            return
        if self.condiciones_para_comprar():
            #self.log(f"🧪 Init check: precio_actual={self.precio_actual}, fixed_buyer={self.fixed_buyer}, usdt={self.usdt}")

            self.precio_ingreso = self.precio_actual
            self.precio_ult_comp = self.precio_actual
            self.inv_inic = self.usdt
            self.start_time = datetime.datetime.now()
            self._stop_flag = False
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
                if not self.running or self._stop_flag:
                    return
                self.precio_actual = self._fetch_precio()
                if self.precio_actual is None:
                    return  
                           
                else:      
                    if self.precio_ult_comp is None:
                        self.varCompra = Decimal("0")
                    else:
                        self.varCompra = self.varpor_compra(self.precio_ult_comp, self.precio_actual)

                    if self.precio_ult_venta is None:
                        self.varVenta = Decimal("0")
                    else:
                        self.varVenta = self.varpor_venta(self.precio_ult_venta, self.precio_actual)
                                             
                    self.actualizar_balance()
                    self.hold_btc_var = self.hold_btc()
                    self.hold_usdt_var = self.hold_usdt()
                    self.var_total = self.variacion_total()

                    # Check global TP/SL
                    if self.check_take_profit_stop_loss():
                        return

                    self.vender()                
                    self.parametro_compra_desde_compra = self.parametro_compra_A()                
                    self.parametro_compra_desde_venta = self.parametro_compra_B()
                    self.parametro_compra_desde_venta_fantasma = self.parametro_compra_C()  
                    self.parametro_venta_fantasma = self.venta_fantasma() 

                    if (self.rebalance_enabled 
                        and self.contador_compras_fantasma >= self.rebalance_threshold 
                        and self.hay_base_rebalance()):
                        self.check_rebalance()

                    if self.precio_ingreso is None:
                        self.var_inicio = Decimal("0")
                    else:
                        self.var_inicio = self.varpor_ingreso()

                    ahora = datetime.datetime.now()
                    if self.ultimo_evento is None:
                        self.ultimo_evento = ahora

                    # si pasaron ≥5 segundos desde el último evento y todavía no lo reportamos
                    if (ahora - self.ultimo_evento).total_seconds() >= 5 and not self.reportado_trabajando:
                        self.log("🟡 Trabajando...")
                        self.log("- - - - - - - - - -")
                        self.reportado_trabajando = True

                if self.btc < 0:
                    self.log("🔴Error: btc negativo")
                    self.ultimo_evento = datetime.datetime.now()
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

    def parametro_compra_C(self):
        if not self.compra_en_venta_fantasma:
            return False
        #self.log(f"🧪 Parametro C: habilitado={self.compra_en_venta_fantasma}, activado={self.activar_compra_tras_vta_fantasma}, ocurrida={self.venta_fantasma_ocurrida}")
        if self.activar_compra_tras_vta_fantasma and self.venta_fantasma_ocurrida:
            
            if self.condiciones_para_comprar():
                self.comprar()
                self.param_b_enabled = False  # 🔒 Desactivar B luego de C
                self.param_a_enabled = True
                self.log("🔵 [Parametro C] Compra tras venta fantasma.")
                self.log("- - - - - - - - - -")
            else:
                self.log("⚠️ Fondos o condiciones insuficientes para Parametro C.")
                self.log("- - - - - - - - - -")
                self.precio_ult_venta = self.precio_actual  # ✅ Siempre actualizamos
                self.param_b_enabled = True  # 🟢 B vuelve a activarse si no se pudo comprar

            self.activar_compra_tras_vta_fantasma = False
            self.venta_fantasma_ocurrida = False
            return True
        
        return False

    def detener(self, motivo=None):
        self.running = False
        self._stop_flag = True
        if motivo:
            self.log(f"🔴 Khazâd detenido. Motivo: {motivo}")
        else:
            self.log("🔴 Khazâd detenido.")
        self.log("- - - - - - - - - -")
        if self.ui_callback_on_stop:
            self.ui_callback_on_stop(motivo)

    def reiniciar(self):
        # estado base
        self.running = False
        self._stop_flag = False
        self.precio_actual = None

        # 1) Guarda lo que queremos preservar
        _exchange = self.exchange
        _logfn = self.log_fn

        # 2) Re-inicializa 
        self.__init__()

        # 3) Restaura exchange y callback
        self.exchange = _exchange
        self.log_fn = _logfn

        # 4) Anota el reinicio
        if self.log_fn:
            self.log("🔄 Khazâd reseteado")
            self.log("- - - - - - - - - -")
        
    def check_take_profit_stop_loss(self):
        variacion = self.variacion_total()

        # nada que hacer si no hay compras reales
        if self.contador_compras_reales == 0:
            return False

        if self.tp_enabled and self.take_profit_pct and variacion >= self.take_profit_pct:
            self.log(f"🎯 Take Profit alcanzado: {variacion:.2f}%")
            
            if self.sound_enabled:
                reproducir_sonido("Sounds/take_profit.wav")

            if self.btc > 0:
                self.usdt += self.btc * self.precio_actual
                self.log(f"💰 Vendido todo el BTC ({self.btc} ₿) a {self.format_fn(self.precio_actual, '$')}")
                self.btc = Decimal("0")
            self.detener(motivo="TP/SL")
            return True

        if self.sl_enabled and self.stop_loss_pct and variacion <= -self.stop_loss_pct:
            self.log(f"🛑 Stop Loss alcanzado: {variacion:.2f}%")
            
            if self.sound_enabled:
                reproducir_sonido("Sounds/stop_loss.wav")

            if self.btc > 0:
                self.usdt += self.btc * self.precio_actual
                self.log(f"💰 Vendido todo el BTC ({self.btc} ₿) a {self.format_fn(self.precio_actual, '$')}")
                self.btc = Decimal("0")
            self.detener(motivo="TP/SL")
            return True

        return False







