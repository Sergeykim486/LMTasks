import os, Classes.config as config, telebot, Classes.functions as functions, Classes.buttons as buttons, logging, time, pickle, asyncio, threading
from Classes.db import Database
from datetime import datetime
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Объявляем глобальные переменные
from Classes.config import ActiveUser, sendedmessages, db, mainclass
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
db.create_table('ClTasks', ['id INTEGER PRIMARY KEY','inn INTEGER', 'Status INTEGER'])

async def job():
    await schedule_message()
async def schedule_message():
    while True:
        logging.info('Проверка расписания')
        tasks = db.select_table('ClTasks')
        for task in tasks:
            clients = db.select_table_with_filters('Clients', {'code': task[1]})
            t = db.get_record_by_id('Tasks', task[0])
            if task[2] != t[11]:
                for client in clients:
                    try:
                        if t[11] == 1:
                            if db.get_record_by_id("Clients", client[0])[6] == "ru":
                                mm = f"🔵 Ваша заявка № {task[0]} успешно зарегистрирована"
                            elif db.get_record_by_id("Clients", client[0])[6] == "en":
                                mm = f"🔵 Your request № {task[0]} has been successfully registered"
                            elif db.get_record_by_id("Clients", client[0])[6] == "uz":
                                mm = f"🔵 Sizning so'rovingiz № {task[0]} muvaffaqiyatli ro'yxatga olingan"
                            bot.send_message(
                                client[0],
                                mm
                            )
                        elif t[11] == 2:
                            master = db.get_record_by_id('Users', t[6])
                            mas = str(master[2]) + ' ' + str(master[1])
                            if db.get_record_by_id("Clients", client[0])[6] == "ru":
                                mm = f"🟡 Вашу заявку № {task[0]} Принял мастер: {mas}\nКонтактный телефон: {str(master[3])}"
                            elif db.get_record_by_id("Clients", client[0])[6] == "en":
                                mm = f"🟡 Your request № {task[0]} has been accepted by the master: {mas}\nContact phone: {str(master[3])}"
                            elif db.get_record_by_id("Clients", client[0])[6] == "uz":
                                mm = f"🟡 {task[0]}-raqamli so'rovingiz qabul qilindi\n ustasi: {mas}\nAloqa raqami: {str(master[3])}"
                            bot.send_message(
                                client[0],
                                mm
                            )
                        elif t[11] == 3:
                            master = db.get_record_by_id('Users', t[6])
                            mas = str(master[2]) + ' ' + str(master[1])
                            if db.get_record_by_id("Clients", client[0])[6] == "ru":
                                mm = f"🟢 Мастер {mas} завершил вашу заявку № {task[0]}."
                            elif db.get_record_by_id("Clients", client[0])[6] == "en":
                                mm = f"🟢 Master {mas} has completed your request № {task[0]}."
                            elif db.get_record_by_id("Clients", client[0])[6] == "uz":
                                mm = f"🟢 {mas} ustasi sizning {task[0]}-raqamli buyurtmangizni tugatdi."
                            bot.send_message(
                                client[0],
                                mm
                            )
                        elif t[11] == 4:
                            master = db.get_record_by_id('Users', t[6])
                            if master is None:
                                mas = '-'
                            else:
                                mas = str(master[2]) + ' ' + str(master[1])
                            canceled = db.get_record_by_id('Users', t[9])[2] + ' ' + db.get_record_by_id('Users', t[9])[1]
                            reson = t[10]
                            if db.get_record_by_id("Clients", client[0])[6] == "ru":
                                mm = f"🔴 Ваша заявка была отменена.\n№ {task[0]}\nМастер {mas}\nЗаявку отменил: {canceled}\nПричина:\n{reson}"
                            elif db.get_record_by_id("Clients", client[0])[6] == "en":
                                mm = f"🔴 Your request has been canceled.\n№ {task[0]}\nMaster: {mas}\nCanceled by: {canceled}\nReason:\n{reson}"
                            elif db.get_record_by_id("Clients", client[0])[6] == "uz":
                                mm = f"🔴 Sizning so'rovingiz bekor qilindi.\n№ {task[0]}\nUsta: {mas}\nBekor qilgan: {canceled}\nSabab:\n{reson}"
                            bot.send_message(
                                client[0],
                                mm
                            )
                    except Exception as e:
                        logging.error(e)
                        pass
                db.update_records(
                    'ClTasks',
                    ['status'],
                    [t[11]],
                    'id',
                    t[0]
                )
        await asyncio.sleep(30)  # проверка каждую минуту
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
            # ActiveUser[userid]['dict']['bcname'],
            ActiveUser[userid]['dict']['bperson'],
            ActiveUser[userid]['dict']['badr'],
            ActiveUser[userid]["dict"]["setmylocs"],
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
            ActiveUser[userid]["dict"]["setmylocs"],
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

