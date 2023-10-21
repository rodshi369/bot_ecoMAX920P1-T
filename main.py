# -*- coding: utf-8 -*-

import os
import sys
import datetime
import time
import sqlite3
import csv
import db
import asyncio

import telebot
from telebot import types
import threading
import queue
# import const
import set

import reader_plum
import logging
# import subscribe


# Настройка логирования в файл
# logging.basicConfig(filename='bot.log', level=logging.ERROR)
logging.basicConfig(filename='bot.log', format = "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s", datefmt='%H:%M:%S')

bot = telebot.TeleBot(set.TOKEN)
########### Инициализируем базы данных
db.init_db()
db.init_db_passing()

######################################
def signal_handler():
    pass

_ON = True
q = queue.Queue()
ON_OFF = False
stream = 0
# thr = threading.Thread(target=subscribe.subcribe_sensors)
# thr.start()


def main(bot, id, q):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Остановить', callback_data="Остановить"))

    to_pin = bot.send_message(id, 'Читаю данные...', reply_markup=markup).message_id
    # CHANNEL_NAME = '-1001909359532'
    # channel_message = bot.send_message(CHANNEL_NAME, 'Читаю данные...').message_id
    # setpoints(id, to_pin)
    # bot.pin_chat_message(chat_id=id, message_id=to_pin)
    # a = 0
    predvalue = {"heating_temp": (0, 0),
                 "current_temp": (0, 0),
                 "return_temp":  (0, 0),
                 "exhaust_temp": (0, 0)}
    arrow_up = "↑"
    arrow_down = "↓"
    while globals()["ON_OFF"]:
        asyncio.run(reader_plum.run(q))
        data_ = q.get()
        txtstate = str(data_["state"])

        heating_temp_trande = data_["heating_temp"]-predvalue["heating_temp"][0]
        heating_temp_trande = str(round(heating_temp_trande, 2))+arrow_up if heating_temp_trande >= predvalue["heating_temp"][1] else str(round(heating_temp_trande, 2))+arrow_down

        current_temp_trade = data_['mixers'][0].data['current_temp']-predvalue["current_temp"][0]
        current_temp_trade = str(round(current_temp_trade, 2))+arrow_up if current_temp_trade >= predvalue["current_temp"][1] else str(round(current_temp_trade, 2))+arrow_down

        return_temp_trade = data_["return_temp"]-predvalue["return_temp"][0]
        return_temp_trade = str(round(return_temp_trade, 2))+arrow_up if return_temp_trade >= predvalue["return_temp"][1] else str(round(return_temp_trade, 2))+arrow_down

        exhaust_temp_trade = data_["exhaust_temp"]-predvalue["exhaust_temp"][0]
        exhaust_temp_trade = str(round(exhaust_temp_trade, 2))+arrow_up if exhaust_temp_trade >= predvalue["exhaust_temp"][1] else str(round(exhaust_temp_trade, 2))+arrow_down

        textdata = "*Опрос системы:*" + \
                   "\nРежим работы:  "+txtstate+\
                   "\nТемп.котла:  "+str(round(data_["heating_temp"], 2))+"; "+heating_temp_trande+";  Уст: "+str(data_["heating_target"])+ \
                   "\nТемп.смесит.: " + str(round(data_['mixers'][0].data['current_temp'], 2)) + "; " + current_temp_trade + "; Уст: " + str(data_['mixers'][0].data['target_temp']) + \
                   "\nТемп.возвр.: " + str(round(data_["return_temp"], 2)) + "; " + return_temp_trade + \
                   "\nТемп.прод.горен.: " + str(round(data_["exhaust_temp"], 2)) + "; "+exhaust_temp_trade + \
                   "\nТемп.подачи топл.: "+str(round(data_["feeder_temp"], 2)) +\
                   "\nТемп.ГВС:                        "+str(round(data_["water_heater_temp"], 2)) + \
                   "\nНасос:                            " + ("Вкл" if data_['mixers'][0].data['pump'] else "Выкл") + \
                   "\nТемп.с наружи:              "+str(round(data_["outside_temp"], 2)) +\
                   "\nМощность вентилятора:        "+str(data_["fan_power"])

        predvalue = {"heating_temp": (round(data_["heating_temp"], 2),                   float(heating_temp_trande[:-1])),
                     "current_temp": (round(data_['mixers'][0].data['current_temp'], 2), float(current_temp_trade[:-1])),
                     "return_temp":  (round(data_["return_temp"], 2),                    float(return_temp_trade[:-1])),
                     "exhaust_temp": (round(data_["exhaust_temp"], 2),                   float(exhaust_temp_trade[:-1]))}
        try:
            bot.edit_message_text(chat_id=id, message_id=to_pin, text=textdata, reply_markup=markup, parse_mode="Markdown")
        except Exception as err:
            logging.error("Произошла ошибка при обработке сообщения: Результат опроса", err.args[0])

        time.sleep(15)
    delete = bot.delete_message(chat_id=id, message_id=to_pin)
    # delete = bot.delete_message(chat_id=CHANNEL_NAME, message_id=channel_message)


