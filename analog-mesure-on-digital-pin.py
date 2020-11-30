#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
import math
import numpy as np
import matplotlib.pyplot as plt

from lib.time_mesure_lib import Exec_time_mesurment
# from lib.mysql_amod_lib import Mysql_amod
from lib.amod_lib import Amod

# mysql_amod = Mysql_amod('192.168.1.139')
# sql_txt = "DELETE FROM tlog;"
# mysql_amod.execute_sql(sql_txt)
# amod.delete_all_records()
  
GPIO.setmode(GPIO.BCM)

pin_cmd = 23
pin_mes = 25

GPIO.setwarnings(False)

GPIO.setup(pin_cmd, GPIO.OUT)                    # broche 12 est une entree numerique
GPIO.setup(pin_mes, GPIO.IN)                   # broche 12 est une sortie numerique

print("mesure started")
GPIO.output(pin_cmd, GPIO.HIGH)

n_moy = 50
n_passe = 100
t_discharge = 0.1E-3

v_offset = 0.01
v_trigger = 1.51

R1 = 100E3
C1 = 10E-9
T = R1 * C1
val = []
n = 0

str_title = "AMOD : moy=" + str(n_moy) + " pass=" + str(n_passe) + " t_discharge=" + str(t_discharge * 1E3) + " ms"
while n < n_passe:
    n += 1
    i = 1
    t_avg = 0
    u_avg = 0
    n_err = 0
    while i <= n_moy:
        
        time.sleep(t_discharge) # pour décharger le condo
        GPIO.output(pin_cmd, GPIO.LOW)
        
        with Exec_time_mesurment() as etm:  
            while GPIO.input(pin_mes) == GPIO.LOW:
                pass
        t_elapsed = etm.interval  
        
        GPIO.output(pin_cmd, GPIO.HIGH)
        
        u_inst = v_offset + ((v_trigger - v_offset) / (1 - math.exp(-round(t_elapsed/T,4))))
        if u_inst < 5 and u_inst > 3:
            u_avg += u_inst  #v_offset + ((v_trigger - v_offset) / (1 - math.exp(-round(t_elapsed/T,4)))) 
            t_avg += t_elapsed
            i += 1
        else:
            n_err += 1
        
    t_avg = round(t_avg / n_moy, 6)
    u_avg = round(u_avg / n_moy, 3)
    val.append(u_avg)
    
#     sql_txt = " ".join(["INSERT INTO tlog (mes_value) VALUES (", str(u_avg), ")"])
#     mysql_amod.execute_sql(sql_txt)
    
    str_2_print = str(n) + " -> t mes = " + '{:.2f}'.format(t_avg * 1E6) + \
        "us / u = " + '{:.3f}'.format(u_avg) + " V / n err = " + str(n_err)
    print(str_2_print)

# values = amod.get_all_measures()
# val = []
# for v in values:
#     for vv in v:
#         val.append(vv)

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
    
# print(hist)
# print(bin_edges)

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
