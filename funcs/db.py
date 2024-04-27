import os
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
                    path_to_photo TEXT,
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

    establishment_id = cursor.lastrowid

    # Закрыть соединение
    conn.close()

    # Возвращаем establishment_id
    return establishment_id


async def check_existing_establishment(name, address, metro, description, type_id, district_id):
    # Подключение к базе данных
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    # Поиск заведения с аналогичными данными
    cursor.execute("SELECT id_establishment FROM establishments WHERE name=? AND address=? AND metro_station=? AND description=? AND id_type=? AND id_district=?",
                   (name, address, metro, description, type_id, district_id))
    result = cursor.fetchone()

    # Закрыть соединение
    conn.close()

    if result:
        # Если заведение найдено, возвращаем его ID
        return result[0]
    else:
        # Если заведение не найдено, возвращаем None
        return None


def save_photo_path_to_database(establishment_id, photo_path):
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO establishment_photos (id_establishment, path_to_photo) VALUES (?, ?)",
                   (establishment_id, photo_path))

    conn.commit()
    conn.close()


async def get_establishments(district_name, establishment_type):
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    # Получаем ID района
    district_id = get_district_id(district_name)

    # Получаем ID типа заведения
    establishment_type_id = get_type_id(establishment_type)

    # Запрос к базе данных для получения заведений по району и типу
    cursor.execute("SELECT * FROM establishments WHERE id_district=? AND id_type=?", (district_id, establishment_type_id))
    establishments = cursor.fetchall()

    conn.close()

    return establishments


def get_photo_paths_for_establishment(establishment_id):
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    # Выбираем пути к фотографиям для указанного establishment_id
    cursor.execute("SELECT path_to_photo FROM establishment_photos WHERE id_establishment = ?", (establishment_id,))
    photo_paths = cursor.fetchall()

    conn.close()

    # Возвращаем список путей к фотографиям
    return [path[0] for path in photo_paths]


async def get_establishments_any_type(district_name):
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    good_district = district_name.split("admin_")[1]

    # Получаем ID района
    district_id = get_district_id(good_district)

    # Запрос к базе данных для получения заведений по району и типу
    cursor.execute("SELECT * FROM establishments WHERE id_district=?", (district_id,))

    establishments = cursor.fetchall()

    conn.close()

    return establishments


def delete_establishment(id_establishment):
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    # Получаем пути к фотографиям заведения
    cursor.execute("SELECT path_to_photo FROM establishment_photos WHERE id_establishment=?", (id_establishment,))
    photo_paths = cursor.fetchall()

    # Удаляем фотографии с диска
    for photo_path in photo_paths:
        if os.path.exists(photo_path[0]):
            os.remove(photo_path[0])

    # Удаляем заведение из базы данных
    cursor.execute("DELETE FROM establishments WHERE id_establishment=?", (id_establishment,))

    # Удаляем связанные с заведением фотографии из базы данных и с диска
    cursor.execute("DELETE FROM establishment_photos WHERE id_establishment=?", (id_establishment,))
    conn.commit()

    conn.close()
