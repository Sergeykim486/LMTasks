import telebot, Classes.config as config
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

def reportbuttons(line1, line2, line3, line4, line5):
    markup = telebot.types.ReplyKeyboardRemove()
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.row(*line1)
    markup.row(*line2)
    markup.row(*line3)
    markup.row(*line4)
    markup.row(*line5)
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

# ⬜️🔳
def buttonslist(filter):
    buttonsl = ['Указать период', 'Зарегистрированные', 'В работе', 'Завершенные', 'Отмененные', 'Только мои', 'Сформировать']
    if filter["added"] == 1:
        buttonsl[1] = "🔳 Зарегистрированные"
    else:
        buttonsl[1] = "⬜️ Зарегистрированные"
    if filter["confirmed"] == 1:
        buttonsl[2] = "🔳 В работе"
    else:
        buttonsl[2] = "⬜️ В работе"
    if filter["done"] == 1:
        buttonsl[3] = "🔳 Завершенные"
    else:
        buttonsl[3] = "⬜️ Завершенные"
    if filter["canceled"] == 1:
        buttonsl[4] = "🔳 Отмененные"
    else:
        buttonsl[4] = "⬜️ Отмененные"
    if filter["justmy"] == 1:
        buttonsl[5] = "🔳 Только мои"
    else:
        buttonsl[5] = "⬜️ Только мои"
    return buttonsl

def buttonsinline(buttons):
    markup = telebot.types.InlineKeyboardMarkup()
    row = []
    for button in buttons:
        tx = button[0]
        cd = button[1]
        row.append(telebot.types.InlineKeyboardButton(text=tx, callback_data=cd))
        if len(row) == 2:
            markup.row(*row)
            row = []
    if row:
        markup.row(*row)
    return markup

def clearbuttons():
    markup = telebot.types.ReplyKeyboardRemove()
    return markup