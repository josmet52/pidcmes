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

import os
import time

from ina219 import INA219

from pidcmes_lib import Pidcmes  # class for 'pidcmes' procedures

if __name__ == '__main__':

    pidcmes = Pidcmes()  # initialize pidcmese class

    # parameters
    U_BAT_MIN = 3.7  # minumum battery voltage
    AVERAGING_ON = 10  # averaging to reduce glitches
    SHUNT_OHMS = 0.05

    ina = INA219(SHUNT_OHMS)
    ina.configure()

    app_dir = os.path.dirname(os.path.realpath(__file__))
    f_name = app_dir + "/ups_check.log"
    # print(app_dir + "/ups_check.log")

    i = 0
    while True:
        i += 1
        u_bus = ina.voltage()
        i_bus = ina.current()
        # while Pidcmes.in_run:
        #     time.sleep(0.2)
        u_avg, err_no, err_msg = pidcmes.get_tension(AVERAGING_ON)  # read the value in volts
        date_time = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime())
        data = ", ".join([err_msg, "->", date_time, '{:.3f}'.format(u_avg), '{:.3f}'.format(u_bus), '{:.3f}'.format(i_bus), "\n"])
        with open(f_name, 'a') as f:
            f.write(data)
        print(str(i) + " - " + data.replace("\n",""))
        time.sleep(10)





