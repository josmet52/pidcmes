#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
# import math
# import numpy as np
import matplotlib.pyplot as plt
plt.ion()

# from lib.time_mesure_lib import Exec_time_mesurment
from amod_lib import Amod
amod = Amod("calibration")
from gpiozero import LoadAverage

# print(str(int(LoadAverage(minutes=1).load_average*100))+"%")
print(LoadAverage.load_average)
R1 = 100E3
C1 = 100e-9

# print("Installez le pont entre la sortie et l'entrée pour la calibration du temps de répose des interruptions")
# v_ok = input("OK pour continuer")
v_min = 9999
v_max = -9999
xdata = []
ydata = []
t_avg = []

for i in range(10000):
    int_resp_time = amod.get_response_time(show_histogram = False)
    if int_resp_time > v_max: v_max = int_resp_time
    if int_resp_time < v_min: v_min = int_resp_time
    print(str(i) + " "'{:.1f}'.format(int_resp_time * 1e6) + " us" + " disp = " + str(int((v_max - v_min) * 1e6)) + " us")
#     print(amod.getCPUuse())
    xdata.append(i)
    ydata.append(int_resp_time * 1e6)
    amod.add_point(xdata, ydata)
    t_avg.append(int_resp_time)
    
print("t moyen = " + str(int(sum(t_avg) / len(t_avg) * 1e6)) + " [us]")

# print("Quelle est la tension mesurée sur la pin 5 du NE555? (défaut = 2.5)")
# u_trig = 2.98
# u_in = input()
# if u_in : u_trig = float(u_in)
#     
# with open('amod.ini', 'w') as ini_file:
#     ini_file.writelines(str(u_trig) + "," + str(R1) + "," + str(C1) + "," + str(int_resp_time))

