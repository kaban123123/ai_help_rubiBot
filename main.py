import asyncio
import os
import uuid
import base64
import urllib3
import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_TOKEN = os.environ.get("TG_TOKEN", "").strip()
GIGACHAT_KEY = os.environ.get("GIGACHAT_KEY", "").strip()

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_access_token() -> str:
    auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    auth_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {GIGACHAT_KEY}",
    }
    auth_data = {"scope": "GIGACHAT_API_PERS"}

    response = requests.post(
        auth_url,
        headers=auth_headers,
        data=auth_data,
        verify=False,
        timeout=60,
    )

    if response.status_code != 200:
        raise Exception(f"Ошибка авторизации GigaChat: {response.status_code} {response.text}")

    data = response.json()
    token = data.get("access_token")
    if not token:
        raise Exception(f"Не получен access_token: {response.text}")

    return token

def get_gigachat_response(user_message: str) -> str:
    try:
        access_token = get_access_token()

        chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        chat_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        chat_data = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": "Ты полезный помощник для Telegram-бота ai_help_rubiBot."},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        response = requests.post(
            chat_url,
            headers=chat_headers,
            json=chat_data,
            verify=False,
            timeout=120,
        )

        if response.status_code != 200:
            return f"Ошибка GigaChat: {response.status_code} {response.text}"

        result = response.json()
        return result["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return f"Ошибка ИИ: {e}"

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "🤖 Привет! Я ai_help_rubiBot.\n\n"
        "Напишите любой вопрос, и я отвечу через ИИ.\n"
        "Команды:\n"
        "/start — приветствие\n"
        "/help — справка\n"
        "/chat [текст] — задать вопрос ИИ"
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "📚 Справка\n\n"
        "Просто отправьте сообщение — бот ответит через ИИ.\n"
        "Или используйте команду:\n"
        "/chat Как научиться Python?"
    )

@dp.message(Command("chat"))
async def chat_command(message: Message):
    chat_text = message.text.split("/chat", 1)[1].strip()
    if not chat_text:
        await message.answer("Напишите текст после /chat")
        return

    await message.answer("🤔 Обрабатываю запрос...")
    response = get_gigachat_response(chat_text)
    await message.answer(response)

@dp.message()
async def handle_message(message: Message):
    if not message.text or message.text.startswith("/"):
        return

    await message.answer("🤖 Думаю...")
    response = get_gigachat_response(message.text)
    await message.answer(response)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
