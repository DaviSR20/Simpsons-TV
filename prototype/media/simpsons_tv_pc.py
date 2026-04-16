import os
import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from pathlib import Path

# --- CONFIGURACIÓN HORIZONTAL (Formato TV 4:3) ---
WIDTH = 640
HEIGHT = 480
FOLDER_EPISODIOS = Path("episodios")

# Crear la carpeta si no existe
if not FOLDER_EPISODIOS.exists():
    FOLDER_EPISODIOS.mkdir()


class EmbeddedPlayer(tk.Frame):
    """Reproductor de vídeo integrado optimizado para 640x480"""

    def __init__(self, parent, video_path, on_close):
        super().__init__(parent, bg="black")
        self.video_path = str(video_path)
        self.on_close = on_close
        self.cap = cv2.VideoCapture(self.video_path)

        # Frame superior para el video
        self.video_frame = tk.Frame(self, bg="black", width=WIDTH, height=HEIGHT - 60)
        self.video_frame.pack(fill="both", expand=True)
        self.video_frame.pack_propagate(False)  # Evita que el frame cambie de tamaño

        self.label = tk.Label(self.video_frame, bg="black")
        self.label.place(relx=0.5, rely=0.5, anchor="center")  # Centrado perfecto

        # Botón inferior
        self.btn_back = tk.Button(
            self, text="DETENER Y VOLVER", command=self.stop,
            bg="#41316f", fg="white", font=("Segoe UI Black", 14), relief="flat", pady=10
        )
        self.btn_back.pack(fill="x", side="bottom")

        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # BGR a RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Redimensionado inteligente manteniendo el ratio (Letterboxing)
            h, w, _ = frame.shape
            ratio = min(WIDTH / w, (HEIGHT - 60) / h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)

            img = Image.fromarray(frame)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            self.photo = ImageTk.PhotoImage(image=img)
            self.label.config(image=self.photo)
            self.after(30, self.update_frame)  # ~30 FPS
        else:
            self.stop()  # Cierra automáticamente al terminar

    def stop(self):
        self.cap.release()
        self.on_close()


class SimpsonsTV:
    def __init__(self, root):
        self.root = root
        self.root.title("Simpsons TV Horizontal")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#130f24")

        self.episodes = self.get_local_episodes()
        self.show_main_menu()

    def get_local_episodes(self):
        """Escanea la carpeta 'episodios' buscando archivos .mp4"""
        files = list(FOLDER_EPISODIOS.glob("*.mp4"))
        episodes = []
        for i, f in enumerate(files, 1):
            episodes.append({
                "id": i,
                "title": f.stem.replace("_", " ").title(),
                "path": f
            })
        return episodes

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear()
        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Configuración de Grid 2x2 para botones táctiles grandes
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        botones = [
            ("VER EPISODIOS", self.show_episodes, 0, 0),
            ("JUEGOS", self.show_placeholder, 0, 1),
            ("AJUSTES RED", self.show_placeholder, 1, 0),
            ("APAGAR", self.root.destroy, 1, 1)
        ]

        for text, cmd, row, col in botones:
            tk.Button(
                container, text=text, command=cmd,
                bg="#f2b929", fg="#1d1635", font=("Segoe UI Black", 18),
                relief="flat"
            ).grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

    def show_episodes(self):
        self.clear()
        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Layout horizontal: Lista a la izquierda, Botones a la derecha
        left_panel = tk.Frame(container, bg="#130f24")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_panel = tk.Frame(container, bg="#130f24", width=180)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        if not self.episodes:
            tk.Label(left_panel, text="No hay videos en la carpeta /episodios\n¡Añade algún .mp4!",
                     fg="#f2b929", bg="#130f24", font=("Segoe UI", 14)).pack(expand=True)
        else:
            lb = tk.Listbox(left_panel, bg="#1a1431", fg="white", font=("Segoe UI", 16),
                            borderwidth=0, selectbackground="#f2b929", selectforeground="#1d1635")
            lb.pack(fill="both", expand=True)

            for ep in self.episodes:
                lb.insert("end", f" Cap. {ep['id']} - {ep['title']}")

            lb.selection_set(0)

            def play_selected():
                selection = lb.curselection()
                if selection:
                    self.play_video(self.episodes[selection[0]])

            tk.Button(right_panel, text="PLAY", command=play_selected,
                      bg="#f2b929", fg="#1d1635", font=("Segoe UI Black", 18), relief="flat").pack(fill="both",
                                                                                                   expand=True,
                                                                                                   pady=(0, 10))

        tk.Button(right_panel, text="VOLVER", command=self.show_main_menu,
                  bg="#41316f", fg="white", font=("Segoe UI Black", 16), relief="flat").pack(fill="both", expand=True,
                                                                                             pady=(10, 0))

    def play_video(self, episode):
        self.clear()
        player = EmbeddedPlayer(self.root, episode["path"], self.show_episodes)
        player.pack(fill="both", expand=True)

    def show_placeholder(self):
        self.clear()
        c = tk.Frame(self.root, bg="#130f24")
        c.pack(fill="both", expand=True)

        tk.Label(c, text="EN DESARROLLO", bg="#130f24", fg="#f2b929", font=("Segoe UI Black", 30)).pack(expand=True)

        tk.Button(c, text="VOLVER AL MENÚ", command=self.show_main_menu,
                  bg="#41316f", fg="white", font=("Segoe UI Black", 18), relief="flat", pady=15).pack(fill="x",
                                                                                                      side="bottom",
                                                                                                      padx=20, pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpsonsTV(root)
    root.mainloop()