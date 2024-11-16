import telebot
from telebot import types
import sqlite3
import requests
import json


# исходник бота
token = '7228816688:AAHBdob34AkZXldvcTqYUAjkZPL11V5CydE'  # Замените на ваш токен
bot = telebot.TeleBot(token)

# Подключение к базе данных
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    phone_number TEXT NOT NULL,
    user_id INTEGER
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

#  реализация работы с бекендом
@bot.message_handler(commands=['check_tenant'])
def check_tenant(message):
    chat_id = message.chat.id
    cursor.execute('SELECT phone_number FROM users WHERE chat_id = ?', (chat_id,))
    result = cursor.fetchone()
    bot.send_message(chat_id, f'Выбран номер телефона{result}')
    if result:
        phone_number = result[0]
        print(type(phone_number))
        phone_number = phone_number[1:]
        print(phone_number)
        # Формирование запроса к API
        url = "https://domo-dev.profintel.ru/tg-bot/check-tenant"
        payload = json.dumps({"phone": phone_number})
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': 'SecretToken'  # Замените на ваш реальный токен
        }
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            bot.send_message(chat_id, f"Успех: {response.json()}")
            response_data = response.json()
            user_id = response_data.get("id")
            cursor.execute('''
                            UPDATE users SET user_id = ? WHERE chat_id = ?
                        ''', (user_id, chat_id))
            conn.commit()
        else:
            bot.send_message(chat_id, f"Ошибка: {response.status_code} - {response.text}")
# Запуск бота
bot.polling()
