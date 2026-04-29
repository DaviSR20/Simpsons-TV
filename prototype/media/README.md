# Videos de prueba

Ahora mismo conviven dos usos:

- `episodios/`: vídeos locales para la app de PC.
- `videos/`: estructura esperada por el servidor Flask del profesor.

Si queréis preparar `videos/` a partir de `episodios/`, podéis ejecutar:

```powershell
python prototype\media\prepare_professor_server_layout.py
```

El servidor del profesor detecta bien nombres como:

- `1x01.mp4`
- `S01E01.mp4`

La app de PC usa `Info.Caps.js` para la metadata y puede trabajar en modo local o en modo remoto contra ese servidor.
