#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
plt.ion()
import matplotlib.dates as mdates

import time
import datetime
from pidcmes_lib import Pidcmes # class for 'pidcmes' procedures
        
if __name__ == '__main__':

    pidcmes = Pidcmes() # initialize pidcmese class
    pidcmes.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H:%M:%S'))

    # parameters
    AVERAGING_ON = 10 # averaging to reduce glitches
    T_BETWEEN_MESUREMENTS = 0
    
    #internal variables
    i = 0 # to count the passes
    xdata = []
    ydata = []

    print("measurement started")

    while True:
        
        t_next_mes = datetime.datetime.now() + datetime.timedelta(seconds = T_BETWEEN_MESUREMENTS)
        
        i += 1 # count passes
        u_avg = round(pidcmes.get_tension(AVERAGING_ON), 2) # read the value in volts
        
        xdata.append(datetime.datetime.now())
        ydata.append(u_avg)
        pidcmes.add_point(xdata, ydata)

        print(datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " - Mesure: " + str(i) + " -> " + '{:.2f}'.format(u_avg) \
              + " (durée de la mesure " + '{:.2f}'.format(T_BETWEEN_MESUREMENTS - (t_next_mes - datetime.datetime.now()).total_seconds()) + " s)")
        
        t_sleep = max((t_next_mes - datetime.datetime.now()).total_seconds(), 0)
        time.sleep(t_sleep)

