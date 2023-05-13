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
    "rev TEXT",
    "status INTEGER"
]
db.create_table("rev", cols2)
bot = telebot.TeleBot(config.TOKENC)

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

def settingsmes(userid):
    if ActiveUser[userid]['status'] == 'Организация':
        print('============= Ф И Р М А =============')
        mes = str(ActiveUser[userid]['dict']['binn']) + ':\n' + str(ActiveUser[userid]['code'])
        mes = mes + '\n' + str(ActiveUser[userid]['dict']['bcname']) + ':\n' + str(ActiveUser[userid]['name'])
        mes = mes + '\n' + str(ActiveUser[userid]['dict']['bperson']) + ':\n' + str(ActiveUser[userid]['person'])
        but = [
            ActiveUser[userid]['dict']['binn'],
            ActiveUser[userid]['dict']['bcname'],
            ActiveUser[userid]['dict']['bperson'],
            ActiveUser[userid]['dict']['badr'],
            ActiveUser[userid]['dict']['bphone'],
            ActiveUser[userid]['dict']['blang'],
            ActiveUser[userid]['dict']['bcancel'],
            ActiveUser[userid]['dict']['bsave']
        ]
    else:
        print('============= Ф И З Л И Ц О =============')
        mes = str(ActiveUser[userid]['dict']['bpinfl']) + ':\n' + str(ActiveUser[userid]['code'])
        mes = mes + '\n' + str(ActiveUser[userid]['dict']['bmyname']) + ':\n' + str(ActiveUser[userid]['name'])
        but = [
            ActiveUser[userid]['dict']['bpinfl'],
            ActiveUser[userid]['dict']['bmyname'],
            ActiveUser[userid]['dict']['badr'],
            ActiveUser[userid]['dict']['bphone'],
            ActiveUser[userid]['dict']['blang'],
            ActiveUser[userid]['dict']['bcancel'],
            ActiveUser[userid]['dict']['bsave']
        ]
    mes = mes + '\n' + str(ActiveUser[userid]['dict']['badr']) + ':\n' + str(ActiveUser[userid]['adr'])
    mes = mes + '\n' + str(ActiveUser[userid]['dict']['bphone']) + ':\n' + str(ActiveUser[userid]['phone'])
    mes = mes + '\n' + str(ActiveUser[userid]['dict']['blang']) + ':\n' + str(ActiveUser[userid]['lang']   )
    mes = mes + '\n\n' + str(ActiveUser[userid]['dict']['qtochange'])
    ActiveUser[userid]['settingsmes'] = bot.send_message(
        userid,
        mes,
        reply_markup=buttons.Buttons(but, 3)
    )

@bot.message_handler(commands=['start'])

def send_welcome(message):
    user_id = message.chat.id
    global ActiveUser
    ActiveUser[message.chat.id] = {}
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        pass
    ActiveUser[message.chat.id]["id"] = message.chat.id
    finduser = db.search_record("Clients", "id", user_id)
    if len(finduser) == 0:
        bot.send_message(
            user_id,
            f'Выберите язык / Tilini tanlang / Select language',
            reply_markup=buttons.Buttons(["🇬🇧 English", "🇺🇿 O'zbekcha", "🇷🇺 Русский"])
        )
        bot.register_next_step_handler(message, Reg.reg1)
    else:
        if db.get_record_by_id("Clients", message.chat.id)[6] == "ru":
            ActiveUser[message.chat.id]["dict"] = config.ru
        elif db.get_record_by_id("Clients", message.chat.id)[6] == "en":
            ActiveUser[message.chat.id]["dict"] = config.en
        elif db.get_record_by_id("Clients", message.chat.id)[6] == "uz":
            ActiveUser[message.chat.id]["dict"] = config.uz
        bot.send_message(
            user_id,
            ActiveUser[message.chat.id]["dict"]["welcome"],
            reply_markup=buttons.Buttons([ActiveUser[user_id]["dict"]["newtask"], ActiveUser[user_id]["dict"]["mytasks"], ActiveUser[user_id]["dict"]["review"], ActiveUser[user_id]["dict"]["rate"], ActiveUser[user_id]["dict"]["settings"]],3)
        )
        bot.register_next_step_handler(message, Main.main1)

