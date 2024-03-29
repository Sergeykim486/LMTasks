import logging, Classes.functions as functions, Classes.buttons as buttons, calendar
from datetime import datetime
from Classes.config import ActiveUser, bot, sendedmessages, db, mainclass

months = {
    '1': ['01','03'],
    '2': ['04','06'],
    '3': ['07','09'],
    '4': ['10','12']
}

num = 0

# отчеты
class report:
    
    # Запрос в базу с параметрами
    def rep(message, daterep, dr = 1, conf = 0, added = 0, done = 0, canc = 0, master = 0, my = 0, tadded = 0, tconf = 0, tdone = 0):
        if message.text == '🚫 Отмена' or message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            donetasks = []
            confirmedtasks = []
            addedtasks = []
            canceledtasks = []
            if tdone == 1:
                if my == 1:
                    filt = {'status': 7, 'master': master}
                else:
                    filt = {'status': 7}
                tdonetasks = functions.listgen(db.select_table_with_filters('Tasks', filt, ['done'], [daterep+' 00:00'], [daterep+' 23:59']), [0, 1, 3, 4, 6], 1)
                if len(tdonetasks) != 0:
                    bot.send_message(
                        message.chat.id,
                        '🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nГотовая техника.',
                        reply_markup=''
                    )
                    for line in tdonetasks:
                        taskid = line.split()[2]
                        bot.send_message(
                            message.chat.id,
                            line,
                            reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid],['ЛОКАЦИЯ', 'location '+taskid]])
                        )
            if tconf == 1:
                if my == 1:
                    filt = {'status': 6, 'master': master}
                else:
                    filt = {'status': 6}
                tconftasks = functions.listgen(db.select_table_with_filters('Tasks', filt), [0, 1, 3, 4, 6], 1)
                if len(tconftasks) != 0:
                    bot.send_message(
                        message.chat.id,
                        '🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nТехника у мастеров.',
                        reply_markup=''
                    )
                    for line in tconftasks:
                        taskid = line.split()[2]
                        bot.send_message(
                            message.chat.id,
                            line,
                            reply_markup=buttons.buttonsinline([['📎 Переназначить', 'set ' + taskid], ['Показать подробности', 'tasklist '+taskid],['ЛОКАЦИЯ', 'location '+taskid]])
                        )
            if tadded == 1:
                taddedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 5}), [0, 1, 3, 4, 6], 1)
                if len(taddedtasks) != 0:
                    bot.send_message(
                        message.chat.id,
                        '🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nОжидает ремонта',
                        reply_markup=''
                    )
                    for line in taddedtasks:
                        taskid = line.split()[2]
                        bot.send_message(
                            message.chat.id,
                            line,
                            reply_markup=buttons.buttonsinline([['👍 Принять', 'confirm ' + taskid], ['📎 Назначить', 'set ' + taskid], ['Показать подробности', 'tasklist '+taskid], ['ЛОКАЦИЯ', 'location '+taskid]])
                        )
            if done == 1:
                if my == 1:
                    filt = {'status': 3, 'master': master}
                else:
                    filt = {'status': 3}
                donetasks = functions.listgen(db.select_table_with_filters('Tasks', filt, ['done'], [daterep+' 00:00'], [daterep+' 23:59']), [0, 1, 3, 4, 6], 1)
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
                            reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid],['ЛОКАЦИЯ', 'location '+taskid]])
                        )
            if conf == 1:
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
                            reply_markup=buttons.buttonsinline([['📎 Переназначить', 'set ' + taskid], ['Показать подробности', 'tasklist '+taskid],['ЛОКАЦИЯ', 'location '+taskid]])
                        )
            if added == 1:
                addedtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 1}), [0, 1, 3, 4, 6], 1)
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
                            reply_markup=buttons.buttonsinline([['👍 Принять', 'confirm ' + taskid], ['📎 Назначить', 'set ' + taskid], ['Показать подробности', 'tasklist '+taskid],['ЛОКАЦИЯ', 'location '+taskid]])
                        )
            if canc == 1:
                canceledtasks = functions.listgen(db.select_table_with_filters('Tasks', {'status': 4}, ['canceled'], [daterep+' 00:00'], [daterep+' 23:59']), [0, 1, 3, 4, 6], 1)
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
                            reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid],['ЛОКАЦИЯ', 'location '+taskid]])
                        )
            if dr == 1:
                reports = '\nВыполнено - ' + str(len(donetasks)) + '\nНе распределенных - ' + str(len(addedtasks)) + '\nВ работе у мастеров - ' + str(len(confirmedtasks)) + '\nОтменено - ' + str(len(canceledtasks))
                reports = reports + '\n\nКоличество заявок выполненных мастерами:\n\n'
                users = db.select_table('Users')
                usersrep = []
                for i in users:
                    tasks = len(db.select_table_with_filters('Tasks', {'master': i[0], 'status': 3}, ['done'], [str(daterep)+' 00:00'], [str(daterep)+' 23:59']))
                    usersrep.append([i[2] + ' ' + i[1], tasks])
                sorted_usersrep = sorted(usersrep, key=lambda x: x[1], reverse=True)
                for j in sorted_usersrep:
                    if j[1] != 0:
                        reports = reports + '\n' + j[0] + ' - ' + str(j[1])
                bot.send_message(
                    message.chat.id,
                    'ИТОГИ ДНЯ\n🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺🔺' + reports,
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
            else:
                if len(addedtasks) != 0 and len(confirmedtasks) != 0 and len(donetasks) != 0 and len(canceledtasks) != 0:
                    bot.send_message(
                        message.chat.id,
                        'Выберите операцию.',
                        reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                    )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False

    # Реакия на нажатие кнопок меню отчетов
    def reportall(message):
        global num
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        if num != 0:
            logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if num == 0:
            num = 1
        if message.text == '📋 Заявки у мастеров':
            num = 0
            users = db.select_table('Users')
            res = ''
            bot.send_message(
                message.chat.id,
                'ЗАЯВКИ У МАСТЕРОВ\n\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻',
                reply_markup=buttons.clearbuttons()
            )
            processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
            tc = 0
            for u in users:
                userid = u[0]
                daterep = str(datetime.now().strftime("%d.%m.%Y"))
                confirmed = db.select_table_with_filters('Tasks', {'status': 2, 'master': userid})
                done = db.select_table_with_filters('Tasks', {'status': 3, 'master': userid}, ['done'], [daterep+' 00:00'], [daterep+' 23:59'])
                canceled = db.select_table_with_filters('Tasks', {'status': 4, 'master': userid}, ['canceled'], [daterep+' 00:00'], [daterep+' 23:59'])
                if len(confirmed) > 0 or len(done) > 0 or len(canceled) > 0:
                    res = res + f'\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\n👤 {u[2]} {u[1]}\n\nЗАЯВКИ В РАБОТЕ:\n'
                    if len(confirmed) > 0:
                        for i in confirmed:
                            contr = db.get_record_by_id('Contragents', i[3])[1]
                            adr = db.get_record_by_id('Contragents', i[3])[2]
                            res = res + f'\n\n🟡 - №{i[0]} от {i[1]} | {contr}\n{adr}'
                    if len(done) > 0:
                        for j in done:
                            contr = db.get_record_by_id('Contragents', j[3])[1]
                            adr = db.get_record_by_id('Contragents', j[3])[2]
                            res = res + f'\n\n🟢 - №{j[0]} от {j[1]} | {contr}\n{adr}'
                    if len(canceled) > 0:
                        for k in canceled:
                            contr = db.get_record_by_id('Contragents', k[3])[1]
                            adr = db.get_record_by_id('Contragents', k[3])[2]
                            res = res + f'\n\n🔴 - №{k[0]} от {k[1]} | {contr}\n{adr}'
                    bot.send_message(
                        message.chat.id,
                        res,
                        reply_markup=buttons.clearbuttons()
                    )
                    res = ''
                    tc = tc + 1
            functions.mesdel(message.chat.id, processing.message_id)
            if tc == 0:
                bot.send_message(
                    message.chat.id,
                    'У мастеров нет заявок.\nВыберите действие',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
            else:
                bot.send_message(
                    message.chat.id,
                    'Выберите действие',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '🖨️ Техника у мастеров':
            num = 0
            users = db.select_table('Users')
            res = ''
            bot.send_message(
                message.chat.id,
                'ТЕХНИКА В РАБОТЕ\n\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻',
                reply_markup=buttons.clearbuttons()
            )
            processing = bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEJL8dkedQ1ckrfN8fniwY7yUc-YNaW_AACIAAD9wLID1KiROfjtgxPLwQ", reply_markup=buttons.clearbuttons())
            tc = 0
            for u in users:
                userid = u[0]
                daterep = str(datetime.now().strftime("%d.%m.%Y"))
                confirmed = db.select_table_with_filters('Tasks', {'status': 6, 'master': userid})
                done = db.select_table_with_filters('Tasks', {'status': 7, 'master': userid}, ['done'], [daterep+' 00:00'], [daterep+' 23:59'])
                if len(confirmed) > 0 or len(done) > 0:
                    res = res + f'\n🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\n👤 {u[2]} {u[1]}\n\nТЕХНИКА НА РЕМОНТЕ:\n'
                    if len(confirmed) > 0:
                        for i in confirmed:
                            tech = i[4].split('\n======================\n')[0] + '\n' + i[4].split('\n======================\n')[1]
                            res = res + f'\n\n🟨 - №{i[0]} от {i[1]}\n{tech}'
                    if len(done) > 0:
                        for j in done:
                            tech = j[4].split('\n======================\n')[0] + '\n' + j[4].split('\n======================\n')[1]
                            res = res + f'\n\n🟩 - №{j[0]} от {j[1]}\n{tech}'
                    bot.send_message(
                        message.chat.id,
                        res,
                        reply_markup=buttons.clearbuttons()
                    )
                    res = ''
                tc = tc + 1
            functions.mesdel(message.chat.id, processing.message_id)
            if tc == 0:
                bot.send_message(
                    message.chat.id,
                    'У мастеров нет техники на ремонте.\nВыберите действие',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
            else:
                bot.send_message(
                    message.chat.id,
                    'Выберите действие',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '📊 Итоги дня':
            num = 0
            bot.send_message(
                message.chat.id,
                'Какой день вы хотите увидеть?',
                reply_markup = buttons.Buttons(['🌞 Сегодня', '🗓️ Другой день'])
            )
            bot.register_next_step_handler(message, report.reportall1)
        elif message.text == '📆 За период':
            num = 0
            bot.send_message(
                message.chat.id,
                'За какой период сформировать отчет?',
                reply_markup = buttons.Buttons(['Месяц\Квартал\Год','Указать вручную'])
            )
            bot.register_next_step_handler(message, report.period0)
        elif message.text == '🚫 Отмена' or message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            if num == 1:
                num = num + 1
                bot.send_message(
                    message.chat.id,
                    'Выберите какой отчет Вам нужен\nПоказать все не выполненные заявки, или показать итоги дня.',
                    reply_markup=buttons.Buttons(['📋 Заявки у мастеров', '🖨️ Техника у мастеров', '📊 Итоги дня', '📆 За период', '🚫 Отмена'])
                )
                bot.register_next_step_handler(message, report.reportall)
            else:
                bot.register_next_step_handler(message, report.reportall)

    def period0(message):# Выбор типа периода
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == 'Указать вручную':
            bot.send_message(
                message.chat.id,
                'Укажите начало периода в формате:\nПРИМЕР: 01.01.2023 или 01,01,2023',
                reply_markup = buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, report.period1)
        elif message.text == 'Месяц\Квартал\Год':
            ActiveUser[message.chat.id]['monthrep'] = 1
            ActiveUser[message.chat.id]['mf'] = '01'
            ActiveUser[message.chat.id]['mt'] = '12'
            ActiveUser[message.chat.id]['y'] = str(datetime.now().year)
            ActiveUser[message.chat.id]['settingsmes'] = None
            ActiveUser[message.chat.id]['daterepf'] = '01.' +  ActiveUser[message.chat.id]['mf'] + '.' + ActiveUser[message.chat.id]['y']
            ActiveUser[message.chat.id]['daterept'] = str(calendar.monthrange(int(ActiveUser[message.chat.id]['y']), int(ActiveUser[message.chat.id]['mt']))[1]) + '.' + ActiveUser[message.chat.id]['mt'] + '.' + ActiveUser[message.chat.id]['y']
            report.repsettings(message)
            bot.register_next_step_handler(message, report.settingshandler)
        elif message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
    
    def settingshandler(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        functions.mesdel(message.chat.id, message.message_id)
        if message.text == '✅Сформировать':
            fr = ActiveUser[message.chat.id]['daterepf']
            t = ActiveUser[message.chat.id]['daterept']
            bot.send_message(
                message.chat.id,
                f'Выбран период с {fr} по {t}\nКакой отчет вывести?',
                reply_markup=buttons.Buttons(['Все заявки','по мастерам','по клиенту'])
            )
            bot.register_next_step_handler(message, report.period3)
        elif message.text == '✅ Месяц' or message.text == 'Месяц':
            ActiveUser[message.chat.id]['monthrep'] = 1
            report.repsettings(message)
            bot.register_next_step_handler(message, report.settingshandler)
        elif message.text == 'Квартал' or message.text == '✅ Квартал':
            ActiveUser[message.chat.id]['monthrep'] = 0
            report.repsettings(message)
            bot.register_next_step_handler(message, report.settingshandler)
        elif message.text == 'Год' or message.text == '✅ Год':
            ActiveUser[message.chat.id]['monthrep'] = 2
            ActiveUser[message.chat.id]['mf'] = '01'
            ActiveUser[message.chat.id]['mt'] = '12'
            report.repsettings(message)
            bot.register_next_step_handler(message, report.settingshandler)
        elif message.text.isdigit() == True and len(message.text) == 2:
            ActiveUser[message.chat.id]['mf'] = message.text
            ActiveUser[message.chat.id]['mt'] = message.text
            report.repsettings(message)
            bot.register_next_step_handler(message, report.settingshandler)
        elif message.text.isdigit() == True and len(message.text) == 1:
            ActiveUser[message.chat.id]['mf'] = months[message.text][0]
            ActiveUser[message.chat.id]['mt'] = months[message.text][1]
            report.repsettings(message)
            bot.register_next_step_handler(message, report.settingshandler)
        elif message.text == '◄':
            ActiveUser[message.chat.id]['y'] = str(int(ActiveUser[message.chat.id]['y']) - 1)
            report.repsettings(message)
            bot.register_next_step_handler(message, report.settingshandler)
        elif message.text == '►':
            ActiveUser[message.chat.id]['y'] = str(int(ActiveUser[message.chat.id]['y']) + 1)
            report.repsettings(message)
            bot.register_next_step_handler(message, report.settingshandler)
        elif message.text == '⛔️Отмена' or message.text == '/start':
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
                'Не верная команда.'
            )
            report.repsettings(message)
            bot.register_next_step_handler(message, report.settingshandler)

    def repsettings(message):
        try:
            functions.mesdel(message.chat.id, ActiveUser[message.chat.id]['settingsmes'].message_id)
        except:
            pass
        ActiveUser[message.chat.id]['daterepf'] = '01.' +  ActiveUser[message.chat.id]['mf'] + '.' + ActiveUser[message.chat.id]['y']
        ActiveUser[message.chat.id]['daterept'] = str(calendar.monthrange(int(ActiveUser[message.chat.id]['y']), int(ActiveUser[message.chat.id]['mt']))[1]) + '.' + ActiveUser[message.chat.id]['mt'] + '.' + ActiveUser[message.chat.id]['y']
        fr = ActiveUser[message.chat.id]['daterepf']
        t = ActiveUser[message.chat.id]['daterept']
        if ActiveUser[message.chat.id]['monthrep'] == 1:
            typebuttons = ['✅ Месяц','Квартал', 'Год']
            buts = ['01','02','03','04','05','06']
            buts2 = ['07','08','09','10','11','12']
        elif ActiveUser[message.chat.id]['monthrep'] == 0:
            typebuttons = ['Месяц','✅ Квартал', 'Год']
            buts = ['1','2','3','4']
            buts2 = []
        else:
            typebuttons = ['Месяц','Квартал', '✅ Год']
            buts = []
            buts2 = []
        ActiveUser[message.chat.id]['settingsmes'] = bot.send_message(
            message.chat.id,
            f'ФОРМИРОВАНИЕ ОТЧЕТА:\nС {fr} ПО {t}\nКогда выберите период нажмите "Сформировать"\n\nЕсли ничего не менять то отчет будет сформирован за текущий год',
            reply_markup = buttons.reportbuttons(typebuttons,['◄',ActiveUser[message.chat.id]['y'],'►'],buts,buts2,['✅Сформировать','⛔️Отмена'])
        )
        return

    def period1(message):# с
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            m1 = message.text
            m1 = m1.replace(' ', '.')
            m1 = m1.replace(',', '.')
            m = m1.split('.')
            if len(m[0]) == 2 and len(m[1]) == 2 and len(m[2]) == 4 and len(m) == 3:
                try:
                    ActiveUser[message.chat.id]['daterepf'] = m1
                    bot.send_message(
                        message.chat.id,
                        'Укажите конец периода в формате:\nПРИМЕР: 01.01.2023 или 01,01,2023',
                        reply_markup=buttons.clearbuttons()
                    )
                    bot.register_next_step_handler(message, report.period2)
                except ValueError:
                    bot.send_message(
                        message.chat.id,
                        'Некорректная дата...\nУкажите начало периода в формате:\nПРИМЕР: 01.01.2023 или 01,01,2023',
                        reply_markup=buttons.clearbuttons()
                    )
                    bot.register_next_step_handler(message, report.period1)
            else:
                bot.send_message(
                    message.chat.id,
                    'Не верный формат даты...\nУкажите начало периода в формате:\nПРИМЕР: 01.01.2023 или 01,01,2023',
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, report.period1)

    def period2(message):# по
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            m1 = message.text
            m1 = m1.replace(' ', '.')
            m1 = m1.replace(',', '.')
            m = m1.split('.')
            if len(m[0]) == 2 and len(m[1]) == 2 and len(m[2]) == 4 and len(m) == 3:
                try:
                    start_date = datetime.strptime(ActiveUser[message.chat.id]['daterepf'], "%d.%m.%Y")
                    end_date = datetime.strptime(m1, "%d.%m.%Y")
                    fr = ActiveUser[message.chat.id]['daterepf']
                    if end_date >= start_date:
                        ActiveUser[message.chat.id]['daterept'] = m1
                        t = ActiveUser[message.chat.id]['daterept']
                        bot.send_message(
                            message.chat.id,
                            f'Выбран период с {fr} по {t}\nКакой отчет вывести?',
                            reply_markup=buttons.Buttons(['Все заявки','по мастерам','по клиенту'])
                        )
                        bot.register_next_step_handler(message, report.period3)
                    else:
                        bot.send_message(
                            message.chat.id,
                            'Дата окончания периода не может быть раньше даты начала периода. Пожалуйста, укажите корректную дату.',
                            reply_markup=buttons.clearbuttons()
                        )
                        bot.register_next_step_handler(message, report.period2)
                except ValueError:
                    bot.send_message(
                        message.chat.id,
                        'Некорректная дата...\nУкажите конец периода в формате:\nПРИМЕР: 01.01.2023 или 01,01,2023',
                        reply_markup=buttons.clearbuttons()
                    )
                    bot.register_next_step_handler(message, report.period2)
            else:
                bot.send_message(
                    message.chat.id,
                    'Не верный формат даты...\nУкажите конец периода в формате:\nПРИМЕР: 01.01.2023 или 01,01,2023',
                    reply_markup=buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, report.period2)

    def period3(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        global ActiveUser
        if message.text == 'Все заявки':
            fr = ActiveUser[message.chat.id]['daterepf']
            t = ActiveUser[message.chat.id]['daterept']
            rept = db.select_table_with_filters('Tasks', {'status': 3}, ['done'], [fr+' 00:00'], [t+' 23:59'])
            functions.sendrepfile(message, rept)
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == 'по мастерам':
            users = db.select_table('Users')
            btn = []
            for user in users:
                line = str(user[0]) + ' ' + str(user[2]) + ' ' + str(user[1])
                btn.append(line)
            bot.send_message(
                message.chat.id,
                'Выберите мастера.',
                reply_markup=buttons.Buttons(btn,1)
            )
            bot.register_next_step_handler(message, report.period4)
        elif message.text == 'по клиенту':
            bot.send_message(
                message.chat.id,
                'Введите ИНН, ПИНФЛ или серию пвсспоррта клиента.\nТак же Вы можете попытаться поискать контрагента по наименованию или его части\nНапримар:\nmonohrom\nВыдаст все компании из базы бота у которых в названии есть monohrom',
                reply_markup=buttons.Buttons(['🚫 Отмена'])
            )
            bot.register_next_step_handler(message, report.period5)
        elif message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False

    def period4(message): # по мастерам
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            uid = message.text.split()[0]
            selecteduser = db.get_record_by_id('Users', uid)
            if uid.isdigit() and selecteduser != None:
                fr = ActiveUser[message.chat.id]['daterepf']
                t = ActiveUser[message.chat.id]['daterept']
                rept = db.select_table_with_filters('Tasks', {'master': selecteduser[0], 'status': 3}, ['done'], [fr+' 00:00'], [t+' 23:59'])
                functions.sendrepfile(message, rept)
                bot.send_message(
                    message.chat.id,
                    'Выберите операцию.',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
                ActiveUser[message.chat.id]['Pause_main_handler'] = False
                ActiveUser[message.chat.id]['Finishedop'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = False
            else:
                users = db.select_table('Users')
                btn = []
                for user in users:
                    line = str(user[0]) + ' ' + str(user[2]) + ' ' + str(user[1])
                    btn.append(line)
                bot.send_message(
                    message.chat.id,
                    'Выберите мастера.',
                    reply_markup=buttons.Buttons(btn,1)
                )
                bot.register_next_step_handler(message, report.period4)

    def period5(message): # по клиентам
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            if message.text == '🚫 Отмена':
                bot.send_message(
                    message.chat.id,
                    'Выберите операцию.',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
                ActiveUser[message.chat.id]['Pause_main_handler'] = False
                ActiveUser[message.chat.id]['Finishedop'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = False
            elif message.text.split()[0].isdigit():
                inn = int(message.text.split()[0])
                client = db.get_record_by_id('Contragents', inn)
                if client[5] != None:
                    fr = ActiveUser[message.chat.id]['daterepf']
                    t = ActiveUser[message.chat.id]['daterept']
                    rept = db.select_table_with_filters('Tasks', {'contragent': inn, 'status': 3}, ['done'], [fr+' 00:00'], [t+' 23:59'])
                    functions.sendrepfile(message, rept)
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
                        'Контрагент не найден.',
                        reply_markup=buttons.Buttons(['🚫 Отмена'])
                    )
                    bot.register_next_step_handler(message, report.period5)
            else:
                contrs = db.select_table('Contragents')
                res = functions.search_items(message.text, contrs)
                contbuttons = []
                contbuttons.append('🚫 Отмена')
                if len(res) > 0:
                    for i in res:
                        line = str(i[0]) + ' ' + str(i[1])
                        if len(contbuttons) < 20:
                            contbuttons.append(line)
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
                    bot.send_message(
                        message.chat.id,
                        'Контрагент не найден.',
                        reply_markup=buttons.Buttons(contbuttons, 1)
                    )
                bot.register_next_step_handler(message, report.period5)

    # Итоги дня
    def reportall1(message):
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            if message.text == '🌞 Сегодня':
                daterep = str(datetime.now().strftime("%d.%m.%Y"))
                report.rep(message, daterep, 1, 1, 1, 1, 1)
            elif message.text == '🗓️ Другой день':
                bot.send_message(
                    message.chat.id,
                    'Укажите дату в формате:\nПРИМЕР: 01.01.2023 или 01,01,2023',
                    reply_markup = buttons.clearbuttons()
                )
                bot.register_next_step_handler(message, report.reportallq)
            else:
                bot.send_message(
                    message.chat.id,
                    'Не верная команда',
                    reply_markup = buttons.Buttons(['🌞 Сегодня', '🗓️ Другой день'])
                )
                bot.register_next_step_handler(message, report.reportall1)

    def reportallq(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            ActiveUser[message.chat.id]['repotherdate'] = message.text
            bot.send_message(
                message.chat.id,
                'Какие заявки показать?',
                reply_markup=buttons.Buttons(['Все', 'Только мои', 'У мастера'])
            )
            bot.register_next_step_handler(message, report.reportall2)

    def reportall2(message):
        global ActiveUser
        username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        if message.text == '/start':
            num = 0
            bot.send_message(
                message.chat.id,
                'Выберите операцию.',
                reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        else:
            m1 = ActiveUser[message.chat.id]['repotherdate']
            m1 = m1.replace(' ', '.')
            m1 = m1.replace(',', '.')
            m = m1.split('.')
            if len(m[0]) == 2 and len(m[1]) == 2 and len(m[2]) == 4 and len(m) == 3:
                ActiveUser[message.chat.id]['daterep'] = m1
            daterep = str(ActiveUser[message.chat.id]['daterep'])
            if message.text.split()[0].isdigit():
                masterid = int(message.text.split()[0])
                mastername = str(db.get_record_by_id('Users', masterid)[2]) + ' ' + str(db.get_record_by_id('Users', masterid)[1])
                bot.send_message(
                    message.chat.id,
                    f'🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nОтчет за: {daterep}\nМастер: {mastername}',
                    reply_markup=buttons.clearbuttons()
                )
                rept = db.select_table_with_filters('Tasks', {'master': masterid, 'status': 3}, ['done'], [daterep+' 00:00'], [daterep+' 23:59'])
                functions.sendrep(message, rept)
                functions.sendrepfile(message, rept)
                bot.send_message(
                    message.chat.id,
                    'Выберите операцию.',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
                ActiveUser[message.chat.id]['Pause_main_handler'] = False
                ActiveUser[message.chat.id]['Finishedop'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = False
            elif message.text == 'Все':
                bot.send_message(
                    message.chat.id,
                    f'🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nОтчет за: {daterep}\nМастер: Все',
                    reply_markup=buttons.clearbuttons()
                )
                rept = db.select_table_with_filters('Tasks', {'status': 3}, ['done'], [daterep+' 00:00'], [daterep+' 23:59'])
                functions.sendrep(message, rept)
                functions.sendrepfile(message, rept)
                bot.send_message(
                    message.chat.id,
                    'Выберите операцию.',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
                ActiveUser[message.chat.id]['Pause_main_handler'] = False
                ActiveUser[message.chat.id]['Finishedop'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = False
            elif message.text == 'Только мои':
                bot.send_message(
                    message.chat.id,
                    f'🔻🔻🔻🔻🔻🔻🔻🔻🔻🔻\nОтчет за: {daterep}\nМастер: Я',
                    reply_markup=buttons.clearbuttons()
                )
                rept = db.select_table_with_filters('Tasks', {'master': message.chat.id, 'status': 3}, ['done'], [daterep+' 00:00'], [daterep+' 23:59'])
                functions.sendrep(message, rept)
                functions.sendrepfile(message, rept)
                bot.send_message(
                    message.chat.id,
                    'Выберите операцию.',
                    reply_markup=buttons.Buttons(['📝 Новая заявка', '🔃 Обновить список заявок', '🖨️ Обновить список техники', '📋 Мои заявки', '✏️ Редактировать контрагента', '📈 Отчеты', '🗺️ Карта', '📢 Написать всем'],3)
                )
                ActiveUser[message.chat.id]['Pause_main_handler'] = False
                ActiveUser[message.chat.id]['Finishedop'] = True
                ActiveUser[message.chat.id]['block_main_menu'] = False
            elif message.text == 'У мастера':
                users = db.select_table('Users')
                masters = []
                masters.append('↩️ Назад')
                for user in users:
                    line = str(user[0]) + ' ' + str(user[2]) + ' ' + str(user[1])
                    masters.append(line)
                bot.send_message(
                    message.chat.id,
                    'Выберите мастера.',
                    reply_markup=buttons.Buttons(masters, 1)
                )
                bot.register_next_step_handler(message, report.reportall2)
            else:
                bot.send_message(
                    message.chat.id,
                    'Не верная команда!\nКакие заявки показать?',
                    reply_markup=buttons.Buttons(['Все', 'Только мои', 'У мастера'])
                )
                bot.register_next_step_handler(message, report.reportall2)

def callback_handler(call):
    try:
        username = db.get_record_by_id('Users', call.message.chat.id)[2] + ' ' + db.get_record_by_id('Users', call.message.chat.id)[1]
        logging.info(f'\nℹ️ {username} Нажал на кнопку\n    -    [{call.data}]\n')
    except Exception as e:
        logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
        pass
