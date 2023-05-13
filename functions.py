from db import Database
from folium import IFrame
import os, folium, logging

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

            if tasks == 1:

                if i == 0:
                    curline = curline + '№ ' + str(line[i]) + '\n'

                elif i == 1:
                    curline = curline + ' от ' + str(line[i]) + '\n'

                elif i == 3:
                    try:
                        location = db.get_record_by_id('Locations', line[12])[2]
                    except Exception as e:
                        logging.error(e)
                        location = ''
                        pass
                    cname = str(db.get_record_by_id('Contragents', line[i])[0]) + " " + str(db.get_record_by_id('Contragents', line[i])[1]) + "\n Локация - " + location + "\nДоговор: " + str(db.get_record_by_id('Contragents', line[i])[6])
                    curline = curline + str(cname) + '\n'

                elif i == 6 and line[i]:
                    Mastername = str(db.get_record_by_id("Users", line[i])[2]) + ' ' + str(db.get_record_by_id("Users", line[i])[1])
                    curline = curline + '\nМастер: - ' + str(Mastername) + '\n'

                else:

                    if i != 6:
                        curline = curline + str(line[i]) + '\n'

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

        elif tasks == 3:
            res.append('👤 ' + curline)

    return res

def curtask(id):
    messtext = ''
    task = db.get_record_by_id('Tasks', id)
    messtext = 'Заявка №' + str(task[0]) + ' от ' + str(task[1])
    messtext = messtext + '\nЗаявку зарегистрировал(а): ' + str(db.get_record_by_id('Users', task[2])[2]) + ' ' + str(db.get_record_by_id('Users', task[2])[1])

    if task[11] == 2 or task[10] == 3:
        messtext = messtext + '\nМастер ' + str(db.get_record_by_id('Users', task[6])[2]) + ' ' + str(db.get_record_by_id('Users', task[6])[1])
        messtext = messtext + ' принял ' + str(task[5])

    elif task[11] == 4:
        messtext = messtext + '\n' + str(db.get_record_by_id('Users', task[9])[1]) + ' отменил заявку\nПРИЧИНА ОТМЕНЫ:\n' + str(task[10])

    if task[10] is not None:
        messtext = messtext + '\n❗️ ' + str(task[10])
    try:
        location = db.get_record_by_id('Locations', task[12])[2]
    except Exception as e:
        logging.error(e)
        location = ''
        pass
    messtext = messtext + '\n\nПоступила от: ' + str(db.get_record_by_id('Contragents', task[3])[0]) + " " + str(db.get_record_by_id('Contragents', task[3])[1]) + " \nЛокация - " + location + "\nДоговор: " +str(db.get_record_by_id('Contragents', task[3])[6])
    messtext = messtext + '\n\nЗАПРОС:\n' + str(task[4])
    messtext = messtext + '\n\nКОНТАКТЫ ЗАКАЗЧИКА:\n' + str(db.get_record_by_id('Contragents', task[3])[3]) + ' - ' + str(db.get_record_by_id('Contragents', task[3])[4])
    messtext = messtext + f'\nАдрес: ' + str(db.get_record_by_id('Contragents', task[3])[2])
    messtext = messtext + '\n\nСтатус заявки - ' + str(db.get_record_by_id('Statuses', task[11])[1])
    return messtext

def getuserlist():
    users = db.select_table('Users')
    userlist = []
    for line in users:
        userlist.append(line[0])
    return userlist

from folium.plugins import MarkerCluster
from folium import IFrame
from urllib.parse import quote

def mapgen(locations):
    # Создание объекта карты
    map = folium.Map(location=[41.28927613679946, 69.31295641163192], zoom_start=12)

    # Создание группы маркеров
    marker_cluster = MarkerCluster().add_to(map)

    # Создание списка точек с попапами
    popup_content = ""
    for location in locations:
        name = location[0]
        taskid = name.split()[1]
        description = location[1]
        lat = float(location[2])
        lon = float(location[3])
        color = 'blue'
        if location[4] == 2:
            color = 'orange'
        elif location[4] == 3:
            color = 'green'
        elif location[4] == 4:
            color = 'red'
        link = f'https://t.me/labmonotasktelebot?start={taskid}'
        point_content = f'<div style="font-size: 16px; color: #0057B5;"><b>{name}</b></div><div style="font-size: 12px; color: black;">{description}</div><div><button style="margin-top: 10px;" onclick="window.open(\'{link}\', \'_blank\')">Перейти к заявке</button></div><br/>'
        point_popup = folium.Popup(IFrame(html=point_content, width=400, height=200), max_width=400)
        folium.Marker([lat, lon], popup=point_popup, icon=folium.Icon(color=color)).add_to(marker_cluster)

        # Добавление точки в список попапов
        # popup_content += f'<div style="margin-bottom: 10px;"><b>{name}</b> - <button onclick="window.open(\'{link}\', \'_blank\')">Перейти к заявке</button></div>'
        # popup_content += f'<div style="margin-bottom: 10px; color: {color};"><b>{name}</b><br/>{description}<br/><button onclick="window.open(\'{link}\', \'_blank\')">Перейти к заявке</button><br/><br/></div>'
        # popup_content += f'<div style="margin-bottom: 10px; color: {color};"><b style="color: {color};">{name}</b><br/>{description}<br/><button onclick="window.open(\'{link}\', \'_blank\')">Перейти к заявке</button><br/><br/></div>'
        popup_content += f'<div style="margin-bottom: 10px; color: {color};"><b style="color: {color};">{name}</b><br/><span style="color: black;">{description}</span><br/><button onclick="window.open(\'{link}\', \'_blank\')">Перейти к заявке</button><br/><br/></div>'

    # Создание маркера с иконкой информации
    legend_marker = folium.Marker(location=[41.28921489333344, 69.31288111459628], icon=folium.Icon(color='gray', icon='info-sign'))
    folium.Popup(IFrame(html=popup_content, width=400, height=600), max_width=400).add_to(legend_marker)
    legend_marker.add_to(map)

    # Сохранение карты в HTML-файл
    map.save('public/map.html')