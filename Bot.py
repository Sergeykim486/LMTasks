import telebot, logging, time, datetime, asyncio, threading, Classes.functions as functions, Classes.buttons as buttons
from Classes.Selected_task import Task
from datetime import datetime
from Classes.edit_contragent import editcont
from Classes.add_new_task import NewTask
from Classes.reports import report
from Classes.config import ActiveUser, bot, sendedmessages, db
# логи
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# =====================================  ФУНКЦИИ ВЫПОЛНЯЕМЫЕ ПО РАСПИСАНИЮ  =====================================

# Проверка расписания
async def job():
    await schedule_message()
async def schedule_message():
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
                            logging.error(e)
                            pass
                    db.update_records('Tasks', ['status'], [1], 'id', line[0])
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
                    functions.sendtoall(mes, '', 0)
        except Exception as e:
            logging.error(e)
            pass
        now = datetime.now()
        # if now.hour == 8 and now.minute == 0:
        #     await daylyreport.morning()
        if now.hour == 20 and now.minute == 0:
            await daylyreport.evening()
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
        if len(confirmedtasks) != 0 and len(addedtasks) != 0:
            functions.sendtoall('ИТОГИ ДНЯ:\nНа завтра остаются следующие заявки:', '', 0)
        if len(donetasks) != 0:
            functions.sendtoall('Выполненные заявки\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in donetasks:
                taskid = line.split()[2]
                functions.sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        if len(confirmedtasks) != 0:
            functions.sendtoall('Заявки у мастеров\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in confirmedtasks:
                taskid = line.split()[2]
                functions.sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        if len(addedtasks) != 0:
            functions.sendtoall('Не принятые заявки\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in addedtasks:
                taskid = line.split()[2]
                functions.sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        if len(canceledtasks) != 0:
            functions.sendtoall('Отмененные\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻', '', 0)
            for line in canceledtasks:
                taskid = line.split()[2]
                functions.sendtoall(line, buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]]), 0)
        reports = '\nВыполнено - ' + str(len(donetasks)) + '\nНе распределенных - ' + str(len(addedtasks)) + '\nВ работе у мастеров - ' + str(len(confirmedtasks)) + '\nОтменено - ' + str(len(canceledtasks))
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
            for j in sorted_usersrep:
                if j[1] != 0:
                    reports = reports + '\n' + j[0] + ' - ' + str(j[1])
        functions.sendtoall('ИТОГИ ДНЯ\n🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺' + reports, '', 0)

