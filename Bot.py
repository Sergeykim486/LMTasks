import os, config, telebot, functions, buttons, logging, time, pickle, asyncio, threading
from telebot import TeleBot, types
from db import Database
from datetime import datetime
# логи
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Глобальная переменная, база и создание объекта бот
ActiveUser = {}
sendedmessages = []
dbname = os.path.dirname(os.path.abspath(__file__)) + '/Database/' + 'lmtasksbase.db'
db = Database(dbname)
bot = telebot.TeleBot(config.TOKEN)
continue_polling = True
sch = 0
# Добавление в список пользователей клиентского бота
if db.get_record_by_id('Users', 0) == None:
    db.insert_record(
        'Users',
        [
            0,
            'Client BOT',
            '...',
            '...'
        ]
    )
# Добавление новой таблицы с локациями и голонки локации для заявки
db.add_column_to_table("Tasks", "location", "INTEGER")
cols = [
    "id INTEGER PRIMARY KEY",
    "inn INTEGER",
    "name TEXT",
    "lat TEXT",
    "lon TEXT"
]
db.create_table("Locations", cols)
# Проверка расписания
async def job():
    await schedule_message()
async def schedule_message():
    while True:
        logging.info('Проверка расписания')
        try:
            Tasks = db.select_table_with_filters('Tasks', {'status': 0})
            if len(Tasks) > 0:
                for line in Tasks:
                    db.update_records('Tasks', ['status'], [1], 'id', line[0])
                    tid = line[0]
                    sendtoall(functions.curtask(tid), buttons.buttonsinline([['Принять', 'confirm ' + str(tid)], ['Назначить', 'set ' + str(tid)]]), 0)
        except Exception as e:
            logging.error(e)
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
                    sendtoall(mes, '', 0)
        except Exception as e:
            logging.error(e)
            pass
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:
            await daylyreport.morning()
        elif now.hour == 20 and now.minute == 0:
            await daylyreport.evening()
        # Формирование карты заявок
        logging.info('формирование карты заявок')
        daterep = str(datetime.now().strftime("%d.%m.%Y"))
        locations = []
        addedlocs = db.select_table_with_filters('Tasks', {'status': 1})
        conflocs = db.select_table_with_filters('Tasks', {'status': 2})
        donet = db.select_table_with_filters('Tasks', {'status': 3}, ['done'], [daterep+' 00:00'], [daterep+' 23:59'])
        canceled = db.select_table_with_filters('Tasks', {'status': 4}, ['canceled'], [daterep+' 00:00'], [daterep+' 23:59'])
        print(f'Добавленные - {len(addedlocs)}\nПринятые - {len(conflocs)}\nЗавершенные - {len(donet)}\nОтмененные - {len(canceled)}\n')
        print('Не принятые')
        try:
            for task in addedlocs:
                company = db.get_record_by_id('Contragents', task[3])[1]
                status = db.get_record_by_id('Statuses', task[11])[1]
                name = '№ ' + str(task[0]) + '\n|=============================|\n' + str(company)
                description = status + '\n | \n' + task[4]
                location = db.get_record_by_id('Locations', task[12])
                if task[12] is not None and location is not None:
                    lat = location[3]
                    lon = location[4]
                else:
                    lat = 41.28921489333344
                    lon = 69.31288111459628
                locations.append([name, description, lat, lon, task[11]])
        except Exception as e:
            logging.info(e)
            pass
        print('Принятые')
        try:
            for task in conflocs:
                company = db.get_record_by_id('Contragents', task[3])[1]
                status = db.get_record_by_id('Statuses', task[11])[1]
                user = db.get_record_by_id('Users', task[6])
                master = str(user[2]) + ' ' + str(user[1])
                name = '№ ' + str(task[0]) + '\n|=============================|\n' + str(company)
                description = status + ' - ' + master + '\n | \n' + task[4]
                if task[12] is None:
                    lat = 41.28921489333344
                    lon = 69.31288111459628
                else:
                    lat = db.get_record_by_id('Locations', task[12])[3]
                    lon = db.get_record_by_id('Locations', task[12])[4]
                locations.append([name, description, lat, lon, task[11]])
        except Exception as e:
            logging.info(e)
            pass
        print('Выполненные')
        try:
            for task in donet:
                company = db.get_record_by_id('Contragents', task[3])[1]
                status = db.get_record_by_id('Statuses', task[11])[1]
                user = db.get_record_by_id('Users', task[6])
                master = str(user[2]) + ' ' + str(user[1])
                name = '№ ' + str(task[0]) + '\n|=============================|\n' + str(company)
                description = status + ' - ' + master + '\n | \n' + task[4]
                if task[12] is None:
                    lat = 41.28921489333344
                    lon = 69.31288111459628
                else:
                    lat = db.get_record_by_id('Locations', task[12])[3]
                    lon = db.get_record_by_id('Locations', task[12])[4]
                locations.append([name, description, lat, lon, task[11]])
        except Exception as e:
            logging.info(e)
            pass
        print('Отмененные')
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
                    lat = db.get_record_by_id('Locations', task[12])[3]
                    lon = db.get_record_by_id('Locations', task[12])[4]
                locations.append([name, description, lat, lon, task[11]])
        except Exception as e:
            logging.info(e)
            pass
        if len(locations) > 0:
            functions.mmapgen(locations)
            functions.mapgen(locations)
        # global sch, continue_polling
        
        # if continue_polling == False:
        #     if sch < 4:
        #         sch = sch + 1
        #     elif sch == 4:
        #         continue_polling = True
        #         bot.polling()
        #         sch = 0
        # else:
        #     sch = 0

        await asyncio.sleep(15)
async def main():
    await job()
# отправка сообщения всем пользователям
def sendtoall(message, markdown, exeptions, nt = 0, notific = False):
    global sendedmessages
    users = db.select_table('Users')
    for user in users:
        logging.info(f'sended message to user {user[2]} {user[1]}')
        try:
            if user[0] != exeptions:
                mes = bot.send_message(
                    user[0],
                    message,
                    reply_markup=markdown,
                    disable_notification=notific
                )
                if nt == 1:
                    sendedmessages.append([[user[0]], [mes.message_id]])
        except Exception as e:
            logging.error(e)
            pass
    return
# Список локаций контрагента
def sendlocations(inn, message):
    locs = db.select_table_with_filters('Locations', {'inn': inn})
    if len(locs) > 0:
        for location in locs:
            loc = types.Location(location[4], location[3])
            bot.send_location(message.chat.id, loc.latitude, loc.longitude)
            bot.send_message(
                message.chat.id,
                str(location[2]),
                reply_markup=buttons.buttonsinline([['Изменить', 'location '+str(location[0])]])
            )
    else:
        return
