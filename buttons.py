import telebot, config
bot = telebot.TeleBot(config.TOKEN)

def Buttons(buttons):
    markup = telebot.types.ReplyKeyboardRemove()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(*buttons)
    return markup

def buttonsinline(buttons):
    markup = telebot.types.ReplyKeyboardRemove()
    markup = telebot.types.InlineKeyboardMarkup()
    for button in buttons:
        tx = button[0]
        cd = button[1]
        markup.add(telebot.types.InlineKeyboardButton(text=tx, callback_data=cd))
    return markup

def clearbuttons():
    markup = telebot.types.ReplyKeyboardRemove()
    return markup