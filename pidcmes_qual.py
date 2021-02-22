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
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pidcmes_lib import Pidcmes
import warnings
warnings.filterwarnings("ignore")


class PidcmesQual:

    @staticmethod
    def verify_quality(n_passe, n_moyenne, n_dummy, graph_dir, mesure_each, n_essai):

        essai_min = []
        essai_max = []
        essai_avg = []
        essai_no = []

        for essai in range(n_essai):

            txt = "\npidcmes qual -> essai: " + str(essai)
            print(txt)
            print("-"*len(txt))

            v_stat_min = []
            v_stat_max = []
            v_stat_avg = []
            v_stat_x = []

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

            # fig1, (ax10, ax20, ax21) = plt.subplots(3)
            # fig1.set_size_inches(10, 12)
            # plt.gcf().subplots_adjust(hspace=0.5)
            #
            # fig1.suptitle('Analyse de qualité pour pass:' + str(n_passe)
            #               + " moy:" + str(n_moyenne) + " dummy: " + str(n_dummy))
            #
            # min_legend = mpatches.Patch(color='#aa0504', label="MIN")
            # max_legend = mpatches.Patch(color='#0504aa', label="MAX")
            # ax10.legend(handles=[min_legend, max_legend])
            # ax10.set_title('Indice des mesures MIN et MAX dans la moyenne')
            # ax10.set_xlabel("Indice de la mesure")
            # ax10.grid(axis='y', alpha=0.75)
            # ax10.set_xlim(0, n_moyenne - 1)
            # ax10.hist(x=[v_stat_min, v_stat_max], color=['#aa0504', '#0504aa'], rwidth=0.85,
            #           bins=min(n_moyenne - 1, 50))
            #
            # avg_legend_txt = "mean=" + '{:.3f}'.format(mean(v_stat_avg)) + "V +/- " + '{:.1f}'.format(
            #     stdev(v_stat_avg) * 1000) + " mV"
            # avg_legend = mpatches.Patch(color='#04aa05', label=avg_legend_txt)
            # ax20.legend(handles=[avg_legend])
            # ax20.set_ylabel("frequency")
            # ax20.set_title("Histogramme de la tension moyenne de chaque passe")
            # ax20.grid(axis='y', alpha=0.75)
            # ax20.hist(x=v_stat_avg, color='#04aa05', alpha=0.7, rwidth=0.85)
            # ax20.set_xlabel('Tension [V]')
            #
            # ax21.set_title("U=f(no passe)(filtered)")
            # ax21.grid(axis='y', alpha=0.75)
            # ax21.plot(v_stat_x, v_stat_avg, color='#041daa')
            # ax21.set_ylabel("Tension [V]")
            # ax21.set_xlabel("Passe no")
            # ax21.set_xlim(0, n_passe - 1)

            # plt.pause(2)
            # graph_file_name = graph_dir + "/" \
            #                   + "pidcmes qual -> essai: " + str(n_essai) \
            #                   + "-" + str(n_passe) \
            #                   + "-" + str(n_moyenne) \
            #                   + "-" + str(n_dummy) \
            #                   + ".png"

            # fig1.savefig(graph_file_name)

            essai_min.append(min(v_stat_avg))
            essai_max.append(max(v_stat_avg))
            essai_avg.append(sum(v_stat_avg)/len(v_stat_avg))
            essai_no.append(essai)

        plt.plot(essai_no, essai_min, label="MIN")
        plt.plot(essai_no, essai_max, label="MAX")
        plt.plot(essai_no, essai_avg, label="AVG")
        plt.legend(loc='best')
        plt.grid(True)
        plt.xlabel("essai no")
        plt.ylabel("tension [V]")
        plt.title("pidcmes: passes=" + str(n_passe)
                  + " moyenne=" + str(n_moyenne)
                  + " dummy=" + str(n_dummy)
                  + " interval=" + str(mesure_each))
        plt.show()


    @staticmethod
    def for_next_step(start, end, step):
        while start <= end:
            yield start
            start += step


if __name__ == '__main__':

    # verify tension and filtering
    PidcmesQual = PidcmesQual()
    pidcmes = Pidcmes()

    graph_dir = pidcmes.app_dir + "/graph_essai"
    filelist = [f for f in os.listdir(graph_dir)]
    for f in filelist:
        os.remove(os.path.join(graph_dir, f))

    mesure_each = 5 #10
    n_essai = 100 #100
    n_passe = 20 #25
    n_moyenne = 5
    n_dummy = 0
    current_dt = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    prt_str = "\nessai no: " + str(n_essai) + " -> " + current_dt + " -> PidcmesQual pass (n_passes=" + str(n_passe) \
              + " n_moyenne=" + str(n_moyenne) + " n_dummy=" + str(n_dummy) + ")"
    # print(prt_str)
    # print("=" * (len(prt_str) - 1))
    PidcmesQual.verify_quality(n_passe, n_moyenne, n_dummy, graph_dir, mesure_each, n_essai)

    # for n_moyenne in PidcmesQual.for_next_step(5, 50, 5):
    #     for n_dummy in PidcmesQual.for_next_step(0, 5, 1):
    #         current_dt = datetime.now().strftime("%d.%m.%y %H:%M:%S")
    #         prt_str = "\n" + current_dt + " -> PidcmesQual pass (n_passes=" + str(n_passe) \
    #                   + " n_moyenne=" + str(n_moyenne) + " n_dummy=" + str(n_dummy) + ")"
    #         print(prt_str)
    #         print("=" * (len(prt_str) - 1))
    #         PidcmesQual.verify_quality(n_passe, n_moyenne, n_dummy, graph_dir, mesure_each)

    print("PidcmesQual mesure terminée")
