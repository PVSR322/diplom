import mysql.connector
from mysql.connector import Error

#Коннект в бд
def create_connection(host_name, user_name, user_password, user_port, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            database=db_name,
            user=user_name,
            passwd=user_password,
            port=user_port
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

#Исполнение запроса
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Успешный запрос")
    except Error as e:
        print(f"The error '{e}' occurred")

#Создание юзера на /start
def create_user(connection, user_id):
    cursor = connection.cursor()
    try:
        cursor.execute(f"INSERT INTO users (telegram_id) VALUES ({user_id})")
        connection.commit()
        print(f"Новый пользователь прописал start! ID: {user_id}")
        return 1
    except Error as e:
        print(f"The error '{e}' occurred")
        return 0

# Получение инфы о юзере
def get_user_data(connection, user_id):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(f"SELECT `fio`,`record_book`,`status` FROM `users` WHERE `telegram_id` = {user_id}")
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

# Регистрация пользователя
def register_user(connection, user_id, fio_user, record_book_number):
    cursor = connection.cursor()
    try:
        cursor.execute(f"UPDATE users"
                       f" SET fio = '{fio_user}', record_book = '{record_book_number}', status = {1}"
                       f" WHERE telegram_id = {user_id}")
        connection.commit()
        print("Успешная регистрация")
        return 1
    except Error as e:
        print(f"The error '{e}' occurred")
        return 0

# Получение всех курсов
def get_course_info(connection):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(f"SELECT * FROM `course`")
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

# Получение всех уроков
def get_lessons_info(connection):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(f"SELECT  id, course_id, name FROM `lessons`")
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

# Получение теории по айди урока
def get_theory(connection, lesson_id):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(f"SELECT theory FROM `lessons` WHERE id = {lesson_id}")
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

# Получение тестов по айди урока
def get_test(connection, lesson_id):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(f"SELECT question_text, answers, true_answer FROM `tests` WHERE lesson_id = {lesson_id}")
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

# Получение практики по айди урока
def get_practice(connection, lesson_id):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(f"SELECT task FROM `lessons` WHERE id = {lesson_id}")
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")