from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from config import HOST_DB, USER_DB, PASS_DB, PORT_DB, NAME_DB

connection = db.create_connection(HOST_DB, USER_DB, PASS_DB, PORT_DB, NAME_DB)

reg_button1 = InlineKeyboardButton('✅', callback_data='confirm_reg_true')
reg_button2 = InlineKeyboardButton('❌', callback_data='confirm_reg_false')
confirm_reg_keyb = InlineKeyboardMarkup().add(reg_button1, reg_button2)

menu_button = InlineKeyboardButton('Меню', callback_data='menu')
menu_keyb = InlineKeyboardMarkup().add(menu_button)

course_menu = InlineKeyboardButton('Начать обучение', callback_data='course_menu')
sign_record = InlineKeyboardButton('Мои успехи', callback_data='sign_record')
main_menu_keyb = InlineKeyboardMarkup(row_width=1).add(course_menu, sign_record)










