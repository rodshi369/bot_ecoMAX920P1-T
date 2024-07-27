# -*- coding: utf-8 -*-
import psutil
import os
import sys
import datetime
import time
import sqlite3
import csv
import json

import bible
import const
import db
import asyncio

import telebot
from telebot import types

from pyqadmin import admin
import win32serviceutil
import multiprocessing

import threading
import queue
import set
import psutil

from pyplumio.const import AlertType
import reader_plum
import app_logger

import gpt

# Настройка логирования в файл
logger = app_logger.get_logger(__name__)
# logger.info("Начало работы.")
#
bot = telebot.TeleBot(set.TOKEN)
########### Инициализируем базы данных
db.init_db()
db.init_db_passing()

# _ON = True
quefirst = multiprocessing.Queue()
# que = queue.Queue()
# que = multiprocessing.Queue
STREAM = []


# @bot.callback_query_handler(func=lambda call: True)
# def callback_function1(callback_obj):
#     if callback_obj.data == "button1":
#         bot.send_message(callback_obj.from_user.id, "Вы нажали на кнопку 1")
#     else:
#         bot.send_message(callback_obj.from_user.id, "Вы нажали на кнопку 2")
#     bot.answer_callback_query(callback_query_id=callback_obj.id)

class Dispatcher():
    global STREAM
    thread = ""

    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self, id, quefirst):
        que = multiprocessing.Queue()
        que = True
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text='Остановить', callback_data="Остановить"))
        to_pin = bot.send_message(id, 'Читаю данные...', reply_markup=markup).message_id

        t2 = multiprocessing.Process(target=survey.survey, args=(id, que, to_pin, markup))
        t2.start()
        time.sleep(5)
        first_survey_point = True
        while self._running and quefirst:
            with open('survey_point.json', 'r', encoding='utf-8') as f:  # открыли файл с данными
                try:
                    param = json.load(f)
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))

            tektime = datetime.datetime.now()
            rrr = datetime.datetime.strptime(param["survey_point"], '%Y-%m-%d %H:%M:%S.%f')
            delta = tektime - rrr
            print(tektime, rrr, delta)
            # if first_survey_point:
            #     to_pin = que.get()
            if delta.seconds > 40 and not first_survey_point:
                t2.terminate()
                time.sleep(2)
                t2.close()
                # try:
                #     bot.delete_message(chat_id=id, message_id=to_pin)
                # except Exception as err:
                #     logger.error("Ошибка удавления сообщения при перезапуске: . {err}".format(err=err.args[0]))
                logger.error("Перезапуск опроса.")
                t2 = multiprocessing.Process(target=survey.survey, args=(id, que, to_pin, markup))
                t2.start()
                print("Опрос перезапущен.")
            first_survey_point = False
            time.sleep(15)
        que = False
        t2.terminate()
        time.sleep(2)
        t2.close()


