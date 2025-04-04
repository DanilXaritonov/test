import telebot
from telebot import types
import logging
import time
import os
import psycopg2
import mysql.connector

# Логирование
logging.basicConfig(filename='bot_errors.log', level=logging.DEBUG)

# Подключение к MySQL (для авторизации)
def connect_to_mysql():
    try:
        db = mysql.connector.connect(
            host="192.168.98.129",
            user="kharitonov",
            password="8@*TU2Rxh*VTotCl",
            database="marketinfo"
        )
        logging.debug("[INFO] Подключение к MySQL успешно")
        return db
    except Exception as e:
        logging.error(f"Ошибка подключения к MySQL: {e}")
        return None

# Подключение к PostgreSQL (для файлов)
def connect_to_postgres():
    try:
        conn = psycopg2.connect(
            dbname="telegram_bot_db",
            user="postgres",
            password="67611522jJ",
            host="192.168.98.81"
        )
        logging.debug("[INFO] Подключение к PostgreSQL успешно")
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к PostgreSQL: {e}")
        return None

# Создание бота
bot = telebot.TeleBot("7499561637:AAFCmcS0qiiHxwFLpVvIyTfDz-ijb0g2BEY")

# Проверка авторизации пользователя
def check_authorization(user_id):
    db = connect_to_mysql()
    if not db:
        return False
    cursor = db.cursor()
    cursor.execute("SELECT * FROM marketinfo.users WHERE telegram_id = %s", (user_id,))
    user = cursor.fetchone()
    db.close()
    return user is not None

# Получение пути файла из базы по описанию
def get_file_for_button(description):
    try:
        conn = connect_to_postgres()
        if not conn:
            return None
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM public.media_files WHERE description = %s;", (description,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        logging.debug(f"[INFO] Найден файл: {result} для {description}")
        return result[0] if result else None
    except Exception as e:
        logging.error(f"Ошибка при получении файла из PostgreSQL: {e}")
        return None

# Универсальная функция отправки файлов
def send_file(chat_id, file_path):
    if not file_path:
        logging.warning("[WARNING] Пустой путь файла")
        bot.send_message(chat_id, "Ошибка загрузки файла.")
        return
    
    file_extension = os.path.splitext(file_path)[1].lower()
    logging.debug(f"[INFO] Отправка файла {file_path} с расширением {file_extension}")
    
    try:
        with open(file_path, 'rb') as file:
            if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
                bot.send_photo(chat_id, file)
            elif file_extension in ['.mp4', '.mov', '.avi']:
                bot.send_video(chat_id, file)
            elif file_extension in ['.pdf', '.docx', '.xlsx', '.txt']:
                bot.send_document(chat_id, file)
            else:
                bot.send_document(chat_id, file)
    except FileNotFoundError:
        logging.error(f"[ERROR] Файл не найден: {file_path}")
        bot.send_message(chat_id, "Файл не найден.")
    except Exception as e:
        logging.error(f"Ошибка при отправке файла: {e}")
        bot.send_message(chat_id, "Ошибка при отправке файла.")

# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    
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

# Обработка кнопок
def handle_buttons(message):
    description_mapping = {
        'Mikrotik (фото 1)': 'RFID_PHOTO_USB',
        'Mikrotik (перезагрузка видео)': 'Reboot_mikrotik',
        'Mikrotik (подключение к 4G фото)': 'Mikrotik (подключение к 4G фото)',
        '4G (инструкция 1)': '4G (инструкция 1)',
        '4G (настройка 2)': '4G (настройка 2)',
        'UniFi (сеть 1)': 'UniFi (сеть 1)',
        'Весы TEM (калибровка)': 'Весы TEM (калибровка)',
        'Тестовый файл': 'file1'
    }

    description = description_mapping.get(message.text)
    
    if description:
        logging.debug(f"[INFO] Нажата кнопка: {message.text}, ищем файл с описанием {description}")
        file_path = get_file_for_button(description)
        send_file(message.chat.id, file_path)
    elif message.text in ['Mikrotik', '4G', 'UniFi', 'Весы TEM']:
        send_submenu(message.chat.id, message.text)
    elif message.text == 'Назад':
        send_main_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Я не понимаю эту команду.")

# Отправка подменю
def send_submenu(chat_id, category):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    
    if category == 'Mikrotik':
        markup.add('Mikrotik (фото 1)', 'Mikrotik (перезагрузка видео)', 'Mikrotik (подключение к 4G фото)', 'Назад')
    elif category == '4G':
        markup.add('4G (инструкция 1)', '4G (настройка 2)', 'Назад')
    elif category == 'UniFi':
        markup.add('UniFi (сеть 1)', 'Назад')
    elif category == 'Весы TEM':
        markup.add('Весы TEM (калибровка)', 'Назад')

    bot.send_message(chat_id, f"Выберите действие для {category}:", reply_markup=markup)

# Запуск бота
while True:
    try:
        logging.debug("[INFO] Запуск бота...")
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске polling: {e}")
        time.sleep(5)
