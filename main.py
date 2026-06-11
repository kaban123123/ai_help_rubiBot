import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import requests

API_TOKEN = os.environ.get("TG_TOKEN")
GIGACHAT_KEY = os.environ.get("GIGACHAT_KEY")
GIGACHAT_SCOPE = os.environ.get("GIGACHAT_SCOPE", "bot")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_gigachat_response(user_message: str) -> str:
    try:
        auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        auth_headers = {
            "RQSN": GIGACHAT_SCOPE,
            "Authorization": f"Bearer {GIGACHAT_KEY}"
        }
        
        auth_response = requests.post(auth_url, headers=auth_headers)
        auth_token = auth_response.headers["Authorization"].split(" ")[1]
        
        chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        chat_headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "Rqmt": "GIGACHAT-4-5"
        }
        
        chat_data = {
            "model": "GigaChat-4.5-Latest",
            "messages": [
                {"role": "system", "content": "Вы помощник для ai_help_rubiBot."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(chat_url, headers=chat_headers, json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Ошибка: {response.status_code}"
    
    except Exception as e:
        return f"Ошибка: {str(e)}"

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("🤖 Привет! Я ai_help_rubiBot с ИИ. Напишите любой вопрос!")

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer("📚 Напишите любой вопрос — ИИ ответит!")

@dp.message(Command("chat"))
async def chat_command(message: Message):
    chat_text = message.text.split("/chat", 1)[1].strip()
    if not chat_text:
        await message.answer("❗ Напишите текст после /chat")
        return
    await message.answer("🤔 ИИ обрабатывает...")
    response = get_gigachat_response(chat_text)
    await message.answer(response)

@dp.message()
async def handle_message(message: Message):
    if message.text.startswith("/"):
        return
    await message.answer("🤖 ИИ читает...")
    response = get_gigachat_response(message.text)
    await message.answer(response)

async def main():
    print("🚀 Запуск бота...")
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())