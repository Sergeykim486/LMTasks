import os, config, telebot, functions, buttons, logging, time, pickle, asyncio, threading
from telebot import TeleBot, types
from db import Database
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ActiveUser = {}
sendedmessages = []

dbname = os.path.dirname(os.path.abspath(__file__)) + '/Database/' + 'lmtasksbase.db'
db = Database(dbname)

bot = telebot.TeleBot(config.TOKEN)

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
        await asyncio.sleep(60)

async def main():
    await job()


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


class daylyreport:

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

def check_user_id(message):
    user_id = message.from_user.id
    global ActiveUser
    username = db.get_record_by_id('Users', user_id)[2] + ' ' + db.get_record_by_id('Users', user_id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    ActiveUser[user_id] = {'id': user_id}
    finduser = db.search_record("Users", "id", user_id)

    if len(finduser) == 0:
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
            reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
        )
        bot.register_next_step_handler(message, MainMenu.Main2)

@bot.message_handler(func=lambda message: True)

def check_user_id(message):
    user_id = message.from_user.id
    global ActiveUser
    username = db.get_record_by_id('Users', user_id)[2] + ' ' + db.get_record_by_id('Users', user_id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    ActiveUser[user_id] = {'id': user_id}
    finduser = db.search_record("Users", "id", user_id)

    if len(finduser) == 0:
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
            reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
        )
        bot.register_next_step_handler(message, MainMenu.Main2)


class Reg:

    def reg1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')

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

    def reg2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['FirstName'] = message.text
        bot.send_message(
            message.chat.id,
            'Укажите Вашу фамилию.',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Reg.reg3)

    def reg3(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['LastName'] = message.text
        bot.send_message(
            message.chat.id,
            'Введите Ваш номер телефона в формате (+998 00 000 0000).',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Reg.reg4)

    def reg4(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['PhoneNumber'] = message.text
        bot.send_message(
            message.chat.id,
            functions.conftext(message, ActiveUser),
            reply_markup=buttons.Buttons(['Да', 'Нет'])
        )
        bot.register_next_step_handler(message, Reg.reg5)

    def reg5(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
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


class MainMenu:

    def Main1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        
        if message.text == 'Главное меню' or message.text == 'Вернуться':
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)

    def Main2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser

        if message.text == 'Новая заявка':
            contragents = db.select_table('Contragents', ['id', 'cname'])
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Выберите клиента или введите его ИНН.',
                reply_markup=buttons.Buttons(functions.listgen(contragents, [0, 1], 2), 1, 1)
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
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
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
                reply_markup=buttons.Buttons(['Все', 'Итоги дня'])
            )

            if message.message_id is not None:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

            bot.register_next_step_handler(message, report.reportall)

        elif message.text == 'Редактировать контрагента':
            contragents = db.select_table('Contragents', ['id', 'cname'])
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Выберите клиента или введите его ИНН.',
                reply_markup=buttons.Buttons(functions.listgen(contragents, [0, 1], 2), 1, 1)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, editcont.ec1)
        
        else:
            bot.register_next_step_handler(message, MainMenu.Main2)


