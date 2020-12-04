#!/usr/bin/env python3
# -*-
"""
    class Amod to
    - read analog tension on two digital pins
    - calibrate the sensor
    - plot the measured data's
"""
import time
import RPi.GPIO as GPIO
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import numpy as np

from lib.time_mesure_lib import Exec_time_mesurment
from lib.mysql_amod_lib import Mysql_amod

class Amod:
    
    def __init__(self, from_who = ""):
        
        # version infos
        VERSION_NO = "0.01.01" 
        VERSION_DATE = "27.11.2020"
        VERSION_DESCRIPTION = "prototype"
        VERSION_STATUS = "initial version"
        VERSION_AUTEUR = "josmet"
        
        self.mysql_amod = Mysql_amod("192.168.1.139") # initilize mysql class with IP of the mysql server

        self.pin_cmd = 38 # control pin
        self.pin_mes = 36 # measure pin
  
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin_cmd, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.pin_mes, GPIO.IN)  # initialize measure pi (attention no pull-up or pull-down)

        self.t_discharge = 0.05E-3 # time to discharge the capacitor

        if from_who != "calibration": # if not in calibration read the ini data 
            with open('amod.ini', 'r') as ini_file:
                data = ini_file.readlines()
                params = data[0].split(",")
                self.u_in_trig = float(params[0]) # the input trigger level (depend on the harware)
                self.R1 = float(params[1]) # value of the resistor
                self.C1 = float(params[2]) # value of the capacitor
        
    def get_tension(self, n_moyenne):

        GPIO.output(self.pin_cmd, GPIO.HIGH)

        i = 0
        t_elapsed_average = 0
        
        while i < n_moyenne:
            
            time.sleep(self.t_discharge) # pour décharger le condo
            with Exec_time_mesurment() as etm:  
                GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
                while GPIO.input(self.pin_mes) == GPIO.LOW:
                    pass
            t_elapsed_average += etm.interval  
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
            i += 1
#             print(i, etm.interval)
            
        t_elapsed = t_elapsed_average / n_moyenne
#         u_average = self.mesure_offset + ((self.u_in_trig - self.mesure_offset) / (1 - math.exp(-t_elapsed / (self.R1 * self.C1))))
        u_average = self.u_in_trig / (1 - math.exp(-t_elapsed / (self.R1 * self.C1))) #- self.mesure_offset
        
        return u_average
        
    def set_param(self, u_in, R1, C1, n_moyenne):

        GPIO.output(self.pin_cmd, GPIO.HIGH)

        i = 1
        t_elapsed_average = 0
        
        while i <= n_moyenne:
            
            time.sleep(self.t_discharge) # pour décharger le condo
            with Exec_time_mesurment() as etm:  
                GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
                while GPIO.input(self.pin_mes) == GPIO.LOW:
                    pass
            t_elapsed_average += etm.interval  
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
            i += 1
            
        t_elapsed = t_elapsed_average / n_moyenne
#         u_trig_calc = self.mesure_offset + ((u_in - self.mesure_offset) * (1 - math.exp(-t_elapsed / (R1 * C1))))
        u_trig_calc = u_in * (1 - math.exp(-t_elapsed / (R1 * C1)))

        with open('amod.ini', 'w') as ini_file:
            ini_file.writelines(str(u_trig_calc) + "," + str(R1) + "," + str(C1))

        return u_trig_calc
    
    def plot_data(self):    

        sql_txt = "SELECT time_stamp, mes_value FROM tlog;"
        data = self.mysql_amod.get_data(sql_txt)

        mes_time = []
        mes_tension = []

        for row in data:
            mes_time.append(row[0])
            mes_tension.append(row[1])

        # Convert datetime.datetime to float days since 0001-01-01 UTC.
        dates = [mdates.date2num(t) for t in mes_time]

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title("first plot test")

        # Configure x-ticks
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H:%M'))

        # Plot temperature data on left Y axis
        ax1.set_ylabel("Tension [V]")
        ax1.plot_date(dates, mes_tension, '-', label="Tension accu", color='b')
        # ax1.plot_date(dates, mes_time, '-', label="Feels like", color='b')

        # Format the x-axis for dates (label formatting, rotation)
        fig.autofmt_xdate(rotation=60)
        fig.tight_layout()

        # Show grids and legends
        ax1.grid(True)
        ax1.legend(loc='best', framealpha=0.5)
        plt.savefig("figure.png")
        plt.show()
