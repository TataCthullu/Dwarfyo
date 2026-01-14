# © 2025 Dungeon Market (Khazâd - Trading Bot - codigo principal)
# Todos los derechos reservados.
"""
MODOS (NO CONFUNDIR):
- modo_app: "dum" | "libre"  -> entorno/economía del proyecto
- modus_operativa: "standard" | "avanzado" -> reglas de trading/historial
- 
"""
import threading
import ccxt
from utils import reproducir_sonido, parse_decimal_user
import datetime
from decimal import Decimal, InvalidOperation, DivisionByZero, ROUND_UP
from secrets import token_hex
import traceback

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
        self.inv_inic = Decimal("0")  # compatibilidad (baseline actual según modo)
        self.inv_inic_libre_usdt = None
        self.inv_inic_dum_usdt = None
        self.usdt = self.inv_inic
        self.btc = Decimal('0')      
        self.btc_comprado = Decimal('0')
        self.take_profit_pct = Decimal("0")   # % de ganancia total donde cerrar
        self.stop_loss_pct = Decimal("0")            # lo dejamos para más adelante
        self.ui_callback_on_stop = None
        self.precio_actual = None
        self.btc_usdt = Decimal('0')
        self.parametro_compra_desde_compra = False
        self.parametro_compra_desde_venta = False
        self.parametro_compra_desde_venta_fantasma = False
        self.parametro_venta_fantasma = False
        self.param_a_enabled = True 
        self.precio_ult_venta = None
        self.porc_desde_compra = Decimal("0.5")
        self.porc_desde_venta = Decimal("0.5")
        self.porc_inv_por_compra = Decimal("10")
        self.porc_profit_x_venta = Decimal("0.5")
        self.rebalance_threshold = int(0)
        self.rebalance_pct = int(0)  # porcentaje del BTC a vender
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
        self.precio_ingreso = None
        self.var_inicio = Decimal('0')
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
        # Comisiones
        self.total_fees_buy = Decimal('0')
        self.total_fees_sell = Decimal('0')
        self.ultimo_evento = None
        self.rebalance_concretado = False
        self.comisiones_enabled = True
        self.comision_pct = Decimal('0')          
        self.btc_fixed_seller = None
        self.update_btc_fixed_seller()
        self.hist_tentacles = None
        self.total_fees_btc = Decimal("0")
        self.dum_mode = False
        self.var_total_usdt = Decimal("0")
        self.rebalance_gain_total = Decimal("0")
        # --- DEV MODE ---
        self.dev_mode = False          # si True: imprime en consola VSCode
        self.dev_mode_ui = False       # si True: también manda DEV a la UI (opcional)
        self.dev_prefix = "DEV"
        self._dev_tick = 0
        self.dev_every = 5   # cada 5 loops (cada 10s si loop=2s)


        # --- MODOS (NO CONFUNDIR) ---
        # entorno / economía
        self.modo_app = "libre"   # "dum" | "libre"

        # reglas / comportamiento (standard vs avanzado)
        self.modus_operativa = "standard"  # "standard" | "avanzado"

        # compatibilidad con tu código viejo (vender() usa modus_actual)
        self.modus_actual = self.modus_operativa

        # vista / formato (si todavía no lo usás, lo dejamos listo)
        self.modo_vista = "decimal"  # "simple" | "detallado"
        
        # --- DUM: economía de run ---
        self.dum_cap = Decimal("5000")               # slot operativo (máximo dentro del bot)
        self.dum_deposit_total = Decimal("0")        # cuánto metió el usuario en total durante la run
        self.dum_extra_obsidiana = Decimal("0")      # exceso depositado que no entra al slot (se devuelve igual al cerrar)
        self.dum_run_abierta = False                 # para bloquear retiros/cambios manuales

        # --- Estado de conexión ---
        self.sin_conexion = False
        self.precio_vta_fantasma = None
        self._after_fn = None
        self._after_id = None
        self.lock = threading.RLock()  # RLock por si hay funciones internas que se llamen entre sí
    
    def _dec(self, x, default=Decimal("0")) -> Decimal:
        try:
            if x is None:
                return default
            return x if isinstance(x, Decimal) else Decimal(str(x))
        except (InvalidOperation, TypeError, ValueError):
            return default

    def _audit_state(self, tag=""):
        try:
            btc = self._dec(self.btc)
            usdt = self._dec(self.usdt)

            if usdt < 0:
                self.audit(f"USDT negativo: {self.format_fn(usdt, '$')}", tag=f"AUDIT{(':'+tag) if tag else ''}")
            if btc < 0:
                self.audit(f"BTC negativo: {self.format_fn(btc, '₿')}", tag=f"AUDIT{(':'+tag) if tag else ''}")

            btc_tx = Decimal("0")
            for tx in self.transacciones:
                if tx.get("fantasma", False):
                    continue
                if tx.get("estado", "activa") != "activa":
                    continue
                b = tx.get("btc", Decimal("0"))
                if isinstance(b, Decimal) and b > 0:
                    btc_tx += b

            tol = Decimal("0.00000001")
            if (btc - btc_tx).copy_abs() > tol:
                self.audit(
                    f"drift BTC → bot={self.format_fn(btc, '₿')} vs tx_act={self.format_fn(btc_tx, '₿')}",
                    tag=f"AUDIT{(':'+tag) if tag else ''}"
                )

        except Exception as e:
            self.audit(f"error: {e}", tag=f"AUDIT{(':'+tag) if tag else ''}")
        
    def _dev_exc(self, where, e):
        if getattr(self, "dev_mode", False):
            try:
                self.dev(f"{where}: {e}", tag="EXC")
                self.dev(traceback.format_exc(), tag="TRACE")
            except Exception:
                pass


    def format_fn(self, valor, simbolo=""):
        if valor is None:
            return ""

        if isinstance(valor, str):
            s = valor.strip()
            return f"{simbolo} {s}" if simbolo and s else s

        try:
            if not isinstance(valor, Decimal):
                valor = Decimal(str(valor))

            if valor == 0:
                return f"{simbolo} 0" if simbolo else "0"

            # salida plana (sin E+…)
            texto = format(valor, "f")  # ej "123.450000"

            # recortar ceros finales SIEMPRE (como venías)
            texto = texto.rstrip("0").rstrip(".") or "0"

            # evitar "-0"
            if texto in ("-0", "-0.0"):
                texto = "0"

            modo = getattr(self, "modo_vista", "decimal")

            # ✅ MODO "4": limitar a 4 decimales (sin redondear)
            
            if modo in ("4", "4_decimales", "cuatro"):
                if "." in texto:
                    ent, dec = texto.split(".", 1)
                    dec = dec[:4]  # ← recorta (NO redondea)
                    # limpiar si quedan ceros
                    dec = dec.rstrip("0")
                    texto = ent if dec == "" else f"{ent}.{dec}"

            return f"{simbolo} {texto}" if simbolo else texto

        except (InvalidOperation, ValueError, TypeError):
            return f"{simbolo} {valor}" if simbolo else str(valor)


    def estado_compra_func(self):
        return "activa"
    
    def es_activa(self, tx) -> bool:
        try:
            return tx.get("estado", "activa") == "activa" and tx.get("btc", Decimal("0")) > 0
        except Exception:
            return False
