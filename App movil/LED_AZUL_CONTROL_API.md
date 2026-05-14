# LED azul en `control_api.py`

La app móvil ya está preparada para llamar a:

- `POST /led/on`
- `POST /led/off`

justo después de conectar correctamente con la Raspberry.

## Pinout usado

- Pin físico `11` -> `GPIO17` -> positivo LED azul
- Pin físico `14` -> `GND` -> negativo LED azul

## Qué añadir en la Raspberry

Dentro de `control_api.py`, añadid esta base:

```python
try:
    from gpiozero import LED
except Exception:
    LED = None

LED_BLUE_GPIO = 17
blue_led = LED(LED_BLUE_GPIO) if LED is not None else None


def set_blue_led(enabled):
    if blue_led is None:
        return False
    if enabled:
        blue_led.on()
    else:
        blue_led.off()
    return True
```

## Encendido y apagado al arrancar

Si queréis asegurar estado inicial:

```python
if blue_led is not None:
    blue_led.off()
```

## Endpoints nuevos

Añadid estas rutas a `control_api.py`:

```python
@app.route("/led/on", methods=["POST"])
def led_on():
    ok = set_blue_led(True)
    return jsonify({"ok": ok, "led": "blue", "state": "on"})


@app.route("/led/off", methods=["POST"])
def led_off():
    ok = set_blue_led(False)
    return jsonify({"ok": ok, "led": "blue", "state": "off"})
```

## Opcional: incluir estado en `/health`

Si queréis verlo desde cliente:

```python
"blueLedAvailable": blue_led is not None,
```

## Dependencia en Raspberry

Si no está instalado `gpiozero`:

```bash
sudo apt update
sudo apt install python3-gpiozero
```

## Qué hace ya la app móvil

En [ConnectScreen.js](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/App movil/src/screens/ConnectScreen.js), después de:

1. autenticar con `/web/auth`
2. validar `/health`

la app llama automáticamente a `POST /led/on`.

Eso hace que el LED azul se encienda cuando la app consigue conectarse a la Raspberry.
