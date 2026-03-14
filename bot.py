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
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties

# ================= НАЛАШТУВАННЯ =================
# Токен тільки зі змінної середовища — можна запускати на будь-якому боті (в .env локально, на Render — Environment)
TOKEN = os.environ.get("8555170398:AAHmwlzUtuUuQf0UQK4quS_cuCsgwa53960")
if not TOKEN:
    raise SystemExit("BOT_TOKEN не заданий. Додай у .env або в змінні середовища (наприклад на Render).")

# URL веб-додатку (розклад). HTTPS, без слеша в кінці. На хмарі вкажи свій Render.
WEB_APP_URL = (os.environ.get("WEB_APP_URL") or "https://student-bot3.onrender.com").rstrip("/")

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


def get_schedule_keyboard():
    """Велика кнопка внизу екрану з написом «Розклад» (без Web App — стабільно показується)."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Розклад")]
        ],
        resize_keyboard=True,
    )


def get_schedule_link_markup():
    """Інлайн-кнопка з посиланням (відправляється після натискання великої кнопки)."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Відкрити розклад", url=WEB_APP_URL)]
        ]
    )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт! 👋\n\n"
        "Я бот для студентів — тут ти можеш швидко відкрити розклад занять.\n\n"
        "Натисни велику кнопку внизу 👇",
        reply_markup=get_schedule_keyboard(),
    )


@dp.message()
async def any_message(message: types.Message):
    # Натиснули велику кнопку «Розклад» — даємо посилання
    if message.text and message.text.strip() == "📅 Розклад":
        await message.answer(
            "Відкрий розклад за посиланням 👇",
            reply_markup=get_schedule_link_markup(),
        )
        return
    if message.text and "відкрити" in message.text.lower():
        return
    await message.answer(
        "Розклад та Zoom — натисни кнопку внизу 👇",
        reply_markup=get_schedule_keyboard(),
    )


async def main():
    run_health_server()
    logger.info("Бот запущено. WEB_APP_URL=%s", WEB_APP_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
