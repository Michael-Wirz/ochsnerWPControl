#!/usr/bin/python3
import asyncio
from pymystrom.switch import MyStromSwitch
import datetime
import logging


logging.basicConfig(filename="/tmp/heating.log", level=logging.INFO, format="%(asctime)s %(message)s")



ip_floorheating = '192.168.1.57'
ip_mainheating = '192.168.1.52'


async def main():
    async with MyStromSwitch(ip_mainheating) as switch_heating:
        await switch_heating.get_state()
        async with MyStromSwitch(ip_floorheating) as switch_floor:
            await switch_floor.get_state()

            if switch_heating.consumption >= 10 and switch_floor.relay == False:
                msg="Heating on, but floorheating off"
                task="Will switch floorheating on"
                logging.info(msg)
                logging.info(task)
                if not switch_floor.relay:
                    await switch_floor.turn_on()
            elif switch_heating.consumption <= 10 and switch_floor.relay == True:
                msg="Heating off, but floorheating on"
                task="Will switch floorheating off"
                logging.info(msg)
                logging.info(task)
                if switch_floor.relay:
                    await switch_floor.turn_off()
            elif switch_heating.consumption >= 10 and switch_floor.relay == True:
                msg="Heating on and floorheating on"
                task="Everything is fine!"
                logging.info(msg)
                logging.info(task)
            elif switch_heating.consumption <= 10 and switch_floor.relay == False:
                msg="Heating off and floorheating off"
                task="Everything is fine!"
                logging.info(msg)
                logging.info(task)


if __name__ == "__main__":
    print(str(datetime.datetime.now()) + ' Checking heating:')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())