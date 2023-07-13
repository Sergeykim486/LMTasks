import logging, telebot, time
import Classes.functions as functions
import Classes.buttons as buttons
from datetime import datetime
from Classes.config import ActiveUser, bot, sendedmessages, db, mainclass

# Редактирование контрагента
class editcont():   
    
    def __init__(self, main):
        self.bot = main

    # Поиск контрагента по ИНН и генераия основной формы def editcontragent(message)
    def ec1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        global ActiveUser
        if message.text == '🚫 Отмена' or message.text == '/start':
            functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text.split()[0].isdigit():
            inn = message.text.split()[0]
            ActiveUser[message.chat.id]['inn'] = inn
            client = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['inn'])
            ActiveUser[message.chat.id]['contold'] = client
            ActiveUser[message.chat.id]['contnew'] = []
            for line in client:
                if line is None:
                    ActiveUser[message.chat.id]['contnew'].append(None)
                else:
                    ActiveUser[message.chat.id]['contnew'].append(line)
            if client != None:
                editcont.editcontragent(message)
                bot.register_next_step_handler(message, editcont.ec2)
            else:
                bot.send_message(
                    message.chat.id,
                    'Контрагент не найден.',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
                ActiveUser[message.chat.id]['Pause_main_handler'] = False
                ActiveUser[message.chat.id]['Finishedop'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
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
                    logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
                    pass
            else:
                functions.mesdel(message.chat.id, processing.message_id)
                ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                    message.chat.id,
                    'Введите ИНН клиента.\nИли вы можете поискать по названию',
                    reply_markup=buttons.Buttons(['🚫 Отмена'])
                )
            bot.register_next_step_handler(message, editcont.ec1)

    # Реакция на нажатие кнопок в меню редактирования
    def ec2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        global ActiveUser
        if message.text == '💾 Сохранить':
            print(ActiveUser[message.chat.id]['contnew'])
            if ActiveUser[message.chat.id]['contnew'][0] != ActiveUser[message.chat.id]['contold'][0]:
                tasks = db.select_table_with_filters('Tasks', {'contragent': ActiveUser[message.chat.id]['contold'][0]})
                for task in tasks:
                    db.update_records(
                        'Tasks',
                        ['contragent'],
                        [ActiveUser[message.chat.id]['contnew'][0]],
                        'id',
                        task[0]
                    )
                locations = db.select_table_with_filters('Locations', {'inn': ActiveUser[message.chat.id]['contold'][0]})
                for location in locations:
                    db.update_records(
                        'Locations',
                        ['inn'],
                        [ActiveUser[message.chat.id]['contnew'][0]],
                        'id',
                        location[0]
                    )
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
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '🚫 Отмена' or message.text == '/start':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            try:
                mes = ActiveUser[message.chat.id]['edcon']
                functions.mesdel(mes.chat.id, mes.message_id)
            except Exception as e:
                pass
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '🏷️ ТИП':
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                f'Введите новое значение ({message.text})',
                reply_markup=buttons.Buttons(['Разовый', 'Долгосрочный', 'Физ. лицо'])
            )
            bot.register_next_step_handler(message, editcont.TYPE)
        elif message.text == '🛣️ АДРЕС':
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Введите новый адрес или отправьте локацию.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, CADR1)
        elif message.text == '📍 ЛОКАЦИИ':
            # ИЗМЕНЕНИЕ ЛОКАЦИЙ КОНТРАГЕНТА
            locations = db.select_table_with_filters('Locations', {'inn': ActiveUser[message.chat.id]['inn']})
            buttonsloc = []
            buttonsloc.append('🆕 Добавить')
            try:
                for location in locations:
                    buttonsloc.append(str(location[0]) + ' ' + str(location[2]))
            except Exception as e:
                logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
                time.sleep(5)
            buttonsloc.append('↩️ Назад')
            if len(locations) > 2:
                bot.send_message(
                    message.chat.id,
                    'Это все локации выберите ту которую хотите изменить.',
                    reply_markup=buttons.Buttons(buttonsloc, 2)
                )
                bot.register_next_step_handler(message, editcont.locations1)
            else:
                bot.send_message(
                    message.chat.id,
                    'Для выбранного контрагента не указаны локации.',
                    reply_markup=buttons.Buttons(buttonsloc, 2)
                )
                bot.register_next_step_handler(message, editcont.locations1)
        else:
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                f'Введите новое значение ({message.text})',
                reply_markup=buttons.clearbuttons()
            )
            if message.text == '🆔 ИНН':
                bot.register_next_step_handler(message, editcont.INN)
            elif message.text == '🏢 НАИМЕНОВАНИЕ':
                bot.register_next_step_handler(message, editcont.CNAME)
            elif message.text == '🙋‍♂️ КОНТАКТНОЕ ЛИЦО':
                bot.register_next_step_handler(message, editcont.CPERSON)
            elif message.text == '📞 ТЕЛЕФОН':
                bot.register_next_step_handler(message, editcont.CPHONE)
            elif message.text == '📄 ДОГОВОР':
                bot.register_next_step_handler(message, editcont.CCONTRACT)

    # ИНН
    def INN(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            if message.text.isdigit():
                ActiveUser[message.chat.id]['contnew'][0] = message.text
                editcont.editcontragent(message)
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
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            ActiveUser[message.chat.id]['contnew'][1] = message.text
            editcont.editcontragent(message)
            bot.register_next_step_handler(message, editcont.ec2)

    # Тип договора разовый или долгосрочный
    def TYPE(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            if message.text == 'Разовый':
                ActiveUser[message.chat.id]['contnew'][5] = 1
            elif message.text == 'Долгосрочный':
                ActiveUser[message.chat.id]['contnew'][5] = 2
            elif message.text == 'Физ. лицо':
                ActiveUser[message.chat.id]['contnew'][5] = 3
            editcont.editcontragent(message)
            bot.register_next_step_handler(message, editcont.ec2)

    # Контактное лио
    def CPERSON(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            ActiveUser[message.chat.id]['contnew'][3] = message.text
            editcont.editcontragent(message)
            bot.register_next_step_handler(message, editcont.ec2)

    # Контактный телефон
    def CPHONE(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            ActiveUser[message.chat.id]['contnew'][4] = message.text
            editcont.editcontragent(message)
            bot.register_next_step_handler(message, editcont.ec2)

    # Номер и дата договора (если долгосрочный)
    def CCONTRACT(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            ActiveUser[message.chat.id]['contnew'][6] = message.text
            editcont.editcontragent(message)
            bot.register_next_step_handler(message, editcont.ec2)

    # Меню и список локаций
    def locations1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            if message.text == '🆕 Добавить':
                bot.send_message(
                    message.chat.id,
                    'Отправьте локацию',
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, newlocation)
            elif message.text == '↩️ Назад':
                editcont.editcontragent(message)
                bot.register_next_step_handler(message, editcont.ec2)
            elif message.text.split()[0].isdigit() and db.get_record_by_id('Locations', message.text.split()[0]) != None:
                location = db.get_record_by_id('Locations', message.text.split()[0])
                loc = telebot.types.Location(location[4], location[3])
                bot.send_location(message.chat.id, loc.latitude, loc.longitude)
                ActiveUser[message.chat.id]['curlocation'] = location[0]
                bot.send_message(
                    message.chat.id,
                    f'Выбрана локация: {location[2]}',
                    reply_markup=buttons.Buttons(['Изменить локацию', 'Изменить название', '🗑️ Удалить', '🚫 Отмена'], 3)
                )
                bot.register_next_step_handler(message, editcont.locations2)
            else:
                bot.send_message(
                    message.chat.id,
                    'Не верная команда.'
                )
                bot.register_next_step_handler(message, editcont.locations1)

    # Редактирование выбранной локации
    def locations2(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        global ActiveUser
        if message.text == 'Изменить локацию':
            bot.send_message(
                message.chat.id,
                'Отправьте новую локацию.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, editcontlocation1)
        elif message.text == 'Изменить название':
            bot.send_message(
                message.chat.id,
                'Укажите новое название локации.',
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, editcont.locations3)
        elif message.text == '🗑️ Удалить':
            locationtodelete = db.get_record_by_id('Locations', ActiveUser[message.chat.id]['curlocation'])[2]
            Contrlocation = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['inn'])[1]
            bot.send_message(
                message.chat.id,
                f'Удалить локацию {locationtodelete} у {Contrlocation}?',
                reply_markup=buttons.Buttons(['✅ Да','⛔️ Нет'])
            )
            bot.register_next_step_handler(message, editcont.locations4)
        elif message.text == '🚫 Отмена' or message.text == '/start':
            locations = db.select_table_with_filters('Locations', {'inn': ActiveUser[message.chat.id]['inn']})
            buttonsloc = []
            buttonsloc.append('🆕 Добавить')
            try:
                for location in locations:
                    buttonsloc.append(str(location[0]) + ' ' + str(location[2]))
            except Exception as e:
                logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
                time.sleep(5)
            buttonsloc.append('↩️ Назад')
            if len(locations) > 2:
                bot.send_message(
                    message.chat.id,
                    'Это все локации выберите ту которую хотите изменить.',
                    reply_markup=buttons.Buttons(buttonsloc, 2)
                )
                bot.register_next_step_handler(message, editcont.locations1)
            else:
                bot.send_message(
                    message.chat.id,
                    'Для выбранного контрагента не указаны локации.',
                    reply_markup=buttons.Buttons(buttonsloc, 2)
                )
                bot.register_next_step_handler(message, editcont.locations1)

    # Сохранение имени новой локации
    def locations3(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
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
                reply_markup=buttons.Buttons(['Изменить локацию', 'Изменить название', '🗑️ Удалить', '🚫 Отмена'], 3)
            )
            bot.register_next_step_handler(message, editcont.locations2)

    # Удаление локации
    def locations4(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            if message.text == '✅ Да':
                db.delete_record('Locations', 'id', ActiveUser[message.chat.id]['curlocation'])
                bot.send_message(
                    message.chat.id,
                    'Локация удалена.',
                    reply_markup=buttons.clearbuttons()
                )
                editcont.editcontragent(message)
                bot.register_next_step_handler(message, editcont.ec2)
            elif message.text == '⛔️ Нет':
                bot.send_message(
                    message.chat.id,
                    'Удаление отменено.\nЧто вы хотите изменить?',
                    reply_markup=buttons.Buttons(['Изменить локацию', 'Изменить название', '🗑️ Удалить', '🚫 Отмена'], 3)
                )
                bot.register_next_step_handler(message, editcont.locations2)
            else:
                locationtodelete = db.get_record_by_id('Locations', ActiveUser[message.chat.id]['curlocation'])[2]
                Contrlocation = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['inn'])[1]
                bot.send_message(
                    message.chat.id,
                    f'Вы не подтвердили удаление.\nУдалить локацию {locationtodelete} у {Contrlocation}?',
                    reply_markup=buttons.Buttons(['✅ Да','⛔️ Нет'])
                )
                bot.register_next_step_handler(message, editcont.locations4)

    # основная форма рдактирования контрагента
    def editcontragent(message):
        try:
            mes = ActiveUser[message.chat.id]['edcon']
            functions.mesdel(mes.chat.id, mes.message_id)
        except Exception as e:
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
            reply_markup=buttons.Buttons(['🆔 ИНН', '🏢 НАИМЕНОВАНИЕ', '🏷️ ТИП', '🛣️ АДРЕС', '📍 ЛОКАЦИИ', '🙋‍♂️ КОНТАКТНОЕ ЛИЦО', '📞 ТЕЛЕФОН', '📄 ДОГОВОР', '💾 Сохранить', '🚫 Отмена'], 3)
        )
        return

# формирование гугл ссылки на карты по локации для адреса компании
def CADR1(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
    if message.text == '/start':
        functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
        bot.send_message(
            message.chat.id,
            'Выберите операцию.',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        ActiveUser[message.chat.id]['Pause_main_handler'] = False
        ActiveUser[message.chat.id]['Finishedop'] = True
        ActiveUser[message.chat.id]['block_main_menu'] = False
    else:
        if message.content_type == 'location':
            lon, lat = message.location.longitude, message.location.latitude
            url = f'GOOGLE: https://www.google.com/maps/search/?api=1&query={lat},{lon}'
            ActiveUser[message.chat.id]['contnew'][2] = url
        else:
            ActiveUser[message.chat.id]['contnew'][2] = message.text
        editcont.editcontragent(message)
        bot.register_next_step_handler(message, editcont.ec2)

# Изменение локаии контрагента
def editcontlocation1(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
    if message.text == '/start':
        functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
        bot.send_message(
            message.chat.id,
            'Выберите операцию.',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        ActiveUser[message.chat.id]['Pause_main_handler'] = False
        ActiveUser[message.chat.id]['Finishedop'] = True
        ActiveUser[message.chat.id]['block_main_menu'] = False
    else:
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
                reply_markup=buttons.Buttons(['Изменить локацию', 'Изменить название', '🗑️ Удалить', '🚫 Отмена'], 3)
            )
            bot.register_next_step_handler(message, editcont.locations2)
        else:
            bot.send_message(
                message.chat.id,
                'Вы должны были отправить локацию.\nОтправьте локацию.',
                reply_markup=buttons.clearbuttons
            )
            bot.register_next_step_handler(message, newlocation)

# Добавление новой локации в список локаций в редактировании контрагента
def newlocation(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
    if message.text == '/start':
        functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
        bot.send_message(
            message.chat.id,
            'Выберите операцию.',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        ActiveUser[message.chat.id]['Pause_main_handler'] = False
        ActiveUser[message.chat.id]['Finishedop'] = True
        ActiveUser[message.chat.id]['block_main_menu'] = False
    else:
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
    logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
    if message.text == '/start':
        functions.mesdel(ActiveUser[message.chat.id]['sentmes'].chat.id, ActiveUser[message.chat.id]['sentmes'].message_id)
        bot.send_message(
            message.chat.id,
            'Выберите операцию.',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        ActiveUser[message.chat.id]['Pause_main_handler'] = False
        ActiveUser[message.chat.id]['Finishedop'] = True
        ActiveUser[message.chat.id]['block_main_menu'] = False
    else:
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
        locations = db.select_table_with_filters('Locations', {'inn': ActiveUser[message.chat.id]['inn']})
        buttonsloc = []
        buttonsloc.append('🆕 Добавить')
        try:
            for location in locations:
                buttonsloc.append(str(location[0]) + ' ' + str(location[2]))
        except Exception as e:
            logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
            time.sleep(5)
        buttonsloc.append('↩️ Назад')
        if len(locations) > 2:
            bot.send_message(
                message.chat.id,
                'Это все локации выберите ту которую хотите изменить.',
                reply_markup=buttons.Buttons(buttonsloc, 2)
            )
        else:
            bot.send_message(
                message.chat.id,
                'Для выбранного контрагента не указаны локации.',
                reply_markup=buttons.Buttons(buttonsloc, 2)
            )
        bot.register_next_step_handler(message, editcont.locations1)