def setpoints(id):
    # opis = bot.get_my_description()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Вкл.регулятор', callback_data="Вкл.регулятор"))
    markup.add(types.InlineKeyboardButton(text='Откл.регулятор', callback_data="Откл.регулятор"))
    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data="Отмена"))
    bot.send_message(id, text="Управление", reply_markup=markup)
    # markup = types.InlineKeyboardMarkup()
    # markup.add(types.InlineKeyboardButton(text="Вкл/Отключить опрос", callback_data=1))
    # bot.send_message(id, reply_markup=markup)


def restart_program():
    python = sys.executable
    try:
        # os.execv(python, python, *sys.argv)
        # os.execl(python, python, 'd:\PYthon\bot_ecoMAX920P1-T\main.py')
        os.execv(sys.executable, [python] + sys.argv)
    except Exception as err:
        print(err)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    answer = "Выберите действие"
    select = call.data
    # message = call.data[1]
    if select == "Отмена":
        try:
            bot.answer_callback_query(callback_query_id=call.id, text='Отбой')
        except Exception as err:
            logging.error("Произошла ошибка при обработке сообщения: Отмена", err.args[0])
        # answer = 'Выберите действие'

    elif select == "Остановить":
        globals()["ON_OFF"] = False

        try:
            bot.answer_callback_query(callback_query_id=call.id, text='Остановка')
        except Exception as err:
            logging.error("Произошла ошибка при обработке сообщения: Остановить", err.args[0])
        # answer = 'Выберите действие'

    elif select == "Перезапустить бот":
        bot.answer_callback_query(callback_query_id=call.id, text='Перезапуск')
        restart_program()
        # answer = 'Выберите действие'

    elif select == 'Вкл.регулятор':
        # await reader_plum.OnOff("Вкл")
        asyncio.run(reader_plum.OnOff("Вкл"))
        bot.answer_callback_query(callback_query_id=call.id, text="Вкл.регулятор")
        answer = 'Включено'
    elif select == 'Откл.регулятор':
        # await reader_plum.OnOff("Выкл")
        asyncio.run(reader_plum.OnOff("Выкл"))
        bot.answer_callback_query(callback_query_id=call.id, text="Откл.регулятор")
        answer = "Выключено"
    #################################### contour
    elif select == 'Кривая нагрева контура':
        msg = bot.send_message(call.from_user.id, "Введите значение -: Кривая нагрева контура")
        bot.register_next_step_handler(msg,  writer, id =('heat_curve', 'QDoubleSpinBox', 'mixer'))

    elif select == 'Параллельный сдвиг контура':
        msg = bot.send_message(call.from_user.id, "Введите значение -Параллельный сдвиг контура:")
        bot.register_next_step_handler(msg,  writer, id=('parallel_offset_heat_curve', 'QSpinBox', 'mixer'))

        ################################ boiler
    elif select == '"Кривая нагрева"':
        msg = bot.send_message(call.from_user.id, "Введите значение: Кривая нагрева")
        bot.register_next_step_handler(msg, writer, id=('heating_heat_curve', 'QDoubleSpinBox', ' '))

    elif select == "Параллельный сдвиг":
        msg = bot.send_message(call.from_user.id, "Введите значение: Параллельный сдвиг")
        bot.register_next_step_handler(msg, writer, id=('heating_heat_curve_shift', 'QSpinBox', ''))

    else:
        pass
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=answer,
                          reply_markup=None)
    except Exception as err:
        logging.error("", err.args[0])

def writer(message, id):
    rez = asyncio.run(reader_plum.writer(message, id))
    pass


class User:
    def __init__(self, id):
        self.id = id
        self.code = None
        self.password = None

# isauthorized = False

user = User(None)


