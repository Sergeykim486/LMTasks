import sqlite3
import csv
import os
import logging
import textwrap
from colorama import Fore, Style


def clear_screen():
    # Очистка консоли
    os.system('cls' if os.name == 'nt' else 'clear')


def display_menu(options):
    # Отображение меню с возможными действиями
    clear_screen()
    print("Меню:")
    for index, option in enumerate(options):
        print(f"{index + 1}. {option}")
    print("0. Выход")


def get_table_names(cursor):
    # Получение списка имен таблиц в базе данных
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    return table_names


def get_column_names(cursor, table_name):
    # Получение списка имен колонок для указанной таблицы
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    return column_names


def display_table_data(cursor, table_name):
    # Отображение содержимого таблицы
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [description[0] for description in cursor.description]
    rows = cursor.fetchall()

    # Определение ширины каждой колонки
    column_widths = [15] * len(columns)  # Ширина колонки - 15 символов

    # Вывод разделителя
    separator = "├─" + "─┼─".join("─" * width for width in column_widths) + "─┤"
    print(separator)

    # Вывод заголовков колонок
    header = "│".join(f" {column.upper():^{width}} " for column, width in zip(columns, column_widths))
    print(f"│{header}│")

    # Вывод разделителя после заголовков
    print(separator)

    # Вывод данных таблицы
    for row in rows:
        wrapped_rows = []
        for value, width in zip(row, column_widths):
            value_str = str(value)
            if len(value_str) <= width:
                wrapped_rows.append([value_str])
            else:
                wrapped_lines = textwrap.wrap(value_str, width=width)
                wrapped_rows.append(wrapped_lines)

        num_rows = max(len(wrapped_rows[col_idx]) for col_idx in range(len(columns)))
        for row_idx in range(num_rows):
            row_data = []
            for col_idx, wrapped_value in enumerate(wrapped_rows):
                if row_idx < len(wrapped_value):
                    row_data.append(f" {wrapped_value[row_idx]:<{column_widths[col_idx]}} ")
                else:
                    row_data.append(f" {'':<{column_widths[col_idx]}} ")

            row_str = "│".join(row_data)
            print(f"│{row_str}│")

        # Вывод разделителя после каждой строки
        print(separator)

    # Вывод разделителя в конце
    print(separator)


def export_table_to_csv(cursor, table_name):
    # Экспорт таблицы в CSV файл
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()
    column_names = get_column_names(cursor, table_name)

    csv_filename = f"{table_name}.csv"

    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(column_names)
        writer.writerows(rows)

    print(f"\nТаблица '{table_name}' успешно экспортирована в файл '{csv_filename}'.\n")
    logging.info(f"Таблица '{table_name}' успешно экспортирована в файл '{csv_filename}'.")


def import_table_from_csv(cursor, table_name):
    # Импорт данных из CSV файла в таблицу
    csv_filename = f"{table_name}.csv"

    if not os.path.exists(csv_filename):
        print(f"\nФайл '{csv_filename}' не существует.\n")
        return

    with open(csv_filename, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

        if len(rows) < 2:
            print(f"\nФайл '{csv_filename}' не содержит данных для импорта.\n")
            return

        column_names = rows[0]
        values = rows[1:]

        # Проверка наличия всех колонок в таблице
        existing_columns = get_column_names(cursor, table_name)
        for column in column_names:
            if column not in existing_columns:
                print(f"\nТаблица '{table_name}' не содержит колонку '{column}'. Импорт невозможен.\n")
                return

        # Очистка таблицы перед импортом
        cursor.execute(f"DELETE FROM {table_name};")

        # Вставка данных из CSV файла в таблицу
        columns_string = ", ".join([f"{column} TEXT" for column in column_names])
        create_table_query = f"CREATE TABLE {table_name} ({columns_string});"
        cursor.execute(create_table_query)

        insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(column_names))});"
        cursor.executemany(insert_query, values)

    print(f"\nТаблица '{table_name}' успешно импортирована из файла '{csv_filename}'.\n")
    logging.info(f"Таблица '{table_name}' успешно импортирована из файла '{csv_filename}'.")


