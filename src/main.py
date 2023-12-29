import telebot
from telebot import types
from config import API_URLs, TelegramData
import time
import datetime
import requests
from loguru import logger
from db import PgDriver
from threading import Thread

bot = telebot.TeleBot(TelegramData.access_token)
cnt_filt_for_lost_calls = [0]
cnt_filt_for_avg_sec = [0]
cnt_filt_for_conversion = [0]

all_messages_for_lost_calls = {}
all_messages_for_avg_sec = {}
all_messages_for_conversion = {}

def send_message_in_chat_cycle():
    while True:
        logger.info(f"TIME {datetime.datetime.now().hour}")

        with PgDriver() as curr:
            curr.execute(
                """
                with projects_count as (
                    select count(phone) as count, pr.id, pr.name from phones ph
                    left join projects pr on ph.project_id = pr.id
                    where pr.is_active = true and ph.used = false
                    group by pr.id, pr.name
                ),
                projects_count_users as (
                    select pc.count, pc.id, pc.name, count(u.id) as active_users_count from projects_count pc
                    left join project_user pu on pu.project_id = pc.id
                    left join users u on u.id = pu.user_id
                    where u.status != 'OFFLINE'
                    group by pc.id, pc.name, pc.count
                )
                select * from projects_count_users
                where active_users_count > 0
                """
            )

            items = curr.fetchall()

        for item in items:
            logger.info(f"{item['name']} - {item['count']} users {item['active_users_count']}")
            if item["count"] <= 50:
                text = f"В проекте {item['name']} осталось номеров: {item['count']}"
                api_url = f'https://api.telegram.org/bot{TelegramData.access_token}/sendMessage'
                params = {'chat_id': TelegramData.chat_id, 'text': text}

                response = requests.post(api_url, params=params)
                result = response.json()

                logger.info(f"send_mes, {result}")

        time.sleep(10)

