import db
from markup import UsersCallback
import markup as nav
from asgiref.sync import sync_to_async
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
from dotenv import load_dotenv

import os




load_dotenv()
TOKEN = os.getenv("TOKEN")


ADMIN = os.getenv("ADMIN")
bot = Bot(TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


class Form(StatesGroup):
    user_id = State()
    text = State()
    answer_time = State()


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    db.new_user(message.chat.first_name, message.chat.id)
    await bot.send_message(message.from_user.id, "Добро пожаловать. Здесь вам будут приходить напоминания от менеджеров. Не пропустите важные сообщения!")


@dp.message_handler(commands=['admin'])
async def command_admin(message: types.Message):
    if message.chat.id == ADMIN:
        names_list = db.get_names()
        await bot.send_message(message.from_user.id, 'Выберете имя и id пользователя', reply_markup=nav.users_markup(names_list))
    else:
        await bot.send_message(message.chat.id, 'У вас нет доступа.')


@dp.callback_query_handler(UsersCallback.filter(space="ChoiceUser"), state=Form.user_id)
async def choice_user(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=None
    )

    logging.info(f"call = {callback_data}")
    name_id = callback_data.get("name_id")

    if name_id == "Другой":
        await bot.send_message(call.message.chat.id, 'Введите новое имя и телеграм id пользователя в формате имя-id')
        await Form.user_id.set()
    else:
        async with state.proxy() as data:
            data['user_id'] = name_id
        await bot.send_message(call.message.chat.id, 'Введите задание для пользователя')
        await Form.text.set()


@dp.message_handler(state=Form.user_id)
async def add_user(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_id'] = message.text
    await bot.send_message(message.chat.id, 'Введите задание для пользователя')
    await Form.text.set()


@dp.message_handler(state=Form.text)
async def add_user_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await bot.send_message(message.chat.id, 'Введите время на выполнение задания в формате ЧЧ:ММ:СС')
    await Form.answer_time.set()


@dp.message_handler(state=Form.answer_time)
async def add_user_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['answer_time'] = message.text
        us_id, task_text, task_date, task_answer_time = db.new_task(data['user_id'], data['text'], data['answer_time'])
    await bot.send_message(message.chat.id, "Задача добавлена в базу данных")
    mess = "Вам выдана задача\n"+ task_text + "\nВремя выполнения: " + task_answer_time
    await bot.send_message(us_id, mess, nav.ReadyMenu)
    await state.finish()

@dp.callback_query_handler(text_contains="ReadyMenu")
async def user_answer(call: CallbackQuery):
    await bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=None
    )
    answ = call.data.split(':')[2]
    mess = "Пользователь с Id" + call.message.chat.id +  " дал ответ " + answ
    await bot.send_message(ADMIN, mess)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
