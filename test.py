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
# from lib.mysql_amod_lib import Mysql_amod

class Amod:
    
    def __init__(self):
        
        # version infos
        VERSION_NO = "0.01.01" 
        VERSION_DATE = "27.11.2020"
        VERSION_DESCRIPTION = "prototype"
        VERSION_STATUS = "initial version"
        VERSION_AUTEUR = "josmet"

        self.pin_cmd = 18 # pin de commande
        self.pin_mes = 16 # pin de mesure
  
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin_cmd, GPIO.OUT)  # la pin 23 est une sortie numérique                  
        GPIO.setup(self.pin_mes, GPIO.IN)  # la pin 25 est une entrée numérique

        self.t_discharge = 0.15E-3 # donner un bref instant pour assurer la déchrge du condensateur
        self.u_sat_mosfet = 0#10E-3 # pour tenir compte de la tension de saturation V_DS du MOSFET

        with open('amod.ini', 'r') as ini_file:
            data = ini_file.readlines()
            params = data[0].split(",")
            self.u_in_trig = float(params[0])
            self.R1 = float(params[1])
            self.C1 = float(params[2])
    
if __name__ == '__main__':

    # etalonne le montage avec le RPI
    amod = Amod()
    while True:
        time.sleep(amod.t_discharge)
        GPIO.output(amod.pin_cmd, GPIO.LOW)    
        with Exec_time_mesurment() as etm:  
            while GPIO.input(amod.pin_mes) == GPIO.LOW:
                pass
        t_elapsed = etm.interval  
        GPIO.output(amod.pin_cmd, GPIO.HIGH)
#         u_in = amod.u_in_trig / (1 - math.exp(-t_elapsed / (amod.R1 * amod.C1)))
#         print('{:.0f}'.format(t_elapsed*1E6) +  "us - U=" + '{:.3f}'.format(u_in))
        

