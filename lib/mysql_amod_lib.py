#!/usr/bin/env python3
# -*-
"""
    class Mysql to manage de db access for the programm analog-mesure-on-digital-pin
"""
import socket
import sys
import tkinter as tk
import mysql.connector


class Mysql_amod:

    def __init__(self, ip_db_server):
        
        # version infos
        VERSION_NO = "0.01.01" 
        VERSION_DATE = "27.11.2020"
        VERSION_DESCRIPTION = "prototype"
        VERSION_STATUS = "initial version"
        VERSION_AUTEUR = "josmet"
        
        self.database_username = "pi"  # YOUR MYSQL USERNAME, USUALLY ROOT
        self.database_password = "mablonde"  # YOUR MYSQL PASSWORD
        self.database_name = "amod"  # YOUR DATABASE NAME
        self.host_name = "localhost"
        self.server_ip = ip_db_server
        self.record = ""
        # get the local IP adress
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.local_ip = s.getsockname()[0]
        s.close()
        # calculate the delay time before retray connection
        ip_s = str(self.local_ip)
        self.delay_time = int(ip_s[-1:])*2 # delay time is different if the ip is differnet so less conflicts
        if self.delay_time == 0 : self.delay_time = 10
        # print(self.delay_time)
        # verify the db connection
        con, e = self.get_db_connection()
        if not con:
            print("analog-mesure-on-digital-pin : _init_ -> DB UNEXPECTED ERROR\n" + str(e[0]), "/", str(e[1]), "/", str(e[2]) + "\nLe programme va s'arrêter")
            msg = "".join(["ERROR " + str(e[0]), "/ ", str(e[1]), "/ ", str(e[2]) + "Le programme va s'arrêter"])
            tk.messagebox.showerror("mysql_lib_logger ERROR", msg)
            print("DB UNEXPECTED ERROR", msg)
            sys.exit()
            
    def get_db_connection(self):
        
        # verify if the mysql server is ok and the db avaliable
        try:
            if self.local_ip == self.server_ip: # if we are on the RPI with mysql server (RPI making temp acquis)
                # test the local database connection
                con = mysql.connector.connect(user=self.database_username, password=self.database_password, host=self.host_name, database=self.database_name)
            else:
                # test the distant database connection
                con = mysql.connector.connect(user=self.database_username, password=self.database_password, host=self.server_ip, database=self.database_name)
            return con, sys.exc_info()
        
        except:
            # return error
            return False, sys.exc_info()
# 
#     def add_record(self, value_to_record):
#         db_connection, err = self.get_db_connection()
#         db_cursor = db_connection.cursor()
#         sql_txt = " ".join(["INSERT INTO tlog (mes_value) VALUES (", str(value_to_record), ")"])
#         db_cursor.execute(sql_txt)
#         db_connection.commit()
#         db_cursor.close()
#         db_connection.close()
# 
#     def delete_all_records(self):
#         db_connection, err = self.get_db_connection()
#         db_cursor = db_connection.cursor()
#         sql_txt = "DELETE FROM tlog;"
#         db_cursor.execute(sql_txt)
#         db_connection.commit()
#         db_cursor.close()
#         db_connection.close()

    def execute_sql(self, sql_txt):
        db_connection, err = self.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(sql_txt)
        db_connection.commit()
        db_cursor.close()
        db_connection.close()
        
    def get_all_measures(self):
        db_connection, err = self.get_db_connection()
        db_cursor = db_connection.cursor()
        sql_txt = "SELECT mes_value FROM tlog;"
        db_cursor.execute(sql_txt)
        row = db_cursor.fetchall()
        db_cursor.close()
        db_connection.close()
        return row
        
    def get_data(self, sql_txt):
        db_connection, err = self.get_db_connection()
        db_cursor = db_connection.cursor()
        db_cursor.execute(sql_txt)
        row = db_cursor.fetchall()
        db_cursor.close()
        db_connection.close()
        return row
        


if __name__ == '__main__':

    db_server_ip = '192.168.1.139'
    mysql_init = Mysql_amod(db_server_ip)
    ip  = mysql_init.local_ip
    connection = mysql_init.get_db_connection()
    
    # verify connection
    if connection:
        print("connected on db server on",db_server_ip)
