import logging
import asyncio
from aiogram.filters.command import CommandObject, Command
from aiogram import types, Router
import g4f

logging.basicConfig(level=logging.INFO)
genetare_router = Router()

# Словарь для хранения истории разговоров
conversation_history = {}

# Параметры для адаптивного управления
MIN_DELAY = 0.6
MAX_DELAY = 2.0
INCREMENT = 0.1


# Функция для обрезки истории разговора
def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history


@genetare_router.message(Command("clear"))
async def process_clear_command(message: types.Message):
    user_id = message.from_user.id
    conversation_history[user_id] = []
    await message.reply("История диалога очищена.")


# Асинхронная функция для обработки ответа из асинхронного генератора и обновления сообщения
async def fetch_response_and_update_message(response_generator, chat_message):
    response_content = ""
    token_buffer = ""
    delay = MIN_DELAY

    async for message in response_generator:
        token_buffer += message
        if len(token_buffer) >= 50:  # Группировка по 10 токенов (можно изменить)
            response_content += token_buffer
            try:
                await chat_message.edit_text(response_content)
                delay = max(MIN_DELAY, delay - INCREMENT)  # Уменьшаем задержку
            except Exception as e:
                if 'retry after' in str(e).lower():
                    delay = min(MAX_DELAY, delay + INCREMENT)  # Увеличиваем задержку при ошибке
                else:
                    logging.error(f"Error updating message: {e}")
                    raise e
            token_buffer = ""
            await asyncio.sleep(delay)

    if token_buffer:  # Добавляем оставшиеся токены
        response_content += token_buffer
        await chat_message.edit_text(response_content)

    return response_content


# Обработчик команды /q
@genetare_router.message(Command("q"))
async def handle_q_command(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    user_input = command.args.strip()

    if not user_input:
        await message.reply("Пожалуйста, укажите вопрос после команды /q.")
        return

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    chat_history = conversation_history[user_id]

    try:
        response_generator = g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=chat_history,
            stream=True,
            provider=g4f.Provider.PerplexityLabs,
        )
        chat_message = await message.answer("...")
        chat_gpt_response = await fetch_response_and_update_message(response_generator, chat_message)
    except Exception as e:
        logging.error(f"{g4f.Provider.PerplexityLabs.__name__}:", e)
        chat_gpt_response = "Извините, произошла ошибка."
        await message.answer(chat_gpt_response)

    conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})
    logging.info(conversation_history)
    length = sum(len(msg["content"]) for msg in conversation_history[user_id])
    logging.info(f"Total conversation length: {length}")
