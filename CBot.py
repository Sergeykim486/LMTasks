import os, config, telebot, functions, buttons, logging, time, pickle, asyncio, threading
from db import Database
from datetime import datetime
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Объявляем глобальные переменные
ActiveUser = {}
# Путь к базе
dbname = os.path.dirname(os.path.abspath(__file__)) + '/Database/' + 'lmtasksbase.db'
db = Database(dbname)
cols = [
    "id INTEGER PRIMARY KEY",
    "code INTEGER",
    "name TEXT",
    "person TEXT",
    "addr TEXT",
    "phone TEXT",
    "lang TEXT",
    "status TEXT",
    "mts TEXT"
]
db.create_table("Clients", cols)
cols2 = [
    "id INTEGER PRIMARY KEY",
    "date TEXT",
    "fromc INTEGER",
    "rev TEXT"
]
db.create_table("rev", cols2)
# Инициализируем токен бота
bot = telebot.TeleBot(config.TOKENC)

# Расписание для рассылки сообщений по утрам и вечерам
async def job():
    await schedule_message()
async def schedule_message():
    while True:
        logging.info('Проверка расписания')
        await asyncio.sleep(60)  # проверка каждую минуту
async def main():
    await job()

def sendtoall(message, markdown, exeptions, nt = 0, notific = False):
    global sendedmessages
    users = db.select_table('Clients')
    for user in users:
        logging.info(f'sended message to user {user[2]}')
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


@bot.message_handler(commands=['start'])

def send_welcome(message):
    user_id = message.chat.id
    global ActiveUser
    ActiveUser[message.chat.id] = {}
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    # Проверяем зарегистрирован ли текущий пользователь
    ActiveUser[message.chat.id]["id"] = message.chat.id
    finduser = db.search_record("Clients", "id", user_id)
    # Если пользователь не зарегистрирован
    if len(finduser) == 0:
        bot.send_message(
            user_id,
            "Plese select lnguge\nIltimos еilini tnlng\nПожалуйста выберите язык",
            reply_markup=buttons.Buttons(["🇬🇧 Englis", "🇺🇿 O'zbekcha", "🇸🇮 Русский"])
        )
        bot.register_next_step_handler(message, Reg.reg1)
    # Если пользователь зарегистрирован отправляем его в главное меню
    else:
        if db.get_record_by_id("Clients", user_id)[6] == "ru":
            ActiveUser[message.chat.id]["dict"] = config.ru
        elif db.get_record_by_id("Clients", user_id)[6] == "en":
            ActiveUser[message.chat.id]["dict"] = config.en
        elif db.get_record_by_id("Clients", user_id)[6] == "uz":
            ActiveUser[message.chat.id]["dict"] = config.uz
        bot.send_message(
            user_id,
            ActiveUser[message.chat.id]["dict"]["welcome"],
            reply_markup=buttons.Buttons([ActiveUser[user_id]["dict"]["newtask"], ActiveUser[user_id]["dict"]["mytasks"], ActiveUser[user_id]["dict"]["review"], ActiveUser[user_id]["dict"]["rate"], ActiveUser[user_id]["dict"]["settings"]],3)
        )
        bot.register_next_step_handler(message, Main.main1)

@bot.message_handler(func=lambda message: True)

def check_user_registered(message):
    user_id = message.chat.id
    global ActiveUser
    ActiveUser[message.chat.id] = {}
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    # Проверяем зарегистрирован ли текущий пользователь
    ActiveUser[message.chat.id]["id"] = message.chat.id
    finduser = db.search_record("Clients", "id", user_id)
    # Если пользователь не зарегистрирован
    if len(finduser) == 0:
        bot.send_message(
            user_id,
            "Plese select lnguge\nIltimos еilini tnlng\nПожалуйста выберите язык",
            reply_markup=buttons.Buttons(["🇬🇧 Englis", "🇺🇿 O'zbekcha", "🇸🇮 Русский"])
        )
        bot.register_next_step_handler(message, Reg.reg1)
    # Если пользователь зарегистрирован отправляем его в главное меню
    else:
        if db.get_record_by_id("Clients", user_id)[6] == "ru":
            ActiveUser[message.chat.id]["dict"] = config.ru
        elif db.get_record_by_id("Clients", user_id)[6] == "en":
            ActiveUser[message.chat.id]["dict"] = config.en
        elif db.get_record_by_id("Clients", user_id)[6] == "uz":
            ActiveUser[message.chat.id]["dict"] = config.uz
        bot.send_message(
            user_id,
            ActiveUser[message.chat.id]["dict"]["welcome"],
            reply_markup=buttons.Buttons([ActiveUser[user_id]["dict"]["newtask"], ActiveUser[user_id]["dict"]["mytasks"], ActiveUser[user_id]["dict"]["review"], ActiveUser[user_id]["dict"]["rate"], ActiveUser[user_id]["dict"]["settings"]],3)
        )
        bot.register_next_step_handler(message, Main.main1)

