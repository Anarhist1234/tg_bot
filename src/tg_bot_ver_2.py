import telebot
import requests
from telebot import types
import time
import telebot
import requests
from telebot import types
import datetime
import os




if __name__ == "__main__":

    cnt_filt_for_lost_calls = [0]
    cnt_filt_for_conversion = [0]
    cnt_filt_for_avg_sec = [0]

    all_messages_for_lost_calls = {}
    all_messages_for_conversion = {}
    all_messages_for_avg_sec = {}



    bot = telebot.TeleBot('6948990728:AAGHj30De5DHCroQEXPSpelKjse2K6HURE4')


    @bot.message_handler(commands=['lost_calls'])  # создаем команду

    def keyboard_for_lost_calls(message):
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton("👋 Вчера", callback_data= 'Вчера')
        btn2 = types.InlineKeyboardButton("👋 Сегодня", callback_data= 'Сегодня')
        btn3 = types.InlineKeyboardButton("👋 Ручной ввод", callback_data='Ручной ввод')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, text="Привет, {0.first_name}! Я вывожу статистику утерянных звонков. Выбери дату".format(message.from_user), reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        today = datetime.datetime.today()
        one_day = datetime.timedelta(days=1)
        yesterday = today - one_day
        yesterday = yesterday.isoformat().split('T')
        yesterday = yesterday[0]


        today = datetime.datetime.today()
        today = today.isoformat().split('T')
        today = today[0]

        today1 = datetime.datetime.today()
        one_day = datetime.timedelta(days=1)
        tommorow = today1 + one_day
        tommorow = tommorow.isoformat().split('T')
        tommorow = tommorow[0]

        if call.message:
            if call.data == 'Вчера':
                bot.send_message(call.message.chat.id, yesterday)
                response_lost_data = requests.get('http://127.0.0.1:8000/count_lost_calls',
                                                  params={'date_from': yesterday,
                                                          'date_to': today,
                                                          'project_id': None})
                dicti = response_lost_data.json()
                lst = []
                for elem in dicti:
                    for key, value in elem.items():
                        new_lst = []
                        new_lst.append(key)
                        new_lst.append(value)
                        lst.append(new_lst)
                for elem in lst:
                    bot.send_message(call.message.chat.id, f'{elem}')
            elif call.data == 'Сегодня':
                bot.send_message(call.message.chat.id, today)
                response_lost_data = requests.get('http://127.0.0.1:8000/count_lost_calls',
                                                  params={'date_from': today,
                                                          'date_to': tommorow,
                                                          'project_id': None})
                dicti = response_lost_data.json()
                lst = []
                for elem in dicti:
                    for key, value in elem.items():
                        new_lst = []
                        new_lst.append(key)
                        new_lst.append(value)
                        lst.append(new_lst)
                for elem in lst:
                    bot.send_message(call.message.chat.id, f'{elem}')
            elif call.data == 'Ручной ввод':
                a = bot.send_message(call.message.chat.id, "Нажмите на ссылку /lost_calls")
                bot.register_next_step_handler(a, get_start)



    def get_start(message):
        global cnt_filt_for_lost_calls
        global all_messages_for_lost_calls
        try:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            button1 = types.KeyboardButton('Да')
            button2 = types.KeyboardButton('Нет')
            keyboard.add(button1, button2)
            if cnt_filt_for_lost_calls[0] == 0:
                msg = bot.send_message(message.chat.id, 'Начинаем процесс ввода фильтров.Вы готовы?', reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_date_from)
            elif cnt_filt_for_lost_calls[0] == 1:
                all_messages_for_lost_calls[len(all_messages_for_lost_calls) + 1] = message.text
                msg = bot.send_message(message.chat.id, ' Фильтр date_from записан\nДля перехода к следующему фильтра введите Да', reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_date_to)
            elif cnt_filt_for_lost_calls[0] == 2:
                all_messages_for_lost_calls[len(all_messages_for_lost_calls) + 1] = message.text
                msg = bot.send_message(message.chat.id, ' Фильтр date_to записан\nДля перехода к следующему фильтра введите Да', reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_project_id)
            else:
                all_messages_for_lost_calls[len(all_messages_for_lost_calls) + 1] = message.text
                bot.send_message(message.chat.id, 'Конец ввода значений для фильтров')

                if all_messages_for_lost_calls[3] == "-":
                    all_messages_for_lost_calls[3] = None

                response_lost_data = requests.get('http://127.0.0.1:8000/count_lost_calls',
                                                      params={'date_from': all_messages_for_lost_calls[1], 'date_to': all_messages_for_lost_calls[2],
                                                              'project_id': all_messages_for_lost_calls[3]})
                dicti = response_lost_data.json()
                lst = []
                for elem in dicti:
                    for key, value in elem.items():
                            new_lst = []
                            new_lst.append(key)
                            new_lst.append(value)
                            lst.append(new_lst)
                for elem in lst:
                    bot.send_message(message.chat.id, f'{elem}')
                bot.send_message(message.chat.id, f'{dicti}')

                for dct in dicti:
                    for key, value in dct.items():
                        bot.send_message(message.chat.id, f'{key} | {value}')

                cnt_filt_for_lost_calls = [0]
                all_messages_for_lost_calls.clear()
        except:
              bot.send_message(message.chat.id, f'Some error')
              cnt_filt_for_lost_calls = [0]
              all_messages_for_lost_calls.clear()


    def get_date_from(message):

        try:
            if message.text == 'Да':
                cnt_filt_for_lost_calls[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите начальную дату периода в форматe YYYY-MM-DD')
                bot.register_next_step_handler(msg, get_start)
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)

    def get_date_to(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_lost_calls[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите конечную дату периода в форматe YYYY-MM-DD')
                bot.register_next_step_handler(msg, get_start)
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)

    def get_project_id(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_lost_calls[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите id проекта.\nДанный фильтр необязательный\nЕсли не хотите вводить id проекта, введите -')
                bot.register_next_step_handler(msg, get_start)
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)



    @bot.message_handler(commands=['info_phones'])  # создаем команду
    def get_info_phones(message):
        response_lost_data = requests.get('http://127.0.0.1:8000/info_phones')
        dicti = response_lost_data.json()
        for elem in dicti:
            bot.send_message(message.chat.id, f'{elem}')




    @bot.message_handler(commands=['avg_sec'])  # создаем команду

    def keyboard_for_avg_sec(message):
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton("👋 Вчера", callback_data= 'Вчера')
        btn2 = types.InlineKeyboardButton("👋 Сегодня", callback_data= 'Сегодня')
        btn3 = types.InlineKeyboardButton("👋 Ручной ввод", callback_data='Ручной ввод')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, text="Привет, {0.first_name}! Я вывожу среднее время ожидание операторов в статусе READY. Выбери дату".format(message.from_user), reply_markup=markup)

    @bot.callback_query_handler(func=lambda call:True)
    def callback_avg_sec(call):
        today = datetime.datetime.today()
        one_day = datetime.timedelta(days=1)
        yesterday = today - one_day
        yesterday = yesterday.isoformat().split('T')
        yesterday = yesterday[0]


        today = datetime.datetime.today()
        today = today.isoformat().split('T')
        today = today[0]

        today1 = datetime.datetime.today()
        one_day = datetime.timedelta(days=1)
        tommorow = today1 + one_day
        tommorow = tommorow.isoformat().split('T')
        tommorow = tommorow[0]

        if call.message:
            if call.data == 'Вчера':
                bot.send_message(call.message.chat.id, yesterday)
                response_lost_data = requests.get('http://127.0.0.1:8000/avg_sec_in_status_ready_for_each_user',
                                                  params={'date_from': yesterday,
                                                          'date_to': today,
                                                          'project_id': None})
                dicti = response_lost_data.json()
                lst = []
                for elem in dicti:
                    for key, value in elem.items():
                        new_lst = []
                        new_lst.append(key)
                        new_lst.append(value)
                        lst.append(new_lst)
                for elem in lst:
                    bot.send_message(call.message.chat.id, f'{elem}')
            elif call.data == 'Сегодня':
                bot.send_message(call.message.chat.id, today)
                response_lost_data = requests.get('http://127.0.0.1:8000/avg_sec_in_status_ready_for_each_user',
                                                  params={'date_from': today,
                                                          'date_to': tommorow,
                                                          'project_id': None})
                dicti = response_lost_data.json()
                lst = []
                for elem in dicti:
                    for key, value in elem.items():
                        new_lst = []
                        new_lst.append(key)
                        new_lst.append(value)
                        lst.append(new_lst)
                for elem in lst:
                    bot.send_message(call.message.chat.id, f'{elem}')
            elif call.data == 'Ручной ввод':
                a = bot.send_message(call.message.chat.id, "Нажмите на ссылку /avg_sec")
                bot.register_next_step_handler(a, get_start_for_avg)

    def get_start_for_avg(message):
        global cnt_filt_for_avg_sec
        global all_messages_for_avg_sec
        try:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            button1 = types.KeyboardButton('Да')
            button2 = types.KeyboardButton('Нет')
            keyboard.add(button1, button2)
            if cnt_filt_for_avg_sec[0] == 0:
                msg = bot.send_message(message.chat.id, 'Начинаем процесс ввода фильтров.Вы готовы?', reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_date_from_avg)
            elif cnt_filt_for_avg_sec[0] == 1:
                all_messages_for_avg_sec[len(all_messages_for_avg_sec) + 1] = message.text
                msg = bot.send_message(message.chat.id,
                                       ' Фильтр date_from записан\nДля перехода к следующему фильтра введите Да',
                                       reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_date_to_avg)
            else:
                all_messages_for_avg_sec[len(all_messages_for_avg_sec) + 1] = message.text
                bot.send_message(message.chat.id, 'Конец ввода значений для фильтров')

                response_lost_data = requests.get('http://127.0.0.1:8000/avg_sec_in_status_ready_for_each_user',
                                                  params={'date_from': all_messages_for_avg_sec[1], 'date_to': all_messages_for_avg_sec[2]})
                dicti = response_lost_data.json()
                bot.send_message(message.chat.id, f'{dicti}')
                cnt_filt_for_avg_sec = [0]
                all_messages_for_avg_sec.clear()
        except:
            bot.send_message(message.chat.id, 'error')
            cnt_filt_for_avg_sec = [0]
            all_messages_for_avg_sec.clear()


    def get_date_from_avg(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_avg_sec[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите начальную дату периода в форматe YYYY-MM-DD')
                bot.register_next_step_handler(msg, get_start_for_avg)
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_avg_sec)

    def get_date_to_avg(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_avg_sec[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите конечную дату периода в форматe YYYY-MM-DD')
                bot.register_next_step_handler(msg, get_start_for_avg)
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_avg_sec)

    @bot.message_handler(commands=['conversion'])
    def get_start_for_conversion(message):
        global all_messages_for_conversion
        global cnt_filt_for_conversion
        try:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            button1 = types.KeyboardButton('Да')
            button2 = types.KeyboardButton('Нет')
            keyboard.add(button1, button2)
            if cnt_filt_for_conversion[0] == 0:
                msg = bot.send_message(message.chat.id, 'Начинаем процесс ввода фильтров.Вы готовы?', reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_date_from_conversion)
            elif cnt_filt_for_conversion[0] == 1:
                all_messages_for_conversion[len(all_messages_for_conversion) + 1] = message.text
                msg = bot.send_message(message.chat.id, ' Фильтр date_from записан\nДля перехода к следующему фильтра введите Да', reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_date_to_conversion)
            elif cnt_filt_for_conversion[0] == 2:
                all_messages_for_conversion[len(all_messages_for_conversion) + 1] = message.text
                msg = bot.send_message(message.chat.id, ' Фильтр date_to записан\nДля перехода к следующему фильтра введите Да', reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_project_id_conversion)
            elif cnt_filt_for_conversion[0] == 3:
                all_messages_for_conversion[len(all_messages_for_conversion) + 1] = message.text
                msg = bot.send_message(message.chat.id, ' Фильтр project_id записан\nДля перехода к следующему фильтра введите Да', reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_user_id_conversion)
            else:
                all_messages_for_conversion[len(all_messages_for_conversion) + 1] = message.text
                bot.send_message(message.chat.id, 'Конец ввода значений для фильтров')

                if all_messages_for_conversion[3] == "-":
                    all_messages_for_conversion[3] = None

                if all_messages_for_conversion[4] == '-':
                    all_messages_for_conversion[4] = None


                    response_lost_data = requests.get('http://127.0.0.1:8000/conversion',
                                                      params={'date_from': all_messages_for_conversion[1], 'date_to': all_messages_for_conversion[2],
                                                              'project_id': all_messages_for_conversion[3], 'user_id': all_messages_for_conversion[4]})
                    dicti = response_lost_data.json()
                    lst = []
                    if len(lst) == 0:
                        print('Нету информации')
                    else:
                        for elem in dicti:
                            for key, value in elem.items():
                                    new_lst = []
                                    new_lst.append(key)
                                    new_lst.append(value)
                                    lst.append(new_lst)
                        for elem in lst:
                            bot.send_message(message.chat.id, f'{elem}')
                        all_messages_for_conversion.clear()
                        cnt_filt_for_conversion = [0]
        except:
                    bot.send_message(message.chat.id, f'error')
                    all_messages_for_conversion.clear()
                    cnt_filt_for_conversion = [0]





    def get_date_from_conversion(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_conversion[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите начальную дату периода в форматe YYYY-MM-DD')
                bot.register_next_step_handler(msg, get_start_for_conversion)
            else:
                bot.send_message(message.chat.id, 'Введите команду /conversion повторно')
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)

    def get_date_to_conversion(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_conversion[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите конечную дату периода в форматe YYYY-MM-DD')
                bot.register_next_step_handler(msg, get_start_for_conversion)
            else:
                bot.send_message(message.chat.id, 'Введите команду /conversion повторно')

        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)

    def get_project_id_conversion(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_conversion[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите id проекта.\nДанный фильтр необязательный\nЕсли не хотите вводить id проекта, введите -')
                bot.register_next_step_handler(msg, get_start_for_conversion)
            else:
                bot.send_message(message.chat.id, 'Введите команду /conversion повторно')
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)
    def get_user_id_conversion(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_conversion[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите id юезра.\nДанный фильтр необязательный\nЕсли не хотите вводить id юзера, введите -')
                bot.register_next_step_handler(msg, get_start_for_conversion)
            else:
                bot.send_message(message.chat.id, 'Введите команду /conversion повторно')
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)


    @bot.message_handler(commands=['info'])
    def get_start_for_conversion(message):
        bot.send_message(message.chat.id,
    """/avg_sec - Среднее время ожидания операторов в статусе READY
/conversion - Конверсия
/info_phones - Информация о активных операторах
/lost_calls - Информация о потерянных звонках
/info - Доступные команды
         """)


    bot.polling()


