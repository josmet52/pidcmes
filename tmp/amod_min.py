#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import call

from lib.mysql_amod_lib import Mysql_amod
from lib.amod_lib import Amod

mysql_amod = Mysql_amod()
mysql_amod = Mysql_amod('192.168.1.139') # initialize mysql class with server IP adress 
sql_txt = "DELETE FROM tlog;" # delete all datas in tlog table
mysql_amod.execute_sql(sql_txt) 

amod = Amod()

print("mesure démarrée")

stop_run = False
u_min = 3.2

while not stop_run:

    u_avg = amod.get_tension(n_moy)
    sql_txt = " ".join(["INSERT INTO tlog (mes_value) VALUES (", str(u_avg), ")"]) # save it in the database
    mysql_amod.execute_sql(sql_txt)

    print('{:.2f}'.format(u_avg))

    if u_avg < u_min:
        stop_run = True
        
    if stop_run:
        call("sudo shutdown -h now", shell=True) # shutdown the RASPI
        