class Main():
    
    def main1(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == ActiveUser[message.chat.id]["dict"]["newtask"]:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["entertask"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, Main.confirmtask1)
        elif message.text == ActiveUser[message.chat.id]["dict"]["mytasks"]:
            filt = {'contragent': db.get_record_by_id("Clients", message.chat.id)[1], "status": 1, "status": 2}
            tasks = functions.listgen(db.select_table_with_filters('Tasks', filt), [0, 1, 3, 4, 6], 1)
            if len(tasks) != 0:
                for line in tasks:
                    bot.send_message(
                        message.chat.id,
                        line,
                        reply_markup=buttons.clearbuttons()
                    )
            else:
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["searchnone"],
                    reply_markup=buttons.clearbuttons()
                )
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["hi"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
            bot.register_next_step_handler(message, Main.main1)
        elif message.text == ActiveUser[message.chat.id]["dict"]["review"]:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["enterreview"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, Main.confirmval1)
        elif message.text == ActiveUser[message.chat.id]["dict"]["rate"]:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["rating"],
                reply_markup=buttons.Buttons(['5️⃣⭐️⭐️⭐️⭐️⭐️','4️⃣⭐️⭐️⭐️⭐️','3️⃣⭐️⭐️⭐️','2️⃣⭐️⭐️','1️⃣⭐️', '0️⃣'], 2)
            )
            bot.register_next_step_handler(message, Main.rate1)
        # elif message.text == ActiveUser[message.chat.id]["dict"]["settings"]:
        else:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["errorcom"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )

    def confirmval1(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]["review"] = message.text
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["confirm"] + '\n' + ActiveUser[message.chat.id]["dict"]["review"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["bsend"], ActiveUser[message.chat.id]["dict"]["bn"]])
        )
        bot.register_next_step_handler(message, Main.confirmval2)
    def confirmval2(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        db.insert_record(
            "rev",
            [
                None,
                datetime.now().strftime("%d.%m.%Y %H:%M"),
                db.get_record_by_id("Clients", message.chat.id)[1],
                ActiveUser[message.chat.id]["review"]
            ],
        )
        messs = str(ActiveUser[message.chat.id]["dict"]["success"]) + "\n" + str(ActiveUser[message.chat.id]["dict"]["hi"])
        bot.send_message(
            message.chat.id,
            messs,
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
        )
        bot.register_next_step_handler(message, Main.main1)

    def rate1(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]["rating"] = message.text
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["confirm"] + '\n' + ActiveUser[message.chat.id]["dict"]["rating"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["bsend"], ActiveUser[message.chat.id]["dict"]["bn"]])
        )
        bot.register_next_step_handler(message, Main.rate2)
    def rate2(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        db.insert_record(
            "rev",
            [
                None,
                datetime.now().strftime("%d.%m.%Y %H:%M"),
                db.get_record_by_id("Clients", message.chat.id)[1],
                ActiveUser[message.chat.id]["rating"]
            ],
        )
        messs = str(ActiveUser[message.chat.id]["dict"]["success"]) + "\n" + str(ActiveUser[message.chat.id]["dict"]["hi"])
        bot.send_message(
            message.chat.id,
            messs,
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
        )
        bot.register_next_step_handler(message, Main.main1)

    def confirmtask1(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]['task'] = message.text
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["confirm"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["by"], ActiveUser[message.chat.id]["dict"]["bn"]])
        )
        bot.register_next_step_handler(message, Main.confirmtask2)
    def confirmtask2(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == ActiveUser[message.chat.id]["dict"]["bn"]:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["hi"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
            bot.register_next_step_handler(message, Main.main1)
        elif message.text == ActiveUser[message.chat.id]["dict"]["by"]:
            task = [
                None,
                datetime.now().strftime("%d.%m.%Y %H:%M"),
                0,
                db.get_record_by_id("Clients", message.chat.id)[1],
                ActiveUser[message.chat.id]['task'],
                None,
                None,
                None,
                None,
                None,
                None,
                1
            ]
            db.insert_record('Tasks',task)
            tasknum = db.get_last_record("Tasks")[0]
            try:
                tasks = db.get_record_by_id("Clients", message.chat.id)[8]
            except Exception as e:
                tasks = str(tasknum)
                pass
            if tasknum != tasks:
                tasks = str(tasks) + ',' + str(tasknum)
            print(tasks)
            db.update_record('Clients', ['mts'], [tasks], 'id', message.chat.id)
            messs = ActiveUser[message.chat.id]["dict"]["success"] + "\n" + ActiveUser[message.chat.id]["dict"]["hi"]
            bot.send_message(
                message.chat.id,
                messs,
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
            bot.register_next_step_handler(message, Main.main1)
        else:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["errorcom"] + " " + ActiveUser[message.chat.id]["dict"]["confirm"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id][""]])
            )
            bot.register_next_step_handler(message, Main.confirmtask2)

