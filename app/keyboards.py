from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def generate_edit_keyboard():
    edit_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
               InlineKeyboardButton(text="Изменить время выезда", callback_data="edit_time_departure"),
               InlineKeyboardButton(text="Изменить значение начального одометра", callback_data="edit_odometer_reading"),
               InlineKeyboardButton(text="Изменить фото начального одометра", callback_data="edit_picture_new_odometer"),
               InlineKeyboardButton(text="Изменить номер заявки", callback_data="edit_arrival_object"),
               InlineKeyboardButton(text="Изменить название комплекса", callback_data="edit_arrival_complex"),
               InlineKeyboardButton(text="Изменить время прибытия на объект", callback_data="edit_arrival_time"),
               InlineKeyboardButton(text="Изменить действия", callback_data="edit_actions_taken"),
               InlineKeyboardButton(text="Изменить время убытия", callback_data="edit_departure_time"),
               InlineKeyboardButton(text="Изменить значения промеж. одометра", callback_data="edit_intermediate_odometer"),
               InlineKeyboardButton(text="Изменить фото промеж. одометра", callback_data="edit_picture_intermediate_odometer"),
               InlineKeyboardButton(text="Изменить конечное значение одометра", callback_data="edit_final_odometer"),
               InlineKeyboardButton(text="Изменить фото конечного одометра", callback_data="edit_picture_final_odometer"),
            ]
        ]
    )