def mainmenu(message):
    if message.text == ActiveUser[message.chat.id]["dict"]["newtask"]:
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["entertask"],
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Main.confirmtask0)
    elif message.text == ActiveUser[message.chat.id]["dict"]["mytasks"]:
        filt = {'contragent': db.get_record_by_id("Clients", message.chat.id)[1], 'status': 2, 'status': 1}
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
        cont = db.get_record_by_id('Contragents', sett[1])
        ActiveUser[message.chat.id]['type'] = cont[5]
        ActiveUser[message.chat.id]["contract"] = cont[6]
        print(ActiveUser[message.chat.id]['status'])
        settingsmes(message.chat.id)
        bot.register_next_step_handler(message, settings.set1)
    elif message.text == 'Sendtoall@labmono2858':
        bot.send_message(
            message.chat.id,
            'Напишите ваше сообщение.',
            reply_markup=buttons.Buttons(['Main Menu'])
        )
        bot.register_next_step_handler(message, allchats.chat1)
    else:
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["errorcom"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
        )
        bot.register_next_step_handler(message, Main.main1)

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
        ActiveUser[message.chat.id]["code"] = None
        ActiveUser[message.chat.id]["name"] = None
        ActiveUser[message.chat.id]["person"] = None
        ActiveUser[message.chat.id]["addr"] = None
        ActiveUser[message.chat.id]["phone"] = None
        ActiveUser[message.chat.id]["lang"] = None
        ActiveUser[message.chat.id]["status"] = None
        ActiveUser[message.chat.id]['code'] = None
        ActiveUser[message.chat.id]['name'] = None
        ActiveUser[message.chat.id]['addr'] = None
        ActiveUser[message.chat.id]['person'] = None
        ActiveUser[message.chat.id]['phone'] = None
        ActiveUser[message.chat.id]['type'] = None
        ActiveUser[message.chat.id]["contract"] = None
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

def check_user_id(message):
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
        ActiveUser[message.chat.id]["code"] = None
        ActiveUser[message.chat.id]["name"] = None
        ActiveUser[message.chat.id]["person"] = None
        ActiveUser[message.chat.id]["addr"] = None
        ActiveUser[message.chat.id]["phone"] = None
        ActiveUser[message.chat.id]["lang"] = None
        ActiveUser[message.chat.id]["status"] = None
        ActiveUser[message.chat.id]['code'] = None
        ActiveUser[message.chat.id]['name'] = None
        ActiveUser[message.chat.id]['addr'] = None
        ActiveUser[message.chat.id]['person'] = None
        ActiveUser[message.chat.id]['phone'] = None
        ActiveUser[message.chat.id]['type'] = None
        ActiveUser[message.chat.id]["contract"] = None
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
        mainmenu(message)

