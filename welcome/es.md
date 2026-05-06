# 👋 ¡Hola! Soy your AI Site Builder

I'm Claude — tu desarrollador AI personal en Claude Code Desktop. Listo para crear sitios web desde descripciones.

## 0. Pre-flight (una vez antes de empezar)

Verifica que `.env` en la carpeta del proyecto esté lleno:

✅ `CLOUDFLARE_API_TOKEN` — from [dash.cloudflare.com → API Tokens](https://dash.cloudflare.com/profile/api-tokens)
✅ `CLOUDFLARE_ACCOUNT_ID` — del sidebar Workers & Pages
✅ `CF_PAGES_PROJECT_NAME` — cualquier slug kebab-case, como `my-first-site`

Deja las variables Namecheap vacías por ahora — solo se necesitan si quieres un dominio propio (`/domain`).

## Qué puedo hacer

✅ Crear cualquier sitio web desde una descripción o prompt
✅ Adaptar diseño según una referencia (foto, enlace)
✅ Publicar en Cloudflare Pages en 30 segundos
✅ Editar elementos al vuelo

## Comandos

| Command | Qué hace |
|---------|--------------|
| `/status` | Verificar credenciales Cloudflare |
| `/new-site [description]` | Crear un nuevo sitio en `site/` |
| `/edit [what to change]` | Editar el sitio actual |
| `/deploy` | Publicar en Cloudflare Pages |
| `/domain` | Opcional: conectar un dominio propio |

## Vamos

Primero verifica la configuración:
```
/status
```

Si todo está ✅, dime qué construir:
```
/new-site Landing de cafetería, estilo minimalista oscuro, menú de 3
```

**Ejemplos:**
- `/new-site Portafolio de fotógrafo, paleta cálida`
- `/new-site Sitio de bufete de abogados, azul corporativo`
- `/new-site Página de lanzamiento de producto, tema oscuro, un CTA`

---
*Si algo va mal — dime, lo solucionaré.*
