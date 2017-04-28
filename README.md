## Description

This is yet another way of controlling carwings. The python script serves as middleware to communicate with carwings. A set of node-red flows take care of user interface and may easily serve future rule deployment to request updates based on external events.

At the moment my personal implementation updates carwings automatically only when receiving carwings emails and avoid useless periodic updates that can hurt Nissan and/or the car's already poor management of the 12V battery.


## Install

- Raspberry pi with emoncms image
- ```pip install git+https://github.com/apreb/pycarwings2.git```
- ```pip install paho-mqtt```
- [TODO] Node-RED Flows to control Carwings


## Using

- Grab the files in the exemples directory and place them on /home/pi 
- perform chmod +x carwings.py
- change mqtt settings in the carwings.ini file
- execute carwings.py

```
root@emonpi(rw):pi# ./carwings.py 

Invalid operand, please check below


usage:
       carwings.py [user] [password] [action]

[user]     - carwings username
[password] - carwings password
[action]
   - battlaststaus          - Request Last Status
   - battupdate             - Request Update
   - climateupdate          - Request Climate Update
   - climatestart           - Request Climate Start
   - climatestop            - Request Climate Stop
   - chargestart            - Request Charge Start
   - RateSimulation YYYYMM  - Request RateSimulation
   - driveanalysis          - Request driveanalysis
root@emonpi(ro):pi# 
```



## credits
- https://github.com/jdhorne/pycarwings2
- https://github.com/glynhudson/leaf-python-mqtt
- https://github.com/emoncms
