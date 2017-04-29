#!/usr/bin/python

import pycarwings2
import time
import datetime
from ConfigParser import SafeConfigParser
import logging
import sys
import pprint
import paho.mqtt.client as mqtt
import os
import json
import re

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

if (len(sys.argv) < 4):
  print "\nInvalid operand, please check below\n"
  print "\nusage:"
  print "       carwings.py [user] [password] [action]\n"
  print "[user]     - carwings username"
  print "[password] - carwings password"
  print "[action]"
  print "   - battlaststaus          - Request Last Status"
  print "   - battupdate             - Request Update"
  print "   - climateupdate          - Request Climate Update"
  print "   - climatestart           - Request Climate Start"
  print "   - climatestop            - Request Climate Stop"
  print "   - chargestart            - Request Charge Start" 
  print "   - RateSimulation YYYYMM  - Request RateSimulation" 
  print "   - driveanalysis          - Request driveanalysis" 
  sys.exit()

username = str(sys.argv[1])
password = str(sys.argv[2])
action = str(sys.argv[3])
originalaction = str(sys.argv[3])

if action == 'RateSimulation':
  if (len(sys.argv) != 5):
    print "\nPovide Target Month in format YYYYMM\n"
    print "\nExample:"
    print "       carwings.py [user] [password] RateSimulation 201703\n"
    sys.exit()
  tdate = str(sys.argv[4])
  pattern = re.compile("^20\d{4}$")
  if not pattern.match(tdate):
    print "Target Month not Valid!"
    sys.exit()

parser = SafeConfigParser()
candidates = [ '/home/pi/carwings.ini' ]
found = parser.read(candidates)

mqtt_host = parser.get('mqtt-info', 'broker')
mqtt_status_topic = parser.get('mqtt-info', 'topic')

client = mqtt.Client()
client.connect(mqtt_host, "1883", 60)

# Prepare Session
s = pycarwings2.Session(username, password , "NE")

try:
  # Login...
  l = s.get_leaf()
  client.publish(mqtt_status_topic , "Login OK" ,qos=0)
except:
  client.publish(mqtt_status_topic , "Login NOK" ,qos=0)
  sys.exit()



if action == 'battupdate':
  # REQUEST UPDATE
  result_key = l.request_update()
  i=0
  while True:
    i = i+1
    time.sleep(20)
    leaf_info = l.get_status_from_update(result_key)
    if leaf_info is not None:
      client.publish(mqtt_status_topic + "/json/update", json.dumps(leaf_info.answer) ,qos=0, retain=True)
      client.publish(mqtt_status_topic + "/json/update/success", "success",qos=0, retain=True)
      break
    if i > 3:
      client.publish(mqtt_status_topic + "/json/update/success", "Timeout",qos=0, retain=True)
      break
          
elif action == 'battlaststaus':
  leaf_info = l.get_latest_battery_status()
  client.publish(mqtt_status_topic + "/json/laststatus", json.dumps(leaf_info.answer) ,qos=0, retain=True)
          
elif action == 'climateupdate':
  leaf_info = l.get_latest_hvac_status()
  client.publish(mqtt_status_topic + "/json/climate", json.dumps(leaf_info.answer)  ,qos=0 )

elif action == 'climatestart':
  result_key = l.start_climate_control()
  client.publish(mqtt_status_topic + "/json/climate", json.dumps(leaf_info.answer) ,qos=0)

elif action == 'climatestop':
  result_key = l.stop_climate_control()
  client.publish(mqtt_status_topic + "/json/climate", json.dumps(leaf_info.answer) ,qos=0)
  
elif action == 'chargestart':
  result_key = l.start_charging()
  client.publish(mqtt_status_topic + "/json/charge", json.dumps(leaf_info.answer) ,qos=0)
         
elif action == 'driveanalysis':
  leaf_info = l.get_driving_analysis()
  client.publish(mqtt_status_topic + "/json/drive", json.dumps(leaf_info.answer) ,qos=0, retain=True)

elif action == 'RateSimulation':
  leaf_info = l.get_electric_rate_simulation(tdate)
  client.publish(mqtt_status_topic + "/json/rate/" + tdate, json.dumps(leaf_info.answer) ,qos=0, retain=True)
  if datetime.datetime.now().strftime("%Y%m") == tdate:
    client.publish(mqtt_status_topic + "/json/rate/latest", json.dumps(leaf_info.answer) ,qos=0, retain=True)

elif action == 'getlatlon':
  leaf_info = l.get_lat_lon()
  client.publish(mqtt_status_topic + "/json/latlon", json.dumps(leaf_info.answer) ,qos=0, retain=True)
