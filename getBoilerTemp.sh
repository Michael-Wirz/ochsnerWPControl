 esp32_cam_ip=192.168.1.186
 influx_host=localhost
 influx_db=your_db_for_saving_the_temp_values
 rm -f saved-photo*
 #tell the esp to snap a new picture
 curl http://${esp32_cam_ip}/capture
 #wait until the picture is ready
 sleep 10
 #grab the picutre
 wget http://${esp32_cam_ip}/saved-photo
 #move the save-photo to save-photo.jpeg
 mv saved-photo saved-photo.jpeg
 #rotate and crop the picture and save the output as afterConvert.jpeg
 convert saved-photo.jpeg -rotate 269 -brightness-contrast -70,0 -crop 1000x500+325+425 -colorspace gray afterConvert.jpeg

 #use textcleaner.sh => makes it easier for the ocr
 ./textcleaner.sh -c 0,0,100,0 afterConvert.jpeg afterTextcleaner.jpeg
 #get the boiler temp from the picture with ssocr
 boilerTemp=$(ssocr/ssocr -d 3 afterTextcleaner.jpeg)
 #Problem with nr7, will be recognized as _ so I replace _ with 7
 boilerTemp=${boilerTemp/_/7}
 #decimal dot will not be recognized => divide the result by 10
 boilerTemp=$(echo "scale=1;${boilerTemp}/10"|bc -l)

 echo "TEMP: ${boilerTemp}"
 if [ -z "${boilerTemp}" ]
 then
   echo "ERROR"
 else
   echo "$(date +%s) ${boilerTemp}" >> templog.txt
   #write the temp value to your influx db
   curl -s -i -XPOST 'http://${influx_host}:8086/write?db=${influx_db' --data-binary 'boiler device="boiler",temp='${boilerTemp}''
 fi