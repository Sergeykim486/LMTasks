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

# from folium.plugins import MarkerCluster
# from folium import IFrame
# from urllib.parse import quote

# def mapgen(locations):
#     # Создание объекта карты
#     map = folium.Map(location=[41.28927613679946, 69.31295641163192], zoom_start=12)

#     # Создание группы маркеров
#     marker_cluster = MarkerCluster().add_to(map)

#     # Создание списка точек с попапами
#     popup_content = ""
#     for location in locations:
#         name = location[0]
#         taskid = name.split()[1]
#         description = location[1]
#         lat = float(location[2])
#         lon = float(location[3])
#         color = 'blue'
#         if location[4] == 2:
#             color = 'orange'
#         elif location[4] == 3:
#             color = 'green'
#         elif location[4] == 4:
#             color = 'red'
#         link = f'https://t.me/labmonotasktelebot?start={taskid}'
#         point_content = f'<div style="font-size: 16px; color: #0057B5;"><b>{name}</b></div><div style="font-size: 12px; color: black;">{description}</div><div><button style="margin-top: 10px;" onclick="window.open(\'{link}\', \'_blank\')">Перейти к заявке</button></div><br/>'
#         point_popup = folium.Popup(IFrame(html=point_content, width=300, height=200), max_width=300)
#         folium.Marker([lat, lon], popup=point_popup, icon=folium.Icon(color=color)).add_to(marker_cluster)

#         # Добавление точки в список попапов
#         popup_content += f'<div style="margin-bottom: 10px; color: {color};"><b style="color: {color};">{name}</b><br/><span style="color: black;">{description}</span><br/><button onclick="window.open(\'{link}\', \'_blank\')">Перейти к заявке</button><br/><br/></div>'

#     # Создание маркера с иконкой информации
#     legend_marker = folium.Marker(location=[41.28921489333344, 69.31288111459628], icon=folium.Icon(color='gray', icon='info-sign'))
#     folium.Popup(IFrame(html=popup_content, width=300, height=600), max_width=300).add_to(legend_marker)
#     legend_marker.add_to(map)

#     # Сохранение карты в HTML-файл
#     map.save('public/map.html')



# from folium.plugins import MarkerCluster
# from folium import IFrame
# from urllib.parse import quote

# def mapgen(locations):
#     # Создание объекта карты
#     map = folium.Map(location=[41.28927613679946, 69.31295641163192], zoom_start=12)

#     # Создание группы маркеров
#     marker_cluster = MarkerCluster().add_to(map)

#     # Создание списка точек с попапами
#     popup_content = ""

#     # Легенды
#     legend_content = '''
#         <div style="font-size: 20px; color: black;"><b>Условные обозначения:</div><br/>
#         <div style="margin-bottom: 10px; color: blue;"><b style="color: blue;">████</b> - Заявки не принятые мастерами</b></div>
#         <div style="margin-bottom: 10px; color: orange;"><b style="color: orange;">████</b> - Заявки у мастеров</b></div>
#         <div style="margin-bottom: 10px; color: green;"><b style="color: green;">████</b> - Выполненные заявки</b></div>
#         <div style="margin-bottom: 10px; color: red;"><b style="color: red;">████</b> - Отмененные заявки</div><br/>
#     '''
    
#     legend_popup = folium.Popup(IFrame(html=legend_content, width=200, height=150), max_width=200)
#     legend_marker = folium.Marker(location=[41.28921489333344, 69.31288111459628], icon=folium.Icon(color='gray', icon='info-sign'), popup=legend_popup)
#     legend_marker.add_to(map)

#     for location in locations:
#         name = location[0]
#         taskid = name.split()[1]
#         description = location[1]
#         lat = float(location[2])
#         lon = float(location[3])
#         color = 'blue'
#         if location[4] == 2:
#             color = 'orange'
#         elif location[4] == 3:
#             color = 'green'
#         elif location[4] == 4:
#             color = 'red'
#         link = f'https://t.me/labmonotasktelebot?start={taskid}'
#         point_content = f'<div style="font-size: 16px; color: #0057B5;"><b>{name}</b></div><div style="font-size: 12px; color: black;">{description}</div><div><button style="margin-top: 10px;" onclick="window.open(\'{link}\', \'_blank\')">Перейти к заявке</button></div><br/>'
#         point_popup = folium.Popup(IFrame(html=point_content, width=370, height=200), max_width=370)
#         folium.Marker([lat, lon], popup=point_popup, icon=folium.Icon(color=color)).add_to(marker_cluster)
        
#         # Добавление точки в список попапов
#         popup_content += f'<div style="margin-bottom: 10px; color: {color};"><b style="color: {color};">{name}</b><br/><span style="color: black;">{description}</span><br/><button onclick="window.open(\'{link}\', \'_blank\')">Перейти к заявке</button><br/><br/></div>'

#     # Добавление легенды в список попапов
#     popup_content = legend_content + popup_content

