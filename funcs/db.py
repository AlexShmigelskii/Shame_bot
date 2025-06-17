import os
import aiosqlite
import datetime

# Заменяю все подключения к базе данных на test_shame.db
DB_PATH = 'shame_new.db'


async def create_database():
    # Подключение к базе данных
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.cursor()

        # Создание таблицы пользователей
        await cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT)''')

        # Создание таблицы заведений
        await cursor.execute('''CREATE TABLE IF NOT EXISTS establishments (
                        id_establishment INTEGER PRIMARY KEY,
                        name TEXT,
                        id_type INTEGER,
                        id_district INTEGER,
                        address TEXT,
                        metro_station TEXT,
                        cuisine TEXT,
                        description TEXT,
                        feature TEXT,
                        FOREIGN KEY (id_type) REFERENCES establishment_types(id_type),
                        FOREIGN KEY (id_district) REFERENCES districts(id_district))''')

        # Создание таблицы типов заведений
        await cursor.execute('''CREATE TABLE IF NOT EXISTS establishment_types (
                        id_type INTEGER PRIMARY KEY,
                        name TEXT)''')

        # Создание таблицы районов
        await cursor.execute('''CREATE TABLE IF NOT EXISTS districts (
                        id_district INTEGER PRIMARY KEY,
                        name TEXT)''')

        # Создание таблицы фотографий заведений
        await cursor.execute('''CREATE TABLE IF NOT EXISTS establishment_photos (
                        id_photo INTEGER PRIMARY KEY,
                        id_establishment INTEGER,
                        path_to_photo TEXT,
                        FOREIGN KEY (id_establishment) REFERENCES establishments(id_establishment))''')

        # Создание таблицы запросов к боту
        await cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        request_time DATETIME)''')

        await cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                        id_booking INTEGER PRIMARY KEY,
                        id_establishment INTEGER,
                        user_id INTEGER,
                        contact_info TEXT,
                        booking_time DATETIME,
                        FOREIGN KEY (id_establishment) REFERENCES establishments(id_establishment))''')

        # Проверяем, пустые ли таблицы перед заполнением
        await cursor.execute("SELECT COUNT(*) FROM districts")
        if (await cursor.fetchone())[0] == 0:
            districts = [
                "Арбат", "Басманный", "Замоскворечье", "Красносельский", "Мещанский",
                "Пресненский", "Таганский", "Тверской", "Хамовники", "Якиманка"
            ]
            for district in districts:
                await cursor.execute("INSERT INTO districts (name) VALUES (?)", (district,))

        await cursor.execute("SELECT COUNT(*) FROM establishment_types")
        if (await cursor.fetchone())[0] == 0:
            establishment_types = ["Ресторан", "Бар"]
            for est_type in establishment_types:
                await cursor.execute("INSERT INTO establishment_types (name) VALUES (?)", (est_type,))

        await db.commit()


async def add_new_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        await db.commit()


async def check_existing_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        existing_user = await cursor.fetchone()
        return existing_user


async def get_district_id(district_name):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id_district FROM districts WHERE name=?", (district_name,))
        result = await cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


async def get_type_id(establishment_type):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id_type FROM establishment_types WHERE name=?", (establishment_type,))
        result = await cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


# Функция для сохранения заведения в базе данных
async def save_establishment_to_database(name, features, address, metro, cuisine, description, district_id, type_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("INSERT INTO establishments (name, feature, address, metro_station, cuisine, description, id_district, id_type)"
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (name, features, address, metro, cuisine, description, district_id, type_id))
        await db.commit()
        establishment_id = cursor.lastrowid
        return establishment_id


async def check_existing_establishment(name, address, metro, description, type_id, district_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id_establishment FROM establishments WHERE name=? AND address=? AND metro_station=? AND description=? AND id_type=? AND id_district=?",
                       (name, address, metro, description, type_id, district_id))
        result = await cursor.fetchone()
        if result:
            return result[0]
        else:
            return None


async def save_photo_path_to_database(establishment_id, photo_path):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO establishment_photos (id_establishment, path_to_photo) VALUES (?, ?)",
                       (establishment_id, photo_path))
        await db.commit()


async def get_establishments(district_name, establishment_type):
    async with aiosqlite.connect(DB_PATH) as db:
        district_id = await get_district_id(district_name)
        establishment_type_id = await get_type_id(establishment_type)
        cursor = await db.execute("SELECT * FROM establishments WHERE id_district=? AND id_type=?", (district_id, establishment_type_id))
        establishments = await cursor.fetchall()
        return establishments


async def get_photo_paths_for_establishment(establishment_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT path_to_photo FROM establishment_photos WHERE id_establishment = ?", (establishment_id,))
        photo_paths = await cursor.fetchall()
        return [path[0] for path in photo_paths]


async def get_establishments_any_type(district_name):
    async with aiosqlite.connect(DB_PATH) as db:
        good_district = district_name.split("admin_")[1]
        district_id = await get_district_id(good_district)
        cursor = await db.execute("SELECT * FROM establishments WHERE id_district=?", (district_id,))
        establishments = await cursor.fetchall()
        return establishments


async def delete_establishment(id_establishment):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT path_to_photo FROM establishment_photos WHERE id_establishment=?", (id_establishment,))
        photo_paths = await cursor.fetchall()

        for photo_path in photo_paths:
            if os.path.exists(photo_path[0]):
                os.remove(photo_path[0])

        await db.execute("DELETE FROM establishments WHERE id_establishment=?", (id_establishment,))
        await db.execute("DELETE FROM establishment_photos WHERE id_establishment=?", (id_establishment,))
        await db.commit()


async def get_user_count():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM users')
        user_count = (await cursor.fetchone())[0]
        return user_count


async def get_establishment_count():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM establishments')
        establishment_count = (await cursor.fetchone())[0]
        return establishment_count


async def log_request(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO requests (user_id, request_time) VALUES (?, ?)
        """, (user_id, datetime.datetime.now()))
        await db.commit()


async def get_request_counts_by_hour(start_date, end_date):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT strftime('%Y-%m-%d %H:00:00', request_time) as hour, COUNT(*)
            FROM requests
            WHERE request_time BETWEEN ? AND ?
            GROUP BY hour
            ORDER BY hour
        """, (start_date.strftime("%Y-%m-%d %H:%M:%S"), end_date.strftime("%Y-%m-%d %H:%M:%S")))
        data = await cursor.fetchall()
        request_counts = {datetime.datetime.strptime(hour, "%Y-%m-%d %H:00:00"): count for hour, count in data}
        return request_counts


async def get_establishment_by_id(establishment_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id_establishment, name, feature, address, metro_station, cuisine, description FROM establishments WHERE id_establishment=?", (establishment_id,))
        row = await cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1], "feature": row[2], "address": row[3], "metro": row[4], "cuisine": row[5], "desc": row[6]}
        return None


async def log_booking(establishment_id: int, user_id: int, contact_info: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO bookings (id_establishment, user_id, contact_info, booking_time) VALUES (?, ?, ?, ?)",
                       (establishment_id, user_id, contact_info, datetime.datetime.now()))
        await db.commit()


async def get_booking_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT e.name, b.contact_info, b.booking_time
            FROM bookings b
            JOIN establishments e ON b.id_establishment = e.id_establishment
            ORDER BY b.booking_time DESC
        """)
        stats = await cursor.fetchall()
        return stats


async def get_places_from_db(category, cuisine):
    async with aiosqlite.connect(DB_PATH) as db:
        query = "SELECT id_establishment, name, feature, address, metro_station, cuisine, description FROM establishments"
        params = []
        
        selected_cuisine = cuisine.lower()
        
        if selected_cuisine != 'any':
            query += " WHERE (cuisine = ? OR cuisine = 'any')"
            params.append(selected_cuisine)
                
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [
            {"id": r[0], "name": r[1], "feature": r[2], "address": r[3], "metro": r[4], "cuisine": r[5], "desc": r[6]} for r in rows
        ]

