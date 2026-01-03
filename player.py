# player.py
import os
import tkinter as tk
from decimal import Decimal
from PIL import Image, ImageTk

from database import (
    cargar_perfil,
    guardar_perfil,
    init_wallet,
    get_wallet,
    set_wallet,
)

from dum import SLOT_1_OBSIDIANA


AVATAR_DIR = os.path.join("imagenes", "deco", "Player", "AvatarBase")


# =========================
# Avatar helpers (limpios)
# =========================

def listar_avatares():
    if not os.path.isdir(AVATAR_DIR):
        return []
    files = []
    for fn in os.listdir(AVATAR_DIR):
        if fn.lower().endswith((".png", ".jpg", ".jpeg")):
            files.append(os.path.join(AVATAR_DIR, fn))
    files.sort()
    return files


def avatar_name_from_path(path):
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    return name


def load_avatar_thumbnail(path, size=(64, 64)):
    try:
        img = Image.open(path)
        img = img.resize(size, resample=Image.Resampling.NEAREST)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


def get_avatar(usuario):
    perfil = cargar_perfil(usuario)
    if not isinstance(perfil, dict):
        perfil = {}
    return (perfil.get("avatar", {}) or {})


def set_avatar(usuario, name, img_path):
    perfil = cargar_perfil(usuario)
    if not isinstance(perfil, dict):
        perfil = {}
    perfil["avatar"] = {"name": name, "img": img_path}
    guardar_perfil(usuario, perfil)


def crear_avatar(usuario, canvas_menu, avatar_text_id, avatar_img_id, btn_crear_avatar):
    """
    Mantengo el nombre 'crear_avatar' para que no tengas que cambiar
    demasiado tu loggin.py. No depende de ventana_loggin.
    """
    # abrimos sobre el toplevel del canvas
    parent = canvas_menu.winfo_toplevel()
    avatar_win = tk.Toplevel(parent)
    avatar_win.title("Elegir Avatar")
    avatar_win.configure(background="PaleGoldenRod")

    paths = listar_avatares()
    if not paths:
        lab = tk.Label(avatar_win, text=f"No hay avatares en:\n{AVATAR_DIR}", bg="PaleGoldenRod")
        lab.pack(padx=10, pady=10)
        return

    lab_nombre = tk.Label(avatar_win, text="Nombre del avatar:", bg="PaleGoldenRod", font=("Carolingia", 12))
    lab_nombre.pack(padx=10, pady=(10, 0), anchor="w")

    nombre_var = tk.StringVar()
    entry_nombre = tk.Entry(avatar_win, textvariable=nombre_var)
    entry_nombre.pack(padx=10, pady=(0, 10), anchor="w")
    entry_nombre.focus_force()

    frame = tk.Frame(avatar_win, bg="PaleGoldenRod")
    frame.pack(padx=10, pady=10)

    avatar_win.thumbs = []
    avatar_win.avatar_buttons = []

    def _update_buttons_state(*_):
        ok = bool(nombre_var.get().strip())
        state = "normal" if ok else "disabled"
        for b in avatar_win.avatar_buttons:
            try:
                b.configure(state=state)
            except Exception:
                pass

    nombre_var.trace_add("write", _update_buttons_state)

    def _select(path):
        nombre_avatar = nombre_var.get().strip()
        if not nombre_avatar:
            return

        set_avatar(usuario, nombre_avatar, path)

        canvas_menu.itemconfig(avatar_text_id, text=nombre_avatar)

        ph = load_avatar_thumbnail(path, size=(64, 64))
        if ph:
            canvas_menu.avatar_photo = ph
            canvas_menu.itemconfig(avatar_img_id, image=ph)

        try:
            btn_crear_avatar.destroy()
        except Exception:
            pass

        avatar_win.destroy()

    cols = 4
    r = c = 0
    for p in paths:
        thumb = load_avatar_thumbnail(p, size=(64, 64))
        if not thumb:
            continue

        avatar_win.thumbs.append(thumb)
        name = avatar_name_from_path(p)

        b = tk.Button(
            frame,
            image=thumb,
            text=name,
            compound="top",
            command=lambda pp=p: _select(pp),
            state="disabled"
        )
        b.grid(row=r, column=c, padx=6, pady=6)
        avatar_win.avatar_buttons.append(b)

        c += 1
        if c >= cols:
            c = 0
            r += 1

    _update_buttons_state()


