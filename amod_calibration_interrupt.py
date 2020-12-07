#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import time
# import RPi.GPIO as GPIO
# import math
# import numpy as np
import matplotlib.pyplot as plt

# from lib.time_mesure_lib import Exec_time_mesurment
from lib.amod_interrupt_lib import Amod
R1 = 100E3
C1 = 100E-9
n_moyenne = 500

amod = Amod("calibration")
print("Quelle est la tension appliquée ?")
u_in = float(input())
u_trig = amod.set_param(u_in, R1, C1, n_moyenne)
print("u_trig = " + str(u_trig))