#     # Создание маркера с иконкой информации
#     legend_marker = folium.Marker(location=[41.28921489333344, 69.31288111459628], icon=folium.Icon(color='gray', icon='info-sign'))
#     folium.Popup(IFrame(html=popup_content, width=400, height=600), max_width=400).add_to(legend_marker)
#     legend_marker.add_to(map)

#     # Добавление кнопки обновления страницы
#     refresh_button = '''
#         <button onclick="location.reload();" style="position: absolute; top: 10px; right: 10px; z-index: 9999; background-color: green; color: white;">Обновить страницу</button>
#     '''
#     map.get_root().html.add_child(folium.Element(refresh_button))

#     # Сохранение карты в HTML-файл
#     map.save('public/map.html')




# import folium
# from folium.plugins import MarkerCluster
# from jinja2 import Template

# def generate_popup(location):
#     name = location[0]
#     description = location[1]
#     status = location[4]
#     task_id = name.split()[1]
#     link = f"https://t.me/labmonotasktelebot?start={task_id}"

#     # Set color based on status
#     color = 'blue'
#     if status == '2':
#         color = 'orange'
#     elif status == '3':
#         color = 'green'
#     elif status == '4':
#         color = 'red'

#     popup_html = f"""
#         <div>
#             <h2 style="color:{color}; font-size:16px; font-weight:bold;">{name}</h2>
#             <p style="color:black; font-size:12px;">{description}</p>
#             <a href="{link}" target="_blank" style="background-color:{color}; color:white;" class="button">Перейти к заявке</a>
#         </div>
#     """
#     return popup_html

# def mapgen(locations):
#     # Create map
#     map_object = folium.Map(location=[41.28927613679946, 69.31295641163192], zoom_start=12)

#     # Create marker cluster
#     marker_cluster = MarkerCluster().add_to(map_object)

#     # Add markers to the cluster
#     for location in locations:
#         name = location[0]
#         lat = location[2]
#         lon = location[3]
#         status = location[4]

#         # Create popup for the marker
#         popup_html = generate_popup(location)
#         popup = folium.Popup(popup_html, max_width=250)

#         # Set marker color based on status
#         marker_color = 'blue'
#         if status == '2':
#             marker_color = 'orange'
#         elif status == '3':
#             marker_color = 'green'
#         elif status == '4':
#             marker_color = 'red'

#         # Create marker with popup
#         marker = folium.Marker(location=[lat, lon], popup=popup, icon=folium.Icon(color=marker_color))
#         marker.add_to(marker_cluster)

#     # Generate HTML and save to file
#     template = Template('''
#         <html>
#         <head>
#             <title>Активные заявки</title>
#             <style>
#                 .button {
#                     padding: 10px 20px;
#                     display: inline-block;
#                     border-radius: 4px;
#                     font-size: 14px;
#                     margin-top: 10px;
#                 }
#                 .blue {
#                     background-color: blue;
#                     color: white;
#                 }
#                 .orange {
#                     background-color: orange;
#                     color: white;
#                 }
#                 .green {
#                     background-color: green;
#                     color: white;
#                 }
#                 .red {
#                     background-color: red;
#                     color: white;
#                 }
#                 .button:hover {
#                     opacity: 0.8;
#                 }
#                 .scrollable-list {
#                     height: 600px;
#                     overflow-y: scroll;
#                 }
#             </style>
#         </head>
#         <body>
#             <header>
#                 <h1>Активные заявки</h1>
#                 <img src="public/logo.png" alt="Logo" style="float:right;">
#                 <button onclick="location.reload();" style="background-color:green; color:white; font-weight:bold;">Обновить страницу</button>
#             </header>
#             <div>
#                 <div class="scrollable-list" style="width:30%; float:left;">
#                     {% for location in locations %}
#                         <div style="margin-bottom: 20px;">
#                             <h2 class="{% if location[4] == '1' %}blue{% elif location[4] == '2' %}orange{% elif location[4] == '3' %}green{% elif location[4] == '4' %}red{% endif %}" style="font-size:16px; font-weight:bold;">{{ location[0] }}</h2>
#                             <p style="color:black; font-size:12px;">{{ location[1] }}</p>
#                             <a href="https://t.me/labmonotasktelebot?start={{ location[0].split()[1] }}" target="_blank" class="{% if location[4] == '1' %}blue{% elif location[4] == '2' %}orange{% elif location[4] == '3' %}green{% elif location[4] == '4' %}red{% endif %} button">Перейти к заявке</a>
#                         </div>
#                     {% endfor %}
#                 </div>
#                 <div style="width:70%; float:right;">
#                     {{ folium_map|safe }}
#                 </div>
#             </div>
#         </body>
#         </html>
#     ''')
#     folium_map = map_object._repr_html_()
#     html = template.render(folium_map=folium_map, locations=locations)

#     with open('public/map.html', 'w') as file:
#         file.write(html)




import folium
from folium.plugins import MarkerCluster
from jinja2 import Template

