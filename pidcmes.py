#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The pidcmes.py program is used to check the stability and precision of the measurement. it is executed in an endless loop.
Each measurement is printed on the screen and on a graph.

- The constant AVERAGING_ON allows to change the number of measurements made before filtering on 1.5 standard deviation
then to take the average. This average is made directly in the get_tension function of the Pidcmes class.

- The T_BETWEEN_MESUREMENTS constant is used to set the time in seconds between two measurements. It can have a value
between 0 and a lot. If it is less than 5 seconds, there is a risk of thermal drift of the measurement.

The measuring range starts at around 2.8 volts and can go up to more than 10V.
Warning in the event of a fault in the LM393 comparator or the BS170 MOSFET, the measurement voltage could be applied to the RPI input and destroy it.
 
"""
# import matplotlib
# matplotlib.use("TKAgg")
import matplotlib.pyplot as plt
# plt.ion()
# import matplotlib.dates as mdates

import time
import datetime
from pidcmes_lib import Pidcmes # class for 'pidcmes' procedures

# import pdb
        
if __name__ == '__main__':

    #Set up plot

    # figure, ax = plt.subplots()
    # lines, = ax.plot([],[], '-')
    #Autoscale on unknown axis and known lims on the other
    # ax.set_autoscaley_on(True)
    # ax.set_title("Battery charge and discharge monitoring")
    # ax.set_ylabel("Tension [V]")

    # Format the x-axis for dates (label formatting, rotation)
    # figure.autofmt_xdate(rotation=45)
    #Other stuff
    # ax.grid()
            
    pidcmes = Pidcmes() # initialize pidcmese class
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H:%M:%S'))

    # parameters
    AVERAGING_ON = 20 # averaging to reduce glitches
    T_BETWEEN_MESUREMENTS = 3 # one mesure each 5 minutes
    
    #internal variables
    i = 0 # to count the passes
    xdata = []
    ydata = []

    print("measurement started")

    while True:
        
        # records the time of the start of the measurement to calculate the sleep time
        t_next_mes = datetime.datetime.now() + datetime.timedelta(seconds = T_BETWEEN_MESUREMENTS)
        
        i += 1 # count passes
        # perform the voltage measurement
        u_avg = round(pidcmes.get_tension(AVERAGING_ON), 2) # read the value in volts
        # prepare the data for the chart
        xdata.append(datetime.datetime.now())
        ydata.append(u_avg)

        plt.xticks(rotation=45)
        plt.title("pidcmes: suivi de la tension")
        plt.ylabel("Tension [V]")
        plt.grid(True)
        plt.autoscale()
        plt.plot(xdata, ydata, 'b-')
        plt.pause(2)
#         plt.close()

        # #Update data (with the new _and_ the old points)
        # lines.set_xdata(xdata)
        # lines.set_ydata(ydata)
        # #Need both of these in order to rescale
        # ax.relim()
        # ax.autoscale_view()
        # #We need to draw *and* flush
        # figure.canvas.draw()
        # figure.canvas.flush_events()
        # figure.show()

        # displays the measured value
        print("measure no: " + str(i) + " - " + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " -> " + '{:.2f}'.format(u_avg))
        
        #calculates and executes sleep time
        t_sleep = max((t_next_mes - datetime.datetime.now()).total_seconds(), 0)
        time.sleep(t_sleep)

