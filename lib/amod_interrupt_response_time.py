#!/usr/bin/env python3
# -*-
"""
    class Cait  (calibrate the interrupt response time)
"""
import time
import RPi.GPIO as GPIO
import scipy.stats as stat
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

class Cirt:
    
    def __init__(self):
        
        self.pin_cmd = 38 # control pin
        self.pin_mes = 36 # measure pin
        
        self.t_start = 0
        self.end_ok = False
        self.n_moy = 50
        self.v_tol = 0.1 # 2.5 %
        self.v_val = []
        self.filter = 0.5 # +/- n ecart types gardés
  
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin_cmd, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.pin_mes, GPIO.IN)  # initialize measure pi (attention no pull-up or pull-down)
        GPIO.add_event_detect(self.pin_mes, GPIO.RISING, callback=self.end_reached) 
        GPIO.output(self.pin_cmd, GPIO.LOW) 
        
    def get_response_time(self, show_histogram = False):

        self.v_val.clear()
        i = 0
        while i < self.n_moy:
            time.sleep(10e-6)
            self.t_start = time.time()
            GPIO.output(self.pin_cmd, GPIO.HIGH) 
            while not self.end_ok:
                pass
            self.end_ok = False
            i += 1
        
        # get stats of data list
        nx, mmx, mx, vx, skx, ktx = stat.describe(self.v_val)
        # filter the data list
        df = pd.DataFrame(self.v_val, columns=list('B'))
        val_filtered = df[((df.B - df.B.mean()) / df.B.std()).abs() < self.filter]
        val_filtered_mean = val_filtered.B.mean()

        # create ans show histogramm
        if show_histogram:
        
            # plot histogramm
            n, bins, patches = plt.hist(x=self.v_val, bins=min(int(self.n_moy/4),50), color='#0504aa', alpha=0.7, rwidth=0.85)
            plt.hist(x=val_filtered, bins=bins, color='#ffff00', alpha=0.7, rwidth=0.85)
            plt.grid(axis='y', alpha=0.75)
            plt.xlabel('Avg = ' + '{:.3f}'.format(val_filtered_mean*1e3) + " ms")
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
            
        GPIO.cleanup()
        return val_filtered_mean
        
        
    def end_reached(self, channel):
        
        v = time.time() - self.t_start
        GPIO.output(self.pin_cmd, GPIO.LOW)
        self.v_val.append(v)
#         print('{:.2f}'.format(v * 1e3) + " ms")
        self.end_ok = True
        
if __name__ == '__main__':
    
    cirt = Cirt()
    resp_time = cirt.get_response_time(show_histogram = True)
    print('{:.3f}'.format(resp_time*1e3) + " ms")
    GPIO.cleanup()