def MenuReactions(message):
    if ActiveUser[message.chat.id]['Pause_main_handler'] == False or ActiveUser[message.chat.id]['Finishedop'] == True:
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = False
        if message.text == '📝 Новая заявка':
            ActiveUser[message.chat.id]['nt'] = 1
            functions.mesdel(message.chat.id, message.message_id)
            ActiveUser[message.chat.id]['Pause_main_handler'] = True
            ActiveUser[message.chat.id]['Finishedop'] = False
            NewTask.nt1(message)
            # time.sleep(10)
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == '🔃 Обновить список заявок':
            daterep = str(datetime.now().strftime("%d.%m.%Y"))
            report.rep(message, daterep, 0, 1, 1, 0, 0)
        elif message.text == '🖨️ Обновить список техники':
            daterep = str(datetime.now().strftime("%d.%m.%Y"))
            report.rep(message, daterep, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)
        elif message.text == '📋 Мои заявки':
            daterep = str(datetime.now().strftime("%d.%m.%Y"))
            report.rep(message, daterep, 0, 1, 0, 1, 0, message.chat.id, 1)
        elif message.text == '📢 Написать всем':
            bot.send_message(
                message.chat.id,
                'Напишите Ваше сообщение и оно будет разослано всем.\nчтобы вернуться в главное меню нажмите [Главное меню]',
                reply_markup=buttons.Buttons(['🏠 Главное меню'])
            )
            if message.message_id != None:
                functions.mesdel(message.chat.id, message.message_id)
            bot.register_next_step_handler(message, allchats.chat1)
        elif message.text == '📈 Отчеты':
            if message.message_id != None:
                functions.mesdel(message.chat.id, message.message_id)
            ActiveUser[message.chat.id]['Pause_main_handler'] = True
            ActiveUser[message.chat.id]['Finishedop'] = False
            report.reportall(message)
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == '✏️ Редактировать контрагента':
            ActiveUser[message.chat.id]['Pause_main_handler'] = True
            ActiveUser[message.chat.id]['Finishedop'] = False
            functions.mesdel(message.chat.id, message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
            editcont.ec1(message)
        elif message.text == '🗺️ Карта':
            markup = telebot.types.InlineKeyboardMarkup()
            button = telebot.types.InlineKeyboardButton(text='Открыть карту', url='http://81.200.149.148/map.html')
            markup.add(button)
            bot.send_message(
                message.chat.id,
                'Вы можете посмотреть все теущие заявки за сегодня, на карте',
                reply_markup=markup
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text != None:
            if message.text.isdigit() or (len(message.text.split()) > 1 and message.text.split()[1].isdigit()):
                if message.text.isdigit():
                    taskid = message.text
                elif message.text.split()[1].isdigit():
                    taskid = message.text.split()[1]
                task = db.get_record_by_id('Tasks', taskid)
                tasks = functions.listgen([task], [0, 1, 3, 4, 6], 1)
                if task != None:
                    bot.send_message(
                        message.chat.id,
                        tasks[0],
                        reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]])
                    )
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
    elif message.text == '/start':
        print('main menu')
        ActiveUser[message.chat.id]['Pause_main_handler'] = False
        bot.send_message(
            message.chat.id,
            'Выберите операцию.',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        bot.register_next_step_handler(message, MainMenu.Main2)
    else:
        print('none')
        bot.register_next_step_handler(message, MainMenu.Main2)

# =====================================  С Т А Р Т   Б О Т А  =====================================

@bot.message_handler(commands=['start'])

# проверка пользователя при первом запуске
def check_user_id(message):
    user_id = message.from_user.id
    global ActiveUser
    try:
        username = db.get_record_by_id('Users', user_id)[2] + ' ' + db.get_record_by_id('Users', user_id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    ActiveUser[user_id] = {'id': user_id}
    ActiveUser[user_id]['Pause_main_handler'] = False
    ActiveUser[user_id]['Finishedop'] = False
    user = db.get_record_by_id('Users', user_id)
    if user is None:
        if user_id == 5390927006:
            bot.send_message(
                user_id,
                "Вы не можете зарегистрироваться.",
                reply_markup=buttons.Buttons(['ok'])
            )
            bot.stop_polling()
        else:
            bot.send_message(
                user_id,
                'Вы не зарегистрированы.',
                reply_markup=buttons.Buttons(['ок'])
            )
        bot.stop_polling()
    else:
        bot.send_message(
            user_id,
            'Выберите операцию.',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        bot.register_next_step_handler(message, MainMenu.Main2)

# =====================================  О С Н О В Н Ы Е   Х Е Н Д Л Е Р Ы  =====================================

@bot.message_handler(func=lambda message: True)

def check_user_id(message):
    user_id = message.from_user.id
    global ActiveUser
    try:
        username = db.get_record_by_id('Users', user_id)[2] + ' ' + db.get_record_by_id('Users', user_id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    ActiveUser[user_id] = {'id': user_id}
    ActiveUser[user_id]['Finishedop'] = True
    ActiveUser[user_id]['Pause_main_handler'] = False
    user = db.get_record_by_id('Users', user_id)
    if user is None:
        if user_id == 5390927006:
            bot.send_message(
                user_id,
                "Вы не можете зарегистрироваться.",
                reply_markup=buttons.Buttons(['ok'])
            )
            bot.stop_polling()
        else:
            bot.send_message(
                user_id,
                'Вы не зарегистрированы.',
                reply_markup=buttons.Buttons(['ок'])
            )
        bot.stop_polling()
    else:
        MenuReactions(message)


# # Регистрация нового пользователя
class Reg:
    # Запрос имени у пользователя
    def reg1(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == '🔑 Регистрация':
            if message.chat.id == 5390927006:
                bot.send_message(
                    message.chat.id,
                    "Вы не можете зарегистрироваться.",
                    reply_markup=buttons.Buttons(['ok'])
                )
                bot.stop_polling()
            bot.send_message(
                message.chat.id,
                'Как Вас зовут (укажите имя)',
            reply_markup=buttons.clearbuttons()
            )
            functions.mesdel(message.chat.id, message.message_id)
            bot.register_next_step_handler(message, Reg.reg2)
        else:
            bot.send_message(
                message.chat.id,
                'Пожалуйста зарегистрируйтесь.',
                reply_markup=buttons.Buttons(['🔑 Регистрация'])
            )
            try:
                functions.mesdel(message.chat.id, message.message_id)
            except Exception as e:
                pass
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
            reply_markup=buttons.Buttons(['✅ Да', '⛔️ Нет'])
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
        if message.text == '✅ Да':
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
                reply_markup=buttons.Buttons(['🏠 Главное меню'])
            )
            functions.mesdel(message.chat.id, message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main1)
        elif message.text == '⛔️ Нет':
            bot.send_message(
                message.chat.id,
                'Пройдите регистрацию повторно.',
                reply_markup=buttons.Buttons(['🔑 Регистрация'])
            )
            bot.register_next_step_handler(message, Reg.reg1)
        else:
            bot.send_message(
                message.chat.id,
                'Вы не подтвердили информацию!\n' + functions.conftext(message, ActiveUser),
                reply_markup=buttons.Buttons(['✅ Да', '⛔️ Нет'])
            )
            functions.mesdel(message.chat.id, message.message_id)
            bot.register_next_step_handler(message, Reg.reg5)

# Главное меню и обработка кнопок главного меню
class MainMenu:
    def Main1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == '🏠 Главное меню' or message.text == 'Вернуться':
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            functions.mesdel(message.chat.id, message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
    # Реакия на кнопки главного меню
    def Main2(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        global ActiveUser
        MenuReactions(message)

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

# общий чат (пересылка сообщения всем пользователям)
class allchats:
    # пересылка пользовательского сообщения всем
    def chat1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос в отправке всем пользователям - {message.text}')
        if message.text == '🏠 Главное меню' or message.text == '/start':
            logging.info('main')
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            functions.mesdel(message.chat.id, message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
        else:
            logging.info('message to all')
            processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
            users = db.select_table('Users')
            for user in users:
                try:
                    # logging.info(f'sended message to user {user[2]} {user[1]}')
                    if user[0] != message.chat.id:
                        bot.forward_message(user[0], message.chat.id, message.message_id)
                except Exception as e:
                    pass
            functions.mesdel(message.chat.id, processing.message_id)
            bot.register_next_step_handler(message, allchats.chat1)

# =====================================  Р Е А К Ц И И   Н А   И Н Л А Й Н О В Ы Е   К Н О П К И  =====================================

@bot.callback_query_handler(func=lambda call: True)
# реакция на инлайновые кнопки
def callback_handler(call):
    global ActiveUser, sendedmessages
    ActiveUser[call.from_user.id]['Pause_main_handler'] = True
    ActiveUser[call.from_user.id]['Finishedop'] = False
    if call.data.split()[0] == 'tasklist':# Подробности заявки
        status = db.get_record_by_id('Tasks', int(call.data.split()[1]))
        if status[11] == 1 or status[11] == 5:
            markdownt = buttons.Buttons(['👍 Принять', '🖊️ Дополнить', '📎 Назначить', '✏️ Изменить текст заявки', '📍 Локация', '🚫 Отменить заявку', '↩️ Назад'])
        elif status[11] == 2 or status[11] == 6:
            markdownt = buttons.Buttons(['✅ Выполнено', '🖊️ Дополнить', '🙅‍♂️ Отказаться от заявки', '📎 Переназначить', '✏️ Изменить текст заявки', '📍 Локация', '🚫 Отменить заявку', '↩️ Назад'], 3)
        else:
            markdownt = buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            ActiveUser[call.from_user.id]['Finishedop'] = True
        ActiveUser[call.from_user.id]['sentmes'] = bot.send_message(
            call.from_user.id,
            functions.curtask(call.data.split()[1]),
            reply_markup=markdownt
        )
        if status[11] != 3:
            ActiveUser[call.from_user.id]['task'] = call.data.split()[1]
            bot.register_next_step_handler(call.message, Task.task1)
        else:
            ActiveUser[call.from_user.id]['Pause_main_handler'] = False
            ActiveUser[call.from_user.id]['Finishedop'] = True
    elif call.data.split()[0] == 'confirm':# Принятие заявки
        processing = bot.send_sticker(call.from_user.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
        if db.get_record_by_id('Tasks', call.data.split()[1])[11] == 5:
            stat = 6
        else:
            stat = 2
        if db.get_record_by_id('Tasks', call.data.split()[1])[11] > 1:
            functions.mesdel(call.from_user.id, processing.message_id)
            bot.send_message(
                call.from_user.id,
                "Вы не можете принять эту заявку! ее уже принял " + db.get_record_by_id('Users', db.get_record_by_id('Tasks', call.data.split()[1])[6])[2] + ' ' + db.get_record_by_id('Users', db.get_record_by_id('Tasks', call.data.split()[1])[6])[1],
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
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
                    stat
                ],
                'id',
                call.data.split()[1]
            )
            functions.sendtoall(str(db.get_record_by_id('Users', call.from_user.id)[2]) + ' ' + str(db.get_record_by_id('Users', call.from_user.id)[1]) + '\nПринял заявку:\n\n' + functions.curtask(call.data.split()[1]), '', call.from_user.id)
            functions.mesdel(call.from_user.id, processing.message_id)
            bot.send_message(
                call.from_user.id,
                "Вы приняли заявку...",
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            functions.deletentm(call.data.split()[1])
        ActiveUser[call.from_user.id]['Pause_main_handler'] = False
        ActiveUser[call.from_user.id]['Finishedop'] = True
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
    else:
        bot.send_message(
            call.message,
            'Ошибка ввода.\nВыберите действие',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        ActiveUser[call.from_user.id]['Pause_main_handler'] = False

# =====================================  Ц И К Л И Ч Е С К И Й   З А П У С К   Б О Т А  =====================================
  
# Запуск бота
if __name__ == '__main__':
    functions.sendtoall('‼️‼️‼️Сервер бота был перезагружен...‼️‼️‼️\nНажмите кнопку "/start"', buttons.Buttons(['/start']), 0, 0, True)
    thread = threading.Thread(target=asyncio.run, args=(main(),))
    thread.start()
    # bot.polling(none_stop=True, interval=0)
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
            logging.info('запуск пула')
        except Exception as e:
            logging.error(e)
            time.sleep(5)