@bot.message_handler(func=lambda message: True)

# def check_user_registered(message):
#     user_id = message.chat.id
#     global ActiveUser
#     ActiveUser[message.chat.id] = {}
#     try:
#         username = db.get_record_by_id('Clients', message.chat.id)[2]
#         logging.info(f'{username} Отправил запрос - {message.text}')
#     except Exception as e:
#         logging.error(e)
#         pass
#     # Проверяем зарегистрирован ли текущий пользователь
#     ActiveUser[message.chat.id]["id"] = message.chat.id
#     finduser = db.search_record("Clients", "id", user_id)
#     # Если пользователь не зарегистрирован
#     if len(finduser) == 0:
#         mesru = "НАШ БОТ БЫЛ ОБНОВЛЕН!\nПожалуйста пройдите короткую регистрацию. Это не займет много времени зато при подаче заявки не нужно каждый раз указывать одну и ту же информацию контактные данные к примеру и т. д.\nТак же Вы можете отслеживать статус своих заявок и какой мастер к вам приедет.\nЕсли есть вопросы - https://t.me/Sergey_kim486"
#         mesuz = "BIZNING BOTIMIZ YANGILANDI!\nIltimos, qisqa ro'yxatdan o'ting. Bu ko'p vaqt olmasa-da, masalan, har safar so'rovnoma topshirishda aloqador ma'lumotlarni kiritingiz kerak emas.\nSiz ham so'rovlaringiz holatini va qaysi usta sizga keladi, kuzatishingiz mumkin.\nAgar savollaringiz bo'lsa, https://t.me/Sergey_kim486 murojaat qiling."
#         mesen = "OUR BOT HAS BEEN UPDATED!\nPlease complete a short registration. It won't take much time but will save you from having to enter the same contact information every time you submit a request, for example.\nYou can also track the status of your requests and which master will come to you.\nIf you have any questions, please visit https://t.me/Sergey_kim486."
#         bot.send_message(
#             user_id,
#             f'{mesru}\n\n{mesuz}\n\n{mesen}\n\nВыберите язык / Tilini tanlang / Select language',
#             reply_markup=buttons.Buttons(["🇬🇧 Englis", "🇺🇿 O'zbekcha", "🇷🇺 Русский"])
#         )
#         bot.register_next_step_handler(message, Reg.reg1)
#     # Если пользователь зарегистрирован отправляем его в главное меню
#     else:
#         if db.get_record_by_id("Clients", user_id)[6] == "ru":
#             ActiveUser[message.chat.id]["dict"] = config.ru
#         elif db.get_record_by_id("Clients", user_id)[6] == "en":
#             ActiveUser[message.chat.id]["dict"] = config.en
#         elif db.get_record_by_id("Clients", user_id)[6] == "uz":
#             ActiveUser[message.chat.id]["dict"] = config.uz
#         bot.send_message(
#             user_id,
#             ActiveUser[message.chat.id]["dict"]["welcome"],
#             reply_markup=buttons.Buttons([ActiveUser[user_id]["dict"]["newtask"], ActiveUser[user_id]["dict"]["mytasks"], ActiveUser[user_id]["dict"]["review"], ActiveUser[user_id]["dict"]["rate"], ActiveUser[user_id]["dict"]["settings"]],3)
#         )
#         bot.register_next_step_handler(message, Main.main1)

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
            filt = {'contragent': db.get_record_by_id("Clients", message.chat.id)[1], 'status': [1, 2]}
            print(filt)
            tasks = functions.listgen(db.select_table_with_filters('Tasks', filt), [0, 1, 3, 4, 6], 1)
            if len(tasks) != 0:
                for line in tasks:
                    bot.send_message(
                        message.chat.id,
                        functions.curtask(line.split()[2]),
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
        elif message.text == ActiveUser[message.chat.id]["dict"]["settings"]:
            sett = db.get_record_by_id('Clients', message.chat.id)
            ActiveUser[message.chat.id]['code'] = sett[1]
            ActiveUser[message.chat.id]['name'] = sett[2]
            ActiveUser[message.chat.id]['person'] = sett[3]
            ActiveUser[message.chat.id]['adr'] = sett[4]
            ActiveUser[message.chat.id]['phone'] = sett[5]
            ActiveUser[message.chat.id]['lang'] = sett[6]
            ActiveUser[message.chat.id]['status'] = sett[7]
            print(ActiveUser[message.chat.id]['status'])
            settingsmes(message.chat.id)
            bot.register_next_step_handler(message, settings.set1)
        else:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["errorcom"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
            bot.register_next_step_handler(message, Main.main1)

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
                message.chat.id,
                ActiveUser[message.chat.id]["review"],
                0
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
                message.chat.id,
                ActiveUser[message.chat.id]["rating"],
                0
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
            message.text + '\n' + ActiveUser[message.chat.id]["dict"]["confirm"],
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
                0,
                None
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
            db.update_records('Clients', ['mts'], [tasks], 'id', message.chat.id)
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
            pass
        if message.text == "🇬🇧 English":
            ActiveUser[message.chat.id]["lang"] = 'en'
            ActiveUser[message.chat.id]["dict"] = config.en
        elif message.text == "🇺🇿 O'zbekcha":
            ActiveUser[message.chat.id]["lang"] = 'uz'
            ActiveUser[message.chat.id]["dict"] = config.uz
        elif message.text == "🇷🇺 Русский":
            ActiveUser[message.chat.id]["lang"] = 'ru'
            ActiveUser[message.chat.id]["dict"] = config.ru
        logging.info(f"Для пользователя {message.chat.id} установлен язык {message.text}")
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["omporindivid"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["bcompany"], ActiveUser[message.chat.id]["dict"]["bindivid"]])
        )
        bot.register_next_step_handler(message, Reg.comp1)
        
    def comp1(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            pass
        if message.text == ActiveUser[message.chat.id]['dict']['bcompany']:
            logging.info('Выбрана фирма')
            ActiveUser[message.chat.id]["status"] = 'Организация'
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["contractifno"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]['bskip']])
            )
            bot.register_next_step_handler(message, Reg.reg2)
        elif message.text == ActiveUser[message.chat.id]['dict']['bindivid']:
            logging.info('Выбрано физ лицо')
            ActiveUser[message.chat.id]["status"] = 'Физлицо'
            ActiveUser[message.chat.id]["contract"] = '...'
            ActiveUser[message.chat.id]['type'] = 3
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["entername"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, Reg.reg3)
        else:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["errorcom"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
            bot.register_next_step_handler(message, settings.set1)
    
    def reg2(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            pass
        if ActiveUser[message.chat.id]["status"] == 'Организация' and message.text != ActiveUser[message.chat.id]["dict"]["bskip"]:
            ActiveUser[message.chat.id]["contract"] = message.text
            ActiveUser[message.chat.id]['type'] = 2
        else:
            ActiveUser[message.chat.id]["contract"] = None
            ActiveUser[message.chat.id]["type"] = 1
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["entercname"],
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Reg.reg3)
        
    def reg3(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            pass
        ActiveUser[message.chat.id]["name"] = message.text
        if ActiveUser[message.chat.id]['status'] == 'Организация':
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
            pass
        if ActiveUser[message.chat.id]["status"] == 'Организация':
            ActiveUser[message.chat.id]["person"] = message.text
        else:
            ActiveUser[message.chat.id]["code"] = message.chat.id
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["enteradr"],
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, reg6)
        
    def reg7(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]["phone"] = message.text
        if ActiveUser[message.chat.id]["status"] == 'Организация':
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
            contragent = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]["code"])
            if contragent is None:
                contract = ActiveUser[message.chat.id]["contract"]
                db.insert_record(
                    'Contragents',
                    [
                        ActiveUser[message.chat.id]['code'],
                        ActiveUser[message.chat.id]['name'],
                        ActiveUser[message.chat.id]['addr'],
                        ActiveUser[message.chat.id]['person'],
                        ActiveUser[message.chat.id]['phone'],
                        ActiveUser[message.chat.id]['type'],
                        contract
                    ]
                )
            else:
                cl = db.get_record_by_id("Contragents", ActiveUser[message.chat.id]['code'])
                print(f"Зарегистрировался существующий клиент - контрагент {cl}")
                db.update_records(
                    'Contragents',
                    [
                        'cadr',
                        'cperson',
                        'cphone'
                    ],
                    [
                        str(cl[2]) + '\n' + str(ActiveUser[message.chat.id]['addr']),
                        str(cl[3]) + ', ' + str(ActiveUser[message.chat.id]['person']),
                        str(cl[4]) + ', ' + str(ActiveUser[message.chat.id]['phone'])
                    ],
                    'id',
                    cl[1]
                )
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["success"] + "\n" + ActiveUser[message.chat.id]["dict"]["hi"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
            bot.register_next_step_handler(message, Main.main1)
        elif message.text == ActiveUser[message.chat.id]["dict"]["bn"]:
            bot.send_message(
                message.chat.id,
                f"Пожалуйста пройдите регистрацию.\nIltimos ro'yxatdan o'ting\nRegister first please/\n\nВыберите язык / Tilini tanlang / Select language",
                reply_markup=buttons.Buttons(["🇬🇧 English", "🇺🇿 O'zbekcha", "🇷🇺 Русский"])
            )
            bot.register_next_step_handler(message, Reg.reg1)
        else:
            bot.register_next_step_handler(message, Reg.regsave)

class settings:
    def set1(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == ActiveUser[message.chat.id]['dict']['bsave']:
            if ActiveUser[message.chat.id]['status'] == 'Организация':
                person = ActiveUser[message.chat.id]['person']
            else:
                person = '...'
            db.update_records(
                'Clients',
                [
                    'code',
                    'name',
                    'person',
                    'addr',
                    'phone',
                    'lang',
                    'status'
                ],
                [
                    ActiveUser[message.chat.id]['code'],
                    ActiveUser[message.chat.id]['name'],
                    person,
                    ActiveUser[message.chat.id]['adr'],
                    ActiveUser[message.chat.id]['phone'],
                    ActiveUser[message.chat.id]['lang'],
                    ActiveUser[message.chat.id]['status']
                ],
                'id',
                message.chat.id
            )
            if db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['code']) == None:
                db.insert_record(
                    'Contragents',
                    [
                        ActiveUser[message.chat.id]['code'],
                        ActiveUser[message.chat.id]['name'],
                        ActiveUser[message.chat.id]['adr'],
                        person,
                        ActiveUser[message.chat.id]['phone']
                    ]
                )
            else:
                db.update_records(
                    'Contragents',
                    [
                        'cadr',
                        'cperson',
                        'cphone'
                    ],
                    [
                        ActiveUser[message.chat.id]['adr'],
                        person,
                        ActiveUser[message.chat.id]['phone']
                    ],
                    'id',
                    message.chat.id
                )
            if db.get_record_by_id("Clients", message.chat.id)[6] == "ru":
                ActiveUser[message.chat.id]["dict"] = config.ru
            elif db.get_record_by_id("Clients", message.chat.id)[6] == "en":
                ActiveUser[message.chat.id]["dict"] = config.en
            elif db.get_record_by_id("Clients", message.chat.id)[6] == "uz":
                ActiveUser[message.chat.id]["dict"] = config.uz
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
            bot.register_next_step_handler(message, Main.main1)
        elif message.text == ActiveUser[message.chat.id]['dict']['bcancel']:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["hi"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
            bot.register_next_step_handler(message, Main.main1)
        elif message.text == ActiveUser[message.chat.id]['dict']['binn']:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["enterinn"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, settings.inn)
        elif message.text == ActiveUser[message.chat.id]['dict']['bpinfl']:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["enterpinfl"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, settings.pinfl)
        elif message.text == ActiveUser[message.chat.id]['dict']['bmyname']:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["entername"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, settings.myname)
        elif message.text == ActiveUser[message.chat.id]['dict']['bcname']:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["entercname"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, settings.cname)
        elif message.text == ActiveUser[message.chat.id]['dict']['bperson']:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["enterperson"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, settings.person)
        elif message.text == ActiveUser[message.chat.id]['dict']['badr']:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["enteradr"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, adr)
        elif message.text == ActiveUser[message.chat.id]['dict']['bphone']:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["enterphone"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, settings.phone)
        elif message.text == ActiveUser[message.chat.id]['dict']['blang']:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["selectlang"],
                reply_markup=buttons.Buttons(["🇬🇧 English", "🇺🇿 O'zbekcha", "🇷🇺 Русский"])
            )
            bot.register_next_step_handler(message, settings.lang)
        else:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["errorcom"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
            bot.register_next_step_handler(message, settings.set1)

    def inn(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]['code'] = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
        settingsmes(message.chat.id)
        bot.register_next_step_handler(message, settings.set1)
    def pinfl(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]['code'] = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
        settingsmes(message.chat.id)
        bot.register_next_step_handler(message, settings.set1)
    def myname(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]['name'] = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
        settingsmes(message.chat.id)
        bot.register_next_step_handler(message, settings.set1)
    def cname(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]['name'] = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
        settingsmes(message.chat.id)
        bot.register_next_step_handler(message, settings.set1)
    def person(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]['person'] = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
        settingsmes(message.chat.id)
        bot.register_next_step_handler(message, settings.set1)
    def phone(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        ActiveUser[message.chat.id]['phone'] = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
        settingsmes(message.chat.id)
        bot.register_next_step_handler(message, settings.set1)
    def lang(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "🇬🇧 English":
            ActiveUser[message.chat.id]["lang"] = 'en'
        elif message.text == "🇺🇿 O'zbekcha":
            ActiveUser[message.chat.id]["lang"] = 'uz'
        elif message.text == "🇷🇺 Русский":
            ActiveUser[message.chat.id]["lang"] = 'ru'
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
        settingsmes(message.chat.id)
        bot.register_next_step_handler(message, settings.set1)

@bot.message_handler(content_types=['text', 'location'])

def reg6(message):
    global ActiveUser
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        pass
    if message.content_type == 'location':
        lon, lat = message.location.longitude, message.location.latitude
        url = f'GOOGLE: https://www.google.com/maps/search/?api=1&query={lat},{lon}'
        ActiveUser[message.chat.id]['addr'] = url
    else:
        ActiveUser[message.chat.id]['addr'] = message.text
    bot.send_message(
        message.chat.id,
        ActiveUser[message.chat.id]["dict"]["enterphone"],
        reply_markup=buttons.clearbuttons()
    )
    bot.register_next_step_handler(message, Reg.reg7)

def adr(message):
    global ActiveUser
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    if message.content_type == 'location':
        lon, lat = message.location.longitude, message.location.latitude
        url = f'GOOGLE: https://www.google.com/maps/search/?api=1&query={lat},{lon}'
        ActiveUser[message.chat.id]['adr'] = url
    else:
        ActiveUser[message.chat.id]['adr'] = message.text
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
    settingsmes(message.chat.id)
    bot.register_next_step_handler(message, settings.set1)

@bot.callback_query_handler(func=lambda call: True)
# Реакция на кнопки
def callback_handler(call):
    # Реакция на инлайновые кнопки
    username = db.get_record_by_id("Clients", call.from_user.id)[1]
    logging.info(f"{username} нажал на кнопку {str(call)}")

# Запуск бота
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
