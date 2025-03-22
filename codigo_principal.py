import ccxt  # Importamos la librería para conectarnos a Binance
import time

# Crear una instancia del exchange Binance
exchange = ccxt.binance()

# Definimos colores para mejor lectura en consola
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Definimos nuestras variables madre
usdt = 0
pdiff = 0
pdiff_ult = 0
btc = 0
btcusdt = 0
ticker = exchange.fetch_ticker('BTC/USDT')
precio_act_btc = ticker['last']
usdt_mas_btc = 0
precio_ult_comp = precio_act_btc
precio_ult_venta = precio_act_btc
precios_compras = []
precios_ventas = []
porc_por_compra = 0.007
porc_por_venta= 0.007
porc_inv_por_compra = 10
kant_usdt_vendido = 0
btc_comprado = 0

#Inicia el programa
print(bcolors.WARNING + "\n... INICIANDO PROGRAMA ...\n" + bcolors.ENDC)

#Variacion de precio con respecto a ultima compra
def varpor_compra(precio_ult_comp, precio_act_btc):
        if precio_ult_comp == 0:
             raise ValueError("la ultima compra no puede ser 0")
        else:
            variante = ((precio_act_btc - precio_ult_comp) / precio_ult_comp) * 100
            return variante 

varporCompra = varpor_compra(precio_ult_comp, precio_act_btc) 


#Variacion desde ultima venta 
def varpor_venta(precio_ult_venta, precio_act_btc):
    if precio_ult_venta == 0:
         raise ValueError("la última venta no puede ser 0")
    else:
         variante = ((precio_act_btc - precio_ult_venta) / precio_ult_venta) * 100
         return variante

varporVenta = varpor_venta (precio_ult_venta, precio_act_btc) 

#Cantidad invertida
def cant_inv(usdt, porc_inv_por_compra):
        total = (usdt * porc_inv_por_compra) / 100
        return total   

#Valor fijo
fixed_buyer = cant_inv (usdt, porc_inv_por_compra)
print("Cantidad fija a invertir por compra: ", fixed_buyer)


#Cantidad de veces que puede comprar en el rango de variacion del precio
"""multiple_porc = varpor(precio_ult_comp, precio_act_btc) // porc_por_compra

if multiple_porc >= 0:
    print("Veces q podria comprar: ", multiple_porc)
else:
    print("Veces q podria comprar: ", 0)"""

print(bcolors.WARNING + "\n... PRIMERA COMPRA ...\n" + bcolors.OKGREEN)
usdt -= fixed_buyer 
btcusdt += (((1/precio_act_btc) * (fixed_buyer)) * precio_act_btc)
precios_compras.append(precio_ult_comp)
precio_ult_comp = precio_act_btc
btc_comprado = (1/precio_act_btc) * (fixed_buyer)
btc = btc_comprado
usdt_mas_btc = usdt + (btc * precio_act_btc)

#PRINTS
time.sleep(1)
print("Precios de compra: USDT: $", precios_compras)        
print("BTC comprado: ", btc_comprado) 
print("BTC comprado representado en USDT: $", (fixed_buyer))         

print(bcolors.WARNING + "\n... INICIANDO BUCLE ...\n" + bcolors.ENDC)

