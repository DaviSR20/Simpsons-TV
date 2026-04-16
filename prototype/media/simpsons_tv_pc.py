import os
import platform

# PARCHE PARA ENCONTRAR VLC EN WINDOWS
if platform.system() == "Windows":
    # Cambia esta ruta si instalaste VLC en otro sitio
    vlc_path = r"C:\Program Files\VideoLAN\VLC"
    if os.path.exists(vlc_path):
        os.add_dll_directory(vlc_path)

import tkinter as tk
from pathlib import Path
import vlc  # Importante: requiere tener VLC instalado en el sistema
import platform

# --- CONFIGURACIÓN HORIZONTAL ---
WIDTH = 640
HEIGHT = 480
FOLDER_EPISODIOS = Path("episodios")

if not FOLDER_EPISODIOS.exists():
    FOLDER_EPISODIOS.mkdir()


class VLCPlayer(tk.Frame):
    """Reproductor de vídeo con Audio usando el motor de VLC"""

    def __init__(self, parent, video_path, on_close):
        super().__init__(parent, bg="black")
        self.on_close = on_close

        # Área de vídeo
        self.video_canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.video_canvas.pack(fill="both", expand=True)

        # Botón inferior para volver
        self.btn_back = tk.Button(
            self, text="DETENER Y VOLVER", command=self.stop,
            bg="#41316f", fg="white", font=("Segoe UI Black", 14), relief="flat", pady=10
        )
        self.btn_back.pack(fill="x", side="bottom")

        # Crear instancia de VLC
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Cargar el vídeo
        media = self.instance.media_new(str(video_path))
        self.player.set_media(media)

        # "Inyectar" el vídeo de VLC dentro del Canvas de Tkinter
        # Esto depende del sistema operativo
        win_id = self.video_canvas.winfo_id()
        if platform.system() == "Windows":
            self.player.set_hwnd(win_id)
        else:
            self.player.set_xwindow(win_id)

        self.player.play()

    def stop(self):
        self.player.stop()
        self.player.release()
        self.instance.release()
        self.on_close()


class SimpsonsTV:
    def __init__(self, root):
        self.root = root
        self.root.title("Simpsons TV con Audio")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg="#130f24")

        self.episodes = self.get_local_episodes()
        self.show_main_menu()

    def get_local_episodes(self):
        files = list(FOLDER_EPISODIOS.glob("*.mp4"))
        return [{"id": i + 1, "title": f.stem.replace("_", " ").title(), "path": f} for i, f in enumerate(files)]

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear()
        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        container.columnconfigure((0, 1), weight=1)
        container.rowconfigure((0, 1), weight=1)

        botones = [
            ("VER EPISODIOS", self.show_episodes, 0, 0),
            ("JUEGOS", self.show_placeholder, 0, 1),
            ("AJUSTES RED", self.show_placeholder, 1, 0),
            ("APAGAR", self.root.destroy, 1, 1)
        ]

        for text, cmd, row, col in botones:
            tk.Button(container, text=text, command=cmd, bg="#f2b929", fg="#1d1635",
                      font=("Segoe UI Black", 18), relief="flat").grid(row=row, column=col, sticky="nsew", padx=10,
                                                                       pady=10)

    def show_episodes(self):
        self.clear()
        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        left_panel = tk.Frame(container, bg="#130f24")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_panel = tk.Frame(container, bg="#130f24", width=180)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        if not self.episodes:
            tk.Label(left_panel, text="Carpeta /episodios vacía", fg="#f2b929", bg="#130f24",
                     font=("Segoe UI", 14)).pack(expand=True)
        else:
            lb = tk.Listbox(left_panel, bg="#1a1431", fg="white", font=("Segoe UI", 16), borderwidth=0,
                            selectbackground="#f2b929", selectforeground="#1d1635")
            lb.pack(fill="both", expand=True)
            for ep in self.episodes:
                lb.insert("end", f" Cap. {ep['id']} - {ep['title']}")
            lb.selection_set(0)

            def play_selected():
                if lb.curselection():
                    self.play_video(self.episodes[lb.curselection()[0]])

            tk.Button(right_panel, text="PLAY", command=play_selected, bg="#f2b929", fg="#1d1635",
                      font=("Segoe UI Black", 18), relief="flat").pack(fill="both", expand=True, pady=(0, 10))

        tk.Button(right_panel, text="VOLVER", command=self.show_main_menu, bg="#41316f", fg="white",
                  font=("Segoe UI Black", 16), relief="flat").pack(fill="both", expand=True, pady=(10, 0))

    def play_video(self, episode):
        self.clear()
        # El reproductor de VLC se encarga de todo
        VLCPlayer(self.root, episode["path"], self.show_episodes).pack(fill="both", expand=True)

    def show_placeholder(self):
        self.clear()
        c = tk.Frame(self.root, bg="#130f24")
        c.pack(fill="both", expand=True)
        tk.Label(c, text="EN DESARROLLO", bg="#130f24", fg="#f2b929", font=("Segoe UI Black", 30)).pack(expand=True)
        tk.Button(c, text="VOLVER", command=self.show_main_menu, bg="#41316f", fg="white",
                  font=("Segoe UI Black", 18)).pack(fill="x", side="bottom", pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpsonsTV(root)
    root.mainloop()