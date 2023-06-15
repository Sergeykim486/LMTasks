import logging, datetime, asyncio, Classes.functions as functions, Classes.buttons as buttons
from datetime import datetime
from Classes.edit_contragent import editcont
from Classes.add_new_task import NewTask
from Classes.reports import report
from Classes.config import ActiveUser, bot, db
# логи
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
sended = 0

# Проверка расписания
async def job():
    await schedule_message()
async def schedule_message():
    global sended
    while True:
        try:
            Tasks = db.select_table_with_filters('Tasks', {'status': 0})
            users = db.select_table('Users')
            if len(Tasks) > 0:
                for line in Tasks:
                    tid = line[0]
                    for user in users:
                        try:
                            uid = user[0]
                            mid = bot.send_message(
                                user[0],
                                functions.curtask(tid),
                                reply_markup=buttons.buttonsinline([['👍 Принять', 'confirm ' + str(tid)], ['📎 Назначить', 'set ' + str(tid)]])
                            )
                            db.insert_record('NewTasksMessages', [None, tid, uid, mid.message_id])
                        except Exception as e:
                            # logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
                            pass
                    db.update_records('Tasks', ['status'], [1], 'id', line[0])
        except Exception as e:
            # logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
            pass
        try:
            revs = db.select_table_with_filters('rev', {'status': 0})
            if len(revs) > 0:
                for line in revs:
                    db.update_records('rev', ['status'], [1], 'id', line[0])
                    mes = 'Поступил отзыв/оценка от клиента\n'
                    mes = mes + '\nКЛИЕНТ - ' + str(db.get_record_by_id('Clients', line[2])[2])
                    mes = mes + '\n\nОТЗЫВ:\n' + str(line[3])
                    mes = mes + '\n\nот ' + str(line[1])
                    functions.sendtoall(mes, '', 0)
        except Exception as e:
            # logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
            pass
        now = datetime.now()
        # if now.hour == 8 and now.minute == 0:
        #     await daylyreport.morning()
        if now.hour == 20 and now.minute == 00:
            if sended == 0:
                sended = 1
                await daylyreport.evening()
        else:
            sended = 0
        daterep = str(datetime.now().strftime("%d.%m.%Y"))
        locations = []
        addedlocs = db.select_table_with_filters('Tasks', {'status': 1})
        conflocs = db.select_table_with_filters('Tasks', {'status': 2})
        donet = db.select_table_with_filters('Tasks', {'status': 3}, ['done'], [daterep+' 00:00'], [daterep+' 23:59'])
        canceled = db.select_table_with_filters('Tasks', {'status': 4}, ['canceled'], [daterep+' 00:00'], [daterep+' 23:59'])
        try:
            for task in addedlocs:
                company = db.get_record_by_id('Contragents', task[3])[1]
                status = db.get_record_by_id('Statuses', task[11])[1]
                name = '№ ' + str(task[0]) + '\n|=============================|\n' + str(company)
                description = status + '\n | \n' + task[4]
                location = db.get_record_by_id('Locations', task[12])
                if task[12] != None and location != None:
                    lat = location[3]
                    lon = location[4]
                else:
                    lat = 41.28921489333344
                    lon = 69.31288111459628
                locations.append([name, description, lat, lon, task[11]])
        except Exception as e:
            logging.info(e)
            pass
        try:
            for task in conflocs:
                company = db.get_record_by_id('Contragents', task[3])[1]
                status = db.get_record_by_id('Statuses', task[11])[1]
                user = db.get_record_by_id('Users', task[6])
                if user == None:
                    master = '-'
                else:
                    master = str(user[2]) + ' ' + str(user[1])
                name = '№ ' + str(task[0]) + '\n|=============================|\n' + str(company)
                description = status + ' - ' + master + '\n | \n' + task[4]
                if task[12] is None:
                    lat = 41.28921489333344
                    lon = 69.31288111459628
                else:
                    loc = db.get_record_by_id('Locations', task[12])
                    lat = loc[3]
                    lon = loc[4]
                locations.append([name, description, lat, lon, task[11]])
        except Exception as e:
            logging.info(e)
            pass
        try:
            for task in donet:
                company = db.get_record_by_id('Contragents', task[3])[1]
                status = db.get_record_by_id('Statuses', task[11])[1]
                user = db.get_record_by_id('Users', task[6])
                if user == None:
                    master = '-'
                else:
                    master = str(user[2]) + ' ' + str(user[1])
                name = '№ ' + str(task[0]) + '\n|=============================|\n' + str(company)
                description = status + ' - ' + master + '\n | \n' + task[4]
                if task[12] is None:
                    lat = 41.28921489333344
                    lon = 69.31288111459628
                else:
                    loc = db.get_record_by_id('Locations', task[12])
                    lat = loc[3]
                    lon = loc[4]
                locations.append([name, description, lat, lon, task[11]])
        except Exception as e:
            logging.info(e)
            pass
        try:
            for task in canceled:
                company = db.get_record_by_id('Contragents', task[3])[1]
                status = db.get_record_by_id('Statuses', task[11])[1]
                name = '№ ' + str(task[0]) + '\n|=============================|\n' + str(company)
                description = status + '\n | \n' + task[4]
                if task[12] is None:
                    lat = 41.28921489333344
                    lon = 69.31288111459628
                else:
                    loc = db.get_record_by_id('Locations', task[12])
                    lat = loc[3]
                    lon = loc[4]
                locations.append([name, description, lat, lon, task[11]])
        except Exception as e:
            logging.info(e)
            pass
        if len(locations) > 0:
            functions.mmapgen(locations)
            functions.mapgen(locations)
        await asyncio.sleep(30)
