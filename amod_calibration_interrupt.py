#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import time
# import RPi.GPIO as GPIO
# import math
# import numpy as np
import matplotlib.pyplot as plt

# from lib.time_mesure_lib import Exec_time_mesurment
from lib.amod_interrupt_lib import Amod
from lib.amod_interrupt_response_time import Cirt

R1 = 100E3
C1 = 1e-6
n_moyenne = 20

print("Installez le pont entre la sortie et l'entrée pour la calibration du temps de répose des interruptions")
v_ok = input()
cirt = Cirt()
int_resp_time = cirt.get_response_time()
print(int_resp_time)

print("Rétablissez le schéma normal")
v_ok = input()

# xx = 5.1e-3
amod = Amod("calibration")
print("Quelle est la tension appliquée ?")
u_in = float(input())
u_trig = amod.set_param(u_in, R1, C1, n_moyenne, int_resp_time)
print("u_trig = " + str(u_trig))

