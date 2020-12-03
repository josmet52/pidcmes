#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import time
# import RPi.GPIO as GPIO
# import math
# import numpy as np
import matplotlib.pyplot as plt

# from lib.time_mesure_lib import Exec_time_mesurment
from lib.amod_lib import Amod

amod = Amod("etalonnage")
u_trig = amod.set_param(u_in=4.082, R1=100E3, C1=100E-9, n_moyenne=500)
print("u_trig = " + str(u_trig))

