# AI Site Builder — Starter Kit v2

> Git-driven. Усе в Claude Code Web. Без локальних інструментів.
> Powered by Claude Code | github.com/JAMM-Automation/ai-site-builder-starter-v2

---

## First Message Protocol

**Step 1 — Detect language from the user's first message:**
- Ukrainian → load `welcome/uk.md` → respond in Ukrainian
- Russian → load `welcome/ru.md` → respond in Russian
- English → load `welcome/en.md` → respond in English
- Spanish/other → load `welcome/es.md` → respond in Spanish

**Step 2 — Greet the user**, show available commands, ask what site to build.

---

## Pre-flight (one-time setup, у Cloudflare Dashboard)

Студент робить це **один раз** перед першим запуском Claude Code Web:

1. Cloudflare Dashboard → Workers & Pages → Create → Pages → **Connect to Git**
2. Install **Cloudflare GitHub App** → дати доступ до цього репо
3. Production branch = `main`, **Build output directory = `site`**, Build command = (порожнє)
4. Save and Deploy → перший білд запускається автоматично з вмістом `site/`
5. Записати у `.env` тільки якщо плануєш `/domain` — інакше пропустити

⚠️ **Cloudflare GitHub App ≠ Anthropic GitHub App.** Це два окремі OAuth flows. Обидва треба пройти (Anthropic — щоб Claude Code мав доступ до коду; Cloudflare — щоб ловив git push і деплоїв).

---

## Commands

Команди студент пише у чат Claude Code Web. Слеш не обов'язковий.

| Команда | Що робить | Потребує |
|---------|-----------|----------|
| `/new-site [опис]` | Згенерувати сайт у `site/` | нічого |
| `/edit [що змінити]` | Відредагувати поточний сайт | нічого |
| `/deploy` | Закомітити `site/` і запушити у `main` (CF auto-rebuild) | git access (Anthropic GitHub App) |
| `/status` | Перевірити підключення (GitHub repo, Cloudflare App) | нічого |
| `/domain` | Підключити власний домен через Namecheap + CF API | `.env` заповнений |

Природні промпти теж розпізнаються:
- "Створи лендинг для кав'ярні" → `/new-site`
- "Зроби кнопку червоною" → `/edit`
- "Опублікуй" / "пуш у прод" → `/deploy`

---

## Agent: New Site

**Trigger:** `/new-site [description]`

**Workflow:**
1. Прочитати `site-template/` як стартову точку
2. Згенерувати кастомний `site/index.html`, `site/assets/style.css` під опис
3. Зберегти у папці `site/` (НЕ у `site-template/`)
4. Повідомити: "Готово. Перевір локально preview, потім кажи `/deploy`."

---

## Agent: Edit

**Trigger:** `/edit [what to change]`

**Workflow:**
1. Прочитати поточний `site/index.html` і `site/assets/style.css`
2. Внести точкові зміни згідно опису
3. Повідомити: "Готово. `/deploy` щоб опублікувати."

---

## Agent: Deploy

**Trigger:** `/deploy`

**Workflow:**
1. Перевірити, що `site/index.html` існує
2. `git add site/`
3. `git commit -m "deploy: <short message>"`
4. `git push origin main`
5. Повідомити: "Pushed. Cloudflare Pages rebuild ~30 секунд. Перевір https://{project}.pages.dev"

**Без локального wrangler.** Pages-проєкт сам ловить webhook і деплоїть `site/`.

---

## Agent: Status

**Trigger:** `/status`

**Workflow:**
1. Підтвердити що Claude бачить `site/index.html` (репо підключено)
2. Перевірити чи є `.git/config` — git налаштований
3. Опціонально: перевірити чи `.env` є і чи заповнено `CLOUDFLARE_API_TOKEN` (для `/domain`)
4. Повідомити статус словами:
   ```
   ✓ GitHub repo: connected (this is your repo)
   ✓ Cloudflare GitHub App: треба перевірити вручну в dash.cloudflare.com
   ✓ /new-site, /edit, /deploy: готові
   ✓ /domain: {available якщо .env заповнений / not configured інакше}
   ```

---

## Agent: Domain (опціонально)

**Trigger:** `/domain`

**Pre-conditions:**
- `.env` створений з `.env.example` і заповнений
- `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `NAMECHEAP_*`, `DOMAIN` заповнені

**Workflow:**
1. Запустити `python3 scripts/setup_domain.py` (auto-installs requirements)
2. Скрипт додає apex (`@`) і `www` CNAME у Namecheap → CF Pages
3. Скрипт реєструє custom hostname у CF Pages через CF API
4. Повідомити URL з HTTPS

⚠️ DNS propagation 5хв — 24год. CF показує статус у dashboard.

---

## Files

| Path | Purpose |
|------|---------|
| `site/` | Деплоєвий вміст (HTML, CSS, JS). CF Pages бере звідси. |
| `site-template/` | Reference template для `/new-site`. Не деплоїться. |
| `welcome/uk.md`, `ru.md`, `en.md`, `es.md` | Multilingual вітання |
| `scripts/deploy.py` | Git-push wrapper для `/deploy` |
| `scripts/setup_domain.py` | Опціональний скрипт для `/domain` |
| `scripts/check_setup.py` | Опціональна перевірка для `/status` |
| `.env.example` | Шаблон секретів (тільки для `/domain`) |
| `.gitignore` | Виключає `.env` і `node_modules/` (НЕ `site/`) |

---

## Ніколи

- ❌ Не друкувати значення з `.env` у відповідях
- ❌ Не додавати `.env` у git
- ❌ Не пропонувати `wrangler login` — git push є джерелом деплою
- ❌ Не плутати Anthropic GitHub App і Cloudflare GitHub App
