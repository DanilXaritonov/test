import telebot
from telebot import types

# Создание объекта бота с помощью токена
bot = telebot.TeleBot("6724473337:AAEvVa74klk5m90DD0mATENwZhJF-fwP254")

# Хранение file_id изображений и видео
files = {
    'Mikrotik': {
        'photo_1': 'AgACAgIAAxkBAAIBhmaqZvW9IdnYG8EcnMaTcQi_y3GBAAKg6DEb2RJRSTi7Ev9ufBCtAQADAgADeQADNQQ',
        'video_reboot': 'CgACAgIAAxkBAAIB2GaqccV8MshyFcMfSH8vyPx3i0sEAAJfTQAC9DtRSQJFvjBp9T0gNQQ',
        #'4G_photos' : 'AgACAgIAAxkBAAIB3maqc5-zTxOjQYBsZAvbdc-oEJjUAAIN6TEb2RJRScEaM3LgR-E9AQADAgADeQADNQQ'
        '4G_photos': [
            'AgACAgIAAxkBAAIB3maqc5-zTxOjQYBsZAvbdc-oEJjUAAIN6TEb2RJRScEaM3LgR-E9AQADAgADeQADNQQ',
            'AgACAgIAAxkBAAIB4GaqdA8R6rSOEfMZ55LDKyCthxETAAIP6TEb2RJRSWHp1DtyZntNAQADAgADeQADNQQ',
            'AgACAgIAAxkBAAIB4maqdNEmR-mbCWcemCHnL0Ix9giMAAIY6TEb2RJRSfrXBYx38qxPAQADAgADeQADNQQ'
        ]
    },
    '4G': {
        'photo_1': 'AgACAgIAAxkBAAIBiGaqZ497oXp5FqEy0_ukQ1WS6XGsAAKo6DEb2RJRSfrCdOaXTH35AQADAgADeQADNQQ',
        'photo_2': 'AgACAgIAAxkBAAIBjGaqaHPDBuykTwgjd7tuCpTUtFpsAAK26DEb2RJRSU4v2ggN7gdpAQADAgADeQADNQQ',
        'video_reboot': 'CgACAgIAAxkBAAIB2maqclJSQJ_VHZqK5v1inW3-exMTAAJwVAAC2RJRSbv4fGjrgllTNQQ',
        'video_sim': 'BAACAgIAAxkBAAIB3GaqcwN7Jwc6EergHpkAAQ8je1JrDgACeFQAAtkSUUlGHTA1o01cVzUE'
    },
    'UniFi': {
        'photo_front': 'AgACAgIAAxkBAAIBimaqZ6AQnslC6iqi76joTlgG1FDrAAKs6DEb2RJRSRVEoa3NthNaAQADAgADeQADNQQ',
        'photo_back': 'AgACAgIAAxkBAAICWmax_4qwq19H1FX7KZSW_7kZwRpMAALX3TEbQGSQSadHo2-3tFcVAQADAgADeQADNQQ',
        'photo_PoE_white': 'AgACAgIAAxkBAAICYGayAAEb3-_dibQ8_Y6KTjDb2TtaLAAC2d0xG0BkkEk284-lOUp47AEAAwIAA3kAAzUE',
        'photo_PoE_black': 'AgACAgIAAxkBAAICYmayAAEmgxZDMroqZ3ykmPTky-uDmwAC2t0xG0BkkElAVJjuYC4diAEAAwIAA3kAAzUE',
        'video_reboot_white': 'CgACAgIAAxkBAAICZmayAAFyM99MycTafoFvm-tY_v_PNQACl04AAkBkkEkPJyDNzli96zUE',
        'video_reboot_black': 'CgACAgIAAxkBAAICZGayAAFWkVRpSGxKQqU8EwuflNfymgAClU4AAkBkkEn_oHPHH1Ju7jUE'
    },
    'Computer': {
        'photo_HDMI': 'AgACAgIAAxkBAAICUGax_05P-6CNKpmw24Np0jYvTNWxAAKh4DEba2CASQOr3l3tA3Y-AQADAgADeQADNQQ',
        'photo_power_button': 'AgACAgIAAxkBAAICdGayBG2VFFjqGhKyssFg017K7PUSAAKf4DEba2CASby07JxjEk9WAQADAgADeQADNQQ',
        'photo_ethernet': 'AgACAgIAAxkBAAICUmax_1U9mCKWnOSBi8vE0_yTTTBMAAKg4DEba2CASd4QnGEg54p9AQADAgADeQADNQQ',
        'video_ethernet': 'CgACAgIAAxkBAAICamayAAGryhU-hk2oec3pI7FpL-xlEQACnE4AAkBkkEmebvKOgrDxTzUE',
        'video_monitor_power': 'CgACAgIAAxkBAAICbGayAAHMtHejDr8OfnPte8fQp0hjsAACnU4AAkBkkEltjyj5Hw6FZTUE',
        'video_monitor_button': 'CgACAgIAAxkBAAICbmayAQi59WdU5neBhhAJmKxLxiyiAAKjTgACQGSQSY5DawbnxOuTNQQ'
    },
    'TEM': {
        'video_check_power': 'CgACAgIAAxkBAAICcGayAVNwJ_lhVID_8hQK8rjvjzXtAAKoTgACQGSQSSgom0jgLE_oNQQ',
        'video_check_cable': 'CgACAgIAAxkBAAICcmayAZKVEtMPC5RyN4BvN3Jwwq2FAAKvTgACQGSQSW8YyffbzujiNQQ',
        'photo_low_batt': 'AgACAgIAAxkBAAICSWax_vIAAW7_BviKEeX7W4zMk2P1bwAC0N0xG0BkkEmf5LWsUsghJAEAAwIAA3kAAzUE'
    }
}

