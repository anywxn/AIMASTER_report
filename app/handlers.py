import os
import re
from aiogram.filters.command import Command
from aiogram import types, F, Router, Bot
import librosa
import soundfile as sf
import speech_recognition as sr

router = Router()


def parse_text(text):
    # Шаблон для поиска всех ключевых слов и их значений
    pattern = r'(\bобъект\b|\bработа\b|\bначальный пробег\b|\bконечный пробег\b)\s*:\s*([^\n]+)'

    # Поиск всех совпадений с шаблоном в тексте
    matches = re.findall(pattern, text, re.IGNORECASE)

    # Создание словаря для хранения извлеченных значений
    parsed_data = {keyword.lower(): value.strip() for keyword, value in matches}

    return parsed_data


def generate_report(text):
    # Извлекаем ключевые слова и их значения из текста
    parsed_data = parse_text(text)

    # Создаем экземпляр класса Report
    report = Report()

    # Заполняем данные отчета из извлеченных значений
    for keyword, value in parsed_data.items():
        if keyword == "объект":
            report.object = value
        elif keyword == "работа":
            report.work = value
        elif keyword == "начальный пробег":
            report.initial_mileage = value
        elif keyword == "конечный пробег":
            report.final_mileage = value

    # Генерируем отчет
    report_text = report.generate_report()

    return report_text


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
class Report:
    def __init__(self):
        self.object = None
        self.work = None
        self.initial_mileage = None
        self.final_mileage = None

    def generate_report(self):
        report = "<b>Отчет:</b>\n"
        if self.object is not None:
            report += f"<b>Объект:</b> {self.object}\n"
        if self.work is not None:
            report += f"<b>Работа:</b> {self.work}\n"
        if self.initial_mileage is not None:
            report += f"<b>Начальный пробег:</b> {self.initial_mileage}\n"
        if self.final_mileage is not None:
            report += f"<b>Конечный пробег:</b> {self.final_mileage}\n"
        return report


def generate_report(text):
    # Извлекаем ключевые слова и их значения из текста
    parsed_data = parse_text(text)

    # Создаем экземпляр класса Report
    report = Report()

    # Заполняем данные отчета из извлеченных значений
    for keyword, value in parsed_data.items():
        if keyword == "объект":
            report.object = value
        elif keyword == "работа":
            report.work = value
        elif keyword == "начальный пробег":
            report.initial_mileage = value
        elif keyword == "конечный пробег":
            report.final_mileage = value

    # Генерируем отчет
    report_text = report.generate_report()

    return report_text



# Обработчик команды /start
@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет, помогу тебе с составлением отчетов с выезда на объекты\n"
                 "<i>Пришли мне голосовое </i> я его распознаю и сформирую отчет в docs файл, \n"
                 "<b>но перед этим посмотри дополнительную информацию по команде /info или по кнопке в меню</b>",
                 parse_mode="html")


# Обработчик команды /info
@router.message(Command("info"))
async def send_info(bot: Bot, message: types.Message):
    await message.reply("Чтобы сообщение хорошо распознавалось необходимо:"
                        "<b><i>записать голосовое сообщение четко и без лишнего шума</i></b>"
                        "\nНужно сказать: Объект, произведенные работы, начальный пробег и конечный пробег в одном голосовом сообщении,\n"
                        "<b>Следуйте инструкциям для максимально эффективного результата</b>", parse_mode="html")


# Обработчик голосовых сообщений
@router.message(F.voice)
async def handle_voice(message: types.Message, bot=None):
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