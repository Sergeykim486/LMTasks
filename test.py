import os
from db import Database
from openpyxl import Workbook
from datetime import datetime

# Определяем имя файла базы данных
dbname = os.path.dirname(os.path.abspath(__file__)) + '/Database/' + 'lmtasksbase.db'

# Создаем объект базы данных
db = Database(dbname)


def print_table(table_name):
    """
    Выводит содержимое таблицы на экран
    """
    rows = db.select_table(table_name)
    if not rows:
        print("Таблица пуста")
        return
    for row in rows:
        print(row)

def tasks_in_period(dfrom, dto):
    rows = db.select_table("Tasks")
    if not rows:
        print("Таблица пуста")
        return
    else:
        tableforexp = []
        for row in rows:
            if datetime.strptime(str(dfrom)+" 00:00", '%d.%m.%Y %H:%M') < datetime.strptime(row[1], '%d.%m.%Y %H:%M') < datetime.strptime(str(dto)+" 23:59", '%d.%m.%Y %H:%M'):
                tableforexp.append((
                    row[0],
                    row[1],
                    str(db.get_record_by_id("Users", row[2])[2]) + " " + str(db.get_record_by_id("Users", row[2])[1]) if row[2] is not None and db.get_record_by_id("Users", row[2]) is not None else '',
                    str(db.get_record_by_id("Contragents", row[3])[1]) if row[3] is not None and db.get_record_by_id("Contragents", row[3]) is not None else '',
                    row[4],
                    row[5],
                    str(db.get_record_by_id("Users", row[6])[2]) + " " + str(db.get_record_by_id("Users", row[6])[1]) if row[6] is not None and db.get_record_by_id("Users", row[6]) is not None else '',
                    row[7],
                    row[8],
                    str(db.get_record_by_id("Users", row[9])[2]) + " " + str(db.get_record_by_id("Users", row[9])[1]) if row[9] is not None and db.get_record_by_id("Users", row[9]) is not None else '',
                    row[10],
                    str(db.get_record_by_id("Statuses", row[11])[1]) if row[11] is not None and db.get_record_by_id("Statuses", row[11]) is not None else ''
                ))

        wb = Workbook()
        ws = wb.active
        ws.append(["№", "Дата поступления", "Зарегистрировал", "Клиент", "Тема заявки", "Дата принятия мастером", "Мастер", "Завершена", "Отменена", "Кем отменена", "Примечание", "Статус"])
        for r in tableforexp:
            ws.append(r)
        wb.save("Отчет по заявкам за период с " + dfrom + " по " + dto + ".xlsx")

def export_table_to_excel(table_name, filename):
    """
    Экспортирует содержимое таблицы в файл xlsx
    """
    rows = db.select_table(table_name)
    if not rows:
        print("Таблица пуста")
        return
    wb = Workbook()
    ws = wb.active
    ws.append([i[0] for i in db.cur.description])
    for row in rows:
        ws.append(row)
    wb.save(filename)

def create_table():
    """
    Создает новую таблицу
    """
    table_name = input("Введите имя таблицы: ")
    num_columns = int(input("Введите количество столбцов: "))
    columns = []
    for i in range(num_columns):
        column_name = input(f"Введите имя столбца {i+1}: ")
        column_type = input(f"Введите тип данных для столбца {column_name}: ")
        columns.append(f"{column_name} {column_type}")
    db.create_table(table_name, columns)
    print(f"Таблица {table_name} создана")


def delete_table():
    """
    Удаляет таблицу
    """
    table_name = input("Введите имя таблицы, которую нужно удалить: ")
    db.cur.execute(f"DROP TABLE IF EXISTS {table_name}")
    db.conn.commit()
    print(f"Таблица {table_name} удалена")


def insert_record():
    """
    Добавляет новую запись в таблицу
    """
    table_name = input("Введите имя таблицы: ")
    columns = db.cur.execute(f"PRAGMA table_info({table_name})").fetchall()
    values = []
    for column in columns:
        value = input(f"Введите значение для столбца {column[1]}: ")
        values.append(value)
    db.insert_record(table_name, values)
    print("Запись добавлена")


def update_record():
    """
    Обновляет запись в таблице
    """
    table_name = input("Введите имя таблицы: ")
    row_id = input("Введите ID записи, которую нужно обновить: ")
    columns = db.cur.execute(f"PRAGMA table_info({table_name})").fetchall()
    for column in columns:
        new_value = input(f"Введите новое значение для столбца {column[1]}: ")
        db.update_record(table_name, column[1], new_value, "id", row_id)
    print("Запись обновлена")


def delete_record():
    """
    Удаляет запись из таблицы
    """
    table_name = input("Введите имя таблицы: ")
    row_id = input("Введите ID записи, которую нужно удалить: ")
    db.delete_record(table_name, "id", row_id)
    print("Запись удалена")


# Главный цикл программы
while True:
    print("1. Вывести содержимое таблицы")
    print("2. Экспорт в Excel")
    print("3. Создать таблицу")
    print("4. Удалить таблицу")
    print("5. Добавить запись в таблицу")
    print("6. Обновить запись в таблице")
    print("7. Удалить запись из таблицы")
    print("8. Отчет по заявкам за период")
    print("0. Выход")
    choice = input("Введите номер действия: ")

    if choice == "1":
        table_name = input("Введите имя таблицы: ")
        print_table(table_name)

    if choice == "2":
        table_name = input("Введите имя таблицы: ")
        xls_file_name = input("Введите имя таблицы: ")
        export_table_to_excel(table_name,xls_file_name)

    elif choice == "3":
        create_table()

    elif choice == "4":
        delete_table()

    elif choice == "5":
        insert_record()

    elif choice == "6":
        update_record()

    elif choice == "7":
        delete_record()

    elif choice == "8":
        dfrom = input("Введите дату начала периода: ")
        dto = input("Введите дату окончания периода: ")
        tasks_in_period(dfrom, dto)

    elif choice == "0":
        print("Выход")
        break

    else:
        print("Неправильный выбор, повторите попытку")

