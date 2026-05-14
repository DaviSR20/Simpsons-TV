# App movil

Versión móvil nueva para conectar con la Raspberry mediante el servidor Flask del profesor.

## Flujo

1. La Raspberry muestra un QR con una URL tipo `http://10.1.32.143:5050`.
2. La app escanea ese QR.
3. El usuario introduce el PIN web, por defecto `1234`.
4. La app consulta `/videos`, muestra bibliotecas, temporadas y episodios.
5. Al pulsar `Play en Raspberry`, llama a `POST /play`.
6. Al conectar correctamente, llama a `POST /led/on` para encender el LED azul.

## Arranque

```powershell
cd "App movil"
npm install
npx expo start
```

## Dependencias importantes

- `expo-camera` para leer el QR.
- `@react-native-async-storage/async-storage` para guardar IP y PIN.
- `@react-navigation/native` y `@react-navigation/native-stack` para navegación.

## Observaciones

- Esta app está adaptada al backend del profesor, no a un servidor inventado aparte.
- El backend exige `X-Web-Pin` en casi todas las rutas.
- Para reproducir, la app envía `id` y `directory`, que es lo que espera `control_api.py`.
- Para el LED azul, hay que añadir a `control_api.py` los endpoints `/led/on` y `/led/off`.
- La guía exacta para esa parte está en [LED_AZUL_CONTROL_API.md](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/App movil/LED_AZUL_CONTROL_API.md).
- La forma actual de subir/buildar con Expo está explicada en [EXPO_BUILD_ACTUAL.md](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/App movil/EXPO_BUILD_ACTUAL.md).
