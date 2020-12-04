#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import datetime as dt

from subprocess import call

# from lib.time_mesure_lib import Exec_time_mesurment
from lib.amod_lib import Amod # class for 'amod' procedures
from lib.mysql_amod_lib import Mysql_amod # class for 'mysql' procededures

mysql_amod = Mysql_amod('192.168.1.139') # initialize mysql class with server IP adress 
sql_txt = "DELETE FROM tlog;" # delete all datas in tlog table
mysql_amod.execute_sql(sql_txt) 

amod = Amod() # initialize amode class

u_bat_min = 3.3 # minumum battery voltage 
n_moy = 200 # averaging to reduce glitches
t_sleep = 60 # sleep time between two mesurements
i = 0 # to count the passes
stop_run = False # to control the execution (run/stop)

print("mesure démarrée")

while not stop_run:
    
    i += 1 # count passes
    u_avg = amod.get_tension(n_moy) # read the value in volts
    
    sql_txt = " ".join(["INSERT INTO tlog (mes_value) VALUES (", str(u_avg), ")"]) # save it in the database
    mysql_amod.execute_sql(sql_txt)
    
    str_2_print = str(i) + " -> " + '{:.2f}'.format(u_avg) + " - " + dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print(str_2_print)
    
    if u_avg < u_bat_min: # or i > 10: 
        stop_run = True # stop the mesure
        
    if stop_run:
        amod.plot_data() # graph the data's
        GPIO.cleanup() # cleanup GPIO
        print("proper shut down of the machine due to low battery")
        call("sudo shutdown -h now", shell=True) # shut down the RASPI
        
    time.sleep(t_sleep) # sleep until the next pass
