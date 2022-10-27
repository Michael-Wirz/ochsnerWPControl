#!/usr/bin/python3
# This is a sample Python script.
# import urllib.request as requests
import requests
import datetime
import logging
# import helper
import ShellyPy

# config = helper.read_config()

logging.basicConfig(filename="/tmp/wp.log", level=logging.INFO, format="%(asctime)s %(message)s")

# influx_url1 = config['INFLUX']['influx_url1']
# influx_url2 = config['INFLUX']['influx_url2']
# start_condition_wp = config['WP_START_CONDITION']['start_condition_wp']
# start_condition_pv = config['WP_START_CONDITION']['start_condition_pv']
# start_condition_room = config['WP_START_CONDITION']['start_condition_room']

# influx_url1 = str(influx_url1)
# min_water_temp = config['WATER_CONFIG']['min_water_temp']
# desired_water_temp = config['WATER_CONFIG']['desired_water_temp']
# legionella_water_temp = config['WATER_CONFIG']['legionella_water_temp']
influx_url1 = "http://192.168.1.43:8086/query?db="
influx_url2 = "http://192.168.1.153:8086/query?db="

start_condition_wp = 3
start_condition_pv = 2
start_condition_room = 1
shelly_boiler = ShellyPy.Shelly("192.168.1.39")
# min seconds
min_runtime = 7200
# min runtime if it starts close to desired_water_temp and reaches it quick
min_runtime_with_temp_ok = 3600

# Minimal Temperature
min_water_temp = 41
# Water temp if last legionella run is < 9 dayys
desired_water_temp = 47
# Water temp fo legionella run
legionella_water_temp = 63
night_tarif_start = '21:00:00'
night_tarif_end = '07:00:00'


def cre_request_date_minutes(avg_minutes):
    request_date = datetime.datetime.now() - datetime.timedelta(hours=2, minutes=avg_minutes)
    return request_date


# function#
# def cre_request_date_days(avg_days):
#    request_date = datetime.datetime.now() - datetime.timedelta(days=avg_days)
#    return request_date

# get average peak pv power for the last 20 minutes
# taking the average over a bigger time (20m), better resulte when weather is changing quickly
def get_pv_last_peak():
    avg_minutes = 20
    influx_db = "solaranzeige"
    influx_query = {
        'q': "select mean(Ueberschuss) from AC where time > '" + str(cre_request_date_minutes(avg_minutes)) + "'"}
    r = requests.get(url=influx_url2 + influx_db, params=influx_query).json()
    pv_last = r['results'][0]['series'][0]['values'][0][1]
    influx_query = {'q': "select mean(Lade_Entladeleistung) from Batterie where time > '" + str(
        cre_request_date_minutes(avg_minutes)) + "'"}
    r = requests.get(url=influx_url2 + influx_db, params=influx_query).json()
    battery_charge = r['results'][0]['series'][0]['values'][0][1]
    if battery_charge <= 0:
        pv_last_peak = pv_last + (-battery_charge)
    else:
        pv_last_peak = pv_last
    return pv_last_peak


# get the average room temperature for the last 5 minutes
# averaging the temp to get rid of temp jumps
def get_room_last_temp():
    avg_minutes = 5
    influx_db = "test1"
    boiler_device = "192.168.1.56"
    influx_query = {'q': "select mean(temp) from mystrom2 where device='" + boiler_device + "' and time > '" + str(
        cre_request_date_minutes(avg_minutes)) + "'"}
    r = requests.get(url=influx_url1 + influx_db, params=influx_query).json()
    room_last_temp = r['results'][0]['series'][0]['values'][0][1]
    return room_last_temp


def get_battery_soc():
    avg_minutes = 5
    influx_db = "solaranzeige"
    influx_query = {
        'q': "select mean(Bat_Act_SOC) from Batterie where time > '" + str(cre_request_date_minutes(avg_minutes)) + "'"}
    r = requests.get(url=influx_url1 + influx_db, params=influx_query).json()
    battery_soc = r['results'][0]['series'][0]['values'][0][1]
    print("SOC" + str(battery_soc))
    return battery_soc


# get the temperature of the boiler
def get_wp_last_temp():
    avg_minutes = 2
    influx_db = "test1"
    influx_query = {
        'q': "select mean(temp) from boiler where time > '" + str(cre_request_date_minutes(avg_minutes)) + "'"}
    r = requests.get(url=influx_url1 + influx_db, params=influx_query).json()
    wp_last_temp = r['results'][0]['series'][0]['values'][0][1]
    return wp_last_temp


