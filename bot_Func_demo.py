from aiogram import Dispatcher, types, F
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from aiogram.filters.command import Command
import time
from config import TOKEN
import re
import asyncio
import datetime


class ReportData:
    def __init__(self, text):
        self.data = {}
        self.extract_data(text)

    def extract_data(self, text):
        data = {}
        data['Время выезда'] = re.findall(r'время выезда (\d+ \d+)', text)[0]
        data['Показания одометра'] = re.findall(r'показания одометра (\d+)', text)[0]
        data['Прибытие на заявку'] = re.findall(r'прибытие на заявку (\d+)', text)[0]
        data['Комплекс'] = re.findall(r'комплекс (\w+-\w+)', text)[0]
        data['Время прибытия'] = re.findall(r'время прибытия (\d+ \d+)', text)[0]
        predp_deistviya = re.findall(r'предпринятые действия (.+?) время убытия', text)
        data['Предпринятые действия'] = predp_deistviya[0].split() if predp_deistviya else []
        data['Время убытия'] = re.findall(r'время убытия (\d+ \d+)', text)[0]
        data['Время пребывания на месте работы'] = re.findall(r'время пребывания на месте работы (\d+)', text)[0]
        data['Промежуточные показания одометра'] = re.findall(r'промежуточные показания одометра (\d+)', text)[0]
        data['Показания одометра'] = re.findall(r'показания одометра (\d+)', text)[1]
        data['Пройдено расстояния всего'] = re.findall(r'пройдено расстояния всего (\d+)', text)[0]

        self.data = data


def create_report(report_data, report_date):
    # Создание нового документа
    document = Document()

    # Настройки документа
    document.styles['Normal'].font.name = 'Times New Roman'
    document.styles['Normal'].font.size = Pt(14)

    # Заголовок
    title = document.add_paragraph()
    title_run1 = title.add_run('Отчет по АВР')
    title_run1.bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run1.style.font.size = Pt(16)
    title.paragraph_format.space_after = Pt(0)  # Установка интервала "После" в 0pt

    title2 = document.add_paragraph()
    title_run2 = title2.add_run(f'за {report_date}.')
    title_run2.bold = True
    title2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run2.style.font.size = Pt(16)

    # Добавление пустой строки
    document.add_paragraph()

    # Добавление данных из класса ReportData
    start_time = document.add_paragraph()
    start_time.add_run('Время выезда: ').bold = True
    start_time.add_run(report_data.data.get('Время выезда', ''))
    start_time.paragraph_format.space_after = Pt(0)

    start_odometer = document.add_paragraph()
    start_odometer.add_run('Показания одометра: ').bold = True
    start_odometer.add_run(report_data.data.get('Показания одометра', ''))
    start_odometer.paragraph_format.space_after = Pt(0)

    pribytie_text = document.add_paragraph()
    pribytie_text.add_run('Прибытие на заявку: ').bold = True
    pribytie_text.add_run(f"{report_data.data.get('Прибытие на заявку', '')} комплекс {report_data.data.get('Комплекс', '')}")
    pribytie_text.paragraph_format.space_after = Pt(0)

    object_time = document.add_paragraph()
    object_time.add_run('Время прибытия: ').bold = True
    object_time.add_run(report_data.data.get('Время прибытия', ''))
    object_time.paragraph_format.space_after = Pt(0)

    action = document.add_paragraph()
    action.add_run('Предпринятые действия: ').bold = True
    action.add_run(', '.join(report_data.data.get('Предпринятые действия', '')))
    action.paragraph_format.space_after = Pt(0)

    final_time = document.add_paragraph()
    final_time.add_run('Время убытия: ').bold = True
    final_time.add_run(report_data.data.get('Время убытия', ''))
    final_time.paragraph_format.space_after = Pt(0)

    cost_time = document.add_paragraph()
    cost_time.add_run('Время пребывания на месте работы: ').bold = True
    cost_time.add_run(f"{report_data.data.get('Время пребывания на месте работы', '')} часа")
    cost_time.paragraph_format.space_after = Pt(0)

    inter_odometer = document.add_paragraph()
    inter_odometer.add_run('Промежуточные показания одометра: ').bold = True
    inter_odometer.add_run(report_data.data.get('Промежуточные показания одометра', ''))
    inter_odometer.paragraph_format.space_after = Pt(0)

    final_odometer = document.add_paragraph()
    final_odometer.add_run('Показания одометра: ').bold = True
    final_odometer.add_run(report_data.data.get('Показания одометра', ''))
    final_odometer.paragraph_format.space_after = Pt(0)

    distance = document.add_paragraph()
    distance.add_run('Пройдено расстояния всего: ').bold = True
    distance.add_run(f"{report_data.data.get('Пройдено расстояния всего', '')} км.")
    distance.paragraph_format.space_after = Pt(0)

    # Сохранение документа
    document.save(f'Отчет по АВР на {report_date}.docx')


# Создание объектов бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправьте мне текст для создания отчета по АВР.")


