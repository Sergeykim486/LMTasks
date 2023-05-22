import telebot, time, logging
from telebot import TeleBot, types
# логи
# Глобальная переменная, база и создание объекта бот
bot = telebot.TeleBot('6132283589:AAEUF8awZ7QfNjcqwztC0GjSj4JPWyWG4BE')

@bot.message_handler(commands=['start'])
# проверка пользователя при первом запуске
def check_user_id(message):
    bot.send_message(
        message.from_user.id,
        'Кинь локаццию или координаты через в формате:\n широта, долгота\n гугл и яндекс как раз выдают их в таком виде.',
    )
    bot.register_next_step_handler(message, locations)


@bot.message_handler(content_types=['text', 'location'])
# формирование гугл ссылки на карты по локации для адреса компании
def locations(message):
    if message.content_type == 'location':
        print('location')
        try:
            lon, lat = message.location.longitude, message.location.latitude
            url = f'https://www.google.com/maps/search/?api=1&query={lat},{lon}'
            bot.send_message(
                message.chat.id,
                f'координаты: {lat}, {lon}\nГугл ссылка: {url}'
            )
        except Exception as e:
            logging.error(e)
            pass
    else:
        print('coordinates')
        try:
            coordinates = message.text.replace(' ', '').split(',')
            loc = types.Location(coordinates[1], coordinates[0])
            bot.send_location(message.chat.id, loc.latitude, loc.longitude)
        except Exception as e:
            logging.error(e)
            pass
    bot.register_next_step_handler(message, locations)
    
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            time.sleep(5)