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
matplotlib.use("TkAgg")
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
        self.PULSE_WIDTH = 1e-3 # pulse width to trig the measure and discharge the condensator
        self.T_PAUSE_BETWEEN_MEASURES = 1e-3 # sleep time between two measures
        self.T_TIMEOUT = 1 # if no interruption after t_timeout -> no tension on the measure pin
        self.filter = 1.5 # +/- filter on n standard deviation

        if from_who == "calibration": 
            GPIO.output(self.pin_cmd, GPIO.HIGH)
            
        else: # if not in calibration read the ini data file
            
            with open("".join([self.app_dir, '/pidcmes.ini']), 'r') as ini_file:
                data = ini_file.readlines()
                params = data[0].split(",")
                self.u_in_trig = float(params[0]) # the input trigger level (depend on the harware)
                self.R1 = float(params[1]) # value of the resistor
                self.C1 = float(params[2]) # value of the capacitor
                self.int_resp_time = float(params[3]) # interrupt response time
            
            GPIO.output(self.pin_cmd, GPIO.LOW)
                
            #Set up plot
            self.figure, self.ax = plt.subplots()
            self.lines, = self.ax.plot([],[], '-')
            #Autoscale on unknown axis and known lims on the other
            self.ax.set_autoscaley_on(True)
            self.ax.set_title("Battery charge and discharge monitoring")
            self.ax.set_ylabel("Tension [V]")

            # Format the x-axis for dates (label formatting, rotation)
            self.figure.autofmt_xdate(rotation=45)
            #Other stuff
            self.ax.grid()

    def add_point_on_graph(self, xdata, ydata):
        
        #Update data (with the new _and_ the old points)
        self.lines.set_xdata(xdata)
        self.lines.set_ydata(ydata)
        #Need both of these in order to rescale
        self.ax.relim()
        self.ax.autoscale_view()
        #We need to draw *and* flush
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        
    def get_tension(self, n_moyenne, show_histogram = False):

        GPIO.output(self.pin_cmd, GPIO.HIGH) # décharger le condensateur

        j = 0
        l_elapsed = []
        while j < n_moyenne:
            
            time.sleep(self.T_PAUSE_BETWEEN_MEASURES) # laisser du temps pour décharger le condo
            
            self.end_required = False
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la mesure (NE555 -> TRIG passe à 0)
            time.sleep(self.PULSE_WIDTH)
            GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure (NE555 -> TRIG passe à 0)
            self.t_start_mesure = time.time() # déclancher le chrono
            while not self.end_required:
                if time.time() - self.t_start_mesure > self.T_TIMEOUT:
                    self.end_required = True
                    print("interruption manquée")
#TODO: manage the miss of input voltage
                    
            elapsed = (self.t_end_mesure - self.t_start_mesure) - self.int_resp_time
            l_elapsed.append(elapsed)
            time.sleep(self.T_PAUSE_BETWEEN_MEASURES)
            j += 1

        # filter the data list on the standard deviation 
        l_elaps_df = pd.DataFrame(l_elapsed, columns=list('B'))
        l_elaps_filtered = l_elaps_df[((l_elaps_df.B - l_elaps_df.B.mean()) / l_elaps_df.B.std()).abs() < self.filter]
        l_elaps_filtered_mean = l_elaps_filtered.B.mean()

        if show_histogram:
            self.calc_and_show_histogram(l_elapsed, n_moyenne)
            
        u_average = self.u_in_trig / (1 - math.exp(- l_elaps_filtered_mean / (self.R1 * self.C1)))
        return u_average

    def calc_and_show_histogram(self, l_elapsed, n_moyenne):
        
        # create ans show histogramm
        l_tension = []
        for v in l_elapsed:
            l_tension.append(self.u_in_trig / (1 - math.exp(- v / (self.R1 * self.C1))))
        
        # filter the data
        df1 = pd.DataFrame(l_tension, columns=list('B'))
        l_tension_filtered = df1[((df1.B - df1.B.mean()) / df1.B.std()).abs() < self.filter]
        l_tension_filtered_mean = l_tension_filtered.B.mean()
    
        # plot histogramm
        n, bins, patches = plt.hist(x=l_tension, bins=min(int(n_moyenne/2),50), color='#0504aa', alpha=0.7, rwidth=0.85)
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
        blue_patch = mpatches.Patch(color='#0504aa', label='excluded from the average')
        yellow_patch = mpatches.Patch(color='#ffff00', label='included in average')
        plt.legend(handles=[blue_patch, yellow_patch])

        plt.show()
            

    def get_interrupt_latency(self):

        v_val = []
        i = 0
        n_measures = 200
        
        self.end_required = False
        GPIO.output(self.pin_cmd, GPIO.HIGH) 
        while i < n_measures:
            
            time.sleep(self.T_PAUSE_BETWEEN_MEASURES) # laisser du temps pour décharger le condo
            
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
    a = pidcmes.get_tension(20, show_histogram = True)
    GPIO.cleanup()

        

