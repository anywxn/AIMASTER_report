import time
import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import TOKEN
import logging
from aiogram import Bot, Dispatcher, types, F
from app.handlers import handle_voice, router
from app.fill_report import routers
from app.generate import genetare_router

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


async def main():
    dp.include_router(router)
    dp.include_router(routers)
    dp.include_router(genetare_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


@routers.message(F.voice)
async def handle_voice_wrapper(message: types.Message):
    await handle_voice(message, bot=bot)


# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())