def generate_popup(location):
    name = location[0].replace('|', '<br>')
    description = location[1].replace('|', '<br>')
    status = location[4]
    task_id = name.split()[1]
    link = f"https://t.me/labmonotasktelebot?start={task_id}"

    # Set color based on status
    color = 'black'
    if status == 1:
        color = 'blue'
    elif status == 2:
        color = 'orange'
    elif status == 3:
        color = 'green'
    elif status == 4:
        color = 'red'

    popup_html = f"""
        <div style="width: auto;">
            <p style="color:{color}; font-size:16px; font-weight:bold;">{name}</p>
            <p style="color:black; font-size:12px;">{description}</p>
            <button onclick="window.open('{link}', '_blank')" style="background-color:{color}; color:white; font-size:16px;">Перейти к заявке</button>
        </div>
    """
    return popup_html

def generate_marker_html(location):
    name = location[0].replace('|', '<br>')
    description = location[1].replace('|', '<br>')
    status = location[4]

    # Set color based on status
    color = 'black'
    if status == 1:
        color = 'blue'
    elif status == 2:
        color = 'orange'
    elif status == 3:
        color = 'green'
    elif status == 4:
        color = 'red'

    marker_html = f"""
        <div>
            <p style="color:{color}; font-size:16px; font-weight:bold;">{name}</p>
            <p style="color:black; font-size:12px;">{description}</p>
            <button onclick="window.open('https://t.me/labmonotasktelebot?start={name.split()[1]}', '_blank')" style="background-color:{color}; color:white; font-size:16px;">Перейти к заявке</button><br><br>
        </div>
    """
    return marker_html

def mapgen(locations):
    # Create map
    map_object = folium.Map(location=[41.28927613679946, 69.31295641163192], zoom_start=12)

    # Create marker cluster
    marker_cluster = MarkerCluster().add_to(map_object)

    # Add markers to the cluster
    for location in locations:
        name = location[0]
        lat = location[2]
        lon = location[3]
        status = location[4]

        # Create popup for the marker
        popup_html = generate_popup(location)
        popup = folium.Popup(popup_html, max_width='auto')

        # Set marker color based on status
        marker_color = 'black'
        if status == 1:
            marker_color = 'blue'
        elif status == 2:
            marker_color = 'orange'
        elif status == 3:
            marker_color = 'green'
        elif status == 4:
            marker_color = 'red'

        # Create marker with popup
        marker = folium.Marker(location=[lat, lon], popup=popup, icon=folium.Icon(color=marker_color))
        marker.add_to(marker_cluster)

    # Generate HTML and save to file
    template = Template('''
        <html>
        <head>
            <title>Активные заявки</title>
            <style>
                .button {
                    padding: 10px 20px;
                    display: inline-block;
                    border-radius: 4px;
                    font-size: 12px;
                    justify-self: flex-start;
                }
                .blue {
                    color: blue;
                }
                .orange {
                    color: orange;
                }
                .green {
                    color: green;
                }
                .red {
                    color: red;
                }
                .map-container {
                    height: calc(100% - 130px);
                    overflow: auto;
                }
                header {
                    height: 100px;
                    display: flex;
                    align-items: flex-start;
                    justify-content: space-between;
                }
                .logo {
                    margin-top: 20px;
                    margin-right: 20px;
                    align-self: flex-start;
                    justify-self: flex-end;
                }
            </style>
        </head>
        <body>
            <header>
                <div style="align-self: flex-start;">
                    <h1 style="margin-top: 0; margin-left: 20px;">Активные заявки</h1>
                    <button onclick="location.reload();" style="background-color: green; color: white; font-weight: bold; font-size: 18px; margin-top: -10px; margin-left: 20px;">Обновить страницу</button>
                </div>
                <div class="logo">
                    <img src="Logo.png" alt="Logo" style="height: 56px;">
                </div>
            </header>
            <div class="map-container" style="width: 70%; float: right;">
                {{ folium_map|safe }}
            </div>
            <div class="scrollable-list" style="width: 30%; float: left; height: calc(100% - 130px); overflow: auto;">
                <div style="margin-bottom: 20px;">
                    <h2 style="color: black; font-size: 18px; font-weight: bold;">Условные обозначения</h2>
                    <p style="color: blue; font-size: 14px;">████ - Заявки не принятые мастерами</p>
                    <p style="color: orange; font-size: 14px;">████ - Заявки у мастеров</p>
                    <p style="color: green; font-size: 14px;">████ - Выполненные заявки</p>
                    <p style="color: red; font-size: 14px;">████ - Отмененные заявки</p>
                    <br>
                </div>
                {% for location in locations %}
                    <div style="margin-bottom: 20px;">
                        {{ generate_marker_html(location) }}
                    </div>
                {% endfor %}
            </div>
        </body>
        </html>
    ''')
    folium_map = map_object._repr_html_()
    html = template.render(folium_map=folium_map, locations=locations, generate_marker_html=generate_marker_html)

    with open('public/map.html', 'w', encoding='utf-8') as file:
        file.write(html)
