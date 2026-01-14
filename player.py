# © 2025 Dungeon Market (Player)
  
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

AVATAR_DIR = os.path.join("imagenes", "deco", "Player", "AvatarBase")
SLOTS_CAP = {
    1: Decimal("5000"),
    2: Decimal("10000"),
    # futuros slots...
}

def get_dum_slot_cap(usuario: str) -> Decimal:
    perfil = cargar_perfil(usuario)  # o tu DB / dict
    slot = int(perfil.get("dum_slot", 1))
    return SLOTS_CAP.get(slot, Decimal("5000"))


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



def depositar_a_bot(usuario: str, bot, delta: Decimal, cap: Decimal):
    """
    Dum: deposita 'delta' desde wallet -> bot, respetando cap (slot).
    - Descuenta de wallet.
    - El bot decide cuánto entra al slot y cuánto queda como excedente,
      vía bot.dum_depositar_obsidiana(delta).
    - Acumula perfil["dum"]["deposito"] (depósito TOTAL de la run).
    - NO pisa bot.inv_inic ni bot.usdt manualmente.
    """
    # --- normalizar delta/cap ---
    try:
        delta = Decimal(str(delta))
    except Exception:
        delta = Decimal("0")

    if delta <= 0:
        return Decimal("0")

    try:
        cap = Decimal(str(cap or "0"))
    except Exception:
        cap = Decimal("0")

    if cap < 0:
        cap = Decimal("0")

    # --- cuánto ya hay depositado al slot (baseline dum) ---
    # OJO: con tu bot nuevo, en Dum el baseline correcto es inv_inic_dum_usdt (o inv_inic reflejando eso).
    try:
        actual = Decimal(str(getattr(bot, "inv_inic_dum_usdt", None) if getattr(bot, "modo_app", "") == "dum" else getattr(bot, "inv_inic", "0") or "0"))
    except Exception:
        actual = Decimal("0")

    if actual < 0:
        actual = Decimal("0")

    # --- no permitir superar cap ---
    max_delta = cap - actual
    if max_delta <= 0:
        return Decimal("0")

    if delta > max_delta:
        delta = max_delta

    # --- leer wallet ---
    obs, quad = get_wallet(usuario)
    try:
        obs = Decimal(str(obs))
    except Exception:
        obs = Decimal("0")
    try:
        quad = Decimal(str(quad))
    except Exception:
        quad = Decimal("0")

    if obs < delta:
        return Decimal("-1")  # señal: no alcanza

    # --- descontar wallet ---
    set_wallet(usuario, obs - delta, quad)

    # --- aplicar depósito al bot (FUENTE ÚNICA DE VERDAD) ---
    ok = False
    try:
        ok = bot.dum_depositar_obsidiana(delta)
    except Exception:
        ok = False

    if not ok:
        # rollback wallet (si el bot no pudo aplicar, devolvemos obsidiana)
        try:
            obs2, quad2 = get_wallet(usuario)
            obs2 = Decimal(str(obs2))
            quad2 = Decimal(str(quad2))
        except Exception:
            obs2 = obs - delta
            quad2 = quad
        set_wallet(usuario, obs2 + delta, quad2)

        return Decimal("0")

    # --- acumular depósito total de la run en perfil (solo tracking) ---
    perfil = cargar_perfil(usuario)
    if not isinstance(perfil, dict):
        perfil = {}

    dum = (perfil.get("dum", {}) or {})

    try:
        dep_prev = Decimal(str(dum.get("deposito", "0") or "0"))
    except Exception:
        dep_prev = Decimal("0")

    dep_new = dep_prev + delta
    dum["deposito"] = str(dep_new)

    # opcional: guardar snapshot informativo del slot actual (lo operable)
    try:
        dum["slot_used_last"] = str(Decimal(str(getattr(bot, "usdt", "0") or "0")))
    except Exception:
        dum["slot_used_last"] = "0"

    perfil["dum"] = dum
    guardar_perfil(usuario, perfil)

    # ⚠️ ojo nombre: en tu bot es dum_deposit_total (no dum_deposito_total)
    try:
        bot.dum_deposit_total = dep_new
    except Exception:
        pass

    return delta


# lock dummy para no romper si bot no tiene .lock
class dummy_lock:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): return False



