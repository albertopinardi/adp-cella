import sqlite3
import time

#connessione al DB
conn = sqlite3.connect('/root/datalogger.db')
c = conn.cursor()
#abilito printout errori
sqlite3.enable_callback_tracebacks(True)
time_now = int(time.time())
intervallo = time_now-600
c.execute("SELECT * from records WHILE time >= intervallo  ")