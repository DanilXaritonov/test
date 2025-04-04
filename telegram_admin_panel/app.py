from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os
import requests
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Устанавливаем время жизни сессии (30 минут)
app.permanent_session_lifetime = timedelta(minutes=30)

# Функция для проверки активности сессии
def check_session():
    if 'user' not in session:
        return False
    if 'last_activity' not in session:
        session['last_activity'] = datetime.now().isoformat()
        return True
    
    last_activity = datetime.fromisoformat(session['last_activity'])
    if datetime.now() - last_activity > app.permanent_session_lifetime:
        session.clear()
        return False
    
    session['last_activity'] = datetime.now().isoformat()
    return True

# Декоратор для проверки авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_session():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Подключение к PostgreSQL
def connect_to_postgres():
    return psycopg2.connect(
        dbname="telegram_bot_db",
        user="postgres",
        password="buyursin123",
        host="192.168.98.81",
        client_encoding='utf8'
    )

# Главная страница (редирект на логин)
@app.route('/')
def index():
    return redirect(url_for('login'))

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username'].encode('utf-8').decode('utf-8')
            password = request.form['password'].encode('utf-8').decode('utf-8')
            print(f"Попытка входа: username={username}")  # Отладочная информация
            
            conn = connect_to_postgres()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session.permanent = True
                session['user'] = username
                session['last_activity'] = datetime.now().isoformat()
                return redirect(url_for('admin_panel'))
            else:
                print("Неверные учетные данные")  # Отладочная информация
                return render_template('login.html', error='Неверное имя пользователя или пароль')
        except Exception as e:
            print(f"Ошибка при входе: {str(e)}")  # Отладочная информация
            return render_template('login.html', error='Произошла ошибка при попытке входа')
    
    return render_template('login.html')

# Страница админ-панели
@app.route('/admin')
@login_required
def admin_panel():
    # Получаем текущего пользователя
    current_user = session.get('user')
    is_admin = current_user == 'admin'  # Проверяем, является ли пользователь администратором
    
    # Получаем список категорий
    categories = [
        'Mikrotik', '4G', 'UniFi', 'PC', 'TEM',
        'RFID', 'PinPad', 'Sewoo', 'Zebra', 'Apexa',
        'Instructions'
    ]
    
    return render_template('admin.html', categories=categories, is_admin=is_admin)

# Страница управления пользователями
@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    # Проверяем, является ли пользователь администратором
    if session.get('user') != 'admin':
        return redirect(url_for('admin_panel'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = connect_to_postgres()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            conn.commit()
        except Exception as e:
            print(f"Ошибка при добавлении пользователя: {str(e)}")
            return f"Ошибка при добавлении пользователя: {str(e)}", 500
        finally:
            conn.close()
        
        return redirect(url_for('manage_users'))
    
    conn = connect_to_postgres()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return render_template('users.html', users=users)

# Страница загрузки файлов
@app.route('/admin/upload/<category>', methods=['GET', 'POST'])
@login_required
def upload_file(category):
    if request.method == 'POST':
        file = request.files['file']
        file_name = request.form['file_name'].encode('utf-8').decode('utf-8')
        description = request.form['description'].encode('utf-8').decode('utf-8')

        # Проверка длины названия и описания в байтах
        file_name_bytes = len(file_name.encode('utf-8'))
        description_bytes = len(description.encode('utf-8'))
        
        print(f"[DEBUG] Длина названия в байтах: {file_name_bytes}")
        print(f"[DEBUG] Длина описания в байтах: {description_bytes}")
        
        if file_name_bytes > 40 or description_bytes > 40:
            error_msg = f"Название и описание файла не должны превышать 40 байт. "
            error_msg += f"Текущая длина названия: {file_name_bytes} байт, "
            error_msg += f"описания: {description_bytes} байт"
            return render_template('upload.html', 
                                 category=category,
                                 error=error_msg)

        if file:
            _, file_extension = os.path.splitext(file.filename)
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', category)
            os.makedirs(save_dir, exist_ok=True)
            
            save_path = os.path.join(save_dir, f"{file_name}{file_extension}")
            file.save(save_path)

            absolute_path = os.path.abspath(save_path)

            conn = connect_to_postgres()
            cursor = conn.cursor()
            
            try:
                cursor.execute(
                    "INSERT INTO media_files (file_name, file_path, description) VALUES (%s, %s, %s)",
                    (file_name, absolute_path, description.capitalize())
                )
                conn.commit()
            except Exception as e:
                print(f"Ошибка при сохранении в базу данных: {str(e)}")
                return f"Ошибка при сохранении в базу данных: {str(e)}", 500
            finally:
                conn.close()

            try:
                requests.post("http://127.0.0.1:5000/clear_cache")
            except Exception as e:
                print(f"Ошибка при очистке кэша: {str(e)}")

            return redirect(url_for('admin_panel'))

    return render_template('upload.html', category=category)

# Выход
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists('media'):
        os.makedirs('media')
    app.run(host='0.0.0.0', port=8080, debug=True)