class editcont():
    
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
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
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
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
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
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == 'Отмена':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
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
            bot.register_next_step_handler(message, CADR)
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
            
    def CNAME(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['contnew'][1] = message.text
        editcontragent(message)
        bot.register_next_step_handler(message, editcont.ec2)
    
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
    
    # def CADR(message):
    #     username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    #     logging.info(f'{username} Отправил запрос - {message.text}')
    #     global ActiveUser
    #     if message.content_type == types.ContentType.LOCATION:
    #         lon, lat = message.location.longitude, message.location.latitude
    #         url = f'https://www.google.com/maps/search/?api=1&query={lat},{lon}'
    #         ActiveUser[message.chat.id]['contnew'][2] = url
    #     else:
    #         ActiveUser[message.chat.id]['contnew'][2] = message.chat.id
        
    #     editcontragent(message)
    #     bot.register_next_step_handler(message, editcont.ec2)
    
    def CPERSON(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['contnew'][3] = message.text
        editcontragent(message)
        bot.register_next_step_handler(message, editcont.ec2)
    
    def CPHONE(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['contnew'][4] = message.text
        editcontragent(message)
        bot.register_next_step_handler(message, editcont.ec2)
    
    def CCONTRACT(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['contnew'][6] = message.text
        editcontragent(message)
        bot.register_next_step_handler(message, editcont.ec2)
    
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
        reply_markup=buttons.Buttons(['ИНН', 'НАИМЕНОВАНИЕ', 'ТИП', 'АДРЕС', 'КОНТАКТНОЕ ЛИЦО', 'ТЕЛЕФОН', 'ДОГОВОР', 'Сохранить', 'Отмена'], 3)
    )
    return


class NewTask:

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
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
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
                if client[5] is not None:
                    bot.send_message(
                        message.chat.id,
                        'Выбран клиент - ' + str(client[1]) + '\nКоротко опишите проблему клиента.',
                        reply_markup=buttons.clearbuttons()
                    )
                    bot.register_next_step_handler(message, NewTask.nt2)
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
            bot.register_next_step_handler(message, NewTask.nt2)

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
            bot.register_next_step_handler(message, NewTask.nt2)

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
        bot.register_next_step_handler(message, NewTask.nt2)

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
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)

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
            bot.send_message(
                message.chat.id,
                'Кратко опишите проблему клиента',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.nt2)
        elif message.text == 'Нет':
            bot.send_message(
                message.chat.id,
                'Контрагент не добавлен.\nВыберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        else:
            bot.send_message(
                message.chat.id,
                'Ошибка ввода!\n' + ActiveUser[message.chat.id]['mess'],
                reply_markup=buttons.Buttons(['Да', 'Нет'])
            )
            bot.register_next_step_handler(message, NewTask.NeContr7)

    def nt2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        ActiveUser[message.chat.id]['task'] = message.text
        confmes = 'Подтвердите заявку. \n Заявка от: '
        confmes = confmes + ActiveUser[message.chat.id]['added']

        record = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['inn'])
        confmes = confmes + '\nКлиент: ' + (record[1] if record[1] is not None else '')
        confmes = confmes + '\nТекст заявки: ' + ActiveUser[message.chat.id]['task']
        confmes = confmes + '\nАдрес: ' + (record[2] if record[2] is not None else '')
        confmes = confmes + '\nКонтактное лицо: ' + (record[3] if record[3] is not None else '')
        confmes = confmes + '\nКонтактный номер: ' + (record[4] if record[4] is not None else '')
        bot.send_message(
            message.chat.id,
            confmes,
            reply_markup=buttons.Buttons(['Да', 'Нет'])
        )
        bot.register_next_step_handler(message, NewTask.nt3)

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
                ActiveUser[message.chat.id]['status']
            ]
            db.insert_record('Tasks',task)
            bot.send_message(
                message.chat.id,
                'Заявка успешно зарегистрирована.',
                reply_markup=buttons.Buttons(['Главное меню'])
            )
            tid = db.get_last_record('Tasks')[0]
            sendtoall(functions.curtask(tid), buttons.buttonsinline([['Принять', 'confirm ' + str(tid)], ['Назначить', 'set ' + str(tid)]]), message.chat.id, 1)
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
            bot.register_next_step_handler(message, NewTask.nt4)


class Task:

    def task1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser

        if message.text == 'Принять':

            if db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[11] != 1:
                bot.send_message(
                    message.chat.id,
                    "Вы не можете принять эту заявку!"
                )

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

            bot.send_message(
                message.chat.id,
                'Вы приняли заявку.\n\nВыберите операцию',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
            )
            sendtoall(mes, mark, exn)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

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
                bot.send_message(
                    message.chat.id,
                    'Вы завершили заявку.',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
                )
                sendtoall(mes, mark, exn)

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
                bot.send_message(
                    message.chat.id,
                    'Вы отказались от заявки.',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
                )
                sendtoall(mes, mark, exn)

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
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    def task2(message):
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
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main1)

    def task3(message):
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
        bot.send_message(
            message.chat.id,
            'Заявка отменена\n\nВыберите операцию.',
            reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
        )
        sendtoall(mes, mark, exn)

    def task4(message):
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
            bot.send_message(
                message.chat.id,
                'Мастер назначен.\n\nВыберите операцию',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
            )
            sendtoall(mes, '', exn)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    def task5(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        tasktext = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[4]
        db.update_records(
            'Tasks',
            ['task'], [tasktext + '\n\n ' + username + ' дополнил(а) заявку...\n' + message.text],
            'id', ActiveUser[message.chat.id]['task']
        )
        tk = functions.curtask(ActiveUser[message.chat.id]['task'])
        mes = str(db.get_record_by_id('Users', message.chat.id)[2]) + ' ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + '\n дополнил(а) заявку:\n\n' + tk
        mark = ''
        exn = message.chat.id

        if sendedmessages is not None:
            for line in sendedmessages:
                try:
                    bot.delete_message(line[0], line[1])
                except Exception as e:
                    logging.error(e)

        bot.send_message(
            message.chat.id,
            'Заявка дополнена.\n\nВыберите операцию',
            reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
        )
        sendtoall(mes, mark, exn)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        

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
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
                )

            else:
                bot.send_message(
                    message.chat.id,
                    'Заявок по вашему запросу не найдено.',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
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
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
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


class allchats:
    
    def chat1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')

        if message.text == 'Главное меню':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)

        else:
            users = db.select_table('Users')
            for user in users:
                try:
                    logging.info(f'sended message to user {user[2]} {user[1]}')

                    if user[0] != message.chat.id:
                        bot.forward_message(user[0], message.chat.id, message.message_id)

                except Exception as e:
                    logging.error(e)
                    pass

            bot.register_next_step_handler(message, allchats.chat1)


