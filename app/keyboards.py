from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton

)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Посмотреть отчет", callback_data="/view_report"),
            KeyboardButton(text="Очистить отчет", callback_data="/reset_report")
        ],
        [
            KeyboardButton(text="Создать отчет в файле docx", callback_data="create_report")
        ],
        [
            KeyboardButton(text="Изменить время выезда", callback_data="edit_time_departure")
        ],
        [
            KeyboardButton(text="Изменить значение начального одометра", callback_data="edit_odometer_reading")
        ],
        [
            KeyboardButton(text="Изменить фото начального одометра", callback_data="edit_picture_new_odometer")
        ],
        [
            KeyboardButton(text="Изменить номер заявки", callback_data="edit_arrival_object")
        ],
        [
            KeyboardButton(text="Изменить название комплекса", callback_data="edit_arrival_complex")
        ],
        [
            KeyboardButton(text="Изменить время прибытия на объект", callback_data="edit_arrival_time")
        ],
        [
            KeyboardButton(text="Изменить действия", callback_data="edit_actions_taken")
        ],
        [
            KeyboardButton(text="Изменить время убытия", callback_data="edit_departure_time")
        ],
        [
            KeyboardButton(text="Изменить значения промеж. одометра", callback_data="edit_intermediate_odometer")
        ],
        [
            KeyboardButton(text="Изменить фото промеж. одометра", callback_data="edit_picture_intermediate_odometer")
        ],
        [
            KeyboardButton(text="Изменить конечное значение одометра", callback_data="edit_final_odometer")
        ],
        [
            KeyboardButton(text="Изменить фото конечного одометра", callback_data="edit_picture_final_odometer")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберете действие из меню",
    selective=True,
)