def _init_propusk():
    query = """SELECT userid,  first_name, last_name, username, pass, datareg FROM users;"""
    otvet = {}
    rez = db.get_record(query, "")
    one_result = rez.fetchall()
    # one_result[0]
    if one_result.__len__() > 0:
        i = 0
        for i in range(0, one_result.__len__()):
            # one_result[i] = one_result[i] + (False, 0)
            otvet[str(one_result[i][0])] = {"userid": one_result[i][0], "first_name": one_result[i][1],
                                            "last_name": one_result[i][2], "username": one_result[i][3],
                                            "pass": one_result[i][4], "datareg": one_result[i][5], "active": False}
            i += 1
    else:
        pass
    return otvet

isauthorized = _init_propusk()


######################################################################################### Проверка пароля
def inputpass(message, schet):
    if schet == 1:
        suffix = ' (попробуй 123)'
    elif schet == 2:
        suffix = ' (qwerty однозначно)'
    else:
        suffix = ""
    bot.send_message(message.from_user.id, "Попытка №" + str(schet + 1) + suffix)
    msg = bot.reply_to(message, """Введите пароль:""")
    bot.register_next_step_handler(msg, verifypass, schet)


def verifypass(message, schet):
    if message.text == str(isauthorized[str(message.from_user.id)]["pass"]):
        bot.send_message(message.from_user.id, "Небось угадал.")
        isauthorized[str(message.from_user.id)]["active"] = True
        mainmenu(message)
    else:
        schet = schet + 1
        if schet <= 2:
            inputpass(message, schet)
        else:
            bot.send_message(message.from_user.id, "Вы какой то подозрительный.")
            bot.clear_step_handler_by_chat_id(chat_id=message.from_user.id)


######################################################################################### Проверка пароля
def makeCSV(data):
    try:
        with open("temp.csv", mode="w", encoding="cp1251") as w_file:
            names = ["id", "dt", "lighting", "installed_lighting", "out1", "out3", "out4", "af1", "af2", "f1"]
            file_writer = csv.DictWriter(w_file, delimiter=";", lineterminator="\r", fieldnames=names)
            file_writer.writeheader()
            for rec in data:
                file_writer.writerow(
                    {"id": rec[0], "dt": rec[1], "lighting": rec[2], "installed_lighting": rec[3], "out1": rec[4],
                     "out3": rec[5], "out4": rec[6], "af1": rec[7], "af2": rec[8], "f1": rec[9]})

            return w_file
    except Exception as err:
        pass


@bot.message_handler(commands=['help'])  # стартовая команда
def help(message):
    bot.reply_to(message, "Бог тебе в помощь.")


@bot.message_handler(commands=['start'])  # стартовая команда
def start(message):
    # Зарегистрируем проходящего
    dt = datetime.datetime.now()
    db.add_record_passing([message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                           message.from_user.username, dt])
    #############################
    if isauthorized.get(str(message.from_user.id)) == None or isauthorized.__len__() == 0:
        registration(message)
    elif isauthorized[str(message.from_user.id)]["active"] is True:
        bot.send_message(message.from_user.id, "Вы авторизованны.")
        mainmenu(message)
        return
    else:
        schet = 0
        inputpass(message, schet)


########################################################################### Регистрация
@bot.message_handler(commands=['reg'])  # команда
def registration(message):
    # if globals()["isauthorized"] is True:
    #     bot.send_message(message.from_user.id, "Вы уже авторизованы.")
    #     return
    bot.reply_to(message, "{who}\nНеобходима регистрация.".format(who=message.from_user.first_name))
    try:
        chat_id = message.from_user.id
        name = message.text
        user = User(message.from_user.id)
        # user_dict[chat_id] = user
        bot.send_message(message.from_user.id, 'Начнём регистацию.')
        msg = bot.send_message(message.from_user.id, 'Введите ключ проекта')
        bot.register_next_step_handler(msg, process_code_step, user)
    except Exception as e:
        bot.reply_to(message, 'Опаньки(oooops)')


def process_code_step(message, user):
    try:
        chat_id = message.from_user.id
        # id = message.text
        # user = User(message.from_user.id)
        user.code = message.text
        if user.code != '369':
            bot.send_message(message.from_user.id, "Неправильный ключ. Обратитесь к Буратино.")
            return
        msg = bot.reply_to(message, 'Введите пароль?')
        bot.register_next_step_handler(msg, process_pass_step, user)
    except Exception as e:
        bot.reply_to(message, 'Опаньки(oooops')


