from tkinter import Label, PhotoImage, TclError, LEFT, RIGHT
import os

class AnimationMixin:
   
    MAX_CABEZAS = 9  # Ajustar según cantidad máxima de frames superiores de la hidra

    def init_animation(self):
        self.skeleton_images = []
        self.skel_purchase_tiles = []
        self.skel_sale_tiles = []
        idx = 1
        while True:
            path_c = f"imagenes/deco/skeleton_hydra_{idx}_new.png"
            path_v = f"imagenes/deco/skeleton_hydra_{idx}_old.png"
            if not os.path.exists(path_c) and not os.path.exists(path_v):
                break
            if os.path.exists(path_c):
                self.skel_purchase_tiles.append(PhotoImage(file=path_c).zoom(2,2))
            if os.path.exists(path_v):
                self.skel_sale_tiles.append(PhotoImage(file=path_v).zoom(2,2))
            idx += 1
        
        if hasattr(self, 'torch_item'):
            self.torch_frame_index = 0
            self.guard_frame_index = 0
            return

        # --- Antorcha ---
        self.torch_frames = []
        for i in range(1, 5):
            path = f"imagenes/deco/torch_{i}.png"
            if os.path.exists(path):
                try:
                    self.torch_frames.append(PhotoImage(file=path).zoom(3, 3))
                except Exception as e:
                    print(f"Error cargando antorcha frame {path}: {e}")
        self.torch_frame_index = 0

        # --- Guardián ---
        self.guard_open_frames = []
        self.guard_closed_frames = []
        for i in range(1, 5):
            open_path = f"imagenes/deco/guardian-eyeopen-flame_{i}.png"
            closed_path = f"imagenes/deco/guardian-eyeclosed-flame_{i}.png"
            if os.path.exists(open_path):
                try:
                    self.guard_open_frames.append(PhotoImage(file=open_path).zoom(2,2))
                except Exception as e:
                    print(f"Error cargando guardia open frame {open_path}: {e}")
            if os.path.exists(closed_path):
                try:
                    self.guard_closed_frames.append(PhotoImage(file=closed_path).zoom(2,2))
                except Exception as e:
                    print(f"Error cargando guardia closed frame {closed_path}: {e}")
        self.guard_frame_index = 0

        # --- Montones de oro (ventas reales) ---
        piles = list(range(1,11)) + [16,19,23,25]
        self.sales_frames = []
        for n in piles:
            path = f"imagenes/deco/gold_pile_{n}.png"
            if os.path.exists(path):
                try:
                    self.sales_frames.append(PhotoImage(file=path).zoom(2,2))
                except Exception as e:
                    print(f"Error cargando pile {path}: {e}")
        

        # --- Hidra (ventas fantasma) ---
        bottom_indices = [1,5,7,8,9]
        self.hydra_bottom_frames = {}
        for n in bottom_indices:
            path = f"imagenes/deco/lernaean_hydra_{n}_bottom.png"
            if os.path.exists(path):
                try:
                    self.hydra_bottom_frames[n] = PhotoImage(file=path).zoom(2,2)
                except Exception as e:
                    print(f"Error cargando hidra bottom {path}: {e}")
        self.hydra_top_frames = []
        for i in range(1, self.MAX_CABEZAS+1):
            path = f"imagenes/deco/lernaean_hydra_{i}_top.png"
            if not os.path.exists(path):
                break
            try:
                img = PhotoImage(file=path).zoom(2,2)
                self.hydra_top_frames.append(img)
            except Exception as e:
                print(f"Error cargando hidra top {path}: {e}")
                break
       
       



                # — Antorcha —
        first_torch = self.torch_frames[0] if self.torch_frames else None
        self.torch_item = self.canvas_animation.create_image(50, 50,
            image=first_torch, anchor='nw'
        )
                
        # — Guardián —
        first_guard = self.guard_closed_frames[0] if self.guard_closed_frames else None
        self.guard_item = self.canvas_animation.create_image(200, 50,
            image=first_guard, anchor='nw'
        )

        # — Montones de oro (ventas reales) —
        self.sales_item = self.canvas_animation.create_image(350, 50,
            image='', anchor='nw'
        )

        # — Hidra fantasma: bottom & top —
        self.hydra_bottom_item = self.canvas_animation.create_image(500, 200,
            image='', anchor='nw'
        )
        self.hydra_top_item = self.canvas_animation.create_image(500, 150,
            image='', anchor='nw'
        )

        self.skel_purchase_item = self.canvas_animation.create_image(50, 270, image='', anchor='nw')
        self.skel_sale_item = self.canvas_animation.create_image(50, 340, image='', anchor='nw')
        self.imagen_actual_compra = ''
        self.imagen_actual_venta = ''

        self.root.after(500, self._update_skeleton_tiles)


            # … después de crear torch_item, guard_item, sales_item, hydra_items …
        self.root.after(100, self._animate_torch)
        self.root.after(100, self._animate_guard)
        
        self.root.after(500, self._update_hydra_image)


    def _sales_index(self, cnt):
        thresholds = list(range(1,11)) + [16,19,23,25]
        idx = 0
        for i, th in enumerate(thresholds):
            if cnt >= th: idx = i
        return min(idx, len(self.sales_frames)-1)

    def _hydra_bottom_key(self, cnt):
        keys = sorted(self.hydra_bottom_frames)
        lower = [k for k in keys if k <= cnt]
        return lower[-1] if lower else keys[0]

    def _animate_torch(self):
        if not self.torch_frames: return
        self.torch_frame_index = (self.torch_frame_index + 1) % len(self.torch_frames)
        img = self.torch_frames[self.torch_frame_index]
        self.canvas_animation.itemconfig(self.torch_item, image=img)
        self.root.after(100, self._animate_torch)

    def _animate_guard(self):
        frames = (self.bot.running and self.guard_open_frames) or self.guard_closed_frames
        if frames:
            self.guard_frame_index = (self.guard_frame_index + 1) % len(frames)
            self.canvas_animation.itemconfig(self.guard_item, image=frames[self.guard_frame_index])
        self.root.after(100, self._animate_guard)

    def _update_sales_image(self):
        cnt = getattr(self.bot, 'contador_ventas_reales', 0)
        img = '' if cnt < 1 else self.sales_frames[self._sales_index(cnt)]
        self.canvas_animation.itemconfig(self.sales_item, image=img)

    def _update_hydra_image(self):
        cnt = getattr(self.bot, 'contador_ventas_fantasma', 0)

        if cnt < 1:
            top = bottom = ''
        else:
            # bottom dinámico por clave
            if self.hydra_bottom_frames:
                key = self._hydra_bottom_key(cnt)
                bottom = self.hydra_bottom_frames.get(key, '')
            else:
                bottom = ''

            # top: lista indexada
            if self.hydra_top_frames:
                top_idx = min(cnt-1, len(self.hydra_top_frames)-1)
                top = self.hydra_top_frames[top_idx]
            else:
                top = ''

        # Actualizar imágenes (incluso si están vacías)
        self.canvas_animation.itemconfig(self.hydra_bottom_item, image=bottom)
        self.canvas_animation.itemconfig(self.hydra_top_item, image=top)

        self.root.after(500, self._update_hydra_image)

    def _update_skeleton_tiles(self):
        compra_real = getattr(self.bot, 'contador_compras_reales', 0) > 0
        venta_real = getattr(self.bot, 'contador_ventas_reales', 0) > 0

        if self.skel_purchase_tiles and compra_real:
            self.imagen_actual_compra = self.skel_purchase_tiles[0]
        else:
            self.imagen_actual_compra = ''  # mantener la referencia vacía

        if self.skel_sale_tiles and venta_real:
            self.imagen_actual_venta = self.skel_sale_tiles[0]
        else:
            self.imagen_actual_venta = ''

        self.canvas_animation.itemconfig(self.skel_purchase_item, image=self.imagen_actual_compra)
        self.canvas_animation.itemconfig(self.skel_sale_item, image=self.imagen_actual_venta)

        self.root.after(500, self._update_skeleton_tiles)

    



    