class report:

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
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
            )

        else:

            if len(addedtasks) != 0 and len(confirmedtasks) != 0 and len(donetasks) != 0 and len(canceledtasks) != 0:
                bot.send_message(
                    message.chat.id,
                    '🟥🟥🟥🟥🟥🟥🟥🟥\nСписок заявок\n🟥🟥🟥🟥🟥🟥🟥🟥',
                    reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
                )

        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.register_next_step_handler(message, MainMenu.Main2)

    def reportall(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')

        if message.text == 'Все':
            logging.info('план отправлен.')
            confirmedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 2}), [0, 1, 3, 4, 6], 1)
            addedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 1}), [0, 1, 3, 4, 6], 1)

            if len(confirmedtasks) == 0 and len(addedtasks) == 0:
                bot.send_message(
                    message.chat.id,
                    'На текущий момент нет переходящих заявок.',
                    reply_markup=''
                )

            else:
                bot.send_message(
                    message.chat.id,
                    'На текущий момент следующие заявки:',
                    reply_markup=''
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

            bot.send_message(
                message.chat.id,
                '🟥🟥🟥🟥🟥🟥🟥🟥Список заявок на сегодня\n🟥🟥🟥🟥🟥🟥🟥🟥',
                reply_markup=buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)
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

def CADR(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    if message.content_type == 'location':
        lon, lat = message.location.longitude, message.location.latitude
        url = f'GOOGLE: https://www.google.com/maps/search/?api=1&query={lat},{lon}\nAPPLE: http://maps.apple.com/maps?ll={lat},{lon}'
        ActiveUser[message.chat.id]['contnew'][2] = url
    else:
        ActiveUser[message.chat.id]['contnew'][2] = message.chat.id
    editcontragent(message)
    bot.register_next_step_handler(message, editcont.ec2)

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



@bot.callback_query_handler(func=lambda call: True)


def callback_handler(call):
    global ActiveUser, sendedmessages

    if call.data.split()[0] == 'tasklist':
        status = db.get_record_by_id('Tasks', int(call.data.split()[1]))

        if status[11] == 1:
            markdownt = buttons.Buttons(['Принять', 'Дополнить', 'Назначить', 'Отменить заявку', 'Назад'])

        elif status[11] == 2:
            markdownt = buttons.Buttons(['Выполнено', 'Дополнить', 'Отказаться от заявки', 'Переназначить', 'Отменить заявку', 'Назад'], 3)

        else:
            markdownt = buttons.Buttons(['Новая заявка', 'Обновить список заявок', 'Мои заявки', 'Редактировать контрагента', 'Дневной отчет', 'Написать всем'],3)

        ActiveUser[call.from_user.id]['sentmes'] = bot.send_message(
            call.from_user.id,
            functions.curtask(call.data.split()[1]),
            reply_markup=markdownt
        )
        ActiveUser[call.from_user.id]['task'] = call.data.split()[1]
        bot.register_next_step_handler(call.message, Task.task1)

    elif call.data.split()[0] == 'confirm':

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
            for line in sendedmessages:
                bot.delete_message(line[0], line[1])

    elif call.data.split()[0] == 'set':
        users = db.select_table('Users')
        bot.send_message(
            call.from_user.id,
            'Выберите мастера...',
            reply_markup=buttons.Buttons(functions.listgen(users, [0, 1, 2], 3), 1)
        )
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        ActiveUser[call.from_user.id]['task'] = call.data.split()[1]
        bot.register_next_step_handler(call.message, Task.task4)

if __name__ == '__main__':
    sendtoall('‼️‼️‼️Сервер бота был перезагружен...‼️‼️‼️\nНажмите кнопку "/start"', buttons.Buttons(['/start']), 0, 0, True)
    thread = threading.Thread(target=asyncio.run, args=(main(),))
    thread.start()
    # bot.polling()
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
            logging.info()
        except Exception as e:
            logging.error(e)
            time.sleep(5)
