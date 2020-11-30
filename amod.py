#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
import pigpio
import math
import numpy as np
import matplotlib.pyplot as plt

from lib.time_mesure_lib import Exec_time_mesurment
from lib.amod_lib import Amod

amod = Amod()

n_passe = 1000
n_moy = 2000
t_discharge = 0.15E-3

val = []
n = 0

str_title = "AMOD : moy=" + str(n_moy) + " pass=" + str(n_passe) + " t_discharge=" + str(t_discharge * 1E3) + " ms"
amod.get_tension(n_moy)
while n < n_passe:
    n += 1
    u_avg = amod.get_tension(n_moy)
    str_2_print = str(n) + " -> " + '{:.3f}'.format(u_avg)  
    print(str_2_print)
    val.append(u_avg)

GPIO.cleanup()

# An "interface" to matplotlib.axes.Axes.hist() method
n, bins, patches = plt.hist(x=val, bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
plt.grid(axis='y', alpha=0.75)
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title(str_title)
plt.text(23, 45, r'$\mu=15, b=3$')
maxfreq = n.max()
# Set a clean upper y-axis limit.
plt.ylim(ymax=np.ceil(maxfreq/10) *10 if maxfreq % 10 else maxfreq + 10)
plt.show()