class Main():
    
    def main1(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        mainmenu(message)

    def confirmval1(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            bot.register_next_step_handler(message, Main.main1)
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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

    def confirmtask0(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            ActiveUser[message.chat.id]['task'] = message.text
            locations = db.select_table_with_filters('Locations', {'inn': db.get_record_by_id('Clients', message.chat.id)[1]})
            btns = []
            btns.append(ActiveUser[message.chat.id]["dict"]["locleave"])
            if len(locations) > 0:
                for loc in locations:
                    btns.append(str(loc[0]) + ' - ' + str(loc[2]))
            btns.append(ActiveUser[message.chat.id]["dict"]["locadd"])
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["locwhere"],
                reply_markup=buttons.Buttons(btns)
            )
            bot.register_next_step_handler(message, Main.confirmtask01)
    def confirmtask01(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            if message.text == ActiveUser[message.chat.id]["dict"]["locleave"]:
                ActiveUser[message.chat.id]['location'] = None
                bot.send_message(
                    message.chat.id,
                    message.text + '\n' + ActiveUser[message.chat.id]["dict"]["confirm"],
                    reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["by"], ActiveUser[message.chat.id]["dict"]["bn"]])
                )
                bot.register_next_step_handler(message, Main.confirmtask2)
            elif message.text == ActiveUser[message.chat.id]["dict"]["locadd"]:
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["locsendloc"],
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, ntnl)
            elif len(message.text.split()) > 1 and (message.text.split()[0].isdigit):
                ActiveUser[message.chat.id]['location'] = int(message.text.split()[0])
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
                    ActiveUser[message.chat.id]['location']
                ]
                db.insert_record('Tasks',task)
                tasknum = db.get_last_record("Tasks")[0]
                db.insert_record(
                    'ClTasks',
                    [
                        tasknum,
                        db.get_record_by_id("Clients", message.chat.id)[1],
                        0
                    ]
                )
                # try:
                #     tasks = db.get_record_by_id("Clients", message.chat.id)[8]
                # except Exception as e:
                #     tasks = str(tasknum)
                #     pass
                # if tasknum != tasks:
                #     tasks = str(tasks) + ',' + str(tasknum)
                # print(tasks)
                # db.update_records('Clients', ['mts'], [tasks], 'id', message.chat.id)
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            ActiveUser[message.chat.id]["contract"] = message.text
            ActiveUser[message.chat.id]['type'] = 2
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
                    reply_markup=buttons.Buttons([ActiveUser[message.chat.id]['dict']['bskip']])
                )
                bot.register_next_step_handler(message, Reg.reg5)
    
    def reg4(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            if message.text.isdigit():
                ActiveUser[message.chat.id]["code"] = message.text
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["enterperson"],
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, Reg.reg5)
            else:
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]['dict']['innerror'],
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, Reg.reg4)
        
    def reg5(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            if message.text.isdigit():
                if ActiveUser[message.chat.id]["status"] == 'Организация':
                    ActiveUser[message.chat.id]["person"] = message.text
                else:
                    ActiveUser[message.chat.id]["code"] = message.text
                    ActiveUser[message.chat.id]["person"] = '...'
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["enteradr"],
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, reg6)
            elif message.text == ActiveUser[message.chat.id]['dict']['bskip']:
                first = 20230001
                finded = 1
                while finded == 1:
                    cont = db.select_table_with_filters('Contragents', {'id': first})
                    if cont == None:
                        finded = 0
                    else:
                        first = first + 1
                if ActiveUser[message.chat.id]["status"] == 'Организация':
                    ActiveUser[message.chat.id]["person"] = first
                else:
                    ActiveUser[message.chat.id]["code"] = first
                    ActiveUser[message.chat.id]["person"] = '...'
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["enteradr"],
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, reg6)
            else:
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]['dict']['innerror'],
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, Reg.reg5)
        
    def reg7(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
                        None
                    ]
                )
                contragent = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]["code"])
                if contragent is None:
                    db.insert_record(
                        'Contragents',
                        [
                            ActiveUser[message.chat.id]['code'],
                            ActiveUser[message.chat.id]['name'],
                            ActiveUser[message.chat.id]['addr'],
                            ActiveUser[message.chat.id]['person'],
                            ActiveUser[message.chat.id]['phone'],
                            ActiveUser[message.chat.id]['type'],
                            ActiveUser[message.chat.id]["contract"]
                        ]
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            if message.text == ActiveUser[message.chat.id]['dict']['bsave']:
                if ActiveUser[message.chat.id]['status'] == 'Организация':
                    person = str(ActiveUser[message.chat.id]['person'])
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
                if db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['code']) is None:
                    db.insert_record(
                        'Contragents',
                        [
                            ActiveUser[message.chat.id]['code'],
                            ActiveUser[message.chat.id]['name'],
                            ActiveUser[message.chat.id]['adr'],
                            person,
                            ActiveUser[message.chat.id]['phone'],
                            None,
                            None
                        ]
                    )
                else:
                    cont = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['code'])
                    if cont is not None:
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
                            cont[0]
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
            elif message.text == ActiveUser[message.chat.id]["dict"]["setmylocs"]:
                usercode = db.get_record_by_id('Clients', message.chat.id)[1]
                locs = db.select_table_with_filters('Locations', {'inn': usercode})
                if len(locs) > 0:
                    for location in locs:
                        loc = telebot.types.Location(location[4], location[3])
                        bot.send_venue(
                            message.chat.id,
                            loc.latitude,
                            loc.longitude,
                            str(location[2]),
                            '',
                            reply_markup=buttons.buttonsinline([[ActiveUser[message.chat.id]["dict"]["setchange"], 'location '+str(location[0])]])
                            )
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["setmestochange"],
                    reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["locadd"], ActiveUser[message.chat.id]["dict"]["bcancel"]])
                )
                bot.register_next_step_handler(message, settings.locations1)
            else:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
                settingsmes(message.chat.id)
                bot.register_next_step_handler(message, settings.set1)

    def locations1(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            if message.text == ActiveUser[message.chat.id]["dict"]["locadd"]:
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["locsendloc"],
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, setloc1)
            elif message.text == ActiveUser[message.chat.id]["dict"]["bcancel"]:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
                settingsmes(message.chat.id)
                bot.register_next_step_handler(message, settings.set1)

    def locations2(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            if message.text == ActiveUser[message.chat.id]["dict"]["setlocationch"]:
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["locsendloc"],
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, setloc3)
            elif message.text == ActiveUser[message.chat.id]["dict"]["setnameloc"]:
                bot.send_message(
                    message.chat.id,
                    "Введите название локации",
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, settings.locations3)
            elif message.text == ActiveUser[message.chat.id]["dict"]["setdelete"]:
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["setconf"],
                    reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["by"], ActiveUser[message.chat.id]["dict"]["bn"]])
                )
                bot.register_next_step_handler(message, settings.locations4)
            elif message.text == ActiveUser[message.chat.id]["dict"]["bcancel"]:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
                settingsmes(message.chat.id)
                bot.register_next_step_handler(message, settings.set1)
    def locations3(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
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
                ActiveUser[message.chat.id]["dict"]["success"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["setlocationch"], ActiveUser[message.chat.id]["dict"]["setnameloc"], ActiveUser[message.chat.id]["dict"]["setdelete"], ActiveUser[message.chat.id]["dict"]["bcancel"]])
            )
            bot.register_next_step_handler(message, settings.locations2)
    def locations4(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            if message.text == ActiveUser[message.chat.id]["dict"]["by"]:
                db.delete_record('Locations', 'id', ActiveUser[message.chat.id]['curlocation'])
                bot.send_message(
                    message.chat.id,
                    "Локация удалена.",
                    reply_markup=buttons.clearbuttons()
                )
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
                settingsmes(message.chat.id)
                bot.register_next_step_handler(message, settings.set1)
            elif message.text == ActiveUser[message.chat.id]["dict"]["bn"]:
                bot.send_message(
                    message.chat.id,
                    "Операция отменена.",
                    reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["setlocationch"], ActiveUser[message.chat.id]["dict"]["setnameloc"], ActiveUser[message.chat.id]["dict"]["setdelete"], ActiveUser[message.chat.id]["dict"]["bcancel"]])
                )
                bot.register_next_step_handler(message, settings.locations2)
            else:
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["setconf2"],
                    reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["by"], ActiveUser[message.chat.id]["dict"]["bn"]])
                )
                bot.register_next_step_handler(message, settings.locations4)

    def inn(message):
        global ActiveUser
        try:
            username = db.get_record_by_id('Clients', message.chat.id)[2]
            logging.info(f'{username} Отправил запрос - {message.text}')
        except Exception as e:
            logging.error(e)
            pass
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            ActiveUser[message.chat.id]['code'] = message.text
            if db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['code']) is None:
                bot.send_message(
                    message.chat.id,
                    ActiveUser[message.chat.id]["dict"]["entercname"],
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, settings.cname)
            else:
                cont = db.get_record_by_id('Contragents', ActiveUser[message.chat.id]['code'])
                if cont is not None:
                    ActiveUser[message.chat.id]['cname'] = cont[1]
                    ActiveUser[message.chat.id]['name'] = cont[1]
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
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

