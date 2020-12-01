#!/usr/bin/env python3
# -*-
"""
    class Amod to read analog tension on two digital pins
"""
import time
import RPi.GPIO as GPIO
import math
from lib.time_mesure_lib import Exec_time_mesurment
# import numpy as np
# import matplotlib.pyplot as plt

# from lib.time_mesure_lib import Exec_time_mesurment
from lib.amod_lib import Amod
    
if __name__ == '__main__':

    # etalonne le montage avec le RPI
    amod = Amod()
    while True:
        time.sleep(amod.t_discharge)
        GPIO.output(amod.pin_cmd, GPIO.LOW)
        time.sleep(0.25E-3)
#         with Exec_time_mesurment() as etm:  
#             while GPIO.input(amod.pin_mes) == GPIO.LOW:
#                 pass
#         t_elapsed = etm.interval  
        GPIO.output(amod.pin_cmd, GPIO.HIGH)
#         u_in = amod.u_in_trig / (1 - math.exp(-t_elapsed / (amod.R1 * amod.C1)))
#         print('{:.0f}'.format(t_elapsed*1E6) +  "us - U=" + '{:.3f}'.format(u_in))
    GPIO.cleanup()
        

