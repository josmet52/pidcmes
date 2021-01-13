#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pidcmes_calibration.py
author : jo metra
date : 07.01.2011
version : 1.0.0
maturity : 4 - beta

pidcmes = raspberry PI Direct Current MEaSurement

This program measures the interruption latency time of the Raspberry PI used and save 
the values of R1, C1, ref_voltage and interrupt_latency_time in the file pidcmes.ini
thus if the harware changes - modification of the value of electronic components
or use of another Raspberry PI model - the new values can be saved in the
'pidcmes.ini' file by this program

"""

# import the class Pidcmes and initialize it
from pidcmes_lib import Pidcmes

if __name__ == '__main__':
    
    pidcmes = Pidcmes("calibration")

    # Set the values of the measurement circuit
    # this values are from used components
    R1 = "100E3" # 100 kohms
    C1 = "1E-6" # 1 uF
    u_trig = "2.5" # LM336 characteristic

    #Start the latency interrupt time measurement
    print("CALIBRATION")
    print("-----------")
    print("Install a bridge between pin " + str(pidcmes.pin_cmd) + " and pin " + str(pidcmes.pin_mes) + " for the interrupt latency measurement")
    v_ok = input("ENTER to continue")
    print("\n... measurement in progress ... (it may take a few seconds)")

    # execute the latency _time measurement
    int_resp_time = pidcmes.get_interrupt_latency() - 1.1e-3
    # for the accuracy of the measurement, the latency must be reduced by 1.1 seconds on a Raspberry PI4 

    # print the results
    print("\nThe following values are saved in the pidcmes.ini file")
    print("--------------------------------------------------------")
    print("Reference voltage (LM336) = ", u_trig + " Volts")
    print("R1 = " + str(R1)+ " Ohms")
    print("C1 = " + str(C1) + " Farads")
    print("Interrupt latency = ", '{:.2f}'.format(int_resp_time * 1e3) + " milli seconds")
    print("\nRemember to remove the bridge between pin ".upper() + str(pidcmes.pin_cmd) + " and pin ".upper() + str(pidcmes.pin_mes))
    print("======================================================\n")

    with open("".join([pidcmes.app_dir, '/pidcmes.ini']), 'w') as ini_file:
        ini_file.writelines(u_trig + "," + R1 + "," + C1 + "," + '{:.6f}'.format(int_resp_time))
        
    print("Calibration completed")