# общий чат (пересылка сообщения всем пользователям)
class allchats:
    # пересылка пользовательского сообщения всем
    def chat1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'{username} Отправил запрос в отправке всем пользователям - {message.text}')
        if message.text == "/start":
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["welcome"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
            )
        else:
            if message.text == 'Main Menu' or message.text == '/start':
                logging.info('main')
                bot.send_message(
                    message.chat.id,
                    'Выберите операцию.',
                    reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
                )
                bot.register_next_step_handler(message, Main.main1)
            else:
                logging.info('message to all')
                users = db.select_table('Clients')
                # for user in users:
                #     try:
                #         logging.info(f'sended message to user {user[3]} from {user[2]}')
                #         if user[0] != message.chat.id:
                #             bot.forward_message(user[0], message.chat.id, message.message_id)
                #     except Exception as e:
                #         logging.error(e)
                #         pass
                for user in users:
                    try:
                        bot.forward_message(user[0], message.chat.id, message.message_id)
                        if message.from_user.id == 65241621 or message.from_user.id == 1669785252:
                            bot.unpin_chat_message(user[0])
                            bot.pin_chat_message(user[0], message.message_id)
                        logging.info(f'sent message to user {user[3]} from {user[2]}')
                    except Exception as e:
                        logging.error(e)
                        pass
                bot.register_next_step_handler(message, allchats.chat1)