class Survey():
    global STREAM

    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def survey(self, id, que, to_pin, markup):
        self._running = True
        # markup = types.InlineKeyboardMarkup()
        # markup.add(types.InlineKeyboardButton(text='Остановить', callback_data="Остановить"))
        # try:
        #     to_pin = bot.send_message(id, 'Читаю данные...', reply_markup=markup).message_id
        #     que.put(to_pin)
        # except Exception as err:
        #     logger.error("Ошибка при обработке сообщения: Читаю данные. {err}".format(err=err.args[0]))
        t = time.localtime()
        _time = time.strftime("%H:%M:%S", t)

        predvalue = {"heating_temp": (0, 0),
                     "current_temp": (0, 0),
                     "return_temp": (0, 0),
                     "exhaust_temp": (0, 0),
                     "time": _time}
        arrow_up = "↑"
        arrow_down = "↓"
        qqq = 0
        while que:
            # Отключим опрос
            qqq += 1

            # t = datetime.datetime.now()
            # que.put(t)
            # que.send([t])

            # self.getTime()
            # try:
            #     data_ = asyncio.run(reader_plum.run())
            # except Exception as err:
            #     logger.error("Ошибка параметра state {err}", err=err)
            # finally:
            #     print("Быдыщь", data_["dt"])
            #
            listparam = [["ecomax_control", "state", "heating_temp", "heating_target", "return_temp", "feeder_temp", "exhaust_temp", "water_heater_temp", "heating_pump",
                          "fan_power", "boiler_load", "outside_temp",
                          "pending_alerts", "alarm", "lighter","regdata"],
                         ["current_temp", "target_temp"]]

            data_ = asyncio.run(reader_plum.getparameter(listparam))

            checklist = bible.checkingdict(listparam, data_)
            if checklist.__len__() != 0:
                print("Не прочитаны {l}".format(l=checklist))
                time.sleep(3)
                continue
            # Запишем точку опроса
            with open('survey_point.json', 'w', encoding='utf-8') as f:  # открыли файл с данными
                try:
                    # t = time.strftime("%H:%M:%S", time.localtime())
                    t = datetime.datetime.now()
                    param = {"survey_point": str(t)}

                    json.dump(param, f, ensure_ascii=False)  # загнали все, что получилось в переменную
                except IOError as e:
                    print("I/O error({0}): {1}".format(e.errno, e.strerror))

            # que.put(data_)
            # try:
            #     txtstate = const.DeviceStateRus[data_["state"]]
            # except Exception as err:
            #     logger.error("Ошибка параметра state  {err}".format(err=err))

            # txtstate = const.DeviceStateRus[data_["state"]]
            perekur = "\U0001F6AC"
            # perekur = '\N{cigarette}'
            # per = '\N{"Sauropod"}'
            if const.DeviceStateRus[data_["state"]] == "Ожидание":
                perekur = "\U0001F6AC"
            else:
                perekur = ""

            if data_["fan_power"] > 0:
                veter = "\U0001F4A8"
            else:
                veter = ""
            # veter = "\U0001F4A8"

            txtstate = (const.DeviceStateRus[data_["state"]] + " {fl}").format(fl=('🔥' if data_["lighter"] else '') + perekur)

            heating_temp_trend = data_["heating_temp"] - predvalue["heating_temp"][0]
            heating_temp_trend = str(round(heating_temp_trend, 2)) + arrow_up if heating_temp_trend >= predvalue["heating_temp"][1] else str(
                round(heating_temp_trend, 2)) + arrow_down

            current_temp_trend = data_['current_temp'] - predvalue["current_temp"][0]
            current_temp_trend = str(round(current_temp_trend, 2)) + arrow_up if current_temp_trend >= predvalue["current_temp"][1] else str(
                round(current_temp_trend, 2)) + arrow_down

            return_temp_trend = data_["return_temp"] - predvalue["return_temp"][0]
            return_temp_trend = str(round(return_temp_trend, 2)) + arrow_up if return_temp_trend >= predvalue["return_temp"][1] else str(
                round(return_temp_trend, 2)) + arrow_down

            exhaust_temp_trend = data_["exhaust_temp"] - predvalue["exhaust_temp"][0]
            exhaust_temp_trend = str(round(exhaust_temp_trend, 2)) + arrow_up if exhaust_temp_trend >= predvalue["exhaust_temp"][1] else str(
                round(exhaust_temp_trend, 2)) + arrow_down

            t = time.localtime()
            _time = time.strftime("%H:%M:%S", t)
            # q.put( datetime.datetime.now())

            # Отследим тревогу
            # if data_["ecomax_control"] == "on" and data_["alarm"]:
            #     text_alerts = "*Оповещение:* " + AlertType(data_["pending_alerts"]).name.replace("_", " ") + " трев." + str(data_["alarm"]) + " " + str(
            #         qqq) + " конт." + str(data_["gcz_contact"]) + " зажиг." + str(data_["lighter"])
            # else:
            #     text_alerts = ""
            text_alerts = ""
            # to_pin_alarm = bot.send_message(id, text=text_alerts, parse_mode="Markdown").message_id

            textdata = "*Опрос системы:*" + _time + \
                       " (" + (datetime.datetime.strptime(_time, "%H:%M:%S") - datetime.datetime.strptime(predvalue["time"], "%H:%M:%S")).seconds.__str__() + "сек.)" + \
                       "\nРежим работы:  " + txtstate + \
                       "\nТемп.котла:    " + str(round(data_["heating_temp"], 2)) + " (" + str(data_["heating_target"]) + "); " + heating_temp_trend + \
                       "\nТемп.смесит.:  " + str(round(data_['current_temp'], 2)) + " (" + str(data_["target_temp"]) + "); " + current_temp_trend + \
                       "\nТемп.возвр.:   " + str(round(data_["return_temp"], 2)) + "; " + return_temp_trend + \
                       "\nТемп.прод.горен.: " + str(round(data_["exhaust_temp"], 2)) + "; " + exhaust_temp_trend + \
                       "\nТемп.подачи топл.: " + str(round(data_["feeder_temp"], 2)) + \
                       "\nТемп.ГВС:                    " + str(round(data_["water_heater_temp"], 2)) + \
                       "\nНасос:                          " + ("Вкл" if data_["heating_pump"] else "Выкл    ") + \
                       "\nМощ-ть вентил.:       " + str(round(data_["fan_power"], 2)) + " % " + veter + \
                       "\nМощ-ть котла:          " + str(data_["boiler_load"]) + " %" + \
                       "\nСостояние клапана:     " + str(data_["regdata"][182]) + " %" + \
                       "\nТемп.с наружи:           " + str(round(data_["outside_temp"], 2)) + \
                       "\n" + text_alerts

            predvalue = {"heating_temp": (round(data_["heating_temp"], 2), float(heating_temp_trend[:-1])),
                         "current_temp": (round(data_['current_temp'], 2), float(current_temp_trend[:-1])),
                         "return_temp": (round(data_["return_temp"], 2), float(return_temp_trend[:-1])),
                         "exhaust_temp": (round(data_["exhaust_temp"], 2), float(exhaust_temp_trend[:-1])),
                         "time": _time}
            try:
                bot.edit_message_text(chat_id=id, message_id=to_pin, text=textdata, reply_markup=markup, parse_mode="Markdown")
            except Exception as err:
                logger.error("Ошибка при обработке сообщения: Результат опроса. {err}".format(err=err.args[0]))
            time.sleep(15)

        logger.info("Завершение опроса.")
        try:
            bot.delete_message(chat_id=id, message_id=to_pin)
        except Exception as err:
            logger.error("Ошибка при обработке удаления : Результат опроса. {err}".format(err=err.args[0]))


