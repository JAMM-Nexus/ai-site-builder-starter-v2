# 👋 ¡Hola! Soy tu AI Site Builder

Soy Claude — tu desarrollador AI personal en Claude Code Desktop. Listo para crear **cualquier cantidad** de sitios web y proyectos desde descripciones. Cada proyecto vive en su propia carpeta y se despliega de forma independiente.

## 0. Pre-flight (una vez antes de empezar)

Verifica que `.env` en la carpeta del proyecto esté completo:

✅ `CLOUDFLARE_API_TOKEN` — de [dash.cloudflare.com → API Tokens](https://dash.cloudflare.com/profile/api-tokens)
✅ `CLOUDFLARE_ACCOUNT_ID` — de la barra lateral de Workers & Pages

Son credenciales **globales** — se llenan una vez y funcionan para todos tus sitios.

Deja vacías las variables de Namecheap — solo se necesitan para un dominio propio (`/domain`).

## Lo que puedo hacer

✅ Crear cualquier sitio web o proyecto desde una descripción
✅ Mantener **muchos** sitios en paralelo en `projects/<slug>/`
✅ Adaptar el diseño desde una referencia (foto, enlace)
✅ Publicar cualquier sitio en Cloudflare Pages en 30 segundos
✅ Editar elementos al vuelo
✅ Cambiar entre sitios con `/use <slug>`

## Comandos

| Comando | Qué hace |
|---------|----------|
| `/status` | Verifica credenciales + lista tus proyectos |
| `/new-site <slug> [descripción]` | Crea un sitio nuevo en `projects/<slug>/` |
| `/edit [slug] [qué cambiar]` | Edita un sitio (el activo si no se da slug) |
| `/deploy [slug]` | Publica en Cloudflare Pages |
| `/list` | Muestra todos tus sitios + URLs |
| `/use <slug>` | Activa un proyecto |
| `/domain [slug]` | Opcional: conecta un dominio propio |

## Empezamos

Primero verifica la configuración:
```
/status
```

Si todo está ✅, dime qué construir. **Slug** = nombre corto en kebab-case (`coffee-shop`, `portfolio`, `cafe-landing`):

```
/new-site cafe-landing Landing para cafetería, estilo minimalista oscuro, menú de 3 items
```

**Ejemplos:**
- `/new-site portfolio Portafolio de fotógrafo, paleta cálida`
- `/new-site law-firm Sitio de bufete de abogados, azul corporativo`
- `/new-site product-launch Página de lanzamiento de producto, dark theme, un CTA`

## Segundo, tercer, centésimo sitio

Solo crea otro — los anteriores no desaparecen:
```
/new-site portfolio Portafolio de fotógrafo
/deploy
```

`/list` muestra todos. `/use <slug>` cambia el activo.

---
*Si algo sale mal — solo dime, lo resolveremos.*
