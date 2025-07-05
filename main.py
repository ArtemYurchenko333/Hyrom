import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, Message
from openai import AsyncOpenAI
from io import BytesIO
import base64

BOT_TOKEN = os.getenv("BOT_TOKEN4")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY4")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

user_prompts = {}

@dp.message(lambda message: message.photo)
async def handle_photo(message: Message):
    await message.reply("✅ Фото получено! Теперь напиши, что ты хочешь узнать по руке (например, 'расскажи про линию судьбы').")
    user_prompts[message.from_user.id] = {
        "photo": message.photo[-1].file_id
    }

@dp.message(lambda message: message.text and message.from_user.id in user_prompts)
async def handle_prompt(message: Message):
    photo_file_id = user_prompts[message.from_user.id]["photo"]
    prompt_text = message.text

    file = await bot.get_file(photo_file_id)
    file_bytes = await bot.download_file(file.file_path)
    file_content = file_bytes.read()
    b64_image = base64.b64encode(file_content).decode()

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты профессиональный хиромант. По изображению руки и запросу пользователя, анализируй ладонь и отвечай на основе хиромантии."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
            ]}
        ]
    )

    await message.reply(response.choices[0].message.content)

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
