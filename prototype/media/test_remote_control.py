from __future__ import annotations

import argparse
import json

from professor_server_client import ProfessorServerClient, ProfessorServerError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cliente de prueba para el servidor Flask del profesor."
    )
    parser.add_argument("--host", required=True, help="IP o hostname de la Raspberry")
    parser.add_argument("--port", type=int, default=5050, help="Puerto del servidor")
    parser.add_argument("--pin", help="PIN web configurado en el servidor")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("ip")
    subparsers.add_parser("auth")
    subparsers.add_parser("health")
    subparsers.add_parser("now")
    episodes_parser = subparsers.add_parser("episodes")
    episodes_parser.add_argument("--directory", help="Filtra por directoryPath del servidor")
    subparsers.add_parser("videos")

    play_parser = subparsers.add_parser("play")
    play_parser.add_argument("episode_id", help="Ejemplo: 1x01 o S01E01")
    play_parser.add_argument("--directory", help="DirectoryPath si el episodio es ambiguo")

    subparsers.add_parser("stop")
    subparsers.add_parser("volume-up")
    subparsers.add_parser("volume-down")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    client = ProfessorServerClient(host=args.host, port=args.port, pin=args.pin)

    try:
        if args.command == "ip":
            payload = client.get_ip()
        elif args.command == "auth":
            payload = client.authenticate()
        elif args.command == "health":
            payload = client.health()
        elif args.command == "now":
            payload = client.now()
        elif args.command == "episodes":
            payload = client.episodes(directory=args.directory)
        elif args.command == "videos":
            payload = client.videos()
        elif args.command == "play":
            payload = client.play(args.episode_id, directory=args.directory)
        elif args.command == "stop":
            payload = client.stop()
        elif args.command == "volume-up":
            payload = client.volume_up()
        elif args.command == "volume-down":
            payload = client.volume_down()
        else:
            raise ValueError(f"Comando no soportado: {args.command}")
    except ProfessorServerError as exc:
        print(str(exc))
        return 1

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