dispatcher = Dispatcher()
survey = Survey()


def restart_program():
    try:
        for i in STREAM:
            # Terminate each process
            i.terminate()
            i.close()
        # os.system('python bible.py')

        # os.system('runas /user:Администратор D:/nssm-2.24/win64/nssm restart "bot_plum"')
        # os.system('D:/nssm-2.24/win64/nssm restart "bot_plum"')
    except Exception as err:
        logger.error("Ошибка перезапуска Бота. {err}".format(err=err.args[0]))


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    answer = "Выберите действие"
    select = call.data
    # message = call.data[1]
    if select == "Отмена":
        try:
            bot.answer_callback_query(callback_query_id=call.id, text='Отбой')
        except Exception as err:
            logger.error("Произошла ошибка при обработке сообщения: Отмена. {err}".format(err=err.args[0]))
        # answer = 'Выберите действие'

    elif select == "Остановить":
        # list(multiprocessing.process.active_children())[0].terminate()
        # dispatcher.terminate()
        # survey.terminate()
        # globals()["STREAM"][0].terminate()
        # globals()["STREAM"][0].close()
        # globals()["STREAM"] = []
        quefirst = False
        try:
            bot.answer_callback_query(callback_query_id=call.id, text='Остановка')
        except Exception as err:
            logger.error("Произошла ошибка при обработке сообщения: Остановить. {err}".format(err=err.args[0]))
        # answer = 'Выберите действие'

    elif select == "Перезапустить бот":
        logger.info("Перезагрузка бота")
        restart_program()
        try:
            # os.system('D:/nssm-2.24/win64/nssm restart "bot_plum"')
            bot.answer_callback_query(callback_query_id=call.id, text='Перезапуск')
        except Exception as err:
            logger.error("Ошибка при обработке сообщения: Перезапустить бот. {err}".format(err=err.args[0]))

        answer = 'Выберите действие'

    elif select == "Выключить компьютер":
        bot.answer_callback_query(callback_query_id=call.id, text='ShutDown')
        os.system("shutdown /s /t 1")
        # answer = 'Выберите действие'

    elif select == 'Вкл.регулятор':
        # await reader_plum.OnOff("Вкл")
        asyncio.run(reader_plum.OnOff("Вкл"))
        try:
            bot.answer_callback_query(callback_query_id=call.id, text="Вкл.регулятор")
        except Exception as err:
            logger.error("Ошибка при обработке сообщения: Вкл.регулятор. {err}".format(err=err.args[0]))
        answer = 'Включено'

    elif select == 'Откл.регулятор':
        # await reader_plum.OnOff("Выкл")
        asyncio.run(reader_plum.OnOff("Выкл"))
        try:
            bot.answer_callback_query(callback_query_id=call.id, text="Откл.регулятор")
        except Exception as err:
            logger.error("Ошибка при обработке сообщения: Откл.регулятор. {err}".format(err=err.args[0]))
        answer = "Выключено"

    #################################### contour
    elif select == 'Кривая нагрева контура':
        msg = bot.send_message(call.from_user.id, "Введите значение -: Кривая нагрева контура")
        bot.register_next_step_handler(msg, writer, id=('heating_curve', 'QDoubleSpinBox', 'mixer', msg,))

    elif select == 'Параллельный сдвиг контура':
        msg = bot.send_message(call.from_user.id, "Введите значение -Параллельный сдвиг контура:")
        bot.register_next_step_handler(msg, writer, id=('heating_curve_shift', 'QSpinBox', 'mixer', msg,))

        ################################ boiler
    elif select == 'Кривая нагрева':
        msg = bot.send_message(call.from_user.id, "Введите значение: Кривая нагрева")
        bot.register_next_step_handler(msg, writer, id=('heating_curve', 'QDoubleSpinBox', ' ', msg,))

    elif select == "Параллельный сдвиг":
        msg = bot.send_message(call.from_user.id, "Введите значение: Параллельный сдвиг")
        bot.register_next_step_handler(msg, writer, id=('heating_curve_shift', 'QSpinBox', '', msg,))

    elif select == "Инфа":
        get_channel_info(call)
    else:
        pass
    try:
        id_m = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=answer,
                                     reply_markup=None).message_id
        bot.delete_message(chat_id=call.message.chat.id, message_id=id_m)
    except Exception as err:
        logger.error("Ошибка редактирования сообщения. {err}".format(err=err.args[0]))


