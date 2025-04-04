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
            password="buyursin123",
            host="192.168.98.81"
        )
        logging.debug("[INFO] Подключение к PostgreSQL успешно")
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к PostgreSQL: {e}")
        return None

# Создание бота
bot = telebot.TeleBot("7499561637:AAFCmcS0qiiHxwFLpVvIyTfDz-ijb0g2BEY")

# Кэш для кнопок
buttons_cache = {}

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

# Получение кнопок из базы
def get_buttons_from_db(category):
    global buttons_cache
    
    if category in buttons_cache:
        logging.info(f"[CACHE] Используем кешированные кнопки для {category}")
        return buttons_cache[category]

    try:
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM media_files WHERE description ILIKE %s;", (f"%{category}%",))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        buttons = []
        for desc in results:
            description = desc[0]
            # Добавляем отладочную информацию
            bytes_length = len(description.encode('utf-8'))
            logging.info(f"[DEBUG] Создание кнопки: текст='{description}', длина в байтах={bytes_length}")
            
            if bytes_length > 40:
                logging.error(f"[ERROR] Описание слишком длинное: '{description}' ({bytes_length} байт)")
                continue
                
            buttons.append(types.InlineKeyboardButton(description, callback_data=description))
            
        buttons_cache[category] = buttons
        logging.info(f"[DB] Загружены кнопки из базы для {category}")
        return buttons
    except Exception as e:
        logging.error(f"Ошибка при получении кнопок из PostgreSQL: {e}")
        return []

# Получение пути файла из базы
def get_file_for_button(description):
    try:
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM media_files WHERE description = %s;", (description,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logging.error(f"Ошибка при получении файла: {e}")
        return None

# Очистка кеша
def clear_cache():
    global buttons_cache
    buttons_cache = {}
    logging.info("[CACHE] Кэш кнопок очищен")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if check_authorization(user_id):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [
            'Mikrotik', '4G', 'UniFi', 'PC', 'Весы TEM',
            'RFID', 'PinPad', 'Sewoo', 'Zebra', 'Apexa',
            'Instructions'
        ]
        keyboard.add(*[types.KeyboardButton(btn) for btn in buttons])
        bot.send_message(user_id, "Выберите категорию:", reply_markup=keyboard)
    else:
        bot.send_message(user_id, "⛔ Доступ запрещен. Вы не авторизованы.")

# Обработчик выбора категории
@bot.message_handler(func=lambda message: message.text in [
    'Mikrotik', '4G', 'UniFi', 'PC', 'Весы TEM',
    'RFID', 'PinPad', 'Sewoo', 'Zebra', 'Apexa',
    'Instructions'
])
def category_selected(message):
    category = message.text
    # Специальная обработка для категории "Весы TEM"
    search_term = "TEM" if category == "Весы TEM" else category
    
    buttons = get_buttons_from_db(search_term)
    
    if not buttons:
        bot.send_message(message.chat.id, "❌ Нет доступных файлов в этой категории.")
        return
    
    keyboard = types.InlineKeyboardMarkup()
    for button in buttons:
        keyboard.add(button)
    
    bot.send_message(message.chat.id, f"Выберите файл из категории {category}:", reply_markup=keyboard)

# Обработчик callback-кнопок
@bot.callback_query_handler(func=lambda call: True)
def send_file(call):
    # Отвечаем на callback с показом "часиков"
    bot.answer_callback_query(call.id, show_alert=False)
    
    file_path = get_file_for_button(call.data)
    if file_path:
        logging.debug(f"[INFO] Попытка открыть файл по пути: {file_path}")
        try:
            with open(file_path, 'rb') as file:
                # Определяем тип файла по расширению
                file_extension = os.path.splitext(file_path)[1].lower()
                
                # Изображения
                if file_extension in ['.jpg', '.jpeg', '.png']:
                    bot.send_photo(call.message.chat.id, file)
                    logging.debug(f"[INFO] Отправлено как фото: {file_path}")
                
                # Видео
                elif file_extension in ['.mp4', '.mov', '.avi']:
                    bot.send_video(call.message.chat.id, file)
                    logging.debug(f"[INFO] Отправлено как видео: {file_path}")
                
                # GIF анимации
                elif file_extension == '.gif':
                    bot.send_animation(call.message.chat.id, file)
                    logging.debug(f"[INFO] Отправлено как GIF: {file_path}")
                
                # Документы (PDF, текстовые файлы и другие)
                else:
                    bot.send_document(call.message.chat.id, file)
                    logging.debug(f"[INFO] Отправлено как документ: {file_path}")
                
                # Отправляем пустое уведомление после успешной отправки файла
                bot.answer_callback_query(call.id, text="", show_alert=False)
                
        except FileNotFoundError:
            logging.error(f"[ERROR] Файл не найден по пути: {file_path}")
            bot.send_message(call.message.chat.id, "❌ Файл не найден.")
            # Отправляем уведомление об ошибке
            bot.answer_callback_query(call.id, text="❌ Файл не найден", show_alert=True)
        except Exception as e:
            logging.error(f"[ERROR] Ошибка при отправке файла {file_path}: {e}")
            bot.send_message(call.message.chat.id, "❌ Ошибка при отправке файла.")
            # Отправляем уведомление об ошибке
            bot.answer_callback_query(call.id, text="❌ Ошибка при отправке файла", show_alert=True)
    else:
        logging.error(f"[ERROR] Путь к файлу не найден для описания: {call.data}")
        bot.send_message(call.message.chat.id, "❌ Файл не найден.")
        # Отправляем уведомление об ошибке
        bot.answer_callback_query(call.id, text="❌ Файл не найден", show_alert=True)

# Добавляем обработчик для очистки кеша
@bot.message_handler(commands=['clear_cache'])
def clear_cache_command(message):
    if message.from_user.id == 123456789:  # Замените на ваш Telegram ID
        clear_cache()
        bot.send_message(message.chat.id, "✅ Кэш успешно очищен")
    else:
        bot.send_message(message.chat.id, "⛔ У вас нет прав для выполнения этой команды")

# Добавляем периодическую проверку новых файлов
def check_new_files():
    while True:
        try:
            conn = connect_to_postgres()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM media_files")
                current_count = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                
                # Если количество файлов изменилось, очищаем кэш
                if hasattr(check_new_files, 'last_count') and check_new_files.last_count != current_count:
                    clear_cache()
                    logging.info("[CACHE] Кэш очищен из-за изменения количества файлов")
                check_new_files.last_count = current_count
        except Exception as e:
            logging.error(f"Ошибка при проверке новых файлов: {e}")
        
        time.sleep(60)  # Проверяем каждую минуту

# Запускаем проверку новых файлов в отдельном потоке
import threading
cache_checker = threading.Thread(target=check_new_files, daemon=True)
cache_checker.start()

# Запуск бота с обработкой ошибок
while True:
    try:
        logging.debug("[INFO] Запуск бота...")
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске polling: {e}")
        time.sleep(5)
