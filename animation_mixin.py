# © 2025 Dungeon Market (Khazâd - Trading Bot)
# Todos los derechos reservados.
from tkinter import PhotoImage
import os

class AnimationMixin:
    MAX_CABEZAS = 9

    def init_animation(self):
        self.cancelar_animaciones()
        if getattr(self, '_animaciones_activas', False):
            return
        self._animaciones_activas = True
        
        if not hasattr(self, "_after_ids"):
            self._after_ids = []

        
        # ─── CARGA DE “ELEFANTES” ───
        # 1) Ruta base de los elefantes
        ruta_ele = os.path.join("imagenes", "deco", "elefants")

        # 2) Carga de la estatua
        stat_path = os.path.join(ruta_ele, "elephant_statue.png")
        self.elephant_statue = PhotoImage(file=stat_path).zoom(3, 3) if os.path.exists(stat_path) else None

        # 3) Carga de los elefantes numerados 0..5
        self.elephants = []
        for i in range(8):
            p = os.path.join(ruta_ele, f"elephant_{i}.png")
            if os.path.exists(p):
                # Aumentamos de tamaño con zoom, si lo deseas
                img = PhotoImage(file=p).zoom(3, 3)
            else:
                img = None
            self.elephants.append(img)

        # 4) Crear el ítem en el canvas_animation (inicialmente con la estatua)
        #    Elegimos una posición fija dentro de canvas_animation; por ejemplo, esquina superior izquierda
        x_ele = 500
        y_ele = 200
        initial_img = self.elephant_statue or (self.elephants[0] if self.elephants[0] else "")
        self.elephant_item = self.canvas_animation.create_image(x_ele, y_ele, image=initial_img, anchor='nw')

        # 5) Programamos la actualización periódica de los elefantes:
        self.animar(500, self._update_elephant)


        # ─── CARGA DE FRAMES ───
        # Antorcha
        self.torch_frames = []
        for i in range(1, 5):
            p = f"imagenes/deco/torch_{i}.png"
            if os.path.exists(p):
                self.torch_frames.append(PhotoImage(file=p).zoom(3,3))
        # Imagen “apagada” si el bot no corre
        off = "imagenes/deco/torch_0.png"
        self.torch_off = PhotoImage(file=off).zoom(3,3) if os.path.exists(off) else None
        self.torch_frame_index = 0

        

        # ─── CARGA DE LÍANAS VERDES Y ROJAS ───
        base_dir = os.path.join("imagenes", "deco", "lianas")
        dirs = {
            "green": os.path.join(base_dir, "verdes"),
            "red":   os.path.join(base_dir, "rojas")
        }
        tokens   = ("north","south","east","west")
        diag_map = {
            "northeast": ("north","east"),
            "northwest": ("north","west"),
            "southeast": ("south","east"),
            "southwest": ("south","west"),
        }

        self.vine_sequence_green = {t: [] for t in tokens}
        self.vine_sequence_red   = {t: [] for t in tokens}

        for color, folder in dirs.items():
            seq_map = self.vine_sequence_green if color=="green" else self.vine_sequence_red
            for fname in os.listdir(folder):
                if not fname.lower().endswith(".png"):
                    continue

                if color=="red":
                    if not fname.startswith("starspawn_"):
                        continue
                    name = fname[len("starspawn_"):-4]
                else:
                    if not fname.startswith("vine_"):
                        continue
                    name = fname[len("vine_"):-4]

                parts = name.split("_")

                if parts[0]=="corner" and len(parts)==2:
                    direcciones = [parts[1]]
                elif parts[0]=="tentacle" and len(parts)==2:
                    direcciones = [parts[1]]
                elif parts[0]=="tentacle" and len(parts)==4 and parts[1]=="segment":
                    direcciones = parts[2:4]
                elif parts[0]=="segment" and len(parts)==3:
                    direcciones = parts[1:3]
                else:
                    continue

                bordes = []
                for d in direcciones:
                    if d in diag_map:
                        bordes += diag_map[d]
                    elif d in tokens:
                        bordes.append(d)

                img = PhotoImage(file=os.path.join(folder, fname)).zoom(2,2)
                for b in set(bordes):
                    seq_map[b].append(img)


