import os
import sqlite3

import openpyxl
from openpyxl_image_loader import SheetImageLoader

from funcs.db import save_establishment_to_database, get_type_id, get_district_id


def insert_photo_paths_into_database(id_establishment, photo_paths):
    conn = sqlite3.connect('shame.db')
    cursor = conn.cursor()

    for photo_path in photo_paths:
        cursor.execute("INSERT INTO establishment_photos (id_establishment, path_to_photo) VALUES (?, ?)",
                       (id_establishment, photo_path))

    conn.commit()
    conn.close()


def populate_photo_db():
    pxl_doc = openpyxl.load_workbook('table.xlsx')
    sheet = pxl_doc['Заведения']

    #calling the image_loader
    image_loader = SheetImageLoader(sheet)

    for row in range(1, 61):

        row_folder = f'photos/{row}'
        os.makedirs(row_folder, exist_ok=True)

        image1 = image_loader.get(f'H{row + 1}')
        image2 = image_loader.get(f'I{row + 1}')
        image3 = image_loader.get(f'J{row + 1}')
        image4 = image_loader.get(f'K{row + 1}')

        image1.save(f'photos/{row}/photo_1.png')
        image2.save(f'photos/{row}/photo_2.png')
        image3.save(f'photos/{row}/photo_3.png')
        image4.save(f'photos/{row}/photo_4.png')

        # Вставка путей к фотографиям в таблицу establishment_photos
        photo_paths = [f'photos/{row}/photo_1.png', f'photos/{row}/photo_2.png', f'photos/{row}/photo_3.png', f'photos/{row}/photo_4.png']
        insert_photo_paths_into_database(row, photo_paths)


async def populate_db():
    pxl_doc = openpyxl.load_workbook('table.xlsx')
    sheet = pxl_doc['Заведения']

    for row in range(1, 62):
        establishment_name = sheet[f'A{row}'].value.strip()
        establishment_type_name = sheet[f'B{row}'].value.strip()
        district_name = sheet[f'C{row}'].value.strip()
        address = sheet[f'D{row}'].value.strip()
        metro_station = sheet[f'E{row}'].value.strip()
        features = sheet[f'F{row}'].value.strip()
        description = sheet[f'G{row}'].value.strip()

        # Получите идентификатор типа заведения и района из словарей
        establishment_type_id = get_type_id(establishment_type_name)
        district_id = get_district_id(district_name)

        # Проверьте, что тип заведения и район существуют в базе данных
        if establishment_type_id is None or district_id is None:
            print(f"Ошибка: Неверный тип заведения или район в строке {row}. Пропускаю строку.")
            continue

        # Вставьте данные в базу данных
        await save_establishment_to_database(establishment_name, features, address, metro_station, description, district_id,
                                       establishment_type_id)

if __name__ == "__main__":
    populate_photo_db()
