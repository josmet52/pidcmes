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
import pdb
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
        GPIO.add_event_detect(self.pin_mes, GPIO.RISING, callback=self.end_charge_reached) 
        
        self.t_discharge = 5e-3 # time to discharge the capacitor
        self.t_charge_stop = 0.0
        self.t_charge_start = 0.0
        self.stop_requierd = False
        self.rep_int_time = 5.15e-3
        self.v_timeout = 1

        if from_who != "calibration": # if not in calibration read the ini data 
            with open('amod.ini', 'r') as ini_file:
                data = ini_file.readlines()
                params = data[0].split(",")
                self.u_in_trig = float(params[0]) # the input trigger level (depend on the harware)
                self.R1 = float(params[1]) # value of the resistor
                self.C1 = float(params[2]) # value of the capacitor
                self.rep_int_time = float(params[3]) # interrupt respons time
        
    def get_tension(self, n_moyenne):

        GPIO.output(self.pin_cmd, GPIO.HIGH)

        i = 0
        j = 0
        n_ref = 20
        v_ref = 0.0
        l_ref = []
        v_tol = 0.025
        v_tol_etalon = v_tol / 2
        t_elapsed_average = 0

#         pdb.set_trace()

        while j < n_ref:
            
            time.sleep(self.t_discharge) # pour décharger le condo
            
            self.stop_requierd = False
            GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
            self.t_charge_start = time.time()
            
            while not self.stop_requierd:
                if time.time() - self.t_charge_start > self.v_timeout:
                    stop_requierd = True
                    print("interruption manquée")
            elapsed = (self.t_charge_stop - self.t_charge_start) - self.rep_int_time
            l_ref.append(elapsed)
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
            j += 1
         
#         pdb.set_trace()
        
        v_ref = sum(l_ref) / len(l_ref)
        print("before filtering: len v_ref = " + str(len(l_ref))+ " elapsed = " + '{:.2f}'.format(v_ref * 1000) + " ms")
        for j, v in enumerate(l_ref):
            if (v < v_ref * (1 - v_tol_etalon)) or (v > v_ref * (1 + v_tol_etalon)):
                print("v_ref = " + '{:.4f}'.format(v_ref) + " removed = " + '{:.4f}'.format(l_ref[j]) \
                               + " delta % = " + '{:.2f}'.format((l_ref[j] - v_ref) / v_ref * 100) \
                               + " tension = " + '{:.2f}'.format(self.u_in_trig / (1 - math.exp(-v / (self.R1 * self.C1)))))
                del l_ref[j]
                
        v_ref = sum(l_ref) / len(l_ref)
        print("after filtering: len v_ref = " + str(len(l_ref))+ " elapsed = " + '{:.2f}'.format(v_ref * 1000) + " ms")
        print()
        
        while i < n_moyenne:
            
            time.sleep(self.t_discharge) # pour décharger le condo
            self.stop_requierd = False
            GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
            self.t_charge_start = time.time()
            while not self.stop_requierd:
                if time.time() - self.t_charge_start > self.v_timeout:
                    stop_requierd = True
                    print("interruption manquée")
            v = self.t_charge_stop - self.t_charge_start - self.rep_int_time
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
            if (v > v_ref * (1 - v_tol)) and (v < v_ref * (1 + v_tol)):
                t_elapsed_average += v
                i += 1
            else:
                print("mesures removed = " + '{:.4f}'.format(v) \
                               + " delta % = " + '{:.2f}'.format((v - v_ref) / v_ref * 100) \
                               + " tension = " + '{:.2f}'.format(self.u_in_trig / (1 - math.exp(-v / (self.R1 * self.C1)))))
            
        t_elapsed = t_elapsed_average / n_moyenne
        u_average = self.u_in_trig / (1 - math.exp(-t_elapsed / (self.R1 * self.C1))) #- self.mesure_offset
        
        return u_average
    
    def end_charge_reached(self, channel):
        self.t_charge_stop = time.time()
        self.stop_requierd = True
        

    def set_param(self, u_in, R1, C1, n_moyenne, int_resp_time):

        GPIO.output(self.pin_cmd, GPIO.HIGH)

        i = 0
        j = 0
        n_ref = 100
        v_ref = 0.0
        l_ref = []
        v_tol = 0.05
        t_elapsed_average = 0
        
        while j < n_ref:
            time.sleep(self.t_discharge) # pour décharger le condo
            self.stop_requierd = False
            GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
            self.t_charge_start = time.time()
            while not self.stop_requierd:
                pass
            elapsed = (self.t_charge_stop - self.t_charge_start) - self.rep_int_time
            l_ref.append(elapsed)
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
            j += 1
         
#         pdb.set_trace()
        
        v_ref = sum(l_ref) / len(l_ref)
        print("before filterint: len v_ref = " + str(len(l_ref))+ " elapsed = " + '{:.2f}'.format(v_ref * 1000) + " ms")
        for j, v in enumerate(l_ref):
            if (v < v_ref * (1 - v_tol)) or (v > v_ref * (1 + v_tol)):
                print("v_ref = " + '{:.4f}'.format(v_ref) + " removed = " + '{:.4f}'.format(l_ref[j]) \
                               + " delta % = " + '{:.2f}'.format((l_ref[j] - v_ref) / v_ref * 100)) # \
#                                + " tension = " + '{:.2f}'.format(self.u_in_trig / (1 - math.exp(-v / (self.R1 * self.C1)))))
                del l_ref[j]
                
        v_ref = sum(l_ref) / len(l_ref)
        print("after filterint: len v_ref = " + str(len(l_ref))+ " elapsed = " + '{:.2f}'.format(v_ref * 1000) + " ms")
        
        while i < n_moyenne:
            
            time.sleep(self.t_discharge) # pour décharger le condo
            self.stop_requierd = False
            GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
            self.t_charge_start = time.time()
            while not self.stop_requierd:
                pass
            v = self.t_charge_stop - self.t_charge_start - self.rep_int_time
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
            if (v > v_ref * (1 - v_tol)) and (v < v_ref * (1 + v_tol)):
                t_elapsed_average += v
                i += 1
            
        t_elapsed = t_elapsed_average / n_moyenne
        u_trig_calc = u_in * (1 - math.exp(-t_elapsed / (R1 * C1)))

        with open('amod.ini', 'w') as ini_file:
            ini_file.writelines(str(u_trig_calc) + "," + str(R1) + "," + str(C1) + "," + str(int_resp_time))

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
