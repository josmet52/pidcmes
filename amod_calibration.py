#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
# import math
# import numpy as np
# import matplotlib.pyplot as plt
# plt.ion()

# from lib.time_mesure_lib import Exec_time_mesurment
from amod_lib import Amod
amod = Amod("calibration")

R1 = 100E3
C1 = 1e-6

print("\nInstallez un pont entre la pin " + str(amod.pin_cmd) + " et la pin " + str(amod.pin_mes) \
      + " du RPI pour mesurer le temps de latence des interruptions")
v_ok = input("OK pour continuer")
v_min = 9999
v_max = -9999
xdata = []
ydata = []
t_avg = []

for i in range(5):
    latency_time = amod.get_response_time(show_histogram = False)
#     if latency_time > v_max: v_max = latency_time
#     if latency_time < v_min: v_min = latency_time
#     print(str(i) + " "'{:.1f}'.format(latency_time * 1e6) + " us" + " disp = " + str(int((v_max - v_min) * 1e6)) + " us")
#     xdata.append(i)
#     ydata.append(latency_time * 1e6)
#     amod.add_point(xdata, ydata)
    t_avg.append(latency_time)

print("\nRétablissez le schema normal")
print("Quelle est la tension mesurée sur la pin 3 du LM393? (défaut = 2.5)")
u_trig = 2.5
u_in = input("Enter pour continuer")
if u_in : u_trig = float(u_in)

print("\nparamètres de l'application amod")
print("--------------------------------")
print("temps de latence des interruptions = " + str(int(sum(t_avg) / len(t_avg) * 1e6)) + " [us]")
print("tension de référence = " + str(u_trig) + " [V]")
print("R1 = " + '{:.0f}'.format(R1 / 1e3) + " [k\u03A9]")
print("C1 = " + '{:.0f}'.format(C1 * 1e9) + " [nF]")
print("constante de temps de la mesure = " + '{:.0f}'.format(R1 * C1 * 1e3) + " [ms]")
    
with open('amod.ini', 'w') as ini_file:
#     ini_file.writelines(str(u_trig) + "," + str(R1) + "," + str(C1) + "," + str(latency_time))
    ini_file.writelines(str(u_trig) + "," + str(R1) + "," + str(C1) + "," + str(sum(t_avg) / len(t_avg)))

