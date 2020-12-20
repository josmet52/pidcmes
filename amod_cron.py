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
    
    def __init__(self):
        
        self.pin_cmd = 8 # control pin
        self.pin_mes = 10 # measure pin
  
        self.u_in_trig = 2.5 # the input trigger level (depend on the harware)
        self.R1 = 100e3 # value of the resistor
        self.C1 = 1e-6 # value of the capacitor
        self.interrupt_latency = 5.1e-3 # interrupt response time

        self.pulse_width = 10e-6
        self.t_pause_between_mesures = 0.5e-3
        self.t_timeout = 1
        self.std_filter = 1.5 # +/- n ecart types gardés
        self.n_moyenne = 20
        
        self.end_requierd = False


        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin_cmd, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.pin_mes, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # initialize measure pi (attention no pull-up or pull-down)
        GPIO.add_event_detect(self.pin_mes, GPIO.FALLING, callback=self.interrupt_management) 
        GPIO.output(self.pin_cmd, GPIO.LOW)
        
    def get_tension(self):

        j = 0
        l_elapsed = []
        for j in range(self.n_moyenne):
            
            self.end_requierd = False
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la mesure (NE555 -> TRIG passe à 0)
            time.sleep(self.pulse_width)
            GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure (NE555 -> TRIG passe à 0)
            self.t_start_mesure = time.time() # déclancher le chrono
            while not self.end_requierd:
                if time.time() - self.t_start_mesure > self.t_timeout:
                    self.end_requierd = True
                    print("interruption manquée")
                    
            elapsed = (self.t_end_mesure - self.t_start_mesure) - self.interrupt_latency
            l_elapsed.append(elapsed)
            time.sleep(self.t_pause_between_mesures)
        GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la décharge du condensateur
        
        # get stats of data list
        nx, mmx, mx, vx, skx, ktx = stat.describe(l_elapsed)
        # filter the data list
        df = pd.DataFrame(l_elapsed, columns=list('B'))
        l_ref_filtered = df[((df.B - df.B.mean()) / df.B.std()).abs() < self.std_filter]
        l_ref_filtered_mean = l_ref_filtered.B.mean()
            
        u_average = self.u_in_trig / (1 - math.exp(- l_ref_filtered_mean / (self.R1 * self.C1)))
        return u_average

    
    def interrupt_management(self, channel):
        self.t_end_mesure = time.time()
        self.end_requierd = True
        
if __name__ == '__main__':

    amod = Amod() # initialize amode class

    u_bat_min = 3.4 # minumum battery voltage 

    u_avg = amod.get_tension() # read the value in volts
    
    if u_avg < u_bat_min:# or i > 10: 
        print("proper shut down of the machine due to low battery (" + '{:.2f}'.format(u_avg) + " [V])")
        time.sleep(5)
        call("sudo shutdown -h now", shell=True) # shutdown the RASPI
