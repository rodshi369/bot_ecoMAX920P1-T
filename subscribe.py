import asyncio

import pyplumio

SUBSCRIBE = ["state", "heating_temp", "feeder_temp", "water_heater_temp", "outside_temp", "return_temp", "exhaust_temp",
             "heating_target", "fan_power", "current_temp", "target_temp"]

async def my_callback(value) -> None:
    """Prints current heating temperature."""
    if globals()['a'] > 10:
        globals()['a'] = 0
    print(SUBSCRIBE[globals()['a']], value)
    globals()['a']=globals()['a']+1

async def subcribe_sensors():
    global a
    a = 0
    """Subscribes callback to the current heating temperature."""
    connection_handler = pyplumio.open_serial_connection(device="com3", baudrate=115200)
    async with connection_handler as conn:
    # async with pyplumio.open_tcp_connection("localhost", 8899) as conn:
        ecomax = await conn.get("ecomax")
        ecomax.subscribe("state", my_callback)
        ecomax.subscribe("heating_temp", my_callback)
        ecomax.subscribe("feeder_temp", my_callback)
        ecomax.subscribe("water_heater_temp", my_callback)
        ecomax.subscribe("outside_temp", my_callback)
        ecomax.subscribe("return_temp", my_callback)
        ecomax.subscribe("exhaust_temp", my_callback)
        ecomax.subscribe("heating_target", my_callback)
        ecomax.subscribe("fan_power", my_callback)
        ecomax.subscribe("fan_power", my_callback)
        mixers = await ecomax.get("mixers")
        Mixer: pyplumio.devices.mixer = mixers[0]
        Mixer.subscribe("current_temp", my_callback)
        Mixer.subscribe("target_temp", my_callback)
        # Wait until disconnected (forever)
        await conn.wait_until_done()


# asyncio.run(subcribe_sensors())