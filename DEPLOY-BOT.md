# Деплой бота (bot.py) на хмару (Render)

Бот вітає студентів і показує кнопку «Відкрити розклад». Інструкція — як закинути його на Render.

---

## Крок 1. GitHub (репо вже створений)

У PowerShell у папці з ботом:

```powershell
cd "C:\Users\danil\Desktop\бот розклад"
git init
git add .
git commit -m "Бот: привітання + кнопка розклад"
git branch -M main
git remote add origin https://github.com/danilaplohotnuk-design/ИМ'Я_РЕПО.git
git push -u origin main
```

Замість **ИМ'Я_РЕПО** підстав URL свого репо. Якщо `origin` вже був, спочатку: `git remote remove origin`, потім `git remote add origin ...` і `git push -u origin main`.

---

## Крок 2. Render.com

1. Зайди на **render.com**, увійди (краще через GitHub).
2. **New** → **Web Service**.
3. Обери репозиторій з ботом. Branch: **main**.
4. Налаштування:
   - **Name:** student-bot (або будь-яка назва).
   - **Runtime:** Python 3.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
   - **Instance type:** Free.
5. **Environment** → Add Environment Variable:
   - **BOT_TOKEN** = токен бота від BotFather.
   - **WEB_APP_URL** = посилання на додаток з розкладом, наприклад `https://student-bot3.onrender.com` (без слеша в кінці).
6. **Create Web Service**. Дочекайся статусу **Live**.

Після деплою бот працює на хмарі. На безкоштовному плані сервіс засинає після простою; після першого повідомлення може бути затримка 30–60 с.

---

## 3. Локально

Скопіюй `.env.example` у `.env`, вкажи `BOT_TOKEN` і `WEB_APP_URL`. Потім:

```powershell
cd "C:\Users\danil\Desktop\бот розклад"
pip install -r requirements.txt
python bot.py
```

Порт для health server задавати не обов'язково — без `PORT` бот просто запускає лише polling.
