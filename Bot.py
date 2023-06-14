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

def MenuReactions(message):

    if ActiveUser[message.chat.id]['Pause_main_handler'] == False or ActiveUser[message.chat.id]['Finishedop'] == True:
        if ActiveUser[message.chat.id]['Pause_main_handler'] == True:
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = False
        if message.text == '📝 Новая заявка':
            ActiveUser[message.chat.id]['nt'] = 1
            ActiveUser[message.chat.id]['Pause_main_handler'] = True
            ActiveUser[message.chat.id]['Finishedop'] = False
            if ActiveUser[message.chat.id]['block_nt1'] == False:
                ActiveUser[message.chat.id]['block_nt1'] = True
                NewTask.nt1(message)
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == '🔃 Обновить список заявок':
            daterep = str(datetime.now().strftime("%d.%m.%Y"))
            report.rep(message, daterep, 0, 1, 1, 0, 0)
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '🖨️ Обновить список техники':
            daterep = str(datetime.now().strftime("%d.%m.%Y"))
            report.rep(message, daterep, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1)
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '📋 Мои заявки':
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
            report.reportall(message)
            bot.register_next_step_handler(message, MainMenu.Main2)
        elif message.text == '✏️ Редактировать контрагента':
            ActiveUser[message.chat.id]['Pause_main_handler'] = True
            ActiveUser[message.chat.id]['Finishedop'] = False
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
            ActiveUser[message.chat.id]['block_main_menu'] = False
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
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    ActiveUser[user_id] = {'id': user_id}
    ActiveUser[user_id]['Pause_main_handler'] = False
    ActiveUser[user_id]['Finishedop'] = False
    ActiveUser[user_id]['block_main_menu'] = False
    ActiveUser[user_id]['block_nt1'] = False
    user = db.get_record_by_id('Users', user_id)
    if user is None:
        bot.send_message(
            user_id,
            'Вы не зарегистрированы.',
            reply_markup=buttons.Buttons(['ок'])
        )
        bot.register_next_step_handler(message, handle_start)
        # bot.send_message(
        #     user_id,
        #     'Вы не зарегистрированы.',
        #     reply_markup=buttons.Buttons(['🔑 Регистрация'])
        # )
        # ActiveUser[message.chat.id]['Pause_main_handler'] = True
        # ActiveUser[message.chat.id]['Finishedop'] = False
        # bot.register_next_step_handler(message, Reg.reg1)
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
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    ActiveUser[user_id]['Finishedop'] = True
    ActiveUser[user_id]['Pause_main_handler'] = False
    ActiveUser[user_id]['block_main_menu'] = False
    ActiveUser[user_id]['block_nt1'] = False
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
        logging.info(f'{username} Отправил запрос - {message.text}')
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
                logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            pass
        if ActiveUser[message.chat.id]['block_main_menu'] == False:
            ActiveUser[message.chat.id]['block_main_menu'] = True
            MenuReactions(message)

# фильтр для запроса в базу
def filters(message):
    username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
    logging.info(f'{username} Отправил запрос - {message.text}')
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
            ActiveUser[message.chat.id]['block_main_menu'] = False
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

if __name__ == '__main__':
    # functions.sendtoall('‼️‼️‼️Сервер бота был перезагружен...‼️‼️‼️\nНажмите кнопку "/start"', buttons.Buttons(['/start']), 0, 0, True)
    users = db.select_table('Users')
    for user in users:
        ActiveUser[user[0]]= {'id': user[0]}
        ActiveUser[user[0]]['block_main_menu'] = False
        ActiveUser[user[0]]['block_nt1'] = False
    thread = threading.Thread(target=asyncio.run, args=(schedule.main(),))
    thread.start()

# bot.polling()

try:
    bot.polling()
except Exception as e:
    logging.error(e)
    pass