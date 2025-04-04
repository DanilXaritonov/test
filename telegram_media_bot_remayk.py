import telebot
from telebot import types
import logging
import time
import mysql.connector
import psycopg2

# Логирование
logging.basicConfig(filename='bot_errors.log', level=logging.DEBUG)

def connect_to_db():
    try:
        db = mysql.connector.connect(
            host="192.168.98.129",
            user="kharitonov",
            password="8@*TU2Rxh*VTotCl",
            database="marketinfo"
        )
        print("[INFO] Подключение к MySQL успешно")
        return db
    except Exception as e:
        logging.error(f"Ошибка подключения к MySQL: {e}")
        print(f"[ERROR] Ошибка подключения к MySQL: {e}")
        return None

def connect_to_postgres():
    try:
        conn = psycopg2.connect(
            dbname="telegram_bot_db",
            user="postgres",
            password="67611522jJ",
            host="localhost"
        )
        print("[INFO] Подключение к PostgreSQL успешно")
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к PostgreSQL: {e}")
        print(f"[ERROR] Ошибка подключения к PostgreSQL: {e}")
        return None

# Создание объекта бота с помощью токена
bot = telebot.TeleBot("7499561637:AAFCmcS0qiiHxwFLpVvIyTfDz-ijb0g2BEY")

def check_authorization(user_id):
    db = connect_to_db()
    if not db:
        return False
    cursor = db.cursor()
    cursor.execute("SELECT * FROM marketinfo.users WHERE telegram_id = %s", (user_id,))
    user = cursor.fetchone()
    print(f"[DEBUG] Пользователь {user_id} авторизован: {user is not None}")
    return user is not None

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    print(f"[DEBUG] Получено сообщение: {message.text} от {user_id}")
    
    if check_authorization(user_id):
        if message.text == '/start':
            bot.send_message(message.chat.id, "Добро пожаловать!")
            send_main_menu(message.chat.id)
        else:
            handle_buttons(message)
    else:
        bot.send_message(message.chat.id, "Извините, у вас нет доступа.")

# Отправка стартового меню
def send_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = ['Mikrotik', '4G', 'UniFi', 'Компьютер', 'Весы TEM', 'Тестовый файл']
    markup.add(*buttons)
    bot.send_message(chat_id, "Выберите устройство:", reply_markup=markup)

def get_test_file():
    try:
        conn = connect_to_postgres()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM public.media_files WHERE file_name = 'file1';")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        print(f"[DEBUG] Запрос к базе PostgreSQL выполнен, результат: {result}")
        if result:
            return result[0]
    except Exception as e:
        logging.error(f"Ошибка при получении файла из PostgreSQL: {e}")
        print(f"[ERROR] Ошибка при получении файла из PostgreSQL: {e}")
        return None

def handle_buttons(message):
    print(f"[DEBUG] Обработка нажатия кнопки: {message.text}")
    try:
        if message.text == 'Тестовый файл':
            file_path = get_test_file()
            if file_path:
                print(f"[INFO] Отправка файла: {file_path}")
                with open(file_path, 'rb') as photo:
                    bot.send_photo(message.chat.id, photo)
            else:
                print("[WARNING] Файл не найден в базе")
                bot.send_message(message.chat.id, "Ошибка загрузки файла.")
        elif message.text == 'Mikrotik':
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            markup.add('Mikrotik (фото 1)', 'Mikrotik (перезагрузка видео)', 'Mikrotik (подключение к 4G фото)', 'Назад')
            bot.send_message(message.chat.id, "Выберите действие для Mikrotik:", reply_markup=markup)
        elif 'Назад' in message.text:
            send_main_menu(message.chat.id)
        else:
            print(f"[WARNING] Неизвестная команда: {message.text}")
            bot.send_message(message.chat.id, "Я не понимаю эту команду.")
    except Exception as e:
        logging.error(f"Ошибка в обработчике сообщений: {e}")
        print(f"[ERROR] Ошибка в обработчике сообщений: {e}")
        raise e

while True:
    try:
        print("[INFO] Запуск бота...")
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске polling: {e}")
        print(f"[ERROR] Ошибка при запуске polling: {e}")
        time.sleep(5)
