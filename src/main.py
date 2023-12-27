
import telebot
import requests
from telebot import types


if __name__ == "__main__":
    bot = telebot.TeleBot('6948990728:AAGHj30De5DHCroQEXPSpelKjse2K6HURE4')


    @bot.message_handler(commands=['lost_calls'])  # создаем команду
    def lost_calls(message):
         try:
            msg = bot.send_message(message.chat.id, """Input date_from, date_to, project_id, user_id in format YYYY-MM-DD/YYYY-MM-DD/proj_id
If you don\'t want to use project_id   use - instead of project_id """)
            bot.register_next_step_handler(msg, get_lost_calls2)
         except:
            return bot.send_message(message.chat.id,'not correct parametr form')

    def get_lost_calls2(message):
        try:
            message_from_user = message.text
            lst_data = message_from_user.split('/')
            if lst_data[2] == '-':
                lst_data[2] = None
            else:
                lst_data[2] = int(lst_data[2])

            markup1 = types.InlineKeyboardMarkup()
            response_lost_data = requests.get('http://127.0.0.1:8000/count_lost_calls',
                                              params={'date_from': lst_data[0], 'date_to': lst_data[1], 'project_id': lst_data[2]})
            dicti = response_lost_data.json()
            lst = []
            for elem in dicti:
                for key, value in elem.items():
                    new_lst = []
                    new_lst.append(key)
                    new_lst.append(value)
                    lst.append(new_lst)
            bot.send_message(message.chat.id, f'{lst}', reply_markup=markup1)
        except:
            return bot.send_message(message.chat.id,'not correct parametr form')


    @bot.message_handler(commands=['avg_sec'])  # создаем команду
    def get_avg_sec(message):
        try:
            msg = bot.send_message(message.chat.id, 'Input date_from, date_to in format YYYY-MM-DD/YYYY-MM-DD')
            bot.register_next_step_handler(msg, get_avg_sec2)
        except:
            return bot.send_message(message.chat.id, 'not correct parametr form')

    def get_avg_sec2(message):
        try:
            message_from_user = message.text
            lst_data = message_from_user.split('/')

            markup = types.InlineKeyboardMarkup()
            response_lost_data = requests.get('http://127.0.0.1:8000/avg_sec_in_status_ready_for_each_user',
                                              params={'date_from': lst_data[0], 'date_to': lst_data[1]})
            dicti = response_lost_data.json()
            bot.send_message(message.chat.id, f'{dicti}', reply_markup=markup)
        except:
            return bot.send_message(message.chat.id,'not correct parametr form')




    @bot.message_handler(commands=['conversion'])  # создаем команду
    def get_conversion(message):
        try:
            msg = bot.send_message(message.chat.id, """Input date_from, date_to, project_id, user_id in format YYYY-MM-DD/YYYY-MM-DD/proj_id/user_id
    If you don\'t want to use project_id or user_id,  use - instead of project_id or user_id""")
            bot.register_next_step_handler(msg, get_conversion2)
        except:
            return bot.send_message(message.chat.id, 'not correct parametr form')

    def get_conversion2(message):
        try:
            message_from_user = message.text
            lst_data = message_from_user.split('/')
            if lst_data[2] == '-' and lst_data[3] == '-':
                lst_data[2] = None
                lst_data[3] = None
            elif lst_data[2] != '-' and lst_data[3] != '-':
                lst_data[2] = int(lst_data[2])
                lst_data[3] = int(lst_data[3])
            elif lst_data[2] == '-':
                lst_data[2] = None
                lst_data[3] = int(lst_data[3])
            elif lst_data[3] == '-':
                lst_data[3] = None
                lst_data[2] = int(lst_data[2])
            print(lst_data)
            markup = types.InlineKeyboardMarkup()
            response_lost_data = requests.get('http://127.0.0.1:8000/conversion',
                                              params={'date_from': lst_data[0], 'date_to': lst_data[1], 'project_id': lst_data[2], 'user_id': lst_data[3]})
            dicti = response_lost_data.json()

            bot.send_message(message.chat.id, f'{dicti}', reply_markup=markup)
        except:
            return bot.send_message(message.chat.id,'not correct parametr form')


    @bot.message_handler(commands=['info_phones'])  # создаем команду
    def get_info_phones(message):
        response_lost_data = requests.get('http://127.0.0.1:8000/info_phones')
        dicti = response_lost_data.json()
        bot.send_message(message.chat.id, f'{dicti}')


    bot.polling(none_stop=True, interval=0)


