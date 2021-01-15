#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program is run at regular intervals to check the battery charge status of the uninterruptible power supply.
In our case, it is a LiPo battery with a nominal voltage of 3.7 volts. By setting the voltage for the
Raspberry PI shutdown procedure at 3.7 V,we ensure that the processor has enough time to make a clean shutdown.

This program must be launched at regular intervals (5 inute in our case) by the Raspberry PI OS cron task scheduler.
The crontab -e command in the home directory opens the cron file and the command line would for example be for a trigger every 5 minutes:
5 * * * * sudo /usr/bin/python3 /home/pi/dev_python/amod/pidcmes_bbu.py
"""

import time
# import datetime as dt


from subprocess import call
from pidcmes_lib import Pidcmes  # class for 'pidcmes' procedures

if __name__ == '__main__':
        
    pidcmes = Pidcmes()  # initialize pidcmese class

    # parameters
    U_BAT_MIN = 3.7  # minumum battery voltage
    AVERAGING_ON = 20  # averaging to reduce glitches

    # internal variables
    stop_run = False  # to control the execution (run/stop)

    u_avg = pidcmes.get_tension(AVERAGING_ON)  # read the value in volts
        
    if u_avg < U_BAT_MIN:  # or i > 10:
        print("proper shut down of the machine due to low battery")
        time.sleep(5)
        call("sudo shutdown -h now", shell=True)  # shutdown the RASPI
    else:
        print("... all is well sleep good people ...!")
