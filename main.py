# New Program to monitor temperature and current presence on the Freezer cell

# Import libraries
import os
import RPi.GPIO as GPIO
import time
import sqlite3
from prometheus_client import Gauge, start_http_server, Summary

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set up database
wd = os.cwd()
db = sqlite3.connect(wd + '/datalogger.db')
CURSOR = db.cursor()

# Set up Prometheus
FREEZER_CURRENT_SUMMARY = Summary('freezer_current', 'Freezer powerloss monitor metrics')
FRIGOR_CURRENT_SUMMARY = Summary('frigor_current', 'Frigor powerloss monitor metrics')
FREEZER_TEMPERATURE_GAUGE = Gauge('freezer_temperature', 'Freezer temperature monitor metrics')
AMBIENT_TEMPERATURE_GAUGE = Gauge('ambient_temperature', 'Ambient temperature monitor metrics')

# Setup Objects for Database
class Records:
    def __init__(self, freezer_current, freezer_temperature, ambient_temperature):
        self.freezer_current = freezer_current
        self.freezer_temperature = freezer_temperature
        self.ambient_temperature = ambient_temperature
    
    def write(self):
        CURSOR.execute("INSERT INTO records VALUES (?, ?, ?)", (self.freezer_current, self.freezer_temperature, self.ambient_temperature))
        db.commit()

class Alarms:
    def __init__(self, freezer_current, freezer_temperature, ambient_temperature):
        self.freezer_current = freezer_current
        self.freezer_temperature = freezer_temperature
        self.ambient_temperature = ambient_temperature
    
    def write(self):
        CURSOR.execute("INSERT INTO alarms VALUES (?, ?, ?)", (self.freezer_current, self.freezer_temperature, self.ambient_temperature))
        db.commit()