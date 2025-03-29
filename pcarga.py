# main.py

import tkinter as tk
from PIL import Image, ImageTk
import pygame
import interfaz

pygame.mixer.init()

def reproducir_sonido(ruta):
    try:
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.play()
    except Exception as e:
        print("No se pudo reproducir el sonido:", e)

# Splash screen
splash = tk.Tk()
splash.withdraw()  # Oculta la ventana inicialmente
splash.overrideredirect(True)
splash.configure(bg="black")
splash.deiconify()  # Muestra la ventana solo cuando está lista

# Tamaño fijo y centrado
screen_width = splash.winfo_screenwidth()
screen_height = splash.winfo_screenheight()
width, height = 600, 600
x = (screen_width // 2) - (width // 2)
y = (screen_height // 2) - (height // 2)
splash.geometry(f"{width}x{height}+{x}+{y}")

# Cargar imagen PIL (no PhotoImage aún)
try:
    pilimagen = Image.open("imagenes/khazadcarga.png")
    pilimagen = pilimagen.resize((400, 400))  # Ajustar tamaño
except Exception as e:
    print("No se pudo cargar la imagen del logo:", e)
    pilimagen = None
except Exception as e:
    print("No se pudo cargar la imagen del logo:", e)

# Texto adicional
logo_img = None  # Referencia global para que la imagen no se destruya
def splash.after(0, mostrar_logo):
    global logo_img
    if pilimagen:
        logo_img = ImageTk.PhotoImage(pilimagen)
        label_logo = tk.Label(splash, image=logo_img, bg="black")
        label_logo.image = logo_img  # Mantiene viva la imagen
        label_logo.pack(pady=20, expand=True)
        texto = tk.Label(splash, text="Iniciando Khazâd...", font=("Arial", 16), bg="black", fg="white")
        texto.pack(pady=10)

mostrar_logo()

# Sonido (opcional)
reproducir_sonido("Sounds/soundinicio.wav")

# Mostrar splash y luego lanzar interfaz
def cerrar_splash():
    splash.after(100, interfaz.pcarga)
    splash.destroy()

# Ahora se programa el cierre solo tras mostrar el logo
splash.after(3000, cerrar_splash)
splash.mainloop()