# Дневной отчет для рассылки по расписанию
class daylyreport:
    # Рассылка текущих хвостов спредыдущих дней
    async def morning():
        logging.info('план отправлен.')
        confirmedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 2}), [0, 1, 3, 4, 6], 1)
        addedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 1}), [0, 1, 3, 4, 6], 1)
        if len(confirmedtasks) == 0 and len(addedtasks) == 0:
            sendtoall('Всем доброе утро!\nНа сегодня нет переходящих заявок.', '', 0)
        else:
            sendtoall('Всем доброе утро!\nСо вчерашнего дня на сегодня переходят следующие заявки:', '', 0)
        if len(confirmedtasks) != 0:
            sendtoall('ЗАЯВКИ У МАСТЕРОВ:\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in confirmedtasks:
                taskid = line.split()[2]
                sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        if len(addedtasks) != 0:
            sendtoall('НЕ РАСПРЕДЕЛЕННЫЕ ЗАЯВКИ:\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in addedtasks:
                taskid = line.split()[2]
                sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        sendtoall('🟥🟥🟥🟥🟥🟥🟥🟥\nСписок заявок на сегодня\n🟥🟥🟥🟥🟥🟥🟥🟥', '', 0)
    # Итоги дня
    async def evening():
        logging.info('план отправлен.')
        daten = str(datetime.now().strftime("%d.%m.%Y"))
        donetasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 3}, ['done'], [daten+' 00:00'], [daten+' 23:59']), [0, 1, 3, 4, 6], 1)
        confirmedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 2}), [0, 1, 3, 4, 6], 1)
        addedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 1}), [0, 1, 3, 4, 6], 1)
        canceledtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 4}, ['canceled'], [daten+' 00:00'], [daten+' 23:59']), [0, 1, 3, 4, 6], 1)
        if len(confirmedtasks) != 0 and len(addedtasks) != 0:
            sendtoall('ИТОГИ ДНЯ:\nНа завтра остаются следующие заявки:', '', 0)
        if len(donetasks) != 0:
            sendtoall('Выполненные заявки\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in donetasks:
                taskid = line.split()[2]
                sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        if len(confirmedtasks) != 0:
            sendtoall('Заявки у мастеров\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in confirmedtasks:
                taskid = line.split()[2]
                sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        if len(addedtasks) != 0:
            sendtoall('Не принятые заявки\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in addedtasks:
                taskid = line.split()[2]
                sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        if len(canceledtasks) != 0:
            sendtoall('Отмененные\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in canceledtasks:
                taskid = line.split()[2]
                sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        reports = '\nВыполнено - ' + str(len(donetasks)) + '\nНе распределенных - ' + str(len(addedtasks)) + '\nВ работе у мастеров - ' + str(len(confirmedtasks)) + '\nОтменено - ' + str(len(canceledtasks))
        if len(donetasks) == 0:
            reports = reports + '\n\nВыполненных заявок нет.'
        else:
            reports = reports + '\n\nКоличество заявок выполненных мастерами:\n'
            users = db.select_table('Users')
            usersrep = []
            for i in users:
                tasks = len(db.select_table_with_filters('Tasks', {'master': i[0]}, ['done'], [daten+' 00:00'], [daten+' 23:59']))
                usersrep.append([i[2] + ' ' + i[1], tasks])
            sorted_usersrep = sorted(usersrep, key=lambda x: x[1], reverse=True)
            for j in sorted_usersrep:
                if j[1] != 0:
                    reports = reports + '\n' + j[0] + ' - ' + str(j[1])
        sendtoall('ИТОГИ ДНЯ\n🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺' + reports, '', 0)

@bot.message_handler(commands=['start'])
# проверка пользователя при первом запуске
def check_user_id(message):
    user_id = message.from_user.id
    global ActiveUser, continue_polling
    try:
        username = db.get_record_by_id('Users', user_id)[2] + ' ' + db.get_record_by_id('Users', user_id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    continue_polling = True
    ActiveUser[user_id] = {'id': user_id}
    # finduser = db.search_record("Users", "id", user_id)
    user = db.get_record_by_id('Users', user_id)
    if user is None:
        bot.send_message(
            user_id,
            'Вам нужно пройти регистрацию',
            reply_markup=buttons.Buttons(['Регистрация'])
        )
        bot.register_next_step_handler(message, Reg.reg1)

    else:
        bot.send_message(
            user_id,
            'Выберите операцию.',
            reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
        )
        bot.register_next_step_handler(message, MainMenu.Main2)

@bot.message_handler(func=lambda message: True)
# проверка пользователя при первом запуске
def check_user_id(message):
    user_id = message.from_user.id
    global ActiveUser, continue_polling
    try:
        username = db.get_record_by_id('Users', user_id)[2] + ' ' + db.get_record_by_id('Users', user_id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    continue_polling = True
    ActiveUser[user_id] = {'id': user_id}
    # finduser = db.search_record("Users", "id", user_id)
    user = db.get_record_by_id('Users', user_id)
    if user is None:
        bot.send_message(
            user_id,
            'Вам нужно пройти регистрацию',
            reply_markup=buttons.Buttons(['Регистрация'])
        )
        bot.register_next_step_handler(message, Reg.reg1)

# Регистрация нового пользователя
class Reg:
    # Запрос имени у пользователя
    def reg1(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == 'Регистрация':
            bot.send_message(
                message.chat.id,
                'Как Вас зовут (укажите имя)',
            reply_markup=buttons.clearbuttons()
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, Reg.reg2)
        else:
            bot.send_message(
                message.chat.id,
                'Пожалуйста зарегистрируйтесь.',
                reply_markup=buttons.Buttons(['Регистрация'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, Reg.reg1)
    # Сохранение имени и запрос фамилии
    def reg2(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        global ActiveUser
        ActiveUser[message.chat.id]['FirstName'] = message.text
        bot.send_message(
            message.chat.id,
            'Укажите Вашу фамилию.',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Reg.reg3)
    # Сохранение фамилии и запрос номера телефона
    def reg3(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        global ActiveUser
        ActiveUser[message.chat.id]['LastName'] = message.text
        bot.send_message(
            message.chat.id,
            'Введите Ваш номер телефона в формате (+998 00 000 0000).',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Reg.reg4)
    # Сохранение телефона и запрос на подтверждение сохраненных данных
    def reg4(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        global ActiveUser
        ActiveUser[message.chat.id]['PhoneNumber'] = message.text
        bot.send_message(
            message.chat.id,
            functions.conftext(message, ActiveUser),
            reply_markup=buttons.Buttons(['Да', 'Нет'])
        )
        bot.register_next_step_handler(message, Reg.reg5)
    # Проверка подтверждения данных
    def reg5(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        global ActiveUser
        if message.text == 'Да':
            valuedict = [
                ActiveUser[message.chat.id]['id'],
                ActiveUser[message.chat.id]['FirstName'],
                ActiveUser[message.chat.id]['LastName'],
                ActiveUser[message.chat.id]['PhoneNumber']
            ]
            db.insert_record("Users", valuedict)
            bot.send_message(
                message.chat.id,
                'Поздравляем Вы успешно зарегистрировались!',
                reply_markup=buttons.Buttons(['Главное меню'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main1)
        elif message.text == 'Нет':
            bot.send_message(
                message.chat.id,
                'Пройдите регистрацию повторно.',
                reply_markup=buttons.Buttons(['Регистрация'])
            )
            bot.register_next_step_handler(message, Reg.reg1)
        else:
            bot.send_message(
                message.chat.id,
                'Вы не подтвердили информацию!\n' + functions.conftext(message, ActiveUser),
                reply_markup=buttons.Buttons(['Да', 'Нет'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, Reg.reg5)
# Главное меню и обработка кнопок главного меню
class MainMenu:
    # Главное меню
    def Main1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == 'Главное меню' or message.text == 'Вернуться':
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
    # Реакия на кнопки главного меню
    def Main2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser, continue_polling
        # if continue_polling == False:
        #     bot.polling()
        #     continue_polling == True
        if message.text == 'Новая заявка':
            ActiveUser[message.chat.id]['nt'] = 1
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Введите ИНН клиента.',
                reply_markup=buttons.Buttons(['Отмена'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, NewTask.nt1)
        elif message.text == 'Обновить список заявок':
            daterep = str(datetime.now().strftime("%d.%m.%Y"))
            report.rep(message, daterep, 0, 1, 1, 0, 0)
        elif message.text == 'Мои заявки':
            daterep = str(datetime.now().strftime("%d.%m.%Y"))
            report.rep(message, daterep, 0, 1, 0, 1, 0, message.chat.id, 1)
        elif message.text == 'Список заявок':
            ActiveUser[message.chat.id]['filter'] = {
                'from': '01.01.2000 00:00',
                'to': '31.12.2100 23:59',
                'added': 1,
                'confirmed': 1,
                'done': 0,
                'canceled': 0,
                'justmy': 0
            }
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(buttons.buttonslist(ActiveUser[message.chat.id]['filter']))
            )
            if message.message_id is not None:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == '/start':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == 'Написать всем':
            bot.send_message(
                message.chat.id,
                'Напишите Ваше сообщение и оно будет разослано всем.\nчтобы вернуться в главное меню нажмите [Главное меню]',
                reply_markup=buttons.Buttons(['Главное меню'])
            )
            if message.message_id is not None:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            bot.register_next_step_handler(message, allchats.chat1)
        elif message.text == 'Дневной отчет':
            bot.send_message(
                message.chat.id,
                'Выберите какой отчет Вам нужен\nПоказать все не выполненные заявки, или показать итоги дня.',
                reply_markup=buttons.Buttons(['Заявки у мастеров', 'Итоги дня'])
            )
            if message.message_id is not None:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, report.reportall)
        elif message.text == 'Редактировать контрагента':
            contragents = db.select_table('Contragents', ['id', 'cname'])
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Введите ИНН клиента.',
                reply_markup=buttons.Buttons(['Отмена'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, editcont.ec1)
        elif message.text == 'Карта':
            markup = types.InlineKeyboardMarkup()
            button = types.InlineKeyboardButton(text='Открыть карту', url='http://81.200.149.148/map.html')
            markup.add(button)
            bot.send_message(
                message.chat.id,
                'Вы можете посмотреть все теущие заявки за сегодня, на карте',
                reply_markup=markup
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text.isdigit() or (len(message.text.split()) > 1 and message.text.split()[1].isdigit()):
            if message.text.isdigit():
                taskid = message.text
            elif message.text.split()[1].isdigit():
                taskid = message.text.split()[1]
            task = db.get_record_by_id('Tasks', taskid)
            tasks = functions.listgen([task], [0, 1, 3, 4, 6], 1)
            if task is not None:
                bot.send_message(
                    message.chat.id,
                    tasks[0],
                    reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]])
                )
                ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                    message.chat.id,
                    'Выберите операцию.',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
                )
            bot.register_next_step_handler(message, MainMenu.Main2)
        else:
            bot.register_next_step_handler(message, MainMenu.Main2)
# Редактирование контрагента
class editcont():
    # Поиск контрагента по ИНН и генераия основной формы def editcontragent(message)
    def ec1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == 'Отмена':
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text.split()[0].isdigit() or message.text.split()[1].isdigit():
            if message.text.split()[0].isdigit():
                inn = message.text.split()[0]
            else:
                inn = message.text.split()[1]
            ActiveUser[message.chat.id]['inn'] = inn
            print(inn)
            client = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['inn'])
            ActiveUser[message.chat.id]['contold'] = client
            ActiveUser[message.chat.id]['contnew'] = []
            for line in client:
                if line is None:
                    ActiveUser[message.chat.id]['contnew'].append(None)
                else:
                    ActiveUser[message.chat.id]['contnew'].append(line)
            if client is not None:
                editcontragent(message)
                bot.register_next_step_handler(message, editcont.ec2)
            else:
                bot.send_message(
                    message.chat.id,
                    'Контрагент не найден.',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
                )
                bot.register_next_step_handler(message, MainMenu.Main2)
        else:
            contragents = db.select_table('Contragents', ['id', 'cname'])
            bot.send_message(
                message.chat.id,
                'Ошибка ввода!\nВведите ИНН или выберите из списка',
                reply_markup=buttons.Buttons(functions.listgen(contragents, [0, 1], 2), 1, 1)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, editcont.ec1)
    # Реакция на нажатие кнопок в меню редактирования
    def ec2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == 'Сохранить':
            print(ActiveUser[message.chat.id]['contnew'])
            db.update_records(
                'Contragents',
                [
                    'id',
                    'cname',
                    'cadr',
                    'cperson',
                    'cphone',
                    'ds',
                    'contract'
                ],
                ActiveUser[message.chat.id]['contnew'],
                'id',
                ActiveUser[message.chat.id]['contold'][0]
            )
            bot.send_message(
                message.chat.id,
                'Данные изменены.\nВыберите действие',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == 'Отмена':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == 'ТИП':
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                f'Введите новое значение ({message.text})',
                reply_markup=buttons.Buttons(['Разовый', 'Долгосрочный', 'Физ. лицо'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, editcont.TYPE)
        elif message.text == 'АДРЕС':
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Введите новый адрес или отправьте локацию.',
                reply_markup=buttons.clearbuttons()
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, CADR1)
        elif message.text == 'ЛОКАЦИИ':
            # ИЗМЕНЕНИЕ ЛОКАЦИЙ КОНТРАГЕНТА
            sendlocations(ActiveUser[message.chat.id]['inn'], message)
            locs = db.select_table_with_filters('Locations', {'inn': ActiveUser[message.chat.id]['inn']})
            if len(locs) == 0:
                bot.send_message(
                    message.chat.id,
                    'Для выбранного контрагента не указаны локации. Добавьте новые\nОтправьте локацию',
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, newlocation)
            else:
                bot.send_message(
                    message.chat.id,
                    'Вы можете добавить локацию',
                    reply_markup=buttons.Buttons(['Добавить', 'Назад'])
                )
            bot.register_next_step_handler(message, editcont.locations1)
        else:
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                f'Введите новое значение ({message.text})',
                reply_markup=buttons.clearbuttons()
            )
            if message.text == 'ИНН':
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.register_next_step_handler(message, editcont.INN)
            elif message.text == 'НАИМЕНОВАНИЕ':
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.register_next_step_handler(message, editcont.CNAME)
            elif message.text == 'КОНТАКТНОЕ ЛИЦО':
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.register_next_step_handler(message, editcont.CPERSON)
            elif message.text == 'ТЕЛЕФОН':
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.register_next_step_handler(message, editcont.CPHONE)
            elif message.text == 'ДОГОВОР':
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.register_next_step_handler(message, editcont.CCONTRACT)
    # ИНН
    def INN(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text.isdigit():
            ActiveUser[message.chat.id]['contnew'][0] = message.text
            editcontragent(message)
            bot.register_next_step_handler(message, editcont.ec2)
        else:
            bot.send_message(
                message.chat.id,
                'Не верно указан ИНН! \nПовторите попытку',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, editcont.INN)
    # Наименование организаии
    def CNAME(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['contnew'][1] = message.text
        editcontragent(message)
        bot.register_next_step_handler(message, editcont.ec2)
    # Тип договора разовый или долгосрочный
    def TYPE(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == 'Разовый':
            ActiveUser[message.chat.id]['contnew'][5] = 1
        elif message.text == 'Долгосрочный':
            ActiveUser[message.chat.id]['contnew'][5] = 2
        elif message.text == 'Физ. лицо':
            ActiveUser[message.chat.id]['contnew'][5] = 3
        editcontragent(message)
        bot.register_next_step_handler(message, editcont.ec2)
    # Контактное лио
    def CPERSON(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['contnew'][3] = message.text
        editcontragent(message)
        bot.register_next_step_handler(message, editcont.ec2)
    # Контактный телефон
    def CPHONE(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['contnew'][4] = message.text
        editcontragent(message)
        bot.register_next_step_handler(message, editcont.ec2)
    # Номер и дата договора (если долгосрочный)
    def CCONTRACT(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['contnew'][6] = message.text
        editcontragent(message)
        bot.register_next_step_handler(message, editcont.ec2)
    # Меню и список локаций
    def locations1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == 'Добавить':
            bot.send_message(
                message.chat.id,
                'Отправьте локацию',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, newlocation)
        elif message.text == 'Назад':
            editcontragent(message)
            bot.register_next_step_handler(message, editcont.ec2)
        else:
            print('пропуск')
    # Редактирование выбранной локации
    def locations2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == 'Локацию':
            bot.send_message(
                message.chat.id,
                'Отправьте новую локацию.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, editcontlocation1)
        elif message.text == 'Название':
            bot.send_message(
                message.chat.id,
                'Укажите новое название локации.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, editcont.locations3)
        elif message.text == 'Удалить':
            locationtodelete = db.get_record_by_id('Locations', ActiveUser[message.chat.id]['curlocation'])[2]
            Contrlocation = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['inn'])[1]
            bot.send_message(
                message.chat.id,
                f'Удалить локацию {locationtodelete} у {Contrlocation}?',
                reply_markup=buttons.Buttons(['Да','Нет'])
            )
            bot.register_next_step_handler(message, editcont.locations4)
        elif message.text == 'Отмена':
            editcontragent(message)
            bot.register_next_step_handler(message, editcont.ec2)
    # Сохранение имени новой локации
    def locations3(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        db.update_records(
            'Locations',
            ['name'],
            [message.text],
            'id',
            ActiveUser[message.chat.id]['curlocation']
        )
        bot.send_message(
            message.chat.id,
            'Название изменено.\nЧто вы хотите изменить?',
            reply_markup=buttons.Buttons(['Локацию','Название','Удалить', 'Отмена'])
        )
        bot.register_next_step_handler(message, editcont.locations2)
    # Удаление локации
    def locations4(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == 'Да':
            db.delete_record('Locations', 'id', ActiveUser[message.chat.id]['curlocation'])
            bot.send_message(
                message.chat.id,
                'Локация удалена.',
                reply_markup=buttons.clearbuttons()
            )
            editcontragent(message)
            bot.register_next_step_handler(message, editcont.ec2)
        elif message.text == 'Нет':
            bot.send_message(
                message.chat.id,
                'Удаление отменено.\nЧто вы хотите изменить?',
                reply_markup=buttons.Buttons(['Локацию','Название','Удалить', 'Отмена'])
            )
            bot.register_next_step_handler(message, editcont.locations2)
        else:
            locationtodelete = db.get_record_by_id('Locations', ActiveUser[message.chat.id]['curlocation'])[2]
            Contrlocation = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['inn'])[1]
            bot.send_message(
                message.chat.id,
                f'Вы не подтвердили удаление.\nУдалить локацию {locationtodelete} у {Contrlocation}?',
                reply_markup=buttons.Buttons(['Да','Нет'])
            )
            bot.register_next_step_handler(message, editcont.locations4)
# основная форма рдактирования контрагента
def editcontragent(message):
    try:
        bot.delete_message(chat_id=ActiveUser[message.chat.id]['edcon'].chat.id, message_id=ActiveUser[message.chat.id]['edcon'].message_id)
    except:
        pass
    mess = "НАИМЕНОВАНИЕ:\n" + str(ActiveUser[message.chat.id]['contnew'][1])
    mess = mess + '\n\n' + "ИНН:\n" + str(ActiveUser[message.chat.id]['contnew'][0])
    if ActiveUser[message.chat.id]['contnew'][5] == 1:
        mess = mess + '\n\n' + "ТИП:\n" + 'Разовый'
    elif ActiveUser[message.chat.id]['contnew'][5] == 2:
        mess = mess + '\n\n' + "ТИП:\n" + 'Долгосрочный'
    elif ActiveUser[message.chat.id]['contnew'][5] == 3:
        mess = mess + '\n\n' + "ТИП:\n" + 'Физ лицо'
    else:
        mess = mess + '\n\n' + "ТИП:\n" + 'Не указан'
    mess = mess + '\n\n' + "АДРЕС:\n" + str(ActiveUser[message.chat.id]['contnew'][2])
    mess = mess + '\n\n' + "КОНТАКТНОЕ ЛИЦО:\n" + str(ActiveUser[message.chat.id]['contnew'][3])
    mess = mess + '\n\n' + "ТЕЛЕФОН:\n" + str(ActiveUser[message.chat.id]['contnew'][4])
    mess = mess + '\n\n' + "ДОГОВОР:\n" + str(ActiveUser[message.chat.id]['contnew'][6])
    mess = mess + '\n\nЧТО ВЫ ХОТИТЕ ИЗМЕНИТЬ?'
    ActiveUser[message.chat.id]['edcon'] = bot.send_message(
        message.chat.id,
        mess,
        reply_markup=buttons.Buttons(['ИНН', 'НАИМЕНОВАНИЕ', 'ТИП', 'АДРЕС', 'ЛОКАЦИИ', 'КОНТАКТНОЕ ЛИЦО', 'ТЕЛЕФОН', 'ДОГОВОР', 'Сохранить', 'Отмена'], 3)
    )
    return
# Новая заявка
class NewTask:
    # Поиск контрагента по ИНН
    def nt1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['added'] = datetime.now().strftime("%d.%m.%Y %H:%M")
        ActiveUser[message.chat.id]['manager'] = message.chat.id
        ActiveUser[message.chat.id]['status'] = 1
        if message.text == 'Отмена':
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text.split()[0].isdigit() or message.text.split()[1].isdigit():
            if message.text.split()[0].isdigit():
                inn = message.text.split()[0]
            else:
                inn = message.text.split()[1]
            ActiveUser[message.chat.id]['inn'] = inn
            findcont = db.get_record_by_id('Contragents', inn)
            if findcont == None:
                bot.send_message(
                    message.chat.id,
                    'Контрагент с указанным Вами ИНН не найден. \nБудет добавлен новый.\nВыберите тип клиента',
                    reply_markup=buttons.Buttons(['Разовый', 'Долгосрочный', 'Физ. лицо'])
                )
                bot.register_next_step_handler(message, NewTask.NeContr1)
            else:
                client = db.get_record_by_id('Contragents', inn)
                if client[5] is not None and ActiveUser[message.chat.id]['nt'] == 1:
                    bot.send_message(
                        message.chat.id,
                        'Выбран клиент - ' + str(client[1]) + '\nКоротко опишите проблему клиента.',
                        reply_markup=buttons.clearbuttons()
                    )
                    bot.register_next_step_handler(message, NewTask.ntlocation1)
                elif ActiveUser[message.chat.id]['nt'] == 0:
                    ActiveUser[message.chat.id]['changecontrintask'] = inn
                    bot.send_message(
                        message.chat.id,
                        f'Контрагент заявки будет изменен на {str(client[1])}',
                        reply_markup=buttons.Buttons(['Да', 'Нет'])
                    )
                    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                    bot.register_next_step_handler(message, Task.task6)
                else:
                    bot.send_message(
                        message.chat.id,
                        'У выбранного клиента - ' + str(client[1]) + ' не определен тип и договор.\nПожалуйста выберите тип клиента.',
                        reply_markup=buttons.Buttons(['Разовый', 'Долгосрочный', 'Физ. лицо'])
                    )
                    bot.register_next_step_handler(message, NewTask.type1)
        else:
            contragents = db.select_table('Contragents', ['id', 'cname'])
            bot.send_message(
                message.chat.id,
                'Ошибка ввода!\nВведите ИНН или выберите из списка',
                reply_markup=buttons.Buttons(functions.listgen(contragents, [0, 1], 2), 1, 1)
            )
            bot.register_next_step_handler(message, NewTask.nt1)
    # Тип соглашения контрагента если не добавлен в реквизиты контрагента
    def type1(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == 'Разовый':
            ActiveUser[message.chat.id]['ds'] = 1
            bot.send_message(
                message.chat.id,
                'Кратко опишите проблему клиента',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.ntlocation1)
        elif message.text == 'Долгосрочный':
            ActiveUser[message.chat.id]['ds'] = 2
            bot.send_message(
                message.chat.id,
                'Укажите номер и дату договора.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.type2)
        elif message.text == 'Физ. лицо':
            ActiveUser[message.chat.id]['ds'] = 3
            bot.send_message(
                message.chat.id,
                'Кратко опишите проблему клиента',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.ntlocation1)
        else:
            bot.send_message(
                message.chat.id,
                'Ошибка ввода!\nВыберите тип клиента.',
                reply_markup=buttons.Buttons(['Разовый', 'Долгосрочный', 'Физ. лицо'])
            )
            bot.register_next_step_handler(message, NewTask.type1)
    def type2(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        ActiveUser[message.chat.id]['contract'] = message.text
        db.update_records(
            "Contragents",
            ["ds", "contract"],
            [ActiveUser[message.chat.id]['ds'], ActiveUser[message.chat.id]['contract']],
            "id", ActiveUser[message.chat.id]['inn']
        )
        bot.send_message(
            message.chat.id,
            'Кратко опишите проблему клиента',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, NewTask.ntlocation1)
    # Обработка ошибки ввода ИНН
    def innerror(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == 'Ввести снова':
            contragents = db.select_table('Contragents', ['id', 'cname'])
            bot.send_message(
                message.chat.id,
                'Выберите клиента или введите его ИНН.',
                reply_markup=buttons.Buttons(functions.listgen(contragents, [0, 1], 2))
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, NewTask.nt1)
        elif message.text == 'Главное меню':
            ActiveUser[message.chat.id].clear()
            bot.send_message(
                message.chat.id,
                'Добро пожаловать в систему. Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
    # Добавление нового контрагента
    def NeContr1(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == 'Разовый':
            ActiveUser[message.chat.id]['ds'] = 1
            ActiveUser[message.chat.id]['contract'] = '...'
            bot.send_message(
                message.chat.id,
                'Введите наименование организации.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.NeContr3)
        elif message.text == 'Долгосрочный':
            ActiveUser[message.chat.id]['ds'] = 2
            bot.send_message(
                message.chat.id,
                'Укажите номер и дату договора..',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.NeContr2)
        elif message.text == 'Физ. лицо':
            ActiveUser[message.chat.id]['ds'] = 3
            ActiveUser[message.chat.id]['contract'] = '...'
            bot.send_message(
                message.chat.id,
                'Введите Ф.И.О. клиента.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.NeContr3)
        else:
            bot.send_message(
                message.chat.id,
                'Ошибка ввода!\nВыберите тип клиента.',
                reply_markup=buttons.Buttons(['Разовый', 'Долгосрочный', 'Физ. лицо'])
            )
            bot.register_next_step_handler(message, NewTask.NeContr1)
    def NeContr2(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        ActiveUser[message.chat.id]['contract'] = message.text
        bot.send_message(
            message.chat.id,
            'Введите наименование организации.',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, NewTask.NeContr3)
    def NeContr3(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        ActiveUser[message.chat.id]['cname'] = message.text
        bot.send_message(
            message.chat.id,
            'Укажите адрес клиента или отправьте локацию.',
            reply_markup=buttons.clearbuttons()
        )

        if ActiveUser[message.chat.id]['ds'] == 3:
            bot.register_next_step_handler(message, NeContr5)

        else:
            bot.register_next_step_handler(message, NeContr4)
    def NeContr6(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['cphone'] = message.text
        ActiveUser[message.chat.id]['mess'] = 'Подтвердите информацию:\n\n'
        if ActiveUser[message.chat.id]['ds'] == 1:
            ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + 'Разовый\n'
            ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + '\nНаименование организации: ' + ActiveUser[message.chat.id]['cname']
            ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + '\nКонтактное лицо: ' + ActiveUser[message.chat.id]['cperson']
        elif ActiveUser[message.chat.id]['ds'] == 2:
            ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + 'Долгосрочный\n'
            ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + '\nНаименование организации: ' + ActiveUser[message.chat.id]['cname']
            ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + '\nДоговор: ' + ActiveUser[message.chat.id]['contract']
            ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + '\nКонтактное лицо: ' + ActiveUser[message.chat.id]['cperson']
        elif ActiveUser[message.chat.id]['ds'] == 3:
            ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + 'Физ. лицо\n'
            ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + '\nФ И О: ' + ActiveUser[message.chat.id]['cname']
        ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + '\nАдрес: ' + ActiveUser[message.chat.id]['cadr']
        ActiveUser[message.chat.id]['mess'] = ActiveUser[message.chat.id]['mess'] + '\nТелефон: ' + ActiveUser[message.chat.id]['cphone']
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]['mess'],
            reply_markup=buttons.Buttons(['Да', 'Нет'])
        )
        bot.register_next_step_handler(message, NewTask.NeContr7)
    def NeContr7(message):
        if message.text == 'Да':
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
            global ActiveUser
            contragent = [
                ActiveUser[message.chat.id]['inn'],
                ActiveUser[message.chat.id]['cname'],
                ActiveUser[message.chat.id]['cadr'],
                ActiveUser[message.chat.id]['cperson'],
                ActiveUser[message.chat.id]['cphone'],
                ActiveUser[message.chat.id]['ds'],
                ActiveUser[message.chat.id]['contract']
            ]
            db.insert_record('Contragents', contragent)
            if ActiveUser[message.chat.id]['nt'] == 0:
                ActiveUser[message.chat.id]['changecontrintask'] = ActiveUser[message.chat.id]['inn']
                client = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['changecontrintask'])
                bot.send_message(
                    message.chat.id,
                    f'Контрагент заявки будет изменен на {str(client[1])}',
                    reply_markup=buttons.Buttons(['Да', 'Нет'])
                )
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.register_next_step_handler(message, Task.task6)
            elif ActiveUser[message.chat.id]['nt'] == 1:
                bot.send_message(
                    message.chat.id,
                    'Кратко опишите проблему клиента',
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, NewTask.ntlocation1)
        elif message.text == 'Нет':
            bot.send_message(
                message.chat.id,
                'Контрагент не добавлен.\nВыберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        else:
            bot.send_message(
                message.chat.id,
                'Ошибка ввода!\n' + ActiveUser[message.chat.id]['mess'],
                reply_markup=buttons.Buttons(['Да', 'Нет'])
            )
            bot.register_next_step_handler(message, NewTask.NeContr7)
    # Выбор локации
    def ntlocation1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['task'] = message.text
        locations = db.select_table_with_filters('Locations', {'inn': ActiveUser[message.chat.id]['inn']})
        clocations = ['Пропустить']
        if len(locations) > 0:
            for i in locations:
                line = str(i[0]) + ' ' + str(i[2])
                clocations.append(line)
            clocations.append('Добавить филиал')
            bot.send_message(
                message.chat.id,
                'Выберите филиал',
                reply_markup=buttons.Buttons(clocations)
            )
        else:
            clocations.append('Добавить филиал')
            bot.send_message(
                message.chat.id,
                'У выбранного контрагента нет назначенных локаций!\nДобавьте новую.',
                reply_markup=buttons.Buttons(clocations)
            )
        bot.register_next_step_handler(message, NewTask.ntlocation2)
    # Проверка нажатия на кнопки выбора локаций
    def ntlocation2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == 'Пропустить':
            ActiveUser[message.chat.id]['location'] = None
            conf(message)
            bot.register_next_step_handler(message, NewTask.nt3)
        elif message.text == 'Добавить филиал':
            bot.send_message(
                message.chat.id,
                'Отправьте локацию',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, newlocationintask1)
        elif len(message.text.split()) > 0 and message.text.split()[0].isdigit():
            if message.text.split()[0].isdigit():
                ActiveUser[message.chat.id]['location'] = int(message.text.split()[0])
                conf(message)
                bot.register_next_step_handler(message, NewTask.nt3)
            else:
                bot.send_message(
                    message.chat.id,
                    'Ошибка вы не выбрали локацию.\nВыберите локацию или добавьте новую.',
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, NewTask.ntlocation1)
        else:
            bot.send_message(
                message.chat.id,
                'Ошибка вы не выбрали локацию.\nВыберите локацию или добавьте новую.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.ntlocation1)  
    # Добавление новой заявки в базу данных
    def nt3(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == 'Да':
            task = [
                None,
                ActiveUser[message.chat.id]['added'],
                ActiveUser[message.chat.id]['manager'],
                ActiveUser[message.chat.id]['inn'],
                ActiveUser[message.chat.id]['task'],
                None,
                None,
                None,
                None,
                None,
                None,
                ActiveUser[message.chat.id]['status'],
                ActiveUser[message.chat.id]['location']
            ]
            db.insert_record('Tasks',task)
            tid = db.get_last_record('Tasks')[0]
            sendtoall(functions.curtask(tid), buttons.buttonsinline([['Принять', 'confirm ' + str(tid)], ['Назначить', 'set ' + str(tid)]]), message.chat.id, 1)
            bot.send_message(
                message.chat.id,
                'Заявка успешно зарегистрирована.',
                reply_markup=buttons.Buttons(['Главное меню'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main1)
        elif message.text == 'Нет':
            bot.send_message(
                message.chat.id,
                'Новая заявка удалена.',
                reply_markup=buttons.Buttons(['Главное меню'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main1)
        else:
            bot.send_message(
                message.chat.id,
                'Сначала подтвердите сохранение.\nСохранить заявку?',
                reply_markup=buttons.Buttons(['Да', 'Нет'])
            )
            bot.register_next_step_handler(message, NewTask.nt3)
# сообщение для подтверждения заявки
def conf(message):
    confmes = 'Подтвердите заявку. \nЗаявка от: '
    confmes = confmes + ActiveUser[message.chat.id]['added']
    record = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['inn'])
    if ActiveUser[message.chat.id]['location'] is not None:
        location = db.get_record_by_id('Locations', ActiveUser[message.chat.id]['location'])[2]
    else:
        location = ''
    confmes = confmes + '\nКлиент: ' + (record[1] if record[1] is not None else '') + (f" {location}" if ActiveUser[message.chat.id]['location'] is not None else '')
    confmes = confmes + '\nТекст заявки: ' + ActiveUser[message.chat.id]['task']
    confmes = confmes + '\nАдрес: ' + (record[2] if record[2] is not None else '')
    confmes = confmes + '\nКонтактное лицо: ' + (record[3] if record[3] is not None else '')
    confmes = confmes + '\nКонтактный номер: ' + (record[4] if record[4] is not None else '')
    bot.send_message(
        message.chat.id,
        confmes,
        reply_markup=buttons.Buttons(['Да', 'Нет'])
    )
    return
# выбранная заявка и действия
class Task:

    def task1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser, continue_polling
        if message.text == 'Принять':
            if db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[11] != 1:
                bot.send_message(
                    message.chat.id,
                    "Вы не можете принять эту заявку!",
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
                )
                # continue_polling = True
                bot.register_next_step_handler(message, MainMenu.Main2)
            db.update_records(
                'Tasks',
                [
                    'confirmed',
                    'master',
                    'status'
                ], [
                    datetime.now().strftime("%d.%m.%Y %H:%M"),
                    message.chat.id, 2
                ],
                'id',
                ActiveUser[message.chat.id]['task']
            )
            tk = functions.curtask(ActiveUser[message.chat.id]['task'])
            mes = str(db.get_record_by_id('Users', message.chat.id)[2]) + ' ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + '\nПринял заявку:\n\n' + tk
            mark = ''
            exn = message.chat.id
            if sendedmessages is not None:
                for line in sendedmessages:
                    try:
                        bot.delete_message(line[0], line[1])
                    except Exception as e:
                        logging.error(e)
            sendtoall(mes, mark, exn)
            bot.send_message(
                message.chat.id,
                'Вы приняли заявку.\n\nВыберите операцию',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # continue_polling = True
            # bot.register_next_step_handler(message, MainMenu.Main2) 
        elif message.text == 'Дополнить':
            bot.send_message(
                message.chat.id,
                'Напишите что вы хотели дополнить...',
                reply_markup=buttons.clearbuttons()
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, Task.task5)
        elif message.text == 'Переназначить' or message.text == 'Назначить':
            users = db.select_table('Users')
            bot.send_message(
                message.chat.id,
                'Выберите мастера...',
                reply_markup=buttons.Buttons(functions.listgen(users, [0, 1, 2], 3), 1)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, Task.task4)
        elif message.text == 'Выполнено':
            manager = str(db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[6])
            if manager == str(message.chat.id):
                db.update_records(
                    'Tasks',[
                        'done',
                        'status'
                    ],[
                        datetime.now().strftime("%d.%m.%Y %H:%M"),
                        3
                    ],
                    'id',
                    ActiveUser[message.chat.id]['task']
                )
                tk = functions.curtask(ActiveUser[message.chat.id]['task'])
                mes = str(db.get_record_by_id('Users', message.chat.id)[2]) + ' ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + '\nВыполнил заявку:\n\n' + tk
                mark = ''
                exn = message.chat.id
                sendtoall(mes, mark, exn)
                bot.send_message(
                    message.chat.id,
                    'Вы завершили заявку.',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
                )
                # continue_polling = True
                # bot.register_next_step_handler(message, MainMenu.Main2) 
        elif message.text == 'Отказаться от заявки':
            manager = str(db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[6])
            if manager == str(message.chat.id):
                confdate = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[5]
                db.update_records(
                    'Tasks',
                    [
                        'more',
                        'master',
                        'status'
                    ], [
                        'Мастер ' + str(db.get_record_by_id('Users', message.chat.id)[2]) + ' ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + ' принял заявку ' + str(confdate) + '.\n ' + str(datetime.now().strftime("%d.%m.%Y %H:%M")) + 'отказался от выполнения',
                        '',
                        1
                    ],
                    'id',
                    ActiveUser[message.chat.id]['task']
                )
                tk = functions.curtask(ActiveUser[message.chat.id]['task'])
                mes = 'Пользователь ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + 'Отказался от заявки:\n\n' + tk
                mark = ''
                exn = message.chat.id
                sendtoall(mes, mark, exn)
                bot.send_message(
                    message.chat.id,
                    'Вы отказались от заявки.',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
                )
                # continue_polling = True
                # bot.register_next_step_handler(message, MainMenu.Main2) 
            else:
                master = db.get_record_by_id('Users', manager)[1]
                bot.send_message(
                    message.chat.id,
                    'Вы не можете отказаться от этой заявки, так как она не Ваша.\nЗаявку принял ' + str(master),
                    reply_markup=buttons.Buttons(['Главное меню'])
                )
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.register_next_step_handler(message, MainMenu.Main1)
        elif message.text == 'Отменить заявку':
            manager = str(db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[2])
            bot.send_message(
                message.chat.id,
                'Вы уверены, что хотите отменить заявку?',
                reply_markup=buttons.Buttons(['Да', 'Нет'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, Task.task2)
        elif message.text == 'Назад':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # continue_polling = True
            # bot.register_next_step_handler(message, MainMenu.Main2) 
        elif message.text == 'Изменить контрагента':
            bot.send_message(
                message.chat.id,
                'введите ИНН контрагента',
                reply_markup=buttons.clearbuttons()
            )
            ActiveUser[message.chat.id]['nt'] = 0
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, NewTask.nt1)
        elif message.text == 'Изменить текст заявки':
            bot.send_message(
                message.chat.id,
                'Введите новый текст заявки.\n\n‼️ ВНИМАНИЕ ‼️\nУчтите что старый текст будет заменен новым поэтому скопируйте старый и отредактируйте.',
                reply_markup=buttons.clearbuttons()
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, Task.task7_1)
        elif message.text == 'Локация':
            print('Локация')
            location = db.get_record_by_id('Locations', db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[12])
            if location is not None:
                loc = types.Location(location[4], location[3])
                bot.send_location(message.chat.id, loc.latitude, loc.longitude)
                bot.send_message(
                    message.chat.id,
                    'Выберите операцию',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
                )
                # continue_polling = True
                # bot.register_next_step_handler(message, MainMenu.Main2) 
            else:
                bot.send_message(
                    message.chat.id,
                    'Прошу прощения но указанная локаия либо не была добавлена, или была удалена.\nВыберите операцию',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
                )
                # continue_polling = True
                # bot.register_next_step_handler(message, MainMenu.Main2) 
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        # continue_polling = True

    def task2(message):
        global ActiveUser, continue_polling
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == 'Да':
            bot.send_message(
                message.chat.id,
                'Пожалуйста укажите причину отмены заявки.',
                reply_markup=buttons.clearbuttons()
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, Task.task3)
        elif message.text == 'Нет':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # continue_polling = True
            # bot.register_next_step_handler(message, MainMenu.Main2) 

    def task3(message):
        global ActiveUser, continue_polling
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        db.update_records(
            'Tasks',[
                'canceled',
                'userc',
                'more',
                'status'
            ],[
                datetime.now().strftime("%d.%m.%Y %H:%M"),
                message.chat.id,
                message.text,
                4
            ],
            'id',
            ActiveUser[message.chat.id]['task']
        )
        tk = functions.curtask(ActiveUser[message.chat.id]['task'])
        mes = str(db.get_record_by_id('Users', message.chat.id)[2]) + ' ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + '\nОтменил заявку:\n\n' + tk + '\n\nПРИЧИНА:\n' + message.text
        mark = ''
        exn = message.chat.id
        sendtoall(mes, mark, exn)
        bot.send_message(
            message.chat.id,
            'Заявка отменена\n\nВыберите операцию.',
            reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
        )
        # continue_polling = True
        # bot.register_next_step_handler(message, MainMenu.Main2)

    def task4(message):
        global ActiveUser, continue_polling
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text.split()[1] is None:
            users = db.select_table('Users')
            bot.send_message(
                message.chat.id,
                'Выберите мастера...',
                reply_markup=buttons.Buttons(functions.listgen(users, [0, 1, 2], 3), 1)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, Task.task4)
        else:
            userm = message.text.split()[1]
            db.update_records(
                'Tasks',
                [
                    'confirmed',
                    'master',
                    'status'
                ], [
                    datetime.now().strftime("%d.%m.%Y %H:%M"),
                    userm, 2
                ],
                'id',
                ActiveUser[message.chat.id]['task']
            )
            if sendedmessages is not None:
                for line in sendedmessages:
                    try:
                        bot.delete_message(line[0], line[1])
                    except Exception as e:
                        logging.error(e)
            tk = functions.curtask(ActiveUser[message.chat.id]['task'])
            mes = str(db.get_record_by_id('Users', userm)[2]) + ' ' + str(db.get_record_by_id('Users', userm)[1]) + '\nбыл назначен исполнителем заявки:\n\n' + tk
            exn = message.chat.id
            sendtoall(mes, '', exn)
            bot.send_message(
                message.chat.id,
                'Мастер назначен.\n\nВыберите операцию',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # continue_polling = True
            # bot.register_next_step_handler(message, MainMenu.Main2)

    def task5(message):
        global ActiveUser, continue_polling
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        tasktext = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[4]
        db.update_records(
            'Tasks',
            ['task'],
            [tasktext + '\n\n ' + username + ' дополнил(а) заявку...\n' + message.text],
            'id',
            ActiveUser[message.chat.id]['task']
        )
        tk = functions.curtask(ActiveUser[message.chat.id]['task'])
        mes = str(db.get_record_by_id('Users', message.chat.id)[2]) + ' ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + '\n дополнил(а) заявку:\n\n' + tk
        mark = ''
        exn = message.chat.id
        sendtoall(mes, mark, exn)
        if sendedmessages is not None:
            for line in sendedmessages:
                try:
                    bot.delete_message(line[0], line[1])
                except Exception as e:
                    logging.error(e)
        bot.send_message(
            message.chat.id,
            'Заявка дополнена.\n\nВыберите операцию',
            reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
        )
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        # continue_polling = True
        # bot.register_next_step_handler(message, MainMenu.Main2)

    def task6(message):
        global ActiveUser, continue_polling
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == 'Да':
            db.update_records(
                'Tasks',
                ['contragent'],
                [ActiveUser[message.chat.id]['changecontrintask']],
                'id',
                ActiveUser[message.chat.id]['task']
            )
            client = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['changecontrintask'])[1]
            tk = functions.curtask(ActiveUser[message.chat.id]['task'])
            mes = str(db.get_record_by_id('Users', message.chat.id)[2]) + ' ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + '\n Изменил(а) клиента в заявке:\n\n' + tk
            mark = ''
            sendtoall(mes, mark, message.chat.id)
            bot.send_message(
                message.chat.id,
                f'Клиент в заявке изменен на {client}.\n\nВыберите операцию',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # continue_polling = True
            # bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == 'Нет':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # continue_polling = True
            # bot.register_next_step_handler(message, MainMenu.Main2)
        else:
            bot.send_message(
                message.chat.id,
                'Неверная команда',
                reply_markup=buttons.Buttons(['Да', 'Нет'])
            )
            bot.register_next_step_handler(message, Task.task6)

    def task7_1(message):
        global ActiveUser, continue_polling
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        taskt = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[4]
        ActiveUser[message.chat.id]['newtasktext'] = message.text
        bot.send_message(
            message.chat.id,
            f'Текст заявку будет изменен с:\n{taskt}\nНа:\n{message.text}\n\n Подтвердите информацию...',
            reply_markup=buttons.Buttons(['Да','Нет'])
        )
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.register_next_step_handler(message, Task.task7_2)

    def task7_2(message):
        global ActiveUser, continue_polling
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == 'Да':
            print(ActiveUser[message.chat.id]['newtasktext'])
            db.update_records(
                'Tasks',
                ['task'],
                [ActiveUser[message.chat.id]['newtasktext']],
                'id',
                ActiveUser[message.chat.id]['task']
            )
            tk = functions.curtask(ActiveUser[message.chat.id]['task'])
            mes = str(db.get_record_by_id('Users', message.chat.id)[2]) + ' ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + '\n внес изменения в заявку\n\n' + tk
            mark = ''
            sendtoall(mes, mark, message.chat.id)
            bot.send_message(
                message.chat.id,
                'Заявка успешно измненена.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # continue_polling = True
            # bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == 'Нет':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # continue_polling = True
            # bot.register_next_step_handler(message, MainMenu.Main2)
        else:
            bot.send_message(
                message.chat.id,
                'Вы не подтвердили информацию.\nЗаменить старый текст заявки на новый',
                reply_markup=buttons.Buttons(['Да','Нет'])
            )
            bot.register_next_step_handler(message, Task.task7_2)
# фильтр для запроса в базу
def filters(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    messagetouser = 'По каким параметрам формировать список\n'
    if ActiveUser[message.chat.id]['filter']['from'] == '01.01.2000 00:00':
        messagetouser = messagetouser + '📅 Будут показаны все заявки за весь период.\n'
    else:
        messagetouser = messagetouser + '📅 Выбран период:\n c' + str(ActiveUser[message.chat.id]['filter']['from']) + ' по ' + str(ActiveUser[message.chat.id]['filter']['to']) + '\n'
    messagetouser = messagetouser + '\n📍 СТАТУС:\n'
    if ActiveUser[message.chat.id]['filter']['added'] == 1:
        messagetouser = messagetouser + '🔵 Зарегистрированные\n'
    if ActiveUser[message.chat.id]['filter']['confirmed'] == 1:
        messagetouser = messagetouser + '🟡 В работе\n'
    if ActiveUser[message.chat.id]['filter']['done'] == 1:
        messagetouser = messagetouser + '🟢 Завершенные\n'
    if ActiveUser[message.chat.id]['filter']['canceled'] == 1:
        messagetouser = messagetouser + '🔴 Отмененные'
    if ActiveUser[message.chat.id]['filter']['justmy'] == 1:
        messagetouser = messagetouser + '\n👤 Показать только мои заявки.'
    return messagetouser
# список заявок
class TL:
    
    def tl1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == 'Сформировать':
            statuses = []
            if ActiveUser[message.chat.id]['filter']['added'] == 1:
                statuses.append(1)
            if ActiveUser[message.chat.id]['filter']['confirmed'] == 1:
                statuses.append(2)
            if ActiveUser[message.chat.id]['filter']['done'] == 1:
                statuses.append(3)
            if ActiveUser[message.chat.id]['filter']['canceled'] == 1:
                statuses.append(4)
            if ActiveUser[message.chat.id]['filter']['justmy'] == 1:
                tasks = db.select_table_with_filters('Tasks', {'status': statuses, 'master': message.chat.id})
            else:
                tasks = db.select_table_with_filters('Tasks', {'status': statuses})
            if ActiveUser[message.chat.id]['filter']['from'] != '01.01.2000 00:00':
                for line in tasks[:]:
                    if datetime.strptime(ActiveUser[message.chat.id]['filter']['from'], '%d.%m.%Y %H:%M') <= datetime.strptime(line[1], '%d.%m.%Y %H:%M') <= datetime.strptime(ActiveUser[message.chat.id]['filter']['to'], '%d.%m.%Y %H:%M'):
                        logging.info('Запись найдена: Заявка №' + str(line[0]) + ' от ' + str(line[1]))
                    else:
                        tasks.remove(line)
            taskslist = functions.listgen(tasks, [0, 1, 3, 4, 6], 1)
            if len(taskslist) != 0:
                bot.send_message(
                    message.chat.id,
                    '🟥🟥🟥🟥🟥🟥🟥🟥\n‼ ️Список заявок: ‼️\n🟥🟥🟥🟥🟥🟥🟥🟥',
                    reply_markup=buttons.clearbuttons()
                )
                for line in taskslist:
                    taskid = line.split()[2]
                    bot.send_message(
                        message.chat.id,
                        line,
                        reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]])
                    )
                bot.send_message(
                    message.chat.id,
                    '🟥🟥🟥🟥🟥🟥🟥🟥\n‼️ Список заявок ‼️\n🟥🟥🟥🟥🟥🟥🟥🟥\nВыберите операцию.',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
                )
            else:
                bot.send_message(
                    message.chat.id,
                    'Заявок по вашему запросу не найдено.',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
                )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == 'Указать период':
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Укажите дату начала периода.\nДень точка Месяц точка Год полностью\nПРИМЕР: 01.01.2023 или 01,01,2023',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, TL.tl2)
        elif message.text == '⬜️ Зарегистрированные' or message.text == '🔳 Зарегистрированные':
            if ActiveUser[message.chat.id]['filter']['added'] == 1:
                ActiveUser[message.chat.id]['filter']['added'] = 0
            else:
                ActiveUser[message.chat.id]['filter']['added'] = 1
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(buttons.buttonslist(ActiveUser[message.chat.id]['filter']))
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == '⬜️ В работе' or message.text == '🔳 В работе':
            if ActiveUser[message.chat.id]['filter']['confirmed'] == 1:
                ActiveUser[message.chat.id]['filter']['confirmed'] = 0
            else:
                ActiveUser[message.chat.id]['filter']['confirmed'] = 1
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(buttons.buttonslist(ActiveUser[message.chat.id]['filter']))
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == '⬜️ Завершенные' or message.text == '🔳 Завершенные':
            if ActiveUser[message.chat.id]['filter']['done'] == 1:
                ActiveUser[message.chat.id]['filter']['done'] = 0
            else:
                ActiveUser[message.chat.id]['filter']['done'] = 1
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(buttons.buttonslist(ActiveUser[message.chat.id]['filter']))
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == '⬜️ Отмененные' or message.text == '🔳 Отмененные':
            if ActiveUser[message.chat.id]['filter']['canceled'] == 1:
                ActiveUser[message.chat.id]['filter']['canceled'] = 0
            else:
                ActiveUser[message.chat.id]['filter']['canceled'] = 1
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(buttons.buttonslist(ActiveUser[message.chat.id]['filter']))
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == '⬜️ Только мои' or message.text == '🔳 Только мои':
            if ActiveUser[message.chat.id]['filter']['justmy'] == 1:
                ActiveUser[message.chat.id]['filter']['justmy'] = 0
            else:
                ActiveUser[message.chat.id]['filter']['justmy'] = 1
                ActiveUser[message.chat.id]['filter']['added'] = 0
                ActiveUser[message.chat.id]['filter']['confirmed'] = 1
                ActiveUser[message.chat.id]['filter']['done'] = 1
                ActiveUser[message.chat.id]['filter']['canceled'] = 0
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(buttons.buttonslist(ActiveUser[message.chat.id]['filter']))
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == 'Отмена':
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)

    def tl2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        m1 = message.text
        m1 = m1.replace(' ', '.')
        m1 = m1.replace(',', '.')
        m = m1.split('.')
        if len(m[0]) == 2 and len(m[1]) == 2 and len(m[2]) == 4 and len(m) == 3:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['filter']['from'] = message.text + ' 00:00'
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Укажите дату конца периода.\nДень точка Месяц точка Год полностью\nПРИМЕР: 01.01.2023 или 01,01,2023',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, TL.tl3)
        else:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'НЕ ВЕРНЫЙ ФОРМАТ!\nУкажите дату начала периода.\nДень точка Месяц точка Год полностью\nПРИМЕР: 01.01.2023 или 01,01,2023',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, TL.tl2)

    def tl3(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if len(message.text.split('.')) == 3 and len(message.text.split('.')[0]) == 2 and len(message.text.split('.')[1]) == 2 and len(message.text.split('.')[2]) == 4 and datetime.strptime(ActiveUser[message.chat.id]['filter']['from'], '%d.%m.%Y %H:%M') < datetime.strptime(message.text + ' 23:00', '%d.%m.%Y %H:%M'):
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['filter']['to'] = message.text + ' 23:00'
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(buttons.buttonslist(ActiveUser[message.chat.id]['filter']))
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif datetime.strptime(ActiveUser[message.chat.id]['filter']['from'], '%d.%m.%Y %H:%M') > datetime.strptime(message.text + ' 23:00', '%d.%m.%Y %H:%M'):
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'УКАЗАННАЯ ВАМИ ДАТА РАНЬШЕ ЧЕМ ДАТА НАЧАЛА ПЕРИОДА!\nУкажите дату конца периода.\nДень точка Месяц точка Год полностью\nПРИМЕР: 01.01.2023 или 01,01,2023',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, TL.tl3)
        else:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'НЕ ВЕРНЫЙ ФОРМАТ!\nУкажите дату конца периода.\nДень точка Месяц точка Год полностью\nПРИМЕР: 01.01.2023 или 01,01,2023',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, TL.tl3)
# общий чат (пересылка сообщения всем пользователям)
class allchats:
    # пересылка пользовательского сообщения всем
    def chat1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос в отправке всем пользователям - {message.text}')
        if message.text == 'Главное меню' or message.text == '/start':
            logging.info('main')
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
        else:
            logging.info('message to all')
            users = db.select_table('Users')
            for user in users:
                try:
                    logging.info(f'sended message to user {user[2]} {user[1]}')
                    if user[0] != message.chat.id:
                        bot.forward_message(user[0], message.chat.id, message.message_id)
                except Exception as e:
                    logging.error(e)
                    pass
            # for user in users:
            #     try:
            #         pinm = bot.forward_message(user[0], message.chat.id, message.message_id)
            #         if message.from_user.id == 65241621 or message.from_user.id == 1669785252:
            #             bot.unpin_chat_message(user[0])
            #             bot.pin_chat_message(user[0], pinm.message_id)
            #         logging.info(f'sent message to user {user[3]} from {user[2]}')
            #     except Exception as e:
            #         logging.error(e)
            #         pass
            bot.register_next_step_handler(message, allchats.chat1)
# отчеты
class report:
    # Запрос в базу с параметрами
    def rep(message, daterep, dr = 1, conf = 0, added = 0, done = 0, canc = 0, master = 0, my = 0):
        donetasks = []
        confirmedtasks = []
        addedtasks = []
        canceledtasks = []
        if done == 1:
            if my == 1:
                filt = {'status': 3, 'master': master}
            else:
                filt = {'status': 3}
            logging.info(f'Запрос в базу на выполненные заявки за {daterep}')
            donetasks = functions.listgen(db.select_table_with_filters('Tasks', filt, ['done'], [daterep+' 00:00'], [daterep+' 23:59']), [0, 1, 3, 4, 6], 1)
        if conf == 1:
            logging.info(f'Запрос в базу на принятые заявки за {daterep}')
            if master == 0:
                filt = {'status': 2}
            else:
                filt = {'status': 2, 'master': master}
            confirmedtasks = functions.listgen(db.select_table_with_filters('Tasks', filt), [0, 1, 3, 4, 6], 1)
            if master != 0 and len(confirmedtasks) == 0:
                bot.send_message(
                    message.chat.id,
                    'У вас нет заявок в работе.',
                    reply_markup=''
                )
        if added == 1:
            logging.info(f'Запрос в базу на зарегистрированные заявки за {daterep}')
            addedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 1}), [0, 1, 3, 4, 6], 1)
        if canc == 1:
            logging.info(f'Запрос в базу на отмененные заявки за {daterep}')
            canceledtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 4}, ['canceled'], [daterep+' 00:00'], [daterep+' 23:59']), [0, 1, 3, 4, 6], 1)
        if len(confirmedtasks) != 0 and len(addedtasks) != 0:
            bot.send_message(
                message.chat.id,
                '🟥🟥🟥🟥🟥🟥🟥🟥\nСписок заявок на сегодня\n🟥🟥🟥🟥🟥🟥🟥🟥',
                reply_markup=''
            )
        if len(donetasks) != 0:
            bot.send_message(
                message.chat.id,
                '🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nВыполненные заявки',
                reply_markup=''
            )
            for line in donetasks:
                taskid = line.split()[2]
                bot.send_message(
                    message.chat.id,
                    line,
                    reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]])
                )
        if len(confirmedtasks) != 0:
            bot.send_message(
                message.chat.id,
                '🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nЗаявки у мастеров',
                reply_markup=''
            )
            for line in confirmedtasks:
                taskid = line.split()[2]
                bot.send_message(
                    message.chat.id,
                    line,
                    reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]])
                )
        if len(addedtasks) != 0:
            bot.send_message(
                message.chat.id,
                '🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nНе принятые заявки',
                reply_markup=''
            )
            for line in addedtasks:
                taskid = line.split()[2]
                bot.send_message(
                    message.chat.id,
                    line,
                    reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]])
                )
        if len(canceledtasks) != 0:
            bot.send_message(
                message.chat.id,
                '🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nОтмененные',
                reply_markup=''
            )
            for line in canceledtasks:
                taskid = line.split()[2]
                bot.send_message(
                    message.chat.id,
                    line,
                    reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]])
                )
        if dr == 1:
            reports = '\nВыполнено - ' + str(len(donetasks)) + '\nНе распределенных - ' + str(len(addedtasks)) + '\nВ работе у мастеров - ' + str(len(confirmedtasks)) + '\nОтменено - ' + str(len(canceledtasks))
            reports = reports + '\n\nКоличество заявок выполненных мастерами:\n\n'
            users = db.select_table('Users')
            usersrep = []
            for i in users:
                tasks = len(db.select_table_with_filters('Tasks', {'master': i[0]}, ['done'], [daterep+' 00:00'], [daterep+' 23:59']))
                usersrep.append([i[2] + ' ' + i[1], tasks])
            sorted_usersrep = sorted(usersrep, key=lambda x: x[1], reverse=True)
            for j in sorted_usersrep:
                if j[1] != 0:
                    reports = reports + '\n' + j[0] + ' - ' + str(j[1])
            bot.send_message(
                message.chat.id,
                'ИТОГИ ДНЯ\n🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺' + reports,
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
        else:
            if len(addedtasks) != 0 and len(confirmedtasks) != 0 and len(donetasks) != 0 and len(canceledtasks) != 0:
                bot.send_message(
                    message.chat.id,
                    '🟥🟥🟥🟥🟥🟥🟥🟥\nСписок заявок\n🟥🟥🟥🟥🟥🟥🟥🟥',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
                )
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.register_next_step_handler(message, MainMenu.Main2)
    # Реакия на нажатие кнопок меню отчетов
    def reportall(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == 'Заявки у мастеров':
            logging.info('план отправлен.')
            users = db.select_table('Users')
            res = ''
            bot.send_message(
                message.chat.id,
                '🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nОТЧЕТ ПО МАСТЕРАМ\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻',
                reply_markup=buttons.clearbuttons()
            )
            tl = db.select_table_with_filters('Tasks', {'status': 1})
            tasks = functions.listgen(tl, [0, 1, 3, 4, 6], 1)
            for task in tasks:
                taskid = task.split()[2]
                bot.send_message(
                    message.chat.id,
                    task,
                    reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]])
                )
            for u in users:
                userid = u[0]
                daterep = str(datetime.now().strftime("%d.%m.%Y"))
                confirmed = db.select_table_with_filters('Tasks', {'status': 2, 'master': userid})
                done = db.select_table_with_filters('Tasks', {'status': 3, 'master': userid}, ['done'], [daterep+' 00:00'], [daterep+' 23:59'])
                canceled = db.select_table_with_filters('Tasks', {'status': 4, 'master': userid}, ['canceled'], [daterep+' 00:00'], [daterep+' 23:59'])
                if len(confirmed) > 0 or len(done) > 0 or len(canceled) > 0:
                    res = res + f'\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\n👤 {u[2]} {u[1]}\n\nЗАЯВКИ В РАБОТЕ:\n'
                    if len(confirmed) > 0:
                        for i in confirmed:
                            contr = db.get_record_by_id('Contragents', i[3])[1]
                            adr = db.get_record_by_id('Contragents', i[3])[2]
                            res = res + f'\n🟡 - №{i[0]} от {i[1]} | {contr}\n{adr}'
                    if len(done) > 0:
                        for j in done:
                            contr = db.get_record_by_id('Contragents', j[3])[1]
                            adr = db.get_record_by_id('Contragents', j[3])[2]
                            res = res + f'\n🟢 - №{j[0]} от {j[1]} | {contr}\n{adr}'
                    if len(canceled) > 0:
                        for k in canceled:
                            contr = db.get_record_by_id('Contragents', k[3])[1]
                            adr = db.get_record_by_id('Contragents', k[3])[2]
                            res = res + f'\n🔴 - №{k[0]} от {k[1]} | {contr}\n{adr}'
                    bot.send_message(
                        message.chat.id,
                        res,
                        reply_markup=buttons.clearbuttons()
                    )
                    res = ''
                else:
                    print('Пустые списки...')
            bot.send_message(
                message.chat.id,
                'Выберите действие',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == 'Итоги дня':
            bot.send_message(
                message.chat.id,
                'Какой день вы хотите увидеть?',
                reply_markup = buttons.Buttons(['Сегодня', 'Другой день'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, report.reportall1)
        elif message.text == 'Отмена':
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Карта', 'Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
    # Итоги дня
    def reportall1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == 'Сегодня':
            try:
                logging.info(f'Формирование отчета для {message.chat.id}')
                daterep = str(datetime.now().strftime("%d.%m.%Y"))
                report.rep(message, daterep, 1, 1, 1, 1, 1)
            except Exception as e:
                logging.error(e)
        elif message.text == 'Другой день':
            bot.send_message(
                message.chat.id,
                'Укажите дату в формате:\nПРИМЕР: 01.01.2023 или 01,01,2023',
                reply_markup = buttons.clearbuttons()
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, report.reportall2)
    def reportall2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        m1 = message.text
        m1 = m1.replace(' ', '.')
        m1 = m1.replace(',', '.')
        m = m1.split('.')
        if len(m[0]) == 2 and len(m[1]) == 2 and len(m[2]) == 4 and len(m) == 3:
            daterep = m1
            try:
                logging.info(f'Формирование отчета для {message.chat.id} За {daterep}')
                report.rep(message, daterep, 1, 1, 1, 1, 1)
            except Exception as e:
                logging.error(e)

@bot.message_handler(content_types=['text', 'location'])
# формирование гугл ссылки на карты по локации для адреса компании
def CADR1(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    if message.content_type == 'location':
        lon, lat = message.location.longitude, message.location.latitude
        url = f'GOOGLE: https://www.google.com/maps/search/?api=1&query={lat},{lon}'
        ActiveUser[message.chat.id]['contnew'][2] = url
    else:
        ActiveUser[message.chat.id]['contnew'][2] = message.text
    editcontragent(message)
    bot.register_next_step_handler(message, editcont.ec2)
# Формирование гугл ссылки на карты по локации для адреса при добавлении нового контрагента
def NeContr4(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    if message.content_type == 'location':
        lon, lat = message.location.longitude, message.location.latitude
        url = f'GOOGLE: https://www.google.com/maps/search/?api=1&query={lat},{lon}\nAPPLE: http://maps.apple.com/maps?ll={lat},{lon}'
        ActiveUser[message.chat.id]['cadr'] = url
    else:
        ActiveUser[message.chat.id]['cadr'] = message.text
    bot.send_message(
        message.chat.id,
        'Кто подал заявку? Укажите имя контактного лица.',
        reply_markup=buttons.clearbuttons()
    )
    bot.register_next_step_handler(message, NeContr5)
def NeContr5(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    if ActiveUser[message.chat.id]['ds'] == 3:
        if message.content_type == 'location':
            lon, lat = message.location.longitude, message.location.latitude
            url = f'GOOGLE: https://www.google.com/maps/search/?api=1&query={lat},{lon}\nAPPLE: http://maps.apple.com/maps?ll={lat},{lon}'
            ActiveUser[message.chat.id]['cadr'] = url
        else:
            ActiveUser[message.chat.id]['cadr'] = message.text
    else:
        ActiveUser[message.chat.id]['cperson'] = message.text
    bot.send_message(
        message.chat.id,
        'Укажите контактный номер телефона для связи с клиентом.',
        reply_markup=buttons.clearbuttons()
    )
    bot.register_next_step_handler(message, NewTask.NeContr6)
# Добавление новой локации в список локаций в редактировании контрагента
def newlocation(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    if message.content_type == 'location':
        ActiveUser[message.chat.id]['lon'], ActiveUser[message.chat.id]['lat'] = message.location.longitude, message.location.latitude
        bot.send_message(
            message.chat.id,
            'Укажите название локации\nНАПРИМЕР:\nФилиал чиланзар или головной офис',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, newlocation1)
    else:
        bot.send_message(
            message.chat.id,
            'Вы должны были отправить локацию.\nОтправьте локацию.',
            reply_markup=buttons.clearbuttons
        )
        bot.register_next_step_handler(message, newlocation)
def newlocation1(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    ActiveUser[message.chat.id]['locationname'] = message.text
    db.insert_record(
        'Locations',
        [
            None,
            ActiveUser[message.chat.id]['inn'],
            ActiveUser[message.chat.id]['locationname'],
            ActiveUser[message.chat.id]['lat'],
            ActiveUser[message.chat.id]['lon']
        ]
    )
    bot.send_message(
        message.chat.id,
        'Локация сохранена.',
        reply_markup=buttons.clearbuttons()
    )
    editcontragent(message)
    bot.register_next_step_handler(message, editcont.ec2)
# Изменение локаии контрагента
def editcontlocation1(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    if message.content_type == 'location':
        lon, lat = message.location.longitude, message.location.latitude
        db.update_records(
            'Locations',
            [
                'lon',
                'lat'
            ],
            [
                lon,
                lat
            ],
            'id',
            ActiveUser[message.chat.id]['curlocation']
        )
        bot.send_message(
            message.chat.id,
            'Локация изменена.\nЧто вы хотите изменить?',
            reply_markup=buttons.Buttons(['Локацию','Название','Удалить', 'Отмена'])
        )
        bot.register_next_step_handler(message, editcont.locations2)
    else:
        bot.send_message(
            message.chat.id,
            'Вы должны были отправить локацию.\nОтправьте локацию.',
            reply_markup=buttons.clearbuttons
        )
        bot.register_next_step_handler(message, newlocation)
# Добавление локации филиала в новой заявке
def newlocationintask1(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    if message.content_type == 'location':
        ActiveUser[message.chat.id]['lon'], ActiveUser[message.chat.id]['lat'] = message.location.longitude, message.location.latitude
        bot.send_message(
            message.chat.id,
            'Укажите название локации\nНАПРИМЕР:\nФилиал чиланзар или головной офис',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, newlocationintask2)
    else:
        bot.send_message(
            message.chat.id,
            'Вы должны были отправить локацию.\nОтправьте локацию.',
            reply_markup=buttons.clearbuttons
        )
        bot.register_next_step_handler(message, newlocationintask1)
def newlocationintask2(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    ActiveUser[message.chat.id]['locationname'] = message.text
    db.insert_record(
        'Locations',
        [
            None,
            ActiveUser[message.chat.id]['inn'],
            ActiveUser[message.chat.id]['locationname'],
            ActiveUser[message.chat.id]['lat'],
            ActiveUser[message.chat.id]['lon']
        ]
    )
    locations = db.select_table_with_filters('Locations', {'inn': ActiveUser[message.chat.id]['inn']})
    clocations = ['Пропустить']
    if len(locations) > 0:
        for i in locations:
            line = str(i[0]) + ' ' + str(i[2])
            clocations.append(line)
        clocations.append('Добавить филиал')
        bot.send_message(
            message.chat.id,
            'Выберите филиал',
            reply_markup=buttons.Buttons(clocations)
        )
    bot.register_next_step_handler(message, NewTask.ntlocation2)

@bot.callback_query_handler(func=lambda call: True)
# реакция на инлайновые кнопки
def callback_handler(call):
    global ActiveUser, sendedmessages, continue_polling
    # bot.stop_polling()
    if call.data.split()[0] == 'tasklist':# Подробности заявки
        status = db.get_record_by_id('Tasks', int(call.data.split()[1]))
        if status[11] == 1:
            markdownt = buttons.Buttons(['Принять', 'Дополнить', 'Назначить', 'Изменить контрагента', 'Изменить текст заявки', 'Локация', 'Отменить заявку', 'Назад'])
        elif status[11] == 2:
            markdownt = buttons.Buttons(['Выполнено', 'Дополнить', 'Отказаться от заявки', 'Переназначить', 'Изменить контрагента', 'Изменить текст заявки', 'Локация', 'Отменить заявку', 'Назад'], 3)
        else:
            markdownt = buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Изменить текст заявки', 'Локация', 'Дневной отчет', 'Написать всем'],3)
        ActiveUser[call.from_user.id]['sentmes'] = bot.send_message(
            call.from_user.id,
            functions.curtask(call.data.split()[1]),
            reply_markup=markdownt
        )
        ActiveUser[call.from_user.id]['task'] = call.data.split()[1]
        bot.register_next_step_handler(call.message, Task.task1)
    elif call.data.split()[0] == 'confirm':# Принятие заявки
        if db.get_record_by_id('Tasks', call.data.split()[1])[11] != 1:
            bot.send_message(
                call.from_user.id,
                "Вы не можете принять эту заявку! ее уже принял " + db.get_record_by_id('Users', db.get_record_by_id('Tasks', ActiveUser[call.from_user.id]['task'])[6])[2] + ' ' + db.get_record_by_id('Users', db.get_record_by_id('Tasks', ActiveUser[call.from_user.id]['task'])[6])[1]
            )
        else:
            db.update_records(
                'Tasks',
                [
                    'confirmed',
                    'master',
                    'status'
                ], [
                    datetime.now().strftime("%d.%m.%Y %H:%M"),
                    call.from_user.id,
                    2
                ],
                'id',
                call.data.split()[1]
            )
            bot.send_message(
                call.from_user.id,
                "Вы приняли заявку..."
            )
            sendtoall(str(db.get_record_by_id('Users', call.from_user.id)[2]) + ' ' + str(db.get_record_by_id('Users', call.from_user.id)[1]) + '\nПринял заявку:\n\n' + functions.curtask(call.data.split()[1]), '', call.from_user.id)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
            continue_polling = True
            # bot.register_next_step_handler(call.message, MainMenu.Main2)
            for line in sendedmessages:
                bot.delete_message(line[0], line[1])
    elif call.data.split()[0] == 'set':# Назначение мастера
        users = db.select_table('Users')
        bot.send_message(
            call.from_user.id,
            'Выберите мастера...',
            reply_markup=buttons.Buttons(functions.listgen(users, [0, 1, 2], 3), 1)
        )
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        ActiveUser[call.from_user.id]['task'] = call.data.split()[1]
        bot.register_next_step_handler(call.message, Task.task4)
    elif call.data.split()[0] == 'location':# Редактирование локации
        ActiveUser[call.from_user.id]['curlocation'] = call.data.split()[1]
        bot.send_message(
            call.from_user.id,
            'Что вы хотите изменить?',
            reply_markup=buttons.Buttons(['Локацию','Название','Удалить', 'Отмена'])
        )
        bot.register_next_step_handler(call.message, editcont.locations2)
    # else:
    #     bot.polling()
        
# Запуск бота
if __name__ == '__main__':
    sendtoall('‼️‼️‼️Сервер бота был перезагружен...‼️‼️‼️\nНажмите кнопку "/start"', buttons.Buttons(['/start']), 0, 0, True)
    thread = threading.Thread(target=asyncio.run, args=(main(),))
    thread.start()
    # bot.polling()
    while True:
        try:
            bot.stop_polling()
            logging.info('остановка пула')
            bot.polling(none_stop=True, interval=0)
            logging.info('запуск пула')
            logging.info()
        except Exception as e:
            logging.error(e)
            time.sleep(5)