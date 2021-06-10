#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    class Pidcmes
    =============
    Measure an analog voltage using two digital pins.
    The measuring range starts just above the reference voltage and can go up to more than 10V.
    The lower the voltage measured, the longer the measurement takes

    Constants : PIN_CMD -> control pin
                PIN_MES -> measure pin
                TRIG_LEVEL -> comparator refenre voltage
                R1 -> resistor of RC circuit for time measurement
                C1 -> condensator of RC circuit for time measurement
                PULSE_WIDTH -> duration of the condensator discharge pulse
                T_TIMEOUT -> after this this the measure is stopedd because no tension on the measurement pins
                FILTER -> standard deviation accepted for good measurement

    Errors :  0 -> measurement is ok
              1 -> no tension on the measure pin
              2 -> n_for_mean < 2
              3 -> not enought measure for st_dev
"""

import time
import datetime
import RPi.GPIO as GPIO
import math
import os
import matplotlib.pyplot as plt


class Pidcmes:
    # in_run = False

    def __init__(self):
        # initialize program constants
        self.PIN_CMD = 8  # control pin
        self.PIN_MES = 10  # measure pin
        self.TRIG_LEVEL = 2.5  # comparator reference voltage
        self.R1 = 100e3  # resistor value 100 k
        self.C1 = 1e-6  # condensator value 1 uF
        self.PULSE_WIDTH = 10e-3  # pulse width to discharge the condensator and trig the measure
        self.T_TIMEOUT = 10 * self.R1 * self.C1  # if no interruption after 10 R1*C1 time -> no tension on the measure pin
        self.FILTER = 1.5  # +/- filter on n standard deviation to exclude bad measurement
        self.app_dir = os.getcwd()

        # initialisation GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.PIN_CMD, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.PIN_MES, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # initialize measure pi (attention no pull-up or pull-down)
        GPIO.output(self.PIN_CMD, GPIO.LOW)

    def get_tension(self, n_mean):

        # verifiy the value of n_mean
        if n_mean < 2:  # n_mean must be greather than 1
            err = 2
            e_msg = "n_mean must be greather than 1"
            return 0, err, e_msg

        l_elapsed = []
        err = 0
        e_msg = "measure ok"

        # read the tension
        for dummy in range(n_mean):

            # trig the measure
            GPIO.output(self.PIN_CMD, GPIO.HIGH)  # discharge condensator
            time.sleep(self.PULSE_WIDTH)
            GPIO.output(self.PIN_CMD, GPIO.LOW)  # start the measurement

            t_start_measure = time.time()  # start stopwatch
            # wait for GPIO.FALLING on pin 'PIN_MES'
            channel = GPIO.wait_for_edge(self.PIN_MES, GPIO.FALLING, timeout=int(self.T_TIMEOUT * 2000))
            # GPIO.FALLING occurs
            if channel is not None:  # measure is ok
                elapsed = (time.time() - t_start_measure)
                l_elapsed.append(elapsed)
            else:  # timeout has occcured
                # pdb.set_trace()
                err = 1
                e_msg = "timeout has occured"
                return 0, err, e_msg

        # Pidcmes.in_run = False
        # filter the data list on the standard deviation

        n = len(l_elapsed)  # number of measurements
        v_mean = sum(l_elapsed) / n  # mean value
        st_dev = math.sqrt(sum([(x - v_mean) ** 2 for x in l_elapsed]) / (n - 1))  # standard deviation
        if st_dev == 0:
            return v_mean, 0, e_msg

        # filter on max stdev = FILTER value
        l_elaps_f = [el for el in l_elapsed if abs((el - v_mean) / st_dev) <= self.FILTER]
        l_elaps_f_mean = sum(l_elaps_f) / len(l_elaps_f)  # mean of elaps filtered

        # calculate  the tension
        u_average = self.TRIG_LEVEL / (1 - math.exp(-l_elaps_f_mean / (self.R1 * self.C1)))
        return u_average, err, e_msg


if __name__ == '__main__':

    # verify tension and filtering
    pidcmes = Pidcmes()
    n_passes = 360
    n_for_mean = 10
    pause_time = 10
    
    i = 0
    data_umin = []
    data_u = []
    data_umax = []
    data_no = []
    
    while i < n_passes:
        
        t = time.time()
        u_min = 999
        u_max = -999
        current_time = datetime.datetime.now()
        u, err_no, err_msg = pidcmes.get_tension(n_for_mean)
        u = int(u * 1000) / 1000
        
        if u < u_min: u_min = u
        if u > u_max: u_max = u
        
        if err_no == 0:  # the measurement is ok
            
            data_umin.append(u_min)
            data_u.append(u)
            data_umax.append(u_max)
            data_no.append(i)
            
            msg = " ".join([str(i), '- ', current_time.strftime("%b %d %Y %H:%M:%S"), '-> ',
                            "u_min=", '{:.2f}'.format(u_min),
                            "u_mes=", '{:.2f}'.format(u),
                            "u_max=", '{:.2f}'.format(u_max),
                            ])
            print(msg)
            i += 1
        elif err_no == 1:  # no tension on the measure entry
            print(err_msg + " -> " + "Pas de tension détectée sur l'entrée de mesure")
        elif err_no == 2:  # n_for_mean < 2
            print(err_msg + " -> " + "la valeur de n_for_mean doit etre >= 2")
        elapsed = time.time() - t
        time.sleep(pause_time - elapsed)
            
    plt.plot(data_no, data_umin, label="MIN")
    plt.plot(data_no, data_u, label="VAL")
    plt.plot(data_no, data_umax, label="MAX")
    plt.legend(loc='best')
    plt.grid(True)
    plt.xlabel("essai no")
    plt.ylabel("tension [V]")
#         plt.title("pidcmes: passes=" + str(n_passe)
#                   + " moyenne=" + str(n_moyenne)
#                   + " dummy=" + str(n_dummy)
#                   + " interval=" + str(mesure_each))
    plt.title("pidcmes mesure de la stabilité")
    plt.show()
    
#     print(data_umin)
#     print(data_u)
#     print(data_umax)
    GPIO.cleanup()