def writer(message, id):
    if message.text.replace(',', '').isdigit() or message.text.replace('.', '').isdigit():
        rez = asyncio.run(reader_plum.writer(message, id))
    else:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)

    bot.delete_message(chat_id=message.chat.id, message_id=id[3].id)

    ip_mes = bot.send_message(chat_id=message.chat.id, text="Ошибка ввода числового значения. ").message_id
    time.sleep(5)
    bot.delete_message(message.chat.id, ip_mes)


class User:
    def __init__(self, id):
        self.id = id
        self.code = None
        self.password = None


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
        bot.send_message(message.chat.id, "Небось угадал.")
        isauthorized[str(message.chat.id)]["active"] = True
        bot.delete_message(message.chat.id, message.id)
        mainmenu(message)
    else:
        schet = schet + 1
        if schet <= 2:
            inputpass(message, schet)
        else:
            bot.send_message(message.chat.id, "Вы какой то подозрительный.")
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)


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
        logger.error("Ошибка {err}".format(err=err.args[0]))
        pass


@bot.message_handler(commands=['get_channel_info'])
def get_channel_info(message):
    channel_info = bot.get_chat(chat_id='-1001900996966')
    channel_info_ = bot.get_chat(chat_id='-1001948581163')  # Замените на имя вашего канала или его идентификатор

    bot.send_message(message.from_user.id, f"Название канала: {channel_info.title}\n"
                                           f"Описание канала: {channel_info.description}\n"
                                           f"Тип чата: {channel_info.type}")


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
        bot.send_message(message.chat.id, "Вы авторизованны.")
        mainmenu(message)
        return
    else:
        schet = 0
        inputpass(message, schet)


