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
import numpy as np
import scipy.stats as stat
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import pdb

class Amod:
    
    def __init__(self, from_who = ""):
        
        # version infos
        VERSION_NO = "0.01.01" 
        VERSION_DATE = "27.11.2020"
        VERSION_DESCRIPTION = "prototype"
        VERSION_STATUS = "initial version"
        VERSION_AUTEUR = "josmet"
        
        self.pin_cmd = 38 # control pin
        self.pin_mes = 36 # measure pin
  
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin_cmd, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.pin_mes, GPIO.IN)  # initialize measure pi (attention no pull-up or pull-down)
        GPIO.add_event_detect(self.pin_mes, GPIO.RISING, callback=self.end_charge_reached) 
        GPIO.output(self.pin_cmd, GPIO.HIGH) 
        
        self.t_discharge = 5e-3 # time to discharge the capacitor
        self.t_charge_stop = 0.0
        self.t_charge_start = 0.0
        self.stop_requierd = False
        self.rep_int_time = 5.15e-3
        self.v_timeout = 1
        self.v_tol = 2.5 / 100 # 2.5 %
        self.filter = 1.5 # +/- n ecart types gardés


        if from_who != "calibration": # if not in calibration read the ini data 
            with open('amod.ini', 'r') as ini_file:
                data = ini_file.readlines()
                params = data[0].split(",")
                self.u_in_trig = float(params[0]) # the input trigger level (depend on the harware)
                self.R1 = float(params[1]) # value of the resistor
                self.C1 = float(params[2]) # value of the capacitor
                self.rep_int_time = float(params[3]) # interrupt respons time
        
    def get_tension(self, n_moyenne, show_histogram = False):

        GPIO.output(self.pin_cmd, GPIO.HIGH) # décharger le condensateur

        j = 0
        l_elapsed = []
        while j < n_moyenne:
            
            time.sleep(self.t_discharge) # laisser du temps pour décharger le condo
            
            self.stop_requierd = False
            GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
            self.t_charge_start = time.time() # déclancher le chrono
#TODO: voir s'il ne faut pas inverser les deux opérations ci-dessus
            
            while not self.stop_requierd:
                if time.time() - self.t_charge_start > self.v_timeout:
                    stop_requierd = True
                    print("interruption manquée")
            elapsed = (self.t_charge_stop - self.t_charge_start) - self.rep_int_time
            l_elapsed.append(elapsed)
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
            j += 1
        
        # get stats of data list
        nx, mmx, mx, vx, skx, ktx = stat.describe(l_elapsed)
        # filter the data list
        df = pd.DataFrame(l_elapsed, columns=list('B'))
        l_ref_filtered = df[((df.B - df.B.mean()) / df.B.std()).abs() < self.filter]
        l_ref_filtered_mean = l_ref_filtered.B.mean()

        # create ans show histogramm
        if show_histogram:
            l_tension = []
            for v in l_elapsed:
                l_tension.append(self.u_in_trig / (1 - math.exp(- v / (self.R1 * self.C1))))
                
            df1 = pd.DataFrame(l_tension, columns=list('B'))
            l_tension_filtered = df1[((df1.B - df1.B.mean()) / df1.B.std()).abs() < self.filter]
            l_tension_filtered_mean = l_tension_filtered.B.mean()
        
            # plot histogramm
            n, bins, patches = plt.hist(x=l_tension, bins=min(int(n_moyenne/4),50), color='#0504aa', alpha=0.7, rwidth=0.85)
            plt.hist(x=l_tension_filtered, bins=bins, color='#ffff00', alpha=0.7, rwidth=0.85)
            plt.grid(axis='y', alpha=0.75)
            plt.xlabel('Avg = ' + '{:.3f}'.format(l_tension_filtered_mean))
            plt.ylabel('Frequency')
            plt.title("Filtered on " + str(self.filter) + " standard deviation")
            plt.text(23, 45, r'$\mu=15, b=3$')
            maxfreq = n.max()
            # Set a clean upper y-axis limit.
            plt.ylim(ymax=np.ceil(maxfreq/10) *10 if maxfreq % 10 else maxfreq + 10)
            # insert a legend
            blue_patch = mpatches.Patch(color='#0504aa', label='excluded')
            yellow_patch = mpatches.Patch(color='#ffff00', label='used for avg')
            plt.legend(handles=[blue_patch, yellow_patch])

            plt.show()
            
        u_average = self.u_in_trig / (1 - math.exp(- l_ref_filtered_mean / (self.R1 * self.C1)))
        return u_average
    
    def end_charge_reached(self, channel):
        self.t_charge_stop = time.time()
        self.stop_requierd = True

    def set_param(self, u_in, xR1, xC1, n_moyenne, int_resp_time):

        GPIO.output(self.pin_cmd, GPIO.HIGH) # décharger le condensateur

        j = 0
        l_elapsed = []
        while j < n_moyenne:
            
            time.sleep(self.t_discharge) # laisser du temps pour décharger le condo
            
            self.stop_requierd = False
            GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
            self.t_charge_start = time.time() # déclancher le chrono
#TODO: voir s'il ne faut pas inverser les deux opérations ci-dessus
            
            while not self.stop_requierd:
                if time.time() - self.t_charge_start > self.v_timeout:
                    stop_requierd = True
                    print("interruption manquée")
            elapsed = (self.t_charge_stop - self.t_charge_start) - self.rep_int_time
            l_elapsed.append(elapsed)
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
            j += 1
        
        # get stats of data list
        nx, mmx, mx, vx, skx, ktx = stat.describe(l_elapsed)
        # filter the data list
        df = pd.DataFrame(l_elapsed, columns=list('B'))
        l_ref_filtered = df[((df.B - df.B.mean()) / df.B.std()).abs() < self.filter]
        l_ref_filtered_mean = l_ref_filtered.B.mean()

        u_trig_calc = u_in * (1 - math.exp(-l_ref_filtered_mean / (xR1 * xC1)))

        with open('amod.ini', 'w') as ini_file:
            ini_file.writelines(str(u_trig_calc) + "," + str(xR1) + "," + str(xC1) + "," + str(int_resp_time))

        return u_trig_calc

if __name__ == '__main__':

    #verify tension and filtering
    amod = Amod()
    a = amod.get_tension(50, show_histogram = True)
    
    GPIO.cleanup()

        