class Reg:
    
    def reg1(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "🇬🇧 Englis":
            ActiveUser[message.chat.id]["lang"] = 'en'
            ActiveUser[message.chat.id]["dict"] = config.en
        elif message.text == "🇺🇿 O'zbekcha":
            ActiveUser[message.chat.id]["lang"] = 'uz'
            ActiveUser[message.chat.id]["dict"] = config.uz
        elif message.text == "🇸🇮 Русский":
            ActiveUser[message.chat.id]["lang"] = 'ru'
            ActiveUser[message.chat.id]["dict"] = config.ru
        logging.info(f"Для пользователя {message.chat.id} установлен язык {message.text}")
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["omporindivid"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["bcompany"], ActiveUser[message.chat.id]["dict"]["bindivid"]])
        )
        bot.register_next_step_handler(message, Reg.reg2)
        
    def reg2(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]["status"] = message.text
        if ActiveUser[message.chat.id]['status'] == ActiveUser[message.chat.id]["dict"]["bcompany"]:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["entercname"],
                reply_markup=buttons.clearbuttons()
            )
        else:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["entername"],
                reply_markup=buttons.clearbuttons()
            )
        bot.register_next_step_handler(message, Reg.reg3)
        
    def reg3(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]["name"] = message.text
        if ActiveUser[message.chat.id]['status'] == ActiveUser[message.chat.id]["dict"]["bcompany"]:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["enterinn"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, Reg.reg4)
        else:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["enterpinfl"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, Reg.reg5)
    
    def reg4(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]["code"] = message.text
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["enterperson"],
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Reg.reg5)
        
    def reg5(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if ActiveUser[message.chat.id]["status"] == ActiveUser[message.chat.id]["dict"]["bcompany"]:
            ActiveUser[message.chat.id]["person"] = message.text
        else:
            ActiveUser[message.chat.id]["code"] = message.chat.id
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["enteradr"],
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Reg.reg6)
        
    def reg6(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]["addr"] = message.chat.id
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["enterphone"],
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Reg.reg7)
        
    def reg7(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]["phone"] = message.chat.id
        if ActiveUser[message.chat.id]["status"] == ActiveUser[message.chat.id]["dict"]["bcompany"]:
            mess = "\n" + str(ActiveUser[message.chat.id]["dict"]["scname"]) + " " + str(ActiveUser[message.chat.id]["name"])
            mess = mess + "\n" + str(ActiveUser[message.chat.id]["dict"]["sperson"]) + " " + str(ActiveUser[message.chat.id]["person"])
        else:
            mess = "\n" + str(ActiveUser[message.chat.id]["dict"]["sname"]) + " " + str(ActiveUser[message.chat.id]["name"])
        mess = mess + "\n" + str(ActiveUser[message.chat.id]["dict"]["sadr"]) + " " + str(ActiveUser[message.chat.id]["addr"])
        mess = mess + "\n" + str(ActiveUser[message.chat.id]["dict"]["sphone"]) + " " + str(ActiveUser[message.chat.id]["phone"])
        mess = mess + "\n" + str(ActiveUser[message.chat.id]["dict"]["slang"]) + " " + str(ActiveUser[message.chat.id]["lang"])
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["confirm"] + mess,
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["by"], ActiveUser[message.chat.id]["dict"]["bn"]])
        )
        bot.register_next_step_handler(message, Reg.regsave)
        
    def regsave(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == ActiveUser[message.chat.id]["dict"]["by"]:
            db.insert_record(
                "Clients",
                [
                    message.chat.id,
                    ActiveUser[message.chat.id]["code"],
                    ActiveUser[message.chat.id]["name"],
                    ActiveUser[message.chat.id]["person"],
                    ActiveUser[message.chat.id]["addr"],
                    ActiveUser[message.chat.id]["phone"],
                    ActiveUser[message.chat.id]["lang"],
                    ActiveUser[message.chat.id]["status"],
                    ""
                ]
            )
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["success"] + "\n" + ActiveUser[message.chat.id]["dict"]["hi"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
            bot.register_next_step_handler(message, Main.main1)

@bot.callback_query_handler(func=lambda call: True)
# Реакция на кнопки
def callback_handler(call):
    # Реакция на инлайновые кнопки
    username = db.get_record_by_id("Clients", call.from_user.id)[1]
    logging.info(f"{username} нажал на кнопку {str(call)}")

# Запуск бота
if __name__ == '__main__':
    sendtoall('‼️‼️‼️Сервер бота был перезагружен...‼️‼️‼️\nНажмите кнопку "Перезапустить"', buttons.Buttons(['Перезапустить']), 0, 0, True)
    thread = threading.Thread(target=asyncio.run, args=(main(),))
    thread.start()
    bot.polling()
    # while True:
    #     try:
    #         bot.polling(none_stop=True, interval=0)
    #         logging.info()
    #     except Exception as e:
    #         logging.error(e)
    #         time.sleep(5)