########################################################################### Регистрация
@bot.message_handler(commands=['reg'])  # команда
def registration(message):
    bot.reply_to(message, "{who}\nНеобходима регистрация.".format(who=message.from_user.first_name))
    try:
        chat_id = message.from_user.id
        name = message.text
        user = User(message.from_user.id)
        # user_dict[chat_id] = user
        bot.send_message(message.chat.id, 'Начнём регистацию.')
        msg = bot.send_message(message.chat.id, 'Введите ключ проекта')
        bot.register_next_step_handler(msg, process_code_step, user)
    except Exception as e:
        bot.reply_to(message, 'Опаньки(oooops)')


def process_code_step(message, user):
    try:
        chat_id = message.from_user.id
        user.code = message.text
        if user.code != '369':
            bot.send_message(message.chat.id, "Неправильный ключ. Обратитесь к Буратино.")
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
    except Exception as e:
        bot.reply_to(message, 'Опаньки(oooops')


########################################################################### Регистрация
def checkregistrationаvtorization(message):
    try:
        if message == None:
            query = "SELECT *  FROM users "
            param = {}
        else:
            # query = """SELECT userid, first_name, last_name, username  FROM users WHERE userid = :userid and first_name =:first_name and last_name = :last_name and username = :username"""
            query = "SELECT userid, first_name, last_name, username, pass, datareg  FROM users WHERE userid = :userid and first_name =:first_name"
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

    id_mess = bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup).message_id


def setpoints(message):
    id = message.chat.id

    to_pin = bot.send_message(id, 'Читаю данные...').message_id
    listparam = [["ecomax_control", "state"]]
    data_ = asyncio.run(reader_plum.getparameter(listparam))

    checklist = bible.checkingdict(listparam, data_)
    if checklist.__len__() != 0:
        logger.error("Ошибка чтения данных котла. {err}".format(err=checklist))
        bot.delete_message(id, to_pin)
        ip_mes = bot.send_message(id, "Ошибка получения данных котла. Повторите.").message_id
        time.sleep(5)
        bot.delete_message(id, ip_mes)
        return

    text = "*Управление регулятором:*" + \
           "\nСостояние: {a} {b}".format(a="Вкл." if data_["ecomax_control"].value == "on" else "Выкл.", b=";  " + const.DeviceStateRus[data_["state"]])
    markup = types.InlineKeyboardMarkup()
    try:
        markup.add(types.InlineKeyboardButton(text='Вкл.регулятор', callback_data="Вкл.регулятор"))
        markup.add(types.InlineKeyboardButton(text='Откл.регулятор', callback_data="Откл.регулятор"))
        markup.add(types.InlineKeyboardButton(text='Отмена', callback_data="Отмена"))
        bot.edit_message_text(chat_id=id, message_id=to_pin, text=text, reply_markup=markup, parse_mode="Markdown")
    except Exception as err:
        logger.error("Ошибка получения данных котла. {err}".format(err=err))
        bot.delete_message(id, to_pin)
        ip_mes = bot.send_message(id, "Ошибка получения данных котла. Повторите.").message_id
        time.sleep(5)
        bot.delete_message(id, ip_mes)


def controlpanel(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    btn1 = types.KeyboardButton("Котел")
    btn2 = types.KeyboardButton("Контуры")
    btn3 = types.KeyboardButton("ВКЛ/ВЫКЛ")
    btn4 = types.KeyboardButton('Главное меню')
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, "Выберите действие", reply_markup=markup)


