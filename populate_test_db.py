import sqlite3
import os

def create_test_db():
    db_path = 'test_shame.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Все таблицы из основной базы
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS establishment_types (
        id_type INTEGER PRIMARY KEY,
        name TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS districts (
        id_district INTEGER PRIMARY KEY,
        name TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS establishments (
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS establishment_photos (
                    id_photo INTEGER PRIMARY KEY,
                    id_establishment INTEGER,
                    path_to_photo TEXT,
                    FOREIGN KEY (id_establishment) REFERENCES establishments(id_establishment))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    request_time DATETIME)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_contexts
                    (user_id INTEGER,
                     message_role TEXT,
                     message_content TEXT,
                     timestamp DATETIME,
                     PRIMARY KEY (user_id, timestamp))''')
    
    # Индекс для контекста
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_context_user_time ON chat_contexts(user_id, timestamp)')

    # Типы заведений
    cursor.executemany("INSERT INTO establishment_types (id_type, name) VALUES (?, ?)", [
        (1, 'Ресторан'),
        (2, 'Бар')
    ])
    # Районы
    cursor.executemany("INSERT INTO districts (id_district, name) VALUES (?, ?)", [
        (1, 'Арбат'),
        (2, 'Басманный')
    ])
    # Тестовые заведения
    cursor.executemany("INSERT INTO establishments (id_establishment, name, id_type, id_district, address, metro_station, cuisine, description, feature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [
        (1, "White Rabbit", 1, 1, "Смоленская пл., 3", "Смоленская", "русская", "Высокая кухня, панорамный вид", "панорамный вид, топ-100 мира"),
        (2, "Twins Garden", 1, 2, "Страстной бульвар, 8А", "Трубная", "авторская", "фермерская концепция, звезды Michelin", "звезды Michelin, фермерские продукты"),
        (3, "Selfie", 1, 1, "Новинский бульвар, 31, стр. 1", "Баррикадная", "европейская", "современная кухня, топ рейтинги", "топ рейтинги, современный интерьер"),
        (4, "Osteria Mario", 1, 2, "Петровка, 27", "Чеховская", "итальянская", "семейный ресторан, паста и пицца", "уютно, семейно"),
        (5, "Сулико", 1, 1, "Арбат, 12", "Арбатская", "грузинская", "традиционная грузинская кухня", "хинкали, хачапури"),
        (6, "Tokyo Sushi", 1, 2, "Басманная, 5", "Курская", "азиатская", "японская кухня, суши и роллы", "суши, роллы, японский стиль"),
        (7, "Кафе Пушкинъ", 1, 1, "Тверской бульвар, 26А", "Тверская", "русская", "Дворянская кухня в историческом особняке", "атмосфера XIX века, библиотека"),
        (8, "Матрешка", 1, 2, "Кутузовский проспект, 2/1с6", "Киевская", "русская", "Современная русская кухня", "вид на набережную, стильный интерьер"),
        (9, "Dr. Живаго", 1, 1, "Моховая ул., 15/1, стр. 1", "Охотный Ряд", "русская", "Советская кухня с видом на Кремль", "вид на Кремль, ностальгия")
    ])

    conn.commit()
    conn.close()
    print('Тестовая база test_shame.db создана и наполнена всеми таблицами.')

if __name__ == "__main__":
    create_test_db() 