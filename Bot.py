import telebot, logging, time, datetime, asyncio, threading, Classes.functions as functions, Classes.buttons as buttons, Classes.schedule_operations as schedule
from Classes.Selected_task import Task
from datetime import datetime
from Classes.edit_contragent import editcont
from Classes.add_new_task import NewTask
from Classes.reports import report
from Classes.register_new_user import Reg
from Classes.config import ActiveUser, bot, sendedmessages, db
# логи
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Вспомогательная функция для обработки нажатий кнопок

def MenuReactions(message):

    if ActiveUser[message.chat.id]['Pause_main_handler'] == False or ActiveUser[message.chat.id]['Finishedop'] == True:
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
        if message.text == '📝 Новая заявка':
            ActiveUser[message.chat.id]['s'] = 0
            ActiveUser[message.chat.id]['nt'] = 1
            ActiveUser[message.chat.id]['Pause_main_handler'] = True
            ActiveUser[message.chat.id]['Finishedop'] = False
            if ActiveUser[message.chat.id]['block_nt1'] == False:
                ActiveUser[message.chat.id]['block_nt1'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = True
                NewTask.nt1(message)
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == '🔃 Обновить список заявок':
            ActiveUser[message.chat.id]['block_main_menu'] = True
            daterep = str(datetime.now().strftime("%d.%m.%Y"))
            report.rep(message, daterep, 0, 1, 1, 0, 0)
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '🖨️ Обновить список техники':
            ActiveUser[message.chat.id]['block_main_menu'] = True
            daterep = str(datetime.now().strftime("%d.%m.%Y"))
            report.rep(message, daterep, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '📋 Мои заявки':
            ActiveUser[message.chat.id]['block_main_menu'] = True
            daterep = str(datetime.now().strftime("%d.%m.%Y"))
            report.rep(message, daterep, 0, 1, 0, 1, 0, message.chat.id, 1)
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '📢 Написать всем':
            bot.send_message(
                message.chat.id,
                'Напишите Ваше сообщение и оно будет разослано всем.\nчтобы вернуться в главное меню нажмите [Главное меню]',
                reply_markup=buttons.Buttons(['🏠 Главное меню'])
            )
            bot.register_next_step_handler(message, allchats.chat1)
        elif message.text == '📈 Отчеты':
            ActiveUser[message.chat.id]['Pause_main_handler'] = True
            ActiveUser[message.chat.id]['Finishedop'] = False
            ActiveUser[message.chat.id]['block_main_menu'] = True
            report.reportall(message)
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == '✏️ Редактировать контрагента':
            ActiveUser[message.chat.id]['Pause_main_handler'] = True
            ActiveUser[message.chat.id]['Finishedop'] = False
            ActiveUser[message.chat.id]['block_main_menu'] = True
            bot.register_next_step_handler(message, MainMenu.Main2)
            editcont.ec1(message)
        elif message.text == '🗺️ Карта':
            ActiveUser[message.chat.id]['block_main_menu'] = True
            markup = telebot.types.InlineKeyboardMarkup()
            button = telebot.types.InlineKeyboardButton(text='Открыть карту', url='http://81.200.149.148/map.html')
            markup.add(button)
            bot.send_message(
                message.chat.id,
                'Вы можете посмотреть все теущие заявки за сегодня, на карте',
                reply_markup=markup
            )
            ActiveUser[message.chat.id]['block_main_menu'] = False
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == '/adduser':
            print('New user')
            bot.send_message(
                message.chat.id,
                'Укажите имя пользователя в формате - Имя Фамилия'
            )
            bot.register_next_step_handler(message, newusername)
        elif message.text == '/deluser':
            users = db.select_table('Users')
            btn = []
            for user in users:
                line = str(user[0]) + ' ' + str(user[2]) + ' ' + str(user[1])
                btn.append(line)
            bot.send_message(
                message.chat.id,
                'Выберите пользователя которого нужно удалить.',
                reply_markup=buttons.Buttons(btn,1)
            )
            bot.register_next_step_handler(message, deluser)
        elif message.text != None:
            if message.text.isdigit() or (len(message.text.split()) > 1 and message.text.split()[1].isdigit()):
                if message.text.isdigit():
                    taskid = message.text
                elif message.text.split()[1].isdigit():
                    taskid = message.text.split()[1]
                if taskid is not None:
                    task = db.get_record_by_id('Tasks', taskid)
                    print(task)
                    print(taskid)
                    if task != None:
                        tasks = functions.listgen([task], [0, 1, 3, 4, 6], 1)
                        if task != None:
                            bot.send_message(
                                message.chat.id,
                                tasks[0],
                                reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid],['ЛОКАЦИЯ', 'location '+taskid]])
                            )
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['block_main_menu'] = False
            bot.register_next_step_handler(message, MainMenu.Main2)
    elif message.text == '/start':
        print('main menu')
        ActiveUser[message.chat.id]['Pause_main_handler'] = False
        bot.send_message(
            message.chat.id,
            'Выберите операцию.',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        ActiveUser[message.chat.id]['block_main_menu'] = False
        bot.register_next_step_handler(message, MainMenu.Main2)
    else:
        ActiveUser[message.chat.id]['block_main_menu'] = False
        bot.register_next_step_handler(message, MainMenu.Main2)


# =====================================  С Т А Р Т   Б О Т А  =====================================

@bot.message_handler(commands=['start'])

# проверка пользователя при первом запуске
def handle_start(message):
    user_id = message.from_user.id
    try:
        username = db.get_record_by_id('Users', user_id)[2] + ' ' + db.get_record_by_id('Users', user_id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
    except Exception as e:
        logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
        pass
    user = db.get_record_by_id('Users', user_id)
    if user is None:
        bot.send_message(
            user_id,
            'Вы не зарегистрированы.',
            reply_markup=buttons.Buttons(['ок'])
        )
        bot.register_next_step_handler(message, handle_start)
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
    try:
        username = db.get_record_by_id('Users', user_id)[2] + ' ' + db.get_record_by_id('Users', user_id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
    except Exception as e:
        logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
        pass
    user = db.get_record_by_id('Users', user_id)
    if user is None:
        bot.send_message(
            user_id,
            'Вы не зарегистрированы.',
            reply_markup=buttons.Buttons(['ок'])
        )
        bot.stop_polling()
    else:
        MenuReactions(message)

# Главное меню и обработка кнопок главного меню
class MainMenu:
    def Main1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '🏠 Главное меню' or message.text == 'Вернуться':
            ActiveUser[message.chat.id]['sentmes'] = bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            bot.register_next_step_handler(message, MainMenu.Main2)
    # Реакия на кнопки главного меню
    def Main2(message):
        try:
            if ActiveUser[message.chat.id]['Pause_main_handler'] == False:
                username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
                logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        except Exception as e:
            pass
        if ActiveUser[message.chat.id]['block_main_menu'] == False:
            ActiveUser[message.chat.id]['block_main_menu'] = True
            MenuReactions(message)

# фильтр для запроса в базу
def filters(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
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

#add user admin
def newusername(message):
    fullname = message.text
    ActiveUser[message.chat.id]['NewUserFName'],ActiveUser[message.chat.id]['NewUserLname'] = fullname.split()
    bot.send_message(
        message.chat.id,
        'Укажите контактный номер телефона.'
    )
    bot.register_next_step_handler(message, newuserphone)

def newuserphone(message):
    ActiveUser[message.chat.id]['NewUserPhone'] = message.text
    bot.send_message(
        message.chat.id,
        'Перешлите мне любое сообщение от нового пользователя...'
    )
    bot.register_next_step_handler(message, newuserid)

def newuserid(message):
    ActiveUser[message.chat.id]['NewUserID'] = message.forward_from.id
    db.insert_record(
        'Users',
        [
            ActiveUser[message.chat.id]['NewUserID'],
            ActiveUser[message.chat.id]['NewUserFName'],
            ActiveUser[message.chat.id]['NewUserLname'],
            ActiveUser[message.chat.id]['NewUserPhone']
        ]
    )
    user_id = ActiveUser[message.chat.id]['NewUserID']
    last_name = ActiveUser[message.chat.id]['NewUserLname']
    first_name = ActiveUser[message.chat.id]['NewUserFName']
    ActiveUser[message.chat.id]['Pause_main_handler'] = False
    ActiveUser[user_id] = {}
    bot.send_message(
        message.chat.id,
            f"Пользователь:\n{user_id}\n"
            f"{last_name} {first_name}\n"
            f"Успешно добавлен в систему",
        reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
    )
    ActiveUser[message.chat.id]['block_main_menu'] = False
    bot.register_next_step_handler(message, MainMenu.Main2)


# delete user
def deluser(message):
    ActiveUser[message.chat.id]['Delid'] = message.text.split(' ', 1)[0]
    bot.send_message(
        message.chat.id,
        'Удалить пользователя?]',
        reply_markup=buttons.Buttons(['Да', 'Нет'],2)
    )
    bot.register_next_step_handler(message, deluser2)

def deluser2(message):
    if message.text == 'Да':
        db.delete_record('Users','id',ActiveUser[message.chat.id]['Delid'])
        if ActiveUser[message.chat.id]['Delid'] in ActiveUser:
            del ActiveUser[message.chat.id]['Delid']
            print(f"Сессия для пользователя {ActiveUser[message.chat.id]['Delid']} успешно удалена. 🗑️")
        else:
            print(f"Пользователя {ActiveUser[message.chat.id]['Delid']} не было в активных сессиях.")
        bot.send_message(
            message.chat.id,
            'Запись удалена. Выберите операцию.',
            reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
        )
        ActiveUser[message.chat.id]['block_main_menu'] = False
        bot.register_next_step_handler(message, MainMenu.Main2)
    else:
        print('del canceled.')
    bot.send_message(
        message.chat.id,
        'Выберите операцию.',
        reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
    )
    ActiveUser[message.chat.id]['block_main_menu'] = False
    bot.register_next_step_handler(message, MainMenu.Main2)


# общий чат (пересылка сообщения всем пользователям)
class allchats:
    # пересылка пользовательского сообщения всем
    def chat1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '🏠 Главное меню' or message.text == '/start':
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['block_main_menu'] = False
            functions.mesdel(message.chat.id, message.message_id)
            bot.register_next_step_handler(message, MainMenu.Main2)
        else:
            processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
            users = db.select_table('Users')
            for user in users:
                try:
                    # logging.info(f'\nℹ️ sended message to user {user[2]} {user[1]}')
                    if user[0] != message.chat.id:
                        bot.forward_message(user[0], message.chat.id, message.message_id)
                except Exception as e:
                    pass
            functions.mesdel(message.chat.id, processing.message_id)
            bot.send_message(
                message.chat.id,
                'Напишите Ваше сообщение и оно будет разослано всем.\nчтобы вернуться в главное меню нажмите [Главное меню]',
                reply_markup=buttons.Buttons(['🏠 Главное меню'])
            )
            bot.register_next_step_handler(message, allchats.chat1)

# =====================================  Р Е А К Ц И И   Н А   И Н Л А Й Н О В Ы Е   К Н О П К И  =====================================

@bot.callback_query_handler(func=lambda call: True)
# реакция на инлайновые кнопки
def callback_handler(call):
    try:
        username = db.get_record_by_id('Users', call.message.chat.id)[2] + ' ' + db.get_record_by_id('Users', call.message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Нажал на кнопку\n    -    [{call.data}]\n')
    except Exception as e:
        logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
        pass
    if ActiveUser[call.from_user.id]['Finishedop'] == True:
        bot.answer_callback_query(callback_query_id=call.id, text='👇🏻👇🏻👇🏻Прокрутите вниз...👇🏻👇🏻👇🏻', show_alert=False, cache_time=3)
        if call.data.split()[0] == 'location':
            task = db.get_record_by_id('Tasks', call.data.split()[1])
            if task[12] == None:
                bot.send_message(
                    call.from_user.id,
                    '<b>У данной заявки нет закрепленной локации!</b>', parse_mode='HTML'
                )
            else:
                location = db.get_record_by_id('Locations', task[12])
                lat = location[3]
                lon = location[4]
                loc = telebot.types.Location(lon, lat)
                # bot.send_location(call.from_user.id, loc.latitude, loc.longitude)
                bot.send_venue(call.from_user.id, loc.latitude, loc.longitude, f'ЗАЯВКА №{call.data.split()[1]}', f'От {db.get_record_by_id("Contragents", task[3])[1]}', 'Дополнительная информация о месте',reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+str(task[0])]]))
        else:
            # ActiveUser[call.from_user.id]['pressed'] = True
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
                print('step 1')
                if db.get_record_by_id('Tasks', call.data.split()[1])[11] == 5:
                    stat = 6
                else:
                    stat = 2
                print('step 2')
                st = 'status - ' + str(db.get_record_by_id('Tasks', call.data.split()[1])[11])
                print(st)
                if db.get_record_by_id('Tasks', call.data.split()[1])[11] != 1 and db.get_record_by_id('Tasks', call.data.split()[1])[11] != 5:
                    print('step 3')
                    functions.mesdel(call.from_user.id, processing.message_id)
                    bot.send_message(
                        call.from_user.id,
                        "Вы не можете принять эту заявку! ее уже принял " + db.get_record_by_id('Users', db.get_record_by_id('Tasks', call.data.split()[1])[6])[2] + ' ' + db.get_record_by_id('Users', db.get_record_by_id('Tasks', call.data.split()[1])[6])[1],
                        reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                    )
                else:
                    print('step 4')
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
                print('step 5')
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
            try:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            except Exception as e:
                logging.error(f'\n🆘 Попытка изменить не существующее сообщение!\n    ⚠️ - {e}\n')
                pass

# =====================================  Ц И К Л И Ч Е С К И Й   З А П У С К   Б О Т А  =====================================

if __name__ == '__main__':
    thread = threading.Thread(target=asyncio.run, args=(schedule.main(),))
    thread.start()
    # bot.polling()
while True:
    try:
        bot.polling()
    except Exception as e:
        logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
        pass

# bot.polling()