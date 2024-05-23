import os
from aiogram.filters.command import Command
from aiogram import types, F, Router
import librosa
import soundfile as sf
import speech_recognition as sr
from app.fill_report import extract_data
from app.keyboards import main_kb

router = Router()


# Функция для распознавания речи
def recognize_speech(phrase_wav_path):
    r = sr.Recognizer()
    with sr.AudioFile(phrase_wav_path) as source:
        audio = r.record(source)
        r.pause_threshold = 0.8  # Установка порога паузы
        r.adjust_for_ambient_noise(source, duration=1)  # Калибровка уровня шума

    try:
        recognized_text = r.recognize_google(audio, language="ru-RU").lower()
        print("Recognized Text: " + recognized_text)
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio")
        recognized_text = None
    except sr.RequestError as e:
        print("Could not request results from Speech Recognition service; {0}".format(e))
        recognized_text = None

    return recognized_text


# Обработчик команды /start
@router.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет, помогу тебе с составлением отчетов АВР\n"
        "Вы можете составить отчет с помощью голоса, \n"
        "Говорите так как говорите обычно, ненужно говорить быстрее или медленнее, \n"
        "\nВот что необходимо сказать\n"
        "\n<b>время выезда</b> 10:00 (десять ноль ноль)\n"
        "<b>начальные показания одометра</b> 250542 (Двести пятьдесят тысяч пятьсот сорок два)\n"
        "<b>прибытие на заявку</b> (Назвать номер заявки)\n"
        "<b>комплекс Б-1</b> (Назвать номер или название комплекса)\n"  
        "<b>время прибытия на заявку</b> 15:00 (пятнадцать ноль ноль)\n"
        "<b>предпринятые действия:</b> перезагрузка, перенастройка и т.д.\n"
        "<b>время убытия</b> 18:00 (восемнадцать ноль ноль)\n"
        "<b>промежуточные показания одометра</b> 250600 (Двести пятьдесят тысяч шестьсот)\n"
        "<b>конечные показания одометра</b> 250660 (Двести пятьдесят тысяч шестьсот шестьдесят)\n"
        "\nПосле обработки голосового сообщения вам выведут результаты распознавания\n" 
        "<b>вы сможете их изменить с помощью клавиатуры на экране</b>\n"
        "\nТак-же вы можете заполнить отчет в текстовом формате с помощью команды /fill_report\n"
        "Когда убедитесь, что все данные верны и картинки заполнены нажмите кнопку 'Создать отчет в файле docx'\n"
        "/info - нажмите для дополнительной информации",
    )


# Обработчик команды /info
@router.message(Command("info"))
async def send_info(message: types.Message):
    await message.reply(
        "Чтобы сообщение хорошо распознавалось необходимо:\n"
        "<b><i>записать голосовое сообщение четко и без лишнего шума</i></b>\n"
        "<b>Следуйте инструкциям для максимально эффективного результата</b>\n"
        "<b><i>Список команд бота: </i></b>\n"
        "/start - Начало\n"
        "/info - Дополнительная информация\n"
        "/q - Задать вопрос ИИ Пример: /q как дела?\n"
        "/fill_report - Составить отчет пошагово\n"
        "/view_report - Просмотреть текущий отчет\n"
        "/reset_report - Очистить текущий отчет\n",
    )


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

    user_id = message.from_user.id
    await message.answer( await extract_data(user_id, recognized_text), reply_markup=main_kb)

    # Удаляем временные файлы
    os.remove(file_name_ogg)
    os.remove(out_path)