def main():
    @bot.message_handler(commands=['start'])
    def keyboard_for_start(message):
        markup = types.InlineKeyboardMarkup(row_width=3)
        btn1 = types.InlineKeyboardButton("😠 Вчера", callback_data='lost_yest')
        btn2 = types.InlineKeyboardButton("😃 Сегодня", callback_data='lost_today')
        btn3 = types.InlineKeyboardButton("❓ Ручной ввод ", callback_data='manual_lost')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, text="Статистика утерянных звонков".format(message.from_user),
                         reply_markup=markup)

        markup1 = types.InlineKeyboardMarkup(row_width=3)
        btn4 = types.InlineKeyboardButton("😠 Вчера", callback_data='avg_yest')
        btn5 = types.InlineKeyboardButton("😃 Сегодня", callback_data='avg_today')
        btn6 = types.InlineKeyboardButton("❓ Ручной ввод ", callback_data='manual_avg')
        markup1.add(btn4, btn5, btn6)
        bot.send_message(message.chat.id,
                         text="Среднее время ожидания каждого оператора в статусе READY".format(message.from_user),
                         reply_markup=markup1)

        markup2 = types.InlineKeyboardMarkup(row_width=3)
        btn7 = types.InlineKeyboardButton("😠 Вчера", callback_data='conv_yest')
        btn8 = types.InlineKeyboardButton("😃 Сегодня", callback_data='conv_today')
        btn9 = types.InlineKeyboardButton("❓ Ручной ввод ", callback_data='manual_conv')
        markup2.add(btn7, btn8, btn9)
        bot.send_message(message.chat.id, text="Конверсия за определенный период".format(message.from_user),
                         reply_markup=markup2)

        markup3 = types.InlineKeyboardMarkup(row_width=1)
        btn10 = types.InlineKeyboardButton("😎 Вывести", callback_data='info_phones')
        markup3.add(btn10)
        bot.send_message(message.chat.id,
                         text="Информация об активных операторах".format(message.from_user),
                         reply_markup=markup3)

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
            if call.data == 'lost_yest':
                response_lost_data = requests.get(API_URLs.lost_calls,
                                                  params={'date_from': yesterday,
                                                          'date_to': today,
                                                          'project_id': None})
                dicti = response_lost_data.json()
                dct = dicti[0]
                value_percent_without_out = round(dct['percent_without_outbound'], 4)  # Процент утерянных звонков без учетом входящих
                value_percent_w_out = round(dct['percent_with_outbound'], 4)  # Процент утерянных звонков с учетом входящих
                cnt_without_usr_out = dct['count_without_user_and_outbound']  # Количество утерянных звонков без входящих
                cnt_all_without_out = dct['count_all_without_outbound']  # Количество всех звонков без входящих
                cnt_without_user = dct['count_without_user']  # Количество утерянных звонков с учетом входящих
                cnt_all_w_out = dct['count_all_with_outbound']  # Количество всех звонков с учетом входящих
                bot.send_message(call.message.chat.id, f"""
{yesterday}
Процент утерянных звонков без учета входящих = {value_percent_without_out}%
Процент утерянных звонков с учетом входящих = {value_percent_w_out}%
Кол-во утерянных звонков без входящих  = {cnt_without_usr_out}
Кол-во всех звонков без входящих = {cnt_all_without_out}
Кол-во утерянных звонков с учетом входящих   = {cnt_without_user}
Кол-во всех звонков с учетом входящих = {cnt_all_w_out}
                                    """)
            elif call.data == 'lost_today':
                response_lost_data = requests.get(API_URLs.lost_calls,
                                                  params={'date_from': today,
                                                          'date_to': tommorow,
                                                          'project_id': None})
                dicti = response_lost_data.json()
                dct = dicti[0]
                value_percent_without_out = round(dct['percent_without_outbound'], 4)  # Процент утерянных звонков без учетом входящих
                value_percent_w_out = round(dct['percent_with_outbound'],4)  # Процент утерянных звонков с учетом входящих
                cnt_without_usr_out = dct['count_without_user_and_outbound']
                cnt_all_without_out = dct['count_all_without_outbound']
                cnt_without_user = dct['count_without_user']
                cnt_all_w_out = dct['count_all_with_outbound']
                bot.send_message(call.message.chat.id, f"""
{today}
Процент утерянных звонков без учета входящих = {value_percent_without_out}%
Процент утерянных звонков с учетом входящих = {value_percent_w_out}%
Кол-во утерянных звонков без входящих  = {cnt_without_usr_out}
Кол-во всех звонков без входящих = {cnt_all_without_out}
Кол-во утерянных звонков с учетом входящих   = {cnt_without_user}
Кол-во всех звонков с учетом входящих = {cnt_all_w_out}
                                    """)
            elif call.data == 'manual_lost':
                a = bot.send_message(call.message.chat.id, "Нажмите на ссылку /lost_calls")
                bot.register_next_step_handler(a, get_start)

            elif call.data == 'avg_yest':
                bot.send_message(call.message.chat.id, yesterday)
                response_lost_data = requests.get(API_URLs.average_seconds,
                                                  params={'date_from': yesterday,
                                                          'date_to': today})
                dicti = response_lost_data.json()
                lst = []
                for dct in dicti:
                    string = f"""user_id= {dct['user_id']}
created_at= {dct['created_at']}
avg_total= {dct['avg_total']}"""
                    lst.append(string)
                lst = '\n----------------\n'.join(lst)
                bot.send_message(call.message.chat.id, f'{lst}')

            elif call.data == 'avg_today':
                bot.send_message(call.message.chat.id, today)
                response_lost_data = requests.get(API_URLs.average_seconds,
                                                  params={'date_from': today,
                                                          'date_to': tommorow})
                dicti = response_lost_data.json()
                lst = []
                for dct in dicti:
                    string = f"""user_id= {dct['user_id']}
created_at= {dct['created_at']}
avg_total= {dct['avg_total']}"""
                    lst.append(string)
                lst = '\n----------------\n'.join(lst)
                bot.send_message(call.message.chat.id, f'{lst}')


            elif call.data == 'manual_avg':
                a = bot.send_message(call.message.chat.id, "Нажмите на ссылку /avg_sec")
                bot.register_next_step_handler(a, get_start_for_avg)


            elif call.data == 'conv_today':
                response_lost_data = requests.get(API_URLs.conversion,
                                                  params={'date_from': yesterday,
                                                          'date_to': today,
                                                          'project_id': None,
                                                          'user_id': None})
                dicti = response_lost_data.json()
                dct = dicti[0]
                key = round(dct['percentage'], 4)
                bot.send_message(call.message.chat.id, f"""
Период {today}
Процент конверсии = {key}% """)

            elif call.data == 'conv_yest':
                response_lost_data = requests.get(API_URLs.conversion,
                                                  params={'date_from': today,
                                                          'date_to': tommorow,
                                                          'project_id': None,
                                                          'user_id': None})
                dicti = response_lost_data.json()
                dct = dicti[0]
                key = round(dct['percentage'], 4)
                bot.send_message(call.message.chat.id, f"""
Период {yesterday}
Процент конверсии = {key}% """)

            elif call.data == 'manual_conv':
                a = bot.send_message(call.message.chat.id, "Нажмите на ссылку /conversion")
                bot.register_next_step_handler(a, get_start_for_conversion)

            elif call.data == 'info_phones':
                a = bot.send_message(call.message.chat.id, "Нажмите на ссылку /info_phones")
                bot.register_next_step_handler(a, get_info_phones)

    @bot.message_handler(commands=['lost_calls'])
    def get_start(message):
        global cnt_filt_for_lost_calls
        global all_messages_for_lost_calls
        try:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            button1 = types.KeyboardButton('Да')
            button2 = types.KeyboardButton('Нет')
            keyboard.add(button1, button2)
            if cnt_filt_for_lost_calls[0] == 0:
                msg = bot.send_message(message.chat.id, 'Начинаем процесс ввода фильтров.Вы готовы?',
                                       reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_date_from)
            elif cnt_filt_for_lost_calls[0] == 1:
                all_messages_for_lost_calls[len(all_messages_for_lost_calls) + 1] = message.text
                msg = bot.send_message(message.chat.id,
                                       ' Фильтр date_from записан\nДля перехода к следующему фильтра введите Да',
                                       reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_date_to)
            elif cnt_filt_for_lost_calls[0] == 2:
                all_messages_for_lost_calls[len(all_messages_for_lost_calls) + 1] = message.text
                msg = bot.send_message(message.chat.id,
                                       ' Фильтр date_to записан\nДля перехода к следующему фильтра введите Да',
                                       reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_project_id)
            else:
                all_messages_for_lost_calls[len(all_messages_for_lost_calls) + 1] = message.text
                bot.send_message(message.chat.id, 'Конец ввода значений для фильтров')

                if all_messages_for_lost_calls[3] == "-":
                    all_messages_for_lost_calls[3] = None

                response_lost_data = requests.get(API_URLs.lost_calls,
                                                  params={'date_from': all_messages_for_lost_calls[1],
                                                          'date_to': all_messages_for_lost_calls[2],
                                                          'project_id': all_messages_for_lost_calls[3]})
                dicti = response_lost_data.json()
                dct = dicti[0]
                value_percent_without_out = round(dct['percent_without_outbound'],
                                                  4)  # Процент утерянных звонков без учетом входящих
                value_percent_w_out = round(dct['percent_with_outbound'],
                                            4)  # Процент утерянных звонков с учетом входящих
                cnt_without_usr_out = dct['count_without_user_and_outbound']
                cnt_all_without_out = dct['count_all_without_outbound']
                cnt_without_user = dct['count_without_user']
                cnt_all_w_out = dct['count_all_with_outbound']
                bot.send_message(message.chat.id, f"""
Период с {all_messages_for_lost_calls[1]} до {all_messages_for_lost_calls[2]}
Процент утерянных звонков без учета входящих = {value_percent_without_out}%
Процент утерянных звонков с учетом входящих = {value_percent_w_out}%
Кол-во утерянных звонков без входящих  = {cnt_without_usr_out}
Кол-во всех звонков без входящих = {cnt_all_without_out}
Кол-во утерянных звонков с учетом входящих   = {cnt_without_user}
Кол-во всех звонков с учетом входящих = {cnt_all_w_out}
                    """)
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
            else:
                msg = bot.send_message(message.chat.id, 'Выполнение прекращено')
                cnt_filt_for_lost_calls[0] = 0



        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)

    def get_date_to(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_lost_calls[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите конечную дату периода в форматe YYYY-MM-DD')
                bot.register_next_step_handler(msg, get_start)
            else:
                msg = bot.send_message(message.chat.id, 'Выполнение прекращено')
                cnt_filt_for_lost_calls[0] = 0
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)

    def get_project_id(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_lost_calls[0] += 1
                msg = bot.send_message(message.chat.id,
                                       'Введите id проекта.\nДанный фильтр необязательный\nЕсли не хотите вводить id проекта, введите -')
                bot.register_next_step_handler(msg, get_start)
            else:
                msg = bot.send_message(message.chat.id, 'Выполнение прекращено')
                cnt_filt_for_lost_calls[0] = 0
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)

    @bot.message_handler(commands=['info_phones'])  # создаем команду
    def get_info_phones(message):
        response_lost_data = requests.get(API_URLs.info_phones)
        dicti = response_lost_data.json()
        lst = []
        for dct in dicti:
            string = f"""Количество телефонов= {dct['count']}
Название проекта = {dct['name']}
Кол-во активных операторов = {dct['active_users_count']}"""
            lst.append(string)
        lst = '\n----------------\n'.join(lst)
        bot.send_message(message.chat.id, f'{lst}')

    @bot.message_handler(commands=['avg_sec'])  # создаем команду
    def get_start_for_avg(message):
        global cnt_filt_for_avg_sec
        global all_messages_for_avg_sec
        try:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
            button1 = types.KeyboardButton('Да')
            button2 = types.KeyboardButton('Нет')
            keyboard.add(button1, button2)
            if cnt_filt_for_avg_sec[0] == 0:
                msg = bot.send_message(message.chat.id, 'Начинаем процесс ввода фильтров.Вы готовы?',
                                       reply_markup=keyboard)
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

                response_lost_data = requests.get(API_URLs.average_seconds,
                                                  params={'date_from': all_messages_for_avg_sec[1],
                                                          'date_to': all_messages_for_avg_sec[2]})
                dicti = response_lost_data.json()
                bot.send_message(message.chat.id,
                                 f'Фильтры: {all_messages_for_avg_sec[1]}, {all_messages_for_avg_sec[2]}')
                lst = []
                for dct in dicti:
                    string = f"""user_id= {dct['user_id']}
created_at= {dct['created_at']}
avg_total= {dct['avg_total']}"""
                    lst.append(string)
                lst = '\n----------------\n'.join(lst)
                try:
                    bot.send_message(message.chat.id, f'{lst}')
                    cnt_filt_for_avg_sec = [0]
                    all_messages_for_avg_sec.clear()
                except:
                    bot.send_message(message.chat.id,
                                     f'{lst[:4095]}')
                    bot.send_message(message.chat.id,
                                     f'Очень большое сообщение. Часть сообщения была обрезана. Выполните команду заново и выберите меньший период')
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
            else:
                msg = bot.send_message(message.chat.id, 'Выполнение прекращено')
                cnt_filt_for_avg_sec[0] = 0
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_avg_sec)

    def get_date_to_avg(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_avg_sec[0] += 1
                msg = bot.send_message(message.chat.id, 'Введите конечную дату периода в форматe YYYY-MM-DD')
                bot.register_next_step_handler(msg, get_start_for_avg)
            else:
                msg = bot.send_message(message.chat.id, 'Выполнение прекращено')
                cnt_filt_for_avg_sec[0] = 0

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
                msg = bot.send_message(message.chat.id, 'Начинаем процесс ввода фильтров.Вы готовы?',
                                       reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_date_from_conversion)
            elif cnt_filt_for_conversion[0] == 1:
                all_messages_for_conversion[len(all_messages_for_conversion) + 1] = message.text
                msg = bot.send_message(message.chat.id,
                                       ' Фильтр date_from записан\nДля перехода к следующему фильтра введите Да',
                                       reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_date_to_conversion)
            elif cnt_filt_for_conversion[0] == 2:
                all_messages_for_conversion[len(all_messages_for_conversion) + 1] = message.text
                msg = bot.send_message(message.chat.id,
                                       ' Фильтр date_to записан\nДля перехода к следующему фильтра введите Да',
                                       reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_project_id_conversion)
            elif cnt_filt_for_conversion[0] == 3:
                all_messages_for_conversion[len(all_messages_for_conversion) + 1] = message.text
                msg = bot.send_message(message.chat.id,
                                       ' Фильтр project_id записан\nДля перехода к следующему фильтра введите Да',
                                       reply_markup=keyboard)
                bot.register_next_step_handler(msg, get_user_id_conversion)
            else:
                all_messages_for_conversion[len(all_messages_for_conversion) + 1] = message.text
                bot.send_message(message.chat.id, 'Конец ввода значений для фильтров')

                if all_messages_for_conversion[3] == "-":
                    all_messages_for_conversion[3] = None

                if all_messages_for_conversion[4] == '-':
                    all_messages_for_conversion[4] = None

                    response_lost_data = requests.get(API_URLs.conversion,
                                                      params={'date_from': all_messages_for_conversion[1],
                                                              'date_to': all_messages_for_conversion[2],
                                                              'project_id': all_messages_for_conversion[3],
                                                              'user_id': all_messages_for_conversion[4]})
                    dicti = response_lost_data.json()
                    dct = dicti[0]
                    key = round(dct['percentage'], 4)
                    bot.send_message(message.chat.id,
                                     f'Фильтры: {all_messages_for_conversion[1]}, {all_messages_for_conversion[2]}, {all_messages_for_conversion[3]} , {all_messages_for_conversion[4]}  ')
                    bot.send_message(message.chat.id, f'Процент конверсии = {key}% ')
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
                cnt_filt_for_conversion[0] = 0
                bot.send_message(message.chat.id, 'Выполнение прекращено')
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
                cnt_filt_for_conversion[0] = 0
                bot.send_message(message.chat.id, 'Выполнение прекращено')

        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)

    def get_project_id_conversion(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_conversion[0] += 1
                msg = bot.send_message(message.chat.id,
                                       'Введите id проекта.\nДанный фильтр необязательный\nЕсли не хотите вводить id проекта, введите -')
                bot.register_next_step_handler(msg, get_start_for_conversion)
            else:
                cnt_filt_for_conversion[0] = 0
                bot.send_message(message.chat.id, 'Выполнение прекращено')
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)

    def get_user_id_conversion(message):
        try:
            if message.text == 'Да':
                cnt_filt_for_conversion[0] += 1
                msg = bot.send_message(message.chat.id,
                                       'Введите id юезра.\nДанный фильтр необязательный\nЕсли не хотите вводить id юзера, введите -')
                bot.register_next_step_handler(msg, get_start_for_conversion)
            else:
                cnt_filt_for_conversion[0] = 0
                bot.send_message(message.chat.id, 'Выполнение прекращено')
        except:
            bot.send_message(message.chat.id, f'Вы ответили {message.text}. Выполните повторно команду бота.')
            print(all_messages_for_lost_calls)

    @bot.message_handler(commands=['info'])
    def get_start_for_info(message):
        bot.send_message(message.chat.id,
                         """
                     /avg_sec - Среднее время ожидания операторов(статус READY)
                     /conversion - Конверсия
                     /info_phones - Информация о активных операторах
                     /lost_calls - Информация о потерянных звонках
                     /info - Доступные команды
                              """)

    while True:
        try:
            bot.polling(non_stop=True, interval=0)
        except Exception as e:
            print(e)
            time.sleep(5)
            continue



if __name__ == "__main__":
    t1 = Thread(target=send_message_in_chat_cycle)
    t2 = Thread(target=main)

    t1.start()
    t2.start()







