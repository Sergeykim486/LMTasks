import os, config, telebot, functions, buttons, logging, time
from db import Database
from datetime import datetime, timedelta
ActiveUser = {}
dbname = os.path.dirname(os.path.abspath(__file__)) + '/Database/' + 'lmtasksbase.db'
db = Database(dbname)
bot = telebot.TeleBot(config.TOKEN)

def sendtoall(message, markdown, exeptions):
    users = db.select_table('Users')
    for user in users:
        if user[0] != exeptions:
            bot.send_message(
                user[0],
                message,
                reply_markup=markdown
            )
    return

@bot.message_handler(commands=['start'])

def send_welcome(message):
    global ActiveUser
    ActiveUser[message.chat.id] = {'id': message.chat.id}
    finduser = db.search_record("Users", "id", message.chat.id)
    if len(finduser) == 0:
        bot.send_message(
            message.chat.id,
            'Вам нужно пройти регистрацию',
            reply_markup=buttons.Buttons(['Регистрация'])
        )
        bot.register_next_step_handler(message, register.reg1)
    else:
        ufname = str(db.get_record_by_id("Users", message.chat.id)[1])
        bot.send_message(
            message.chat.id,
            'Вы зарегистрированы как' + ufname + '.',
            reply_markup=buttons.Buttons(['Главное меню'])
        )
        bot.register_next_step_handler(message, MainMenu.Main1)

@bot.message_handler(content_types=['text'])

