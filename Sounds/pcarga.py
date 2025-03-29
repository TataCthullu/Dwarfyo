import tkinter as tk
from PIL import Image, ImageTk
import threading
import pygame
import interfaz  # Este debe ser tu archivo principal de interfaz, sin .py

pygame.mixer.init()

def reproducir_sonido(ruta):
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play()

def iniciar_programa():
    splash.destroy()
    threading.Thread(target=interfaz.lanzar_interfaz, daemon=True).start()

# Splash screen
splash = tk.Tk()
splash.overrideredirect(True)
splash.geometry("1200x700")

try:
    pilimagen = Image.open("imagenes/khazadcarga.png")
    pilimagen = pilimagen.resize((500, 500))
    logo_img = ImageTk.PhotoImage(pilimagen)

    label_logo = tk.Label(splash, image=logo_img)
    label_logo.image = logo_img
    label_logo.pack(pady=20)
except Exception as e:
    print("No se pudo cargar la imagen del logo:", e)

# Texto adicional
texto = tk.Label(splash, text="Iniciando Khazâd...", font=("Arial", 16), bg="black", fg="white")
texto.pack()

# Sonido (opcional)
reproducir_sonido("Sounds/soundinicio.wav")

# Espera y abre la interfaz principal
splash.after(3000, iniciar_programa)
splash.mainloop()
