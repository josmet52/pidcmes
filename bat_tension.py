#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import datetime as dt
# import RPi.GPIO as GPIO
# import pigpio
# import math
# import numpy as np
# import matplotlib.pyplot as plt

from subprocess import call
from lib.time_mesure_lib import Exec_time_mesurment
from lib.amod_lib import Amod
from lib.mysql_amod_lib import Mysql_amod

mysql_amod = Mysql_amod('192.168.1.139')
sql_txt = "DELETE FROM tlog;"
mysql_amod.execute_sql(sql_txt)

amod = Amod()

n_moy = 200
i = 0
t_sleep = 60
stop_run = False

print("mesure démarrée")

while not stop_run:
    u_avg = 0
    i += 1
    
    u_avg += amod.get_tension(n_moy)
    
    sql_txt = " ".join(["INSERT INTO tlog (mes_value) VALUES (", str(u_avg), ")"])
    mysql_amod.execute_sql(sql_txt)
    
    str_2_print = str(i) + " -> " + '{:.2f}'.format(u_avg) + " - " + dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print(str_2_print)
    
    if u_avg < 3 :
        
        # graph the data's
        amod.plot_data()
        # stop the mesure
        GPIO.cleanup()
        stop_run = True
        # shut down the RASPI
        print("proper shut down of the machine due to low battery")
#         call("sudo shutdown -h now", shell=True)
        
    time.sleep(t_sleep)
#     if i >= 10:
#         stop_run = True
    
GPIO.cleanup()
