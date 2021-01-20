#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    class Pidcmes to
    - read analog tension on two digital pins
    - calibrate the sensor
    - plot the measured data's
"""
import time
from datetime import datetime
from statistics import stdev, mean
import os
# import matplotlib
# matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pidcmes_lib import Pidcmes
import warnings
warnings.filterwarnings("ignore")


class PidcmesQual:

    @staticmethod
    def verify_quality(n_passe, n_moyenne, n_dummy, graph_dir):

        v_stat_min = []
        v_stat_max = []
        v_stat_avg = []
        v_stat_x = []

        mesure_each = 1

        for i in range(n_passe):
            sw_start = time.time()
            u, i_min, u_min, i_max, u_max = pidcmes.get_tension(n_moyenne, n_dummy=0, 
                                            show_histogram=False, return_min_max=True)
            print("passe: " + '{:0>2d}'.format(i) + " -> UAVG:" + '{:.3f}'.format(u) + " / UMIN:"
                  + '{:0>2d}'.format(i_min) + "-" + '{:.3f}'.format(u_min) + " / UMAX:" 
                  + '{:0>2d}'.format(i_max) + "-" + '{:.3f}'.format(u_max))
            v_stat_min.append(i_min)
            v_stat_max.append(i_max)
            v_stat_avg.append(u)
            v_stat_x.append(i)

            sw_sleep = max(0, mesure_each - int(time.time() - sw_start))
            time.sleep(sw_sleep)

        u_avg = sum(v_stat_avg) / len(v_stat_avg)

        fig1, (ax10, ax11, ax20, ax21) = plt.subplots(4)
        fig1.set_size_inches(10, 12)
        plt.gcf().subplots_adjust(hspace=0.25)

        fig1.suptitle('Analyse de qualité pour pass:' + str(n_passe)
                      + " moy:" + str(n_passe) + " dummy: " + str(n_dummy))

        ax10.set_title('MIN')
        ax10.set_xlim(0, n_moyenne)
        ax10.grid(axis='y', alpha=0.75)
        # ax10.set_xlabel("Indice des mesures")
        ax10.hist(x=v_stat_min, bins=min(n_passe, 50), color='#b39500', alpha=0.7, rwidth=0.85)

        ax11.set_title('MAX')
        ax11.set_xlim(0, n_moyenne)
        ax11.grid(axis='y', alpha=0.75)
        # ax11.set_xlabel("Indice des mesures")
        ax11.hist(x=v_stat_max, bins=min(n_passe, 50), color='#0504aa', alpha=0.7, rwidth=0.85)

        ax21.set_title("U=f(no)")
        ax21.grid(axis='y', alpha=0.75)
        ax21.plot(v_stat_x, v_stat_avg, color='#041daa')
        # ax21.set_xlabel("Mesure no")
        ax21.set_ylabel("Tension [V]")

        avg_legend_txt = "mean=" + '{:.3f}'.format(mean(v_stat_avg))  + "V +/-" + '{:.4f}'.format(stdev(v_stat_avg))
        avg_legend = mpatches.Patch(color='#aa1d04', label=avg_legend_txt)
        ax20.set_title("AVG")
        ax20.grid(axis='y', alpha=0.75)
        ax20.hist(x=v_stat_avg, bins=min(n_passe, 50), color='#04aa05', alpha=0.7, rwidth=0.85)
        # ax20.set_xlabel('U average = ' + '{:.3f}'.format(u_avg) + "V")

        ax20.legend(handles=[avg_legend])
        ax20.set_ylabel("frequency")

        # plt.pause(2)
        graph_file_name = graph_dir + "/" \
                          + "pidcmes qual -> passes:" + str(n_passe) \
                          + " moyenne:" + str(n_moyenne) \
                          + " dummy:" + str(n_dummy)\
                          + ".png"
        fig1.savefig(graph_file_name)

    @staticmethod
    def for_next_step(start, end, step):
        while start <= end:
            yield start
            start += step


if __name__ == '__main__':

    # verify tension and filtering
    PidcmesQual = PidcmesQual()
    pidcmes = Pidcmes()
    # n_passe = 600
    # n_moyenne = 5
    # n_dummy = 0

    graph_dir = pidcmes.app_dir + "/graph"
    filelist = [f for f in os.listdir(graph_dir)]
    for f in filelist:
        os.remove(os.path.join(graph_dir, f))

    for n_dummy in PidcmesQual.for_next_step(0, 10, 2):
        # print("n_dummy:", n_dummy)
        for n_moyenne in PidcmesQual.for_next_step(5, 50, 5):
            # print("n_moyenne:", n_moyenne)
            for n_passe in PidcmesQual.for_next_step(10, 100, 10):
                # print("passe:", n_passe)
                current_dt = datetime.now().strftime("%d.%m.%y %H:%M:%S")
                prt_str = "\n" + current_dt + " -> PidcmesQual pass (n_passes=" + str(n_passe) \
                          + " n_moyenne=" + str(n_moyenne) + " n_dummy=" + str(n_dummy) + ")"
                print(prt_str)
                print("="*(len(prt_str)-1))
                PidcmesQual.verify_quality(n_passe, n_moyenne, n_dummy, graph_dir)

    print("PidcmesQual mesure terminée")
