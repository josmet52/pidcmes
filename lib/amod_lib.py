#!/usr/bin/env python3
# -*-
"""
    class Amod to read analog tension on two digital pins
"""
import time
import RPi.GPIO as GPIO
import math
# import numpy as np
# import matplotlib.pyplot as plt

from lib.time_mesure_lib import Exec_time_mesurment
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

        with open('amod.ini', 'r') as ini_file:
            data = ini_file.readlines()
            params = data[0].split(",")
            self.u_in_trig = float(params[0])
            self.R1 = float(params[1])
            self.C1 = float(params[2])
        
    def get_tension(self, n_moyenne):

        GPIO.output(self.pin_cmd, GPIO.HIGH)

        i = 0
        t_elapsed_average = 0
        
        while i < n_moyenne:
            
            time.sleep(self.t_discharge) # pour décharger le condo
            with Exec_time_mesurment() as etm:  
                GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
                while GPIO.input(self.pin_mes) == GPIO.LOW:
                    pass
            t_elapsed_average += etm.interval  
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
            i += 1
            
        t_elapsed = t_elapsed_average / n_moyenne
        u_average = self.u_in_trig / (1 - math.exp(-t_elapsed / (self.R1 * self.C1)))
        
        return u_average
        
    def set_param(self, u_in, R1, C1, n_moyenne):

        GPIO.output(self.pin_cmd, GPIO.HIGH)

        i = 1
        t_elapsed_average = 0
        
        while i <= n_moyenne:
            
            time.sleep(self.t_discharge) # pour décharger le condo
            with Exec_time_mesurment() as etm:  
                GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
                while GPIO.input(self.pin_mes) == GPIO.LOW:
                    pass
            t_elapsed_average += etm.interval  
            GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
            i += 1
            
        t_elapsed = t_elapsed_average / n_moyenne
        u_trig_calc = u_in * (1 - math.exp(-t_elapsed / (R1 * C1)))

        with open('amod.ini', 'w') as ini_file:
            ini_file.writelines(str(u_trig_calc) + "," + str(R1) + "," + str(C1))

        return u_trig_calc
    
#     def set_param(self, u_in, R1, C1, n_moy):
# 
#         GPIO.output(self.pin_cmd, GPIO.HIGH)
# 
#         i = 1
#         u_avg = 0
#         
#         while i <= n_moy:
#             
#             time.sleep(self.t_discharge) # pour décharger le condo
#             GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
#             
#             with Exec_time_mesurment() as etm:  
#                 while GPIO.input(self.pin_mes) == GPIO.LOW:
#                     pass
#             t_elapsed = etm.interval  
#             
#             GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
#             
# #             u_trig_calc = self.u_sat_mosfet + ((u_in - self.u_sat_mosfet) * (1 - math.exp(-t_elapsed / (R1 * C1))))
#             u_trig_calc = u_in * (1 - math.exp(-t_elapsed / (R1 * C1)))
#             u_avg += u_trig_calc   
#             i += 1
#             
#         u_avg = u_avg / n_moy
# 
#         with open('amod.ini', 'w') as ini_file:
#             ini_file.writelines(str(u_avg) + "," + str(R1) + "," + str(C1))
# 
#         return u_avg
#     
#         
#     def get_tension_old(self, n_moyenne):
# 
#         GPIO.output(self.pin_cmd, GPIO.HIGH)
# 
#         i = 1
#         u_average = 0
#         
#         while i <= n_moyenne:
#             
#             time.sleep(self.t_discharge) # pour décharger le condo
#             GPIO.output(self.pin_cmd, GPIO.LOW) # déclancher la mesure
#             
#             with Exec_time_mesurment() as etm:  
#                 while GPIO.input(self.pin_mes) == GPIO.LOW:
#                     pass
#             t_elapsed = etm.interval  
#             
#             GPIO.output(self.pin_cmd, GPIO.HIGH) # déclancher la décharge du condensateur
#             
# #             u_mesure = self.u_sat_mosfet + ((self.u_in_trig - self.u_sat_mosfet) / (1 - math.exp(-t_elapsed / (self.R1 * self.C1))))
#             u_average += self.u_in_trig / (1 - math.exp(-t_elapsed / (self.R1 * self.C1)))
# #             u_average += u_mesure  
#             i += 1
#             
#         u_average = u_average / n_moyenne
#         
#         return u_average

# if __name__ == '__main__':
# 
#     # etalonne le montage avec le RPI
#     amod = Amod()
#     u_trig = amod.set_param(5, 100E3, 10E-9, 100)
#     print("u_trig = " + str(u_trig))
#     # vérifie la mesure
#     amod = Amod()
#     u_mes = amod.get_tension(100)
#     print("u_mes = " + str(u_mes))
    