# Check for the last time the temperature was more than 60°
# Only the last 10 days are checked
# When no result, date is set to 01.01.1999' to force a legionella run
def get_last_legionella_date():
    influx_db = "test1"
    influx_query = {'q': "select max(temp) from boiler where temp > 60"}
    r = requests.get(url=influx_url1 + influx_db, params=influx_query).json()
    if len(str(r)) <= 40:
        date_last_legionella = "1999-01-01 01:01:01T0000"
    else:
        date_last_legionella = r['results'][0]['series'][0]['values'][0][0]
    return date_last_legionella


def get_last_start_date():
    avg_minutes = 900
    influx_db = "test1"
    influx_query = {
        'q': "select temp from boiler where temp > desired_water_temp and time > '" + str(cre_request_date_minutes(avg_minutes)) + "'"}
    r = requests.get(url=influx_url1 + influx_db, params=influx_query).json()
    print(r)
    if len(str(r)) <= 40:
        date_last_start = "1999-01-01 01:01:01T0000"
    else:
        date_last_start = r['results'][0]['series'][0]['values'][0][0]
    days_since_last_start = datetime.datetime.strptime(str(datetime.datetime.now()).split(" ", 1)[0],
                                                       '%Y-%m-%d') - datetime.datetime.strptime(
        str(date_last_start.split(" ", 1)[0]).replace("T", " ").split(" ", 1)[0], '%Y-%m-%d')
    return days_since_last_start


