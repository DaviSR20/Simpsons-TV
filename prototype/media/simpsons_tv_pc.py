from __future__ import annotations

import argparse
import json
import os
import platform
import re
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageTk

from professor_server_client import ProfessorServerClient, ProfessorServerError, parse_episode_key

try:
    import vlc
except ImportError:
    vlc = None


WIDTH = 640
HEIGHT = 480
BASE_DIR = Path(__file__).resolve().parent
FOLDER_EPISODIOS = BASE_DIR / "episodios"
FOLDER_IMAGENES = BASE_DIR / "imagenes"
FILE_DATA = BASE_DIR / "Info.Caps.js"


if platform.system() == "Windows" and vlc is not None:
    vlc_path = r"C:\Program Files\VideoLAN\VLC"
    if os.path.exists(vlc_path):
        os.add_dll_directory(vlc_path)


def load_episodes_from_js() -> dict[str, dict]:
    if not FILE_DATA.exists():
        return {}

    try:
        content = FILE_DATA.read_text(encoding="utf-8", errors="replace")
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            return {}

        raw_data = json.loads(json_match.group(0))
        flat_data = {}
        for season in raw_data.get("seasons", []):
            s_num = season.get("id")
            for ep in season.get("episodes", []):
                ep_number = ep.get("episodeNumber")
                ep_id = ep.get("id") or f"{s_num}x{ep_number:02d}"
                flat_data[ep_id.lower()] = {
                    "id": ep_id.lower(),
                    "title": ep.get("title"),
                    "season": s_num,
                    "episode": ep_number,
                    "synopsis": ep.get("synopsis"),
                    "image": ep.get("image"),
                }
        return flat_data
    except Exception as exc:
        print(f"Error al procesar Info.Caps.js: {exc}")
        return {}


