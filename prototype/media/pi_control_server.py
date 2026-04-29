from __future__ import annotations

import argparse
import json
import os
import platform
import re
import signal
import subprocess
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
FILE_DATA = BASE_DIR / "Info.Caps.js"
FOLDER_EPISODIOS = BASE_DIR / "episodios"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 5050


def is_raspberry_pi() -> bool:
    machine = platform.machine().lower()
    system = platform.system().lower()
    return system == "linux" and ("arm" in machine or "aarch" in machine)


def load_episodes_from_js() -> dict[str, dict[str, Any]]:
    if not FILE_DATA.exists():
        raise FileNotFoundError(f"No se encuentra {FILE_DATA}")

    content = FILE_DATA.read_text(encoding="utf-8", errors="replace")
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    if not json_match:
        raise ValueError("No se ha encontrado el objeto JSON dentro de Info.Caps.js")

    raw_data = json.loads(json_match.group(0))
    flat_data: dict[str, dict[str, Any]] = {}

    for season in raw_data.get("seasons", []):
        season_number = season.get("id")
        season_title = season.get("title")
        for episode in season.get("episodes", []):
            ep_id = episode.get("id")
            if not ep_id:
                continue
            video_path = FOLDER_EPISODIOS / f"{ep_id}.mp4"
            flat_data[ep_id] = {
                "id": ep_id,
                "title": episode.get("title", ep_id),
                "season": season_number,
                "season_title": season_title,
                "episode": episode.get("episodeNumber"),
                "duration": episode.get("duration"),
                "air_date": episode.get("airDate"),
                "image": episode.get("image"),
                "synopsis": episode.get("synopsis", ""),
                "video_path": str(video_path),
                "video_exists": video_path.exists(),
            }

    return flat_data


class PlaybackManager:
    def __init__(self, episodes: dict[str, dict[str, Any]], desktop_preview: bool = False) -> None:
        self.episodes = episodes
        self.desktop_preview = desktop_preview
        self.lock = threading.Lock()
        self.process: subprocess.Popen | None = None
        self.current_episode_id: str | None = None
        self.current_video_path: str | None = None
        self.started_at: float | None = None

    def _build_player_command(self, video_path: str) -> list[str]:
        if is_raspberry_pi() and not self.desktop_preview:
            return ["omxplayer", "--no-osd", "--aspect-mode", "fill", video_path]
        if platform.system() == "Windows":
            return ["cmd", "/c", "start", "", video_path]
        if platform.system() == "Darwin":
            return ["open", video_path]
        return ["xdg-open", video_path]

    def _poll_state_unlocked(self) -> None:
        if self.process and self.process.poll() is not None:
            self.process = None
            self.current_episode_id = None
            self.current_video_path = None
            self.started_at = None

    def status(self) -> dict[str, Any]:
        with self.lock:
            self._poll_state_unlocked()
            return {
                "playing": self.process is not None,
                "episode_id": self.current_episode_id,
                "video_path": self.current_video_path,
                "started_at": self.started_at,
            }

    def play(self, episode_id: str) -> dict[str, Any]:
        episode = self.episodes.get(episode_id)
        if episode is None:
            raise KeyError(f"Episodio no encontrado: {episode_id}")

        video_path = Path(episode["video_path"])
        if not video_path.exists():
            raise FileNotFoundError(f"No existe el video {video_path}")

        command = self._build_player_command(str(video_path))

        with self.lock:
            self._poll_state_unlocked()
            self._stop_unlocked(silent=True)

            kwargs: dict[str, Any] = {}
            if is_raspberry_pi() and not self.desktop_preview:
                kwargs["stdin"] = subprocess.PIPE
                kwargs["stdout"] = subprocess.DEVNULL
                kwargs["stderr"] = subprocess.DEVNULL
            else:
                kwargs["stdout"] = subprocess.DEVNULL
                kwargs["stderr"] = subprocess.DEVNULL

            self.process = subprocess.Popen(command, **kwargs)
            self.current_episode_id = episode_id
            self.current_video_path = str(video_path)
            self.started_at = time.time()

            return {
                "playing": True,
                "episode_id": episode_id,
                "video_path": str(video_path),
                "command": command,
            }

    def _stop_unlocked(self, silent: bool = False) -> dict[str, Any]:
        self._poll_state_unlocked()
        previous_episode_id = self.current_episode_id

        if self.process is None:
            return {"stopped": False, "episode_id": previous_episode_id}

        process = self.process
        try:
            if is_raspberry_pi() and not self.desktop_preview and process.stdin:
                process.stdin.write(b"q")
                process.stdin.flush()
                process.wait(timeout=3)
            else:
                process.terminate()
                process.wait(timeout=3)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass

        self.process = None
        self.current_episode_id = None
        self.current_video_path = None
        self.started_at = None

        return {"stopped": True, "episode_id": previous_episode_id, "silent": silent}

    def stop(self, silent: bool = False) -> dict[str, Any]:
        with self.lock:
            return self._stop_unlocked(silent=silent)