def get_wp_state():
    avg_minutes = 1
    influx_db = "test1"
    boiler_device = "192.168.1.56"
    influx_query = {'q': "select last(power) from mystrom2 where device='" + boiler_device + "' and time > '" + str(
        cre_request_date_minutes(avg_minutes)) + "'"}
    r = requests.get(url=influx_url1 + influx_db, params=influx_query).json()
    if r['results'][0]['series'][0]['values'][0][1] > 100:
        wp_state = True
    elif r['results'][0]['series'][0]['values'][0][1] < 100:
        wp_state = False
    avg_minutes = 360
    if wp_state is True:
        influx_query = {
            'q': "select last(power) from mystrom2 where device='" + boiler_device + "' and power < 100 and time > '" + str(
                cre_request_date_minutes(avg_minutes)) + "'"}
        r = requests.get(url=influx_url1 + influx_db, params=influx_query).json()
        # adding two hours at the end because of influx and sysdate time difference
        # print(r)
        last_start_time = datetime.datetime.strptime(
            str(r['results'][0]['series'][0]['values'][0][0].split(" ", 1)[0]).split(".", 1)[0].replace("T", " "),
            '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=2)
        time_since_start = datetime.datetime.strptime(str(datetime.datetime.now()).split(".", 1)[0],
                                                      '%Y-%m-%d %H:%M:%S') - last_start_time

        # Do not stop WP when running less than 1h (default) (min_runtime seconds) to prevent stopping and starting to often
        act_wp_temp = get_wp_last_temp()
        if time_since_start.seconds < min_runtime and act_wp_temp < desired_water_temp:
            wp_stoppable = False
            logging.info("Not stoppable bc cause 1, act_wp_temp = " + str(act_wp_temp))
        # Stop if running for more than 1h and temp is greate desired_water_temp + 1 degree
        elif act_wp_temp >= desired_water_temp:
            wp_stoppable = True
            logging.info("Stoppable bc cause 2")
        else:
            wp_stoppable = True
            logging.info("Stoppable bc cause 3")
        logging.info("Runtime in seconds: " + str(time_since_start.seconds))
        logging.info("wp_stoppable: " + str(wp_stoppable))
    else:
        wp_stoppable = True
        logging.info("Stoppable bc cause 4")
    return wp_state, wp_stoppable


def stop_heating():
    print("stop_heating function activated: ")
    if get_wp_state()[1] is True and get_wp_state()[0] is True:
        print("Turn WP OFF")
        logging.info("Turn WP OFF")
        shelly_boiler.relay(0, turn=False)
    elif get_wp_state()[1] is True and get_wp_state()[0] is False:
        print("Nothing to do, WP already OFF")
        logging.info("Nothing to do, WP already OFF")
    else:
        print("Can not stop WP: Is running for less then 2h")
        logging.info("Can not stop WP: Is running for less then 2h")


def start_heating():
    days_since_last_legionella = datetime.datetime.strptime(str(datetime.datetime.now()).split(" ", 1)[0],
                                                            '%Y-%m-%d') - datetime.datetime.strptime(
        str(get_last_legionella_date().split(" ", 1)[0]).replace("T", " ").split(" ", 1)[0], '%Y-%m-%d')
    if days_since_last_legionella.days > 9:
        print("Actual Temp: " + str(get_wp_last_temp()))
        print("Temp Goal: " + str(legionella_water_temp))
        logging.info("Actual Temp: " + str(get_wp_last_temp()))
        logging.info("Temp Goal: " + str(legionella_water_temp))
        shelly_boiler.relay(0, turn=True)
    else:
        print("Actual Temp: " + str(get_wp_last_temp()))
        print("Temp Goal: " + str(desired_water_temp))
        logging.info("Actual Temp: " + str(get_wp_last_temp()))
        logging.info("Temp Goal: " + str(desired_water_temp))
        shelly_boiler.relay(0, turn=True)


def decide_what_2_do():
    days_since_last_legionella = datetime.datetime.strptime(str(datetime.datetime.now()).split(" ", 1)[0],
                                                            '%Y-%m-%d') - datetime.datetime.strptime(
        str(get_last_legionella_date().split(" ", 1)[0]).replace("T", " ").split(" ", 1)[0], '%Y-%m-%d')
    pv_last_peak_value = get_pv_last_peak()
    get_wp_state()
    if get_wp_state()[0] is True:
        pv_last_peak_value = pv_last_peak_value + 600

    if pv_last_peak_value <= 600:
        state_pv = 1
    elif 600 < pv_last_peak_value < 1000:
        state_pv = 2
    elif pv_last_peak_value > 1000:
        state_pv = 3
    room_last_peak_value = get_room_last_temp()
    if room_last_peak_value <= 19:
        state_room = 1
    elif 19 < room_last_peak_value < 23:
        state_room = 2
    elif room_last_peak_value > 23:
        state_room = 3
    wp_last_temp_value = get_wp_last_temp()
    if wp_last_temp_value <= 43:
        state_wp = 1
    elif 43.1 < wp_last_temp_value <= 45.1:
        state_wp = 2
    elif 45.2 < wp_last_temp_value <= 47.1:
        state_wp = 3
    elif 47.1 < wp_last_temp_value <= 50.1:
        state_wp = 4
    elif wp_last_temp_value > 50.1:
        state_wp = 5
    logging.info("Days since last legionella: " + str(days_since_last_legionella.days))
    print("Days since last legionella: " + str(days_since_last_legionella.days))
    logging.info("state_wp: " + str(state_wp) + " WP Temp: " + str(wp_last_temp_value))
    logging.info("state_pv: " + str(state_pv) + " PV Power: " + str(pv_last_peak_value))
    logging.info("state_room: " + str(state_room) + " Room Temp: " + str(room_last_peak_value))

    if state_wp <= start_condition_wp or days_since_last_legionella.days > 9:
        if days_since_last_legionella.days > 9:
            condition = "Legionella Temp necessary heating to: " +str(legionella_water_temp)
            msg = condition
            logging.info(msg)
            start_heating()
        elif get_last_start_date().days == 0 and wp_last_temp_value >= desired_water_temp - 2:
            condition = "Heating has already been activated today and temperatur is above desired_water_temp-2 => Will not start"
            msg = condition
            logging.info(msg)
            stop_heating()
        elif state_pv >= start_condition_pv and state_room >= start_condition_room and wp_last_temp_value < desired_water_temp:
            condition = "Heating"
            msg = "WP target: Heating"
            logging.info(msg)
            start_heating()
        elif state_pv <= start_condition_pv and state_room >= start_condition_room:
            condition = "Waiting for PV"
            msg = "Waiting for PV to produce enough power, current value: " + str(pv_last_peak_value)
            logging.info(msg)
            stop_heating()
        elif state_pv >= start_condition_pv and state_room <= start_condition_room:
            condition = "Waiting for Room Temp"
            msg = "Waiting for Room Temp to heat up, room only at: " + str(room_last_peak_value)
            logging.info(msg)
            stop_heating()
        elif state_room >= 3 and get_battery_soc() >= 80:
            condition = "Using warm room, letting WP work for 1 hour even when PV is not high enough"
            msg = condition
            start_heating()
        elif state_wp == 1 and get_battery_soc() >= 80:
            condition = "Start WP because WP temp to low: PV not high enough but battery SOC > 80%"
            msg = condition
            start_heating()
    #    elif  state_wp = 1 and get_battery_soc() <= 80 and datetime.datetime.now())
    elif state_wp != start_condition_wp:
        condition = "Warm enough"
        msg = "No heating required, Water is warm enough: " + str(wp_last_temp_value)
        logging.info(msg)
        stop_heating()
    else:
        condition = "Nothing to do"
        msg = condition
        logging.info(msg)
    print(msg)
    return (
        state_wp, pv_last_peak_value, state_room, room_last_peak_value, state_wp, wp_last_temp_value, condition, msg)


if __name__ == '__main__':
    print(str(datetime.datetime.now()) + ' Checking WP:')
    # logging.info(str(datetime.datetime.now()))
    print("Working state: " + str(decide_what_2_do()))
