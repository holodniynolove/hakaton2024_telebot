import telebot
from telebot import types
import sqlite3

token = '7228816688:AAHBdob34AkZXldvcTqYUAjkZPL11V5CydE'  # Замените на ваш токен
bot = telebot.TeleBot(token)

# Подключение к базе данных
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    phone_number TEXT NOT NULL,
    user_id INTEGER,
    apartment_number TEXT,
    entrance_number TEXT
)
''')
conn.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Нажмите кнопку ниже, чтобы поделиться своим номером телефона.')
    send_contact_button(message.chat.id)


def send_contact_button(chat_id):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    button = types.KeyboardButton("Поделиться номером", request_contact=True)
    keyboard.add(button)
    bot.send_message(chat_id, "Пожалуйста, поделитесь своим номером телефона:", reply_markup=keyboard)


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    phone_number = message.contact.phone_number
    chat_id = message.chat.id

    cursor.execute('''
        INSERT OR REPLACE INTO users (chat_id, phone_number) VALUES (?, ?)
        ''', (chat_id, phone_number))
    conn.commit()

    bot.send_message(chat_id, f'Вы успешно авторизованы с номером {phone_number}!')


@bot.message_handler(commands=['get_phone'])
def get_phone(message):
    chat_id = message.chat.id
    cursor.execute('SELECT phone_number FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()

    if result:
        bot.send_message(chat_id, f'Ваш номер телефона: {result[0]}')
    else:
        bot.send_message(chat_id, 'Вы не авторизованы. Пожалуйста, поделитесь своим номером телефона.')

# Запуск бота
bot.polling()
