# import psutil
import app_logger
import os
# import win32serviceutil
from pyqadmin import admin

logger = app_logger.get_logger(__name__)

# def getService(name):
#
#     service = None
#     try:
#         service = psutil.win_service_get(name)
#         service = service.as_dict()
#     except Exception as ex:
#         logger.error("Ошибка определения службы {ex}".format(ex=ex))
#         print(str(ex))
#
#     if not service:
#         logger.error("Службы не существует.")

@admin
def restart_program():
    # proc = psutil.Process(os.getpid())
    # pass
    # python = sys.executable
    try:
        # os.execv(sys.executable, [python] + sys.argv)
        # logger.info("пошёл на рестарт")
        os.system('D:/nssm-2.24/win64/nssm restart "bot_plum"')

        # os.system('D:/nssm-2.24/win64/nssm stop "bot_plum"')
        # os.system('D:/nssm-2.24/win64/nssm start "bot_plum"')

        # status = win32serviceutil.QueryServiceStatus("bot_plum")
        # win32serviceutil.StartService(serviceName="bot_plum", machine=None)
    except Exception as err:
        logger.error("Ошибка перезапуска Бота. {err}".format(err=err.args[0]))

def checkingdict(checklist, controldict):
    if checklist.__len__() == 0:
        return []

    if checklist.__len__() == 1:
        param = list(checklist[0] - controldict.keys())
    else:
        param = []

    if checklist.__len__() > 1:
        mix = list(checklist[1] - controldict.keys())
    else:
        mix = []

    # if 189 in controldict["regdata"]:


    return param + mix

if __name__ == '__main__':
    # ind = 0
    print('🔥')
    # for ind in range(0,1500):
    #     print(ind, chr(ind))
    # list1 = [['a', 'b', 'c'], ['d', 'f', 'i']]
    # dict1 = {'a': 1, 'b': 2, 'c': 3,}
    # dict2 = {'d': 3, 'f': 3}
    # dict4 = {'a': 1, 'b': 2, 'c': 3, 'mixers': {"0": {'d': 3, 'f': 3}}}
    # otvet = checkingdict(list1, dict4)
    # diffkey = dict1.keys() - dict4.keys()
    # diffkey1 = list1[0] - dict4.keys()
    # diffkey2 = list1[1] - dict4["mixers"]["0"].keys()
    # # for key in list1:
    # #     dict4
    # print(diffkey)
    # print(set(dict1.keys()) in set(dict4.keys()))
    # print(dict1 == dict4)
    # restart_program()