def cerrar_run_dum(usuario: str, usdt_final):
    """
    Cierre Dum:
    obsidiana_devuelta = min(usdt_final, deposito_total_obs)
    quad_ganado        = max(usdt_final - deposito_total_obs, 0)
    Luego resetea dum["deposito"] y dum["slot_used_last"].
    """
    # Normalizar usdt_final
    try:
        usdt_final = Decimal(str(usdt_final))
    except Exception:
        usdt_final = Decimal("0")

    if usdt_final < 0:
        usdt_final = Decimal("0")

    # Leer depósito total acumulado de la run
    perfil = cargar_perfil(usuario)
    if not isinstance(perfil, dict):
        perfil = {}
    dum = (perfil.get("dum", {}) or {})

    try:
        deposito_total = Decimal(str(dum.get("deposito", "0") or "0"))
    except Exception:
        deposito_total = Decimal("0")

    # Fórmula Dum
    obs_devuelta = usdt_final if usdt_final <= deposito_total else deposito_total
    quad_ganado = (usdt_final - deposito_total) if usdt_final > deposito_total else Decimal("0")

    # Actualizar wallet
    obs, quad = get_wallet(usuario)
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
    if quad < 0:
        quad = Decimal("0")

    set_wallet(usuario, obs + obs_devuelta, quad + quad_ganado)

    # Reset dum perfil
    dum["deposito"] = "0"
    dum["slot_used_last"] = "0"
    perfil["dum"] = dum
    guardar_perfil(usuario, perfil)

    return obs_devuelta, quad_ganado