def boiler(message):
    id = message.chat.id

    to_pin = bot.send_message(id, 'Читаю данные...').message_id
    listparam = [["state", "weather_control", "heating_curve", "heating_curve_shift", "heating_temp", "heating_target", "fuel_level"]]
    data_ = asyncio.run(reader_plum.getparameter(listparam))
    checklist = bible.checkingdict(listparam, data_)
    if checklist.__len__() != 0:
        logger.error("Ошибка чтения данных котла. {err}".format(err=checklist))
        bot.delete_message(id, to_pin)
        ip_mes = bot.send_message(id, "Ошибка получения данных котла. Повторите.").message_id
        time.sleep(5)
        bot.delete_message(id, ip_mes)
        return

    markup = types.InlineKeyboardMarkup()
    try:
        markup.add(types.InlineKeyboardButton(text='Погодное управление: ' +
                                                   "Вкл" if str(data_['weather_control'].value) == "on" else "Выкл" + str(data_['weather_control'].value),
                                              callback_data="Погодное управление"))
        markup.add(types.InlineKeyboardButton(text='Кривая нагрева: ' + str(round(data_['heating_curve'].value, 2)),
                                              callback_data="Кривая нагрева"))
        markup.add(types.InlineKeyboardButton(text='Параллельный сдвиг: ' + str(data_['heating_curve_shift'].value),
                                              callback_data="Параллельный сдвиг"))
        markup.add(types.InlineKeyboardButton(text='Вкл.регулятор', callback_data="Вкл.регулятор"))
        markup.add(types.InlineKeyboardButton(text='Откл.регулятор', callback_data="Откл.регулятор"))
        markup.add(types.InlineKeyboardButton(text='Отмена', callback_data="Отмена"))
        text = "*Управление котлом:*" + \
               "\n"+const.DeviceStateRus[data_["state"]] + \
               "\nТемп. котла:             " + str(round(data_["heating_temp"], 2)) + ";  Уст: " + str(data_["heating_target"]) + \
               "\nУровень топлива: " + str(data_["fuel_level"]) + "%"

        bot.edit_message_text(chat_id=id, message_id=to_pin, text=text, reply_markup=markup, parse_mode="Markdown")
    except Exception as err:
        logger.error("Ошибка получения данных котла. {err}".format(err=err))
        bot.delete_message(id, to_pin)
        ip_mes = bot.send_message(id, "Ошибка получения данных котла. Повторите.").message_id
        time.sleep(5)
        bot.delete_message(id, ip_mes)


def contour(message):
    id = message.chat.id
    to_pin = bot.send_message(id, 'Читаю данные...').message_id

    # data_ = asyncio.run(reader_plum.run())
    listparam = [['return_temp'], ['weather_control', 'heating_curve', 'heating_curve_shift', 'current_temp', 'target_temp']]
    data_ = asyncio.run(reader_plum.getparameter(listparam))
    checklist = bible.checkingdict(listparam, data_)
    if checklist.__len__() != 0:
        logger.error("Ошибка чтения данных котла. {err}".format(err=checklist))
        bot.delete_message(id, to_pin)
        ip_mes = bot.send_message(id, "Ошибка получения данных котла. Повторите.").message_id
        time.sleep(5)
        bot.delete_message(id, ip_mes)
        return

    markup = types.InlineKeyboardMarkup()
    try:
        markup.add(types.InlineKeyboardButton(
            text='Погодное управление: ' + "Вкл" if str(data_['weather_control'].value) == "on" else "Выкл" + str(
                data_['weather_control'].value), callback_data="Погодное управление"))
        markup.add(types.InlineKeyboardButton(text='Кривая нагрева контура: ' + str(round(data_['heating_curve'].value, 2)),
                                              callback_data="Кривая нагрева контура"))
        markup.add(types.InlineKeyboardButton(text='Параллельный сдвиг контура: ' + str(data_['heating_curve_shift'].value),
                                              callback_data="Параллельный сдвиг контура"))
        # markup.add(types.InlineKeyboardButton(text='Погодное управление: ', callback_data="Погодное управление"))
        # markup.add(types.InlineKeyboardButton(text='Кривая нагрева: ', callback_data="Кривая нагрева"))
        markup.add(types.InlineKeyboardButton(text='Отмена', callback_data="Отмена"))
        # bot.send_message(id, text="Управление", reply_markup=markup)
        bot.edit_message_text(chat_id=id, message_id=to_pin, text='*Управление отоплением:*' +
                                                                  "\nТемп. смесителя:     " + str(round(data_['current_temp'], 2)) + "; Уст: " + str(
            data_['target_temp']) +
                                                                  "\nТемп. возврата:      " + str(round(data_['return_temp'], 2))
                              , reply_markup=markup, parse_mode="Markdown")
    except Exception as err:
        logger.error("Ошибка получения данных котла. {err}".format(err=err))
        bot.delete_message(id, to_pin)
        ip_mes = bot.send_message(id, "Ошибка получения данных контура. Повторите.").message_id
        time.sleep(5)
        bot.delete_message(id, ip_mes)