# Отправка стартового меню
def send_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = ['Mikrotik', '4G', 'UniFi', 'Компьютер', 'Весы TEM']
    markup.add(*buttons)
    bot.send_message(chat_id, "Выберите устройство:", reply_markup=markup)


# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    send_main_menu(message.chat.id)


# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == 'Mikrotik':
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add('Mikrotik (фото 1)', 'Mikrotik (перезагрузка видео)', 'Mikrotik (подключение к 4G фото)', 'Назад')
        bot.send_message(message.chat.id, "Выберите действие для Mikrotik:", reply_markup=markup)
    
    elif message.text == '4G':
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add('4G (фото 1)', '4G (фото 2)', '4G (перезагрузка видео)', '4G (замена SIM видео)', 'Назад')
        bot.send_message(message.chat.id, "Выберите действие для 4G:", reply_markup=markup)

    elif message.text == 'UniFi':
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add('UniFi (фронт фото)', 'UniFi (зад фото)', 'UniFi (PoE белый фото)', 'UniFi (PoE черный фото)', 'UniFi (перезагрузка белый видео)', 'UniFi (перезагрузка черный видео)', 'Назад')
        bot.send_message(message.chat.id, "Выберите действие для UniFi:", reply_markup=markup)

    elif message.text == 'Компьютер':
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add('Компьютер (HDMI фото)', 'Компьютер (кнопка питания фото)', 'Компьютер (Ethernet фото)', 'Компьютер (Ethernet видео)', 'Компьютер (питание монитора видео)', 'Компьютер (кнопка монитора видео)', 'Назад')
        bot.send_message(message.chat.id, "Выберите действие для Компьютера:", reply_markup=markup)

    elif message.text == 'Весы TEM':
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add('Весы TEM (проверка питания видео)', 'Весы TEM (проверка кабеля видео)', 'Весы TEM (низкий заряд фото)', 'Назад')
        bot.send_message(message.chat.id, "Выберите действие для Весов TEM:", reply_markup=markup)
    
    # Сначала проверяем кнопку "Back" для всех меню
    elif 'Назад' in message.text:
        send_main_menu(message.chat.id)
    
    # Дальше идет фильтрация по "Mikrotik"
    elif message.text.startswith('Mikrotik'):
        if 'фото 1' in message.text:
            file_id = files['Mikrotik']['photo_1']
            bot.send_photo(message.chat.id, file_id)
        elif 'перезагрузка видео' in message.text:
            file_id = files['Mikrotik']['video_reboot']
            bot.send_video(message.chat.id, file_id)
        elif 'подключение к 4G фото' in message.text:
            for photo_id in files['Mikrotik']['4G_photos']:
                bot.send_photo(message.chat.id, photo_id)
    # elif message.text.startswith('Mikrotik' or 'Back'):
    #     if 'фото' in message.text:
    #         file_id = files['Mikrotik']['photo_1']
    #         bot.send_photo(message.chat.id, file_id)
    #     elif 'перезагрузка видео' in message.text:
    #         file_id = files['Mikrotik']['video_reboot']
    #         bot.send_video(message.chat.id, file_id)
    #     elif 'подключение к 4G фото' in message.text:
    #         for photo_id in files['Mikrotik']['4G_photos']:
    #             bot.send_photo(message.chat.id, photo_id)
    #     elif 'Back' in message.text:
    #             send_main_menu(message.chat.id)
            
    #elif 'Назад' in message.text:
            #send_main_menu(message.chat.id)
    elif message.text.startswith('4G'):
        if 'фото 1' in message.text:
            file_id = files['4G']['photo_1']
            bot.send_photo(message.chat.id, file_id)
        elif 'фото 2' in message.text:
            file_id = files['4G']['photo_2']
            bot.send_photo(message.chat.id, file_id)
        elif 'перезагрузка видео' in message.text:
            file_id = files['4G']['video_reboot']
            bot.send_video(message.chat.id, file_id)
        elif 'замена SIM видео' in message.text:
            file_id = files['4G']['video_sim']
            bot.send_video(message.chat.id, file_id)
        

    elif message.text.startswith('UniFi'):
        if 'фронт фото' in message.text:
            file_id = files['UniFi']['photo_front']
            bot.send_photo(message.chat.id, file_id)
        elif 'зад фото' in message.text:
            file_id = files['UniFi']['photo_back']
            bot.send_photo(message.chat.id, file_id)
        elif 'PoE белый фото' in message.text:
            file_id = files['UniFi']['photo_PoE_white']
            bot.send_photo(message.chat.id, file_id)
        elif 'PoE черный фото' in message.text:
            file_id = files['UniFi']['photo_PoE_black']
            bot.send_photo(message.chat.id, file_id)
        elif 'перезагрузка белый видео' in message.text:
            file_id = files['UniFi']['video_reboot_white']
            bot.send_video(message.chat.id, file_id)
        elif 'перезагрузка черный видео' in message.text:
            file_id = files['UniFi']['video_reboot_black']
            bot.send_video(message.chat.id, file_id)
        elif 'Назад' in message.text:
            send_main_menu(message.chat.id)

    elif message.text.startswith('Компьютер'):
        if 'HDMI фото' in message.text:
            file_id = files['Computer']['photo_HDMI']
            bot.send_photo(message.chat.id, file_id)
        elif 'кнопка питания фото' in message.text:
            file_id = files['Computer']['photo_power_button']
            bot.send_photo(message.chat.id, file_id)
        elif 'Ethernet фото' in message.text:
            file_id = files['Computer']['photo_ethernet']
            bot.send_photo(message.chat.id, file_id)
        elif 'Ethernet видео' in message.text:
            file_id = files['Computer']['video_ethernet']
            bot.send_video(message.chat.id, file_id)
        elif 'питание монитора видео' in message.text:
            file_id = files['Computer']['video_monitor_power']
            bot.send_video(message.chat.id, file_id)
        elif 'кнопка монитора видео' in message.text:
            file_id = files['Computer']['video_monitor_button']
            bot.send_video(message.chat.id, file_id)
        elif 'Назад' in message.text:
            send_main_menu(message.chat.id)

    elif message.text.startswith('Весы TEM'):
        if 'проверка питания видео' in message.text:
            file_id = files['TEM']['video_check_power']
            bot.send_video(message.chat.id, file_id)
        elif 'проверка кабеля видео' in message.text:
            file_id = files['TEM']['video_check_cable']
            bot.send_video(message.chat.id, file_id)
        elif 'низкий заряд фото' in message.text:
            file_id = files['TEM']['photo_low_batt']
            bot.send_photo(message.chat.id, file_id)
        elif 'Назад' in message.text:
            send_main_menu(message.chat.id)

# Запуск бота
#bot.polling(timeout=60, long_polling_timeout=30)
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Ошибка при запуске polling: {e}")
        time.sleep(5)  # Подождать перед перезапуском
