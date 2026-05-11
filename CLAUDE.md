# AI Site Builder — Starter Kit (Multi-Project)
> Desktop edition. Запускається з Claude Code Desktop у папці проєкту.
> Course: [create-your-ai.site](https://create-your-ai.site)
> Version: **v3** (multi-project, multi-site)

---

## What this kit is

Один воркспейс — багато сайтів і проєктів. Кожен сайт живе у власній папці `projects/<slug>/` з власною метаінформацією і власним Cloudflare Pages target'ом. Спільні Cloudflare креди — один раз у `.env`.

Стек:
- **Claude Code Desktop** — генерує і редагує проєкти у `projects/<slug>/`
- **Cloudflare Pages** — hosting (безкоштовно). Деплой через `wrangler` локально.
- **Namecheap** *(опціонально)* — реєстратор для власного домену через `/domain`.

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

`.env` з 2 обов'язковими змінними (глобально — один раз):
- `CLOUDFLARE_API_TOKEN` — для wrangler (Cloudflare Pages — Edit permission)
- `CLOUDFLARE_ACCOUNT_ID` — з sidebar Workers & Pages у dash.cloudflare.com

**Namecheap змінні — ТІЛЬКИ для опціональної команди `/domain`.** Базовий флоу (створити + опублікувати сайт на pages.dev) працює без них.

⚠️ Ніколи не друкуй значення з `.env` у відповідях. Читай через `os.getenv()`.

---

## Project model

Кожен проєкт живе у `projects/<slug>/`:
- Файли сайту (`index.html`, `assets/`, тощо) — у корені папки проєкту
- `.project.json` — metadata: `{slug, type, cf_project_name, domain, created}`

**Active project pointer:** `projects/.active` (одна стрічка зі slug'ом активного проєкту).
- Команди без slug-аргументу використовують active
- Якщо `.active` не існує і проєктів кілька → Claude питає який
- Якщо проєкт один → автоматично використовує його

---

## Commands

| Команда | Що робить | Pre-conditions |
|---------|-----------|----------------|
| `/new-site <slug> [опис]` | Створити новий сайт у `projects/<slug>/` | `<slug>` kebab-case, унікальний |
| `/new-project <slug> [опис]` | Створити generic проєкт (не обов'язково сайт) | те саме |
| `/edit [slug] [що змінити]` | Відредагувати проєкт (active якщо slug опущений) | проєкт існує |
| `/deploy [slug]` | Опублікувати проєкт на Cloudflare Pages | `index.html` у проєкті |
| `/list` | Показати всі проєкти + їх deploy URL | — |
| `/use <slug>` | Зробити проєкт активним | проєкт існує |
| `/status` | Перевірити налаштування + список проєктів | — |
| `/domain [slug]` | Опціонально: підключити власний домен | Namecheap креди + `DOMAIN` у .env |

Природні промпти теж розпізнаються (Claude визначає команду + slug з контексту):
- "Створи лендинг для кав'ярні" → `/new-site coffee-shop ...` (slug запропонувати)
- "Зроби кнопку на сайті pizza червоною" → `/edit pizza ...`
- "Опублікуй coffee-shop" → `/deploy coffee-shop`
- "Покажи мої сайти" → `/list`

---

## Slug rules

- kebab-case: малі літери, цифри, дефіси. Без пробілів, нижніх підкреслень, юнікоду
- 3–40 символів
- Unique across `projects/` AND across Cloudflare Pages account (для першого деплою)
- Якщо студент не дав slug — Claude генерує з опису (напр. "лендинг для кав'ярні" → `cafe-landing`) і **показує** його у відповіді перед створенням

---

## Agent: New Site / New Project

**Trigger:** `/new-site <slug> [description]` або природний промпт

**Workflow:**
1. Парсити slug (validate per Slug rules). Якщо невалідний — запропонувати fix.
2. Якщо `projects/<slug>/` вже існує — STOP, спитати: replace / pick another slug.
3. Прочитати `templates/site/` як стартову точку (для `/new-site`). Для `/new-project` — порожня папка.
4. Згенерувати кастомний `projects/<slug>/index.html`, `projects/<slug>/assets/style.css` під опис.
5. Створити `projects/<slug>/.project.json` з `{slug, type: "site", cf_project_name: <slug>, domain: null, created: <date>}`.
6. Записати slug у `projects/.active`.
7. Повідомити: "Готово. Тепер `/deploy` щоб опублікувати (або `/deploy <slug>` явно)."

---

## Agent: Edit

**Trigger:** `/edit [slug] [what to change]`

**Workflow:**
1. Resolve slug: explicit arg → active → ask якщо проєктів >1.
2. Прочитати `projects/<slug>/index.html` (+ assets за потреби).
3. Внести точкові зміни.
4. Повідомити: "Готово. `/deploy [slug]` щоб оновити live."

⚠️ **Ніколи не редагуй інший проєкт замість поточного.** Якщо студент сказав "онови" без slug — використовуй active. Якщо active не співпадає з контекстом розмови (напр. щойно говорили про `pizza` але active=`coffee`) — спитай який саме.

---

## Agent: Deploy

**Trigger:** `/deploy [slug]`

**Workflow:**
1. Resolve slug (як у Edit).
2. Запустити `python3 scripts/deploy.py <slug>` (auto-installs python-dotenv).
3. Скрипт читає `projects/<slug>/.project.json`, бере `cf_project_name`, викликає `npx wrangler@3 pages deploy projects/<slug> --project-name=<cf_project_name>`.
4. Wrangler авторизується через `CLOUDFLARE_API_TOKEN` з `.env` (без OAuth).
5. Повідомити URL `https://<cf_project_name>.pages.dev`.

⚠️ При першому деплої Cloudflare створює Pages проєкт автоматично через API.

---

## Agent: List

**Trigger:** `/list`

**Workflow:**
1. Запустити `python3 scripts/list_projects.py`
2. Скрипт показує: slug | type | cf_project_name | active marker | live URL.

---

## Agent: Use

**Trigger:** `/use <slug>`

**Workflow:**
1. Перевірити що `projects/<slug>/` існує.
2. Записати slug у `projects/.active`.
3. Повідомити: "Активний проєкт: `<slug>`. Команди без slug-аргументу будуть йому."

---

## Agent: Status

**Trigger:** `/status`

**Workflow:**
1. Запустити `python3 scripts/check_setup.py`.
2. Скрипт перевіряє: CF креди → API call → success; перелічує проєкти у `projects/`.
3. Звітує: ✓ CF готовий / ○ Namecheap не налаштований (OK для базового флоу) / N projects detected.

---

## Agent: Domain (опціонально)

**Trigger:** `/domain [slug]`

**Pre-conditions:** `.env` заповнений Namecheap-змінними і `DOMAIN`.

**Workflow:**
1. Resolve slug (як у Deploy).
2. Запустити `python3 scripts/setup_domain.py <slug>`.
3. Скрипт додає apex (`@`) і `www` CNAME у Namecheap → custom hostname у CF Pages → оновлює `projects/<slug>/.project.json` з `domain`.
4. Повідомити URL з HTTPS.

DNS propagation 5хв-24год.

---

## Auto-migration from v2 (single-site layout)

**Trigger detection:** на будь-яку команду спершу перевір:
- Якщо `./site/index.html` існує АБО `./site-template/` існує АБО `.env` містить `CF_PAGES_PROJECT_NAME` — це legacy v2 layout.
- І `./projects/` НЕ існує АБО порожня → ЗАПРОПОНУЙ міграцію перш ніж виконувати команду.

**Migration workflow** (тільки з підтвердження студента):
1. Визначити slug:
   - Якщо `CF_PAGES_PROJECT_NAME` у `.env` заповнений → це slug.
   - Інакше → `my-first-site`.
   - Запропонувати студенту, дати змінити.
2. Створити `projects/<slug>/`.
3. Перенести вміст `site/*` → `projects/<slug>/`. Якщо `site/` порожній або відсутній → створити `projects/<slug>/index.html` зі скелета з `templates/site/`.
4. Створити `projects/<slug>/.project.json` з `{slug, type: "site", cf_project_name: <slug-or-old-env-value>, domain: <якщо є у env>, created: <today>}`.
5. Записати `projects/.active` ← slug.
6. Якщо `site-template/` ще не перенесений → перенести у `templates/site/`.
7. Опціонально: видалити порожні старі папки `site/`, `site-template/` (підтвердження).
8. `CF_PAGES_PROJECT_NAME` з `.env` можна не видаляти — вона ігнорується новими скриптами (всі скрипти читають `cf_project_name` з `.project.json`).
9. Повідомити: "Міграція завершена. Зараз доступно `<N>` проєктів. Активний: `<slug>`. Спробуй `/list` або `/deploy`."

---

## Files

| Path | Purpose |
|------|---------|
| `projects/<slug>/` | Окремий проєкт. Cloudflare публікує саме цю папку. |
| `projects/<slug>/.project.json` | Metadata (slug, cf_project_name, domain). |
| `projects/.active` | Slug активного проєкту (одна стрічка). |
| `templates/site/` | Reference template для `/new-site`. Не деплоїться. |
| `welcome/{uk,ru,en,es}.md` | Multilingual вітання |
| `scripts/deploy.py` | wrangler wrapper для `/deploy <slug>` |
| `scripts/new_project.py` | scaffold для `/new-site <slug>` |
| `scripts/list_projects.py` | для `/list` |
| `scripts/check_setup.py` | для `/status` |
| `scripts/setup_domain.py` | для `/domain <slug>` |
| `.env` | Глобальні креди (НІКОЛИ не коміти) |

---

## Ніколи

- ❌ Не друкувати значення з `.env`
- ❌ Не коміти `.env` у git
- ❌ Не перезаписувати чужий проєкт без явного підтвердження. Якщо `projects/<slug>/` вже існує — STOP, спитати.
- ❌ Не редагувати інший проєкт замість того, який студент має на увазі. У разі сумніву — спитати.
- ❌ Не вимагати Namecheap для базового флоу — це опціонально.
