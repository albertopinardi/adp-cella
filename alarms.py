import sqlite3
import time
import os
#Identifico Directory del DB
wd = os.getcwd()
db_name = 'datalogger.db'
db_path = wd + db_name

#connessione al DB
conn = sqlite3.connect(db_path)
c = conn.cursor()
#abilito printout errori
sqlite3.enable_callback_tracebacks(True)
time_now = int(time.time())
intervallo = time_now-600
c.execute("SELECT * from records WHILE time >= intervallo  ")