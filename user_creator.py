import tkinter as tk

user_win = tk.Tk()
user_win.geometry("400x200")
user_win.title("Creacion De Usuario - Dungeon Market")
user_win.config(background="PaleGoldenRod")

user_win_laba = tk.Label(user_win, text="Saludos!", font=("Carolingia", 18), background="PaleGoldenRod")
user_win_laba.pack(anchor="center", pady=10)

nombre_lab = tk.Label(user_win, text="Nombre: ", font=("Carolingia", 18), background="PaleGoldenRod")
nombre_lab.pack(anchor="w")

nombre_entry = tk.Entry(user_win)
nombre_entry.pack(anchor="w")

pass_lab = tk.Label(user_win, text="Contraseña: ", font=("Carolingia", 18), background="PaleGoldenRod")
pass_lab.pack(anchor="w")

pass_entry = tk.Entry(user_win)
pass_entry.pack(anchor="w")

btn_crear_pj = tk.Button(user_win, text="Crear", font=("Carolingia", 18))
btn_crear_pj.pack(pady=10)

user_win.mainloop()