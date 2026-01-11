# © 2025 Dungeon Market (Khazâd - Trading Bot - animation mixin)
# Todos los derechos reservados.

import os
import random
import tkinter as tk
from tkinter import PhotoImage


class AnimationMixin:
    MAX_CABEZAS = 9

    # ---------------------------
    # Helpers seguros (sin "except Exception")
    # ---------------------------

    def _canvas_is_alive(self, canvas) -> bool:
        try:
            return canvas is not None and canvas.winfo_exists()
        except tk.TclError:
            return False

    def _safe_type(self, canvas, item_id):
        """Devuelve canvas.type(item_id) o None si falla por TclError."""
        if not self._canvas_is_alive(canvas) or not item_id:
            return None
        try:
            return canvas.type(item_id)
        except tk.TclError:
            return None

    def _safe_itemconfig(self, canvas, item_id, **kwargs) -> bool:
        """Itemconfig tolerante a items borrados/destruidos."""
        if not self._canvas_is_alive(canvas) or not item_id:
            return False
        if self._safe_type(canvas, item_id) is None:
            return False
        try:
            canvas.itemconfig(item_id, **kwargs)
            return True
        except tk.TclError:
            return False

    def _safe_itemconfigure(self, canvas, item_id, **kwargs) -> bool:
        if not self._canvas_is_alive(canvas) or not item_id:
            return False
        if self._safe_type(canvas, item_id) is None:
            return False
        try:
            canvas.itemconfigure(item_id, **kwargs)
            return True
        except tk.TclError:
            return False

    def _safe_coords(self, canvas, item_id, x, y) -> bool:
        if not self._canvas_is_alive(canvas) or not item_id:
            return False
        if self._safe_type(canvas, item_id) is None:
            return False
        try:
            canvas.coords(item_id, x, y)
            return True
        except tk.TclError:
            return False

    def _safe_delete(self, canvas, item_id) -> bool:
        if not self._canvas_is_alive(canvas) or not item_id:
            return False
        try:
            canvas.delete(item_id)
            return True
        except tk.TclError:
            return False

    def _safe_tag_raise(self, canvas, item_id, above_this=None) -> bool:
        if not self._canvas_is_alive(canvas) or not item_id:
            return False
        try:
            if above_this is None:
                canvas.tag_raise(item_id)
            else:
                canvas.tag_raise(item_id, above_this)
            return True
        except tk.TclError:
            return False

    # ---------------------------
    # Inicialización
    # ---------------------------

    def init_animation(self):
        self.cancelar_animaciones()
        if getattr(self, "_animaciones_activas", False):
            return
        self._animaciones_activas = True

        if not hasattr(self, "_after_ids"):
            self._after_ids = []

        # ─── PEDESTAL ───
        pedestal_path = "imagenes/deco/rebalance/pedestal.png"
        if os.path.exists(pedestal_path):
            self.pedestal_img = PhotoImage(file=pedestal_path).zoom(2, 2)
            self.pedestal_item = self.canvas_various.create_image(
                1450, 25, image=self.pedestal_img, anchor="nw"
            )

        # ─── VARITA ───
        wand_path = "imagenes/deco/woods/gem_wood_new.png"
        if os.path.exists(wand_path):
            self.wand_img = PhotoImage(file=wand_path).zoom(2, 2)
            self.wand_item = self.canvas_various.create_image(
                1450, 20, image=(self.wand_img or ""), anchor="nw"
            )

        # ─── CARGA SEARING RAY ───
        self.searing_frames = []
        for i in range(6):  # 0..5
            p = f"imagenes/deco/lights/searing_ray/searing_ray_{i}.png"
            if os.path.exists(p):
                self.searing_frames.append(PhotoImage(file=p))

        # ─── CARGA MAGIC DART ───
        self.magic_frames = []
        for i in range(6):  # 0..5
            p = f"imagenes/deco/lights/magic_dart/magic_dart_{i}.png"
            if os.path.exists(p):
                self.magic_frames.append(PhotoImage(file=p))

        # Item en el canvas_various
        self.searing_item = self.canvas_various.create_image(
            1450, 20, image="", anchor="nw"
        )

        # ─── ALTARES TP / SL ───
        def _img(path, zoom=2):
            return PhotoImage(file=path).zoom(zoom, zoom) if os.path.exists(path) else None

        # bases
        self.altar_base = _img("imagenes/deco/sltp/altar_base.png", 2) or _img("altar_base.png", 2)
        self.altar_trog = _img("imagenes/deco/sltp/altar_trog.png", 2) or _img("altar_trog.png", 2)
        self.gozag_frames = [
            p for p in (
                _img("imagenes/deco/sltp/gozag_0.png", 2) or _img("gozag_0.png", 2),
                _img("imagenes/deco/sltp/gozag_1.png", 2) or _img("gozag_1.png", 2),
                _img("imagenes/deco/sltp/gozag_2.png", 2) or _img("gozag_2.png", 2)
            ) if p
        ]
        self.jiyva_frames = [
            p for p in (
                _img("imagenes/deco/sltp/altar_jiyva_0.png", 2) or _img("altar_jiyva_0.png", 2),
                _img("imagenes/deco/sltp/altar_jiyva_1.png", 2) or _img("altar_jiyva_1.png", 2)
            ) if p
        ]

        fedhas_path = "imagenes/deco/sltp/altar_fedhas.png"
        self.altar_fedhas = PhotoImage(file=fedhas_path).zoom(2, 2) if os.path.exists(fedhas_path) else None

        self.icon_sword = _img("imagenes/deco/sltp/long_sword_1_new.png", 2) or _img("long_sword_1_new.png", 2)
        self.icon_shield = _img("imagenes/deco/sltp/buckler_1_new.png", 2) or _img("buckler_1_new.png", 2)

        Wv = int(self.canvas_various["width"])
        base_y = 30
        tp_x = Wv - 440
        sl_x = Wv - 360

        self.altar_tp_item = self.canvas_various.create_image(tp_x, base_y, image=self.altar_base or "", anchor="nw")
        self.altar_sl_item = self.canvas_various.create_image(sl_x, base_y, image=self.altar_base or "", anchor="nw")

        self.tp_icon_item = self.canvas_various.create_image(tp_x + 12, base_y - 25, image=self.icon_sword or "", anchor="nw")
        self.sl_icon_item = self.canvas_various.create_image(sl_x + 2, base_y - 16, image=self.icon_shield or "", anchor="nw")
        self.canvas_various.itemconfigure(self.tp_icon_item, state="hidden")
        self.canvas_various.itemconfigure(self.sl_icon_item, state="hidden")

        self._tp_state = "inactive"
        self._sl_state = "inactive"
        self._altar_frame = 0

        if not getattr(self, "bot", None) or not self.bot.running:
            if self.altar_fedhas:
                self.canvas_various.itemconfig(self.altar_tp_item, image=self.altar_fedhas)
                self.canvas_various.itemconfig(self.altar_sl_item, image=self.altar_fedhas)
                self.canvas_various.itemconfigure(self.tp_icon_item, state="hidden")
                self.canvas_various.itemconfigure(self.sl_icon_item, state="hidden")

        self.animar(600, self._animate_altars)

        self.ashenzari_img = _img("imagenes/deco/sltp/ashenzari.png", 2) or _img("ashenzari.png", 2)
        self.destroy_tp_item = self.canvas_various.create_image(tp_x, base_y, image=self.ashenzari_img or "", anchor="nw")
        self.destroy_sl_item = self.canvas_various.create_image(sl_x, base_y, image=self.ashenzari_img or "", anchor="nw")
        self.canvas_various.itemconfigure(self.destroy_tp_item, state="hidden")
        self.canvas_various.itemconfigure(self.destroy_sl_item, state="hidden")

        # ─── ELEFANTES ───
        ruta_ele = os.path.join("imagenes", "deco", "elefants")
        stat_path = os.path.join(ruta_ele, "elephant_statue.png")
        self.elephant_statue = PhotoImage(file=stat_path).zoom(3, 3) if os.path.exists(stat_path) else None

        self.elephants = []
        for i in range(8):
            p = os.path.join(ruta_ele, f"elephant_{i}.png")
            img = PhotoImage(file=p).zoom(3, 3) if os.path.exists(p) else None
            self.elephants.append(img)

        x_ele = 550
        y_ele = 330
        initial_img = self.elephant_statue or (self.elephants[0] if self.elephants and self.elephants[0] else "")
        self.elephant_item = self.canvas_animation.create_image(x_ele, y_ele, image=initial_img, anchor="nw")
        self.animar(500, self._update_elephant)

        # ─── ANTORCHA ───
        self.torch_frames = []
        for i in range(1, 5):
            p = f"imagenes/deco/torch/torch_{i}.png"
            if os.path.exists(p):
                self.torch_frames.append(PhotoImage(file=p).zoom(3, 3))

        off = "imagenes/deco/torch/torch_0.png"
        self.torch_off = PhotoImage(file=off).zoom(3, 3) if os.path.exists(off) else None
        self.torch_frame_index = 0

        # ─── LÍANAS VERDES/ROJAS ───
        base_dir = os.path.join("imagenes", "deco", "lianas")
        dirs = {
            "green": os.path.join(base_dir, "verdes"),
            "red": os.path.join(base_dir, "rojas"),
        }
        tokens = ("north", "south", "east", "west")
        diag_map = {
            "northeast": ("north", "east"),
            "northwest": ("north", "west"),
            "southeast": ("south", "east"),
            "southwest": ("south", "west"),
        }

        self.vine_sequence_green = {t: [] for t in tokens}
        self.vine_sequence_red = {t: [] for t in tokens}

        for color, folder in dirs.items():
            seq_map = self.vine_sequence_green if color == "green" else self.vine_sequence_red
            if not os.path.isdir(folder):
                continue
            for fname in os.listdir(folder):
                if not fname.lower().endswith(".png"):
                    continue

                if color == "red":
                    if not fname.startswith("starspawn_"):
                        continue
                    name = fname[len("starspawn_"):-4]
                else:
                    if not fname.startswith("vine_"):
                        continue
                    name = fname[len("vine_"):-4]

                parts = name.split("_")

                if parts[0] == "corner" and len(parts) == 2:
                    direcciones = [parts[1]]
                elif parts[0] == "tentacle" and len(parts) == 2:
                    direcciones = [parts[1]]
                elif parts[0] == "tentacle" and len(parts) == 4 and parts[1] == "segment":
                    direcciones = parts[2:4]
                elif parts[0] == "segment" and len(parts) == 3:
                    direcciones = parts[1:3]
                else:
                    continue

                bordes = []
                for d in direcciones:
                    if d in diag_map:
                        bordes += diag_map[d]
                    elif d in tokens:
                        bordes.append(d)

                img = PhotoImage(file=os.path.join(folder, fname)).zoom(2, 2)
                for b in set(bordes):
                    seq_map[b].append(img)

        # items vines sobre canvas_right_b
        self.vine_items = []
        self.vine_indices = {t: 0 for t in tokens}

        W = int(self.canvas_right_b["width"])
        H = int(self.canvas_right_b["height"])

        width_top = self.vine_sequence_green["north"][0].width() if self.vine_sequence_green["north"] else 0
        width_bottom = self.vine_sequence_green["south"][0].width() if self.vine_sequence_green["south"] else 0
        height_left = self.vine_sequence_green["west"][0].height() if self.vine_sequence_green["west"] else 0
        height_right = self.vine_sequence_green["east"][0].height() if self.vine_sequence_green["east"] else 0
        width_right = self.vine_sequence_green["east"][0].width() if self.vine_sequence_green["east"] else 0
        height_bottom = self.vine_sequence_green["south"][0].height() if self.vine_sequence_green["south"] else 0

        if width_top > 0:
            for x in range(0, W, width_top):
                iid = self.canvas_right_b.create_image(x, 0, image="", anchor="nw")
                self.vine_items.append(("north", iid))

        if width_bottom > 0 and height_bottom > 0:
            y_bottom = H - height_bottom
            for x in range(0, W, width_bottom):
                iid = self.canvas_right_b.create_image(x, y_bottom, image="", anchor="nw")
                self.vine_items.append(("south", iid))

        if height_left > 0:
            for y in range(0, H, height_left):
                iid = self.canvas_right_b.create_image(0, y, image="", anchor="nw")
                self.vine_items.append(("west", iid))

        if width_right > 0:
            x_right = W - width_right
            step = height_right if height_right > 0 else 1
            for y in range(0, H, step):
                iid = self.canvas_right_b.create_image(x_right, y, image="", anchor="nw")
                self.vine_items.append(("east", iid))

        # ─── ICONOS SONIDO ───
        on_path = "imagenes/deco/noise/i-noise_new.png"
        off_path = "imagenes/deco/noise/i-noise_old.png"
        self.noise_on = PhotoImage(file=on_path).zoom(2, 2) if os.path.exists(on_path) else None
        self.noise_off = PhotoImage(file=off_path).zoom(2, 2) if os.path.exists(off_path) else None

        self._hydra_gate = "imagenes/deco/gates/enter_snake.png"
        self.hydra_gate = PhotoImage(file=self._hydra_gate).zoom(4, 4) if os.path.exists(self._hydra_gate) else None

        # Guardián
        self.guard_open_frames = []
        self.guard_closed_frames = []
        for i in range(1, 5):
            po = f"imagenes/deco/guards/guardian-eyeopen-flame_{i}.png"
            pc = f"imagenes/deco/guards/guardian-eyeclosed-flame_{i}.png"
            if os.path.exists(po):
                self.guard_open_frames.append(PhotoImage(file=po).zoom(2, 2))
            if os.path.exists(pc):
                self.guard_closed_frames.append(PhotoImage(file=pc).zoom(2, 2))
        self.guard_frame_index = 0

        # Abyss gate
        self.abyss_frames = []
        for i in range(1, 4):
            path = f"imagenes/deco/gates/abyss/enter_abyss_{i}.png"
            if os.path.exists(path):
                self.abyss_frames.append(PhotoImage(file=path).zoom(3, 3))

        abyss_static = "imagenes/deco/gates/abyss/enter_abyss.png"
        self.abyss_static_img = PhotoImage(file=abyss_static).zoom(3, 3) if os.path.exists(abyss_static) else None
        self.abyss_frame_index = 0

        # Dithmenos
        self.dithmenos_frames = []
        for name in ("dithmenos.png", "dithmenos_2.png", "dithmenos_3.png", "dithmenos_4.png"):
            path = os.path.join("imagenes", "deco", "dith", name)
            if os.path.exists(path):
                self.dithmenos_frames.append(PhotoImage(file=path).zoom(2, 2))
        self.dithmenos_index = 0

        # Oro (ventas reales)
        piles = list(range(1, 11)) + [16, 19, 23, 25]
        self.sales_frames = []
        for n in piles:
            p = f"imagenes/deco/gold_pile/gold_pile_{n}.png"
            if os.path.exists(p):
                self.sales_frames.append(PhotoImage(file=p).zoom(2, 2))

        # Hidra (ventas fantasma)
        bottom_idxs = [1, 5, 7, 8, 9]
        self.hydra_bottom = {}
        for n in bottom_idxs:
            p = f"imagenes/deco/hydra/lernaean_hydra_{n}_bottom.png"
            if os.path.exists(p):
                self.hydra_bottom[n] = PhotoImage(file=p).zoom(2, 2)
        self.hydra_top = []
        for i in range(1, self.MAX_CABEZAS + 1):
            p = f"imagenes/deco/hydra/lernaean_hydra_{i}_top.png"
            if not os.path.exists(p):
                break
            self.hydra_top.append(PhotoImage(file=p).zoom(2, 2))

        # Esqueleto hidra (compras/ventas)
        self.skel_buy = []
        self.skel_sell = []
        idx = 1
        while True:
            nb = f"imagenes/deco/skl_hydra/skeleton_hydra_{idx}_new.png"
            ns = f"imagenes/deco/skl_hydra/skeleton_hydra_{idx}_old.png"
            if not os.path.exists(nb) and not os.path.exists(ns):
                break
            if os.path.exists(nb):
                self.skel_buy.append(PhotoImage(file=nb).zoom(2, 2))
            if os.path.exists(ns):
                self.skel_sell.append(PhotoImage(file=ns).zoom(2, 2))
            idx += 1

        # ─── LÁMPARA + EFREET ───
        lamppaths = [
            (
                os.path.join("imagenes", "deco", "rebalance", "magic_lamp.png"),
                os.path.join("imagenes", "deco", "rebalance", "efreet.png"),
            ),
            ("/mnt/data/magic_lamp.png", "/mnt/data/efreet.png"),
        ]
        lamp_path = None
        efreet_path = None
        for lp, ep in lamppaths:
            if os.path.exists(lp) and os.path.exists(ep):
                lamp_path, efreet_path = lp, ep
                break

        self.lamp_img = PhotoImage(file=lamp_path).zoom(2, 2) if lamp_path else None
        self.efreet_img = PhotoImage(file=efreet_path).zoom(3, 3) if efreet_path else None

        y_bottom = 400
        x_left = 400
        self.lamp_item = self.canvas_animation.create_image(
            x_left, y_bottom, image=(self.lamp_img or ""), anchor="sw"
        )
        self.efreet_item = self.canvas_animation.create_image(
            320, 380, image="", anchor="sw"
        )

        # subir efreet sobre lámpara (si el canvas vive)
        self._safe_tag_raise(self.canvas_animation, self.efreet_item, self.lamp_item)

        self.animar(250, self._update_lamp_genie)

        # Antorcha en canvas_center
        first_torch = self.torch_frames[0] if self.torch_frames else self.torch_off
        self.torch_item = self.canvas_center.create_image(350, 250, image=first_torch, anchor="nw")
        self.hydra_gate_f = self.canvas_center.create_image(200, 320, image=self.hydra_gate, anchor="nw")

        # Guardián en canvas_various
        guard0 = self.guard_closed_frames[0] if self.guard_closed_frames else None
        self.guard_item = self.canvas_various.create_image(1800, 15, image=guard0, anchor="nw")

        # Dithmenos item
        if self.dithmenos_frames:
            self.dithmenos_item = self.canvas_center.create_image(0, 390, image=self.dithmenos_frames[0], anchor="nw")

        # item sound
        initial = self.noise_on if getattr(self, "sound_enabled", True) else self.noise_off
        self.noise_item = self.canvas_various.create_image(1700, 16, image=initial, anchor="nw")

        # Oro (en various)
        self.sales_item = self.canvas_various.create_image(1350, 15, image="", anchor="nw")

        # Hidra en center
        self.hydra_bottom_it = self.canvas_center.create_image(230, 400, image="", anchor="nw")
        self.hydra_top_it = self.canvas_center.create_image(230, 350, image="", anchor="nw")

        # Esqueleto hidra en center
        self.skel_buy_it = self.canvas_center.create_image(360, 385, image="", anchor="nw")
        self.skel_sell_it = self.canvas_center.create_image(100, 385, image="", anchor="nw")

        # Abyss item
        initial_g = self.abyss_static_img or (self.abyss_frames[0] if self.abyss_frames else "")
        self.abyss_item = self.canvas_center.create_image(650, 400, image=initial_g, anchor="center")

        # ─── HISTORIAL: ELDRITCH / KRAKEN ───
        base_dir_hist = os.path.join("imagenes", "deco", "lianas")
        tokens_hist = ("north", "south", "east", "west")

        self.eldritch_seq = {t: [] for t in tokens_hist}
        self.kraken_seq = {t: [] for t in tokens_hist}

        def _load_sorted(folder, prefix=None):
            frames = []
            if not os.path.isdir(folder):
                return frames

            def _key(fn):
                name = fn[:-4]
                parts = name.split("_")
                try:
                    return (0, int(parts[-1]))
                except (ValueError, TypeError):
                    return (1, name)

            files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
            for fname in sorted(files, key=_key):
                if prefix and not fname.startswith(prefix):
                    continue
                # Si falla una imagen por TclError (archivo roto), la salteamos
                try:
                    frames.append(PhotoImage(file=os.path.join(folder, fname)).zoom(2, 2))
                except tk.TclError:
                    continue
            return frames

        eld_ends_dir = os.path.join(base_dir_hist, "eldritch", "eldritch_ends")
        eld_ends = _load_sorted(eld_ends_dir, prefix="eldritch_tentacle_")
        self.eldritch_seq = {t: list(eld_ends) for t in tokens_hist}

        kra_head_dir = os.path.join(base_dir_hist, "kraken", "kraken_head")
        kra_ends_dir = os.path.join(base_dir_hist, "kraken", "kraken_ends")

        self.kraken_head_frames = _load_sorted(kra_head_dir, prefix="kraken_head_")[:2]
        kra_tentacles = _load_sorted(kra_ends_dir, prefix="kraken_tentacle_")
        self.kraken_seq = {t: list(kra_tentacles) for t in tokens_hist}

        self.hist_items = []

        def _dim(seq, k, kind):
            arr = seq.get(k, [])
            if not arr:
                return 0
            return arr[0].width() if kind == "w" else arr[0].height()

        try:
            WH = int(self.canvas_right["width"])
            HH = int(self.canvas_right["height"])
        except (ValueError, tk.TclError, KeyError):
            WH, HH = 640, 360

        w_top = max(_dim(self.eldritch_seq, "north", "w"), _dim(self.kraken_seq, "north", "w"))
        w_bottom = max(_dim(self.eldritch_seq, "south", "w"), _dim(self.kraken_seq, "south", "w"))
        h_left = max(_dim(self.eldritch_seq, "west", "h"), _dim(self.kraken_seq, "west", "h"))
        h_right = max(_dim(self.eldritch_seq, "east", "h"), _dim(self.kraken_seq, "east", "h"))
        w_right = max(_dim(self.eldritch_seq, "east", "w"), _dim(self.kraken_seq, "east", "w"))
        h_bottom = max(_dim(self.eldritch_seq, "south", "h"), _dim(self.kraken_seq, "south", "h"))

        if w_top > 0:
            for x in range(0, WH, w_top):
                iid = self.canvas_right.create_image(x, 0, image="", anchor="nw")
                self.hist_items.append(("north", iid))

        if w_bottom > 0 and h_bottom > 0:
            yb = HH - h_bottom
            for x in range(0, WH, w_bottom):
                iid = self.canvas_right.create_image(x, yb, image="", anchor="nw")
                self.hist_items.append(("south", iid))

        if h_left > 0:
            for y in range(0, HH, h_left):
                iid = self.canvas_right.create_image(0, y, image="", anchor="nw")
                self.hist_items.append(("west", iid))

        if h_right > 0:
            xr = WH - (w_right if w_right > 0 else 1)
            for y in range(0, HH, h_right):
                iid = self.canvas_right.create_image(xr, y, image="", anchor="nw")
                self.hist_items.append(("east", iid))

        self.hist_slots = {t: [] for t in ("north", "south", "east", "west")}
        for borde, iid in self.hist_items:
            self.hist_slots[borde].append(iid)

        self.hist_frame_idx = {t: 0 for t in self.hist_slots}
        self.hist_slot_idx = {t: 0 for t in self.hist_slots}

        self.kraken_head_item = None
        self._kh_frame_idx = 0
        self._kh_move_ctr = 0
        self._kh_move_every = 3

        # ─── LOOP ANIMACIONES ───
        self.animar(100, self._animate_torch)
        self.animar(100, self._animate_guard)
        self.animar(300, self._animate_dithmenos)
        self.animar(500, self._update_sales)
        self.animar(500, self._update_hydra)
        self.animar(500, self._update_skeleton)
        self.animar(200, self._update_noise_icon)
        self.animar(250, self._animate_vines)
        self.animar(500, self._update_abyss)

        self.searing_index = 0
        self.animar(250, self._update_searing_magic)

        self.animar(800, self._animate_historial_tentacles)

    # ---------------------------
    # Animaciones / updates
    # ---------------------------

    def _update_searing_magic(self):
        if not getattr(self, "bot", None) or not self.bot.running:
            self._safe_itemconfig(self.canvas_various, self.searing_item, image="")
            self.animar(250, self._update_searing_magic)
            return

        total = (self.bot.usdt or 0) + (self.bot.btc_usdt or 0)
        guia = self.bot.hold_usdt_var or 0

        frames = None
        if total > guia and self.searing_frames:
            frames = self.searing_frames
        elif total < guia and self.magic_frames:
            frames = self.magic_frames

        if frames:
            self.searing_index = (self.searing_index + 1) % len(frames)
            img = frames[self.searing_index]
            self._safe_itemconfig(self.canvas_various, self.searing_item, image=img)
        else:
            self._safe_itemconfig(self.canvas_various, self.searing_item, image="")

        self.animar(250, self._update_searing_magic)

    def _is_valid_image_item(self, canvas, item_id):
        return self._safe_type(canvas, item_id) == "image"

    def cancelar_animaciones(self):
        if not hasattr(self, "_after_ids"):
            self._after_ids = []
            return

        for aid in list(self._after_ids):
            try:
                self.root.after_cancel(aid)
            except tk.TclError:
                # after_id inválido porque ya se ejecutó/canceló o root muerto
                pass

        self._after_ids.clear()
        self._animaciones_activas = False

    def animar(self, delay_ms, callback):
        aid = self.root.after(delay_ms, callback)
        self._after_ids.append(aid)

    def _safe_next_frame(self, frames, index):
        if not frames:
            return None, index
        index = (index + 1) % len(frames)
        return frames[index], index

    def _rand_kraken_head_coords(self, frame_img):
        try:
            WH = int(self.canvas_right["width"])
            HH = int(self.canvas_right["height"])
        except (ValueError, tk.TclError, KeyError):
            WH, HH = 640, 360

        if not frame_img:
            return 0, 0

        w = frame_img.width()
        h = frame_img.height()

        side = random.choice(("north", "south", "east", "west"))
        if side == "north":
            x = random.randint(0, max(0, WH - w))
            y = 0
        elif side == "south":
            x = random.randint(0, max(0, WH - w))
            y = max(0, HH - h)
        elif side == "east":
            x = max(0, WH - w)
            y = random.randint(0, max(0, HH - h))
        else:
            x = 0
            y = random.randint(0, max(0, HH - h))
        return x, y

    def _ensure_abyss_item(self):
        if not hasattr(self, "canvas_center"):
            return False

        img0 = getattr(self, "abyss_static_img", None) or (
            self.abyss_frames[0] if getattr(self, "abyss_frames", None) else None
        )
        if img0 is None:
            return False

        c = self.canvas_center

        if getattr(self, "abyss_item", None) and self._safe_type(c, self.abyss_item) == "image":
            return True

        # si existía algo inválido, lo borramos (si se puede)
        if getattr(self, "abyss_item", None):
            self._safe_delete(c, self.abyss_item)

        self.abyss_item = c.create_image(650, 400, image=img0, anchor="center")
        return True

    def _abyss_set_image(self, img):
        if img is None:
            return
        if not self._ensure_abyss_item():
            return
        if self._safe_type(self.canvas_center, self.abyss_item) != "image":
            return
        self._safe_itemconfig(self.canvas_center, self.abyss_item, image=img)

    def _update_abyss(self):
        bot = getattr(self, "bot", None)
        usar_animacion = bool(getattr(bot, "compra_en_venta_fantasma", False))

        if usar_animacion and getattr(self, "abyss_frames", None):
            frame, self.abyss_frame_index = self._safe_next_frame(self.abyss_frames, self.abyss_frame_index)
            self._abyss_set_image(frame)
        else:
            static_img = getattr(self, "abyss_static_img", None)
            if static_img is not None:
                self._abyss_set_image(static_img)
            elif getattr(self, "abyss_frames", None):
                self._abyss_set_image(self.abyss_frames[0])

        self.animar(500, self._update_abyss)

    def _update_lamp_genie(self):
        raw = getattr(self, "bot", None) and getattr(self.bot, "rebalance_enabled", False)
        if isinstance(raw, str):
            show_genie = raw.strip().lower() in ("on", "true", "1", "sí", "si", "yes")
        else:
            show_genie = bool(raw)

        if getattr(self, "lamp_item", None) is not None:
            self._safe_itemconfig(self.canvas_animation, self.lamp_item, image=(self.lamp_img or ""))

        if getattr(self, "efreet_item", None) is not None:
            self._safe_itemconfig(self.canvas_animation, self.efreet_item, image=(self.efreet_img if show_genie else ""))
            self._safe_tag_raise(self.canvas_animation, self.efreet_item)

        self.animar(400, self._update_lamp_genie)

    def set_take_profit_state(self, state: str):
        self._tp_state = state
        self._refresh_altar_image(kind="tp")

        if state == "hit":
            self._sl_state = "inactive"
            self._refresh_altar_image(kind="sl")

            self._safe_itemconfigure(self.canvas_various, self.destroy_sl_item, state="normal")
            self._safe_itemconfigure(self.canvas_various, self.sl_icon_item, state="hidden")
            self._safe_itemconfigure(self.canvas_various, self.altar_sl_item, state="hidden")
            self._safe_tag_raise(self.canvas_various, self.destroy_sl_item)
        else:
            self._safe_itemconfigure(self.canvas_various, self.destroy_sl_item, state="hidden")
            self._safe_itemconfigure(self.canvas_various, self.altar_sl_item, state="normal")

    def set_stop_loss_state(self, state: str):
        self._sl_state = state
        self._refresh_altar_image(kind="sl")

        if state == "hit":
            self._tp_state = "inactive"
            self._refresh_altar_image(kind="tp")

            self._safe_itemconfigure(self.canvas_various, self.destroy_tp_item, state="normal")
            self._safe_itemconfigure(self.canvas_various, self.tp_icon_item, state="hidden")
            self._safe_itemconfigure(self.canvas_various, self.altar_tp_item, state="hidden")
            self._safe_tag_raise(self.canvas_various, self.destroy_tp_item)
        else:
            self._safe_itemconfigure(self.canvas_various, self.destroy_tp_item, state="hidden")
            self._safe_itemconfigure(self.canvas_various, self.altar_tp_item, state="normal")

    def _refresh_altar_image(self, kind: str):
        if kind == "tp":
            state = self._tp_state
            item = self.altar_tp_item
            icon_item = self.tp_icon_item
        else:
            state = self._sl_state
            item = self.altar_sl_item
            icon_item = self.sl_icon_item

        if state == "hit":
            img = (self.gozag_frames[self._altar_frame % len(self.gozag_frames)] if self.gozag_frames else self.altar_base)
            if kind == "sl":
                img = self.altar_trog or self.altar_base
        elif state == "inactive":
            img = (self.jiyva_frames[self._altar_frame % len(self.jiyva_frames)] if self.jiyva_frames else self.altar_base)
        else:
            img = self.altar_base

        self._safe_itemconfig(self.canvas_various, item, image=(img or ""))

        visible = "normal" if state == "armed" else "hidden"
        self._safe_itemconfigure(self.canvas_various, icon_item, state=visible)

    def _animate_altars(self):
        if (not getattr(self, "bot", None) or not self.bot.running) and getattr(self, "altar_fedhas", None):
            self._safe_itemconfig(self.canvas_various, self.altar_tp_item, image=self.altar_fedhas)
            self._safe_itemconfig(self.canvas_various, self.altar_sl_item, image=self.altar_fedhas)
            self._safe_itemconfigure(self.canvas_various, self.tp_icon_item, state="hidden")
            self._safe_itemconfigure(self.canvas_various, self.sl_icon_item, state="hidden")
            self.animar(600, self._animate_altars)
            return

        self._altar_frame += 1
        self._refresh_altar_image("tp")
        self._refresh_altar_image("sl")
        self.animar(600, self._animate_altars)

    def _update_elephant(self):
        cnt = getattr(self, "bot", None) and self.bot.contador_compras_fantasma or 0

        if cnt <= 0:
            img = self.elephant_statue
        elif 1 <= cnt <= len(self.elephants):
            idx = min(cnt - 1, len(self.elephants) - 1)
            img = self.elephants[idx]
        else:
            img = self.elephants[-1] if self.elephants else None

        if img:
            self._safe_itemconfig(self.canvas_animation, self.elephant_item, image=img)

        self.animar(500, self._update_elephant)

    def _animate_torch(self):
        if self.bot and self.bot.running and self.torch_frames:
            frame, self.torch_frame_index = self._safe_next_frame(self.torch_frames, self.torch_frame_index)
        else:
            frame = self.torch_off

        if frame and self._safe_type(self.canvas_center, self.torch_item) == "image":
            self._safe_itemconfig(self.canvas_center, self.torch_item, image=frame)

        self.animar(100, self._animate_torch)

    def _update_noise_icon(self):
        frame = self.noise_on if getattr(self, "sound_enabled", True) else self.noise_off
        if frame and self._safe_type(self.canvas_various, self.noise_item) == "image":
            self._safe_itemconfig(self.canvas_various, self.noise_item, image=frame)
        self.animar(200, self._update_noise_icon)

    def _animate_guard(self):
        frames = self.guard_open_frames if (self.bot and self.bot.running) else self.guard_closed_frames
        if frames:
            frame, self.guard_frame_index = self._safe_next_frame(frames, self.guard_frame_index)
            if frame and self._safe_type(self.canvas_various, self.guard_item) == "image":
                self._safe_itemconfig(self.canvas_various, self.guard_item, image=frame)
        self.animar(100, self._animate_guard)

    def _sales_index(self, cnt):
        ths = list(range(1, 11)) + [16, 19, 23, 25]
        idx = 0
        for i, t in enumerate(ths):
            if cnt >= t:
                idx = i
        return min(idx, len(self.sales_frames) - 1) if self.sales_frames else 0

    def _update_sales(self):
        cnt = getattr(self, "bot", None) and self.bot.contador_ventas_reales or 0
        img = self.sales_frames[self._sales_index(cnt)] if (cnt > 0 and self.sales_frames) else ""
        self._safe_itemconfig(self.canvas_various, self.sales_item, image=img)
        self.animar(500, self._update_sales)

    def _hydra_key(self, cnt):
        keys = sorted(self.hydra_bottom)
        lower = [k for k in keys if k <= cnt]
        return (lower or keys)[-1]

    def _update_hydra(self):
        cnt = getattr(self, "bot", None) and self.bot.contador_ventas_fantasma or 0
        if cnt > 0 and self.hydra_bottom:
            key = self._hydra_key(cnt)
            bot_img = self.hydra_bottom.get(key)
            top_img = self.hydra_top[min(cnt - 1, len(self.hydra_top) - 1)] if self.hydra_top else None
        else:
            bot_img = None
            top_img = None

        if bot_img and self._is_valid_image_item(self.canvas_center, self.hydra_bottom_it):
            self._safe_itemconfig(self.canvas_center, self.hydra_bottom_it, image=bot_img)
        if top_img and self._is_valid_image_item(self.canvas_center, self.hydra_top_it):
            self._safe_itemconfig(self.canvas_center, self.hydra_top_it, image=top_img)

        self.animar(500, self._update_hydra)

    def _update_skeleton(self):
        buy = getattr(self, "bot", None) and self.bot.contador_compras_reales or 0
        sell = getattr(self, "bot", None) and self.bot.contador_ventas_reales or 0

        def _resolve_image(count, frames):
            if not frames:
                return None, False
            n = len(frames)
            if count <= 0:
                return "", True
            if 1 <= count <= n:
                return frames[count - 1], False
            r = count % (n + 1)
            if r == 0:
                return "", True
            return frames[r - 1], False

        img_b, clear_b = _resolve_image(buy, self.skel_buy)
        img_s, clear_s = _resolve_image(sell, self.skel_sell)

        if self._is_valid_image_item(self.canvas_center, self.skel_buy_it):
            if clear_b:
                self._safe_itemconfig(self.canvas_center, self.skel_buy_it, image="")
            elif img_b:
                self._safe_itemconfig(self.canvas_center, self.skel_buy_it, image=img_b)

        if self._is_valid_image_item(self.canvas_center, self.skel_sell_it):
            if clear_s:
                self._safe_itemconfig(self.canvas_center, self.skel_sell_it, image="")
            elif img_s:
                self._safe_itemconfig(self.canvas_center, self.skel_sell_it, image=img_s)

        self.animar(500, self._update_skeleton)

    def _animate_dithmenos(self):
        if self.dithmenos_frames:
            if getattr(self, "bot", None) and self.bot.precio_actual is None:
                frame = self.dithmenos_frames[0]
            else:
                frame, self.dithmenos_index = self._safe_next_frame(self.dithmenos_frames, self.dithmenos_index)

            if frame and self._safe_type(self.canvas_center, self.dithmenos_item) == "image":
                self._safe_itemconfig(self.canvas_center, self.dithmenos_item, image=frame)

        self.animar(300, self._animate_dithmenos)

    def _animate_vines(self):
        if not hasattr(self, "vine_items") or not hasattr(self, "vine_indices"):
            self.animar(12000, self._animate_vines)
            return

        if self.bot.contador_compras_reales == 0:
            seq_map = None
        else:
            delta_pct = self.bot.var_total
            if delta_pct > 0:
                seq_map = self.vine_sequence_green
            elif delta_pct < 0:
                seq_map = self.vine_sequence_red
            else:
                seq_map = None

        for border, iid in self.vine_items:
            if not seq_map or border not in seq_map or not seq_map[border]:
                img = None
            else:
                frames = seq_map[border]
                idx = (self.vine_indices[border] + 1) % len(frames)
                self.vine_indices[border] = idx
                img = frames[idx]

            if img and self._safe_type(self.canvas_right_b, iid) == "image":
                self._safe_itemconfig(self.canvas_right_b, iid, image=img)

        self.animar(12000, self._animate_vines)

    def _animate_historial_tentacles(self):
        if not getattr(self, "bot", None) or not self.bot.running:
            for _, iid in getattr(self, "hist_items", []):
                self._safe_itemconfig(self.canvas_right, iid, image="")

            if getattr(self, "kraken_head_item", None):
                self._safe_delete(self.canvas_right, self.kraken_head_item)
                self.kraken_head_item = None

            self.animar(800, self._animate_historial_tentacles)
            return

        bot = getattr(self, "bot", None)
        slots = getattr(self, "hist_slots", {})
        if not bot or not slots:
            self.animar(800, self._animate_historial_tentacles)
            return

        familia_activa = getattr(bot, "hist_tentacles", None)
        if familia_activa == "eldritch":
            seq_map = self.eldritch_seq
        elif familia_activa == "kraken":
            seq_map = self.kraken_seq
        else:
            seq_map = None
            for _, iid in getattr(self, "hist_items", []):
                self._safe_itemconfig(self.canvas_right, iid, image="")
            if getattr(self, "kraken_head_item", None):
                self._safe_delete(self.canvas_right, self.kraken_head_item)
                self.kraken_head_item = None
            self.animar(800, self._animate_historial_tentacles)
            return

        if familia_activa == "eldritch":
            if getattr(self, "kraken_head_item", None):
                self._safe_delete(self.canvas_right, self.kraken_head_item)
                self.kraken_head_item = None

            for borde, iids in slots.items():
                frames = seq_map.get(borde, [])
                if not frames or not iids:
                    for iid in iids:
                        self._safe_itemconfig(self.canvas_right, iid, image="")
                    continue

                self.hist_frame_idx[borde] = (self.hist_frame_idx[borde] + 1) % len(frames)
                self.hist_slot_idx[borde] = (self.hist_slot_idx[borde] + 1) % len(iids)

                frame = frames[self.hist_frame_idx[borde]]
                target_iid = iids[self.hist_slot_idx[borde]]

                for iid in iids:
                    self._safe_itemconfig(self.canvas_right, iid, image="")
                self._safe_itemconfig(self.canvas_right, target_iid, image=frame)

        elif familia_activa == "kraken":
            for borde, iids in slots.items():
                frames = seq_map.get(borde, [])
                if not frames or not iids:
                    for iid in iids:
                        self._safe_itemconfig(self.canvas_right, iid, image="")
                    continue

                self.hist_frame_idx[borde] = (self.hist_frame_idx[borde] + 1) % len(frames)
                self.hist_slot_idx[borde] = (self.hist_slot_idx[borde] + 1) % len(iids)

                frame = frames[self.hist_frame_idx[borde]]
                target_iid = iids[self.hist_slot_idx[borde]]

                for iid in iids:
                    self._safe_itemconfig(self.canvas_right, iid, image="")
                self._safe_itemconfig(self.canvas_right, target_iid, image=frame)

            if getattr(self, "kraken_head_frames", None):
                if len(self.kraken_head_frames) >= 2:
                    self._kh_frame_idx = (self._kh_frame_idx + 1) % 2
                head_frame = self.kraken_head_frames[self._kh_frame_idx]

                if not getattr(self, "kraken_head_item", None):
                    x, y = self._rand_kraken_head_coords(head_frame)
                    self.kraken_head_item = self.canvas_right.create_image(x, y, image=head_frame, anchor="nw")
                else:
                    self._safe_itemconfig(self.canvas_right, self.kraken_head_item, image=head_frame)
                    self._kh_move_ctr += 1
                    if self._kh_move_ctr >= self._kh_move_every:
                        self._kh_move_ctr = 0
                        x, y = self._rand_kraken_head_coords(head_frame)
                        self._safe_coords(self.canvas_right, self.kraken_head_item, x, y)

        self.animar(800, self._animate_historial_tentacles)
