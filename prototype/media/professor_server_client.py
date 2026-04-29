from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib import error, request


SEASON_EPISODE_RE = re.compile(r"^(?:S)?(\d{1,2})[XEX](\d{1,2})$", re.IGNORECASE)


class ProfessorServerError(Exception):
    pass


class ProfessorServerHTTPError(ProfessorServerError):
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"HTTP {status_code}: {payload}")


@dataclass
class EpisodeMatch:
    server_id: str
    directory_path: str
    relative_path: str
    season_number: int | None
    episode_number: int | None

    @property
    def catalog_id(self) -> str | None:
        if self.season_number is None or self.episode_number is None:
            return None
        return f"{self.season_number}x{self.episode_number:02d}"


def parse_episode_key(value: str) -> tuple[int, int] | None:
    normalized = value.strip().upper().replace("-", "").replace("_", "")
    match = SEASON_EPISODE_RE.match(normalized)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def build_episode_aliases(value: str) -> set[str]:
    aliases = {value.strip(), value.strip().upper(), value.strip().lower()}
    parsed = parse_episode_key(value)
    if parsed:
        season_number, episode_number = parsed
        aliases.update(
            {
                f"{season_number}x{episode_number:02d}",
                f"{season_number}X{episode_number:02d}",
                f"S{season_number:02d}E{episode_number:02d}",
            }
        )
    return {alias for alias in aliases if alias}


class ProfessorServerClient:
    def __init__(self, host: str, port: int = 5050, pin: str | None = None, timeout: int = 10) -> None:
        self.host = host
        self.port = port
        self.pin = pin
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        include_pin: bool = True,
    ) -> tuple[int, Any]:
        data = None
        headers: dict[str, str] = {}

        if include_pin and self.pin:
            headers["X-Web-Pin"] = self.pin

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)

        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                parsed = json.loads(body) if body else {}
                return response.status, parsed
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body) if body else {}
            except json.JSONDecodeError:
                parsed = {"error": body}
            raise ProfessorServerHTTPError(exc.code, parsed) from exc
        except error.URLError as exc:
            raise ProfessorServerError(f"No se pudo conectar con {self.base_url}: {exc.reason}") from exc

    def authenticate(self, pin: str | None = None) -> Any:
        active_pin = pin if pin is not None else self.pin
        if not active_pin:
            raise ProfessorServerError("Falta el PIN web para autenticarse.")
        _status, payload = self._request_json(
            "POST",
            "/web/auth",
            payload={"pin": active_pin},
            include_pin=False,
        )
        if pin is not None:
            self.pin = pin
        return payload

    def get_ip(self) -> Any:
        _status, payload = self._request_json("GET", "/ip", include_pin=False)
        return payload

    def health(self) -> Any:
        _status, payload = self._request_json("GET", "/health")
        return payload

    def now(self) -> Any:
        _status, payload = self._request_json("GET", "/now")
        return payload

    def episodes(self, directory: str | None = None) -> list[dict[str, Any]]:
        path = "/episodes"
        if directory:
            path += f"?directory={directory}"
        _status, payload = self._request_json("GET", path)
        if not isinstance(payload, list):
            raise ProfessorServerError(f"Respuesta inesperada de /episodes: {payload}")
        return payload

    def videos(self) -> Any:
        _status, payload = self._request_json("GET", "/videos")
        return payload

    def stop(self) -> Any:
        _status, payload = self._request_json("POST", "/stop", payload={})
        return payload

    def volume_up(self) -> Any:
        _status, payload = self._request_json("POST", "/volume/up", payload={})
        return payload

    def volume_down(self) -> Any:
        _status, payload = self._request_json("POST", "/volume/down", payload={})
        return payload

    def resolve_episode(self, episode_id: str, directory: str | None = None) -> EpisodeMatch:
        aliases = build_episode_aliases(episode_id)
        requested_numbers = parse_episode_key(episode_id)
        matches: list[EpisodeMatch] = []

        for episode in self.episodes(directory=directory):
            server_id = str(episode.get("id") or "").strip()
            if not server_id:
                continue
            season_number = episode.get("seasonNumber")
            episode_number = episode.get("episodeNumber")

            same_alias = server_id in aliases or server_id.upper() in aliases
            same_numbers = (
                requested_numbers is not None
                and season_number == requested_numbers[0]
                and episode_number == requested_numbers[1]
            )
            if not same_alias and not same_numbers:
                continue

            matches.append(
                EpisodeMatch(
                    server_id=server_id,
                    directory_path=str(episode.get("directoryPath") or ""),
                    relative_path=str(episode.get("relativePath") or ""),
                    season_number=season_number,
                    episode_number=episode_number,
                )
            )

        if not matches:
            raise ProfessorServerError(f"No se ha encontrado el episodio {episode_id}")

        if directory:
            return matches[0]

        unique_keys = {(match.server_id, match.directory_path) for match in matches}
        if len(unique_keys) > 1:
            options = [
                {
                    "id": match.server_id,
                    "directoryPath": match.directory_path,
                    "relativePath": match.relative_path,
                }
                for match in matches
            ]
            raise ProfessorServerError(
                "El episodio es ambiguo en el servidor. Opciones: "
                + json.dumps(options, ensure_ascii=False)
            )

        return matches[0]

    def play(self, episode_id: str, directory: str | None = None) -> Any:
        match = self.resolve_episode(episode_id, directory=directory)
        payload = {"id": match.server_id}
        if match.directory_path:
            payload["directory"] = match.directory_path
        _status, result = self._request_json("POST", "/play", payload=payload)
        return result
