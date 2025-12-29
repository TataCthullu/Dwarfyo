# player.py
import os
from PIL import Image, ImageTk
from database import cargar_perfil, guardar_perfil

AVATAR_DIR = os.path.join("imagenes", "deco", "Player", "AvatarBase")

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
