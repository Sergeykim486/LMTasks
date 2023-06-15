import logging
import Classes.functions as functions
import Classes.buttons as buttons
from Classes.config import ActiveUser, bot, db


# Регистрация нового пользователя
class Reg:
    # Запрос имени у пользователя
    def reg1(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        except Exception as e:
            logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
            pass
        if message.text == '🔑 Регистрация':
            if message.chat.id == 5390927006:
                bot.send_message(
                    message.chat.id,
                    "Вы не можете зарегистрироваться.",
                    reply_markup=buttons.Buttons(['ok'])
                )
                bot.stop_polling()
            bot.send_message(
                message.chat.id,
                'Как Вас зовут (укажите имя)',
            reply_markup=buttons.clearbuttons()
            )
            bot.register_next_step_handler(message, Reg.reg2)
        else:
            bot.send_message(
                message.chat.id,
                'Пожалуйста зарегистрируйтесь.',
                reply_markup=buttons.Buttons(['🔑 Регистрация'])
            )
            bot.register_next_step_handler(message, Reg.reg1)
    # Сохранение имени и запрос фамилии
    def reg2(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        except Exception as e:
            logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
            pass
        global ActiveUser
        ActiveUser[message.chat.id]['FirstName'] = message.text
        bot.send_message(
            message.chat.id,
            'Укажите Вашу фамилию.',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Reg.reg3)
    # Сохранение фамилии и запрос номера телефона
    def reg3(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        except Exception as e:
            logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
            pass
        global ActiveUser
        ActiveUser[message.chat.id]['LastName'] = message.text
        bot.send_message(
            message.chat.id,
            'Введите Ваш номер телефона в формате (+998 00 000 0000).',
            reply_markup=buttons.clearbuttons()
        )
        bot.register_next_step_handler(message, Reg.reg4)
    # Сохранение телефона и запрос на подтверждение сохраненных данных
    def reg4(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        except Exception as e:
            logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
            pass
        global ActiveUser
        ActiveUser[message.chat.id]['PhoneNumber'] = message.text
        bot.send_message(
            message.chat.id,
            functions.conftext(message, ActiveUser),
            reply_markup=buttons.Buttons(['✅ Да', '⛔️ Нет'])
        )
        bot.register_next_step_handler(message, Reg.reg5)
    # Проверка подтверждения данных
    def reg5(message):
        try:
            username = db.get_record_by_id('Users', message.chat.id)[2] + ' ' + db.get_record_by_id('Users', message.chat.id)[1]
            logging.info(f'\nℹ️ {username} Отправил запрос\n    -    {message.text}\n')
        except Exception as e:
            logging.error(f'\n🆘 Ошибка!\n    ⚠️ - {e}\n')
            pass
        global ActiveUser
        if message.text == '✅ Да':
            valuedict = [
                ActiveUser[message.chat.id]['id'],
                ActiveUser[message.chat.id]['FirstName'],
                ActiveUser[message.chat.id]['LastName'],
                ActiveUser[message.chat.id]['PhoneNumber']
            ]
            db.insert_record("Users", valuedict)
            bot.send_message(
                message.chat.id,
                'Поздравляем Вы успешно зарегистрировались!',
                reply_markup=buttons.Buttons(['🏠 Главное меню'])
            )
            ActiveUser[message.chat.id]['Pause_main_handler'] = False
            ActiveUser[message.chat.id]['Finishedop'] = True
            ActiveUser[message.chat.id]['block_main_menu'] = False
        elif message.text == '⛔️ Нет':
            bot.send_message(
                message.chat.id,
                'Пройдите регистрацию повторно.',
                reply_markup=buttons.Buttons(['🔑 Регистрация'])
            )
            bot.register_next_step_handler(message, Reg.reg1)
        else:
            bot.send_message(
                message.chat.id,
                'Вы не подтвердили информацию!\n' + functions.conftext(message, ActiveUser),
                reply_markup=buttons.Buttons(['✅ Да', '⛔️ Нет'])
            )
            bot.register_next_step_handler(message, Reg.reg5)