# DEV
    def log(self, mensaje, both: bool = False):
        # UI log (ScrolledText)
        if self.log_fn:
            self.log_fn(mensaje)

        # si querés duplicar algo puntual a consola
        if both and getattr(self, "dev_mode", False):
            try:
                print(mensaje)
            except Exception:
                pass
    def dev(self, mensaje, tag=None):
        """
        DEV log: imprime en consola VSCode si dev_mode=True.
        Si dev_mode_ui=True también lo manda a la UI.
        """
        if not getattr(self, "dev_mode", False):
            return

        pref = getattr(self, "dev_prefix", "DEV")
        if tag:
            out = f"[{pref}:{tag}] {mensaje}"
        else:
            out = f"[{pref}] {mensaje}"

        # consola VSCode
        try:
            print(out)
        except Exception:
            pass

        # opcional: duplicar a UI
        if getattr(self, "dev_mode_ui", False):
            if self.log_fn:
                self.log_fn(out)

    def audit(self, mensaje, tag="AUDIT"):
        """
        Auditoría: por defecto a consola (dev_mode).
        """
        self.dev(mensaje, tag=tag)
#DEV

    def set_valores_iniciales(self, valores):
        self.valores_iniciales = valores  # un dict con los datos iniciales
                        
    def _fetch_precio(self) -> Decimal | None:
        """Devuelve el precio como Decimal, o None si no se pudo obtener."""

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
        Si precio_actual es None, btc_usdt queda 0 y usdt_mas_btc queda en USDT.
        """
        try:
            btc = self.btc if isinstance(self.btc, Decimal) else Decimal(str(self.btc or "0"))
            usdt = self.usdt if isinstance(self.usdt, Decimal) else Decimal(str(self.usdt or "0"))

            if self.precio_actual is None:
                self.btc_usdt = Decimal("0")
                self.usdt_mas_btc = usdt
                return

            precio = self.precio_actual if isinstance(self.precio_actual, Decimal) else Decimal(str(self.precio_actual))

            self.btc_usdt = btc * precio
            self.usdt_mas_btc = usdt + self.btc_usdt

        except (InvalidOperation, TypeError, ValueError) as e:
            self._dev_exc("actualizar_balance", e)
            # NO pisar a 0 todo (conserva último estado)
            return



    def cant_inv(self) -> Decimal:
        """
        Calcula cuánto invertir (inv_inic * porc_inv_por_compra / 100),
        devolviendo 0 en Decimal si hay cualquier problema.
        """
        try:
            inv = self.inv_inic if isinstance(self.inv_inic, Decimal) else Decimal(str(self.inv_inic or "0"))
            pct = self.porc_inv_por_compra if isinstance(self.porc_inv_por_compra, Decimal) else Decimal(str(self.porc_inv_por_compra or "0"))
            return (inv * pct) / Decimal("100")
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")
        
    def get_baseline_usdt(self) -> Decimal:
        """
        Baseline para métricas (PnL/variación) según modo_app.
        - libre: inv_inic_libre_usdt
        - dum:   inv_inic_dum_usdt
        Fallback: self.inv_inic
        """
        try:
            if getattr(self, "modo_app", "libre") == "dum":
                base = getattr(self, "inv_inic_dum_usdt", None)
            else:
                base = getattr(self, "inv_inic_libre_usdt", None)

            if base is None:
                base = getattr(self, "inv_inic", Decimal("0"))

            return base if isinstance(base, Decimal) else Decimal(str(base or "0"))
        except Exception:
            return Decimal("0")

    def varpor_compra(self, precio_ult_comp: Decimal | None, precio_act_btc: Decimal | None) -> Decimal:
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

    def varpor_venta(self, precio_ult_venta: Decimal | None, precio_act_btc: Decimal | None) -> Decimal:
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
            
            return
        
        if not self.running or self._stop_flag:
            return
        
        if self.contador_compras_fantasma < self.rebalance_threshold or not self.precio_actual:
            return
        
        with self.lock:
            # usar SOLO compras activas con BTC > 0
            activos = [
                tx for tx in self.transacciones
                if self.es_activa(tx)
                and tx.get("btc", Decimal("0")) > 0
                and not tx.get("fantasma", False)     # 👈 clave
            ]

            n_total = len(activos)
            rebalance_loss_event = Decimal("0")  # 🔻 pérdida total SOLO de este rebalance

            if n_total == 0:
                self.log("⚖️ Rebalance: no hay transacciones activas. Se omite.")
                self.contador_compras_fantasma = 0  # evita loops
                return
            
            _rebalance_done = False

            try:
                precio = self.precio_actual if isinstance(self.precio_actual, Decimal) else Decimal(str(self.precio_actual))
            except (InvalidOperation, TypeError, ValueError):
                return
            if precio <= 0:
                return

            if n_total > 1:
                # purgar % de las más antiguas (redondeo hacia ARRIBA)
                raw = (Decimal(n_total) * Decimal(self.rebalance_pct)) / Decimal("100")
                n_a_vender = int(raw.to_integral_value(rounding=ROUND_UP))
                n_a_vender = max(1, min(n_total, n_a_vender))  # clamp entre 1 y n_total

                activos_ordenados = sorted(activos, key=lambda tx: tx.get("numcompra", 0))
                a_vender = activos_ordenados[:n_a_vender]

                total_btc_vendido = Decimal("0")
                total_usdt_obtenido = Decimal("0")

                for tx in a_vender:
                    btc_vender = tx.get("btc", Decimal("0"))
                    if btc_vender <= 0:
                        continue

                    usdt_obtenido = btc_vender * precio

                    # fee (si aplica)
                    fee = Decimal("0")
                    if getattr(self, "comisiones_enabled", False):
                        pct = getattr(self, "comision_pct", Decimal("0")) or Decimal("0")
                        fee = (usdt_obtenido * pct) / Decimal("100")
                        usdt_obtenido -= fee
                    
                    if fee > 0:
                        self.total_fees_sell += fee

                    # mover balances
                    self.usdt += usdt_obtenido
                    self.btc  -= btc_vender

                    # ✅ pérdida/ganancia vs costo base (AHORA sí: btc_vender existe)
                    perdida = None
                    costo_base = None
                    precio_compra_tx = tx.get("compra", None)

                    if isinstance(precio_compra_tx, Decimal):
                        costo_base = btc_vender * precio_compra_tx
                        perdida = costo_base - usdt_obtenido  # >0 pérdida, <0 ganancia

                    if perdida is not None:
                        if perdida > 0:
                            rebalance_loss_event += perdida
                            self.log(
                                f"🔻 Rebalance compra #{tx.get('numcompra')}: "
                                f"-{self.format_fn(perdida, '$')} "
                                f"(base {self.format_fn(costo_base, '$')} → {self.format_fn(usdt_obtenido, '$')})"
                            )
                        elif perdida < 0:
                            gan = -perdida
                            self.rebalance_gain_total = (getattr(self, "rebalance_gain_total", Decimal("0")) or Decimal("0")) + gan
                            self.log(
                                f"✅ Rebalance compra #{tx.get('numcompra')}: "
                                f"+{self.format_fn(gan, '$')} "
                                f"(base {self.format_fn(costo_base, '$')} → {self.format_fn(usdt_obtenido, '$')})"
                            )

                    # marcar estado
                    tx["estado"] = "anulada"
                    tx["btc"] = Decimal("0")
                

                    self.log(f"📝 Estado de compra #{tx.get('numcompra')} (id {tx.get('id')}): activa → anulada")
                    self.log("- - - - - - - - - -")

                    total_btc_vendido += btc_vender
                    total_usdt_obtenido += usdt_obtenido
                    _rebalance_done = True

                self.log(f"⚖️ Rebalance: purga {n_a_vender}/{n_total} compras antiguas.")
                self.log(f"📉 BTC vendido: {self.format_fn(total_btc_vendido, '₿')}")
                self.log(f"💰 USDT recibido: {self.format_fn(total_usdt_obtenido, '$')}")
                self.log("- - - - - - - - - -")

                if self.sound_enabled:
                    reproducir_sonido("Sounds/rebalance.wav")

            else:
                tx = activos[0]
                btc_total_tx = tx.get("btc", Decimal("0"))
                cantidad_a_vender = Decimal("0")
                usdt_obtenido = Decimal("0")

                if btc_total_tx > 0:
                    cantidad_a_vender = (btc_total_tx * self.rebalance_pct) / Decimal("100")
                    usdt_obtenido = cantidad_a_vender * precio
                    
                    fee = Decimal("0")
                    if getattr(self, "comisiones_enabled", False):
                        pct = getattr(self, "comision_pct", Decimal("0")) or Decimal("0")
                        fee = (usdt_obtenido * pct) / Decimal("100")
                        usdt_obtenido -= fee
                        
                    if fee > 0:
                        self.total_fees_sell += fee   # ✅ acá va
                    
                    self.usdt += usdt_obtenido
                    self.btc  -= cantidad_a_vender
                    tx["btc"]  = btc_total_tx - cantidad_a_vender

                    _rebalance_done = True   # ✅ si vendió, se concretó

                    # pérdida (si hay compra Decimal)
                    # pérdida/ganancia (parcial)
                    precio_compra_tx = tx.get("compra", None)
                    if isinstance(precio_compra_tx, Decimal) and cantidad_a_vender > 0:
                        costo_base = cantidad_a_vender * precio_compra_tx
                        perdida = costo_base - usdt_obtenido  # >0 pérdida, <0 ganancia

                        if perdida > 0:
                            rebalance_loss_event += perdida
                            self.log(
                                f"🔻 Rebalance parcial compra #{tx.get('numcompra')}: "
                                f"-{self.format_fn(perdida, '$')} "
                                f"(base {self.format_fn(costo_base, '$')} → {self.format_fn(usdt_obtenido, '$')})"
                            )
                        elif perdida < 0:
                            gan = -perdida
                            self.rebalance_gain_total = (getattr(self, "rebalance_gain_total", Decimal("0")) or Decimal("0")) + gan
                            self.log(
                                f"✅ Rebalance parcial compra #{tx.get('numcompra')}: "
                                f"+{self.format_fn(gan, '$')} "
                                f"(base {self.format_fn(costo_base, '$')} → {self.format_fn(usdt_obtenido, '$')})"
                            )


                    if self.sound_enabled:
                        reproducir_sonido("Sounds/rebalance.wav")


        # reset del trigger para no rebotar
        usdt = self.usdt if isinstance(self.usdt, Decimal) else Decimal(str(self.usdt or "0"))
        pct  = self.porc_inv_por_compra if isinstance(self.porc_inv_por_compra, Decimal) else Decimal(str(self.porc_inv_por_compra or "0"))
        self.fixed_buyer = self.cant_inv()


        self.update_btc_fixed_seller()
        self.contador_compras_fantasma = 0
        # ✅ actualizar balances y dejar constancia
        
        self.actualizar_balance()
        self._audit_state("REBALANCE")
        self.log(
            f"💼 Balance tras rebalance → "
            f"USDT: {self.format_fn(self.usdt, '$')} | "
            f"BTC: {self.format_fn(self.btc, '₿')} | "
            f"TOTAL: {self.format_fn(self.usdt_mas_btc, '$')}"
        )

        self.log("- - - - - - - - - -")
        
        if '_rebalance_done' in locals() and _rebalance_done:
            self.rebalance_count += 1
            self.log(f"📊 Rebalance #{self.rebalance_count} ejecutado")
            self.rebalance_concretado = True   # ← encender jade

        # 🔻 Totales de pérdida
        if rebalance_loss_event > 0:
            self.rebalance_loss_total = (self.rebalance_loss_total or Decimal("0")) + rebalance_loss_event
            self.log(f"🔻 Pérdida total en este rebalance: {self.format_fn(rebalance_loss_event, '$')}")
            self.log(f"📉 Pérdida acumulada por rebalances: {self.format_fn(self.rebalance_loss_total, '$')}")
            self.log("- - - - - - - - - -")

    def hay_base_rebalance(self):
        return any(
            self.es_activa(tx)
            and tx.get("btc", Decimal("0")) > 0
            and not tx.get("fantasma", False)
            for tx in self.transacciones
        )

    def comprar(self, trigger=None):
            if not self.running or self._stop_flag:
                return
            # precio_actual ya fue actualizado por loop()
            if self.precio_actual is None:
                return
            
            with self.lock:
                self.update_btc_fixed_seller()

                if not self.condiciones_para_comprar():
                    self.log("Condiciones inválidas. No se realiza compra")
                    self.log("- - - - - - - - - -")
                    return
                
                if self.usdt is None or self.usdt < self.fixed_buyer:
                    self.log("⚠️ Usdt insuficiente para comprar.")
                    self.log("- - - - - - - - - -")
                    return
                
                if self.precio_actual is None or self.precio_actual == 0:
                    self.log("⚠️ Precio actual inválido para calcular BTC comprado.")
                    self.log("- - - - - - - - - -")
                    return
                
                try:
                    precio = self.precio_actual if isinstance(self.precio_actual, Decimal) else Decimal(str(self.precio_actual))
                    fixed  = self.fixed_buyer if isinstance(self.fixed_buyer, Decimal) else Decimal(str(self.fixed_buyer))
                except (InvalidOperation, TypeError, ValueError):
                    return
                if precio <= 0 or fixed <= 0:
                    return


            id_op = self._new_id()
            self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.usdt -= fixed
            self.precio_ult_comp = precio
            self.btc_comprado = fixed / precio

            # === Comisión de compra ===
            # Se cobra en BTC (resta BTC), pero se muestra en USDT al precio de compra
            comision_btc = Decimal("0")
            fee_buy_usdt = Decimal("0")
            if self.comisiones_enabled and (self.comision_pct or Decimal("0")) > 0:
                comision_btc = (self.btc_comprado * self.comision_pct) / Decimal("100")
                self.btc_comprado -= comision_btc            # afecta realmente al monto en BTC
                fee_buy_usdt = comision_btc * precio
                # 🔹 ACUMULADOR GLOBAL DE COMISIÓN EN BTC
                self.total_fees_btc += comision_btc

            self.precio_objetivo_venta = (self.precio_ult_comp * (Decimal('100') + self.porc_profit_x_venta)) / Decimal('100')
            self.btc = (self.btc or Decimal("0")) + self.btc_comprado
            self.contador_compras_reales += 1 
            self.rebalance_concretado = False
            valor_compra_usdt = self.btc_comprado * self.precio_actual
            
            

            self.transacciones.append({
                    "compra": self.precio_ult_comp,
                    "id": id_op,     
                    "venta_obj": self.precio_objetivo_venta,
                    "btc": self.btc_comprado,
                    "invertido_usdt": self.fixed_buyer,
                    "fee_usdt": fee_buy_usdt,
                    "fee_btc": comision_btc,
                    "ejecutado": False,
                    "numcompra": self.contador_compras_reales,
                    "valor_en_usdt": valor_compra_usdt,
                    "timestamp": self.timestamp,
                    "estado": self.estado_compra_func()
                })
            # Acumular total de comisiones de compra
            self.total_fees_buy += fee_buy_usdt
            self.actualizar_balance() 
            self._audit_state("BUY")           
            self.log("✅ Compra realizada.")
            self.log(f" . Fecha y Hora: {self.timestamp}")
            self.log(f"📉 Precio de compra: {self.format_fn(self.precio_actual, '$')}")
            self.log(f"🪙 Btc comprado: {self.format_fn(self.btc_comprado, '₿')}")
            self.log(f"🧾 Comisión: -{self.format_fn(fee_buy_usdt, '$')}")
            if comision_btc != 0:
                self.log(f"🧾 Comisión Satoshys: -{self.format_fn(comision_btc, '₿')}")
            self.log(f"🧾 Btc/Usdt comprado: {self.format_fn(valor_compra_usdt, '$')}")
            self.log(f"🪙 Compra id: {id_op}")
            self.log(f"🪙 Compra Num: {self.contador_compras_reales}")
            self.log(f"📜 Estado: {self.transacciones[-1].get('estado', 'activa')}")
            self.log(f"🎯 Objetivo de venta: {self.format_fn(self.precio_objetivo_venta, '$')}")            
            # ... al final de comprar(), justo después de self.btc += self.btc_comprado
            self.update_btc_fixed_seller()

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
                return True 
            else:                               
                self.compras_fantasma.append({
                    "precio": self.precio_actual,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "fantasma": True
                })

                self.contador_compras_fantasma += 1
               
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.log(f"📌(A) {ts} · Sin Usdt para comprar, nueva compra fantasma registrada a {self.format_fn(self.precio_actual, '$')}, Num: {self.contador_compras_fantasma}.")
                self.log("- - - - - - - - - -")                 
                self.precio_ult_comp = self.precio_actual   
                self.ultimo_evento = datetime.datetime.now()                             
                self.reportado_trabajando = False
                if self.sound_enabled:
                    reproducir_sonido("Sounds/compra_fantasma.wav")
                return False
        return False
         
    def parametro_compra_B(self):
        if self.porc_desde_venta <= Decimal('0'):
            return False
        #Compra con referencia a la ultima venta
        if not self.param_b_enabled:
            return False
        if self.varVenta <= -self.porc_desde_venta:            
            if self.condiciones_para_comprar():                     
                self.comprar(trigger='B')
                self.log("🔵 [Parametro B].")
                self.log("- - - - - - - - - -")
                self.precio_ult_comp = self.precio_actual
                self.param_a_enabled = True
                self.param_b_enabled = False  # Deshabilitamos B hasta la próxima venta                                
                return True
            else:         
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")                 
                self.log(f"⚠️  {ts} · Fondos insuficientes, nueva compra fantasma registrada a: {self.format_fn(self.precio_actual, '$')}")
                self.log("- - - - - - - - - -")
                self.contador_compras_fantasma += 1  
                self.compras_fantasma.append({
                    "precio": self.precio_actual,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "fantasma": True
                })               
                self.param_b_enabled = False  
                self.ultimo_evento = datetime.datetime.now()     
                self.reportado_trabajando = False
                if self.sound_enabled:
                    reproducir_sonido("Sounds/compra_fantasma.wav")                                         
                return False     
        return False
    
    def vender(self):
        if not self.running or self._stop_flag:
            return
        # refrescar precio
        # precio_actual ya fue actualizado por loop()
        if self.precio_actual is None:
            return
        
        with self.lock:
            self.update_btc_fixed_seller()
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
                    usdt_bruto = btc_vender * self.precio_actual
                    fee_sell_usdt = Decimal("0")
                    usdt_obtenido = usdt_bruto

                    if self.comisiones_enabled and (self.comision_pct or Decimal("0")) > 0:
                        fee_sell_usdt = (usdt_bruto * self.comision_pct) / Decimal("100")
                        usdt_obtenido = usdt_bruto - fee_sell_usdt
                    # Acumular total de comisiones de venta
                    self.total_fees_sell += fee_sell_usdt
                    self.usdt = (self.usdt or Decimal("0")) + usdt_obtenido
                    self.btc  = (self.btc or Decimal("0")) - btc_vender
                    self.precio_ult_venta = self.precio_actual
                    invertido_usdt = transaccion.get("invertido_usdt", self.fixed_buyer)
                    # Ganancia de esta operación (solo esta venta)
                    self.ganancia_neta = usdt_obtenido - invertido_usdt

                    
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
                        "fee_usdt": fee_sell_usdt,
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
                    self.log(f"🧾 Comisión: {self.format_fn(fee_sell_usdt, '$')}")
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
            if ejecutadas:
                # Solo borrar en modo Standard
                """modo_op = getattr(self, "modus_operativa", getattr(self, "modus_actual", "standard"))
                if modo_op == "standard":
                    for transaccion in ejecutadas:
                        if transaccion in self.transacciones:
                            self.transacciones.remove(transaccion)"""


                # Reinicio de parámetros siempre
                self.param_b_enabled = True
                self.param_a_enabled = False

            self.actualizar_balance()    

    def libre_depositar_usdt(self, monto) -> bool:
        """
        LIBRE: deposita USDT al bot (se SUMA, no setea).
        - Actualiza baseline libre (inv_inic_libre_usdt) sumando el depósito.
        - Recalcula fixed_buyer, btc_fixed_seller y balances.
        """
        try:
            if getattr(self, "modo_app", "libre") != "libre":
                return False

            try:
                m = parse_decimal_user(monto)
            except Exception:
                self.log(f"⚠️ Depósito inválido: {monto!r}")
                return False

            if m <= 0:
                return False

            with self.lock:
                usdt_actual = self.usdt if isinstance(self.usdt, Decimal) else Decimal(str(self.usdt or "0"))
                self.usdt = usdt_actual + m

                # baseline libre: acumula depósito (porque es capital que entra al sistema)
                if self.inv_inic_libre_usdt is None:
                    self.inv_inic_libre_usdt = Decimal("0")
                self.inv_inic_libre_usdt += m

                # compatibilidad: inv_inic refleja el baseline del modo actual
                self.inv_inic = self.inv_inic_libre_usdt

                # recalcular tamaño fijo / métricas
                self.fixed_buyer = self.cant_inv()
                self.update_btc_fixed_seller()
                self.actualizar_balance()

            self.log(
                f"🟦 LIBRE: depósito aplicado.\n"
                f" · USDT: {self.format_fn(self.usdt, '$')}\n"
                f" · Baseline libre: {self.format_fn(self.inv_inic_libre_usdt, '$')}"
            )
            self.log("- - - - - - - - - -")
            return True

        except (InvalidOperation, TypeError, ValueError):
            return False



    def liquidar_todo(self, motivo="CIERRE_TOTAL"):
        """
        Cierre total: vende TODO el BTC actual al precio_actual.
        - Aplica comisión de venta si corresponde.
        - Actualiza balances.
        - Marca transacciones activas como cerradas (TP/SL).
        - Registra 1 evento global en precios_ventas.
        Devuelve True si liquidó algo, False si no había nada para vender.
        """
        
        if not self.running or self._stop_flag:
            return False

        if self.precio_actual is None:
            return False

        try:
            precio = self.precio_actual if isinstance(self.precio_actual, Decimal) else Decimal(str(self.precio_actual))
        except (InvalidOperation, TypeError, ValueError):
            return False

        if precio <= 0:
            return False

        btc_total = self.btc if isinstance(self.btc, Decimal) else Decimal(str(self.btc or "0"))
        if btc_total <= 0:
            return False

        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- cálculo bruto y fee ---
        usdt_bruto = btc_total * precio
        fee_sell_usdt = Decimal("0")
        usdt_neto = usdt_bruto

        if self.comisiones_enabled and (self.comision_pct or Decimal("0")) > 0:
            pct = self.comision_pct if isinstance(self.comision_pct, Decimal) else Decimal(str(self.comision_pct))
            fee_sell_usdt = (usdt_bruto * pct) / Decimal("100")
            usdt_neto = usdt_bruto - fee_sell_usdt

        # --- aplicar al balance ---
        self.usdt = (self.usdt or Decimal("0")) + usdt_neto
        self.btc = Decimal("0")
        self.total_fees_sell += fee_sell_usdt
        self.precio_ult_venta = precio  # baseline coherente
        btc_vendido_real = btc_total
        # --- marcar transacciones activas ---
        estado_cierre = f"cerrada_{motivo}"  # ej: "cerrada_TP" / "cerrada_SL"
        cerradas = 0
        for tx in self.transacciones:
            st = tx.get("estado", "activa")
            b = tx.get("btc", Decimal("0"))

            # (opcional) auditoría previa
            if isinstance(b, Decimal) and b > 0:
                self.audit(
                    f"tx {tx.get('id')} estado={st} btc={b}",
                    tag=f"AUDIT:LIQUIDAR:{motivo or 'NA'}"
                )

            if st == "activa" and isinstance(b, Decimal) and b > 0 and not tx.get("fantasma", False):
                tx["estado"] = estado_cierre
                tx["btc"] = Decimal("0")
                tx["ejecutado"] = True
                cerradas += 1

            # (opcional) si querés detectar “drift” de estados raros
            st2 = tx.get("estado", "activa")
            b2 = tx.get("btc", Decimal("0"))
            if st2 != "activa" and isinstance(b2, Decimal) and b2 > 0:
                self.audit(
                    f"tx {tx.get('id')} estado={st2} con BTC>0 ({b2})",
                    tag=f"AUDIT:LIQUIDAR:{motivo or 'NA'}"
                )

        
        

        # --- registrar 1 evento global en historial ---
        # ganancia neta global vs inversión inicial (si existe)
        inv = self.get_baseline_usdt()
        usdt_actual = self.usdt if isinstance(self.usdt, Decimal) else Decimal(str(self.usdt or "0"))
        ganancia_global = usdt_actual - inv

        self.contador_ventas_reales += 1
        self.precios_ventas.append({
            "compra": self.precio_ingreso if isinstance(self.precio_ingreso, Decimal) else (None if self.precio_ingreso is None else Decimal(str(self.precio_ingreso))),
            "venta": precio,
            "btc_vendido": btc_vendido_real,
            "ganancia": ganancia_global,
            "invertido_usdt": inv,
            "fee_usdt": fee_sell_usdt,
            "venta_numero": self.contador_ventas_reales,
            "timestamp": self.timestamp,
            "id_compra": "CIERRE_TOTAL",
            "motivo": motivo,
            "tx_cerradas": cerradas,
        })

        # acumuladores globales (coherente con tu esquema)
        self.ganancia_neta = ganancia_global
       

        self.actualizar_balance()

        # --- logs ---
        self.log(f"🧨 CIERRE TOTAL ({motivo})")
        self.log(f" . Fecha y Hora: {self.timestamp}")
        self.log(f"📈 Precio: {self.format_fn(precio, '$')}")
        self.log(f"📤 BTC vendido: {self.format_fn(btc_total, '₿')}")
        self.log(f"💰 USDT bruto: {self.format_fn(usdt_bruto, '$')}")
        self.log(f"🧾 Fee venta: -{self.format_fn(fee_sell_usdt, '$')}")
        self.log(f"💰 USDT neto: {self.format_fn(usdt_neto, '$')}")
        self.log(f"📌 Tx cerradas: {cerradas}")
        self.log(f"💹 Resultado global vs inv_inic: {self.format_fn(ganancia_global, '$')}")
        self.log("- - - - - - - - - -")

        if self.sound_enabled:
            if motivo == "TP":
                reproducir_sonido("Sounds/take_profit.wav")
            elif motivo == "SL":
                reproducir_sonido("Sounds/stop_loss.wav")
            else:
                reproducir_sonido("Sounds/venta.wav")

        self.ultimo_evento = datetime.datetime.now()
        self.reportado_trabajando = False
        self.param_b_enabled = True
        self.param_a_enabled = False
        self.fixed_buyer = self.cant_inv()
        self.update_btc_fixed_seller()
        self.actualizar_balance()


        return True




    def update_btc_fixed_seller(self):
        """
        btc_fixed_seller = fixed_buyer / precio_actual (Decimal o None)
        Si no hay precio válido (>0) o fixed_buyer <= 0 → None
        """
        try:
            fb = self.fixed_buyer if isinstance(self.fixed_buyer, Decimal) else Decimal(str(self.fixed_buyer or 0))
        except (InvalidOperation, TypeError, ValueError):
            self.btc_fixed_seller = None
            return

        p = self.precio_actual
        try:
            pdec = p if isinstance(p, Decimal) else (None if p is None else Decimal(str(p)))
        except (InvalidOperation, TypeError, ValueError):
            self.btc_fixed_seller = None
            return

        if fb is not None and pdec is not None and fb > 0 and pdec > 0:
            # ✅ considerar comisión de compra en BTC
            if self.comisiones_enabled and (self.comision_pct or Decimal("0")) > 0:
                net_factor = (Decimal("100") - self.comision_pct) / Decimal("100")
            else:
                net_factor = Decimal("1")
            self.btc_fixed_seller = (fb / pdec) * net_factor
        else:
            self.btc_fixed_seller = None

        self.update_hist_tentacles()
    
    def venta_fantasma(self) -> bool:
        """
        Venta fantasma = mover el ancla de venta hacia arriba por escalones:
        cuando el precio sube >= porc_profit_x_venta desde precio_ult_venta.
        Guarda el precio exacto en precio_vta_fantasma para que Parametro C compre ahí.
        """
        # Necesitamos baseline: al menos una venta real previa
        if self.contador_ventas_reales == 0 or self.precio_ult_venta is None:
            # no hay baseline: nada que hacer
            self.activar_compra_tras_vta_fantasma = False
            self.venta_fantasma_ocurrida = False
            self.precio_vta_fantasma = None
            return False

        if self.precio_actual is None:
            return False

        # Variación desde la última venta (baseline móvil)
        self.varVenta = self.varpor_venta(self.precio_ult_venta, self.precio_actual)

        # Si todavía no superó el escalón de profit, apagar flags (no hay evento)
        if self.varVenta < self.porc_profit_x_venta:
            self.activar_compra_tras_vta_fantasma = False
            self.venta_fantasma_ocurrida = False
            self.precio_vta_fantasma = None
            return False

        # ✅ Evento de venta fantasma: subimos el ancla
        id_f = token_hex(2)
        self.contador_ventas_fantasma += 1
        self.venta_fantasma_ocurrida = True

        # Guardar el precio exacto del evento (para que C compre ahí)
        self.precio_vta_fantasma = self.precio_actual

        # Mover baseline para el próximo escalón
        self.precio_ult_venta = self.precio_actual

        # Habilitar compra C si el usuario lo activó (toggle)
        self.activar_compra_tras_vta_fantasma = True

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ventas_fantasma.append({
            "id": id_f,
            "precio": self.precio_vta_fantasma,
            "timestamp": ts,
        })

        self.log(
            f"📌 {ts} · Venta fantasma #{self.contador_ventas_fantasma} "
            f"(ancla ↑) a {self.format_fn(self.precio_vta_fantasma, '$')}"
        )
        self.log("- - - - - - - - - -")
        self.ultimo_evento = datetime.datetime.now()
        self.reportado_trabajando = False

        if self.sound_enabled:
            reproducir_sonido("Sounds/venta_fantasma.wav")

        return True



    def update_hist_tentacles(self):
        """
        Decide la familia a mostrar en historial por disponibilidad de recursos:
        - 'eldritch' si USDT < fixed_buyer
        - 'kraken'  si BTC  < btc_fixed_seller
        - None      en otro caso
        Todo en Decimal, sin floats.
        """
        from decimal import Decimal, InvalidOperation

        def _dec(x, default=None):
            try:
                return x if isinstance(x, Decimal) else Decimal(str(x))
            except (InvalidOperation, TypeError, ValueError):
                return default

        # Valores “cocinados” por el bot
        usdt   = _dec(getattr(self, "usdt", 0), Decimal("0"))
        btc    = _dec(getattr(self, "btc", 0),  Decimal("0"))
        fixed  = _dec(getattr(self, "fixed_buyer", 0), None)  # USDT necesarios para una compra
        btc_need = getattr(self, "btc_fixed_seller", None)     # BTC necesarios p/ vender un fixed_buyer

        # Guard-rails: si no hay fixed_buyer válido, apagamos todo
        if fixed is None:
            self.hist_tentacles = None
            return

        # 1) Eldritch: sin USDT suficientes
        if usdt is None or usdt <= 0 or usdt < fixed:
            self.hist_tentacles = "eldritch"
            return

        # 2) Kraken: sin BTC suficientes (para cubrir una venta de tamaño fixed_buyer)
        if (btc_need is not None) and (btc is not None) and (btc < btc_need):
            self.hist_tentacles = "kraken"
            return

        # 3) Nada
        self.hist_tentacles = None

    def variacion_total(self) -> Decimal:
        """
        % de variación sobre la inversión inicial (baseline según modo).
        Si no hay precio_actual válido o baseline es cero, devolvemos 0.
        """
        try:
            # Baseline correcto según modo (libre / dum)
            inv = self.get_baseline_usdt()
            if inv <= 0:
                return Decimal("0")

            # Necesitamos precio para valorar BTC
            if self.precio_actual is None:
                return Decimal("0")

            usdt = self.usdt if isinstance(self.usdt, Decimal) else Decimal(str(self.usdt or "0"))
            btc  = self.btc  if isinstance(self.btc, Decimal)  else Decimal(str(self.btc or "0"))
            precio = self.precio_actual if isinstance(self.precio_actual, Decimal) else Decimal(str(self.precio_actual))

            if precio <= 0:
                return Decimal("0")

            actual = usdt + (btc * precio)

            delta = (actual - inv) * Decimal("100") / inv
            return delta if delta != 0 else Decimal("0")

        except (InvalidOperation, DivisionByZero, TypeError, ValueError):
            return Decimal("0")

    
    def variacion_total_usdt(self) -> Decimal:
        try:
            inv = self.get_baseline_usdt()
            if inv <= 0:
                return Decimal("0")

            actual = self.usdt_mas_btc or Decimal("0")
            return actual - inv


        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0")


    def condiciones_para_comprar(self) -> bool:
        try:
            if any(x is None for x in [self.fixed_buyer, self.usdt, self.precio_actual]):
                return False
            if self.fixed_buyer <= Decimal('0'):
                return False
            if self.usdt < self.fixed_buyer:
                return False

            # ✅ convertir precio con str para evitar float binary issues
            fb = self.fixed_buyer if isinstance(self.fixed_buyer, Decimal) else Decimal(str(self.fixed_buyer))
            u  = self.usdt if isinstance(self.usdt, Decimal) else Decimal(str(self.usdt))
            p  = self.precio_actual if isinstance(self.precio_actual, Decimal) else Decimal(str(self.precio_actual))

            if p <= 0:
                return False

            return True

        except Exception as e:
            self.log(f"❌ Error en condiciones_para_comprar: {e}")
            return False


    def hold_usdt(self) -> Decimal:
        """
        Valor 'guía HODL' expresado en USDT.
        Aplica la comisión solo en la compra (como si hubieras comprado pagando fee).
        """
        try:
            if not self.running:
                return Decimal("0")
            
            if not self.precio_ingreso or not self.precio_actual or not self.inv_inic:
                return Decimal("0")

            inv = self.get_baseline_usdt()
            px_in = self.precio_ingreso if isinstance(self.precio_ingreso, Decimal) else Decimal(str(self.precio_ingreso))
            px_now = self.precio_actual if isinstance(self.precio_actual, Decimal) else Decimal(str(self.precio_actual))

            if inv <= 0 or px_in <= 0 or px_now <= 0:
                return Decimal("0")

            # ✅ Solo comisión de compra (BTC recibido menor)
            if self.comisiones_enabled and (self.comision_pct or Decimal("0")) > 0:
                buy_factor = (Decimal("100") - self.comision_pct) / Decimal("100")
            else:
                buy_factor = Decimal("1")

            btc_hold = (inv / px_in) * buy_factor
            return btc_hold * px_now

        except (InvalidOperation, ZeroDivisionError, TypeError, ValueError):
            return Decimal("0")



    def hold_btc(self) -> Decimal:
        """
        Devuelve cuánto BTC habrías comprado con la inversión baseline
        al precio de ingreso, aplicando solo la comisión de compra.
        """
        try:
            if not self.precio_ingreso:
                return Decimal("0")

            inv = self.get_baseline_usdt()
            if inv <= 0:
                return Decimal("0")

            precio = (
                self.precio_ingreso
                if isinstance(self.precio_ingreso, Decimal)
                else Decimal(str(self.precio_ingreso))
            )

            if precio <= 0:
                return Decimal("0")

            if self.comisiones_enabled and (self.comision_pct or Decimal("0")) > 0:
                buy_factor = (Decimal("100") - self.comision_pct) / Decimal("100")
            else:
                buy_factor = Decimal("1")

            return (inv / precio) * buy_factor

        except (InvalidOperation, ZeroDivisionError, TypeError, ValueError) as e:
            self.log(f"❌ Error en hold_btc: {e}")
            return Decimal("0")


    def diff_vs_hold_usdt(self) -> Decimal:
        """
        Diferencia en USDT entre:
        - tu balance actual (USDT + BTC valorado en USDT)
        - y el HODL teórico (hold_usdt_var).

        > 0 => Khazâd rinde mejor que el HODL.
        < 0 => rinde peor que el HODL.
        """
        try:
            # Nos aseguramos de que los balances estén actualizados
            self.actualizar_balance()

            # Aseguramos que la guía esté calculada
            if getattr(self, "hold_usdt_var", None) is None:
                self.hold_usdt_var = self.hold_usdt()

            hodl = self.hold_usdt_var or Decimal("0")
            total = self.usdt_mas_btc or Decimal("0")

            return total - hodl

        except (InvalidOperation, TypeError, ValueError):
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
        else:
            self.log("No cumple las condiciones para comprar")

    def iniciar(self):
        # Siempre requerimos precio real para iniciar
        self.precio_actual = self._fetch_precio()
        if self.precio_actual is None:
            self.log("🌑 Sin conexión / sin precio. No se puede iniciar.")
            self.log("- - - - - - - - - -")
            return

        # ✅ 1) Normalizar USDT antes de capturar baseline
        try:
            self.usdt = self.usdt if isinstance(self.usdt, Decimal) else Decimal(str(self.usdt or "0"))
        except (InvalidOperation, TypeError, ValueError):
            self.usdt = Decimal("0")

        # ✅ 2) Baseline según modo_app (libre vs dum)
        if getattr(self, "modo_app", "libre") == "dum":
            if self.inv_inic_dum_usdt is None:
                self.inv_inic_dum_usdt = self.usdt
            self.inv_inic = self.inv_inic_dum_usdt
        else:
            if self.inv_inic_libre_usdt is None:
                self.inv_inic_libre_usdt = self.usdt
            self.inv_inic = self.inv_inic_libre_usdt

        # ✅ 3) Recién ahora recalcular tamaño fijo por compra
        self.fixed_buyer = self.cant_inv()
        self.update_btc_fixed_seller()

        if self.condiciones_para_comprar():
            #self.log(f"🧪 Init check: precio_actual={self.precio_actual}, fixed_buyer={self.fixed_buyer}, usdt={self.usdt}")

            self.precio_ingreso = self.precio_actual
            self.precio_ult_comp = self.precio_actual
            self.start_time = datetime.datetime.now()
            self._stop_flag = False
            self.running = True
            self.sin_conexion = False
            self.log("🟡 Khazâd iniciado.")
            self.log("- - - - - - - - - -")
            self.hold_usdt_var = self.hold_usdt()
            self.hold_btc_var = self.hold_btc()
            self.realizar_primera_compra()
            
            # --- Log comisión guía (solo en compra inicial) ---
            if self.comisiones_enabled and (self.comision_pct or Decimal("0")) > 0:
                # 💡 hold_usdt_var ya es el HODL con comisión aplicada
                # La "comisión guía" (en USDT) es la diferencia frente a no tener fee
                self.log("- - - - - - - - - -")
                comision_guia = self.inv_inic - self.hold_usdt_var
                self.log("Compra Hodl hipotética:")
                self.log(f" ---- En Usdt: {self.format_fn(self.hold_usdt_var, '$')}")
                self.log(f" ---- Satoshys: {self.format_fn(self.hold_btc_var, '₿')}")
                self.log(
                    f"💠 Comisión guía Hodl: \n"
                    f" ---- (-{self.format_fn(comision_guia, '$')})\n"
                    f" ---- (-{self.format_fn(self.comision_pct, '%')})"
                )
    
            self.log("- - - - - - - - - -")

        else:
            self.log("No se puede iniciar por montos invalidos")    
            return
        
    def get_start_time_str(self) -> str | None:   
        if not self.start_time:
            return None
        return self.start_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_runtime_str(self) -> str | None:
        """
        Devuelve una cadena tipo 'Xd Yh Zm' con
        días, horas y minutos transcurridos desde start_time.
        """
        if not self.start_time:
            return None
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

            # --- precio: siempre requerido para operar ---
            nuevo_precio = self._fetch_precio()

            if nuevo_precio is None:
                # Pausa sin detener: no operar hasta que vuelva el precio
                if not self.sin_conexion:
                    self.sin_conexion = True
                    self.log("🌑 Sin conexión / sin precio. Pausando operaciones hasta que vuelva.")
                    self.log("- - - - - - - - - -")
                return  # el finally reprograma el loop

            # Volvió el precio: reanudamos
            if self.sin_conexion:
                self.sin_conexion = False
                self.log("✨ Conexión restaurada. Reanudando operaciones.")
                self.log("- - - - - - - - - -")

            self.precio_actual = nuevo_precio

            # ✅ a partir de acá: lógica común (Dum y Standard)
            self.update_btc_fixed_seller()

            if self.precio_ult_comp is None:
                self.varCompra = Decimal("0")
            else:
                self.varCompra = self.varpor_compra(self.precio_ult_comp, self.precio_actual)

            if self.precio_ult_venta is None:
                self.varVenta = Decimal("0")
            else:
                self.varVenta = self.varpor_venta(self.precio_ult_venta, self.precio_actual)

            self.actualizar_balance()
            # DEV
            self._dev_tick += 1
            if self.dev_mode and (self._dev_tick % self.dev_every == 0):
                self.dev(
                    f"px={self.format_fn(self.precio_actual,'$')} | "
                    f"usdt={self.format_fn(self.usdt,'$')} | btc={self.format_fn(self.btc,'₿')} | "
                    f"total={self.format_fn(self.usdt_mas_btc,'$')} | "
                    f"tx={len(self.transacciones)} | "
                    f"ghost(C/V)={self.contador_compras_fantasma}/{self.contador_ventas_fantasma}",
                    tag="SNAP"
                )
            self._audit_state("LOOP")
            #DEV
            self.hold_btc_var = self.hold_btc()
            self.hold_usdt_var = self.hold_usdt()
            self.var_total = self.variacion_total()
            self.var_total_usdt = self.variacion_total_usdt()

            # Check global TP/SL
            if self.check_take_profit_stop_loss():
                return

            self.vender()
            self.parametro_compra_desde_compra = self.parametro_compra_A()
            self.parametro_compra_desde_venta = self.parametro_compra_B()
            self.parametro_venta_fantasma = self.venta_fantasma()
            self.parametro_compra_desde_venta_fantasma = self.parametro_compra_C()
            

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
            self._dev_exc("loop", e)
            if self.sound_enabled:
                reproducir_sonido("Sounds/error.wav")
        

        finally:
            if after_fn and self.running and not self._stop_flag:
                self._after_fn = after_fn
                # cancelar el anterior si existía (por seguridad)
                try:
                    if self._after_id is not None:
                        after_fn.__self__.after_cancel(self._after_id)  # si after_fn es root.after
                except Exception:
                    pass
                self._after_id = after_fn(2000, lambda: self.loop(after_fn))

                
    def comprar_en_precio(self, precio_exec: Decimal, trigger="C") -> bool:
        """
        Compra usando un precio fijo (precio_vta_fantasma), para que C sea exacto.
        NO usa self.precio_actual para el cálculo del BTC comprado.
        Devuelve True si compró, False si no.
        """
        if not self.running or self._stop_flag:
            return False

        if precio_exec is None:
            return False

        try:
            precio_exec = precio_exec if isinstance(precio_exec, Decimal) else Decimal(str(precio_exec))
        except (InvalidOperation, TypeError, ValueError):
            return False

        if precio_exec <= 0:
            return False

        # ✅ si no hay fondos/condiciones, no compra
        if self.fixed_buyer is None or self.usdt is None:
            return False
        if self.fixed_buyer <= Decimal("0"):
            return False
        if self.usdt < self.fixed_buyer:
            return False

        # --- ejecutar compra usando precio_exec ---
        id_op = self._new_id()
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.usdt -= self.fixed_buyer
        self.precio_ult_comp = precio_exec
        self.btc_comprado = self.fixed_buyer / precio_exec

        # Comisión de compra (en BTC)
        comision_btc = Decimal("0")
        fee_buy_usdt = Decimal("0")
        if self.comisiones_enabled and (self.comision_pct or Decimal("0")) > 0:
            comision_btc = (self.btc_comprado * self.comision_pct) / Decimal("100")
            self.btc_comprado -= comision_btc
            fee_buy_usdt = comision_btc * precio_exec
            self.total_fees_btc += comision_btc

        self.precio_objetivo_venta = (precio_exec * (Decimal("100") + self.porc_profit_x_venta)) / Decimal("100")
        self.btc = (self.btc or Decimal("0")) + self.btc_comprado

        self.contador_compras_reales += 1
        self.rebalance_concretado = False
        valor_compra_usdt = self.btc_comprado * precio_exec

        self.transacciones.append({
            "compra": precio_exec,
            "id": id_op,
            "venta_obj": self.precio_objetivo_venta,
            "btc": self.btc_comprado,
            "invertido_usdt": self.fixed_buyer,
            "fee_usdt": fee_buy_usdt,
            "fee_btc": comision_btc,
            "ejecutado": False,
            "numcompra": self.contador_compras_reales,
            "valor_en_usdt": valor_compra_usdt,
            "timestamp": self.timestamp,
            "estado": self.estado_compra_func(),
            "trigger": trigger,  # opcional, útil para historial
        })

        self.total_fees_buy += fee_buy_usdt

        # Actualizar balances usando precio actual (si existe) para UI,
        # pero la compra ya quedó registrada a precio_exec.
        self.actualizar_balance()
        self.update_btc_fixed_seller()

        self.log("✅ Compra realizada (precio fijo).")
        self.log(f" . Trigger: {trigger}")
        self.log(f" . Fecha y Hora: {self.timestamp}")
        self.log(f"📉 Precio de compra (fijo): {self.format_fn(precio_exec, '$')}")
        self.log(f"🪙 Btc comprado: {self.format_fn(self.btc_comprado, '₿')}")
        self.log(f"🧾 Comisión: -{self.format_fn(fee_buy_usdt, '$')}")
        if comision_btc != 0:
            self.log(f"🧾 Comisión Satoshys: -{self.format_fn(comision_btc, '₿')}")
        self.log(f"🪙 Compra id: {id_op}")
        self.log(f"🪙 Compra Num: {self.contador_compras_reales}")
        self.log(f"🎯 Objetivo de venta: {self.format_fn(self.precio_objetivo_venta, '$')}")
        self.log("- - - - - - - - - -")

        if self.sound_enabled:
            reproducir_sonido("Sounds/compra.wav")

        self.ultimo_evento = datetime.datetime.now()
        self.reportado_trabajando = False
        return True


    def parametro_compra_C(self):
        """
        Compra tras venta fantasma:
        - Solo si el usuario activó compra_en_venta_fantasma (toggle UI)
        - Solo si hay evento fantasma pendiente (flags + precio_vta_fantasma)
        - Si hay desconexión: NO compra y NO limpia flags (reintenta cuando vuelva)
        - Compra EXACTAMENTE en precio_vta_fantasma (precio fijo)
        """
        # ✅ toggle del usuario
        if not self.compra_en_venta_fantasma:
            return False

        # Debe haber evento pendiente
        if not (self.activar_compra_tras_vta_fantasma and self.venta_fantasma_ocurrida):
            return False

        # ✅ si hay desconexión o no hay precio actual, NO hacemos nada (queda pendiente)
        if getattr(self, "sin_conexion", False) or self.precio_actual is None:
            return False

        precio_exec = getattr(self, "precio_vta_fantasma", None)

        # Si no hay precio guardado, cancelamos el pendiente para no dejar animación colgada
        if precio_exec is None:
            self.log("⚠️ Parametro C: no hay precio_vta_fantasma. Cancelando pendiente.")
            self.log("- - - - - - - - - -")
            self.activar_compra_tras_vta_fantasma = False
            self.venta_fantasma_ocurrida = False
            self.precio_vta_fantasma = None
            return False

        ok = self.comprar_en_precio(precio_exec, trigger="C")

        if ok:
            # ajustar estados A/B como venías haciendo
            self.param_b_enabled = False
            self.param_a_enabled = True

            self.log("🔵 [Parametro C] Compra tras venta fantasma (precio exacto).")
            self.log("- - - - - - - - - -")

            # ✅ limpiar flags del evento (NO tocar toggle usuario)
            self.activar_compra_tras_vta_fantasma = False
            self.venta_fantasma_ocurrida = False
            self.precio_vta_fantasma = None
            return True

        # Si no compró por fondos/condiciones: cancelamos evento (si no, quedaría colgado)
        self.log("⚠️ Parametro C: fondos/condiciones insuficientes. Cancelando pendiente.")
        self.log("- - - - - - - - - -")

        # baseline coherente (opcional): ya es el ancla, lo dejamos
        self.precio_ult_venta = precio_exec
        self.param_b_enabled = True

        # ✅ limpiar flags del evento (NO tocar toggle usuario)
        self.activar_compra_tras_vta_fantasma = False
        self.venta_fantasma_ocurrida = False
        self.precio_vta_fantasma = None
        return False

    def detener(self, motivo=None):
        self.running = False
        self._stop_flag = True
       
    # cancelar loop programado
        try:
            if self._after_fn and self._after_id:
                self._after_fn.__self__.after_cancel(self._after_id)
        except Exception:
            pass
        self._after_id = None
        
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

        if self.contador_compras_reales == 0:
            return False

        if self.tp_enabled and self.take_profit_pct and variacion >= self.take_profit_pct:
            self.log(f"🎯 Take Profit alcanzado: {self.format_fn(variacion, '%')}")
            ok = self.liquidar_todo(motivo="TP")
            if ok:
                self.detener(motivo="TP")
                return True
            return False


        if self.sl_enabled and self.stop_loss_pct and variacion <= -self.stop_loss_pct:
            self.log(f"🎯 Stop Loss alcanzado: {self.format_fn(variacion, '%')}")
            ok = self.liquidar_todo(motivo="SL")
            if ok:
                self.detener(motivo="SL")
                return True
            return False



    def dum_depositar_obsidiana(self, monto) -> bool:
        """
        DUM: deposita obsidiana en cualquier momento durante la run.
        - Se SUMA (no setea).
        - El bot SOLO puede operar con hasta dum_cap (5000) dentro de self.usdt.
        - El excedente se guarda en dum_extra_obsidiana para devolver al cerrar.
        """
        try:
            if getattr(self, "modo_app", "libre") != "dum":
                return False

            try:
                m = parse_decimal_user(monto)
            except Exception:
                self.log(f"⚠️ DUM depósito inválido: {monto!r}")
                return False


            if m <= 0:
                return False

            with self.lock:
                # marcar run activa (si querés que empiece al primer depósito)
                self.dum_run_abierta = True

                self.dum_deposit_total = (self.dum_deposit_total or Decimal("0")) + m

                # llenar slot operativo hasta el cap
                cap = self.dum_cap or Decimal("5000")
                usdt_actual = self.usdt if isinstance(self.usdt, Decimal) else Decimal(str(self.usdt or "0"))

                espacio = cap - usdt_actual
                al_slot = Decimal("0")   # 👈 SIEMPRE existe

                if espacio <= 0:
                    # todo va a excedente
                    self.dum_extra_obsidiana = (self.dum_extra_obsidiana or Decimal("0")) + m
                else:
                    al_slot = m if m <= espacio else espacio
                    exced = m - al_slot

                    self.usdt = usdt_actual + al_slot
                    if exced > 0:
                        self.dum_extra_obsidiana = (self.dum_extra_obsidiana or Decimal("0")) + exced

                # recalcular tamaño fijo / métricas
                self.fixed_buyer = self.cant_inv()
                self.update_btc_fixed_seller()
                self.actualizar_balance()
                # ✅ baseline DUM: acumula SOLO lo que entra al slot operativo (al_slot)
                if self.inv_inic_dum_usdt is None:
                    self.inv_inic_dum_usdt = Decimal("0")

                # 'al_slot' es lo que efectivamente entró a self.usdt (operable)
                # (si todo fue a excedente, al_slot será 0)
                self.inv_inic_dum_usdt += al_slot

                # compatibilidad: inv_inic siempre refleja el baseline activo del modo
                self.inv_inic = self.inv_inic_dum_usdt


            self.log(
                f"🟪 DUM: depósito aplicado.\n"
                f" · Operando con: {self.format_fn(self.usdt, '$')}\n"
                f" · Excedente: {self.format_fn(self.dum_extra_obsidiana, '$')}\n"
                f" · Total depositado: {self.format_fn(self.dum_deposit_total, '$')}"
            )
            self.log("- - - - - - - - - -")
            return True

        except (InvalidOperation, TypeError, ValueError):
            return False


    def dum_equity_total(self) -> Decimal:
        try:
            self.actualizar_balance()
            extra = self.dum_extra_obsidiana or Decimal("0")
            return (self.usdt_mas_btc or Decimal("0")) + extra
        except Exception:
            return Decimal("0")

    def dum_variacion_total_user(self) -> Decimal:
        try:
            base = (self.inv_inic_dum_usdt or Decimal("0")) + (self.dum_extra_obsidiana or Decimal("0"))
            if base <= 0:
                return Decimal("0")
            total = self.dum_equity_total()
            return (total - base) * Decimal("100") / base
        except Exception:
            return Decimal("0")
        


