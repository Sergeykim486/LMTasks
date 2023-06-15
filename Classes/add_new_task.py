import logging, datetime, telebot
import Classes.functions as functions
import Classes.buttons as buttons
from datetime import datetime
from Classes.config import ActiveUser, bot, sendedmessages, db, mainclass
num = 0

# Новая заявка
class NewTask:

    # Поиск контрагента по ИНН
    def nt1(message):
        global num
        if num == 0:
            num = 1
        ActiveUser[message.chat.id]['block_nt1'] = True
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        ActiveUser[message.chat.id]['added'] = datetime.now().strftime("%d.%m.%Y %H:%M")
        ActiveUser[message.chat.id]['manager'] = message.chat.id
        ActiveUser[message.chat.id]['status'] = 1
        if message.text == '🚫 Отмена':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
            ActiveUser[message.chat.id]['block_nt1'] = False
        elif message.text.split()[0].isdigit():
            processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
            if message.text.split()[0].isdigit():
                inn = message.text.split()[0]
            else:
                inn = message.text.split()[1]
            ActiveUser[message.chat.id]['inn'] = inn
            findcont = db.get_record_by_id('Contragents', inn)
            if findcont == None:
                functions.mesdel(message.chat.id, processing.message_id)
                bot.send_message(
                    message.chat.id,
                    'Контрагент с указанным Вами ИНН не найден. \nБудет добавлен новый.\nВыберите тип клиента',
                    reply_markup=buttons.Buttons(['Разовый', 'Долгосрочный', 'Физ. лицо'])
                )
                ActiveUser[message.chat.id]['block_nt1'] = False
                bot.register_next_step_handler(message, NewTask.NeContr1)
            else:
                functions.mesdel(message.chat.id, processing.message_id)
                client = db.get_record_by_id('Contragents', inn)
                if client[5] != None and ActiveUser[message.chat.id]['nt'] == 1:
                    bot.send_message(
                        message.chat.id,
                        'Выбран клиент - ' + str(client[1]) + '\nЗаявка или техника?',
                        reply_markup=buttons.Buttons(['📝 Заявка','🖨️ Техника'])
                    )
                    functions.top10add(client, message.chat.id)
                    ActiveUser[message.chat.id]['block_nt1'] = False
                    bot.register_next_step_handler(message, NewTask.tech1)
                else:
                    bot.send_message(
                        message.chat.id,
                        'У выбранного клиента - ' + str(client[1]) + ' не определен тип и договор.\nПожалуйста выберите тип клиента.',
                        reply_markup=buttons.Buttons(['Разовый', 'Долгосрочный', 'Физ. лицо'])
                    )
                    functions.top10add(client, message.chat.id)
                    ActiveUser[message.chat.id]['block_nt1'] = False
                    bot.register_next_step_handler(message, NewTask.type1)
        else:
            if num == 1:
                num = num + 1
                processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
                contrs = db.select_table('Contragents')
                res = functions.search_items(message.text, contrs)
                contbuttons = []
                contbuttons.append('🚫 Отмена')
                if len(res) > 0:
                    for i in res:
                        line = str(i[0]) + ' ' + str(i[1])
                        if len(contbuttons) < 20:
                            contbuttons.append(line)
                    functions.mesdel(message.chat.id, processing.message_id)
                    try:
                        bot.send_message(
                            message.chat.id,
                            'Если нужный клиент не вышел в списке, попробуйте перефразировать и ввести снова.\nВыберите контрагента из списка, или введите его ИНН, ПИНФЛ, серию пасспорта или повторите поиск.',
                            reply_markup=buttons.Buttons(contbuttons, 1)
                        )
                    except Exception as e:
                        logging.error(e)
                        pass
                else:
                    functions.mesdel(message.chat.id, processing.message_id)
                    print(message.text)
                    if message.text == '📝 Новая заявка' or message.text == None:
                        bot.send_message(
                            message.chat.id,
                            'Введите ИНН, ПИНФЛ или серию пвсспоррта клиента.\nТак же Вы можете попытаться поискать контрагента по наименованию или его части\nНапримар:\nmonohrom\nВыдаст все компании из базы бота у которых в названии есть monohrom',
                            reply_markup=buttons.Buttons(functions.top10buttons(message.chat.id), 1)
                        )
                    else:
                        bot.send_message(
                            message.chat.id,
                            '⚠️ ВНИМЕНИЕ!\nКонтрагент не найден.\nПопробуйте перефразировать.',
                            reply_markup=buttons.Buttons(functions.top10buttons(message.chat.id), 1)
                        )
                ActiveUser[message.chat.id]['block_nt1'] = False
                bot.register_next_step_handler(message, NewTask.nt1)
            else:
                bot.register_next_step_handler(message, NewTask.nt1)

    # Техника
    def tech1(message):
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == '📝 Заявка':
            bot.send_message(
                message.chat.id,
                'опишите проблему клиента...',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.ntlocation1)
        elif message.text == '🖨️ Техника':
            ActiveUser[message.chat.id]['status'] = 5
            bot.send_message(
                message.chat.id,
                'Укажите модель и производителя...',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, NewTask.tech2)
        else:
            bot.send_message(
                message.chat.id,
                "Сначала выберить что оформляете Заявка или Техника",
                reply_markup=buttons.Buttons(['📝 Заявка','🖨️ Техника'])
            )
            bot.register_next_step_handler(message, NewTask.tech1)

    def tech2(message):
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        ActiveUser[message.chat.id]['task'] = message.text
        bot.send_message(
            message.chat.id,
            'Опишите проблему с техникой...',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, NewTask.tech3)

    def tech3(message):
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        ActiveUser[message.chat.id]['task'] = ActiveUser[message.chat.id]['task'] + '\n======================\n' + message.text
        bot.send_message(
            message.chat.id,
            'Укажите номер квитанции и дату...\nПример:\n№ 10 от 01.01.2023',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, NewTask.nt2)

    # Тип соглашения контрагента если не добавлен в реквизиты контрагента
    def type1(message):
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
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
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
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
            'Заявка или техника?',
            reply_markup=buttons.Buttons(['📝 Заявка','🖨️ Техника'])
        )
        bot.register_next_step_handler(message, NewTask.tech1)

    # Обработка ошибки ввода ИНН
    def innerror(message):
        global num
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == 'Ввести снова':
            contragents = db.select_table('Contragents', ['id', 'cname'])
            bot.send_message(
                message.chat.id,
                'Выберите клиента или введите его ИНН.',
                reply_markup=buttons.Buttons(functions.listgen(contragents, [0, 1], 2))
            )
            bot.register_next_step_handler(message, NewTask.nt1)
        elif message.text == '🏠 Главное меню':
            num = 0
            ActiveUser[message.chat.id].clear()
            bot.send_message(
                message.chat.id,
                'Добро пожаловать в систему. Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False

    # Добавление нового контрагента
    def NeContr1(message):
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
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
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
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
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
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
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
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
            reply_markup=buttons.Buttons(['✅ Да', '⛔️ Нет'])
        )
        bot.register_next_step_handler(message, NewTask.NeContr7)

    def NeContr7(message):
        global num
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == '✅ Да':
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
            if ActiveUser[message.chat.id]['nt'] == 1:
                bot.send_message(
                    message.chat.id,
                    'Заявка или техника?',
                    reply_markup=buttons.Buttons(['📝 Заявка','🖨️ Техника'])
                )
                bot.register_next_step_handler(message, NewTask.tech1)
        elif message.text == '⛔️ Нет':
            num = 0
            bot.send_message(
                message.chat.id,
                'Контрагент не добавлен.\nВыберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            bot.send_message(
                message.chat.id,
                'Ошибка ввода!\n' + ActiveUser[message.chat.id]['mess'],
                reply_markup=buttons.Buttons(['✅ Да', '⛔️ Нет'])
            )
            bot.register_next_step_handler(message, NewTask.NeContr7)

    # Выбор локации
    def ntlocation1(message):
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        if ActiveUser[message.chat.id]['status'] == 1:
            ActiveUser[message.chat.id]['task'] = message.text
        else:
            ActiveUser[message.chat.id]['task'] = ActiveUser[message.chat.id]['task'] + '\n======================\n' + message.text
        locations = db.select_table_with_filters('Locations', {'inn': ActiveUser[message.chat.id]['inn']})
        clocations = ['⏩ Пропустить']
        if len(locations) > 0:
            for i in locations:
                line = str(i[0]) + ' ' + str(i[2])
                clocations.append(line)
            clocations.append('🆕 Добавить филиал')
            bot.send_message(
                message.chat.id,
                'Выберите филиал, или введите название филиала',
                reply_markup=buttons.Buttons(clocations,2)
            )
        else:
            clocations.append('🆕 Добавить филиал')
            bot.send_message(
                message.chat.id,
                'У выбранного контрагента нет назначенных локаций!\nДобавьте новую.',
                reply_markup=buttons.Buttons(clocations)
            )
        bot.register_next_step_handler(message, NewTask.ntlocation2)

    # Проверка нажатия на кнопки выбора локаций
    def ntlocation2(message):
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        if message.text == '⏩ Пропустить':
            ActiveUser[message.chat.id]['location'] = None
            conf(message)
            bot.register_next_step_handler(message, NewTask.nt3)
        elif message.text == '🆕 Добавить филиал':
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
            contloc = db.select_table_with_filters('Locations', {'inn': ActiveUser[message.chat.id]['inn']})
            res = functions.search_items(message.text, contloc)
            but = []
            but.append('⏩ Пропустить')
            if len(res) > 0:
                for r in res:
                    line = str(r[0]) + ' ' + str(r[2])
                    but.append(line)
                but.append('🆕 Добавить филиал')
                bot.send_message(
                    message.chat.id,
                    'Выберите филиал, или введите название филиала',
                    reply_markup=buttons.Buttons(but, 2)
                )
                bot.register_next_step_handler(message, NewTask.ntlocation2)
            else:
                but.append('🆕 Добавить филиал')
                bot.send_message(
                    message.chat.id,
                    'Совпадений не найдено, попробуйте еще раз или добавьте филиал',
                    reply_markup=buttons.Buttons(but)
                )
                bot.register_next_step_handler(message, NewTask.ntlocation2)  

    # Добавление новой заявки в базу данных
    def nt2(message):
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        ActiveUser[message.chat.id]['location'] = 999
        ActiveUser[message.chat.id]['task'] = ActiveUser[message.chat.id]['task'] + '\n======================\n' + message.text
        conf(message)
        bot.register_next_step_handler(message, NewTask.nt3)

    def nt3(message):
        global num
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'{username} Отправил запрос - {message.text}')
        processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
        if message.text == '✅ Да':
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
            users = db.select_table('Users')
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
                    pass
            functions.mesdel(message.chat.id, processing.message_id)
            bot.send_message(
                message.chat.id,
                'Заявка успешно зарегистрирована.\nВыберрите операцию',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            num = 0
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '⛔️ Нет':
            bot.send_message(
                message.chat.id,
                'Новая заявка удалена.\nВыберрите операцию',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            functions.mesdel(message.chat.id, processing.message_id)
            num = 0
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            bot.send_message(
                message.chat.id,
                'Сначала подтвердите сохранение.\nСохранить заявку?',
                reply_markup=buttons.Buttons(['✅ Да', '⛔️ Нет'])
            )
            functions.mesdel(message.chat.id, processing.message_id)
            bot.register_next_step_handler(message, NewTask.nt3)

# сообщение для подтверждения заявки
def conf(message):
    confmes = 'Подтвердите заявку. \nЗаявка от: '
    confmes = confmes + ActiveUser[message.chat.id]['added']
    record = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['inn'])
    if ActiveUser[message.chat.id]['location'] != None:
        location = db.get_record_by_id('Locations', ActiveUser[message.chat.id]['location'])[2]
    else:
        location = ''
    confmes = confmes + '\nКлиент: ' + (record[1] if record[1] != None else '') + (f" {location}" if ActiveUser[message.chat.id]['location'] != None else '')
    confmes = confmes + '\nТекст заявки: ' + ActiveUser[message.chat.id]['task']
    confmes = confmes + '\nАдрес: ' + (record[2] if record[2] != None else '')
    confmes = confmes + '\nКонтактное лицо: ' + (record[3] if record[3] != None else '')
    confmes = confmes + '\nКонтактный номер: ' + (record[4] if record[4] != None else '')
    bot.send_message(
        message.chat.id,
        confmes,
        reply_markup=buttons.Buttons(['✅ Да', '⛔️ Нет'])
    )
    return

# Формирование гугл ссылки на карты по локации для адреса при добавлении нового контрагента
def NeContr4(message):
    if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
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
    if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
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

# Добавление локации филиала в новой заявке
def newlocationintask1(message):
    if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
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
    if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос - {message.text}')
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
    clocations = ['⏩ Пропустить']
    if len(locations) > 0:
        for i in locations:
            line = str(i[0]) + ' ' + str(i[2])
            clocations.append(line)
        clocations.append('🆕 Добавить филиал')
        bot.send_message(
            message.chat.id,
            'Выберите филиал',
            reply_markup=buttons.Buttons(clocations)
        )
    bot.register_next_step_handler(message, NewTask.ntlocation2)

