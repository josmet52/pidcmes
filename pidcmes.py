#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.ion()

import time
import datetime as dt

from subprocess import call

from pidcmes_lib import Pidcmes # class for 'pidcmes' procedures
from lib.mysql_pidcmes_lib import Mysql_pidcmes # class for 'mysql' procededures

import pdb
        
if __name__ == '__main__':
        
    mysql_pidcmes = Mysql_pidcmes('192.168.1.139') # initialize mysql class with server IP adress 
    sql_txt = "DELETE FROM tlog;" # delete all datas in tlog table
    mysql_pidcmes.execute_sql(sql_txt) 

    pidcmes = Pidcmes() # initialize pidcmese class
    pidcmes.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H:%M:%S'))

    u_bat_min = 3.4 # minumum battery voltage 
    n_moy = 20 # averaging to reduce glitches
    t_sleep = 2 # sleep time between two mesurements
    i = 0 # to count the passes
    stop_run = False # to control the execution (run/stop)
    xdata = []
    ydata = []

    print("mesure démarrée")

    while not stop_run:
        
        i += 1 # count passes
        u_avg = pidcmes.get_tension(n_moy) # read the value in volts
        
        sql_txt = " ".join(["INSERT INTO tlog (mes_value) VALUES (", str(u_avg), ")"]) # save it in the database
        mysql_pidcmes.execute_sql(sql_txt)

        xdata.append(dt.datetime.now())
        ydata.append(u_avg)
        pidcmes.add_point(xdata, ydata)

        print(dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " - Mesure: " + str(i) + " -> " + '{:.4f}'.format(u_avg))
        
        if u_avg < u_bat_min:# or i > 10: 
#             pidcmes.plot_data() # graph the data's
            print("proper shut down of the machine due to low battery")
#             time.sleep(5)
#             call("sudo shutdown -h now", shell=True) # shutdown the RASPI
        t = 5 - dt.datetime.now().second
        if t < 0 : t = 1
#         print(t)
        time.sleep(t)

