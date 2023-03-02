from db import Database
import os
dbname = os.path.dirname(os.path.abspath(__file__)) + '/Database/' + 'lmtasksbase.db'
db = Database(dbname)

def conftext(message, ActiveUser):
    mestext = "Подтвердите правильность введенной информации.\n"
    mestext = mestext + "Ваш id:" + str(ActiveUser[message.chat.id]["id"]) + "\n"
    mestext = mestext + "Имя:" + str(ActiveUser[message.chat.id]["FirstName"]) + "\n"
    mestext = mestext + "Фамилия:" + str(ActiveUser[message.chat.id]["LastName"]) + "\n"
    mestext = mestext + "Телефон:" + str(ActiveUser[message.chat.id]["PhoneNumber"]) + "\n"
    return mestext

def listgen(table, cols, tasks = 0):
    res = []
    for line in table:
        curline = ''
        for i in cols:
            print(line[i])
            if tasks == 1:
                if i == 0:
                    curline = curline + '№ ' + str(line[i])
                elif i == 1:
                    curline = curline + ' от ' + str(line[i])
                elif i == 3:
                    cname = db.get_record_by_id('Contragents', line[i])[1]
                    print(cname)
                    curline = curline + str(cname) + ' '
                else:
                    curline = curline + str(line[i]) + ' ' 
            else:
                curline = curline + str(line[i]) + ' ' 
        if tasks == 0:
            res.append(curline)
        elif tasks == 1:
            marker = ''
            if str(line[11]) == '1': marker = '🔵 '
            elif str(line[11]) == '2': marker = '🟡 '
            elif str(line[11]) == '3': marker = '🟢 '
            elif str(line[11]) == '4': marker = '🔴 '
            else: marker = '⚪️ '
            res.append(marker + curline)
        elif tasks == 2:
            res.append('🗄 ' + curline)
    return res

def curtask(id):
    messtext = ''
    task = db.get_record_by_id('Tasks', id)
    print('Выбранная заявка найдена')
    messtext = 'Заявка №' + str(task[0]) + ' от ' + str(task[1])
    messtext = messtext + '\nЗаявку зарегистрировал: ' + str(db.get_record_by_id('Users', task[2])[1])
    if task[11] == 2 or task[10] == 3:
        messtext = messtext + '\nМастер ' + str(db.get_record_by_id('Users', task[6])[2]) + str(db.get_record_by_id('Users', task[6])[1])
        messtext = messtext + 'принял ' + str(task[5])
    elif task[11] == 4:
        messtext = messtext + '\n' + str(db.get_record_by_id('Users', task[9])[1]) + ' отменил заявку\nПРИЧИНА ОТМЕНЫ:\n' + str(task[10])
    messtext = messtext + '\nПоступила от: ' + str(db.get_record_by_id('Contragents', task[3])[1])
    messtext = messtext + '\nЗАПРОС:\n' + str(task[4])
    messtext = messtext + '\nКОНТАКТЫ ЗАКАЗЧИКА:\n' + str(db.get_record_by_id('Contragents', task[3])[3]) + ' - ' + str(db.get_record_by_id('Contragents', task[3])[4])
    messtext = messtext + '\n\nСтатус заявки - ' + str(db.get_record_by_id('Statuses', task[11])[1])
    return messtext

def getuserlist():
    users = db.select_table('Users')
    userlist = []
    for line in users:
        userlist.append(line[0])
    return userlist