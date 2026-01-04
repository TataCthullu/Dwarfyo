# © 2025 Dungeon Market (utils) 
# Todos los derechos reservados.

import pygame
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