import pymystrom

plug_mainheating = "192.168.1.52"
plug_floorheating = "192.168.1.57"


def decide_what_2_do():
    print(pymystrom.MyStromPlug(plug_mainheating))

if __name__ == '__main__':
    print(str(datetime.datetime.now()) + ' Checking:')
   #logging.info(str(datetime.datetime.now()))
    print("Working state: " +str(decide_what_2_do()))
