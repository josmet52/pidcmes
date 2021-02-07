#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program returns the voltage applied to the input of the measurement circuit
"""

import time
from pidcmes_lib import Pidcmes  # class for 'pidcmes' procedures

if __name__ == '__main__':

    pidcmes = Pidcmes()  # initialize pidcmese class

    # parameters
    AVERAGING_ON = 5  # averaging to reduce glitches

    # take the measurement
    u, err = pidcmes.get_tension(AVERAGING_ON)

    # check if errors
    if err == 0: # no error
        print("la tension sur l'entrée de mesure est de: " + '{:.2f}'.format(u) + " [V]")
    elif err == 1: # no tesnion on the measure entry
        print("Pas de tension détectée sur l'entrée de mesure")
    elif err == 2: # n_moyenne < 2
        print("la valeur de n_moyenne doit etre >= 2")
