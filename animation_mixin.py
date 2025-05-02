from tkinter import Label, PhotoImage
import os

class AnimationMixin:
    """
    Mixin para manejar animaciones de antorcha, guardián, montones de oro e hidra.
    Debe mezclarse en BotInterface después de definir root, info_frame y center_frame.
    """
    MAX_CABEZAS = 9  # Ajustar según cantidad máxima de frames superiores de la hidra

    def init_animation(self):
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
        # Creamos etiqueta en center_frame
        self.sales_label = Label(self.center_frame, bg="DarkGoldenrod")
        self.sales_label.pack()

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
        # Labels de hidra
        self.hydra_top_label = Label(self.center_frame, bg="DarkGoldenrod", bd=0)
        self.hydra_bottom_label = Label(self.center_frame, bg="DarkGoldenrod", bd=0)
        self.hydra_top_label.pack()
        self.hydra_bottom_label.pack()


        # Inicia bucles de animación y de decor
        self.root.after(100, self._animate_torch)
        self.root.after(100, self._animate_guard)
        self.root.after(500, self._update_decor)

    def _animate_torch(self):
        if getattr(self, 'config_ventana', None) and self.config_ventana and self.config_ventana.winfo_exists():
            # Crear label si no existe o fue destruido
            if not hasattr(self, 'torch_label') or not getattr(self.torch_label, 'winfo_exists', lambda: False)():
                self.torch_label = Label(self.config_ventana, bg="DarkGoldenrod")
                self.torch_label.pack(pady=(8, 0))
            # Actualizar imagen si aún existe
            if self.torch_frames and getattr(self.torch_label, 'winfo_exists', lambda: False)():
                frame = self.torch_frames[self.torch_frame_index]
                try:
                    self.torch_label.configure(image=frame)
                except Exception:
                    # Ignorar si el widget fue destruido
                    pass
                self.torch_frame_index = (self.torch_frame_index + 1) % len(self.torch_frames)
        self.root.after(100, self._animate_torch)

    def _animate_guard(self):
        if not hasattr(self, 'guard_label') or self.guard_label is None:
            # lo creamos una sola vez en info_frame
            self.guard_label = Label(self.info_frame,
                                     image=(self.guard_closed_frames[0] if self.guard_closed_frames else None),
                                     bg="DarkGoldenrod")
            self.guard_label.pack(side="left", anchor="e", padx=5, pady=5)
        running = getattr(self, 'bot', None) and self.bot.running
        frames = self.guard_open_frames if running and self.guard_open_frames else self.guard_closed_frames
        if frames:
            frame = frames[self.guard_frame_index % len(frames)]
            self.guard_label.configure(image=frame)
            self.guard_frame_index = (self.guard_frame_index + 1) % len(frames)
        self.root.after(100, self._animate_guard)

    def _update_decor(self):
        # refresca oro e hidra tras cada compra/venta
        try:
            self._update_sales_image()
            self._update_hydra_image()
        except Exception as e:
            print("Error actualizando decor:", e)
        finally:
            self.root.after(500, self._update_decor)

    def _update_sales_image(self):
        count = getattr(self, 'bot', None) and self.bot.contador_ventas_reales or 0
        if count < 1:
            self.sales_label.configure(image='')
            return
        thresholds = list(range(1,11)) + [16,19,23,25]
        idx = 0
        for i, th in enumerate(thresholds):
            if count >= th:
                idx = i
        idx = min(idx, len(self.sales_frames) - 1)
        self.sales_label.configure(image=self.sales_frames[idx])

    def _update_hydra_image(self):
        count = getattr(self, 'bot', None) and self.bot.contador_ventas_fantasma or 0
        if count < 1:
            self.hydra_bottom_label.configure(image='')
            self.hydra_top_label.configure(image='')
            return
        available = sorted(self.hydra_bottom_frames.keys())
        lower = [n for n in available if n <= count]
        chosen_bottom = lower[-1] if lower else available[0]
        idx_top = min(count-1, len(self.hydra_top_frames)-1)
        self.hydra_top_label.configure(image=self.hydra_top_frames[idx_top])
        self.hydra_bottom_label.configure(image=self.hydra_bottom_frames[chosen_bottom])
