from tkinter import Label, PhotoImage, TclError, LEFT, RIGHT
import os

class AnimationMixin:
    """
    Mixin para manejar animaciones de antorcha, guardián, montones de oro e hidra.
    Debe mezclarse en BotInterface después de definir root, info_frame y center_frame.
    """
    MAX_CABEZAS = 9  # Ajustar según cantidad máxima de frames superiores de la hidra

    def init_animation(self):
        # Placeholder para los skeleton frames
        self.skel_purchase_frames = []
        self.skel_sale_frames     = []

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
       
        # Arrancar actualización periódica
        self.root.after(500, self._update_skel_hydra)



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

        # — Esqueletos hydra (compras/ventas reales) —
        first_sk = self.skel_purchase_frames[0] if self.skel_purchase_frames else None
        self.skel_purchase_item = self.canvas_animation.create_image(650,  50,
            image=first_sk, anchor='ne'
        )
        self.skel_sale_item     = self.canvas_animation.create_image(650, 100,
            image='',   anchor='ne'
        )

            # … después de crear torch_item, guard_item, sales_item, hydra_items …
        self.root.after(100, self._animate_torch)
        self.root.after(100, self._animate_guard)
        self.root.after(500, self._update_decor)
        self.root.after(500, self._update_skel_hydra)


    


    def init_skeleton_hydra(self):
        # Cargar frames skeleton hydra compra (new) y venta (old)
        self.skel_purchase_frames = []
        self.skel_sale_frames = []
        idx = 1
        while True:
            new_path = f"imagenes/deco/skeleton_hydra_{idx}_new.png"
            old_path = f"imagenes/deco/skeleton_hydra_{idx}_old.png"
            if not os.path.exists(new_path) and not os.path.exists(old_path):
                break
            if os.path.exists(new_path):
                self.skel_purchase_frames.append(PhotoImage(file=new_path).zoom(2,2))
            if os.path.exists(old_path):
                self.skel_sale_frames.append(PhotoImage(file=old_path).zoom(2,2))
            idx += 1
        # Crea los items en el canvas
        first_sk = self.skel_purchase_frames[0] if self.skel_purchase_frames else ''
        self.skel_purchase_item = self.canvas_animation.create_image(650,  50, image=first_sk, anchor='ne')
        self.skel_sale_item     = self.canvas_animation.create_image(650, 100, image='',     anchor='ne')

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
            bottom = self.hydra_bottom_frames[self._hydra_bottom_key(cnt)]
            top_idx = min(cnt-1, len(self.hydra_top_frames)-1)
            top    = self.hydra_top_frames[top_idx]
        self.canvas_animation.itemconfig(self.hydra_bottom_item, image=bottom)
        self.canvas_animation.itemconfig(self.hydra_top_item,    image=top)

    def _update_skel_hydra(self):
        pur = getattr(self.bot, 'contador_compras_reales', 0)
        if pur > 0 and self.skel_purchase_frames:
            idx = min(pur-1, len(self.skel_purchase_frames)-1)
            img = self.skel_purchase_frames[idx]
        else:
            img = ''
        self.canvas_animation.itemconfig(self.skel_purchase_item, image=img)

        sel = getattr(self.bot, 'contador_ventas_reales', 0)
        if sel > 0 and self.skel_sale_frames:
            idx2 = min(sel-1, len(self.skel_sale_frames)-1)
            img2 = self.skel_sale_frames[idx2]
        else:
            img2 = ''
        self.canvas_animation.itemconfig(self.skel_sale_item, image=img2)
        self.root.after(500, self._update_skel_hydra)

    def _update_decor(self):
        try:
            self._update_sales_image()
            self._update_hydra_image()
        except Exception as e:
            print("Error actualizando decor:", e)
        finally:
            self.root.after(500, self._update_decor)