@bot.message_handler(content_types=['text', 'location'])

def reg6(message):
    global ActiveUser
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        pass
    if message.text == "/start":
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["welcome"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
        )
    else:
        if message.content_type == 'location':
            lon, lat = message.location.longitude, message.location.latitude
            url = f'https://www.google.com/maps/search/?api=1&query={lat},{lon}'
            ActiveUser[message.chat.id]['addr'] = url
            db.insert_record(
                'Locations',
                [
                    None,
                    ActiveUser[message.chat.id]['code'],
                    'Основной адрес',
                    lat,
                    lon
                ]
            )
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
    if message.text == "/start":
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["welcome"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
        )
    else:
        if message.content_type == 'location':
            lon, lat = message.location.longitude, message.location.latitude
            url = f'https://www.google.com/maps/search/?api=1&query={lat},{lon}'
            ActiveUser[message.chat.id]['adr'] = url
            db.update_records(
                'Locations',
                ['lat', 'lon'],
                [lat, lon],
                'name',
                'Основной адрес'
            )
        else:
            ActiveUser[message.chat.id]['adr'] = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=ActiveUser[message.chat.id]['settingsmes'].chat.id, message_id=ActiveUser[message.chat.id]['settingsmes'].message_id)
        settingsmes(message.chat.id)
        bot.register_next_step_handler(message, settings.set1)

def ntnl(message):
    global ActiveUser
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    if message.text == "/start":
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["welcome"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
        )
    else:
        if message.content_type == 'location':
            ActiveUser[message.chat.id]['lon'], ActiveUser[message.chat.id]['lat'] = message.location.longitude, message.location.latitude
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["locentername"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, ntnl1)
        else:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["locerrorloc"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, ntnl)

def ntnl1(message):
    global ActiveUser
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    if message.text == "/start":
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["welcome"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
        )
    else:
        ActiveUser[message.chat.id]['locationname'] = message.text
        inn = db.get_record_by_id('Clients', message.chat.id)[1]
        db.insert_record(
            'Locations',
            [
                None,
                inn,
                message.text,
                ActiveUser[message.chat.id]['lat'],
                ActiveUser[message.chat.id]['lon']
            ]
        )
        locations = db.select_table_with_filters('Locations', {'inn': db.get_record_by_id('Clients', message.chat.id)[1]})
        if len(locations) > 0:
            btns = []
            btns.append(ActiveUser[message.chat.id]["dict"]["locleave"])
            for loc in locations:
                btns.append(str(loc[0]) + ' - ' + str(loc[2]))
            btns.append(ActiveUser[message.chat.id]["dict"]["locadd"])
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["locwhere"],
                reply_markup=buttons.Buttons(btns)
            )
            bot.register_next_step_handler(message, Main.confirmtask01)

