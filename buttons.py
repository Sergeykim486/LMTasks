import telebot, config
bot = telebot.TeleBot(config.TOKEN)

def Buttons(buttons, r = 2, cancelbut = None):
    markup = telebot.types.ReplyKeyboardRemove()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if cancelbut is not None:
        markup.row('Отмена')
    result = []
    for i in range(0, len(buttons), r):
        result.append(buttons[i:i+r])
    for line in result:
        markup.row(*line)
    return markup

def Buttons1(buttons, r = 3):
    markup = telebot.types.ReplyKeyboardRemove()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    result = []
    first = buttons[0]
    last = buttons[len(buttons) - 1]
    buttons.remove(buttons[0])
    buttons.remove(buttons[len(buttons) - 1])
    markup.row(first)
    for i in range(0, len(buttons), r):
        result.append(buttons[i:i+r])
    for line in result:
        markup.row(*line)
    markup.row(last)
    markup.row('Отмена')
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