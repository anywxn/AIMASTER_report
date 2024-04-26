import os
import traceback
import re
import time
import asyncio
from aiogram.filters.command import Command
from aiogram.types import ContentType, File, Message
from config import TOKEN
import logging
from aiogram import Bot, Dispatcher, types, F
import librosa
import soundfile as sf
import speech_recognition as sr

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


#Паттерн для парсинга текста гс
def parse_text(text):
    # Шаблон для поиска ключевых слов и значений
    pattern = r'(\bобъект\b|\bработа\b|\bначальный пробег\b|\bконечный пробег\b)\s*:\s*([^\n]+)'

    # Поиск всех совпадений с шаблоном в тексте
    matches = re.findall(pattern, text, re.IGNORECASE)

    # Создание словаря для хранения извлеченных значений
    parsed_data = {}
    for match in matches:
        key = match[0].lower()  # Приведение ключа к нижнему регистру
        value = match[1].strip()  # Удаление лишних пробелов в значении
        parsed_data[key] = value

    return parsed_data


# Функция для распознавания речи
def recognize_speech(phrase_wav_path):
    r = sr.Recognizer()
    hellow = sr.AudioFile(phrase_wav_path)
    with hellow as source:
        audio = r.record(source)
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
    try:
        s = r.recognize_google(audio, language="ru-RU").lower()
        print("Text: " + s)
        result = s
    except Exception as e:
        print("Exception: " + str(e))
        result = None
    return result


# Функция для создания отчета на основе распознанного текста
def generate_report(text):
    # Ключевые слова
    keywords = ["объект", "работа", "начальный", "конечный"]

    # Инициализация переменных для хранения извлеченных значений
    parsed_data = {keyword: None for keyword in keywords}
    initial_mileage = None  # Переменная для хранения начального пробега
    final_mileage = None  # Переменная для хранения конечного пробега

    # Разбиваем текст на слова
    words = text.lower().split()

    # Переменная для хранения текущего ключевого слова
    current_keyword = None

    # Проверяем каждое слово на наличие ключевых слов
    for word in words:
        if word in keywords:
            # Если слово является ключевым, сохраняем его как текущее ключевое слово
            current_keyword = word
        elif current_keyword is not None:
            # Если есть текущее ключевое слово, сохраняем следующее слово как его значение
            if current_keyword == "начальный":
                if word.isdigit():  # Проверяем, является ли слово числом
                    initial_mileage = word
            elif current_keyword == "конечный":
                if word.isdigit():  # Проверяем, является ли слово числом
                    final_mileage = word
            else:
                if parsed_data[current_keyword] is None:
                    parsed_data[current_keyword] = word
                else:
                    # Если значение уже существует, добавляем к нему новое слово
                    parsed_data[current_keyword] += " " + word

    # Формируем отчет
    report = "<b>Отчет:</b>\n"
    for keyword, value in parsed_data.items():
        if value is not None:
            report += f"<b>{keyword.capitalize()}:</b> {value}\n"
    if initial_mileage is not None:
        report += f"<b>Начальный пробег:</b> {initial_mileage}\n"
    if final_mileage is not None:
        report += f"<b>Конечный пробег:</b> {final_mileage}\n"

    return report


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет, помогу тебе с составлением отчетов с выезда на объекты\n"
                 "<i>Пришли мне голосовое </i> я его распознаю и сформирую отчет в docs файл, \n"
                 "<b>но перед этим посмотри дополнительную информацию по команде /info или по кнопке в меню</b>",
                 parse_mode="html")


# Обработчик команды /info
@dp.message(Command("info"))
async def send_info(message: types.Message):
    await message.reply("Чтобы сообщение хорошо распознавалось необходимо:"
                        "<b><i>записать голосовое сообщение четко и без лишнего шума</i></b>"
                        "\nНужно сказать: Объект, произведенные работы, начальный пробег и конечный пробег в одном голосовом сообщении,\n"
                        "<b>Следуйте инструкциям для максимально эффективного результата</b>", parse_mode="html")


# Обработчик голосовых сообщений
@dp.message(F.voice)
async def handle_voice(message: types.Message):
    await message.reply("Ваше сообщение распознаётся...")
    file_info = await bot.get_file(message.voice.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    # Сохраняем файл на диск
    file_id = message.voice.file_id
    file_name = f'./audio/{file_id}.ogg'
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file.read())

    # Конвертируем файл в формат WAV
    audio_path = f'./audio/{file_id}.ogg'
    y, sr = librosa.load(audio_path)
    out_path = f'./audio/{file_id}1.wav'
    sf.write(out_path, y, sr, format='wav')

    # Распознаем речь
    recognized_text = recognize_speech(out_path)
    edited_message_text = '<b><i>Ваш запрос: </i></b>' + recognized_text
    await message.answer(edited_message_text, parse_mode="html")

    # Формируем отчет на основе распознанного текста
    report = generate_report(recognized_text)

    # Отправляем отчет пользователю
    await message.reply(report, parse_mode="html")

    # Удаляем временные файлы
    os.remove(file_name)
    os.remove(out_path)


async def main():
    await dp.start_polling(bot)

# Запуск бота
if __name__ == '__main__':
    while True:
        try:
            try:
                asyncio.run(main())
                time.sleep(5)
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                time.sleep(5)
        except KeyboardInterrupt:
            print("Завершение выполнения")