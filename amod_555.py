#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.ion()

import time
import datetime as dt

from subprocess import call

from amod_555_lib import Amod # class for 'amod' procedures
from lib.mysql_amod_lib import Mysql_amod # class for 'mysql' procededures

import pdb
        
if __name__ == '__main__':
        
    mysql_amod = Mysql_amod('192.168.1.139') # initialize mysql class with server IP adress 
    sql_txt = "DELETE FROM tlog;" # delete all datas in tlog table
    mysql_amod.execute_sql(sql_txt) 

    u_bat_min = 3.4 # minumum battery voltage 
    n_moy = 20 # averaging to reduce glitches
    t_sleep = 2 # sleep time between two mesurements
    i = 0 # to count the passes
    stop_run = False # to control the execution (run/stop)
    
    pin_cmd_bat = 8
    pin_mes_bat = 10
    pin_cmd_out = 12
    pin_mes_out = 16

    amod = Amod(pin_cmd_bat, pin_mes_bat, pin_cmd_out, pin_mes_out) # initialize amode class
   
    xdata = []
    ydata_bat = []
    ydata_out = []

    print("mesure démarrée")

    while not stop_run:
        
        i += 1 # count passes
        u_avg_bat = amod.get_tension(n_moy, pin_cmd_bat, pin_mes_bat) # read the value in volts
        u_avg_out = amod.get_tension(n_moy, pin_cmd_out, pin_mes_out) # read the value in volts
        
        sql_txt = " ".join(["INSERT INTO tlog (u_bat, u_out) VALUES (", str(u_avg_bat), ", ", str(u_avg_out), ")"]) # save it in the database
        mysql_amod.execute_sql(sql_txt)

        xdata.append(dt.datetime.now())
        ydata_bat.append(u_avg_bat)
        ydata_out.append(u_avg_out)
        amod.add_point(xdata, ydata_bat, ydata_out)

        print(dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " - " \
              + str(i) + " bat -> " + '{:.2f}'.format(u_avg_bat) \
               + " out -> " + '{:.2f}'.format(u_avg_out))
        
#         pdb.set_trace()
        
#         if u_avg < u_bat_min:# or i > 10: 
#             stop_run = True # stop the mesure
            
#         if stop_run:
#             amod.plot_data() # graph the data's
#             print("proper shut down of the machine due to low battery")
#             time.sleep(5)
#             call("sudo shutdown -h now", shell=True) # shutdown the RASPI
            
        time.sleep(t_sleep) # sleep until the next pass
