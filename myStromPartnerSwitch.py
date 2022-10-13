"""Example code for communicating with a myStrom plug/switch."""
import asyncio

from pymystrom.switch import MyStromSwitch


ip_floorheating = '192.168.1.57'
ip_mainheating = '192.168.1.52'


async def main():
    async with MyStromSwitch(ip_mainheating) as switch_heating:
        await switch_heating.get_state()
        async with MyStromSwitch(ip_floorheating) as switch_floor:
            await switch_floor.get_state()

            if switch_heating.consumption >= 10 and switch_floor.relay == False:
                print("Heating on, but floorheating off")
                print("Will switch floorheating on")
                if not switch_floor.relay:
                    await switch_floor.turn_on()
            elif switch_heating.consumption <= 10 and switch_floor.relay == True:
                print("Heating off, but floorheating on")
                print("Will switch floorheating off")
                if not switch_floor.relay:
                    await switch_floor.turn_off()
            elif switch_heating.consumption >= 10 and switch_floor.relay == True:
                print("Heating on and floorheating on")
                print("Everything is fine!")
            elif switch_heating.consumption <= 10 and switch_floor.relay == False:
                print("Heating off and floorheating off")
                print("Everything is fine!")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())