class DumWindow:
    """
    Ventana principal del jugador (HUD de wallet/Dum).
    """
    def __init__(
        self,
        master,
        usuario: str,
        rellenar_mosaico_fn,
        bg_path: str,
        icon_path: str = None,
        open_khazad_dum_fn=None,   # <-- NUEVO (opcional)
    ):
        self.master = master
        self.usuario = usuario
        self.rellenar_mosaico_fn = rellenar_mosaico_fn
        self.bg_path = bg_path
        self.icon_path = icon_path
        self.open_khazad_dum_fn = open_khazad_dum_fn  # <-- GUARDA callback

        self.win = None
        self.canvas = None
        
        self.dum_text_id = None
        
        self.obs_label_id = None
        self.obs_value_id = None
        self.quad_label_id = None
        self.quad_value_id = None
        
        # Avatar HUD
        self.avatar_text_id = None
        self.avatar_img_id = None
        self.btn_crear_avatar = None

    def open(self):
        if self.win is not None and self.win.winfo_exists():
            self.win.lift()
            self.win.focus_force()
            return

        self.win = tk.Toplevel(self.master)
        self.win.geometry("750x800")
        self.win.title("Dungeon Market - Dum")

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

        # Reset refs
        self.btn_crear_avatar = None

        # =========================
        # 1) Título centrado
        # =========================
        self.title_dum = self.canvas.create_text(
            375, 40,
            text="Dum",
            fill="Gold",
            font=("Carolingia", 20),
            anchor="center"
        )

        # =========================
        # 2) Wallet a la izquierda
        # =========================
        x_label = 40
        x_value = 60
        y_obs   = 95
        y_quad  = 125

        self.obs_label_id = self.canvas.create_text(
            x_label, y_obs,
            text="Obsidiana:",
            fill="Orange",
            font=("Carolingia", 14),
            anchor="w"
        )
        self.obs_value_id = self.canvas.create_text(
            x_value, y_obs,
            text="0",
            fill="Orange",
            font=("Carolingia", 14),
            anchor="w"
        )

        self.quad_label_id = self.canvas.create_text(
            x_label, y_quad,
            text="Quad:",
            fill="Gold",
            font=("Carolingia", 14),
            anchor="w"
        )
        self.quad_value_id = self.canvas.create_text(
            x_value, y_quad,
            text="0",
            fill="Gold",
            font=("Carolingia", 14),
            anchor="w"
        )

        # =========================
        # 3) Botón Khazad Dum (ANTES del avatar)
        # =========================
        self.btn_khazad_dum = None
        if callable(self.open_khazad_dum_fn):
            self.btn_khazad_dum = tk.Button(
                self.win,
                text="Khazad bot (Dum)",
                font=("Carolingia", 14),
                command=self.open_khazad_dum_fn
            )
            self.canvas.create_window(375, 250, window=self.btn_khazad_dum, anchor="center")

        # =========================
        # 4) Avatar centrado + nombre abajo + crear avatar (si falta)
        # =========================
        avatar_center_x = 375
        avatar_img_y    = 550
        avatar_name_y   = 620
        avatar_btn_y    = 650

        self.avatar_img_id = self.canvas.create_image(
            avatar_center_x, avatar_img_y,
            image="",
            anchor="center"
        )

        self.avatar_text_id = self.canvas.create_text(
            avatar_center_x, avatar_name_y,
            text="Sin avatar",
            fill="Gold",
            font=("Carolingia", 14),
            anchor="center"
        )

        av = get_avatar(self.usuario)
        av_name = (av.get("name") or "").strip()
        av_img  = (av.get("img") or "").strip()

        tiene_avatar = bool(av_name and av_img and os.path.isfile(av_img))

        if tiene_avatar:
            self.canvas.itemconfig(self.avatar_text_id, text=av_name)

            ph = load_avatar_thumbnail(av_img, size=(96, 96))
            if ph:
                self.canvas.avatar_photo = ph
                self.canvas.itemconfig(self.avatar_img_id, image=ph)

        else:
            self.btn_crear_avatar = tk.Button(
                self.win,
                text="Crear avatar",
                font=("Carolingia", 14),
                command=lambda: crear_avatar(
                    self.usuario,
                    self.canvas,
                    self.avatar_text_id,
                    self.avatar_img_id,
                    self.btn_crear_avatar
                )
            )
            self.canvas.create_window(
                avatar_center_x, avatar_btn_y,
                window=self.btn_crear_avatar,
                anchor="center"
            )

        # refresco inicial
        self.refresh()

        def _al_cerrar():
            try:
                self.win.destroy()
            except Exception:
                pass
            self.win = None
            self.canvas = None

        self.win.protocol("WM_DELETE_WINDOW", _al_cerrar)



    def refresh(self):
        if self.win is None or not self.win.winfo_exists() or self.canvas is None:
            return

        # -------------------------
        # Wallet
        # -------------------------
        try:
            obs, quad = get_wallet(self.usuario)
            obs_d = Decimal(str(obs))
            quad_d = Decimal(str(quad))
        except Exception:
            obs_d = Decimal("0")
            quad_d = Decimal("0")

        try:
            if self.obs_value_id is not None:
                self.canvas.itemconfig(self.obs_value_id, text=str(obs_d))
            if self.quad_value_id is not None:
                self.canvas.itemconfig(self.quad_value_id, text=str(quad_d))
        except Exception:
            pass

        # -------------------------
        # Avatar
        # -------------------------
        try:
            av = get_avatar(self.usuario)
            av_name = (av.get("name") or "").strip()
            av_img  = (av.get("img") or "").strip()
            tiene_avatar = bool(av_name and av_img and os.path.isfile(av_img))

            if tiene_avatar:
                if self.avatar_text_id is not None:
                    self.canvas.itemconfig(self.avatar_text_id, text=av_name)

                if self.avatar_img_id is not None:
                    ph = load_avatar_thumbnail(av_img, size=(96, 96))
                    if ph:
                        self.canvas.avatar_photo = ph
                        self.canvas.itemconfig(self.avatar_img_id, image=ph)

                # si ya tiene avatar, borrar botón crear si existía
                if getattr(self, "btn_crear_avatar", None) is not None:
                    try:
                        self.btn_crear_avatar.destroy()
                    except Exception:
                        pass
                    self.btn_crear_avatar = None

            else:
                if self.avatar_text_id is not None:
                    self.canvas.itemconfig(self.avatar_text_id, text="Sin avatar")

        except Exception:
            pass



# ------------------------------------------------------------
# DUM SERVICE (API de alto nivel para UI/Bot)
# ------------------------------------------------------------

