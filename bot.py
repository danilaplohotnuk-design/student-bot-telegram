import asyncio
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import MenuButtonWebApp, WebAppInfo
from aiogram.client.default import DefaultBotProperties

# ================= НАЛАШТУВАННЯ =================
# Токен тільки зі змінної середовища — можна запускати на будь-якому боті (в .env локально, на Render — Environment)
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise SystemExit("BOT_TOKEN не заданий. Додай у .env або в змінні середовища (наприклад на Render).")

# URL веб-додатку (розклад). HTTPS обов'язково — інакше кнопка не відкриється як посилання.
_raw_url = (os.environ.get("WEB_APP_URL") or "https://student-bot3.onrender.com").strip().rstrip("/")
WEB_APP_URL = _raw_url if _raw_url.startswith(("http://", "https://")) else "https://" + _raw_url

# Порт для health-check на хмарі (Render тощо). Якщо не задано — сервер не запускається (лише бот).
PORT = os.environ.get("PORT")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Мінімальний HTTP-сервер, щоб хмара (Render) не вбивала процес — він має слухати PORT
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


def run_health_server():
    if not PORT:
        return
    port = int(PORT)
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("Health server on port %s", port)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Натисни синю кнопку внизу зліва — відкриється розклад.")


@dp.message()
async def any_message(message: types.Message):
    await message.answer("Натисни синю кнопку внизу зліва.")


async def main():
    run_health_server()
    # Якщо для бота вже був webhook (наприклад з tg-schedule-app), Telegram не дасть робити polling. Видаляємо webhook.
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook видалено, запускаємо polling.")
    except Exception as e:
        logger.warning("delete_webhook: %s", e)
    # Синя кнопка біля поля вводу (меню бота) — відкриває веб-додаток
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Відкрити розклад", web_app=WebAppInfo(url=WEB_APP_URL))
        )
        logger.info("Кнопка меню (Web App) встановлена.")
    except Exception as e:
        logger.warning("set_chat_menu_button: %s", e)
    logger.info("Бот запущено. WEB_APP_URL=%s", WEB_APP_URL)
    # Затримка перед polling: під час деплою старий інстанс ще вмикається — чекаємо, щоб уникнути Conflict
    await asyncio.sleep(45)
    logger.info("Запуск polling.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