def add_object_to_table(cursor, table_name):
    # Добавление нового объекта в таблицу
    column_names = get_column_names(cursor, table_name)
    values = []

    print(f"\nДобавление нового объекта в таблицу '{table_name}':")
    for column_name in column_names:
        value = input(f"Введите значение для поля '{column_name}': ")
        values.append(value)

    insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(column_names))});"
    cursor.execute(insert_query, tuple(values))

    print(f"\nНовый объект успешно добавлен в таблицу '{table_name}'.\n")
    logging.info(f"Новый объект успешно добавлен в таблицу '{table_name}'.")


def update_object_in_table(cursor, table_name):
    # Редактирование выбранного объекта в таблице
    column_names = get_column_names(cursor, table_name)

    display_table_data(cursor, table_name)

    try:
        row_id = int(input("Введите ID объекта для редактирования: "))
    except ValueError:
        print("\nНекорректный ввод.")
        return

    if row_id <= 0:
        print("\nНекорректный ID объекта.")
        return

    select_query = f"SELECT * FROM {table_name} WHERE rowid = ?;"
    cursor.execute(select_query, (row_id,))
    row_data = cursor.fetchone()

    if row_data is None:
        print(f"\nОбъект с ID {row_id} не найден в таблице '{table_name}'.")
        return

    print(f"\nРедактирование объекта с ID {row_id} в таблице '{table_name}':")
    updated_values = []
    for index, column_name in enumerate(column_names):
        current_value = row_data[index]
        new_value = input(f"Введите новое значение для поля '{column_name}' (текущее значение: '{current_value}'): ")
        updated_values.append(new_value if new_value != "" else current_value)

    update_query = f"UPDATE {table_name} SET {', '.join([f'{column} = ?' for column in column_names])} WHERE rowid = ?;"
    cursor.execute(update_query, tuple(updated_values + [row_id]))

    print(f"\nОбъект с ID {row_id} успешно обновлен в таблице '{table_name}'.\n")
    logging.info(f"Объект с ID {row_id} успешно обновлен в таблице '{table_name}'.")


def delete_object_from_table(cursor, table_name):
    # Удаление выбранного объекта из таблицы
    display_table_data(cursor, table_name)

    try:
        row_id = int(input("Введите ID объекта для удаления: "))
    except ValueError:
        print("\nНекорректный ввод.")
        return

    if row_id <= 0:
        print("\nНекорректный ID объекта.")
        return

    delete_query = f"DELETE FROM {table_name} WHERE rowid = ?;"
    cursor.execute(delete_query, (row_id,))

    print(f"\nОбъект с ID {row_id} успешно удален из таблицы '{table_name}'.\n")
    logging.info(f"Объект с ID {row_id} успешно удален из таблицы '{table_name}'.")


def main():
    db_path = os.path.join("Database", "lmtasksbase.db")
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    logging.basicConfig(filename='baseeditlog.txt', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    while True:
        try:
            table_names = get_table_names(cursor)
            display_menu(table_names)

            try:
                choice = int(input("Введите номер таблицы (или 0 для выхода): "))
            except ValueError:
                continue

            if choice == 0:
                break

            if choice > 0 and choice <= len(table_names):
                table_name = table_names[choice - 1]
                display_table_data(cursor, table_name)

                action = input("Введите 'e' для экспорта в CSV, 'i' для импорта из CSV, 'a' для добавления объекта, "
                               "'u' для редактирования объекта, 'd' для удаления объекта или любую клавишу для продолжения: ")

                if action.lower() == "e":
                    export_table_to_csv(cursor, table_name)
                elif action.lower() == "i":
                    import_table_from_csv(cursor, table_name)
                elif action.lower() == "a":
                    add_object_to_table(cursor, table_name)
                elif action.lower() == "u":
                    update_object_in_table(cursor, table_name)
                elif action.lower() == "d":
                    delete_object_from_table(cursor, table_name)

                input("\nНажмите Enter для продолжения...")
            else:
                continue
        except Exception as e:
            print(f"\n{Fore.RED}Ошибка: {str(e)}{Style.RESET_ALL}\n")
            logging.exception(f"Ошибка: {str(e)}")
            input("\nНажмите Enter для продолжения...")

    connection.close()


if __name__ == "__main__":
    main()