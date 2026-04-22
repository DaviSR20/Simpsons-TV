import os
import json
import re
import tkinter as tk
from pathlib import Path
import vlc
import platform
from PIL import Image, ImageTk

# --- CONFIGURACIÓN ---
WIDTH = 640
HEIGHT = 480
FOLDER_EPISODIOS = Path("episodios")
FOLDER_IMAGENES = Path("imagenes")
FILE_DATA = Path("Info.Caps.js")

# Parche VLC para Windows
if platform.system() == "Windows":
    vlc_path = r"C:\Program Files\VideoLAN\VLC"
    if os.path.exists(vlc_path):
        os.add_dll_directory(vlc_path)


def load_episodes_from_js():
    """
    Lee el archivo Info.Caps.js, extrae el objeto JSON y
    lo devuelve como un diccionario de Python indexado por ID (nxm).
    """
    if not FILE_DATA.exists():
        print(f"Error: No se encuentra {FILE_DATA}")
        return {}

    try:
        content = FILE_DATA.read_text(encoding="utf-8")
        # Buscamos lo que hay entre el primer '{' y el último '}'
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            return {}

        raw_data = json.loads(json_match.group(0))

        # Aplanamos la estructura de temporadas para buscar por ID fácilmente
        flat_data = {}
        for season in raw_data.get("seasons", []):
            s_num = season.get("id")
            for ep in season.get("episodes", []):
                ep_id = ep.get("id")  # Ej: "1x01"
                flat_data[ep_id] = {
                    "title": ep.get("title"),
                    "season": s_num,
                    "episode": ep.get("episodeNumber"),
                    "synopsis": ep.get("synopsis"),
                    "image": ep.get("image")
                }
        return flat_data
    except Exception as e:
        print(f"Error al procesar Info.Caps.js: {e}")
        return {}


class VLCPlayer(tk.Frame):
    def __init__(self, parent, video_path, on_close):
        super().__init__(parent, bg="black")
        self.on_close = on_close
        self.video_canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.video_canvas.pack(fill="both", expand=True)

        tk.Button(self, text="DETENER VIDEO", command=self.stop,
                  bg="#41316f", fg="white", font=("Arial", 12, "bold")).pack(fill="x")

        self.instance = vlc.Instance("--no-xlib", "--quiet")
        self.player = self.instance.media_player_new()

        win_id = self.video_canvas.winfo_id()
        if platform.system() == "Windows":
            self.player.set_hwnd(win_id)
        else:
            self.player.set_xwindow(win_id)

        self.player.set_media(self.instance.media_new(str(video_path)))
        self.player.play()

    def stop(self):
        self.player.stop()
        self.on_close()


class SimpsonsTV:
    def __init__(self, root):
        self.root = root
        self.root.title("Simpsons TV - Data Dinámica")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg="#130f24")

        # Cargar datos desde el archivo JS
        self.data_caps = load_episodes_from_js()

        FOLDER_EPISODIOS.mkdir(exist_ok=True)
        FOLDER_IMAGENES.mkdir(exist_ok=True)

        self.show_main_menu()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear()
        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        container.columnconfigure((0, 1), weight=1)
        container.rowconfigure((0, 1), weight=1)

        menu_items = [
            ("VER EPISODIOS", self.show_episodes_list, 0, 0),
            ("JUEGOS", lambda: print("Juegos"), 0, 1),
            ("AJUSTES", lambda: print("Ajustes"), 1, 0),
            ("APAGAR", self.root.destroy, 1, 1)
        ]

        for text, cmd, r, c in menu_items:
            tk.Button(container, text=text, command=cmd, bg="#f2b929", fg="#1d1635",
                      font=("Segoe UI Black", 18), relief="flat").grid(row=r, column=c, sticky="nsew", padx=10, pady=10)

    def show_episodes_list(self):
        self.clear()
        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        # Solo listamos los episodios que REALMENTE tienen un archivo .mp4 en la carpeta
        available = []
        for ep_id, info in self.data_caps.items():
            if (FOLDER_EPISODIOS / f"{ep_id}.mp4").exists():
                available.append({"id": ep_id, "title": info['title']})

        lb = tk.Listbox(container, bg="#1a1431", fg="white", font=("Arial", 16), borderwidth=0,
                        selectbackground="#f2b929", selectforeground="#1d1635")
        lb.pack(side="left", fill="both", expand=True, padx=(0, 10))

        for item in available:
            lb.insert("end", f" {item['id']} - {item['title']}")

        if available: lb.selection_set(0)

        btns = tk.Frame(container, bg="#130f24", width=150)
        btns.pack(side="right", fill="y")

        def check_details():
            if lb.curselection():
                idx = lb.curselection()[0]
                self.show_details(available[idx]['id'])

        tk.Button(btns, text="VER INFO", command=check_details, bg="#f2b929", font=("Arial", 14, "bold")).pack(fill="x",
                                                                                                               pady=5)
        tk.Button(btns, text="VOLVER", command=self.show_main_menu, bg="#41316f", fg="white", font=("Arial", 14)).pack(
            fill="x", side="bottom")

    def show_details(self, ep_id):
        self.clear()
        info = self.data_caps[ep_id]

        # Imagen
        img_canvas = tk.Canvas(self.root, width=640, height=220, bg="black", highlightthickness=0)
        img_canvas.pack(side="top")

        img_path = FOLDER_IMAGENES / info['image']
        if img_path.exists():
            img = Image.open(img_path).resize((640, 220), Image.Resampling.LANCZOS)
            self.current_img = ImageTk.PhotoImage(img)
            img_canvas.create_image(0, 0, anchor="nw", image=self.current_img)
        else:
            img_canvas.create_text(320, 110, text="SIN PREVISUALIZACIÓN", fill="white")

        # Texto
        info_frame = tk.Frame(self.root, bg="#130f24", padx=25, pady=15)
        info_frame.pack(fill="both", expand=True)

        tk.Label(info_frame, text=info['title'], fg="#f2b929", bg="#130f24", font=("Arial", 18, "bold")).pack(
            anchor="w")
        tk.Label(info_frame, text=f"Temporada {info['season']} | Episodio {info['episode']}",
                 fg="#8e8e8e", bg="#130f24", font=("Arial", 11)).pack(anchor="w", pady=(0, 5))

        tk.Label(info_frame, text=info['synopsis'], fg="white", bg="#130f24", font=("Arial", 11),
                 wraplength=580, justify="left").pack(anchor="w")

        # Botones
        btn_bar = tk.Frame(self.root, bg="#130f24", pady=15)
        btn_bar.pack(fill="x", side="bottom")

        tk.Button(btn_bar, text="VOLVER", command=self.show_episodes_list,
                  bg="#41316f", fg="white", font=("Arial", 12), width=12).pack(side="left", padx=40)

        video_path = FOLDER_EPISODIOS / f"{ep_id}.mp4"
        tk.Button(btn_bar, text="PLAY", command=lambda: self.play_video(video_path, ep_id),
                  bg="#f2b929", font=("Arial", 12, "bold"), width=12).pack(side="right", padx=40)

    def play_video(self, path, ep_id):
        self.clear()
        VLCPlayer(self.root, path, lambda: self.show_details(ep_id)).pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpsonsTV(root)
    root.mainloop()