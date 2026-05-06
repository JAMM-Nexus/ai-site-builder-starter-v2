# AI Site Builder — Starter Kit
> Desktop edition. Запускається з Claude Code Desktop у папці проєкту.
> Course: [create-your-ai.site](https://create-your-ai.site)

---

## Stack

- **Claude Code Desktop** — генерує і редагує сайти у папці `site/`
- **Cloudflare Pages** — hosting (безкоштовно). Деплой через `wrangler pages deploy` локально.
- **Namecheap** *(опціонально)* — реєстратор для власного домену через `/domain` команду.

---

## First Message Protocol

Коли студент пише першим — визнач мову з повідомлення:
- Українська → `welcome/uk.md` → відповідай українською
- Російська → `welcome/ru.md` → російською
- English → `welcome/en.md` → English
- Spanish → `welcome/es.md` → Español

Привітайся, покажи список команд, спитай який сайт побудувати.

---

## Required setup

`.env` з 3 обов'язковими змінними:
- `CLOUDFLARE_API_TOKEN` — для wrangler (Cloudflare Pages — Edit permission)
- `CLOUDFLARE_ACCOUNT_ID` — з sidebar Workers & Pages у dash.cloudflare.com
- `CF_PAGES_PROJECT_NAME` — slug майбутнього сайту (kebab-case)

**Namecheap змінні — ТІЛЬКИ для опціональної команди `/domain`.** Базовий флоу (створити + опублікувати сайт на pages.dev) працює без них.

⚠️ Ніколи не друкуй значення з `.env` у відповідях. Читай через `os.getenv()`.

---

## Commands

| Команда | Що робить | Pre-conditions |
|---------|-----------|----------------|
| `/new-site [опис]` | Згенерувати сайт у `site/` під опис | нічого |
| `/edit [що змінити]` | Відредагувати поточний сайт | `site/index.html` існує |
| `/deploy` | Опублікувати на Cloudflare Pages через wrangler | CF креди у `.env` |
| `/status` | Перевірити налаштування | нічого |
| `/domain` | Опціонально: підключити власний домен | Namecheap креди + `DOMAIN` |

Природні промпти теж розпізнаються:
- "Створи лендинг для кав'ярні" → `/new-site`
- "Зроби кнопку червоною" → `/edit`
- "Опублікуй" → `/deploy`

---

## Agent: New Site

**Trigger:** `/new-site [description]`

**Workflow:**
1. Прочитати `site-template/` як стартову точку
2. Згенерувати кастомний `site/index.html`, `site/assets/style.css`
3. Якщо `CF_PAGES_PROJECT_NAME` у `.env` порожнє — згенерувати slug з опису і запропонувати додати у `.env`
4. Повідомити: "Готово. Тепер `/deploy` щоб опублікувати."

---

## Agent: Edit

**Trigger:** `/edit [what to change]`

**Workflow:**
1. Прочитати поточний `site/index.html` і `site/assets/style.css`
2. Внести точкові зміни
3. Повідомити: "Готово. `/deploy` щоб оновити live."

---

## Agent: Deploy

**Trigger:** `/deploy`

**Workflow:**
1. Запустити `python3 scripts/deploy.py` (auto-installs python-dotenv)
2. Скрипт викликає `npx wrangler@3 pages deploy ./site --project-name=<slug>`
3. Wrangler авторизується через `CLOUDFLARE_API_TOKEN` з `.env` (без OAuth)
4. Повідомити URL `https://<slug>.pages.dev`

⚠️ При першому деплої Cloudflare створює Pages проєкт автоматично через API.

---

## Agent: Status

**Trigger:** `/status`

**Workflow:**
1. Запустити `python3 scripts/check_setup.py`
2. Скрипт перевіряє: CF креди → API call → success
3. Звітує: ✓ CF готовий / ○ Namecheap не налаштований (OK для базового флоу)

---

## Agent: Domain (опціонально)

**Trigger:** `/domain`

**Pre-conditions:** `.env` заповнений Namecheap-змінними і `DOMAIN`

**Workflow:**
1. Запустити `python3 scripts/setup_domain.py`
2. Скрипт додає apex (`@`) і `www` CNAME у Namecheap
3. Реєструє custom hostname у CF Pages через CF API
4. Повідомити URL з HTTPS

DNS propagation 5хв-24год.

---

## Files

| Path | Purpose |
|------|---------|
| `site/` | Деплоєвий вміст (HTML, CSS, JS). Cloudflare публікує звідси. |
| `site-template/` | Reference template для `/new-site`. Не деплоїться. |
| `welcome/{uk,ru,en,es}.md` | Multilingual вітання |
| `scripts/deploy.py` | wrangler wrapper для `/deploy` |
| `scripts/check_setup.py` | Перевірка для `/status` |
| `scripts/setup_domain.py` | Опціональний для `/domain` |
| `.env` | Креди (НІКОЛИ не коміти) |

---

## Ніколи

- ❌ Не друкувати значення з `.env`
- ❌ Не коміти `.env` у git
- ❌ Не вимагати Namecheap для базового флоу — це опціонально
