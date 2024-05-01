import os
import re
from aiogram.filters.command import Command
from aiogram import types, F, Router, Bot
from aiogram.types import FSInputFile
import librosa
import soundfile as sf
import speech_recognition as sr
from docx import Document
from datetime import datetime

router = Router()


input_keywords = ["объект", "работа", "начальный", "конечный"]


class TextProcessor:
    def __init__(self, text, keywords):
        self.text = text
        self.keywords = keywords
        self.data = {
            "Объект": None,
            "Работа": None,
            "Начальный пробег": None,
            "Конечный пробег": None
        }

    def process_text(self):
        words = self.text.split()
        i = 0
        while i < len(words):
            word = words[i]
            if word.lower() in self.keywords:
                if word.lower() == "начальный":
                    j = i + 1
                    while j < len(words):
                        if words[j].isdigit():
                            self.data["Начальный пробег"] = words[j]
                            break
                        j += 1
                elif word.lower() == "конечный":
                    j = i + 1
                    while j < len(words):
                        if words[j].isdigit():
                            self.data["Конечный пробег"] = words[j]
                            break
                        j += 1
                else:
                    current_key = word.capitalize()
                    current_value = " ".join(words[i + 1:]).strip()
                    next_keyword_index = len(words)  # По умолчанию, следующее ключевое слово - последнее слово в тексте
                    for keyword in self.keywords:
                        if keyword in words[i+1:]:
                            next_keyword_index = min(next_keyword_index, words[i+1:].index(keyword) + i + 1)
                    current_value = " ".join(words[i + 1:next_keyword_index]).strip()
                    self.data[current_key] = current_value
                    i = next_keyword_index - 1  # Устанавливаем индекс i на следующее ключевое слово
            i += 1

    def generate_report(self):
        report = "Отчет:\n"
        for key, value in self.data.items():
            if value is not None:
                report += f"{key}: {value}\n"
        return report.strip()

    def save_to_word(self, filename):
        doc = Document()
        report = self.generate_report()
        doc.add_paragraph(report)
        doc.save(filename)


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
    print('recognize_speech: ' + result)
    return result


# Обработчик команды /start
@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет, помогу тебе с составлением отчетов с выезда на объекты\n"
                 "<i>Пришли мне голосовое </i> я его распознаю и сформирую отчет в docs файл, \n"
                 "<b>но перед этим посмотри дополнительную информацию по команде /info или по кнопке в меню</b>",
                 parse_mode="html")


# Обработчик команды /info
@router.message(Command("info"))
async def send_info(message: types.Message):
    await message.reply("Чтобы сообщение хорошо распознавалось необходимо:"
                        "<b><i>записать голосовое сообщение четко и без лишнего шума</i></b>"
                        "\nНужно сказать: Объект, произведенные работы, начальный пробег и"
                        " конечный пробег в одном голосовом сообщении,\n"
                        "<b>Следуйте инструкциям для максимально эффективного результата</b>", parse_mode="html")


# Обработчик голосовых сообщений
@router.message(F.voice)
async def handle_voice(message: types.Message, bot=None):
    await message.reply("Ваше сообщение распознаётся...")
    file_info = await bot.get_file(message.voice.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    # Сохраняем файл на диск
    file_id = message.voice.file_id
    file_name_ogg = f'./audio/{file_id}.ogg'
    with open(file_name_ogg, 'wb') as new_file:
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

    # Получаем текущую дату
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Создаем экземпляр TextProcessor и обрабатываем распознанный текст
    report_text = TextProcessor(recognized_text, input_keywords)
    report_text.process_text()

    # Получаем значение поля "Объект" из TextProcessor
    object_name = report_text.data["Объект"]

    # Составляем имя файла с текущей датой и значением поля "Объект"
    file_name_docx = f"./docs/{object_name}_{current_date}_отчет.docx"

    # Сохраняем отчет в документ Word
    report_text.save_to_word(file_name_docx)

    # Отправляем отчет пользователю
    await message.reply(report_text.generate_report(), parse_mode="html")

    # Отправляем файл в формате документа
    document = FSInputFile(path=file_name_docx)
    await message.answer_document(document=document)

    # Удаляем временные файлы
    os.remove(file_name_ogg)
    os.remove(out_path)