#INICIA EL BUCLE
while True:
    time.sleep(3)
    ticker = exchange.fetch_ticker('BTC/USDT')
    precio_act_btc = ticker['last']
    varporCompra = varpor_compra(precio_ult_comp, precio_act_btc)
    varporVenta = varpor_venta(precio_ult_venta, precio_act_btc) 
    usdt_mas_btc = usdt + (btc * precio_act_btc)
    
    # Calcular promedios
    promedio_compra = sum(precios_compras) / len(precios_compras) if precios_compras else 0
    promedio_venta = sum(precios_ventas) / len(precios_ventas) if precios_ventas else 0
    time.sleep(10)
    print(bcolors.HEADER + "\n- - - - - - - - - - - ")
    print("Valor BTC actual en UDST: ", precio_act_btc)
    print("Valor de la ultima compra en USDT: ", precio_ult_comp)
    print(f"Porcentaje de variación del precio desde ultima compra, contra el actual: ({varporCompra:.3f}){bcolors.ENDC}")
    print(f"Porcentaje de variación del precio desde ultima venta, contra el actual: ({varporVenta:.3f}){bcolors.ENDC}")
    print(f"{bcolors.FAIL}EL PORCENTAJE NO ES SUFICIENTE PARA TRADEAR.{bcolors.ENDC}")
    print(bcolors.BOLD + "\n---- BALANCE ACTUAL ----" + bcolors.ENDC)      
    print(f"- USDT: ${usdt:.2f}")
    print(f"- Profit neto: ${pdiff:.2f}")
    print(f"- BTC: {btc} (USDT ${btc * precio_act_btc:.2f})")
    print(f"- BTC + USDT, en USDT: ${usdt_mas_btc:.2f}")
    if usdt < fixed_buyer:
            print("Inversión agotada")
    
    """# Comparar los promedios
    if promedio_venta > promedio_compra:
        print(f"{bcolors.OKGREEN}Histórico favorable : Compraste por ultima vez a un promedio de {promedio_compra:.2f} y vendiste a {promedio_venta:.2f}, obteniendo: ",pdiff_ult, ", sumando un total de ganancia acumulada de: $",pdiff, {bcolors.ENDC})
    else:
        continue
    print(bcolors.HEADER + "- - - - - - - - - - - " + bcolors.ENDC)"""
   
#Logica de compra
    if (varporVenta <= -porc_por_compra) and usdt >= fixed_buyer: 
        print(f"{bcolors.OKCYAN}PORCENTAJE HABILITA A COMPRAR. ({varporVenta:.3f}){bcolors.ENDC}")
        usdt -= fixed_buyer
        btcusdt += ((1/precio_act_btc) * fixed_buyer) * precio_act_btc
        precio_ult_comp = precio_act_btc
        precios_compras.append(precio_ult_comp)
        btc_comprado = (1/precio_act_btc) * fixed_buyer
        btc += btc_comprado 
        usdt_mas_btc = usdt + (btc * precio_act_btc)
        
        time.sleep(1)
        print("Precios de compra: USDT: $", precios_compras)
        time.sleep(0.5)        
        print("BTC comprado: ", (1/precio_act_btc) * fixed_buyer) 
        print("BTC comprado representado en USDT: $", fixed_buyer)  
          
#Logica de venta
    if varporCompra >= porc_por_compra and btc >= btc_comprado: 
        precio_ult_venta = precio_act_btc
        print(f"{bcolors.OKCYAN}EL PORCENTAJE HABILITA A VENDER. ({varporCompra:.3f}){bcolors.ENDC}")
        kant_usdt_vendido = btc_comprado * precio_act_btc
        pdiff_ult = kant_usdt_vendido - fixed_buyer
        usdt += kant_usdt_vendido
        btc -= btc_comprado
        btcusdt -= ((1/precio_ult_comp) * fixed_buyer) * precio_act_btc
        precio_ult_comp = precio_act_btc
        precios_ventas.append(precio_ult_venta)
        usdt_mas_btc = usdt + (btc * precio_act_btc)
        
        print("Profit diferencial de la ultima venta: ", pdiff_ult) 
        print("Profit diferencial total: ", pdiff)
        time.sleep(1)
        print("Precios de venta: USDT$", precios_ventas)
        time.sleep(0.5)   
        print("BTC vendido: ", btc_comprado)   
        print("BTC vendido representado en USDT: $", kant_usdt_vendido)                            
        
        if btc < btc_comprado:
            print(bcolors.FAIL + "No hay suficiente BTC para vender." + bcolors.ENDC)
            

                               
    