def setloc1(message):
    global ActiveUser
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    if message.text == "/start":
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["welcome"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
        )
    else:
        if message.content_type == 'location':
            ActiveUser[message.chat.id]['lon'], ActiveUser[message.chat.id]['lat'] = message.location.longitude, message.location.latitude
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["locentername"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, setloc2)
        else:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["locerrorloc"],
                reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, setloc1)
def setloc2(message):
    global ActiveUser
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    if message.text == "/start":
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["welcome"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
        )
    else:
        ActiveUser[message.chat.id]['locationname'] = message.text
        inn = db.get_record_by_id('Clients', message.chat.id)[1]
        db.insert_record(
            'Locations',
            [
                None,
                inn,
                message.text,
                ActiveUser[message.chat.id]['lat'],
                ActiveUser[message.chat.id]['lon']
            ]
        )
        usercode = db.get_record_by_id('Clients', message.chat.id)[1]
        locs = db.select_table_with_filters('Locations', {'inn': usercode})
        if len(locs) > 0:
            for location in locs:
                loc = telebot.types.Location(location[4], location[3])
                bot.send_location(message.chat.id, loc.latitude, loc.longitude)
                bot.send_message(
                    message.chat.id,
                    str(location[2]),
                    reply_markup=buttons.buttonsinline([[ActiveUser[message.chat.id]["dict"]["setchange"], 'location '+str(location[0])]])
                )
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["setmestochange"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["locadd"], ActiveUser[message.chat.id]["dict"]["bcancel"]])
        )
        bot.register_next_step_handler(message, settings.locations1)
def setloc3(message):
    global ActiveUser
    try:
        username = db.get_record_by_id('Clients', message.chat.id)[2]
        logging.info(f'{username} Отправил запрос - {message.text}')
    except Exception as e:
        logging.error(e)
        pass
    if message.text == "/start":
        bot.send_message(
            message.chat.id,
            ActiveUser[message.chat.id]["dict"]["welcome"],
            reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["newtask"], ActiveUser[message.chat.id]["dict"]["mytasks"], ActiveUser[message.chat.id]["dict"]["review"], ActiveUser[message.chat.id]["dict"]["rate"], ActiveUser[message.chat.id]["dict"]["settings"]],3)
        )
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
                ActiveUser[message.chat.id]["dict"]["success"],
                reply_markup=buttons.Buttons([ActiveUser[message.chat.id]["dict"]["setlocationch"], ActiveUser[message.chat.id]["dict"]["setnameloc"], ActiveUser[message.chat.id]["dict"]["setdelete"], ActiveUser[message.chat.id]["dict"]["bcancel"]])
            )
            bot.register_next_step_handler(message, settings.locations2)
        else:
            bot.send_message(
                message.chat.id,
                ActiveUser[message.chat.id]["dict"]["locerrorloc"],
                reply_markup=buttons.clearbuttons
            )
            bot.register_next_step_handler(message, setloc3)

@bot.callback_query_handler(func=lambda call: True)
# Реакция на кнопки
def callback_handler(call):
    # Реакция на инлайновые кнопки
    # username = db.get_record_by_id("Clients", call.from_user.id)[1]
    # logging.info(f"{username} нажал на кнопку {str(call)}")
    if call.data.split()[0] == 'location':# Редактирование локации
        ActiveUser[call.from_user.id]['curlocation'] = call.data.split()[1]
        bot.send_message(
            call.from_user.id,
            ActiveUser[call.from_user.id]["dict"]["setwywtch"],
            reply_markup=buttons.Buttons([ActiveUser[call.from_user.id]["dict"]["setlocationch"], ActiveUser[call.from_user.id]["dict"]["setnameloc"], ActiveUser[call.from_user.id]["dict"]["setdelete"], ActiveUser[call.from_user.id]["dict"]["bcancel"]])
        )
        bot.register_next_step_handler(call.message, settings.locations2)

# Запуск бота
if __name__ == '__main__':
    thread = threading.Thread(target=asyncio.run, args=(main(),))
    thread.start()
    # bot.polling()
while True:
    try:
        bot.polling()
    except Exception as e:
        logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
        pass