def dum_deposit_to_target(usuario, bot, target_total: Decimal):
    """
    Ajusta el depósito total de la run hacia ARRIBA hasta target_total.
    Reglas Dum:
    - No se puede bajar el total (no hay retiros durante run).
    - No se puede superar cap del slot.
    - Descuenta obsidiana del wallet usando depositar_a_bot().
    Retorna dict con info:
      { "ok": bool, "msg": str, "deposited": Decimal, "total": Decimal, "cap": Decimal }
    """
    cap = get_dum_slot_cap(usuario)
    try:
        target_total = Decimal(str(target_total or "0"))
    except Exception:
        target_total = Decimal("0")

    actual = Decimal(str(getattr(bot, "inv_inic", "0") or "0"))

    # No permitir bajar
    if target_total < actual:
        return {
            "ok": False,
            "msg": "⚠️ Dum: no se puede retirar obsidiana hasta terminar la run.",
            "deposited": Decimal("0"),
            "total": actual,
            "cap": cap,
        }

    # Cap
    if target_total > cap:
        return {
            "ok": False,
            "msg": f"⚠️ Dum: tu tope de slot es {cap}.",
            "deposited": Decimal("0"),
            "total": actual,
            "cap": cap,
        }

    delta = target_total - actual
    if delta <= 0:
        return {
            "ok": True,
            "msg": "🟨 Dum: depósito sin cambios.",
            "deposited": Decimal("0"),
            "total": actual,
            "cap": cap,
        }

    # Depositar (usa tu función existente)
    dep = depositar_a_bot(usuario, bot, delta, cap)

    # Mantengo tu contrato: -1 => sin wallet suficiente
    if dep == Decimal("-1"):
        return {
            "ok": False,
            "msg": "⚠️ Dum: no tenés suficiente obsidiana en wallet para ese depósito.",
            "deposited": Decimal("0"),
            "total": actual,
            "cap": cap,
        }

    if dep <= 0:
        return {
            "ok": False,
            "msg": "⚠️ Dum: no se pudo depositar (cap alcanzado o delta inválido).",
            "deposited": Decimal("0"),
            "total": Decimal(str(getattr(bot, "inv_inic", actual) or actual)),
            "cap": cap,
        }

    total = Decimal(str(getattr(bot, "inv_inic", "0") or "0"))
    return {
        "ok": True,
        "msg": f"🟨 Dum depósito: +{dep} (slot ahora: {total})",
        "deposited": dep,
        "total": total,
        "cap": cap,
    }


def dum_start_run(usuario, bot):
    dep_actual = Decimal(str(getattr(bot, "inv_inic", "0") or "0"))
    if dep_actual <= 0:
        return {"ok": False, "msg": "⚠️ Dum: configurá el depósito antes de iniciar.", "deposit": dep_actual}

    cap = get_dum_slot_cap(usuario)

    with bot.lock:
        bot.modo_app = "dum"
        bot.dum_cap = cap
        bot.dum_run_abierta = True

        # el slot operable es usdt (no debería exceder cap)
        bot.usdt = min(dep_actual, cap)

        # opcional: si por alguna razón dep_actual > cap, guardarlo como excedente
        if dep_actual > cap:
            bot.dum_extra_obsidiana = (getattr(bot, "dum_extra_obsidiana", Decimal("0")) or Decimal("0")) + (dep_actual - cap)

    return {"ok": True, "msg": "🟨 Dum: run preparada.", "deposit": dep_actual}


def dum_close_run_once(usuario, bot, usdt_final: Decimal, ui_guard=None):
    """
    Cierra la run Dum (settlement) de forma idempotente.
    - ui_guard: si querés, pasale un objeto con atributo booleano (ej. self) para marcar una sola vez.
      Ej: dum_close_run_once(usuario, bot, usdt_final, ui_guard=self) y que self tenga _dum_run_closed.
    Devuelve dict:
      { "ok": bool, "msg": str }
    """
    # Idempotencia: si ui_guard ya marcó cerrado, no repetir.
    if ui_guard is not None:
        if getattr(ui_guard, "_dum_run_closed", False):
            return {"ok": True, "msg": "🟨 Dum: run ya estaba cerrada."}
        setattr(ui_guard, "_dum_run_closed", True)

    try:
        usdt_final = Decimal(str(usdt_final or "0"))
    except Exception:
        usdt_final = Decimal("0")

    try:
        cerrar_run_dum(usuario, usdt_final)
        return {"ok": True, "msg": "🟨 Dum: run cerrada y saldo devuelto a wallet."}
    except Exception as e:
        return {"ok": False, "msg": f"⚠️ Dum: error al cerrar run: {e}"}

