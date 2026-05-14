# Forma actual de subir y buildar con Expo

Esta es la vía actual basada en documentación oficial de Expo.

## Lo antiguo

La forma antigua con:

- `expo build:android`
- `expo build:ios`
- `expo publish`

ya no es la recomendada actual.

Expo indica hoy que:

- para builds se usa **EAS Build**
- para actualizaciones OTA se usa **EAS Update**

Fuentes oficiales:

- [EAS Build](https://docs.expo.dev/build/introduction/)
- [Create your first build](https://docs.expo.dev/build/setup/)
- [Build APKs for Android devices](https://docs.expo.dev/build-reference/apk/)
- [EAS Update](https://docs.expo.dev/eas-update/introduction/)

## Preparación inicial

Dentro de `App movil`:

```powershell
npm.cmd install
npm.cmd install -g eas-cli
eas login
```

Luego configurar el proyecto para EAS:

```powershell
cd "App movil"
eas build:configure
```

Eso enlaza el proyecto con Expo y, si hace falta, añade la configuración necesaria.

## Probar en el teléfono ahora mismo

Si solo quieres probar rápido durante desarrollo:

```powershell
cd "App movil"
npx.cmd expo start
```

Y abrirlo con:

- **Expo Go** en Android
- o el QR del servidor local de Expo

## Build instalable en tu Android

Para generar un **APK instalable en tu teléfono**, la forma actual recomendada es un perfil `preview` con EAS Build.

Ya he dejado [eas.json](/C:/Users/xexud/Documents/GitHub/Simpsons-TV/App movil/eas.json) preparado.

Lanzar build:

```powershell
cd "App movil"
eas build -p android --profile preview
```

Cuando acabe:

1. Expo te dará una URL
2. la abres en tu teléfono Android
3. descargas el `.apk`
4. lo instalas manualmente

Esto sigue la guía actual oficial de Expo para APKs instalables:
[Build APKs for Android devices](https://docs.expo.dev/build-reference/apk/)

## Si luego quieres publicar cambios sin rehacer build nativo

Para cambios JavaScript, estilos o pantallas:

```powershell
eas update --branch preview --message "Cambio en conexión y LED"
```

Pero eso solo sirve si la app ya está preparada para recibir **EAS Update** y ya tienes un build instalado compatible.

## Recomendación para vuestro caso

Para vosotros ahora mismo:

1. usar `npx expo start` para probar rápido
2. cuando el LED y la conexión estén funcionando, hacer:

```powershell
eas build -p android --profile preview
```

3. instalar ese APK en vuestro teléfono Android

Así no dependéis de un método antiguo ni de builds clásicos ya obsoletos.
