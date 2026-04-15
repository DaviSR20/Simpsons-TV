from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any

import tkinter as tk
from tkinter import ttk

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CATALOG = BASE_DIR / "catalog.json"


def load_catalog(catalog_path: Path) -> dict[str, Any]:
    with catalog_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    seasons = data.get("seasons", [])
    if not seasons:
        raise ValueError("El catalogo no tiene temporadas.")

    for season in seasons:
        if not season.get("episodes"):
            raise ValueError(
                f"La temporada {season.get('number', '?')} no tiene episodios."
            )

    return data


def get_local_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "No disponible"


def launch_media(target: str) -> tuple[bool, str]:
    if target.startswith("http://") or target.startswith("https://"):
        opened = webbrowser.open(target)
        if opened:
            return True, f"Abierto en el navegador: {target}"
        return False, "No se pudo abrir la URL en el navegador."

    path = Path(target)
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()

    if not path.exists():
        return False, f"No existe el archivo: {path}"

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return True, f"Reproductor lanzado: {path}"
    except OSError as exc:
        return False, f"Error: {exc}"


class SimpsonsTVApp:
    def __init__(self, root: tk.Tk, catalog: dict[str, Any]) -> None:
        self.root = root
        self.catalog = catalog
        self.current_after_ids: list[str] = []
        self.current_season_index = 0
        self.current_episode_index = 0
        self.simulation_progress = 0

        # Resolucion exacta de la pantalla tactil
        self.root.title("Simpsons TV Prototype")
        self.root.geometry("480x640")
        self.root.resizable(False, False)
        self.root.configure(bg="#130f24")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "TV.Horizontal.TProgressbar",
            troughcolor="#241d42",
            background="#ffd85a",
            bordercolor="#241d42",
            lightcolor="#ffd85a",
            darkcolor="#ffd85a",
        )

        self.show_boot_screen()

    def schedule(self, delay_ms: int, callback) -> None:
        after_id = self.root.after(delay_ms, callback)
        self.current_after_ids.append(after_id)

    def clear_screen(self) -> None:
        for after_id in self.current_after_ids:
            try:
                self.root.after_cancel(after_id)
            except tk.TclError:
                pass
        self.current_after_ids.clear()
        for child in self.root.winfo_children():
            child.destroy()

    def show_boot_screen(self) -> None:
        self.clear_screen()

        boot = tk.Frame(self.root, bg="#0e0a1b")
        boot.pack(fill="both", expand=True)

        tk.Label(
            boot,
            text="Simpsons TV",
            bg="#0e0a1b",
            fg="#f2efff",
            font=("Segoe UI Black", 28),
        ).pack(expand=True, pady=(150, 0))

        progress = ttk.Progressbar(
            boot,
            length=300,
            mode="determinate",
            maximum=100,
            style="TV.Horizontal.TProgressbar",
        )
        progress.pack(pady=40)

        def animate(step: int = 0) -> None:
            progress["value"] = min(100, step * 25)
            if step < 4:
                self.schedule(450, lambda: animate(step + 1))
            else:
                self.schedule(350, self.show_main_menu)

        animate()

    def show_main_menu(self) -> None:
        self.clear_screen()

        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        actions = [
            ("VER EPISODIOS", self.show_season_menu),
            ("JUEGOS", self.show_games_menu),
            ("AJUSTES DE RED", self.show_network_menu),
            ("APAGAR", self.power_off),
        ]

        # 4 botones gigantes ocupando toda la pantalla
        for text, command in actions:
            btn = tk.Button(
                container,
                text=text,
                command=command,
                bg="#f2b929",
                fg="#1d1635",
                activebackground="#ffd85a",
                activeforeground="#1d1635",
                relief="flat",
                bd=0,
                font=("Segoe UI Black", 22),
            )
            btn.pack(fill="both", expand=True, pady=10)

    def show_season_menu(self) -> None:
        self.clear_screen()

        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        seasons = self.catalog["seasons"]

        # Lista tactil grande
        season_list = tk.Listbox(
            container,
            bg="#1a1431",
            fg="#f8f5ff",
            selectbackground="#f2b929",
            selectforeground="#1a1431",
            activestyle="none",
            relief="flat",
            highlightthickness=0,
            font=("Segoe UI", 18),
        )
        season_list.pack(fill="both", expand=True, pady=(0, 15))

        for season in seasons:
            season_list.insert("end", f" Temporada {season['number']}")

        season_list.selection_set(self.current_season_index)

        # Botones inferiores grandes
        btn_frame = tk.Frame(container, bg="#130f24")
        btn_frame.pack(fill="x", pady=5)

        tk.Button(
            btn_frame,
            text="ABRIR",
            command=lambda: self.show_episode_menu(season_list.curselection()[0] if season_list.curselection() else 0),
            bg="#f2b929",
            fg="#1d1635",
            font=("Segoe UI Black", 16),
            relief="flat",
            ipady=15
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="VOLVER",
            command=self.show_main_menu,
            bg="#41316f",
            fg="#ffffff",
            font=("Segoe UI Black", 16),
            relief="flat",
            ipady=15
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def show_episode_menu(self, season_index: int) -> None:
        self.current_season_index = season_index
        self.clear_screen()

        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=15, pady=15)

        season = self.catalog["seasons"][season_index]

        # Lista de episodios grande para dedos
        episode_list = tk.Listbox(
            container,
            bg="#1a1431",
            fg="#f8f5ff",
            selectbackground="#f2b929",
            selectforeground="#1a1431",
            activestyle="none",
            relief="flat",
            highlightthickness=0,
            font=("Segoe UI", 16),
        )
        episode_list.pack(fill="both", expand=True, pady=(0, 15))

        for episode in season["episodes"]:
            episode_list.insert("end", f" E{episode['number']:02d} | {episode['title']}")

        episode_list.selection_set(0)

        btn_frame = tk.Frame(container, bg="#130f24")
        btn_frame.pack(fill="x", pady=5)

        tk.Button(
            btn_frame,
            text="PLAY",
            command=lambda: self.play_episode(season,
                                              episode_list.curselection()[0] if episode_list.curselection() else 0),
            bg="#f2b929",
            fg="#1d1635",
            font=("Segoe UI Black", 16),
            relief="flat",
            ipady=15
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="VOLVER",
            command=self.show_season_menu,
            bg="#41316f",
            fg="#ffffff",
            font=("Segoe UI Black", 16),
            relief="flat",
            ipady=15
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def play_episode(self, season: dict[str, Any], episode_index: int) -> None:
        self.clear_screen()
        episode = season["episodes"][episode_index]

        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text=f"T{season['number']:02d} E{episode['number']:02d}",
            bg="#130f24",
            fg="#ffe477",
            font=("Segoe UI Black", 24),
        ).pack(pady=(40, 10))

        tk.Label(
            container,
            text=episode["title"],
            bg="#130f24",
            fg="#f8f5ff",
            font=("Segoe UI", 16),
            wraplength=400,
            justify="center"
        ).pack(pady=(0, 40))

        progress = ttk.Progressbar(
            container, length=400, mode="determinate", maximum=100, style="TV.Horizontal.TProgressbar"
        )
        progress.pack(pady=20)

        source = episode.get("video_path") or episode.get("stream_url")
        if source:
            launched, _ = launch_media(source)
            if launched:
                progress["value"] = 100

        if progress["value"] != 100:
            self.run_demo_playback(progress, episode["duration_minutes"])

        tk.Button(
            container,
            text="VOLVER",
            command=lambda: self.show_episode_menu(self.current_season_index),
            bg="#41316f",
            fg="#ffffff",
            font=("Segoe UI Black", 18),
            relief="flat",
            ipady=15
        ).pack(fill="x", side="bottom", pady=20)

    def run_demo_playback(self, progress: ttk.Progressbar, duration_minutes: int) -> None:
        progress["value"] = 0
        self.simulation_progress = 0
        total_steps = max(10, duration_minutes)

        def tick() -> None:
            self.simulation_progress += 1
            progress["value"] = min(100, (self.simulation_progress / total_steps) * 100)
            if self.simulation_progress < total_steps:
                self.schedule(700, tick)

        tick()

    def show_network_menu(self) -> None:
        self.clear_screen()
        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="IP LOCAL",
            bg="#130f24",
            fg="#f8f5ff",
            font=("Segoe UI Black", 20),
        ).pack(pady=(60, 10))

        ip_label = tk.Label(
            container,
            text=get_local_ip(),
            bg="#130f24",
            fg="#ffe477",
            font=("Segoe UI", 28, "bold"),
        )
        ip_label.pack(pady=(0, 40))

        tk.Button(
            container,
            text="REFRESCAR",
            command=lambda: ip_label.config(text=get_local_ip()),
            bg="#f2b929",
            fg="#1d1635",
            font=("Segoe UI Black", 18),
            relief="flat",
            ipady=15
        ).pack(fill="x", pady=10)

        tk.Button(
            container,
            text="VOLVER",
            command=self.show_main_menu,
            bg="#41316f",
            fg="#ffffff",
            font=("Segoe UI Black", 18),
            relief="flat",
            ipady=15
        ).pack(fill="x", pady=10)

    def show_games_menu(self) -> None:
        self.clear_screen()
        container = tk.Frame(self.root, bg="#130f24")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            container,
            text="JUEGOS",
            bg="#130f24",
            fg="#ffe477",
            font=("Segoe UI Black", 28),
        ).pack(expand=True)

        tk.Button(
            container,
            text="VOLVER",
            command=self.show_main_menu,
            bg="#41316f",
            fg="#ffffff",
            font=("Segoe UI Black", 18),
            relief="flat",
            ipady=15
        ).pack(fill="x", side="bottom", pady=20)

    def power_off(self) -> None:
        self.clear_screen()
        tk.Label(
            self.root,
            text="APAGANDO...",
            bg="#130f24",
            fg="#f2b929",
            font=("Segoe UI Black", 24),
        ).pack(expand=True)
        self.schedule(900, self.root.destroy)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    args = parser.parse_args()

    catalog = load_catalog(args.catalog)

    root = tk.Tk()
    SimpsonsTVApp(root, catalog)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())