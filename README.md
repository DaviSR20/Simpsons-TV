# Simpsons-TV

Primera prueba local del menu de la mini tele de los Simpsons.

## Prototipo actual

Se ha montado una demo para PC en [prototype/simpsons_tv_pc.py](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/prototype/simpsons_tv_pc.py) que simula:

- arranque de la Raspberry
- menu principal
- seleccion de temporada
- seleccion de capitulo con sinopsis
- reproduccion del episodio
- accesos base a juegos, ajustes de red y apagado

Si no hay un video real disponible, la app entra en modo demo y simula la reproduccion.

## Ejecutar

Desde la raiz del proyecto:

```powershell
python prototype\simpsons_tv_pc.py
```

Prueba rapida sin abrir interfaz:

```powershell
python prototype\simpsons_tv_pc.py --smoke-test
```

## Videos de prueba

La app busca los MP4 en [prototype/media/README.md](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/prototype/media/README.md).

Si quereis probar reproduccion real en PC, basta con meter archivos como:

- `prototype/media/s01e01.mp4`
- `prototype/media/s01e02.mp4`
- `prototype/media/s02e01.mp4`

## Siguiente paso natural

Cuando tengais decidido el Raspberry Pi OS, el siguiente salto seria:

- cambiar la apertura local por `omxplayer` o el reproductor final de la Pi
- leer episodios reales desde disco o USB
- crear el servicio HTTP local para lanzar capitulos desde movil o PC
- implementar QR + ajustes WiFi
- conectar el menu de juegos con `pygame`

## Control remoto Raspberry

He dejado una primera base de servidor en [prototype/media/pi_control_server.py](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/prototype/media/pi_control_server.py) para arrancarlo en la Raspberry por SSH y probar reproducción remota.

Arranque en la Raspberry:

```bash
cd ~/Simpsons-TV/prototype/media
python3 pi_control_server.py
```

Pruebas desde el PC con `curl`:

```powershell
curl http://IP_DE_LA_RASPBERRY:5050/health
curl http://IP_DE_LA_RASPBERRY:5050/episodes?available=1
curl -X POST http://IP_DE_LA_RASPBERRY:5050/play -H "Content-Type: application/json" -d "{\"episode_id\":\"1x01\"}"
curl http://IP_DE_LA_RASPBERRY:5050/status
curl -X POST http://IP_DE_LA_RASPBERRY:5050/stop -H "Content-Type: application/json" -d "{}"
```

Tambien hay un cliente de prueba en [prototype/media/test_remote_control.py](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/prototype/media/test_remote_control.py):

```powershell
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY health
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY episodes
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY play 1x01
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY stop
```
