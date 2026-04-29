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

La integración remota se ha adaptado al servidor Flask del profesor. Ese servidor:

- usa autenticación por PIN vía `POST /web/auth`
- exige `X-Web-Pin` en casi todas las peticiones
- expone `/ip`, `/health`, `/now`, `/episodes`, `/videos`, `/play`, `/stop`, `/volume/up` y `/volume/down`
- busca los vídeos en una carpeta `videos/`

Herramientas preparadas en este repo:

- [prototype/media/professor_server_client.py](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/prototype/media/professor_server_client.py): cliente reutilizable para Python.
- [prototype/media/test_remote_control.py](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/prototype/media/test_remote_control.py): pruebas rápidas desde PC.
- [prototype/media/prepare_professor_server_layout.py](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/prototype/media/prepare_professor_server_layout.py): crea `videos/` a partir de `episodios/`.
- [prototype/media/simpsons_tv_pc.py](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/prototype/media/simpsons_tv_pc.py): la app de PC ahora puede trabajar también en modo remoto.

Preparar la estructura de vídeos compatible con el servidor:

```powershell
python prototype\media\prepare_professor_server_layout.py
```

Pruebas desde PC con el cliente:

```powershell
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY ip
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY --pin 1234 auth
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY --pin 1234 health
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY --pin 1234 episodes
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY --pin 1234 play 1x01
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY --pin 1234 now
python prototype\media\test_remote_control.py --host IP_DE_LA_RASPBERRY --pin 1234 stop
```

Prueba con interfaz de PC contra la Raspberry:

```powershell
python prototype\media\simpsons_tv_pc.py --server-host IP_DE_LA_RASPBERRY --server-pin 1234
```
