# -*- coding: utf-8 -*-

import asyncio
import datetime

from typing import Final
import json
from pyplumio import open_serial_connection

from pyplumio.devices import Device
from pyplumio.helpers.event_manager import EventManager
# from pyplumio.helpers.typing import EventDataType
from pyplumio.devices import mixer
from pyplumio.helpers import parameter
import const
import set
import app_logger

logger = app_logger.get_logger(__name__)

FILENAME: Final = "ecomax_data.json"
REDACTED: Final = "**REDACTED**"
TIMEOUT = set.TIMEOUT
DEVICE = set.DEVICE
BAUDRATE = set.BAUDRATE


# class DevState(DeviceState):
#
#     STABILIZATION = 12
#     CHECKING_FLAME = 14

def _is_json_serializable(data) -> bool:
    """Check if data is json serializable."""
    try:
        json.dumps(data)
        return True
    except TypeError:
        return False


def redact_device_data(data):
    """Redact sensitive imformation from device data."""
    if "product" in data:
        data["product"].uid = REDACTED

    if "password" in data:
        data["password"] = REDACTED

    return data


class DeviceDataEncoder(json.JSONEncoder):
    """Represents custom device data encoder."""

    def default(self, o):
        """Encode device data to json."""
        if isinstance(o, dict):
            o = {x: self.default(y) for x, y in o.items()}

        if isinstance(o, list):
            o = [self.default(x) for x in o]

        if isinstance(o, EventManager):
            o = self.default(o.data)

        if _is_json_serializable(o):
            return o

        return {"__type": str(type(o)), "repr": repr(o)}


async def read_regdata(self):
    # FILENAME =
    connection_handler = open_serial_connection(device=DEVICE, baudrate=BAUDRATE)
    async with connection_handler as connection:
        ecomax: Device = await connection.get("ecomax")

        await ecomax.get("product", timeout=TIMEOUT)
        # await ecomax.wait_for("loaded", timeout=TIMEOUT)
        # await ecomax.get("loaded", timeout=TIMEOUT)
        try:
            with open(FILENAME, "w", encoding="UTF-8") as file:
                data = redact_device_data(dict(ecomax.data))
                rez = set(const.CONTROLLED_PARAMETERS).issubset(list(ecomax.data))
                file.write(json.dumps(data, cls=DeviceDataEncoder, indent=5))
        except Exception as err:
            logger.error("Ошибка записи файла {filejson}. {err}".format(err=err.args[0], filejson=FILENAME))

        self.data = ecomax.data
    await connection_handler.close()


async def OnOff(vklvykl):
    connection = open_serial_connection(device=DEVICE, baudrate=BAUDRATE)

    async with connection as conn:
        try:
            print("Получим ecomax")

            ecomax: Device = await conn.get("ecomax")

            ecomax_control = await ecomax.get("ecomax_control")
            if vklvykl == "Вкл" and ecomax_control.value == "off":
                result = await ecomax_control.turn_on()
                # pass
            elif vklvykl == "Выкл" and ecomax_control.value == "on":
                result = await ecomax_control.turn_off()
                # pass
        except Exception as err:
            pass
    # Close the connection.
    await connection.close()


async def writer(message, id):
    # парам = self.sender().sender().objectName()
    connection_handler = open_serial_connection(device=DEVICE, baudrate=BAUDRATE)
    async with connection_handler as connection:
        ecomax: Device = await connection.get("ecomax")
        # Пишем в Миксер
        if id[2] == 'mixer':
            mixers = await ecomax.get("mixers", TIMEOUT)
            Mixer: mixer = mixers[0]
            # items_for_change = await Mixer.get(id[0])
            if id[1] == 'QSpinBox':
                items_for_change = await Mixer.get(id[0], TIMEOUT)
                if id[0] == 'heating_curve_shift':
                    await Mixer.set(id[0], int(message.text))
                else:
                    await Mixer.set(id[0], int(message.text))
            elif id[1] == 'QDoubleSpinBox':
                items_for_change = await Mixer.get(id[0], TIMEOUT)
                await Mixer.set(id[0], float(message.text.replace(',', '.')))
            elif id[1] == 'QComboBox':
                # items_for_change = await ecomax.get(id[0])
                pass
        else:
            if id[1] == 'QSpinBox':
                items_for_change = await ecomax.get(id[0], TIMEOUT)
                await ecomax.set(id[0], int(message.text))
            elif id[1] == 'QDoubleSpinBox':
                items_for_change = await ecomax.get(id[0])
                await ecomax.set(id[0], float(message.text.replace(',', '.')))
            elif id[1] == 'QComboBox':
                pass
    await connection_handler.close()


async def reset_connect():
    connection_handler = open_serial_connection(device=DEVICE, baudrate=BAUDRATE)
    await connection_handler.close()


async def getparameter(param) -> dict:
    connection = open_serial_connection(device=DEVICE, baudrate=BAUDRATE)
    try:
        await connection.connect()
    except asyncio.TimeoutError as err:
        logger.error("Ошибка подключения к устройству. {err}".format(err=err))
        await connection.close()
    try:
        ecomax: Device = await connection.get("ecomax", timeout=TIMEOUT)
        responselist = {}
        if param.__len__() > 0 and param[0].__len__() > 0:
            # ecomax: Device = await connection.get("ecomax")
            for id in param[0]:
                responselist[id] = await ecomax.get(id, timeout=TIMEOUT)

        if param.__len__() > 1 and param[1].__len__() > 0:
            # Get connected mixers.
            mixers = await ecomax.get("mixers")
            # Get single mixer.
            mix: mixer = mixers[0]
            for id in param[1]:
                responselist[id] = await mix.get(id, timeout=TIMEOUT)
    except Exception as err:
        logger.error("Ошибка получения ecomax. {err}".format(err=err))

    await connection.close()
    return responselist


async def run():
    """Opens the connection and gets the ecoMAX device."""
    # bible.getService("bot_plum")
    connection = open_serial_connection(device=DEVICE, baudrate=BAUDRATE)
    # logger.info("До подключения. ")
    # Connect to the device.
    try:
        # t = time.strftime("%H:%M:%S", time.localtime())
        # logger.info("До подключения. "+t)
        await connection.connect()
        # t = time.strftime("%H:%M:%S", time.localtime())
        # logger.info("После подключения. {t}".format(t=t))
    except asyncio.TimeoutError as err:
        logger.error("Ошибка подключения к устройству. {err}".format(err=err))
        await connection.close()

    try:
        # Get the ecoMAX device within 10 seconds or
        # timeout.

        ecomax: Device = await connection.get("ecomax")

        # t = time.strftime("%H:%M:%S", time.localtime())
        # logger.info("               Получение данных modules начало. {t}".format(t=t))

        try:
            # await ecomax.get("ecomax", timeout=TIMEOUT)
            #
            # await ecomax.wait_for("modules", timeout=TIMEOUT)
            # await ecomax.get("modules", timeout=TIMEOUT)
            await ecomax.wait_for("regdata", timeout=TIMEOUT)
        except Exception as err:
            logger.error("Ошибка получение данных regdata. {err}".format(err=err))

    except asyncio.TimeoutError:
        # Log the error, if device times out.
        logger.error("Failed to get the device within {time} seconds".format(time=TIMEOUT))
    # Close the connection.
    await connection.close()
    ecomax.data["dt"] = datetime.datetime.now()
    return ecomax.data

# if __name__ == "__main__":
#     # sys.exit(run(main()))
#     sys.exit(asyncio.run(main()))