def process_pass_step(message, user):
    try:
        chat_id = message.from_user.id
        name = message.text
        user.password = message.text
        db.add_record([message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                       message.from_user.username, user.password, datetime.datetime.now()])

        isauthorized[str(message.from_user.id)] = {"userid": message.from_user.id,
                                                   "first_name": message.from_user.first_name,
                                                   "last_name": message.from_user.last_name,
                                                   "username": message.from_user.username,
                                                   "pass": user.password, "datareg": datetime.datetime.now(),
                                                   "active": True}
        # bot.register_next_step_handler(msg, process_age_step)
        # globals()["isauthorized"] = _init_propusk()
    except Exception as e:
        bot.reply_to(message, 'Опаньки(oooops')


########################################################################### Регистрация
def checkregistrationаvtorizacion(message):
    try:
        if message == None:
            query = """SELECT *  FROM users """
            param = {}
        else:
            # query = """SELECT userid, first_name, last_name, username  FROM users WHERE userid = :userid and first_name =:first_name and last_name = :last_name and username = :username"""
            query = """SELECT userid, first_name, last_name, username, pass, datareg  FROM users WHERE userid = :userid and first_name =:first_name"""
            param = {"userid": message.from_user.id, "first_name": message.from_user.first_name}

        rez = db.get_record(query, param)
        one_result = rez.fetchall()
        if one_result.__len__() > 0:
            return [True, one_result, 0]
        else:
            return [False, one_result, 0]
    except sqlite3.Error as err:
        print(err)


def mainmenu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
    btn1 = types.KeyboardButton("Опрос состояния")
    # btn2 = types.KeyboardButton("Вкл")
    # btn3 = types.KeyboardButton("Отключить опрос")
    btn4 = types.KeyboardButton("Котел")
    btn5 = types.KeyboardButton("Контуры")
    btn6 = types.KeyboardButton("Вкл/Выкл")
    btn7 = types.KeyboardButton("Bot")
    # btn4 = types.KeyboardButton('Управление')
    markup.add(btn1, btn4, btn5, btn6, btn7)

    id_mess = bot.send_message(message.from_user.id, "Выберите действие", reply_markup=markup).message_id
    # delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    # bot.send_message(message.from_user.id, reply_markup=markup)


def ControlPanel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    btn1 = types.KeyboardButton("Котел")
    btn2 = types.KeyboardButton("Контуры")
    btn3 = types.KeyboardButton("ВКЛ/ВЫКЛ")
    btn4 = types.KeyboardButton('Главное меню')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.from_user.id, "Выберите действие", reply_markup=markup)


def boiler(massage):

    id = massage.from_user.id

    to_pin = bot.send_message(id, 'Читаю данные...').message_id
    # bot.send_chat_action(chat_id=id, action=telebot.con.constants.ChatAction.TYPING)
    asyncio.run(reader_plum.run(q))
    data_ = q.get()
    # data_ = globals()['q'].get()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Погодное управление: '+"Вкл" if str(data_['heating_weather_control'].value) == "on" else "Выкл" +str(data_['heating_weather_control'].value), callback_data="Погодное управление"))
    markup.add(types.InlineKeyboardButton(text='Кривая нагрева: '+str(data_['heating_heat_curve'].value), callback_data="Кривая нагрева"))
    markup.add(types.InlineKeyboardButton(text='Параллельный сдвиг: ' + str(data_['heating_heat_curve_shift'].value), callback_data="Параллельный сдвиг"))
    # markup.add(types.InlineKeyboardButton(text='Погодное управление: ', callback_data="Погодное управление"))
    # markup.add(types.InlineKeyboardButton(text='Кривая нагрева: ', callback_data="Кривая нагрева"))
    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data="Отмена"))
    # bot.send_message(id, text="Управление", reply_markup=markup)
    text = "*Управление котлом:*" +\
            "\nТемп. котла:             " + str(round(data_["heating_temp"], 2)) + ";  Уст: " + str(data_["heating_target"])

    bot.edit_message_text(chat_id=id, message_id=to_pin, text=text, reply_markup=markup, parse_mode="Markdown")


