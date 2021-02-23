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
              3 -> not enought measures for st_dev
              99 -> another error

    **** BE CAREFUL : ONE APP FOR ONE HARWARE ****
"""

import math
import time
import RPi.GPIO as GPIO
import linecache
import sys
from subprocess import call
from ina219 import INA219


class Pidcmes:

    def __init__(self):

        # initialize program constants
        self.PIN_CMD = 8  # control pin
        self.PIN_MES = 10  # measure pin
        self.TRIG_LEVEL = 2.5  # comparator reference voltage
        self.R1 = 100e3  # resistor value 100 k ohms
        self.C1 = 1e-6  # condensator value 1 uF
        self.PULSE_WIDTH = 10e-3  # pulse width to discharge the condensator and trig the measure
        self.T_TIMEOUT = 1000 * 10 * self.R1 * self.C1  # if no interruption after 10*R1*C1 time -> no tension on the measure pin
        self.FILTER = 1.5  # +/- filter on n standard deviation to exclude bad measurement

        # initialisation GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.PIN_CMD, GPIO.OUT)  # initialize control pin
        GPIO.setup(self.PIN_MES, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.output(self.PIN_CMD, GPIO.LOW)

    def get_tension(self, n_for_mean):

        try:
            # verifiy the value of n_for_mean
            if n_for_mean < 2:  # n_for_mean must be greather than 1
                err_no = 2
                err_msg = "n_for_mean must be greather than 1"
                return 0, err_no, err_msg

            l_elapsed = []
            err_no = 0
            err_msg = "Measure ok"

            for dummy in range(n_for_mean):

                # trig the measure
                GPIO.output(self.PIN_CMD, GPIO.HIGH)  # discharge condensator
                time.sleep(self.PULSE_WIDTH)
                GPIO.output(self.PIN_CMD, GPIO.LOW)  # start the measurement

                t_start_measure = time.time()  # start stopwatch
                # wait for GPIO.FALLING on pin 'PIN_MES'
                channel = GPIO.wait_for_edge(self.PIN_MES, GPIO.FALLING, timeout=int(self.T_TIMEOUT))
                # GPIO.FALLING occurs
                if channel is not None:  # measure is ok
                    elapsed = (time.time() - t_start_measure)
                    l_elapsed.append(elapsed)
                else:  # timeout has occcured
                    err_no = 1
                    err_msg = "timeout has occured"
                    return 0, err_no, err_msg

            # filter the data list on the standard deviation

            n = len(l_elapsed)  # number of measurements
            v_mean = sum(l_elapsed) / n  # mean value
            st_dev = math.sqrt(sum([(x - v_mean) ** 2 for x in l_elapsed]) / (n - 1))  # standard deviation
            if st_dev == 0:
                err_no = 3
                err_msg = "not enought measures for st_dev -> no filtering applied"
                return v_mean, err_no, err_msg

            # filter on max stdev = FILTER value
            l_elaps_f = [el for el in l_elapsed if abs((el - v_mean) / st_dev) <= self.FILTER]
            l_elaps_f_mean = sum(l_elaps_f) / len(l_elaps_f)  # mean of elaps filtered

            # calculate  the tension
            u_average = self.TRIG_LEVEL / (1 - math.exp(-l_elaps_f_mean / (self.R1 * self.C1)))
            return u_average, err_no, err_msg

        except Exception as error:
            filename, lineno, line, exc_obj = PrintException()
            return 0, '', 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

def PrintException():

    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    # print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    return filename, lineno, line, exc_obj

if __name__ == '__main__':

    pidcmes = Pidcmes()  # initialize pidcmese class

    # parameters
    U_BAT_MIN = 3.7  # minumum battery voltage
    AVERAGING_ON = 10  # averaging to reduce glitches
    SHUNT_OHMS = 0.05

    # initialize INA
    ina = INA219(SHUNT_OHMS)
    ina.configure()

    u_avg, err_no, err_msg = pidcmes.get_tension(AVERAGING_ON)  # read the value in volts
    u_bus = ina.voltage()
    # check if errors
    date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
    str_status = " / ".join([" -> bat:%.2f[V]" % u_avg, "bus:%.2f[V]" % ina.voltage(), "crt:%.0f[mA]" % ina.current()])
    if err_no == 0:  # no error
        if u_avg < U_BAT_MIN:  # or i > 10:
            print("".join([date_time, " -> controlled PI shut down due to a low battery !", str_status]))
            time.sleep(5)
            print("now stop the PI")
            # to active the real shutdown uncomment the next line
            call("sudo shutdown -h now", shell=True)  # shutdown the RASPI
        else:
            print("".join([date_time, " -> all is calm sleep good people!", str_status]))

    elif err_no == 1:  # no voltage on the measure entry
        print("".join([date_time, " -> no voltage detected on the measurement input", str_status]))
    elif err_no == 2:  # n_moyenne < 2
        print("".join([date_time, " -> The value of AVERAGING_ON must be> = 2", str_status]))
    else:
        print(" ".join([date_time, err_msg]))

    GPIO.cleanup()
