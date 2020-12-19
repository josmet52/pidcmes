#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import time
# import RPi.GPIO as GPIO
# import math
# import numpy as np
import matplotlib.pyplot as plt

# from lib.time_mesure_lib import Exec_time_mesurment
from amod_555_lib import Amod
amod = Amod("calibration")

R1 = 100E3
C1 = 1e-6

print("Installez le pont entre la sortie et l'entrée pour la calibration du temps de répose des interruptions")
v_ok = input()
int_resp_time = amod.get_response_time()
print('{:.1f}'.format(int_resp_time * 1e6) + " us")

print("Quelle est la tension mesurée sur la pin 5 du NE555? (défaut = 2.5)")
u_trig = 2.5
u_in = input()
if u_in : u_trig = float(u_in)
    
with open('amod_555.ini', 'w') as ini_file:
    ini_file.writelines(str(u_trig) + "," + str(R1) + "," + str(C1) + "," + str(int_resp_time))

