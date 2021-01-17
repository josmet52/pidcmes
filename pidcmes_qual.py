#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    class Pidcmes to
    - read analog tension on two digital pins
    - calibrate the sensor
    - plot the measured data's
"""
import time
# import matplotlib
# matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
from pidcmes_lib import Pidcmes


class Pidcmes_qual:

    def verify_quality(self, n_passes, n_moyenne):

        v_stat_min = []
        v_stat_max = []
        v_stat_avg = []
        v_stat_x = []

        mesure_each = 60

        for i in range(n_passes):
            sw_start = time.time()
            u, i_min, u_min, i_max, u_max = pidcmes.get_tension(n_moyenne, show_histogram=False, return_min_max=True)
            print("passe: " + '{:0>2d}'.format(i) + " -> UAVG:" + '{:.3f}'.format(u) + " / UMIN:"
                  + '{:0>2d}'.format(i_min) + "-" + '{:.3f}'.format(u_min) + " / UMAX:" + '{:0>2d}'.format(i_max)
                  + "-" + '{:.3f}'.format(u_max))
            v_stat_min.append(i_min)
            v_stat_max.append(i_max)
            v_stat_avg.append(u)
            v_stat_x.append(i)

            sw_sleep = mesure_each - (time.time() - sw_start)
            time.sleep(sw_sleep)

        u_avg = sum(v_stat_avg) / len(v_stat_avg)

        fig1, (ax10, ax11) = plt.subplots(1, 2, sharey=True)
        fig1.suptitle('Répartition des indices MIN et MAX \npour ' + str(n_passes)
                      + " passes et moyenne sur " + str(n_moyenne) + " mesures")

        ax10.set_title('MIN')
        ax10.set_xlim(0, n_moyenne)
        ax10.grid(axis='y', alpha=0.75)
        ax10.set_xlabel("Indice des mesures")
        ax10.hist(x=v_stat_min, bins=min(n_moyenne, 50), color='#ffd500', alpha=0.7, rwidth=0.85)

        ax11.set_title('MAX')
        ax11.set_xlim(0, n_moyenne)
        ax11.grid(axis='y', alpha=0.75)
        ax11.set_xlabel("Indice des mesures")
        ax11.hist(x=v_stat_max, bins=min(n_moyenne, 50), color='#0504aa', alpha=0.7, rwidth=0.85)

        plt.pause(2)

        fig2, (ax20, ax21) = plt.subplots(1, 2)
        fig2.suptitle('Variation de la tension \npour ' + str(n_passes)
                      + " passes et moyenne sur " + str(n_moyenne) + " mesures")

        ax20.set_title("Gaussienne des AVG")
        ax20.grid(axis='y', alpha=0.75)
        ax20.hist(x=v_stat_avg, bins=min(n_moyenne, 50), color='#aa1d04', alpha=0.7, rwidth=0.85)
        ax20.set_xlabel('U average = ' + '{:.3f}'.format(u_avg) + "V")
        ax20.set_ylabel("frequency")

        ax21.set_title("U = f(mesure no)")
        ax21.grid(axis='y', alpha=0.75)
        ax21.plot(v_stat_x, v_stat_avg, color='#041daa')
        ax21.set_xlabel("Mesure no")
        ax21.set_ylabel("Tension [V]")

        plt.pause(2)


if __name__ == '__main__':

    # verify tension and filtering
    pidcmes_qual = Pidcmes_qual()
    pidcmes = Pidcmes()
    n_passes = 600
    n_moyenne = 50
    print("pidcmes_qual start (n_passes=" + str(n_passes) + " n_moyenne=" + str(n_moyenne) + ")")
    pidcmes_qual.verify_quality(n_passes, n_moyenne)
    print("pidcmes_qual mesure terminée")

