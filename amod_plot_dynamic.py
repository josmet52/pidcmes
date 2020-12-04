#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import numpy as np

from lib.time_mesure_lib import Exec_time_mesurment
from lib.mysql_amod_lib import Mysql_amod
from lib.amod_lib import Amod
#     
# class Plot_dyn:
#     
#     def __init__(self):
#         self.mysql_amod = Mysql_amod("192.168.1.139") # initilize mysql class with IP of the mysql server
#     
#     def plot_data(self):    
# 
#         sql_txt = "SELECT time_stamp, mes_value FROM tlog;"
#         data = self.mysql_amod.get_data(sql_txt)
# 
#         mes_time = []
#         mes_tension = []
# 
#         for row in data:
#             mes_time.append(row[0])
#             mes_tension.append(row[1])
# 
#         # Convert datetime.datetime to float days since 0001-01-01 UTC.
#         dates = [mdates.date2num(t) for t in mes_time]
# 
#         fig = plt.figure()
#         ax1 = fig.add_subplot(111)
#         ax1.set_title("first plot test")
# 
#         # Configure x-ticks
#         ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H:%M'))
# 
#         # Plot temperature data on left Y axis
#         ax1.set_ylabel("Tension [V]")
#         ax1.plot_date(dates, mes_tension, '-', label="Tension accu", color='b')
#         # ax1.plot_date(dates, mes_time, '-', label="Feels like", color='b')
# 
#         # Format the x-axis for dates (label formatting, rotation)
#         fig.autofmt_xdate(rotation=60)
#         fig.tight_layout()
# 
#         # Show grids and legends
#         ax1.grid(True)
#         ax1.legend(loc='best', framealpha=0.5)
#         plt.savefig("figure.png")
#         plt.show()
# 
# if __name__ == '__main__':
# 
#     plot_dyn = Plot_dyn()
#     plot_dyn.plot_data()
amod = Amod()
amod.plot_data()
