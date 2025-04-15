import pygame
pygame.mixer.init()


def reproducir_sonido(ruta):
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play()

def detener_sonido_y_cerrar(ventana):
            pygame.mixer.music.stop()
            ventana.destroy()    