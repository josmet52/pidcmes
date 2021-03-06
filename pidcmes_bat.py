#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pidcmes_bbu.py
==============
author : Joseph Metrailler
date : 07.02.2021
status : prototype
version : 1.0
This program should be run at regular intervals to check the battery charge status of the
uninterruptible power supply. In our case, it is a LiPo battery with a nominal voltage of
3.7 volts. By setting the voltage for the Raspberry PI shutdown procedure at 3.7 V,we ensure
that the processor has enough time to make a clean shutdown.
This program must be launched at regular intervals by the Raspberry PI OS cron task scheduler.
The command
    sudo crontab -e
in the pi_user home directory opens the cron file and the command line would be, for example,
for a trigger every 5 minutes:
    */5 * * * * /usr/bin/python3 /home/pi/dev_python/pidcmes/pidcmes_bbu.py 2>&1
"""

import time

from subprocess import call
from pidcmes_lib import Pidcmes  # class for 'pidcmes' procedures

if __name__ == '__main__':

    pidcmes = Pidcmes()  # initialize pidcmese class

    # parameters
    U_BAT_MIN = 3.7  # minumum battery voltage
    AVERAGING_ON = 10  # averaging to reduce glitches

    u_avg, err, msg = pidcmes.get_tension(AVERAGING_ON)  # read the value in volts
    # check if errors
    date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
    str_status = "bat = %.2f[V]" % u_avg
    if err == 0:  # no error
        if u_avg < U_BAT_MIN:  # or i > 10:
            print("".join([date_time, " - ", str_status, " -> controlled PI shut down due to a low battery!"]))
            time.sleep(5)
            print("now stop the PI")
            # to active the real shutdown uncomment the next line
#             call("sudo shutdown -h now", shell=True)  # shutdown the RASPI
        else:
            print("".join([(date_time), " - ", str_status, " -> all is calm sleep good people!"]))
    elif err == 1:  # no voltage on the measure entry
        print("".join([(date_time), " - bat = -.-- no voltage detected on the measurement input"]))
    elif err == 2:  # n_moyenne < 2
        print("".join([(date_time), " - bat = -.-- the value of AVERAGING_ON must be bigger or equal to 2"]))