class SimpsonsRequestHandler(BaseHTTPRequestHandler):
    server_version = "SimpsonsTVControl/0.1"

    @property
    def app(self) -> "SimpsonsControlServer":
        return self.server.app  # type: ignore[attr-defined]

    def log_message(self, format: str, *args) -> None:
        print(f"[http] {self.address_string()} - {format % args}")

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw_body = self.rfile.read(length)
        if not raw_body:
            return {}
        return json.loads(raw_body.decode("utf-8"))

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _episode_id_from_request(self, body: dict[str, Any]) -> str | None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        return body.get("episode_id") or query.get("episode_id", [None])[0]

    def do_OPTIONS(self) -> None:
        self._send_json(HTTPStatus.OK, {"ok": True})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "service": "simpsons-tv-control",
                    "host": self.app.host,
                    "port": self.app.port,
                    "raspberry_mode": is_raspberry_pi() and not self.app.desktop_preview,
                },
            )
            return

        if parsed.path == "/episodes":
            only_available = parse_qs(parsed.query).get("available", ["0"])[0] == "1"
            episodes = list(self.app.episodes.values())
            if only_available:
                episodes = [episode for episode in episodes if episode["video_exists"]]
            self._send_json(
                HTTPStatus.OK,
                {
                    "count": len(episodes),
                    "episodes": episodes,
                },
            )
            return

        if parsed.path == "/status":
            self._send_json(HTTPStatus.OK, self.app.playback.status())
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "Ruta no encontrada"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": "JSON inválido"})
            return

        if parsed.path == "/play":
            episode_id = self._episode_id_from_request(body)
            if not episode_id:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"ok": False, "error": "Debes enviar episode_id"},
                )
                return
            try:
                result = self.app.playback.play(episode_id)
            except KeyError as exc:
                self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": str(exc)})
                return
            except FileNotFoundError as exc:
                self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": str(exc)})
                return
            except Exception as exc:
                self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": str(exc)})
                return

            self._send_json(HTTPStatus.OK, {"ok": True, **result})
            return

        if parsed.path == "/stop":
            result = self.app.playback.stop()
            self._send_json(HTTPStatus.OK, {"ok": True, **result})
            return

        self._send_json(HTTPStatus.NOT_FOUND, {"ok": False, "error": "Ruta no encontrada"})


class SimpsonsControlServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        request_handler_class: type[BaseHTTPRequestHandler],
        episodes: dict[str, dict[str, Any]],
        desktop_preview: bool,
    ) -> None:
        super().__init__(server_address, request_handler_class)
        self.episodes = episodes
        self.host, self.port = server_address
        self.desktop_preview = desktop_preview
        self.playback = PlaybackManager(episodes, desktop_preview=desktop_preview)
        self.app = self


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Servidor HTTP mínimo para controlar la Simpsons TV desde PC o móvil."
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host de escucha. Por defecto 0.0.0.0")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Puerto HTTP. Por defecto 5050")
    parser.add_argument(
        "--desktop-preview",
        action="store_true",
        help="Usa el reproductor del sistema en lugar de omxplayer, útil para PC.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    episodes = load_episodes_from_js()
    server = SimpsonsControlServer(
        (args.host, args.port),
        SimpsonsRequestHandler,
        episodes=episodes,
        desktop_preview=args.desktop_preview,
    )

    def shutdown_handler(signum, frame) -> None:
        del signum, frame
        server.playback.stop(silent=True)
        server.shutdown()

    signal.signal(signal.SIGINT, shutdown_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown_handler)

    print(
        f"Simpsons TV control server escuchando en http://{args.host}:{args.port} "
        f"| episodios cargados: {len(episodes)}"
    )
    try:
        server.serve_forever()
    finally:
        server.playback.stop(silent=True)
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
