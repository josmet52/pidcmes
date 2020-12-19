#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

"""
import time
import RPi.GPIO as GPIO
import math
import scipy.stats as stat
import pandas as pd
import datetime as dt

from subprocess import call


class Amod:
    
    def __init__(self, from_who = ""):
        
        self.pin_cmd = 8 # control pin
        self.pin_mes = 10 # measure pin
  
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin_cmd, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.pin_mes, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # initialize measure pi (attention no pull-up or pull-down)
        GPIO.add_event_detect(self.pin_mes, GPIO.FALLING, callback=self.interrupt_management) 
        GPIO.output(self.pin_cmd, GPIO.LOW)

        with open('amod_cron.ini', 'r') as ini_file:
            data = ini_file.readlines()
            params = data[0].split(",")
            self.u_in_trig = float(params[0]) # the input trigger level (depend on the harware)
            self.R1 = float(params[1]) # value of the resistor
            self.C1 = float(params[2]) # value of the capacitor
            self.int_resp_time = float(params[3]) # interrupt response time
        
    def get_tension(self, n_moyenne, show_histogram = False):

        GPIO.output(self.pin_cmd, GPIO.HIGH) # décharger le condensateur
        
        pulse_width = 10e-6
        t_pause_between_mesures = 0.5e-3
        t_timeout = 1
        std_filter = 1.5 # +/- n ecart types gardés

        j = 0
        l_elapsed = []
        while j < n_moyenne:
            
            time.sleep(t_pause_between_mesures) # laisser du temps pour décharger le condo
            
            self.end_requierd = False
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la mesure (NE555 -> TRIG passe à 0)
            time.sleep(pulse_width)
            GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure (NE555 -> TRIG passe à 0)
            self.t_start_mesure = time.time() # déclancher le chrono
            while not self.end_requierd:
                if time.time() - self.t_start_mesure > t_timeout:
                    self.end_requierd = True
                    print("interruption manquée")
                    
            elapsed = (self.t_end_mesure - self.t_start_mesure) - self.int_resp_time
            l_elapsed.append(elapsed)
            time.sleep(t_pause_between_mesures)
            j += 1
#             print(j)
        GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la décharge du condensateur
        
        # get stats of data list
        nx, mmx, mx, vx, skx, ktx = stat.describe(l_elapsed)
        # filter the data list
        df = pd.DataFrame(l_elapsed, columns=list('B'))
        l_ref_filtered = df[((df.B - df.B.mean()) / df.B.std()).abs() < std_filter]
        l_ref_filtered_mean = l_ref_filtered.B.mean()

        # create ans show histogramm
        if show_histogram:
            l_tension = []
            for v in l_elapsed:
                l_tension.append(self.u_in_trig / (1 - math.exp(- v / (self.R1 * self.C1))) - self.VCEsat)
                
            df1 = pd.DataFrame(l_tension, columns=list('B'))
            l_tension_filtered = df1[((df1.B - df1.B.mean()) / df1.B.std()).abs() < std_filter]
            l_tension_filtered_mean = l_tension_filtered.B.mean()
        
            # plot histogramm
            n, bins, patches = plt.hist(x=l_tension, bins=min(int(n_moyenne/2),50), color='#0504aa', alpha=0.7, rwidth=0.85)
            plt.hist(x=l_tension_filtered, bins=bins, color='#ffff00', alpha=0.7, rwidth=0.85)
            plt.grid(axis='y', alpha=0.75)
            plt.xlabel('Avg = ' + '{:.3f}'.format(l_tension_filtered_mean))
            plt.ylabel('Frequency')
            plt.title("Filtered on " + str(std_filter) + " standard deviation")
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

    
    def interrupt_management(self, channel):
        self.t_end_mesure = time.time()
        self.end_requierd = True
        
if __name__ == '__main__':

    amod = Amod() # initialize amode class

    u_bat_min = 3.4 # minumum battery voltage 
    n_moy = 20 # averaging to reduce glitches
    t_sleep = 2 # sleep time between two mesurements
    stop_run = False # to control the execution (run/stop)

    u_avg = amod.get_tension(n_moy) # read the value in volts
    
    if u_avg < u_bat_min:# or i > 10: 
        print("proper shut down of the machine due to low battery (" + '{:.2f}'.format(u_avg) + " [V])")
        time.sleep(5)
#         call("sudo shutdown -h now", shell=True) # shutdown the RASPI