async def main():
    await job()
# Дневные отчеты
class daylyreport:
    # Рассылка текущих хвостов спредыдущих дней
    async def morning():
        logging.info('план отправлен.')
        confirmedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 2}), [0, 1, 3, 4, 6], 1)
        addedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 1}), [0, 1, 3, 4, 6], 1)
        if len(confirmedtasks) == 0 and len(addedtasks) == 0:
            functions.sendtoall('Всем доброе утро!\nНа сегодня нет переходящих заявок.', '', 0)
        else:
            functions.sendtoall('Всем доброе утро!\nСо вчерашнего дня на сегодня переходят следующие заявки:', '', 0)
        if len(confirmedtasks) != 0:
            functions.sendtoall('ЗАЯВКИ У МАСТЕРОВ:\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in confirmedtasks:
                taskid = line.split()[2]
                functions.sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        if len(addedtasks) != 0:
            functions.sendtoall('НЕ РАСПРЕДЕЛЕННЫЕ ЗАЯВКИ:\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in addedtasks:
                taskid = line.split()[2]
                functions.sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        functions.sendtoall('🟥🟥🟥🟥🟥🟥🟥🟥\nСписок заявок на сегодня\n🟥🟥🟥🟥🟥🟥🟥🟥', '', 0)
    # Итоги дня
    async def evening():
        logging.info('план отправлен.')
        daten = str(datetime.now().strftime("%d.%m.%Y"))
        donetasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 3}, ['done'], [daten+' 00:00'], [daten+' 23:59']), [0, 1, 3, 4, 6], 1)
        confirmedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 2}), [0, 1, 3, 4, 6], 1)
        addedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 1}), [0, 1, 3, 4, 6], 1)
        canceledtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 4}, ['canceled'], [daten+' 00:00'], [daten+' 23:59']), [0, 1, 3, 4, 6], 1)
        # if len(confirmedtasks) != 0 and len(addedtasks) != 0:
        #     functions.sendtoall('ИТОГИ ДНЯ:\nНа завтра остаются следующие заявки:', '', 0)
        # if len(donetasks) != 0:
        #     functions.sendtoall('Выполненные заявки\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
        #     for line in donetasks:
        #         taskid = line.split()[2]
        #         functions.sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        # if len(confirmedtasks) != 0:
        #     functions.sendtoall('Заявки у мастеров\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
        #     for line in confirmedtasks:
        #         taskid = line.split()[2]
        #         functions.sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        # if len(addedtasks) != 0:
        #     functions.sendtoall('Не принятые заявки\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
        #     for line in addedtasks:
        #         taskid = line.split()[2]
        #         functions.sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        # if len(canceledtasks) != 0:
        #     functions.sendtoall('Отмененные\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
        #     for line in canceledtasks:
        #         taskid = line.split()[2]
        #         functions.sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        reports = '\n🟢 Выполнено - ' + str(len(donetasks)) + '\n🔵 Не распределенных - ' + str(len(addedtasks)) + '\n🟡 В работе у мастеров - ' + str(len(confirmedtasks)) + '\n🔴 Отменено - ' + str(len(canceledtasks))
        if len(donetasks) == 0:
            reports = reports + '\n\nВыполненных заявок нет.'
        else:
            reports = reports + '\n\nКоличество заявок выполненных мастерами:\n'
            users = db.select_table('Users')
            usersrep = []
            for i in users:
                tasks = len(db.select_table_with_filters('Tasks', {'master': i[0], 'status': 3}, ['done'], [daten+' 00:00'], [daten+' 23:59']))
                usersrep.append([i[2] + ' ' + i[1], tasks])
            sorted_usersrep = sorted(usersrep, key=lambda x: x[1], reverse=True)
            place = 1
            for j in sorted_usersrep:
                if j[1] != 0:
                    reports = reports + '\n'+ placenum(str(place)) + '. ' + j[0] + ' - ' + str(j[1])
                    place = place + 1
        functions.sendtoall('🔲🔳🔲🔳🔲🔳🔲🔳🔲🔳🔲🔳🔲\n\nИТОГИ ДНЯ\n' + reports + '\n\n🔲🔳🔲🔳🔲🔳🔲🔳🔲🔳🔲🔳🔲', '', 0)

def placenum(place):
    digits = {'0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣', '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'}
    result = ''.join(digits.get(c, c) for c in place)
    return result