import logging, datetime, telebot
import Classes.functions as functions
import Classes.buttons as buttons
from datetime import datetime
from Classes.config import ActiveUser, bot, sendedmessages, db, mainclass


class Task:

    def __init__(self, main):
        self.bot = main

    def task1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        global ActiveUser
        if message.text == '👍 Принять':
            processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
            if db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[11] == 5:
                stat = 6
            else:
                stat = 2
            if db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[11] == 1 or db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[11] == 5:
                db.update_records(
                    'Tasks',
                    [
                        'confirmed',
                        'master',
                        'status'
                    ], [
                        datetime.now().strftime("%d.%m.%Y %H:%M"),
                        message.chat.id, stat
                    ],
                    'id',
                    ActiveUser[message.chat.id]['task']
                )
                tk = functions.curtask(ActiveUser[message.chat.id]['task'])
                mes = str(db.get_record_by_id('Users', message.chat.id)[2]) + ' ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + '\nПринял заявку:\n\n' + tk
                mark = ''
                exn = message.chat.id
                if sendedmessages != None:
                    for line in sendedmessages:
                        functions.mesdel(line[0], line[1])
                functions.sendtoall(mes, mark, exn)
                functions.mesdel(message.chat.id, processing.message_id)
                bot.send_message(
                    message.chat.id,
                    'Вы приняли заявку.\n\nВыберите операцию',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
                ActiveUser[message.chat.id]['Pause_main_handler'] = False
                ActiveUser[message.chat.id]['Finishedop'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = False
            else:
                bot.send_message(
                    message.chat.id,
                    "Вы не можете принять эту заявку!",
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
                ActiveUser[message.chat.id]['Pause_main_handler'] = False
                ActiveUser[message.chat.id]['Finishedop'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = False
            functions.mesdel(message.chat.id, message.message_id)
            functions.deletentm(ActiveUser[message.chat.id]['task'])
        elif message.text == '🖊️ Дополнить':
            bot.send_message(
                message.chat.id,
                'Напишите что вы хотели дополнить...',
                reply_markup=buttons.clearbuttons()
            )
            functions.mesdel(message.chat.id, message.message_id)
            bot.register_next_step_handler(message, Task.task5)
        elif message.text == '📎 Переназначить' or message.text == '📎 Назначить':
            users = db.select_table('Users')
            bot.send_message(
                message.chat.id,
                'Выберите мастера...',
                reply_markup=buttons.Buttons(functions.listgen(users, [0, 1, 2], 3), 1)
            )
            bot.register_next_step_handler(message, Task.task4)
        elif message.text == '✅ Выполнено':
            processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
            manager = str(db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[6])
            if manager == str(message.chat.id):
                if db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[11] == 2:
                    stat = 3
                else:
                    stat = 7
                db.update_records(
                    'Tasks',[
                        'done',
                        'status'
                    ],[
                        datetime.now().strftime("%d.%m.%Y %H:%M"),
                        stat
                    ],
                    'id',
                    ActiveUser[message.chat.id]['task']
                )
                tk = functions.curtask(ActiveUser[message.chat.id]['task'])
                mes = str(db.get_record_by_id('Users', message.chat.id)[2]) + ' ' + str(db.get_record_by_id('Users', message.chat.id)[1]) + '\nВыполнил заявку:\n\n' + tk
                mark = ''
                exn = message.chat.id
                functions.sendtoall(mes, mark, exn)
                functions.mesdel(message.chat.id, processing.message_id)
                bot.send_message(
                    message.chat.id,
                    'Вы завершили заявку.',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '🙅‍♂️ Отказаться от заявки':
            manager = str(db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[6])
            if manager == str(message.chat.id):
                processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
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
                functions.sendtoall(mes, mark, exn)
                functions.mesdel(message.chat.id, processing.message_id)
                bot.send_message(
                    message.chat.id,
                    'Вы отказались от заявки.',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
                ActiveUser[message.chat.id]['Pause_main_handler'] = False
                ActiveUser[message.chat.id]['Finishedop'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = False
            else:
                master = db.get_record_by_id('Users', manager)[1]
                bot.send_message(
                    message.chat.id,
                    'Вы не можете отказаться от этой заявки, так как она не Ваша.\nЗаявку принял ' + str(master),
                    reply_markup=buttons.Buttons(['🏠 Главное меню'])
                )
                ActiveUser[message.chat.id]['Pause_main_handler'] = False
                ActiveUser[message.chat.id]['Finishedop'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '🚫 Отменить заявку':
            manager = str(db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[2])
            bot.send_message(
                message.chat.id,
                'Вы уверены, что хотите отменить заявку?',
                reply_markup=buttons.Buttons(['✅ Да', '⛔️ Нет'])
            )
            bot.register_next_step_handler(message, Task.task2)
        elif message.text == '↩️ Назад':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '✏️ Изменить текст заявки':
            bot.send_message(
                message.chat.id,
                'Введите новый текст заявки.\n\n‼️ ВНИМАНИЕ ‼️\nУчтите что старый текст будет заменен новым поэтому скопируйте старый и отредактируйте.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, Task.task7_1)
        elif message.text == '📍 Локация':
            location = db.get_record_by_id('Locations', db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[12])
            if location != None:
                loc = telebot.types.Location(location[4], location[3])
                bot.send_location(message.chat.id, loc.latitude, loc.longitude)
                bot.send_message(
                    message.chat.id,
                    'Вы можете добавить и закррепить локацию за этой заявкой. Выберите операцию',
                    reply_markup=buttons.Buttons(['📍 Указать локацию', '🚫 Отмена'])
                )
                bot.register_next_step_handler(message, Task.locations1)
            else:
                bot.send_message(
                    message.chat.id,
                    'Прошу прощения но указанная локация либо не была добавлена, или была удалена.\nВыберите операцию',
                    reply_markup=buttons.Buttons(['📍 Указать локацию', '🚫 Отмена'])
                )
                bot.register_next_step_handler(message, Task.locations1)
        else:
            bot.send_message(
                message.chat.id,
                'Ошибка ввода.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False

    def locations1(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == '📍 Указать локацию':
            logging.info('Локации')
            inn = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[3]
            locations = db.select_table_with_filters('Locations', {'inn': inn})
            buttonsloc = []
            buttonsloc.append('🆕 Добавить филиал')
            if len(locations) > 0:
                for location in locations:
                    line = str(location[0]) + ' ' + str(location[2])
                    print(line)
                    buttonsloc.append(line)
            buttonsloc.append('🚫 Отмена')
            print(buttonsloc)
            bot.send_message(
                message.chat.id,
                'Выберите филиал',
                reply_markup=buttons.Buttons(buttonsloc, 2)
            )
            bot.register_next_step_handler(message, Task.locations2)
        elif message.text == '🚫 Отмена':
            print('Нажата отмена')
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False

    def locations2(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        ActiveUser[message.chat.id]['inn'] = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[3]
        if message.text == '🆕 Добавить филиал':
            bot.send_message(
                message.chat.id,
                'Отправьте локацию.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, tnl1)
        elif message.text == '🚫 Отмена':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text.split()[0].isdigit():
            selected = db.get_record_by_id('Locations', message.text.split()[0])
            db.update_records(
                'Tasks',
                ['location'],
                [selected[0]],
                'id',
                ActiveUser[message.chat.id]['task']
            )
            bot.send_message(
                message.chat.id,
                f'Выбрана локация {selected[2]}',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            inn = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[3]
            locations = db.select_table_with_filters('Locations', {'inn': inn})
            buttonsloc = []
            buttonsloc.append('🆕 Добавить филиал')
            if len(locations) > 0:
                for location in locations:
                    buttonsloc.append(str(location[0]) + ' ' + str(location[2]))
            buttonsloc.append('🚫 Отмена')
            if len(locations) > 0:
                bot.send_message(
                    message.chat.id,
                    'Ошибка ввода!\nВыберите филиал',
                    reply_markup=buttons.Buttons(buttonsloc, 2)
                )
            bot.register_next_step_handler(message, Task.locations2)

    def task2(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == '✅ Да':
            bot.send_message(
                message.chat.id,
                'Пожалуйста укажите причину отмены заявки.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, Task.task3)
        elif message.text == '⛔️ Нет':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False

    def task3(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
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
        functions.sendtoall(mes, mark, exn)
        functions.mesdel(message.chat.id, processing.message_id)
        bot.send_message(
            message.chat.id,
            'Заявка отменена\n\nВыберите операцию.',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        ActiveUser[message.chat.id]['Pause_main_handler'] = False
        ActiveUser[message.chat.id]['Finishedop'] = True
        ActiveUser[message.chat.id]['block_main_menu'] = False

    def task4(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[11] == 5:
            stat = 6
        else:
            stat = 2
        if message.text.split()[1] is None:
            users = db.select_table('Users')
            bot.send_message(
                message.chat.id,
                'Выберите мастера...',
                reply_markup=buttons.Buttons(functions.listgen(users, [0, 1, 2], 3), 1)
            )
            bot.register_next_step_handler(message, Task.task4)
        else:
            processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
            userm = message.text.split()[1]
            
            db.update_records(
                'Tasks',
                [
                    'confirmed',
                    'master',
                    'status'
                ], [
                    datetime.now().strftime("%d.%m.%Y %H:%M"),
                    userm, stat
                ],
                'id',
                ActiveUser[message.chat.id]['task']
            )
            if sendedmessages != None:
                for line in sendedmessages:
                    functions.mesdel(line[0], line[1])
            tk = functions.curtask(ActiveUser[message.chat.id]['task'])
            mes = str(db.get_record_by_id('Users', userm)[2]) + ' ' + str(db.get_record_by_id('Users', userm)[1]) + '\nбыл назначен исполнителем заявки:\n\n' + tk
            exn = message.chat.id
            functions.sendtoall(mes, '', exn)
            functions.mesdel(message.chat.id, processing.message_id)
            bot.send_message(
                message.chat.id,
                'Мастер назначен.\n\nВыберите операцию',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False

    def task5(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
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
        functions.sendtoall(mes, mark, exn)
        if sendedmessages != None:
            for line in sendedmessages:
                functions.mesdel(line[0], line[1])
        functions.mesdel(message.chat.id, processing.message_id)
        bot.send_message(
            message.chat.id,
            'Заявка дополнена.\n\nВыберите операцию',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        ActiveUser[message.chat.id]['Pause_main_handler'] = False
        ActiveUser[message.chat.id]['Finishedop'] = True
        ActiveUser[message.chat.id]['block_main_menu'] = False

    def task6(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == '✅ Да':
            processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
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
            functions.sendtoall(mes, mark, message.chat.id)
            functions.mesdel(message.chat.id, processing.message_id)
            bot.send_message(
                message.chat.id,
                f'Клиент в заявке изменен на {client}.\n\nВыберите операцию',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
        elif message.text == '⛔️ Нет':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
        else:
            bot.send_message(
                message.chat.id,
                'Неверная команда',
                reply_markup=buttons.Buttons(['✅ Да', '⛔️ Нет'])
            )
            bot.register_next_step_handler(message, Task.task6)

    def task7_1(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        taskt = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[4]
        ActiveUser[message.chat.id]['newtasktext'] = message.text
        bot.send_message(
            message.chat.id,
            f'Текст заявку будет изменен с:\n{taskt}\nНа:\n{message.text}\n\n Подтвердите информацию...',
            reply_markup=buttons.Buttons(['✅ Да','⛔️ Нет'])
        )
        bot.register_next_step_handler(message, Task.task7_2)

    def task7_2(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == '✅ Да':
            processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
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
            functions.sendtoall(mes, mark, message.chat.id)
            functions.mesdel(message.chat.id, processing.message_id)
            bot.send_message(
                message.chat.id,
                'Заявка успешно измненена.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '⛔️ Нет':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            bot.send_message(
                message.chat.id,
                'Вы не подтвердили информацию.\nЗаменить старый текст заявки на новый',
                reply_markup=buttons.Buttons(['✅ Да','⛔️ Нет'])
            )
            bot.register_next_step_handler(message, Task.task7_2)

# Добавление локации филиала в акнивной заявке
def tnl1(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    if message.content_type == 'location':
        lon, lat = message.location.longitude, message.location.latitude
        ActiveUser[message.chat.id]['lon'] = lon
        ActiveUser[message.chat.id]['lat'] = lat
        bot.send_message(
            message.chat.id,
            'Укажите название локации\nНАПРИМЕР:\nФилиал чиланзар или головной офис',
        )
        bot.register_next_step_handler(message, tnl2)
    else:
        bot.send_message(
            message.chat.id,
            'Вы должны были отправить локацию.\nОтправьте локацию.',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, tnl1)

def tnl2(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
    global ActiveUser
    ActiveUser[message.chat.id]['locationname'] = message.text
    ActiveUser[message.chat.id]['inn'] = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[3]
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
    inn = db.get_record_by_id('Tasks', ActiveUser[message.chat.id]['task'])[3]
    locations = db.select_table_with_filters('Locations', {'inn': inn})
    buttonsloc = []
    buttonsloc.append('🆕 Добавить филиал')
    if len(locations) > 0:
        for location in locations:
            buttonsloc.append(str(location[0]) + ' ' + str(location[2]))
    buttonsloc.append('🚫 Отмена')
    if len(locations) > 0:
        bot.send_message(
            message.chat.id,
            'Выберите филиал...',
            reply_markup=buttons.Buttons(buttonsloc, 2)
        )
    bot.register_next_step_handler(message, Task.locations2)