import os
import csv
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, NamedStyle
from db import Database

# формируем абсолютный путь до базы данных
db_path = os.path.abspath("Database/lmtasksbase.db")

# создаем подключение к базе данных
db = Database(db_path)

# получаем список статусов из базы данных
statuses = db.select_table("Statuses")

# запрашиваем у пользователя статусы, по которым нужно сформировать отчет
print("Выберите статусы для формирования отчета:")
for i, status in enumerate(statuses):
    print(f"{i + 1}. {status[1]}")
status_choices = input("Введите номера статусов через запятую: ").split(",")
status_ids = [statuses[int(choice) - 1][0] for choice in status_choices]

# запрашиваем у пользователя период, за который нужно сформировать отчет
start_date_str = input("Введите начало периода в формате ДД.ММ.ГГГГ ЧЧ:ММ: ")
end_date_str = input("Введите конец периода в формате ДД.ММ.ГГГГ ЧЧ:ММ: ")
start_date = datetime.datetime.strptime(start_date_str, "%d.%m.%Y %H:%M")
end_date = datetime.datetime.strptime(end_date_str, "%d.%m.%Y %H:%M")

# получаем список заявок из базы данных по заданным статусам и периоду
tasks = db.select_table_with_filters(
    "Tasks",
    {"status": status_ids},
)
filtered_tasks = [
    task
    for task in tasks
    if start_date <= datetime.datetime.strptime(task[1], "%d.%m.%Y %H:%M") <= end_date
]

# заменяем id пользователей и клиентов на их имя и фамилию
users = db.select_table("Users")
contragents = db.select_table("Contragents")
for i, task in enumerate(filtered_tasks):
    manager_id = task[2]
    contragent_id = task[3]
    master_id = task[6]
    userc_id = task[9]

    manager = next((user for user in users if user[0] == manager_id), None)
    contragent = next((c for c in contragents if c[0] == contragent_id), None)
    master = next((user for user in users if user[0] == master_id), None)
    userc = next((user for user in users if user[0] == userc_id), None)

    if manager is not None:
        filtered_tasks[i] = (
            task[0],
            task[1],
            f"{manager[2]} {manager[1]}",
            contragent[1] if contragent is not None else "",
            task[4],
            task[5],
            f"{master[2]} {master[1]}" if master is not None else "",
            task[7],
            task[8],
            f"{userc[2]} {userc[1]}" if userc is not None else "",
            task[10],
            task[11],
        )


# Создаем объект Workbook
workbook = Workbook()

# Получаем активный лист
worksheet = workbook.active

# Настройки форматирования
bold_font = Font(bold=True)
header_fill = PatternFill(start_color='C0C0C0', end_color='C0C0C0', fill_type='solid')
date_format = NamedStyle(name='datetime', number_format='DD.MM.YYYY HH:MM')

# Заголовки столбцов
headers = ["ID", "Дата создания", "Менеджер", "Клиент", "Тема", "Принята мастером", "Мастер", "Завершена", "Отменена", "Кто отменил", "Примечание", "Статус"]
for i, header in enumerate(headers):
    cell = worksheet.cell(row=1, column=i+1)
    cell.value = header
    cell.fill = header_fill
    cell.font = bold_font

# Данные
for i, task in enumerate(filtered_tasks):
    for j, value in enumerate(task):
        cell = worksheet.cell(row=i+2, column=j+1)
        if isinstance(value, datetime.datetime):
            cell.value = value
            cell.style = date_format
        else:
            cell.value = value

# Сохраняем файл
report_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_report.xlsx")
workbook.save(report_name)


# Сохраняем файл
report_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_report.xlsx")
workbook.save(report_name)
# сохраняем результаты в файл csv
# report_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S_report.csv")
# with open(report_name, mode="w", newline="", encoding="utf-8") as report_file:
#     report_writer = csv.writer(report_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
#     report_writer.writerow(["ID", "Дата создания", "Менеджер", "Клиент", "Тема", "Принята мастером", "Мастер", "Завершена", "Отменена", "Кто отменил", "Примечание", "Статус"])
#     report_writer.writerows(filtered_tasks)

# print(f"Отчет сохранен в файл {report_name}.")