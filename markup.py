from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

UsersCallback = CallbackData("btn", "space", "name_id")

def users_markup(names_list):
    UsersMenu = InlineKeyboardMarkup(row_width=1)

    space = "ChoiceUser"
    names_list.append('Другой')


    for name_id in names_list:
        UsersMenu.insert(InlineKeyboardButton(
            text=name_id,
            callback_data=UsersCallback.new(
                space=space,
                name_id=name_id)
        ))
    return UsersMenu