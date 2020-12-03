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

n_passe = 5000
n_moy = 200
# t_discharge = 0.05E-3


val = []
n = 0

str_title = "AMOD : moy=" + str(n_moy) + " pass=" + str(n_passe) + " R1=" + str(int(amod.R1/1E3)) + "k C1=" + str(int(amod.C1*1E9)) + "nF"
print("mesure démarrée")
amod.get_tension(n_moy)
while n < n_passe:
    n += 1
    u_avg = amod.get_tension(n_moy)
    str_2_print = str(n) + " -> " + '{:.2f}'.format(u_avg)  
    print(str_2_print)
    val.append(u_avg)

GPIO.cleanup()

# i = 0
# prt_str = ""
# hist, bin_edges = np.histogram(val)
# for edge in bin_edges:
#     if i < len(hist):
#         prt_str += "  -" + str(edge) + " - " + str(hist[i])
#     else:
#         prt_str += "  -" + str(edge) + " - " 
#     i += 1
# print(prt_str)
#     
# print(max(hist),hist)
# print(bin_edges)
# 
# valid_data_index = []
# for i, v in enumerate(hist):
#     if v >= max(hist)/100:
#         valid_data_index.append(i)
# print(valid_data_index)
# val_min = bin_edges[valid_data_index[0]]
# val_max = bin_edges[valid_data_index[-1]]
# 
# 
# filtred_data = []
# for v in val:
#     if v > val_min and v < val_max:
#         filtred_data.append(v)
    
    
    
    
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

