#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import pdb
import pandas as pd
# import matplotlib
# matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import warnings
warnings.filterwarnings("ignore")


class Pidcmes:
        
    app_dir = os.path.dirname(os.path.realpath(__file__))
    pin_cmd = 8  # control pin
    pin_mes = 10  # measure pin
    # initialize program variables
    t_end_measure = 0.0  # value changed by interrupt_handling()
    interruption_occurred = False  # set to true by interrupt_handling()

    def __init__(self):

        # initialisation GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin_cmd, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.pin_mes, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # initialize measure pi (attention no pull-up or pull-down)
        GPIO.output(self.pin_cmd, GPIO.LOW)

        # read the ini data file
        with open("".join([self.app_dir, '/pidcmes.ini']), 'r') as ini_file:
            data = ini_file.readlines()
            params = data[0].split(",")
            self.U_TRIGGER = float(params[0])  # the input trigger level (depend on the harware)
            self.R1 = float(params[1])  # value of the resistor
            self.C1 = float(params[2])  # value of the capacitor

        # initialize program constants
        self.PULSE_WIDTH = 10e-3  # pulse width to discharge the condensator and trig the measure
        self.T_TIMEOUT = 10 * self.R1 * self.C1  # if no interruption after 10 tau -> no tension on the measure pin
        self.FILTER = 1.5  # +/- filter on n standard deviation

    def get_tension(self, n_moyenne, show_histogram=False, return_min_max=False):
        
        j = 0
        l_elapsed = []
        l_elaps_filtered = []
        n_dummy = 5
        # read the tension
        while j < n_moyenne + n_dummy:

            # trig the measure
            GPIO.output(self.pin_cmd, GPIO.HIGH)  # décharger le condo
            time.sleep(self.PULSE_WIDTH)
            GPIO.output(self.pin_cmd, GPIO.LOW)  # déclencher la mesure

            t_start_measure = time.time()  # start stopwatch
            # wait for GPIO.FALLING on pin 'pin_mes'
            channel = GPIO.wait_for_edge(self.pin_mes, GPIO.FALLING, timeout=int(self.T_TIMEOUT*1000))
            self.t_end_measure = time.time()  # stop stopwatch

            # GPIO.FALLING occurs
            if channel is None:  # timeout has occcured
                print("pas de tension détectée sur l'entrée de measure")
                time.sleep(2)
            else:  # measure is ok
                elapsed = (self.t_end_measure - t_start_measure)
                if elapsed > 0:
                    j += 1
                    if j > n_dummy:
                        l_elapsed.append(elapsed)
                else:
                    print("======= negative time error =========: ")
                    print("t_end:   " + str(self.t_end_measure))
                    print("t_start: " + str(t_start_measure))
                    print("t_end - t_start: " + str(self.t_end_measure - t_start_measure))
                    print("elapsed:" + str((self.t_end_measure - t_start_measure)))
                    pdb.set_trace()

        GPIO.output(self.pin_cmd, GPIO.LOW)  # décharger le condo

        # filter the data list on the standard deviation 
        l_elaps_df = pd.DataFrame(l_elapsed, columns=list('B'))
        l_elaps_filtered = l_elaps_df[((l_elaps_df.B - l_elaps_df.B.mean()) / l_elaps_df.B.std()).abs() < self.FILTER]
        l_elaps_filtered_mean = l_elaps_filtered.B.mean()

        u_average = self.U_TRIGGER / (1 - math.exp(- l_elaps_filtered_mean / (self.R1 * self.C1)))

        if show_histogram:
            self.calc_and_show_histogram(l_elapsed, n_moyenne)
        if return_min_max:
            i_min_u, u_min_u, i_max_u, u_max_u = self.get_min_max(l_elaps_filtered.B)
            return u_average, i_min_u, u_min_u, i_max_u, u_max_u
        else:
            return u_average

    def get_min_max(self, l_elapsed):

        l_tension = []
        for t_elaps in l_elapsed:
            l_tension.append(self.U_TRIGGER / (1 - math.exp(- t_elaps / (self.R1 * self.C1))))
        u_min_h = 9999
        i_min_h = 9999
        u_max_h = -9999
        i_max_h = -9999
        for i_h, u_h in enumerate(l_tension):
            if u_h < u_min_h:
                u_min_h = u_h
                i_min_h = i_h
            if u_h > u_max_h:
                u_max_h = u_h
                i_max_h = i_h
        return i_min_h, u_min_h, i_max_h, u_max_h

    def calc_and_show_histogram(self, l_elapsed, n_moyenne):

        # # create ans show histogramm
        l_tension = []
        for t_elaps in l_elapsed:
            l_tension.append(self.U_TRIGGER / (1 - math.exp(- t_elaps / (self.R1 * self.C1))))

        # filter the data
        df1 = pd.DataFrame(l_tension, columns=list('B'))
        l_tension_filtered = df1[((df1.B - df1.B.mean()) / df1.B.std()).abs() < self.FILTER]
        l_tension_filtered_mean = l_tension_filtered.B.mean()

        # plot histogramm
        n2, bins2, patches2 = plt.hist(x=l_tension, bins=min(int(n_moyenne/2), 50), color='#0504aa', alpha=0.7, rwidth=0.85)
        plt.hist(x=l_tension_filtered, bins=bins2, color='#ffff00', alpha=0.7, rwidth=0.85)
        plt.grid(axis='y', alpha=0.75)
        plt.xlabel('Avg = ' + '{:.3f}'.format(l_tension_filtered_mean))
        plt.ylabel('Frequency')
        plt.title("Filtered on " + str(self.FILTER) + " standard deviation")
        plt.text(23, 45, r'$\mu=15, b=3$')
        maxfreq_l = n2.max()
        # Set a clean upper y-axis limit.
        plt.ylim(ymax=np.ceil(maxfreq_l / 10) * 10 if maxfreq_l % 10 else maxfreq_l + 10)
        # insert a legend
        blue_patch = mpatches.Patch(color='#0504aa', label='excluded from the average')
        yellow_patch = mpatches.Patch(color='#ffff00', label='included in average')
        plt.legend(handles=[blue_patch, yellow_patch])

        plt.show()
        return


if __name__ == '__main__':

    # # verify tension and filtering
    pidcmes = Pidcmes()
    n_moyenne = 50
    pidcmes.get_tension(n_moyenne, show_histogram=True, return_min_max=False)
    GPIO.cleanup()
