from tkinter import PhotoImage
import os

class AnimationMixin:
   
    MAX_CABEZAS = 9  # Ajustar según cantidad máxima de frames superiores de la hidra

    def init_animation(self):
        # ✅ Salir si ya fueron cargados los elementos gráficos
        if hasattr(self, 'torch_item') and hasattr(self, 'guard_open_frames'):
            return
        
        self.skeleton_images = []
        self.skel_purchase_tiles = []
        self.skel_sale_tiles = []
        self.imagen_actual_oro = ''
    
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

        # --- Imagen antorcha apagada (torch_0.png) ---
        
        path_off = "imagenes/deco/torch_0.png"
        if os.path.exists(path_off):
            try:
                self.torch_off_image = PhotoImage(file=path_off).zoom(3, 3)
            except Exception as e:
                print(f"Error cargando antorcha apagada: {e}")

        

        


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
        self.torch_item = self.canvas_center.create_image(250, 250,
            image=first_torch, anchor='nw'
        )
                
         # --- Guardián ---
        self.guard_open_frames = []
        self.guard_closed_frames = []
        for i in range(1, 5):
            open_path = f"imagenes/deco/guardian-eyeopen-flame_{i}.png"
            closed_path = f"imagenes/deco/guardian-eyeclosed-flame_{i}.png"
            if os.path.exists(open_path):
                try:
                    self.guard_open_frames.append(PhotoImage(file=open_path).zoom(2, 2))
                except Exception as e:
                    print(f"Error cargando guardia open frame {open_path}: {e}")
            if os.path.exists(closed_path):
                try:
                    self.guard_closed_frames.append(PhotoImage(file=closed_path).zoom(2, 2))
                except Exception as e:
                    print(f"Error cargando guardia closed frame {closed_path}: {e}")
        self.guard_frame_index = 0
        # Guardián en canvas_uno
        # ✅ Solo crear la imagen si hay frames cargados
        if self.guard_closed_frames:
            self.guard_image_actual = self.guard_closed_frames[0]
            self.guard_item = self.canvas_uno.create_image(500, 750, image=self.guard_image_actual, anchor='nw')
            self.guard_referencia_img = self.guard_image_actual




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
        self.root.after(500, self._update_sales_image)
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
        if not hasattr(self, 'canvas_center') or not hasattr(self, 'torch_item'):
            self.root.after(500, self._animate_torch)
            return

        if not self.bot.running:
            if self.torch_off_image:
                self.canvas_center.itemconfig(self.torch_item, image=self.torch_off_image)
            self.root.after(500, self._animate_torch)
            return

        if not self.torch_frames:
            return

        self.torch_frame_index = (self.torch_frame_index + 1) % len(self.torch_frames)
        img = self.torch_frames[self.torch_frame_index]
        self.canvas_center.itemconfig(self.torch_item, image=img)
        self.root.after(100, self._animate_torch)



    def _animate_guard(self):
        if not hasattr(self, 'canvas_uno') or not hasattr(self, 'guard_item'):
            self.root.after(100, self._animate_guard)
            return

        frames = (self.bot.running and self.guard_open_frames) or self.guard_closed_frames
        if frames:
            self.guard_frame_index = (self.guard_frame_index + 1) % len(frames)
            img = frames[self.guard_frame_index]
            self.guard_image_actual = img
            self.guard_referencia_img = img  # mantener referencia viva
            self.canvas_uno.itemconfig(self.guard_item, image=img)

            
        
        self.root.after(100, self._animate_guard)



    def _update_sales_image(self):
        cnt = getattr(self.bot, 'contador_ventas_reales', 0)
        if cnt < 1 or not self.sales_frames:
            self.imagen_actual_oro = ''
        else:
            idx = self._sales_index(cnt)
            self.imagen_actual_oro = self.sales_frames[idx]
        self.canvas_animation.itemconfig(self.sales_item, image=self.imagen_actual_oro)

        self.root.after(500, self._update_sales_image)



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
        comp_count = getattr(self.bot, 'contador_compras_reales', 0)
        vent_count = getattr(self.bot, 'contador_ventas_reales', 0)

        if self.skel_purchase_tiles and comp_count > 0:
            idx = min(comp_count - 1, len(self.skel_purchase_tiles) - 1)
            self.imagen_actual_compra = self.skel_purchase_tiles[idx]
        else:
            self.imagen_actual_compra = ''

        if self.skel_sale_tiles and vent_count > 0:
            idx = min(vent_count - 1, len(self.skel_sale_tiles) - 1)
            self.imagen_actual_venta = self.skel_sale_tiles[idx]
        else:
            self.imagen_actual_venta = ''

        self.canvas_animation.itemconfig(self.skel_purchase_item, image=self.imagen_actual_compra)
        self.canvas_animation.itemconfig(self.skel_sale_item, image=self.imagen_actual_venta)

        self.root.after(500, self._update_skeleton_tiles)


    



    


