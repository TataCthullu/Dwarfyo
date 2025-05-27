
from tkinter import PhotoImage
import os

class AnimationMixin:
    MAX_CABEZAS = 9

    def init_animation(self):
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

        # ─── CARGA DE LÍANAS ───
        deco_dir = os.path.join("imagenes", "deco")
        files = [f for f in os.listdir(deco_dir)
                 if f.startswith("vine_segment") and f.endswith(".png")]

        # Bordes válidos
        tokens   = ("north","south","east","west")
        diag_map = {
            "northeast": ("north","east"),
            "northwest": ("north","west"),
            "southeast": ("south","east"),
            "southwest": ("south","west"),
        }

        # Prepara contenedores
        segments = {t: [] for t in tokens}

        # Clasifica cada imagen en uno o varios bordes
        for fname in files:
            keyname = fname[len("vine_segment_"):-4]  # e.g. "northeast_south"
            parts   = keyname.split("_")              # ["northeast","south"]
            path    = os.path.join(deco_dir, fname)
            img     = PhotoImage(file=path).zoom(2,2)

            for part in parts:
                if part in diag_map:
                    # e.g. "northeast" → añade a north y east
                    for b in diag_map[part]:
                        segments[b].append(img)
                elif part in segments:
                    segments[part].append(img)
                # resto de combinaciones se ignoran

        # ─── PREP PARA ANIMAR ───
        self.vine_sequence = segments
        self.vine_items    = []  # (borde, item_id)
        self.vine_indices  = {b: 0 for b in segments}

        # dimensiones del canvas de la consola (right_panel_b)
        W = int(self.canvas_right_b["width"])
        H = int(self.canvas_right_b["height"])

        # ancho de tile para top/bottom (toma del primer frame disponible)
        width_top    = segments["north"][0].width()  if segments["north"] else 0
        width_bottom = segments["south"][0].width()  if segments["south"] else 0
        # alto de tile para left/right
        height_left  = segments["west"][0].height()  if segments["west"] else 0
        height_right = segments["east"][0].height()  if segments["east"] else 0

        # —————— (1) Carga de los iconos de sonido ——————
        on_path  = "imagenes/deco/i-noise_new.png"
        off_path = "imagenes/deco/i-noise_old.png"
        self.noise_on  = PhotoImage(file=on_path)  if os.path.exists(on_path)  else None
        self.noise_off = PhotoImage(file=off_path) if os.path.exists(off_path) else None

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

        # ─── ÍTEMS liana ───
        # Norte
        if width_top:
            for x in range(0, W, width_top):
                img0 = segments["north"][0]
                iid  = self.canvas_right_b.create_image(x, 0, image=img0, anchor="nw")
                self.vine_items.append(("north", iid))

        # Sur
        if width_bottom:
            y0 = H - (segments["south"][0].height())
            for x in range(0, W, width_bottom):
                img0 = segments["south"][0]
                iid  = self.canvas_right_b.create_image(x, y0, image=img0, anchor="nw")
                self.vine_items.append(("south", iid))

        # Oeste
        if height_left:
            for y in range(0, H, height_left):
                img0 = segments["west"][0]
                iid  = self.canvas_right_b.create_image(0, y, image=img0, anchor="nw")
                self.vine_items.append(("west", iid))

        # Este
        if height_right:
            x0 = W - (segments["east"][0].width())
            for y in range(0, H, height_right):
                img0 = segments["east"][0]
                iid  = self.canvas_right_b.create_image(x0, y, image=img0, anchor="nw")
                self.vine_items.append(("east", iid))

        



        # Guardián en canvas_uno
        guard0 = self.guard_closed_frames[0] if self.guard_closed_frames else None
        self.guard_item = self.canvas_uno.create_image(0,830, image=guard0, anchor='nw')

         # 2) Crea el item en el canvas
        if self.dithmenos_frames:
            self.dithmenos_item = self.canvas_center.create_image(
                0, 390,
                image=self.dithmenos_frames[0],
                anchor='nw'
            )

        # 3) Arranca tu bucle propio
        #if hasattr(self, 'dithmenos_item'):
        
        # item sound
        initial = self.noise_on if getattr(self, 'sound_enabled', True) else self.noise_off
        self.noise_item = self.canvas_animation.create_image(
            10, 10,
            image=initial,
            anchor='nw'
        )

            

        # Oro e hidra en canvas_animation
        self.sales_item       = self.canvas_animation.create_image(350,50,  image='', anchor='nw')
        self.hydra_bottom_it  = self.canvas_animation.create_image(500,200, image='', anchor='nw')
        self.hydra_top_it     = self.canvas_animation.create_image(500,150, image='', anchor='nw')

        # Esqueleto hidra en canvas_animation
        self.skel_buy_it  = self.canvas_animation.create_image(50,270, image='', anchor='nw')
        self.skel_sell_it = self.canvas_animation.create_image(50,340, image='', anchor='nw')

        # ─── BUQUES INDEPENDIENTES ───
        self.root.after(100,  self._animate_torch)
        self.root.after(100,  self._animate_guard)
        self.root.after(250, self._animate_dithmenos)
        self.root.after(500,  self._update_sales)
        self.root.after(500,  self._update_hydra)
        self.root.after(500,  self._update_skeleton)
        self.root.after(200, self._update_noise_icon)
       
        self.root.after(3000, self._animate_vines)

        

    def _animate_torch(self):
        # Si bot.running: ciclo normal; si no: imagen apagada
        if getattr(self, 'bot', None) and self.bot.running and self.torch_frames:
            self.torch_frame_index = (self.torch_frame_index + 1) % len(self.torch_frames)
            img = self.torch_frames[self.torch_frame_index]
        else:
            img = self.torch_off
        self.canvas_center.itemconfig(self.torch_item, image=img)
        self.root.after(100, self._animate_torch)

    def _update_noise_icon(self):
        # Elige imagen según bandera
        if getattr(self, 'sound_enabled', True):
            img = self.noise_on
        else:
            img = self.noise_off

        # Actualiza sólo el image del canvas
        if img:
            self.canvas_animation.itemconfig(self.noise_item, image=img)

        # Vuelve a revisarlo cada 200 ms (o el intervalo que prefieras)
        self.root.after(200, self._update_noise_icon)    

    def _animate_guard(self):
        frames = (self.bot.running and self.guard_open_frames) or self.guard_closed_frames
        if frames:
            self.guard_frame_index = (self.guard_frame_index + 1) % len(frames)
            self.canvas_uno.itemconfig(self.guard_item, image=frames[self.guard_frame_index])
        self.root.after(100, self._animate_guard)

    def _sales_index(self, cnt):
        ths = list(range(1,11)) + [16,19,23,25]
        idx = 0
        for i, t in enumerate(ths):
            if cnt >= t: idx = i
        return min(idx, len(self.sales_frames)-1)

    def _update_sales(self):
        cnt = getattr(self, 'bot', None) and self.bot.contador_ventas_reales or 0
        img = self.sales_frames[self._sales_index(cnt)] if cnt>0 else ''
        self.canvas_animation.itemconfig(self.sales_item, image=img)
        self.root.after(500, self._update_sales)

    def _hydra_key(self, cnt):
        keys = sorted(self.hydra_bottom)
        lower = [k for k in keys if k<=cnt]
        return (lower or keys)[-1]

    def _update_hydra(self):
        cnt = getattr(self, 'bot', None) and self.bot.contador_ventas_fantasma or 0
        if cnt>0:
            bot_img = self.hydra_bottom[self._hydra_key(cnt)]
            top_img = self.hydra_top[min(cnt-1, len(self.hydra_top)-1)]
        else:
            bot_img = top_img = ''
        self.canvas_animation.itemconfig(self.hydra_bottom_it, image=bot_img)
        self.canvas_animation.itemconfig(self.hydra_top_it,    image=top_img)
        self.root.after(500, self._update_hydra)

    def _update_skeleton(self):
        buy  = getattr(self, 'bot', None) and self.bot.contador_compras_reales or 0
        sell = getattr(self, 'bot', None) and self.bot.contador_ventas_reales or 0
        img_b = self.skel_buy[min(buy-1, len(self.skel_buy)-1)] if buy>0 else ''
        img_s = self.skel_sell[min(sell-1, len(self.skel_sell)-1)] if sell>0 else ''
        self.canvas_animation.itemconfig(self.skel_buy_it,  image=img_b)
        self.canvas_animation.itemconfig(self.skel_sell_it, image=img_s)
        self.root.after(500, self._update_skeleton)

    def _animate_dithmenos(self):
        # Avanza el frame
        self.dithmenos_index = (self.dithmenos_index + 1) % len(self.dithmenos_frames)
        # Actualiza la imagen
        self.canvas_center.itemconfig(
            self.dithmenos_item,
            image=self.dithmenos_frames[self.dithmenos_index]
        )
        # Reprograma la siguiente actualización
        self.root.after(250, self._animate_dithmenos)

    def _animate_vines(self):
        for border, iid in self.vine_items:
            seq = self.vine_sequence.get(border, [])
            if not seq: 
                continue
            idx = (self.vine_indices[border] + 1) % len(seq)
            self.vine_indices[border] = idx
            self.canvas_right_b.itemconfig(iid, image=seq[idx])
        self.root.after(3000, self._animate_vines)