#items
        self.vine_items   = []                # (borde, item_id)
        self.vine_indices = {t: 0 for t in tokens}

        # dimensiones del canvas
        W = int(self.canvas_right_b["width"])
        H = int(self.canvas_right_b["height"])

        # calculamos anchuras y altos (usamos uno de los mapas, da igual)
        width_top    = self.vine_sequence_green["north"][0].width()  if self.vine_sequence_green["north"] else 0
        width_bottom = self.vine_sequence_green["south"][0].width()  if self.vine_sequence_green["south"] else 0
        height_left  = self.vine_sequence_green["west"][0].height()  if self.vine_sequence_green["west"] else 0
        height_right = self.vine_sequence_green["east"][0].height()  if self.vine_sequence_green["east"] else 0
        width_right  = self.vine_sequence_green["east"][0].width()   if self.vine_sequence_green["east"] else 0

      

        if width_top > 0:
            for x in range(0, W, width_top):
                iid = self.canvas_right_b.create_image(
                    x, 0,
                    image='',     # arranca vacío
                    anchor="nw"
                )
                self.vine_items.append(("north", iid))

        if width_bottom > 0:
            for x in range(0, W, width_bottom):
                iid = self.canvas_right_b.create_image(
                    x, H,
                    image='',     # arranca vacío
                    anchor="sw"
                )
                self.vine_items.append(("south", iid))

        if height_left > 0:
            for y in range(0, H, height_left):
                iid = self.canvas_right_b.create_image(
                    0, y,
                    image='',     # arranca vacío
                    anchor="nw"
                )
                self.vine_items.append(("west", iid))

        if width_right > 0:
            x0 = W - width_right
            for y in range(0, H, height_right):
                iid = self.canvas_right_b.create_image(
                    x0, y,
                    image='',     # arranca vacío
                    anchor="nw"
                )
                self.vine_items.append(("east", iid))


        
        # —————— (1) Carga de los iconos de sonido ——————
        on_path  = "imagenes/deco/i-noise_new.png"
        off_path = "imagenes/deco/i-noise_old.png"
        self.noise_on  = PhotoImage(file=on_path).zoom(2,2)  if os.path.exists(on_path)  else None
        self.noise_off = PhotoImage(file=off_path).zoom(2,2) if os.path.exists(off_path) else None



        self._hydra_gate = "imagenes/deco/gates/enter_snake.png"
        self.hydra_gate = PhotoImage(file=self._hydra_gate).zoom(4,4) if os.path.exists(self._hydra_gate) else None

        # Guardián
        self.guard_open_frames = []
        self.guard_closed_frames = []
        for i in range(1, 5):
            po = f"imagenes/deco/guardian-eyeopen-flame_{i}.png"
            pc = f"imagenes/deco/guardian-eyeclosed-flame_{i}.png"
            if os.path.exists(po):
                self.guard_open_frames.append(PhotoImage(file=po).zoom(2,2))
            if os.path.exists(pc):
                self.guard_closed_frames.append(PhotoImage(file=pc).zoom(2,2))
        self.guard_frame_index = 0
#abyssal gate
        self.abyss_frames = []
        for i in range(1, 4):
            path = "imagenes/deco/gates/abyss/enter_abyss_{}.png".format(i)
            if os.path.exists(path):
                self.abyss_frames.append(PhotoImage(file=path).zoom(3, 3))

        # Imagen estática (cuando está desactivado)
        abyss_static = "imagenes/deco/gates/abyss/enter_abyss.png"
        self.abyss_static_img = PhotoImage(file=abyss_static).zoom(3, 3) if os.path.exists(abyss_static) else None

        # Índice para animación
        self.abyss_frame_index = 0

