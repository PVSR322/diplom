import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.helper import Helper, HelperMode, ListItem
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import mysql.connector
from mysql.connector import Error
from database import db
from config import TOKEN, HOST_DB, USER_DB, PASS_DB, PORT_DB, NAME_DB
import kb
import random
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token=TOKEN, )
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
connection = db.create_connection(HOST_DB, USER_DB, PASS_DB, PORT_DB, NAME_DB)

#Состояния
class TestStates(Helper):
    mode = HelperMode.snake_case

    AUTHORIZED = ListItem()
    REGISTRATION_0 = ListItem()
    REGISTRATION_1 = ListItem()
    COURSE_MENU = ListItem()
    LESSONS_MENU = ListItem()
    THEORY_MENU = ListItem()
    TEST = ListItem()
    TASK = ListItem()

# Вывод меню / старт
@dp.callback_query_handler(state='*', text='menu')
async def process_menu_button(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    await state.reset_state()
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    telegram_id = callback_query.from_user.id
    user_info = db.get_user_data(connection, telegram_id)
    if (db.create_user(connection, telegram_id) or (user_info[2] == 0)):
        await bot.send_message(callback_query.from_user.id, "Здравствуйте! Это бот-учитель по 3D редактору blender\n"
                                                            "Для начала обучения необходимо зарегестрироваться.\n\n"
                                                            "1️⃣ Напишите ваше ФИО:")
        await state.set_state(TestStates.REGISTRATION_0[0])
    else:
        await bot.send_message(callback_query.from_user.id ,f"Здравствуйте, {user_info[0]}!\n\n"
                                                            f"📌 Ваша зачетная книжка: {user_info[1]}\n"
                                                            f"📚 Для работы с ботом используйте меню:", reply_markup=kb.main_menu_keyb)
        await state.set_state(TestStates.AUTHORIZED[0])

@dp.message_handler(state='*', commands=['start'])
async def process_start_command(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()
    telegram_id = message.from_user.id
    user_info = db.get_user_data(connection, telegram_id)
    if (db.create_user(connection, telegram_id) or (user_info[2] == 0)):
        await message.reply("Здравствуйте! Это бот-учитель по 3D редактору blender\n"
                            "Для начала обучения необходимо зарегестрироваться.\n\n"
                            "1️⃣ Напишите ваше ФИО:")
        await state.set_state(TestStates.REGISTRATION_0[0])
    else:
        await message.reply(f"Здравствуйте, {user_info[0]}!\n\n"
                            f"📌 Ваша зачетная книжка: {user_info[1]}\n"
                            f"📚 Для работы с ботом используйте меню:", reply_markup=kb.main_menu_keyb)
        await state.set_state(TestStates.AUTHORIZED[0])

#=====================REGISTRATION=============================
@dp.message_handler(state=TestStates.REGISTRATION_0)
async def reg_first_step(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    nickname = message.text
    if (not nickname) or (len(nickname) > 50):
        return await message.reply("❗️ Я не понял как к вам обращаться, пожалуйста напишите ваше корректное ФИО:")

    async with state.proxy() as user_data:
        user_data['fio'] = nickname

    await message.reply('2️⃣ Напишите номер вашей зачетной книжки:', reply=False)
    await state.set_state(TestStates.REGISTRATION_1[0])

@dp.message_handler(state=TestStates.REGISTRATION_1)
async def reg_second_step(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    zachetka = message.text
    if (not zachetka.isdigit()) or (len(zachetka) > 20):
        return await message.reply("❗️ Пожалуйста напишите корректный номер вашей зачетной книжки:")

    async with state.proxy() as user_data:
        user_data['record_book'] = zachetka
        nickname = user_data['fio']

    await message.reply(f'3️⃣ Подтвердите введенные данные.\n'
                        f'📌 ФИО: {nickname} \n'
                        f'📌 Зачетная книжка: {zachetka}', reply=False, reply_markup=kb.confirm_reg_keyb)

@dp.callback_query_handler(state=TestStates.REGISTRATION_1, text = 'confirm_reg_true')
async def process_callback_button_reg(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    async with state.proxy() as user_data:
        fio = user_data['fio']
        record_book = user_data['record_book']

    result = db.register_user(connection, callback_query.from_user.id, fio, record_book)
    if (result == 1):
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, '✅ Успешная регистрация!', reply_markup=kb.menu_keyb)
    else:
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, '❌ Данные для регистрации некорректны, пожалуйста пройдите регистрацию снова.\n\n'
                                                            '1️⃣ Напишите ваше ФИО:')
        await state.set_state(TestStates.REGISTRATION_0[0])

@dp.callback_query_handler(state=TestStates.REGISTRATION_1, text = 'confirm_reg_false')
async def process_callback_button_reg2(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    state = dp.current_state(user=callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, '❗️ Введите данные заново!\n'
                                                        'Напишите ваше ФИО:')
    await state.set_state(TestStates.REGISTRATION_0[0])
#=========================REGISTRATION END=================================



#=====================COURSE MENU==============================
@dp.callback_query_handler(state=TestStates.AUTHORIZED, text='course_menu')
async def process_menu_button(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.set_state(TestStates.COURSE_MENU[0])
    user_info = db.get_user_data(connection, callback_query.from_user.id)

    course_result = db.get_course_info(connection)
    course_keyb = InlineKeyboardMarkup(row_width=1)
    for course_id in course_result:
        course_keyb.insert(InlineKeyboardButton(f'{course_id[1]}', callback_data=f'get_lesson_{course_id[0]}'))
    course_keyb.insert(kb.menu_button)

    await bot.send_message(callback_query.from_user.id , f"Меню доступных курсов\n"
                                                         f"Пройдено курсов:\n"
                                                         f"Осталось пройти:\n\n"
                                                         f"Выберите курс, чтобы посмотреть доступные уроки для изучения:", reply_markup=course_keyb)
    del course_keyb
#=====================COURSE MENU END==========================



#=====================LESSONS MENU ============================
@dp.callback_query_handler(state=TestStates.COURSE_MENU)
async def process_menu_button(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.set_state(TestStates.LESSONS_MENU[0])

    user_info = db.get_user_data(connection, callback_query.from_user.id)
    course_id = callback_query.data
    lessons_result = db.get_lessons_info(connection)
    lessons_keyb = InlineKeyboardMarkup(row_width=1)
    for lesson in lessons_result:
        if (f"get_lesson_{lesson[1]}" == course_id):
            lessons_keyb.insert(InlineKeyboardButton(f'{lesson[2]}', callback_data=f'get_theory_{lesson[0]}'))
    lessons_keyb.insert(kb.menu_button)

    await bot.send_message(callback_query.from_user.id , f"Меню доступных уроков\n"
                                                         f"Пройдено уроков:\n"
                                                         f"Осталось пройти:\n\n"
                                                         f"Выберите урок, который хотите пройти:", reply_markup=lessons_keyb)
    del lessons_keyb
#=====================LESSONS MENU END========================

#=====================THEORY MENU ============================
@dp.callback_query_handler(state=TestStates.LESSONS_MENU)
async def process_menu_button(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.set_state(TestStates.THEORY_MENU[0])

    user_info = db.get_user_data(connection, callback_query.from_user.id)
    lesson_id = callback_query.data.split("_")[2]
    theory_text = db.get_theory(connection, lesson_id)

    start_test = InlineKeyboardButton('Пройти тест', callback_data=f'start_test_{lesson_id}')
    get_task = InlineKeyboardButton('Получить практическое задание', callback_data=f'get_task_{lesson_id}')
    theory_menu_button = InlineKeyboardMarkup(row_width=1).add(start_test, get_task, kb.menu_button)
    await bot.send_message(callback_query.from_user.id , f"{theory_text[0]}", reply_markup=theory_menu_button)
#=====================THEORY MENU ============================


#=====================TEST MENU ============================
@dp.callback_query_handler(state=TestStates.THEORY_MENU)
async def pre_poll(callback_query: types.CallbackQuery):
    state = dp.current_state(user=callback_query.from_user.id)
    await state.set_state(TestStates.TEST[0])
    user_info = db.get_user_data(connection, callback_query.from_user.id)

    lesson_id = callback_query.data.split("_")[2]
    item_name = callback_query.data.split("_")[1]

    async with state.proxy() as user_data:
        user_data['lesson_id'] = lesson_id
        user_data['step_count'] = 0
        user_data['correct_answer'] = 0

    if item_name == "test":
        all_tests = db.get_test(connection, lesson_id)
        tests_true_dict = {}
        tests_answer_dict = {}
        question_dict = {}
        i = 0
        for test in all_tests:
            tests_true_dict[i] = test[2]
            tests_answer_dict[i] = test[1].split("|")
            question_dict[i] = test[0]
            i += 1
        answer_data = tests_answer_dict[0]
        random.shuffle(tests_answer_dict)
        async with state.proxy() as user_data:
            user_data['true_ans'] = answer_data.index(tests_true_dict[0])

        return await bot.send_poll(chat_id=callback_query.from_user.id, question=question_dict[0], is_anonymous=False, options=answer_data, type="quiz", correct_option_id=answer_data.index(tests_true_dict[0]), reply_markup=kb.menu_button)
    if item_name == "task":
        task_text = db.get_practice(connection, lesson_id)
        await bot.send_message(callback_query.from_user.id,
                               f'{task_text[0]}', reply_markup=kb.menu_keyb)

@dp.poll_answer_handler(lambda message: True)
async def my_poll(poll_answer: types.PollAnswer):
    state = dp.current_state(user=poll_answer.user.id)
    async with state.proxy() as user_data:
        lesson_id = user_data['lesson_id']
        correct_answer = user_data['correct_answer']
        step_count = user_data['step_count']
        true_ans = user_data['true_ans']
    await state.set_state(TestStates.TEST[0])
    all_tests = db.get_test(connection, lesson_id)
    tests_true_dict = {}
    tests_answer_dict = {}
    question_dict = {}
    i = 0
    for test in all_tests:
        tests_true_dict[i] = test[2]
        tests_answer_dict[i] = test[1].split("|")
        question_dict[i] = test[0]
        i += 1

    if poll_answer.option_ids[0] == true_ans:
        correct_answer += 1


    step_count += 1
    async with state.proxy() as user_data:
        user_data['lesson_id'] = lesson_id
        user_data['correct_answer'] = correct_answer
        user_data['step_count'] = step_count

    if step_count != i:
        answer_data = tests_answer_dict[step_count]
        random.shuffle(tests_answer_dict)

        async with state.proxy() as user_data:
            user_data['true_ans'] = answer_data.index(tests_true_dict[step_count])
        await bot.send_poll(chat_id=poll_answer.user.id, question=question_dict[step_count], is_anonymous=False, options=answer_data, type="quiz", correct_option_id=answer_data.index(tests_true_dict[step_count]), reply_markup=kb.menu_button)
    else:
        await bot.send_message(poll_answer.user.id,
                         f'Тестирование завершено.\nВерных ответов {correct_answer} из {step_count}.', reply_markup=kb.menu_keyb)


#=====================TEST MENU ============================


if __name__ == '__main__':
        executor.start_polling(dp, skip_updates=True)