def Bot(message):
    id = message.chat.id

    to_pin = bot.send_message(id, 'Читаю данные...').message_id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Сбросить опрос', callback_data="Остановить"))
    markup.add(types.InlineKeyboardButton(text='Перезапустить бот', callback_data='Перезапустить бот'))
    markup.add(types.InlineKeyboardButton(text='Выключить компьютер', callback_data='Выключить компьютер'))
    markup.add(types.InlineKeyboardButton(text='Инфа с канала', callback_data='Инфа'))
    markup.add(types.InlineKeyboardButton(text='Отмена', callback_data="Отмена"))
    text = "*Управление ботом:*"

    bot.edit_message_text(chat_id=id, message_id=to_pin, text=text, reply_markup=markup, parse_mode="Markdown")


# CHANNEL_NAME = '-1001909359532'
# # @bot.message_handler(content_types=['photo', 'text'])
# @bot.channel_post_handler(content_types=['text'])
# def repost_msg(message):
#
#     bot.copy_message(CHANNEL_NAME, message.chat.id, message.message_id)
#

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    if isauthorized.get(str(message.from_user.id)) == None or isauthorized.__len__() == 0:
        dt = datetime.datetime.now()
        db.add_record_passing([message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                               message.from_user.username, dt])
        registration(message)
    elif isauthorized[str(message.from_user.id)]["active"] is False:
        pass
    else:
        pass

    if message.text == 'Главное меню':
        mainmenu(message)
        delete = bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    elif message.text == 'Опрос состояния':
        dispatcher._running = True
        delete = bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        id = message.chat.id

        quefirst = True
        t1 = multiprocessing.Process(target=dispatcher.run, args=(id, quefirst))
        t1.start()
        globals()["STREAM"].append(t1)
        logger.info("Запущен процесс {name}".format(name=t1.name))

    elif message.text == 'Отключить опрос':
        delete = bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    elif message.text == "Управление":
        controlpanel(message)
        delete = bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    elif message.text == "Главное меню":
        mainmenu(message)
        delete = bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    elif message.text == "Вкл/Выкл":
        setpoints(message)
        delete = bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    elif message.text == "Котел":
        boiler(message)
        delete = bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    elif message.text == "Контуры":
        contour(message)
        delete = bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    elif message.text == "Bot":
        Bot(message)
        delete = bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    else:
        # pass
        gpt.ask_gpt(message.text)
        bot.send_message(chat_id=message.chat.id, text=gpt.ask_gpt(message.text))


def startbot():
    logger.info("Начало работы.")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)


if __name__ == '__main__':
    startbot()
    #
    # bot = telebot.TeleBot(set.TOKEN)

    # logger.info("Начало работы.")
    # multiprocessing.set_start_method('fork')

    # t = multiprocessing.Process(target=startbot)
    # t.start()