# dithmenos
        self.dithmenos_frames = []
        for name in ("dithmenos.png", "dithmenos_2.png", "dithmenos_3.png"):
            path = os.path.join("imagenes", "deco", name)
            if os.path.exists(path):
                self.dithmenos_frames.append(PhotoImage(file=path).zoom(2,2))
        self.dithmenos_index = 0

        # Montones de oro (ventas reales)
        piles = list(range(1,11)) + [16,19,23,25]
        self.sales_frames = []
        for n in piles:
            p = f"imagenes/deco/gold_pile_{n}.png"
            if os.path.exists(p):
                self.sales_frames.append(PhotoImage(file=p).zoom(2,2))

        # Hidra (ventas fantasma)
        bottom_idxs = [1,5,7,8,9]
        self.hydra_bottom = {}
        for n in bottom_idxs:
            p = f"imagenes/deco/lernaean_hydra_{n}_bottom.png"
            if os.path.exists(p):
                self.hydra_bottom[n] = PhotoImage(file=p).zoom(2,2)
        self.hydra_top = []
        for i in range(1, self.MAX_CABEZAS+1):
            p = f"imagenes/deco/lernaean_hydra_{i}_top.png"
            if not os.path.exists(p): break
            self.hydra_top.append(PhotoImage(file=p).zoom(2,2))

        # Esqueleto hidra (compras/ventas)
        self.skel_buy  = []
        self.skel_sell = []
        idx = 1
        while True:
            nb = f"imagenes/deco/skeleton_hydra_{idx}_new.png"
            ns = f"imagenes/deco/skeleton_hydra_{idx}_old.png"
            if not os.path.exists(nb) and not os.path.exists(ns): break
            if os.path.exists(nb): self.skel_buy.append(PhotoImage(file=nb).zoom(2,2))
            if os.path.exists(ns): self.skel_sell.append(PhotoImage(file=ns).zoom(2,2))
            idx += 1

        # ─── CREACIÓN DE ITEMS ───
        # Antorcha en canvas_center
        first_torch = self.torch_frames[0] if self.torch_frames else self.torch_off
        self.torch_item = self.canvas_center.create_image(350,250, image=first_torch, anchor='nw')

        
        
        self.hydra_gate_f = self.canvas_center.create_image(200,320, image=self.hydra_gate, anchor='nw')
        

        

        # Guardián en canvas_various
        guard0 = self.guard_closed_frames[0] if self.guard_closed_frames else None
        self.guard_item = self.canvas_various.create_image(1800,15, image=guard0, anchor='nw')

         # 2) Crea el item en el canvas
        if self.dithmenos_frames:
            self.dithmenos_item = self.canvas_center.create_image(
                0, 390,
                image=self.dithmenos_frames[0],
                anchor='nw'
            )

        
        
        # item sound
        initial = self.noise_on if getattr(self, 'sound_enabled', True) else self.noise_off
        self.noise_item = self.canvas_various.create_image(
            1500, 10,
            image=initial,
            anchor='nw'
        )

            
        self._after_ids = []

        # Oro e hidra en canvas_animation
        self.sales_item       = self.canvas_various.create_image(1350,15,  image='', anchor='nw')

        self.hydra_bottom_it  = self.canvas_center.create_image(230,400, image='', anchor='nw')
        self.hydra_top_it     = self.canvas_center.create_image(230,350, image='', anchor='nw')

        # Esqueleto hidra en canvas_center
        self.skel_buy_it  = self.canvas_center.create_image(360,385, image='', anchor='nw')
        self.skel_sell_it = self.canvas_center.create_image(100,385, image='', anchor='nw')

        # abyssal gate
        
        # Crear imagen inicial
        initial_g = self.abyss_static_img or (self.abyss_frames[0] if self.abyss_frames else "")
        self.abyss_item = self.canvas_center.create_image(590, 350, image=initial_g, anchor='nw')

        # Garantizar que esté al frente después de que todo cargue
        #self.canvas_uno.tag_raise(self.abyss_item)


        # ─── BUQUES INDEPENDIENTES ───
        self.animar(100,  self._animate_torch)
        self.animar(100,  self._animate_guard)
        self.animar(1000, self._animate_dithmenos)
        self.animar(500,  self._update_sales)
        self.animar(500,  self._update_hydra)
        self.animar(500,  self._update_skeleton)
        self.animar(200, self._update_noise_icon)
        self.animar(250, self._animate_vines)
        self.animar(500, self._update_abyss)

    def _is_valid_image_item(self, canvas, item_id):
        try:
            return canvas.type(item_id) == 'image'
        except Exception:
            return False

    def cancelar_animaciones(self):
        if not hasattr(self, '_after_ids'):
            self._after_ids = []
            return  # No hay nada que cancelar aún

        for aid in self._after_ids:
            try:
                self.root.after_cancel(aid)
            except Exception:
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

    def _update_abyss(self):
        usar_animacion = getattr(self.bot, 'compra_en_venta_fantasma', False)
        if usar_animacion and self.abyss_frames:
            frame, self.abyss_frame_index = self._safe_next_frame(self.abyss_frames, self.abyss_frame_index)
            self.canvas_center.itemconfig(self.abyss_item, image=frame)
        elif self.abyss_static_img:
            self.canvas_center.itemconfig(self.abyss_item, image=self.abyss_static_img)

        self.animar(500, self._update_abyss)

   
    def _update_elephant(self):
        """
        Cada 500 ms revisamos self.bot.contador_compras_fantasma y reemplazamos la imagen:
        - Si contador == 0: mostramos elephant_statue.
        - Si 1 <= contador <= 6: mostramos elephants[contador-1] (o clamp a max índice).
        - Si contador > 6, mostramos siempre elephant_5.
        """
        cnt = getattr(self, 'bot', None) and self.bot.contador_compras_fantasma or 0

        if cnt <= 0:
            img = self.elephant_statue
        elif 1 <= cnt <= 8:
            # Mapeamos “1 compra fantasma” → elephants[0], “2” → elephants[1], … hasta elephants[7]
            idx = min(cnt-1, len(self.elephants)-1)
            img = self.elephants[idx]
        else:
            # Si hay más de 8 compras fantasma, mostramos siempre el último elefante
            img = self.elephants[-1]

        if img:
            self.canvas_animation.itemconfig(self.elephant_item, image=img)

        # Volver a programar dentro de 500 ms
        self.animar(500, self._update_elephant)


    def _animate_torch(self):
        if self.bot and self.bot.running and self.torch_frames:
            frame, self.torch_frame_index = self._safe_next_frame(self.torch_frames, self.torch_frame_index)
        else:
            frame = self.torch_off
        if frame and self.canvas_center.type(self.torch_item) == 'image':
            self.canvas_center.itemconfig(self.torch_item, image=frame)
        self.animar(100, self._animate_torch)

    def _update_noise_icon(self):
        frame = self.noise_on if getattr(self, 'sound_enabled', True) else self.noise_off
        if frame and self.canvas_various.type(self.noise_item) == 'image':
            self.canvas_various.itemconfig(self.noise_item, image=frame)
        self.animar(200, self._update_noise_icon)

    def _animate_guard(self):
        frames = self.guard_open_frames if self.bot and self.bot.running else self.guard_closed_frames
        if frames:
            frame, self.guard_frame_index = self._safe_next_frame(frames, self.guard_frame_index)
            if frame and self.canvas_various.type(self.guard_item) == 'image':
                self.canvas_various.itemconfig(self.guard_item, image=frame)
        self.animar(100, self._animate_guard)

    def _sales_index(self, cnt):
        ths = list(range(1,11)) + [16,19,23,25]
        idx = 0
        for i, t in enumerate(ths):
            if cnt >= t: idx = i
        return min(idx, len(self.sales_frames)-1)

    def _update_sales(self):
        cnt = getattr(self, 'bot', None) and self.bot.contador_ventas_reales or 0
        img = self.sales_frames[self._sales_index(cnt)] if cnt>0 else ''
        self.canvas_various.itemconfig(self.sales_item, image=img)
        self.animar(500, self._update_sales)

    def _hydra_key(self, cnt):
        keys = sorted(self.hydra_bottom)
        lower = [k for k in keys if k<=cnt]
        return (lower or keys)[-1]

    def _update_hydra(self):
        cnt = getattr(self, 'bot', None) and self.bot.contador_ventas_fantasma or 0
        if cnt > 0:
            key = self._hydra_key(cnt)
            bot_img = self.hydra_bottom.get(key)
            top_img = self.hydra_top[min(cnt - 1, len(self.hydra_top) - 1)] if self.hydra_top else None
        else:
            bot_img = top_img = None

        if bot_img and self._is_valid_image_item(self.canvas_center, self.hydra_bottom_it):
            self.canvas_center.itemconfig(self.hydra_bottom_it, image=bot_img)
        if top_img and self._is_valid_image_item(self.canvas_center, self.hydra_top_it):
            self.canvas_center.itemconfig(self.hydra_top_it, image=top_img)

        self.animar(500, self._update_hydra)


    def _update_skeleton(self):
        buy = getattr(self, 'bot', None) and self.bot.contador_compras_reales or 0
        sell = getattr(self, 'bot', None) and self.bot.contador_ventas_reales or 0

        img_b = self.skel_buy[min(buy - 1, len(self.skel_buy) - 1)] if buy > 0 and self.skel_buy else None
        img_s = self.skel_sell[min(sell - 1, len(self.skel_sell) - 1)] if sell > 0 and self.skel_sell else None

        if img_b and self._is_valid_image_item(self.canvas_center, self.skel_buy_it):
            self.canvas_center.itemconfig(self.skel_buy_it, image=img_b)
        if img_s and self._is_valid_image_item(self.canvas_center, self.skel_sell_it):
            self.canvas_center.itemconfig(self.skel_sell_it, image=img_s)

        self.animar(500, self._update_skeleton)


    def _animate_dithmenos(self):
        if self.dithmenos_frames:
            frame, self.dithmenos_index = self._safe_next_frame(self.dithmenos_frames, self.dithmenos_index)
            if frame and self.canvas_center.type(self.dithmenos_item) == 'image':
                self.canvas_center.itemconfig(self.dithmenos_item, image=frame)
        self.animar(1000, self._animate_dithmenos)

    def _animate_vines(self):
        if not hasattr(self, 'vine_items') or not hasattr(self, 'vine_indices'):
            self.animar(12000, self._animate_vines)
            return

        # Usar secuencia según la variación
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
                img = None  # oculta
            else:
                frames = seq_map[border]
                idx = (self.vine_indices[border] + 1) % len(frames)
                self.vine_indices[border] = idx
                img = frames[idx]

            if img and self.canvas_right_b.type(iid) == 'image':
                self.canvas_right_b.itemconfig(iid, image=img)

        self.animar(12000, self._animate_vines)