def contour(massage):
    id = massage.from_user.id
    to_pin = bot.send_message(id, 'Читаю данные...').message_id

    asyncio.run(reader_plum.run(q))
    data_ = q.get()
    # data_ = globals()['q'].get()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text='Погодное управление: ' + "Вкл" if str(data_['heating_weather_control'].value) == "on" else "Выкл" + str(
            data_['heating_weather_control'].value), callback_data="Погодное управление"))
    markup.add(types.InlineKeyboardButton(text='Кривая нагрева контура: '+str(data_['mixers'][0].data['heat_curve'].value), callback_data="Кривая нагрева контура"))
    markup.add(types.InlineKeyboardButton(text='Параллельный сдвиг контура: ' + str(data_['mixers'][0].data['parallel_offset_heat_curve'].value-20), callback_data="Параллельный сдвиг контура"))
    # markup.add(types.InlineKeyboardButton(text='Погодное управление: ', callback_data="Погодное управление"))
    # markup.add(types.InlineKeyboardButton(text='Кривая нагрева: ', callback_data="Кривая нагрева"))
    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data="Отмена"))
    # bot.send_message(id, text="Управление", reply_markup=markup)
    bot.edit_message_text(chat_id=id, message_id=to_pin, text='*Управление отоплением:*' +
                                                              "\nТемп. смесителя:     "+str(round(data_['mixers'][0].data['current_temp'], 2))+"; Уст: "+str(data_['mixers'][0].data['target_temp']) +
                                                              "\nТемп. возврата:      " + str(round(data_['return_temp'], 2))
                          , reply_markup=markup, parse_mode="Markdown")


def Bot(massage):

    id = massage.from_user.id

    to_pin = bot.send_message(id, 'Читаю данные...').message_id
    # bot.send_chat_action(chat_id=id, action=telebot.con.constants.ChatAction.TYPING)
    # asyncio.run(reader_plum.run(q))
    # data_ = q.get()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Сбросить опрос', callback_data="Остановить"))
    markup.add(types.InlineKeyboardButton(text='Перезапустить бот', callback_data='Перезапустить бот'))
    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data="Отмена"))
    # bot.send_message(id, text="Управление", reply_markup=markup)
    text = "*Управление ботом:*"

    bot.edit_message_text(chat_id=id, message_id=to_pin, text=text, reply_markup=markup, parse_mode="Markdown")



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # list(filter(lambda x: x[4] == 123, isauthorized))[0]
    if isauthorized.get(str(message.from_user.id)) == None or isauthorized.__len__() == 0:
        dt = datetime.datetime.now()
        db.add_record_passing([message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                               message.from_user.username, dt])
        registration(message)
    elif isauthorized[str(message.from_user.id)]["active"] is False:
        pass
        # bot.send_message(message.from_user.id, "Авторизуйтесь.")
        # start(message)
        # dt = datetime.datetime.now()
        # db.add_record_passing([message.from_user.id, message.from_user.first_name, message.from_user.last_name,
        #                        message.from_user.username, disauthorizedt])
        # bot.send_message(message.from_user.id, "Авторизуйтесь(/start).")
        # return
    else:
        pass
        # mainmenu(message)

    if message.text == 'Главное меню':
        mainmenu(message)
        delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

    elif message.text == 'Опрос состояния':
        if globals()["stream"] in threading._active:
            delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            return
        else:
            globals()["ON_OFF"] = False
            globals()["stream"] = 0

        if globals()["ON_OFF"] == True:
            delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            return

        globals()["ON_OFF"] = True
        delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        id = message.from_user.id
        t1 = threading.Thread(target=main, args=[bot, id, q], daemon=True)
        t1.start()

        logging.info("Запущен процесс ",t1.name)
        globals()["stream"] = t1.ident
        t1.join()
        # opros(id)
        delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    # elif message.text == 'Вкл':
    #     pass
    elif message.text == 'Отключить опрос':
        globals()["ON_OFF"] = False
        delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

    elif message.text == "Управление":
        ControlPanel(message)
        # setpoints(message.from_user.id)
        delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

    elif message.text == "Главное меню":
        mainmenu(message)
        delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

    elif message.text == "Вкл/Выкл":
        setpoints(message.from_user.id)
        delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

    elif message.text == "Котел":
        boiler(message)
        delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

    elif message.text == "Контуры":
        contour(message)
        delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    elif message.text =="Bot":
        Bot(message)
        delete = bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
# bot.polling(none_stop=True, interval=0)  # обязательная для работы бота часть
bot.infinity_polling(timeout=10, long_polling_timeout=5)
