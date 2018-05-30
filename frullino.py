#!/usr/bin/env python
import os
import glob
import time
import gammu
import sys
import sqlite3
import datetime
import smtplib
#Definizione Testo Mail di invio
#Messaggio mancanza corrente
message_c = """From: Allarme Cella Amici del Peru' <allarme-adp@fastmail.it>
MIME-Version: 1.0
Content-type: text/html
To: Volontari
Subject: Allarme Mancanza Tensione Cella {}
<HTML>
Attenzione intervenire il prima possibile!!!
</HTML>
"""
#Messaggio raggiungimento soglia Temperatura
message_t = """From: Allarme Cella Amici del Peru' <allarme-adp@fastmail.it>
MIME-Version: 1.0
Content-type: text/html
To: Volontari
Subject: Allarme Temperatura Cella {}
<HTML>
Attenzione intervenire il prima possibile!!!
Temperatura in Cella : {}
</HTML>
"""
#Indicazione percrso di lettura delle sonde
base_dir = '/sys/bus/w1/devices/'
device_freezer = base_dir + '28-041633ae3bff'
device_frigor = base_dir + '28-800000040599'
path_freezer = device_freezer + '/w1_slave'
path_frigor = device_frigor + '/w1_slave'

#Stato dei GPIO
#Attenzione PIN OUT BCM !!!
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24, GPIO.IN)
GPIO.setup(23, GPIO.IN)

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
        return temp_c

def sms_alarm_temp( num, cella, temp):
        sm = gammu.StateMachine()
        sm.ReadConfig()
        sm.Init()
        message = {
                'Text': 'Attenzione!!! Allarme Cella {cella}. Temperatura attuale : {temp}',
                'SMSC': {'Location': 1},
                'Number': num,
        }
        sm.SendSMS(message)

def sms_alarm_tens( num, cella ):
        sm = gammu.StateMachine()
        sm.ReadConfig()
        sm.Init()
        message = {
               'Text': 'Attenzione!!! Allarme Mancanza Tensione Cella {cella}',
               'SMSC': {'Location': 1},
               'Number': num,
        }
        sm.SendSMS(message)

def stampa_stdout():
        print("T° Freezer: ", temp_c_z,"T° Frigor: ", temp_c_g , "Ore: ", time.ctime(int(time_now)), "Corrente Freezer: ",sfreezer, "Corrente Frigor: ",sfrigor)


def push_records_db():
        c.execute("INSERT INTO records(id, time , temp_freezer , temp_frigor , tens_freezer, tens_frigor) VALUES ( NULL,?,?,?,?,?)",(time_now, temp_c_z, temp_c_g, sfreezer, sfrigor))


#Allarmi SMS per DB
sms_tens = "Attenzione!!! Allarme Tensione Cella {}}"
sms_temp = "Attenzione!!! Allarme Cella {} - {}"