class register:

    def reg1(message):
        if message.text == 'Регистрация':
            bot.send_message(
                message.chat.id,
                'Как Вас зовут (укажите имя)',
            reply_markup=buttons.clearbuttons()
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, register.reg2)
        else:
            bot.send_message(
                message.chat.id,
                'Пожалуйста зарегистрируйтесь.',
                reply_markup=buttons.Buttons(['Регистрация'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, register.reg1)

    def reg2(message):
        global ActiveUser
        ActiveUser[message.chat.id]['FirstName'] = message.text
        bot.send_message(
            message.chat.id,
            'Укажите Вашу фамилию.',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, register.reg3)

    def reg3(message):
        global ActiveUser
        ActiveUser[message.chat.id]['LastName'] = message.text
        bot.send_message(
            message.chat.id,
            'Введите Ваш номер телефона в формате (+998 00 000 0000).',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, register.reg4)

    def reg4(message):
        global ActiveUser
        ActiveUser[message.chat.id]['PhoneNumber'] = message.text
        bot.send_message(
            message.chat.id,
            functions.conftext(message, ActiveUser),
            reply_markup=buttons.Buttons(['Да', 'Нет'])
        )
        bot.register_next_step_handler(message, register.reg5)

    def reg5(message):
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
            bot.register_next_step_handler(message, register.reg1)
        else:
            bot.send_message(
                message.chat.id,
                'Вы не подтвердили информацию!\n' + functions.conftext(message, ActiveUser),
                reply_markup=buttons.Buttons(['Да', 'Нет'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, register.reg5)

class MainMenu:

    def Main1(message):
        global ActiveUser
        print('main menu')
        if message.text == 'Главное меню' or message.text == 'Вернуться':
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Что вы хотите сделать.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Список заявок', 'Написать всем'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)

    def Main2(message):
        if message.text == 'Новая заявка':
            contragents = db.select_table('Contragents', ['id', 'cname'])
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Выберите клиента или введите его ИНН.',
                reply_markup=buttons.Buttons(functions.listgen(contragents, [0, 1], 2), 1, 1)
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, NewTask.nt1)
        elif message.text == 'Список заявок':
            ActiveUser[message.chat.id]['filter'] = {
                'from': '01.01.2000 00:00',
                'to': '31.12.2100 23:59',
                'added': 1,
                'confirmed': 0,
                'done': 0,
                'canceled': 0,
                'justmy': 0
            }
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(['Указать период', 'Зарегистрированные', 'В работе', 'Завершенные', 'Отмененные', 'Только мои', 'Сформировать'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == 'Написать всем':
            bot.send_message(
                message.chat.id,
                'Напишите Ваше сообщение и оно будет разослано всем.\nчтобы вернуться в главное меню нажмите [Главное меню]',
                reply_markup=buttons.Buttons(['Главное меню'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, allchats.chat1)
        else:
            bot.send_message(
                message.chat.id,
                'Не верная команда!',
                reply_markup=buttons.Buttons(['Новая заявка', 'Список заявок', 'Написать всем'])
            )
            bot.register_next_step_handler(message, MainMenu.Main2)

class NewTask:

    def nt1(message):
        global ActiveUser
        ActiveUser[message.chat.id]['added'] = datetime.now().strftime("%d.%m.%Y %H:%M")
        ActiveUser[message.chat.id]['manager'] = message.chat.id
        ActiveUser[message.chat.id]['status'] = 1
        if message.text == 'Отмена':
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Что вы хотите сделать.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Список заявок', 'Написать всем'])
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif len(message.text.replace(' ', '')) == 9:
            ActiveUser[message.chat.id]['inn'] = message.text
            findcont = db.get_record_by_id('Contragents', message.text)
            if findcont == None:
                bot.send_message(
                    message.chat.id,
                    'Контрагент с указанным Вами ИНН не найден. \nПожалуйста укажите наименование организации',
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, NewTask.nt2)
            else:
                client = db.get_record_by_id('Contragents', message.text)
                bot.send_message(
                    message.chat.id,
                    'Выбран клиент - ' + str(client[1]) + '\nКоротко опишите проблему клиента.',
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, NewTask.nt6)
        elif len(message.text) < 9 & len(message.text) & message.text.isdigit():
            bot.send_message(
                message.chat.id,
                'Внимание!\nВведенный Вами ИНН не корректен.\nПожалуйста проверьте ИНН и введите снова.\nДля повторной попытки нажмите ВВЕСТИ СНОВА.\nДля отмены нажмите Главное меню.',
                reply_markup=buttons.Buttons(['Ввести снова', 'Главное меню'])
            )
            bot.register_next_step_handler(message, NewTask.innerror)
        else:
            mes = message.text
            text = mes.split(' ')
            print(text[1])
            ActiveUser[message.chat.id]['inn'] = text[1]
            client = db.get_record_by_id('Contragents', text[1])
            bot.send_message(
                message.chat.id,
                'Выбран клиент - ' + str(client[1]) + '\nКоротко опишите проблему клиента.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.nt6)

    def innerror(message):
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
            global ActiveUser
            ActiveUser[message.chat.id].clear()
            bot.send_message(
                message.chat.id,
                'Добро пожаловать в систему. Что вы хотите сделать.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Список заявок', 'Написать всем'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)

    def nt2(message):
        global ActiveUser
        ActiveUser[message.chat.id]['cname'] = message.text
        bot.send_message(
            message.chat.id,
            'Укажите адрес клиента.',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, NewTask.nt3)

    def nt3(message):
        global ActiveUser
        ActiveUser[message.chat.id]['cadr'] = message.text
        bot.send_message(
            message.chat.id,
            'Кто подал заявку? Укажите имя контактного лица.',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, NewTask.nt4)

    def nt4(message):
        global ActiveUser
        ActiveUser[message.chat.id]['cperson'] = message.text
        bot.send_message(
            message.chat.id,
            'Укажите контактный номер телефона для связи с клиентом.',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, NewTask.nt5)

    def nt5(message):
        global ActiveUser
        ActiveUser[message.chat.id]['cphone'] = message.text
        contragent = [
            ActiveUser[message.chat.id]['inn'],
            ActiveUser[message.chat.id]['cname'],
            ActiveUser[message.chat.id]['cadr'],
            ActiveUser[message.chat.id]['cperson'],
            ActiveUser[message.chat.id]['cphone']
        ]
        db.insert_record('Contragents', contragent)
        bot.send_message(
            message.chat.id,
            'Кратко опишите проблему клиента',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, NewTask.nt6)

    def nt6(message):
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
        bot.register_next_step_handler(message, NewTask.nt7)

    def nt7(message):
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
            tid = db.get_last_record('Tasks')[0]
            sendtoall(functions.curtask(tid), buttons.buttonsinline([['Принять', 'confirm ' + str(tid)]]), message.chat.id)
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
            bot.register_next_step_handler(message, NewTask.nt7)

        # bot.register_next_step_handler(message, MainMenu.Main1)

class Task:
    def task1(message):
        global ActiveUser
        if message.text == 'Принять':
            print('Пользователь принимает заявку')
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
            print('запись изменена')
            atask = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])
            tk = '№' + str(atask[0]) + ' от ' + str(atask[1]) + '\nпоступившую от ' + str(db.get_record_by_id('Contragents', atask[2]))
            mes = '-> ' + str(db.get_record_by_id('Users', call.from_user.id)[2]) + ' ' + str(db.get_record_by_id('Users', call.from_user.id)[1]) + '\nПринял заявку' + tk
            mark = buttons.Buttons(['Главное меню'])
            exn = message.chat.id
            sendtoall(mes, mark, exn)
            print('оповещение о успешном принятии заявки')
            bot.send_message(
                message.chat.id,
                'Вы приняли заявку.',
                reply_markup=buttons.Buttons(['Главное меню'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main1)
        elif message.text == 'Выполнено':
            manager = str(db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[6])
            print(manager)
            if manager == str(message.chat.id):
                print('Пользователь выполнил заявку')
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
                atask = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])
                tk = '№' + str(atask[0]) + ' от ' + str(atask[1]) + '\nпоступившую от ' + str(db.get_record_by_id('Contragents', atask[2]))
                mes = '-> ' + str(db.get_record_by_id('Users', call.from_user.id)[2]) + ' ' + str(db.get_record_by_id('Users', call.from_user.id)[1]) + '\nВыполнил заявку ' + tk
                mark = buttons.Buttons(['Главное меню'])
                exn = message.chat.id
                sendtoall(mes, mark, exn)
                bot.send_message(
                    message.chat.id,
                    'Вы завершили заявку.',
                    reply_markup=buttons.Buttons(['Главное меню'])
                )
                bot.register_next_step_handler(message, MainMenu.Main1)
        elif message.text == 'Отказаться от заявки':
            manager = str(db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[6])
            print(manager)
            if manager == str(message.chat.id):
                confdate = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[5]
                db.update_records(
                    'Tasks',
                    [
                        'more',
                        'master',
                        'status'
                    ], [
                        'Мастер ' + str(db.get_record_by_id('Users', call.from_user.id)[2]) + ' ' + str(db.get_record_by_id('Users', call.from_user.id)[1]) + ' принял заявку ' + str(confdate) + '.\n ' + str(datetime.now().strftime("%d.%m.%Y %H:%M")) + 'отказался от выполнения',
                        '',
                        1
                    ],
                    'id',
                    ActiveUser[message.chat.id]['task']
                )
                atask = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])
                tk = '№' + str(atask[0]) + ' от ' + str(atask[1]) + '\nпоступившую от ' + str(db.get_record_by_id('Contragents', atask[2]))
                mes = 'Пользователь ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + 'Отказался от заявки ' + tk
                mark = buttons.Buttons(['Главное меню'])
                exn = message.chat.id
                sendtoall(mes, mark, exn)
                bot.send_message(
                    message.chat.id,
                    'Вы отказались от заявки.',
                    reply_markup=buttons.Buttons(['Главное меню'])
                )
                bot.register_next_step_handler(message, MainMenu.Main1)
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
            print(manager)
            if manager == str(message.chat.id):
                print('Пользователь отменил заявку')
                bot.send_message(
                    message.chat.id,
                    'Вы уверены, что хотите отменить заявку?',
                    reply_markup=buttons.Buttons(['Да', 'Нет'])
                )
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.register_next_step_handler(message, Task.task2)
            else:
                master = db.get_record_by_id('Users', manager)[1]
                bot.send_message(
                    message.chat.id,
                    'Вы пытаетесь отменить заявку которую зарегистрировал другой пользователь.\nОтменить эту заявку может только ' + str(master),
                    reply_markup=buttons.Buttons(['Главное меню'])
                )
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.register_next_step_handler(message, MainMenu.Main1)
        elif message.text == 'Назад':
            bot.send_message(
                message.chat.id,
                'Что вы хотите сделать.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Список заявок', 'Написать всем'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            # bot.register_next_step_handler(message, MainMenu.Main2)

    def task2(message):
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
                'Вернитесь в главное меню.',
                reply_markup=buttons.Buttons(['Главное меню'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main1)

    def task3(message):
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
        atask = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])
        tk = '№' + str(atask[0]) + ' от ' + str(atask[1]) + '\nпоступившую от ' + str(db.get_record_by_id('Contragents', atask[2]))
        mes = '-> ' + str(db.get_record_by_id('Users', call.from_user.id)[2]) + ' ' + str(db.get_record_by_id('Users', call.from_user.id)[1]) + '\nОтменил заявку ' + tk + '\nПРИЧИНА:\n' + message.text
        mark = buttons.Buttons(['Главное меню'])
        exn = message.chat.id
        sendtoall(mes, mark, exn)
        bot.send_message(
            message.chat.id,
            'Заявка отменена',
            reply_markup=buttons.Buttons(['Главное меню'])
        )
        bot.register_next_step_handler(message, MainMenu.Main1)

def filters(message):
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
                        print('Запись найдена: Заявка №' + str(line[0]) + ' от ' + str(line[1]))
                    else:
                        tasks.remove(line)
            taskslist = functions.listgen(tasks, [0, 1, 3, 4], 1)
            for line in taskslist:
                print(line)
                taskid = line.split()[2]
                print('номер заявки - ' + taskid)
                bot.send_message(
                    message.chat.id,
                    line,
                    reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]])
                )
            bot.send_message(
                message.chat.id,
                'Что вы хотите сделать.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Список заявок', 'Написать всем'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == 'Указать период':
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Укажите дату начала периода.\nДень точка Месяц точка Год полностью\nПРИМЕР: 01.01.2023',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, TL.tl2)
        elif message.text == 'Зарегистрированные':
            if ActiveUser[message.chat.id]['filter']['added'] == 1:
                ActiveUser[message.chat.id]['filter']['added'] = 0
            else:
                ActiveUser[message.chat.id]['filter']['added'] = 1
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(['Указать период', 'Зарегистрированные', 'В работе', 'Завершенные', 'Отмененные', 'Только мои', 'Сформировать'])
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == 'В работе':
            if ActiveUser[message.chat.id]['filter']['confirmed'] == 1:
                ActiveUser[message.chat.id]['filter']['confirmed'] = 0
            else:
                ActiveUser[message.chat.id]['filter']['confirmed'] = 1
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(['Указать период', 'Зарегистрированные', 'В работе', 'Завершенные', 'Отмененные', 'Только мои', 'Сформировать'])
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == 'Завершенные':
            if ActiveUser[message.chat.id]['filter']['done'] == 1:
                ActiveUser[message.chat.id]['filter']['done'] = 0
            else:
                ActiveUser[message.chat.id]['filter']['done'] = 1
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(['Указать период', 'Зарегистрированные', 'В работе', 'Завершенные', 'Отмененные', 'Только мои', 'Сформировать'])
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == 'Отмененные':
            if ActiveUser[message.chat.id]['filter']['canceled'] == 1:
                ActiveUser[message.chat.id]['filter']['canceled'] = 0
            else:
                ActiveUser[message.chat.id]['filter']['canceled'] = 1
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(['Указать период', 'Зарегистрированные', 'В работе', 'Завершенные', 'Отмененные', 'Только мои', 'Сформировать'])
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == 'Только мои':
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
                reply_markup=buttons.Buttons1(['Указать период', 'Зарегистрированные', 'В работе', 'Завершенные', 'Отмененные', 'Только мои', 'Сформировать'])
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif message.text == 'Отмена':
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Что вы хотите сделать.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Список заявок', 'Написать всем'])
            )
            bot.register_next_step_handler(message, MainMenu.Main2)

    def tl2(message):
        if len(message.text.split('.')) == 3 and len(message.text.split('.')[0]) == 2 and len(message.text.split('.')[1]) == 2 and len(message.text.split('.')[2]) == 4:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['filter']['from'] = message.text + ' 00:00'
            print(ActiveUser[message.chat.id]['filter']['from'])
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Укажите дату конца периода.\nДень точка Месяц точка Год полностью\nПРИМЕР: 01.01.2023',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, TL.tl3)
        else:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'НЕ ВЕРНЫЙ ФОРМАТ!\nУкажите дату начала периода.\nДень точка Месяц точка Год полностью\nПРИМЕР: 01.01.2023',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, TL.tl2)

    def tl3(message):
        if len(message.text.split('.')) == 3 and len(message.text.split('.')[0]) == 2 and len(message.text.split('.')[1]) == 2 and len(message.text.split('.')[2]) == 4 and datetime.strptime(ActiveUser[message.chat.id]['filter']['from'], '%d.%m.%Y %H:%M') < datetime.strptime(message.text + ' 23:00', '%d.%m.%Y %H:%M'):
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['filter']['to'] = message.text + ' 23:00'
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                filters(message),
                reply_markup=buttons.Buttons1(['Указать период', 'Зарегистрированные', 'В работе', 'Завершенные', 'Отмененные', 'Только мои', 'Сформировать'])
            )
            bot.register_next_step_handler(message, TL.tl1)
        elif datetime.strptime(ActiveUser[message.chat.id]['filter']['from'], '%d.%m.%Y %H:%M') > datetime.strptime(message.text + ' 23:00', '%d.%m.%Y %H:%M'):
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'УКАЗАННАЯ ВАМИ ДАТА РАНЬШЕ ЧЕМ ДАТА НАЧАЛА ПЕРИОДА!\nУкажите дату конца периода.\nДень точка Месяц точка Год полностью\nПРИМЕР: 01.01.2023',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, TL.tl3)
        else:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=ActiveUser[message.chat.id]['sentmes'].chat.id, message_id=ActiveUser[message.chat.id]['sentmes'].message_id)
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'НЕ ВЕРНЫЙ ФОРМАТ!\nУкажите дату конца периода.\nДень точка Месяц точка Год полностью\nПРИМЕР: 01.01.2023',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, TL.tl3)

