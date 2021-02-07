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
"""

import time
import RPi.GPIO as GPIO
import math


class Pidcmes:
    
    # initialize program constants
    PIN_CMD = 8  # control pin
    PIN_MES = 10  # measure pin
    TRIG_LEVEL = 2.5  # comparator reference voltage
    R1 = 100e3  # resistor value 100 k
    C1 = 1e-6  # condensator value 1 uF
    PULSE_WIDTH = 10e-3  # pulse width to discharge the condensator and trig the measure
    T_TIMEOUT = 10 * R1 * C1  # if no interruption after 10 R1*C1 time -> no tension on the measure pin
    FILTER = 1.5  # +/- filter on n standard deviation to exclude bad measurement

    def __init__(self):

        # initialisation GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.PIN_CMD, GPIO.OUT)  # initialize control pin                  
        GPIO.setup(self.PIN_MES, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # initialize measure pi (attention no pull-up or pull-down)
        GPIO.output(self.PIN_CMD, GPIO.LOW)

    def get_tension(self, n_for_mean):

        # verifiy the value of n_for_mean
        if n_for_mean < 2:  # n_for_mean must be greather than 1
            err = 2
            return 0, err

        l_elapsed = []
        err = 0

        # read the tension
        for dummy in range(n_for_mean):

            # trig the measure
            GPIO.output(self.PIN_CMD, GPIO.HIGH)  # discharge condensator
            time.sleep(Pidcmes.PULSE_WIDTH)
            GPIO.output(self.PIN_CMD, GPIO.LOW)  # start the measurement

            t_start_measure = time.time()  # start stopwatch
            # wait for GPIO.FALLING on pin 'PIN_MES'
            channel = GPIO.wait_for_edge(self.PIN_MES, GPIO.FALLING, timeout=int(Pidcmes.T_TIMEOUT * 1000))

            # GPIO.FALLING occurs
            if channel is not None:  # measure is ok
                elapsed = (time.time() - t_start_measure)
                l_elapsed.append(elapsed)
            else:  # timeout has occcured
                err = 1
                return 0, err

        # filter the data list on the standard deviation

        n = len(l_elapsed)  # number of measurements
        v_mean = sum(l_elapsed) / n  # mean value
        st_dev = math.sqrt(sum([(x - v_mean) ** 2 for x in l_elapsed]) / (n - 1))  # standard deviation

        # filter on max stdev = FILTER value
        l_elaps_f = [el for el in l_elapsed if abs((el - v_mean) / st_dev) <= Pidcmes.FILTER]
        l_elaps_f_mean = sum(l_elaps_f) / len(l_elaps_f)  # mean of elaps filtered

        # calculate  the tension
        u_average = Pidcmes.TRIG_LEVEL / (1 - math.exp(-l_elaps_f_mean / (Pidcmes.R1 * Pidcmes.C1)))
        return u_average, err


if __name__ == '__main__':

    # verify tension and filtering
    pidcmes = Pidcmes()
    n_for_mean = 10  # the greater this value, the longer the measurement takes
    u, err = pidcmes.get_tension(n_for_mean)
    if err == 0:  # the measurement is ok
        print("la tension sur l'entrée de mesure est de: " + '{:.2f}'.format(u) + " [V]")
    elif err == 1:  # no tesnion on the measure entry
        print("Pas de tension détectée sur l'entrée de mesure")
    elif err == 2:  # n_for_mean < 2
        print("la valeur de n_for_mean doit etre >= 2")
    GPIO.cleanup()