# =========================
# Dum helpers / Player HUD
# =========================

def depositar_a_bot(usuario: str, bot):
    """
    Lógica de player (Dum): toma del wallet y carga al bot.
    """
    obs, quad = get_wallet(usuario)

    # Normalizar
    try:
        obs = Decimal(str(obs))
    except Exception:
        obs = Decimal("0")
    try:
        quad = Decimal(str(quad))
    except Exception:
        quad = Decimal("0")

    if obs < 0:
        obs = Decimal("0")

    deposito = min(obs, SLOT_1_OBSIDIANA)

    # retirar del wallet (queda "bloqueado" en la run)
    set_wallet(usuario, obs - deposito, quad)

    # cargar al bot
    bot.usdt = deposito
    bot.dum_slot_used = deposito

    return deposito


class DumWindow:
    """
    Ventana principal del jugador (por ahora solo HUD de wallet/Dum).
    """
    def __init__(self, master, usuario: str, rellenar_mosaico_fn, bg_path: str, icon_path: str = None):
        self.master = master
        self.usuario = usuario
        self.rellenar_mosaico_fn = rellenar_mosaico_fn
        self.bg_path = bg_path
        self.icon_path = icon_path

        self.win = None
        self.canvas = None
        self.wallet_text_id = None
        self.dum_text_id = None

    def open(self):
        if self.win is not None and self.win.winfo_exists():
            self.win.lift()
            self.win.focus_force()
            return

        self.win = tk.Toplevel(self.master)
        self.win.geometry("750x800")
        self.win.title("Dungeon Market - Dungeon")

        if self.icon_path:
            try:
                self.win.iconbitmap(self.icon_path)
            except Exception:
                pass

        self.canvas = tk.Canvas(self.win, width=750, height=800, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        # Fondo
        self.rellenar_mosaico_fn(self.canvas, self.bg_path, escala=2)

        # Asegurar wallet
        init_wallet(self.usuario)

        self.wallet_text_id = self.canvas.create_text(
            375, 105,
            text="Obsidiana: 0  |  Quad: 0",
            fill="Orange",
            font=("Carolingia", 14),
            anchor="center"
        )

        self.dum_text_id = self.canvas.create_text(
            375, 130,
            text="Dum · Slot cap: 0 | Depósito: 0 | Slot usado: 0",
            fill="Gold",
            font=("Carolingia", 16),
            anchor="center"
        )

        self.refresh()
        
        def _tick_refresh():
            if self.win is None or not self.win.winfo_exists():
                return
            self.refresh()
            self.win.after(1000, _tick_refresh)

        _tick_refresh()


        def _al_cerrar():
            try:
                self.win.destroy()
            except Exception:
                pass
            self.win = None

        self.win.protocol("WM_DELETE_WINDOW", _al_cerrar)

    def refresh(self):
        if self.win is None or not self.win.winfo_exists():
            return

        # wallet
        try:
            obs, quad = get_wallet(self.usuario)
            obs_d = Decimal(str(obs))
            quad_d = Decimal(str(quad))
        except Exception:
            obs_d = Decimal("0")
            quad_d = Decimal("0")

        # perfil dum
        perfil = cargar_perfil(self.usuario)
        if not isinstance(perfil, dict):
            perfil = {}
        di = (perfil.get("dum", {}) or {})

        try:
            dep = Decimal(str(di.get("deposito", "0") or "0"))
        except Exception:
            dep = Decimal("0")

        try:
            su = Decimal(str(di.get("slot_used_last", "0") or "0"))
        except Exception:
            su = Decimal("0")

        slot_cap = min(obs_d, SLOT_1_OBSIDIANA)

        self.canvas.itemconfig(self.wallet_text_id, text=f"Obsidiana: {obs_d}  |  Quad: {quad_d}")
        self.canvas.itemconfig(self.dum_text_id, text=f"Dum · Slot cap: {slot_cap} | Depósito: {dep} | Slot usado: {su}")







