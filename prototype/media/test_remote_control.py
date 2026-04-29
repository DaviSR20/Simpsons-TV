from __future__ import annotations

import argparse
import json
from urllib import error, request


def http_json(method: str, url: str, payload: dict | None = None) -> tuple[int, dict]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=10) as response:
        body = response.read().decode("utf-8")
        return response.status, json.loads(body)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cliente de prueba para el servidor remoto de Simpsons TV."
    )
    parser.add_argument("--host", required=True, help="IP o hostname de la Raspberry")
    parser.add_argument("--port", type=int, default=5050, help="Puerto del servidor")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("health")
    subparsers.add_parser("status")
    subparsers.add_parser("episodes")
    play_parser = subparsers.add_parser("play")
    play_parser.add_argument("episode_id", help="Ejemplo: 1x01")
    subparsers.add_parser("stop")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    base_url = f"http://{args.host}:{args.port}"

    try:
        if args.command == "health":
            status, payload = http_json("GET", f"{base_url}/health")
        elif args.command == "status":
            status, payload = http_json("GET", f"{base_url}/status")
        elif args.command == "episodes":
            status, payload = http_json("GET", f"{base_url}/episodes?available=1")
        elif args.command == "play":
            status, payload = http_json(
                "POST",
                f"{base_url}/play",
                payload={"episode_id": args.episode_id},
            )
        elif args.command == "stop":
            status, payload = http_json("POST", f"{base_url}/stop", payload={})
        else:
            raise ValueError(f"Comando no soportado: {args.command}")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(body)
        return exc.code
    except Exception as exc:
        print(f"Error de conexión: {exc}")
        return 1

    print(f"HTTP {status}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