# Обработчик текстового сообщения с данными для отчета
@dp.message(F.text)
async def process_report_text(message: types.Message):
    text = message.text
    report_data = ReportData(text)
    report_date = datetime.datetime.now().strftime("%d %m %Y")
    await message.reply(f"Отчет по АВР за {report_date}:\n"
                        f"Время выезда: {report_data.data.get('Время выезда', '')}\n"
                        f"Показания одометра: {report_data.data.get('Показания одометра', '')}\n"
                        f"Прибытие на заявку: {report_data.data.get('Прибытие на заявку', '')} комплекс {report_data.data.get('Комплекс', '')}\n"
                        f"Время прибытия: {report_data.data.get('Время прибытия', '')}\n"
                        f"Предпринятые действия: {', '.join(report_data.data.get('Предпринятые действия', ''))}\n"
                        f"Время убытия: {report_data.data.get('Время убытия', '')}\n"
                        f"Время пребывания на месте работы: {report_data.data.get('Время пребывания на месте работы', '')} часа\n"
                        f"Промежуточные показания одометра: {report_data.data.get('Промежуточные показания одометра', '')}\n"
                        f"Показания одометра: {report_data.data.get('Показания одометра', '')}\n"
                        f"Пройдено расстояния всего: {report_data.data.get('Пройдено расстояния всего', '')} км."
                        )


class FillReport(StatesGroup):
    time_departure = State()  # Время выезда
    odometer_reading = State()  # Показания одометра
    arrival_time = State()  # Прибытие на заявку
    actions_taken = State()  # Предпринятые действия
    departure_time = State()  # Время убытия
    time_spent = State()  # Время пребывания на месте работы
    intermediate_odometer = State()  # Промежуточные показания одометра
    final_odometer = State()  # Показания одометра
    total_distance = State()  # Пройдено расстояния всего


# Обработчик для команды /fill_report, начинающей процесс заполнения отчета
@dp.message(commands=['fill_report'])
async def fill_report_start(message: types.Message):
    # Очищаем состояние, если оно было сохранено
    await FillReport.reset_state().set()
    await message.reply("Введите время выезда (например, 'время выезда 9 35').")


# Обработчики для заполнения данных отчета
@dp.message(state=FillReport.time_departure)
async def process_time_departure(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time_departure'] = message.text
    # Переходим к следующему состоянию
    await FillReport.next()
    await message.reply("Отправьте показания одометра (например, 'показания одометра 250465').")


@dp.message(state=FillReport.odometer_reading)
async def process_odometer_reading(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['odometer_reading'] = message.text
    # Переходим к следующему состоянию
    await FillReport.next()
    await message.reply(
        "Отправьте время прибытия на заявку (например, 'прибытие на заявку 9 45 комплекс LBS11400-LBL11401').")


@dp.message(state=FillReport.arrival_time)
async def process_arrival_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['arrival_time'] = message.text
    # Переходим к следующему состоянию
    await FillReport.next()
    await message.reply("Отправьте время прибытия на объект (например, 'время прибытия 10 15').")


@dp.message(state=FillReport.actions_taken)
async def process_actions_taken(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['actions_taken'] = message.text
    # Переходим к следующему состоянию
    await FillReport.next()
    await message.reply("Отправьте время убытия (например, 'время убытия 12 30').")


@dp.message(state=FillReport.departure_time)
async def process_departure_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['departure_time'] = message.text
    # Переходим к следующему состоянию
    await FillReport.next()
    await message.reply("Отправьте время пребывания на месте работы (например, 'время пребывания на месте работы 2').")


@dp.message(state=FillReport.intermediate_odometer)
async def process_intermediate_odometer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['intermediate_odometer'] = message.text
    # Переходим к следующему состоянию
    await FillReport.next()
    await message.reply(
        "Отправьте промежуточные показания одометра (например, 'промежуточные показания одометра 250556').")


@dp.message(state=FillReport.final_odometer)
async def process_final_odometer(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['final_odometer'] = message.text
    # Переходим к следующему состоянию
    await FillReport.next()
    await message.reply("Отправьте пройденное расстояние всего (например, 'пройдено расстояния всего 182').")


# Обработчик для завершения процесса и отправки текстового сообщения с данными
@dp.message(state="*", commands=["done"])
async def send_report(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # Создаем объект ReportData, используя данные из состояния
        report_data = ReportData(data)
        # Формируем текст сообщения
        report_text = (
            f"Отчет по АВР:\n"
            f"Время выезда: {report_data.data.get('time_departure', '')}\n"
            f"Показания одометра: {report_data.data.get('odometer_reading', '')}\n"
            f"Прибытие на заявку: {report_data.data.get('arrival_time', '')} комплекс {report_data.data.get('arrival_complex', '')}\n"
            f"Время прибытия: {report_data.data.get('arrival_time', '')}\n"
            f"Предпринятые действия: {report_data.data.get('actions_taken', '')}\n"
            f"Время убытия: {report_data.data.get('departure_time', '')}\n"
            f"Время пребывания на месте работы: {report_data.data.get('time_spent', '')} часа\n"
            f"Промежуточные показания одометра: {report_data.data.get('intermediate_odometer', '')}\n"
            f"Показания одометра: {report_data.data.get('final_odometer', '')}\n"
            f"Пройдено расстояния всего: {report_data.data.get('total_distance', '')} км."
        )
        # Отправляем сообщение с данными
        await message.reply(report_text)
    # Сбрасываем состояние
    await state.finish()


# Запуск бота
async def main():
    await dp.start_polling(bot)


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