class VLCPlayer(tk.Frame):
    def __init__(self, parent, video_path: Path, on_close):
        if vlc is None:
            raise RuntimeError("python-vlc no está instalado en este PC.")

        super().__init__(parent, bg="black")
        self.on_close = on_close
        self.video_canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.video_canvas.pack(fill="both", expand=True)

        tk.Button(
            self,
            text="DETENER VIDEO",
            command=self.stop,
            bg="#41316f",
            fg="white",
            font=("Arial", 12, "bold"),
        ).pack(fill="x")

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
    def __init__(self, root: tk.Tk, server_host: str | None = None, server_pin: str | None = None, server_port: int = 5050):
        self.root = root
        self.root.title("Simpsons TV - Control PC")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg="#130f24")

        self.server_client = (
            ProfessorServerClient(server_host, port=server_port, pin=server_pin)
            if server_host
            else None
        )
        self.remote_mode = self.server_client is not None
        self.remote_index: dict[str, dict] = {}

        self.data_caps = load_episodes_from_js()
        FOLDER_EPISODIOS.mkdir(exist_ok=True)
        FOLDER_IMAGENES.mkdir(exist_ok=True)

        if self.remote_mode:
            self.load_remote_episodes()

        self.show_main_menu()

    def load_remote_episodes(self) -> None:
        assert self.server_client is not None

        if self.server_client.pin:
            self.server_client.authenticate()

        remote_episodes = self.server_client.episodes()
        self.remote_index = {}
        for remote_episode in remote_episodes:
            season_number = remote_episode.get("seasonNumber")
            episode_number = remote_episode.get("episodeNumber")
            if season_number is None or episode_number is None:
                continue
            catalog_id = f"{season_number}x{episode_number:02d}"
            self.remote_index[catalog_id.lower()] = remote_episode

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def available_episodes(self) -> list[dict]:
        items = []
        for ep_id, info in self.data_caps.items():
            if self.remote_mode:
                remote_entry = self.remote_index.get(ep_id.lower())
                if not remote_entry:
                    continue
                items.append({"id": ep_id, "title": info["title"], "remote": remote_entry})
                continue

            local_video = FOLDER_EPISODIOS / f"{ep_id}.mp4"
            if local_video.exists():
                items.append({"id": ep_id, "title": info["title"]})

        items.sort(key=lambda item: parse_episode_key(item["id"]) or (999, 999))
        return items

    def show_main_menu(self):
        self.clear()
        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        container.columnconfigure((0, 1), weight=1)
        container.rowconfigure((0, 1), weight=1)

        menu_items = [
            ("VER EPISODIOS", self.show_episodes_list, 0, 0),
            ("JUEGOS", lambda: messagebox.showinfo("Pendiente", "El minijuego irá aquí."), 0, 1),
            ("AJUSTES", self.show_settings, 1, 0),
            ("APAGAR", self.root.destroy, 1, 1),
        ]

        for text, cmd, row_index, col_index in menu_items:
            tk.Button(
                container,
                text=text,
                command=cmd,
                bg="#f2b929",
                fg="#1d1635",
                font=("Segoe UI Black", 18),
                relief="flat",
            ).grid(row=row_index, column=col_index, sticky="nsew", padx=10, pady=10)

    def show_settings(self):
        self.clear()
        frame = tk.Frame(self.root, bg="#130f24", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        lines = ["Modo PC local"]
        if self.remote_mode and self.server_client is not None:
            lines = [
                "Modo remoto activo",
                f"Host: {self.server_client.host}",
                f"Puerto: {self.server_client.port}",
                f"PIN cargado: {'sí' if self.server_client.pin else 'no'}",
            ]

        tk.Label(
            frame,
            text="\n".join(lines),
            bg="#130f24",
            fg="white",
            justify="left",
            font=("Arial", 14),
        ).pack(anchor="w", pady=(0, 20))

        if self.remote_mode and self.server_client is not None:
            tk.Button(
                frame,
                text="VER ESTADO REMOTO",
                command=self.show_remote_status,
                bg="#f2b929",
                fg="#1d1635",
                font=("Arial", 14, "bold"),
            ).pack(fill="x", pady=5)

        tk.Button(
            frame,
            text="VOLVER",
            command=self.show_main_menu,
            bg="#41316f",
            fg="white",
            font=("Arial", 14),
        ).pack(fill="x", side="bottom")

    def show_remote_status(self):
        if not self.server_client:
            return
        try:
            payload = self.server_client.health()
        except ProfessorServerError as exc:
            messagebox.showerror("Servidor", str(exc))
            return

        messagebox.showinfo(
            "Estado remoto",
            json.dumps(payload, indent=2, ensure_ascii=False),
        )

    def show_episodes_list(self):
        self.clear()
        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        available = self.available_episodes()

        lb = tk.Listbox(
            container,
            bg="#1a1431",
            fg="white",
            font=("Arial", 16),
            borderwidth=0,
            selectbackground="#f2b929",
            selectforeground="#1d1635",
        )
        lb.pack(side="left", fill="both", expand=True, padx=(0, 10))

        for item in available:
            label = f" {item['id']} - {item['title']}"
            if self.remote_mode:
                directory_label = item["remote"].get("directoryPath") or "root"
                label += f" [{directory_label}]"
            lb.insert("end", label)

        if available:
            lb.selection_set(0)

        btns = tk.Frame(container, bg="#130f24", width=150)
        btns.pack(side="right", fill="y")

        def check_details():
            if lb.curselection():
                idx = lb.curselection()[0]
                self.show_details(available[idx]["id"])

        tk.Button(
            btns,
            text="VER INFO",
            command=check_details,
            bg="#f2b929",
            font=("Arial", 14, "bold"),
        ).pack(fill="x", pady=5)
        tk.Button(
            btns,
            text="VOLVER",
            command=self.show_main_menu,
            bg="#41316f",
            fg="white",
            font=("Arial", 14),
        ).pack(fill="x", side="bottom")

    def show_details(self, ep_id: str):
        self.clear()
        info = self.data_caps[ep_id.lower()]

        img_canvas = tk.Canvas(self.root, width=640, height=220, bg="black", highlightthickness=0)
        img_canvas.pack(side="top")

        img_path = FOLDER_IMAGENES / str(info["image"])
        if img_path.exists():
            img = Image.open(img_path).resize((640, 220), Image.Resampling.LANCZOS)
            self.current_img = ImageTk.PhotoImage(img)
            img_canvas.create_image(0, 0, anchor="nw", image=self.current_img)
        else:
            img_canvas.create_text(320, 110, text="SIN PREVISUALIZACIÓN", fill="white")

        info_frame = tk.Frame(self.root, bg="#130f24", padx=25, pady=15)
        info_frame.pack(fill="both", expand=True)

        tk.Label(
            info_frame,
            text=info["title"],
            fg="#f2b929",
            bg="#130f24",
            font=("Arial", 18, "bold"),
        ).pack(anchor="w")
        tk.Label(
            info_frame,
            text=f"Temporada {info['season']} | Episodio {info['episode']}",
            fg="#8e8e8e",
            bg="#130f24",
            font=("Arial", 11),
        ).pack(anchor="w", pady=(0, 5))

        if self.remote_mode:
            remote_entry = self.remote_index.get(ep_id.lower())
            if remote_entry:
                tk.Label(
                    info_frame,
                    text=f"Servidor: {remote_entry.get('id')} | Ruta: {remote_entry.get('relativePath')}",
                    fg="#8e8e8e",
                    bg="#130f24",
                    font=("Arial", 10),
                ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            info_frame,
            text=info["synopsis"],
            fg="white",
            bg="#130f24",
            font=("Arial", 11),
            wraplength=580,
            justify="left",
        ).pack(anchor="w")

        btn_bar = tk.Frame(self.root, bg="#130f24", pady=15)
        btn_bar.pack(fill="x", side="bottom")

        tk.Button(
            btn_bar,
            text="VOLVER",
            command=self.show_episodes_list,
            bg="#41316f",
            fg="white",
            font=("Arial", 12),
            width=12,
        ).pack(side="left", padx=20)

        if self.remote_mode:
            tk.Button(
                btn_bar,
                text="STOP",
                command=self.stop_remote_playback,
                bg="#842029",
                fg="white",
                font=("Arial", 12, "bold"),
                width=12,
            ).pack(side="left", padx=8)
            tk.Button(
                btn_bar,
                text="PLAY REMOTO",
                command=lambda: self.play_remote(ep_id),
                bg="#f2b929",
                font=("Arial", 12, "bold"),
                width=14,
            ).pack(side="right", padx=20)
        else:
            video_path = FOLDER_EPISODIOS / f"{ep_id}.mp4"
            tk.Button(
                btn_bar,
                text="PLAY",
                command=lambda: self.play_local(video_path, ep_id),
                bg="#f2b929",
                font=("Arial", 12, "bold"),
                width=12,
            ).pack(side="right", padx=40)

    def play_local(self, path: Path, ep_id: str):
        try:
            self.clear()
            VLCPlayer(self.root, path, lambda: self.show_details(ep_id)).pack(fill="both", expand=True)
        except RuntimeError as exc:
            messagebox.showerror("VLC", str(exc))
            self.show_details(ep_id)

    def play_remote(self, ep_id: str):
        if not self.server_client:
            return
        remote_entry = self.remote_index.get(ep_id.lower())
        directory = remote_entry.get("directoryPath") if remote_entry else None
        try:
            payload = self.server_client.play(ep_id, directory=directory)
        except ProfessorServerError as exc:
            messagebox.showerror("Servidor", str(exc))
            return

        messagebox.showinfo("Servidor", json.dumps(payload, indent=2, ensure_ascii=False))

    def stop_remote_playback(self):
        if not self.server_client:
            return
        try:
            payload = self.server_client.stop()
        except ProfessorServerError as exc:
            messagebox.showerror("Servidor", str(exc))
            return
        messagebox.showinfo("Servidor", json.dumps(payload, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Visor/controlador PC para Simpsons TV.")
    parser.add_argument("--server-host", help="IP o hostname de la Raspberry para modo remoto")
    parser.add_argument("--server-port", type=int, default=5050, help="Puerto del servidor Flask")
    parser.add_argument("--server-pin", help="PIN web del servidor del profesor")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = tk.Tk()
    try:
        SimpsonsTV(
            root,
            server_host=args.server_host,
            server_pin=args.server_pin,
            server_port=args.server_port,
        )
    except ProfessorServerError as exc:
        messagebox.showerror("Servidor", str(exc))
        return 1

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
