#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.ion()

import time
import datetime as dt

from subprocess import call

# from lib.time_mesure_lib import Exec_time_mesurment
from lib.amod_interrupt_lib import Amod # class for 'amod' procedures
from lib.mysql_amod_lib import Mysql_amod # class for 'mysql' procededures

class Bat_mon_dyn:
    
    def __init__(self):
        #Set up plot
        self.figure, self.ax = plt.subplots()
        self.lines, = self.ax.plot([],[], '-')
        #Autoscale on unknown axis and known lims on the other
        self.ax.set_autoscaley_on(True)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H:%M:%S'))
        self.ax.set_title("Battery charge and discharge monitoring")
        self.ax.set_ylabel("Tension [V]")

        # Format the x-axis for dates (label formatting, rotation)
        self.figure.autofmt_xdate(rotation=45)
        #Other stuff
        self.ax.grid()

    def add_point(self, xdata, ydata):
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
    
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
        
if __name__ == '__main__':

    bat_mon_dyn = Bat_mon_dyn() # initialize bat_mon_dyn class
        
    mysql_amod = Mysql_amod('192.168.1.139') # initialize mysql class with server IP adress 
    sql_txt = "DELETE FROM tlog;" # delete all datas in tlog table
    mysql_amod.execute_sql(sql_txt) 

    amod = Amod() # initialize amode class

    u_bat_min = 3 # minumum battery voltage 
    n_moy = 50 # averaging to reduce glitches
    t_sleep = 2 # sleep time between two mesurements
    i = 0 # to count the passes
    stop_run = False # to control the execution (run/stop)
    
    xdata = []
    ydata = []

    print("mesure démarrée")

    while not stop_run:
        
        i += 1 # count passes
        u_avg = amod.get_tension(n_moy) # read the value in volts
        
        sql_txt = " ".join(["INSERT INTO tlog (mes_value) VALUES (", str(u_avg), ")"]) # save it in the database
        mysql_amod.execute_sql(sql_txt)

        xdata.append(dt.datetime.now())
        ydata.append(u_avg)
        bat_mon_dyn.add_point(xdata, ydata)

        print(dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " - " + str(i) + " -> " + '{:.3f}'.format(u_avg))
        
        if u_avg < u_bat_min:# or i > 10: 
            stop_run = True # stop the mesure
            
        if stop_run:
#             amod.plot_data() # graph the data's
            print("proper shut down of the machine due to low battery")
#             time.sleep(5)
#             call("sudo shutdown -h now", shell=True) # shutdown the RASPI
            
        time.sleep(t_sleep) # sleep until the next pass
