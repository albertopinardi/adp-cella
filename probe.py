#!/usr/bin/env python
import time
import sqlite3
import datetime
import RPi.GPIO as GPIO
import os

#Stato dei GPIO
#Attenzione PIN OUT BCM !!!
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24, GPIO.IN)
GPIO.setup(23, GPIO.IN)

base_dir = '/sys/bus/w1/devices/'
device_freezer = base_dir + '28-041633ae3bff'
device_frigor = base_dir + '28-800000040599'
path_freezer = device_freezer + '/w1_slave'
path_frigor = device_frigor + '/w1_slave'

#Identifico Directory del DB
wd = os.getcwd()
db_name = 'datalogger.db'
db_path = wd + db_name

#connessione al DB
conn = sqlite3.connect(db_path)
c = conn.cursor()
#abilito printout errori
sqlite3.enable_callback_tracebacks(True)

def read_temp_raw(pth1):
    f = open(pth1, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(pth):
    lines = read_temp_raw(pth)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(pth)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        #return temp_c, temp_f
        return temp_c

#Definizione Variabili
temp_sup_z = -1         #Intervallo di Allarme superiore Cella Freezer
temp_inf_z = -24
temp_sup_g = 100                #Intervallo di Allarme superiore Cella Frigor
temp_inf_g = 0
step = 1
ctrl = 0
while (step < 6):
    time_now = int(time.time())
    temp_c_z = read_temp(path_freezer)
    temp_c_g = read_temp(path_frigor)
    sfreezer = GPIO.input(24)
    sfrigor = GPIO.input(23)
    c.execute("INSERT INTO records(id, time , temp_freezer , temp_frigor , tens_freezer, tens_frigor) VALUES ( NULL,?,?,?,?,?)",(time_now, temp_c_z, temp_c_g, sfreezer, sfrigor))
    print("T° Freezer: ", temp_c_z,"T° Frigor: ", temp_c_g , "Ore: ", time.ctime(int(time_now)), "Corrente Freezer: ",sfreezer, "Corrente Frigor: ",sfrigor)
    print("Rilevazione n' : ", step )
    step += 1
print ("Ciclo terminato...")
GPIO.cleanup()
conn.commit()
conn.close()