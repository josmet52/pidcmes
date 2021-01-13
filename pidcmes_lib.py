#!/usr/bin/env python3
# -*-
"""
    class Pidcmes to
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
import matplotlib
matplotlib.use("TKAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import os

class Pidcmes:
        
    app_dir = os.path.dirname(os.path.realpath(__file__))
    pin_cmd = 8 # control pin
    pin_mes = 10 # measure pin
    
    def __init__(self, from_who = ""):
  
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin_cmd, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.pin_mes, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # initialize measure pi (attention no pull-up or pull-down)
        GPIO.add_event_detect(self.pin_mes, GPIO.FALLING, callback=self.interrupt_management) 
        
        self.t_end_mesure = 0.0 # value changed by interrupt_management()
        self.end_required = False
        self.PULSE_WIDTH = 10e-3 # pulse width to trig the measure and discharge the condensator
#         self.T_PAUSE_BETWEEN_MEASURES = 10e-3 # sleep time between two measures
        self.T_TIMEOUT = 1 # if no interruption after t_timeout -> no tension on the measure pin
        self.filter = 1.5 # +/- filter on n standard deviation

        if from_who == "calibration": 
            GPIO.output(self.pin_cmd, GPIO.HIGH)
        else: 
            GPIO.output(self.pin_cmd, GPIO.LOW)
            # if not in calibration read the ini data file
            with open("".join([self.app_dir, '/pidcmes.ini']), 'r') as ini_file:
                data = ini_file.readlines()
                params = data[0].split(",")
                self.u_in_trig = float(params[0]) # the input trigger level (depend on the harware)
                self.R1 = float(params[1]) # value of the resistor
                self.C1 = float(params[2]) # value of the capacitor
                self.int_resp_time = float(params[3]) # interrupt response time
        
    def get_tension(self, n_moyenne, show_histogram = False):

#         GPIO.output(self.pin_cmd, GPIO.HIGH) # décharger le condensateur
#         time.sleep(self.T_PAUSE_BETWEEN_MEASURES)
#         GPIO.output(self.pin_cmd, GPIO.LOW) # décharger le condensateur
        
        j = 0
        l_elapsed = []
        while j < n_moyenne + 2:
            
#             time.sleep(self.T_PAUSE_BETWEEN_MEASURES) # laisser du temps pour décharger le condo
            
            self.end_required = False
            measure_error = False
            GPIO.output(self.pin_cmd, GPIO.HIGH) # décharger le condo 
            time.sleep(self.PULSE_WIDTH)
            GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure 
            self.t_start_mesure = time.time() # déclancher le chrono il sera stoppé lors de l'interruption
            while not self.end_required: # tant que l'interruption n'a pas eu lieu
                if time.time() - self.t_start_mesure > self.T_TIMEOUT:
                    measure_error = True
                    self.end_required = True
                    print("pas de tension détectée sur l'entrée de mesure")
                    time.sleep(2)
#TODO: manage the miss of input voltage
            if not measure_error:
                if j > 1: # on ignore la première mesure car souvent trop faible (pourquoi ???)
                    elapsed = (self.t_end_mesure - self.t_start_mesure) - self.int_resp_time
                    l_elapsed.append(elapsed)
    #             time.sleep(self.T_PAUSE_BETWEEN_MEASURES)
                j += 1

        # filter the data list on the standard deviation 
        l_elaps_df = pd.DataFrame(l_elapsed, columns=list('B'))
        l_elaps_filtered = l_elaps_df[((l_elaps_df.B - l_elaps_df.B.mean()) / l_elaps_df.B.std()).abs() < self.filter]
        l_elaps_filtered_mean = l_elaps_filtered.B.mean()

        if show_histogram:
            i_min, u_min, i_max, u_max = self.calc_and_show_histogram(l_elapsed, n_moyenne)
            
        u_average = self.u_in_trig / (1 - math.exp(- l_elaps_filtered_mean / (self.R1 * self.C1)))
        if u_average < 0:
            print("elaps: " + '{:.1f}'.format(l_elaps_filtered_mean * 1000) + "ms tension: " + '{:.2f}'.format(u_average) + "V")
        return u_average, i_min, u_min, i_max, u_max

    def calc_and_show_histogram(self, l_elapsed, n_moyenne):
        
        # create ans show histogramm
        l_tension = []
        for v in l_elapsed:
            l_tension.append(self.u_in_trig / (1 - math.exp(- v / (self.R1 * self.C1))))
        u_min = 9999
        i_min = 0
        u_max = -9999
        i_max = 0
        for i, u in enumerate(l_tension):
            if u < u_min :
                u_min = u
                i_min = i
            if u > u_max:
                u_max = u
                i_max = i
#         print(str(i_min) + " - " + '{:.4}'.format(l_tension[i_min]), " / " + str(i_max) + " - " + '{:.4}'.format(l_tension[i_max]))
        
#         # filter the data
#         df1 = pd.DataFrame(l_tension, columns=list('B'))
#         l_tension_filtered = df1[((df1.B - df1.B.mean()) / df1.B.std()).abs() < self.filter]
#         l_tension_filtered_mean = l_tension_filtered.B.mean()
#     
#         # plot histogramm
#         n, bins, patches = plt.hist(x=l_tension, bins=min(int(n_moyenne/2),50), color='#0504aa', alpha=0.7, rwidth=0.85)
#         plt.hist(x=l_tension_filtered, bins=bins, color='#ffff00', alpha=0.7, rwidth=0.85)
#         plt.grid(axis='y', alpha=0.75)
#         plt.xlabel('Avg = ' + '{:.3f}'.format(l_tension_filtered_mean))
#         plt.ylabel('Frequency')
#         plt.title("Filtered on " + str(self.filter) + " standard deviation")
#         plt.text(23, 45, r'$\mu=15, b=3$')
#         maxfreq = n.max()
#         # Set a clean upper y-axis limit.
#         plt.ylim(ymax=np.ceil(maxfreq/10) *10 if maxfreq % 10 else maxfreq + 10)
#         # insert a legend
#         blue_patch = mpatches.Patch(color='#0504aa', label='excluded from the average')
#         yellow_patch = mpatches.Patch(color='#ffff00', label='included in average')
#         plt.legend(handles=[blue_patch, yellow_patch])

#         plt.show()
        return i_min, u_min, i_max, u_max

    def get_interrupt_latency(self):

        v_val = []
        i = 0
        n_measures = 200
        
        self.end_required = False
        GPIO.output(self.pin_cmd, GPIO.HIGH) 
        while i < n_measures:
            
#             time.sleep(self.T_PAUSE_BETWEEN_MEASURES) # laisser du temps pour décharger le condo
            
            GPIO.output(self.pin_cmd, GPIO.LOW) 
            t_start_mesure = time.time()
            while not self.end_required:
                pass
            elapsed = (self.t_end_mesure - t_start_mesure)
            GPIO.output(self.pin_cmd, GPIO.HIGH) 
            self.end_required = False
            v_val.append(elapsed)
            i += 1
        
        # filter the data list
        df = pd.DataFrame(v_val, columns=list('B'))
        val_filtered = df[((df.B - df.B.mean()) / df.B.std()).abs() < self.filter]
        # get the average of the filtered data list
        val_filtered_mean = val_filtered.B.mean()
        
        return val_filtered_mean
    
    def interrupt_management(self, channel):
        self.t_end_mesure = time.time()
        self.end_required = True

if __name__ == '__main__':

    #verify tension and filtering
    pidcmes = Pidcmes()
    print("pidcmes_lib start (it may take a few seconds)")
    
    v_stat_min = []
    v_stat_max = []
    n_passes = 2500
    
    for i in range(n_passes):
        u, i_min, u_min, i_max, u_max = pidcmes.get_tension(50, show_histogram = True)
        print("passe: " + '{:0>2d}'.format(i) + " : " + '{:.3f}'.format(u) + " -> " + '{:0>2d}'.format(i_min) + " - " + '{:.3f}'.format(u_min), \
              " / " + '{:0>2d}'.format(i_max) + " - " + '{:.3f}'.format(u_max))
        v_stat_min.append(i_min)
        v_stat_max.append(i_max)
    
#     v_stat_min = [1, 34, 35, 22, 5, 44, 38, 32, 26, 20, 14, 19, 24, 22, 12, 1, 34, 28, 45, 16, 10, 44, 3, 37, 39, 25, 24, 13, 7, 1, 40, 24, 1, 10, 4, 43, 47, 30, 13, 7, 22, 29, 34, 13, 43, 16, 23, 22, 37, 13, 42, 36, 29, 34, 28, 22, 16, 1, 29, 20, 14, 9, 30, 7, 5, 40, 2, 39, 28, 10, 23, 43, 2, 23, 15, 17, 20, 14, 10, 18, 0, 24, 2, 42, 5, 28, 36, 28, 9, 7, 38, 18, 21, 45, 18, 42, 29, 47, 9, 39, 33, 22, 12, 26, 48, 14, 34, 43, 45, 0, 44, 21, 12, 6, 13, 8, 1, 39, 37, 48, 33, 11, 19, 28, 19, 30, 16, 36, 15, 20, 11, 19, 13, 9, 13, 2, 46, 48, 43, 24, 40, 0, 33, 16, 47, 8, 32, 40, 0, 16, 32, 38, 45, 18, 6, 10, 19, 25, 14, 30, 11, 13, 25, 13, 39, 0, 17, 33, 48, 19, 45, 40, 11, 19, 43, 47, 6, 23, 6, 46, 14, 41, 1, 28, 40, 26, 8, 35, 36, 22, 25, 42, 13, 40, 22, 23, 9, 13, 40, 41]
#     v_stat_max = [21, 26, 44, 21, 17, 11, 39, 44, 20, 24, 26, 42, 5, 34, 20, 15, 1, 2, 5, 28, 31, 8, 11, 19, 43, 37, 8, 1, 37, 8, 18, 16, 28, 22, 16, 10, 45, 8, 25, 32, 13, 7, 24, 17, 0, 28, 39, 8, 21, 15, 9, 48, 7, 46, 41, 34, 10, 28, 2, 32, 39, 21, 33, 12, 13, 7, 40, 6, 46, 26, 36, 40, 20, 18, 16, 43, 42, 28, 16, 41, 2, 32, 7, 26, 6, 18, 48, 21, 35, 28, 39, 0, 25, 8, 41, 16, 41, 11, 14, 24, 44, 39, 0, 2, 42, 16, 48, 47, 19, 12, 22, 22, 33, 27, 0, 46, 44, 15, 47, 40, 6, 33, 28, 42, 31, 43, 28, 48, 27, 30, 26, 32, 25, 0, 48, 28, 24, 10, 20, 36, 0, 12, 9, 25, 4, 20, 36, 39, 29, 37, 9, 15, 2, 19, 45, 12, 29, 14, 26, 42, 1, 0, 9, 36, 0, 44, 36, 18, 15, 31, 15, 17, 6, 22, 20, 0, 47, 46, 7, 33, 26, 28, 24, 5, 8, 30, 20, 9, 18, 42, 0, 8, 5, 28, 8, 31, 0, 25, 21, 23]
#     v_stat_min = [2, 44, 1, 47, 8, 8, 24, 48, 9, 49, 23, 22, 23, 10, 13, 37, 11, 3, 18, 12, 48, 39, 13, 14, 27, 9, 45, 28, 27, 40, 29, 2, 4, 44, 10, 34, 3, 4, 10, 44, 5, 1, 32, 6, 46, 46, 7, 11, 41, 8, 35, 35, 21, 8, 48, 35, 9, 40, 36, 10, 9, 37, 37, 47, 4, 38, 14, 1, 26, 13, 18, 40, 34, 3, 26, 23, 40, 27, 1, 8, 28, 2, 45, 29, 3, 16, 43, 26, 4, 30, 31, 5, 4, 45, 32, 6, 12, 31, 5, 3, 32, 19, 6, 12, 1, 20, 7, 4, 47, 21, 8, 15, 48, 35, 9, 13, 49, 36, 10, 10, 32, 41, 3, 24, 11, 30, 9, 43, 4, 49, 23, 10, 16, 10, 23, 10, 46, 2, 37, 37, 24, 11, 24, 1, 43, 38, 25, 29, 2, 39, 39, 13, 26, 49, 4, 40, 35, 1, 34, 41, 28, 15, 19, 39, 39, 26, 26, 13, 22, 40, 17, 40, 40, 14, 1, 1, 17, 41, 28, 28, 28, 2, 2, 47, 5, 42, 29, 16, 3, 12, 9, 21, 9, 30, 30, 17, 4, 4, 29, 18]
#     v_stat_max = [48, 34, 37, 0, 22, 9, 42, 12, 23, 35, 37, 44, 47, 19, 39, 38, 44, 7, 0, 45, 0, 40, 14, 30, 28, 10, 41, 16, 36, 0, 0, 0, 0, 30, 36, 0, 31, 18, 0, 45, 38, 2, 46, 0, 23, 47, 46, 10, 35, 22, 0, 49, 35, 38, 49, 49, 49, 12, 37, 14, 0, 0, 25, 23, 0, 0, 23, 13, 4, 27, 38, 41, 0, 40, 14, 1, 0, 3, 13, 0, 42, 26, 35, 30, 39, 11, 7, 27, 48, 20, 32, 19, 41, 29, 33, 31, 45, 13, 0, 0, 46, 45, 17, 13, 0, 34, 21, 25, 42, 35, 0, 6, 49, 36, 10, 40, 0, 29, 24, 24, 0, 16, 0, 38, 25, 0, 43, 39, 0, 37, 32, 40, 19, 11, 11, 11, 27, 11, 0, 0, 15, 32, 0, 24, 0, 39, 0, 13, 29, 45, 40, 14, 1, 46, 30, 26, 36, 29, 22, 49, 42, 27, 0, 0, 36, 40, 27, 29, 9, 0, 0, 41, 41, 28, 15, 0, 0, 15, 42, 0, 22, 42, 0, 0, 43, 30, 47, 30, 39, 35, 23, 27, 0, 31, 44, 31, 31, 29, 0, 0]

    print(v_stat_min)
    # plot histogramm
    n, bins, patches = plt.hist(x=v_stat_min, bins=min(int(n_passes/2),50), color='#0504aa', alpha=0.7, rwidth=0.85)
    plt.hist(x=v_stat_min, bins=bins, color='#ffff00', alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    maxfreq = n.max()
    # Set a clean upper y-axis limit.
    plt.ylim(ymax=np.ceil(maxfreq/10) *10 if maxfreq % 10 else maxfreq + 10)
    # insert a legend
    plt.show()
    
    print(v_stat_max)
    # plot histogramm
    n, bins, patches = plt.hist(x=v_stat_max, bins=min(int(n_passes/2),50), color='#0504aa', alpha=0.7, rwidth=0.85)
    plt.hist(x=v_stat_max, bins=bins, color='#ffff00', alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    maxfreq = n.max()
    # Set a clean upper y-axis limit.
    plt.ylim(ymax=np.ceil(maxfreq/10) *10 if maxfreq % 10 else maxfreq + 10)
    # insert a legend
    plt.show()

    GPIO.cleanup()
        

