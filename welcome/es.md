# 👋 ¡Hola! Soy your AI Site Builder

I'm Claude — tu desarrollador AI personal. Estoy conectado a tu repo de GitHub y listo para crear sitios web con IA.

## 0. Pre-flight (una vez antes de empezar)

Antes de tu primer `/new-site` asegúrate de que:

✅ **Cloudflare GitHub App** está instalada en este repo
   → dash.cloudflare.com → Workers & Pages → Create → Pages → **Connect to Git**

✅ Proyecto Pages creado (Production branch = `main`, **Build output = `site`**)

⚠️ Cloudflare GitHub App ≠ Anthropic GitHub App. Dos flujos OAuth separados — ambos son necesarios.

## Qué puedo hacer

✅ Crear cualquier sitio web a partir de una descripción o prompt
✅ Adaptar diseño según una referencia (foto, enlace)
✅ Publicar vía `git push` en 30 segundos
✅ Editar elementos al vuelo

## Comandos

| Command | Qué hace |
|---------|--------------|
| `/new-site [description]` | Crear un nuevo sitio web |
| `/edit [what to change]` | Editar el sitio actual |
| `/deploy` | Commit y push (CF reconstruye automáticamente) |
| `/status` | Verificar configuración |
| `/domain` | Opcional: conectar un dominio personalizado |

## ¡Vamos!

Verifica el estado:
```
/status
```

O ve directo:
```
/new-site Landing de cafetería, estilo minimalista oscuro, menú de 3 posiciones
```

**Ejemplos:**
- `/new-site Portafolio de fotógrafo, paleta cálida`
- `/new-site Sitio de bufete de abogados, azul corporativo`
- `/new-site Página de lanzamiento de producto, tema oscuro, un CTA`

---
*Si algo falla — dime, lo solucionaré.*
