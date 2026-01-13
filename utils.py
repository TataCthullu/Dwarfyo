# © 2025 Dungeon Market (utils) 
# Todos los derechos reservados.

import pygame
from decimal import Decimal, InvalidOperation
pygame.mixer.init()

# canal 0 reservado para música de fondo
pygame.mixer.set_num_channels(8)  # por si quieres varios
canal_musica = pygame.mixer.Channel(0)

def reproducir_sonido(ruta):
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play()

def detener_sonido_y_cerrar(ventana):
            pygame.mixer.music.stop()
            ventana.destroy()    

def reproducir_musica_fondo(ruta, loop=-1, volumen=0.3):
    """Reproduce una pista en bucle en el canal 0 sin cortar otros sonidos."""
    try:
        snd = pygame.mixer.Sound(ruta)
        canal_musica.play(snd, loops=loop)
        canal_musica.set_volume(volumen)
    except Exception as e:
        print(f"[ERROR musica fondo] {e}")

def detener_musica_fondo():
    canal_musica.stop()


def parse_decimal_user(texto) -> Decimal:
    """
    Convierte strings tipo:
    '3000' / '3000,5' / '3.000,5' / '3,000.5'
    a Decimal válido.
    """
    if texto is None:
        raise InvalidOperation("None")

    if isinstance(texto, Decimal):
        return texto

    s = str(texto).strip()
    if not s:
        raise InvalidOperation("empty")

    # Caso 1: tiene coma y punto -> uno es miles y el otro decimal
    if "," in s and "." in s:
        # Si el último separador es coma => coma es decimal, puntos son miles: 3.000,5
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "")
            s = s.replace(",", ".")
        # Si el último separador es punto => punto es decimal, comas son miles: 3,000.5
        else:
            s = s.replace(",", "")

    # Caso 2: solo coma -> coma decimal: 3000,5
    elif "," in s:
        s = s.replace(",", ".")

    # Caso 3: solo punto -> ya sirve (3000.5 o 3000)
    # (no hacemos nada)

    return Decimal(s)
