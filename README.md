# ochsnerWPControl

PROJECT UNDER DEVELOPMENT ***USE AT YOUR OWN RISK***\
Description not finished yet, still working on the project 2022-10-14

Project to control your warm water heater.

You need: \
A warm water heater you wish to control which has a potential free input option \

Solaranzeige.de for measuring all the values of your PV system\

An influx DB (you can reuse the one from solaranzeige.de) to save the temperature values from your heater\

A ShellyV1 to control your potential free circuit of your heater\

An ESP32-CAM to capture the screen of your heater (or a heater with a connection to read the actual water temperature)

MyStrom power switch to measure the temperature of the room and the power consumption of the heater.

------------------------------

I am using a ESP32-CAM (7$ Aliexpress) to capture the screen of my heater.

Here you can find a tutorial, how to setup the cam:
https://randomnerdtutorials.com/esp32-cam-take-photo-display-web-server/

This software creates a webserver on the ESP32 where you can grab the picture from.

The getBoilerTemp.sh script grabs the picture from the esp, OCR the numbers from the picutre and saves them into an influx db.
Requirements for getBoilerTemp.sh
SSOCR:
https://www.unix-ag.uni-kl.de/~auerswal/ssocr/
Textcleaner:
http://www.fmwconcepts.com/imagemagick/textcleaner/index.php

The main script is ochsnerControl.py
First phase: getting all the necessary information

Power:\
It grabs the average "Ueberschuss" from Solaranzeige for the last 20 Minutes and combines it with the "Lade_Entladeleistung" of the Batterie to get the amount of available power which is not consumed by the house