@bot.message_handler(func=lambda message: True)

class allchats:
    def chat1(message):
        if message.text == 'Главное меню':
            bot.send_message(
                message.chat.id,
                'Что вы хотите сделать.',
                reply_markup=buttons.Buttons(['Новая заявка', 'Список заявок', 'Написать всем'])
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
        else:
            users = db.select_table('Users')
            for user in users:
                if user [0] != message.chat.id:
                    bot.forward_message(user[0], message.chat.id, message.message_id)
            bot.register_next_step_handler(message, allchats.chat1)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global ActiveUser
    if call.data.split()[0] == 'tasklist':
        print('Пользователь выбрал заявку')
        status = db.get_record_by_id('Tasks', int(call.data.split()[1]))
        print(status)
        if status[11] == 1:
            markdownt = buttons.Buttons(['Принять', 'Отменить заявку', 'Назад'])
        elif status[11] == 2:
            markdownt = buttons.Buttons(['Выполнено', 'Отказаться от заявки', 'Отменить заявку', 'Назад'])
        else:
            markdownt = buttons.Buttons(['Новая заявка', 'Список заявок', 'Написать всем'])
        print('Отправка текста заявки пользователю.')
        bot.send_message(
            call.from_user.id,
            functions.curtask(call.data.split()[1]),
            reply_markup=markdownt
        )
        ActiveUser[call.from_user.id]['task'] = call.data.split()[1]
        print(ActiveUser[call.from_user.id]['task'])
        bot.register_next_step_handler(call.message, Task.task1)
    elif call.data.split()[0] == 'confirm':
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
        sendtoall('-> ' + str(db.get_record_by_id('Users', call.from_user.id)[2]) + ' ' + str(db.get_record_by_id('Users', call.from_user.id)[1]) + '\nПринял заявку №' + str(call.data.split()[1]), '', call.from_user.id)


while True:
    try:
        # bot.polling(none_stop=True, timeout=60)
        bot.polling()
    except Exception as e:
        print(e)
        time.sleep(5)