import sqlite3


def create_database():
    # Подключение к базе данных
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT)''')

    # Создание таблицы заведений
    cursor.execute('''CREATE TABLE IF NOT EXISTS establishments (
                    id_establishment INTEGER PRIMARY KEY,
                    name TEXT,
                    id_type INTEGER,
                    id_district INTEGER,
                    address TEXT,
                    metro_station TEXT,
                    description TEXT,
                    feature TEXT,
                    FOREIGN KEY (id_type) REFERENCES establishment_types(id_type),
                    FOREIGN KEY (id_district) REFERENCES districts(id_district))''')

    # Создание таблицы типов заведений
    cursor.execute('''CREATE TABLE IF NOT EXISTS establishment_types (
                    id_type INTEGER PRIMARY KEY,
                    name TEXT)''')

    # Создание таблицы районов
    cursor.execute('''CREATE TABLE IF NOT EXISTS districts (
                    id_district INTEGER PRIMARY KEY,
                    name TEXT)''')

    # Создание таблицы фотографий заведений
    cursor.execute('''CREATE TABLE IF NOT EXISTS establishment_photos (
                    id_photo INTEGER PRIMARY KEY,
                    id_establishment INTEGER,
                    path_to_photo1 TEXT,
                    path_to_photo2 TEXT,
                    path_to_photo3 TEXT,
                    path_to_photo4 TEXT,
                    FOREIGN KEY (id_establishment) REFERENCES establishments(id_establishment))''')

    # districts = [
    #     "Арбат",
    #     "Басманный",
    #     "Замоскворечье",
    #     "Красносельский",
    #     "Мещанский",
    #     "Пресненский",
    #     "Таганский",
    #     "Тверской",
    #     "Хамовники",
    #     "Якиманка"
    # ]
    # for district in districts:
    #     cursor.execute("INSERT INTO districts (name) VALUES (?)", (district,))
    #
    # # Заполнение таблицы типов заведений
    # establishment_types = ["Ресторан", "Бар"]
    # for est_type in establishment_types:
    #     cursor.execute("INSERT INTO establishment_types (name) VALUES (?)", (est_type,))

    conn.commit()

    # Закрыть соединение
    conn.close()


def add_new_user(user_id):
    # Подключение к базе данных
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    # Добавление нового пользователя в базу данных
    cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

    # Закрыть соединение
    conn.close()


def check_existing_user(user_id):
    # Подключение к базе данных
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    # Проверка наличия пользователя в базе данных
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()

    # Закрыть соединение
    conn.close()

    return existing_user


def get_district_id(district_name):
    # Подключение к базе данных
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id_district FROM districts WHERE name=?", (district_name,))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return None


def get_type_id(establishment_type):
    # Подключение к базе данных
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    cursor.execute("SELECT id_type FROM establishment_types WHERE name=?", (establishment_type,))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return None

# Функция для сохранения заведения в базе данных
async def save_establishment_to_database(name, features, address, metro, description, district_id, type_id):
    # Подключение к базе данных
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    # Добавление нового заведения
    cursor.execute("INSERT INTO establishments (name, feature, address, metro_station, description, id_district, id_type)"
                   "VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (name, features, address, metro, description, district_id, type_id))
    conn.commit()

    # Закрыть соединение
    conn.close()
