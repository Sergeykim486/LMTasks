tasks = db.select_table('Tasks',['id', 'added', 'contragent', 'status'])
taskslist = functions.listgen(tasks, [0, 1, 3, 10], 1)
for line in taskslist:
    print(line)
    taskid = line.split()[2]
    print('номер заявки - ' + taskid)
    bot.send_message(
        message.chat.id,
        line,
        reply_markup=buttons.buttonsinline([['Показать подробности', 'tasklist '+taskid]])
    )
bot.send_message(
    message.chat.id,
    'Вернитесь в главное меню.',
    reply_markup=buttons.Buttons(['Главное меню'])
)