#Definizione Variabili
temp_sup_z = -5         #Intervallo di Allarme superiore Cella Freezer
temp_inf_z = -30        #Intervallo inferiore Freezer
temp_sup_g = 100        #Intervallo di Allarme superiore Cella Frigor
temp_inf_g = -100          #Intervallo inferiore Frigor
#Lista numeri da contattare
list_sms = ['+393406694374','+393394483981','+393342457975']
sender = 'allarme-adp@fastmail.it'
receivers = ['alberto@fastmail.it']
step = 1
ctrl = 0
type_e = "email"
type_s = "sms"
#Fine definizione
while (step < 6):
        time_now = int(time.time())
        temp_c_z = read_temp(path_freezer)
        temp_c_g = read_temp(path_frigor)
        sfreezer = GPIO.input(24)
        sfrigor = GPIO.input(23)
        stampa_stdout
        print("Rilevazione n' : ", step )
        step += 1
        if ((temp_c_z >= temp_inf_z) & (temp_c_z <= temp_sup_z) & sfreezer & sfrigor & (temp_c_g >= temp_inf_g) & (temp_c_g <= temp_sup_g)):
                push_records_db
        elif not sfreezer:
                print("---!!!Allarme Tensione Rilevato in Cella Freezer!!!---")
                push_records_db
                rid = c.lastrowid
                if not (ctrl) :
                        for dest_addr in receivers:
                                try:
                                        smtpObj = smtplib.SMTP('localhost')
                                        smtpObj.sendmail(sender, dest_addr, (message_c.format("Freezer")))
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e, dest_addr,(message_c.format("Freezer"))))
                                        print "e-mail Inviata a {}".format(dest_addr)
                                except smtplib.SMTPException:
                                        print "e-mail NON Inviata a {}".format(dest_addr)
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e, dest_addr,smtplib.SMTPException) )
                        ctrl = 1
                        for dest_sms in list_sms:
                                try:
                                        sms_alarm_tens(dest_sms,'Freezer')
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,sms_tens) )
                                        print "SMS Inviato a {}".format(dest_sms)
                                except gammu.GSMError:
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,"Errore di connessione"))
                                        print "SMS NON Inviato a {}".format(dest_sms)
        elif not sfrigor:
                print("---!!!Allarme Tensione Rilevato in Cella Frigor!!!---")
                push_records_db
                rid = c.lastrowid
                if not (ctrl) :
                        for dest_addr in receivers:
                                try:
                                        smtpObj = smtplib.SMTP('localhost')
                                        smtpObj.sendmail(sender, dest_addr, (message_c.format("Frigor")))
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e,dest_addr,(message_c.format("Frigor"))) )
                                        print "e-mail Inviata a {}".format(dest_addr)
                                except smtplib.SMTPException:
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e,dest_addr,smtplib.SMTPException) )
                                        print "e-mail NON Inviata a {}".format(dest_addr)
                        ctrl = 1
                        for dest_sms in list_sms:
                                try:
                                        sms_alarm_tens(dest_sms,'Frigor')
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,sms_tens) )
                                        print "SMS Inviato a {}".format(dest_sms)
                                except gammu.GSMError:
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,"Conn. err."))
                                        print "SMS NON Inviato a {}".format(dest_sms)
        elif not (temp_c_z >= temp_inf_z):
                print("---!!!Allarme Temperatura Troppo Bassa Rilevata in Cella Freezer!!!---")
                push_records_db
                rid = c.lastrowid
                if not (ctrl) :
                        for dest_addr in receivers:
                                try:
                                        smtpObj = smtplib.SMTP('localhost')
                                        smtpObj.sendmail(sender, receivers, (message_t.format(cella='Freezer', temp=temp_c_z)))
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e,dest_addr,(message_t.format(cella='Freezer', temp=temp_c_z))))
                                        print "e-mail Inviata a {}".format(dest_addr)
                                except smtplib.SMTPException:
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e,dest_addr,smtplib.SMTPException))
                                        print "e-mail NON Inviata a {}".format(dest_addr)
                        ctrl = 1
                        for dest_sms in list_sms:
                                try:
                                        sms_alarm_temp(dest_sms,'Freezer',temp_c_z)
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,(sms_temp.format(temp_c_z))))
                                        print "SMS Inviato a {}".format(dest_sms)
                                except gammu.GSMError:
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,"Conn.Err."))
                                        print "SMS NON Inviato a {}".format(dest_sms)
        elif not (temp_c_z <= temp_sup_z):
                print("---!!!Allarme Temperatura Troppo Alta Rilevata in Cella Freezer!!!---")
                push_records_db
                rid = c.lastrowid
                if not (ctrl) :
                        for dest_addr in receivers:
                                try:
                                        smtpObj = smtplib.SMTP('localhost')
                                        smtpObj.sendmail(sender, receivers, (message_t.format(cella='Freezer', temp=temp_c_z)))
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e,dest_addr,(message_t.format(cella='Freezer', temp=temp_c_z))))
                                        print "e-mail Inviata a {}".format(dest_addr)
                                except smtplib.SMTPException:
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e,dest_addr,smtplib.SMTPException))
                                        print "e-mail NON Inviata a {}".format(dest_addr)
                        ctrl = 1
                        for dest_sms in list_sms:
				try:
                                        sms_alarm_temp(dest_sms,'Freezer',temp_c_z)
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,(sms_temp.format(temp_c_z))))
                                        print "SMS Inviato a {}".format(dest_sms)
                                except gammu.GSMError:
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,"Conn.Err."))
                                        print "SMS NON Inviato a {}".format(dest_sms)
        elif not (temp_c_g >= temp_inf_g):
                print("---!!!Allarme Temperatura Troppo Bassa Rilevata in Cella Frigor!!!---")
                push_records_db
                rid = c.lastrowid
                if not (ctrl) :
                        for dest_addr in receivers:
                                try:
                                        smtpObj = smtplib.SMTP('localhost')
                                        smtpObj.sendmail(sender, receivers, (message_t.format(cella='Frigor', temp=temp_c_g)))
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e,dest_addr,(message_t.format(cella='Frigor', temp=temp_c_g))))
                                        print "e-mail Inviata a {}".format(dest_addr)
                                except smtplib.SMTPException:
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e,dest_addr,str(smtplib.SMTPException)))
                                        print "e-mail NON Inviata a {}".format(dest_addr)
                        ctrl = 1
                        for dest_sms in list_sms:
                                try:
                                        sms_alarm_temp(dest_sms,'Frigor', temp_c_g)
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,(sms_temp.format(temp_c_g))))
                                        print "SMS Inviato a {}".format(dest_sms)
                                except gammu.GSMError:
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,"Conn.Err."))
                                        print "SMS NON Inviato a {}".format(dest_sms)
        elif not (temp_c_g <= temp_sup_g):
                print("---!!!Allarme Temperatura Troppo Alta Rilevata in Cella Frigor!!!---")
                push_records_db
                rid = c.lastrowid
                if not (ctrl) :
                        for dest_addr in receivers:
                                try:
                                        smtpObj = smtplib.SMTP('localhost')
                                        smtpObj.sendmail(sender, receivers, (message_t.format(cella='Frigor', temp=temp_c_g)))
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e,dest_addr,(message_t.format(cella='Frigor',temp=temp_c_g))))
                                        print "e-mail Inviata a {}".format(dest_addr)
                                except smtplib.SMTPException:
                                        c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_e,dest_addr,str(smtplib.SMTPException)))
                                        print "e-mail NON Inviata a {}".format(dest_addr)
                        ctrl = 1
                        for dest_sms in list_sms:
                               try:
                                       sms_alarm_temp(dest_sms,'Frigor', temp_c_g)
                                       c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,(sms_temp.format(temp_c_g))))
                                       print "SMS Inviato a {}".format(dest_sms)
                               except gammu.GSMError:
                                       c.execute("INSERT INTO alerts(id, fid, type, dest, err) VALUES ( NULL,?,?,?,?)",(rid,type_s, dest_sms,"Conn.Err."))
                                       print "SMS NON Inviato a {}".format(dest_sms)
#Chiusura connessione al DB e pulizia stati GPio
print ("Ciclo terminato...")
GPIO.cleanup()
conn.commit()
conn.close()
