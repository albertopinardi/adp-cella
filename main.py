# New Program to monitor temperature and current presence on the Freezer cell

# Import libraries
import logging
import signal
import time
import sys
import RPi.GPIO as GPIO
from prometheus_client import Gauge, start_http_server, Counter
from w1thermsensor import W1ThermSensor, Sensor


# Set up Prometheus metrics
FREEZER_TIMER = Counter('freezer_current', 'Freezer powerloss monitor metrics')
FRIDGE_TIMER = Counter('fridge_current', 'Fridge powerloss monitor metrics')
FREEZER_TEMP = Gauge('freezer_temperature', 'Freezer temperature monitor metrics')
AMBIENT_TEMP = Gauge('ambient_temperature', 'Ambient temperature monitor metrics')

# Set up sensors
FREEZER_HWID = "041633ae3bff"
AMBIENT_HWID = "800000040599"
FREEZER_PIN = 24
FRIDGE_PIN = 23


def setup_logger():
    """Setup the logger"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger


def signal_handler(sig, frame):
    """Handle the SIGINT signal"""
    logger.info("Shutting down")
    GPIO.cleanup()
    sys.exit(0)


@FRIDGE_TIMER.time()
def fridge_off(*args):
    """Control how long the fridge is powered off"""
    logger.debug(f"Function Called: {args}")
    start = time.perf_counter_ns()
    while GPIO.input(FRIDGE_PIN) is GPIO.LOW:
        time.sleep(1)
    stop = time.perf_counter_ns()
    duration = stop - start
    logger.debug(f"Fridge off for {duration / 1e9 } seconds")


@FREEZER_TIMER.time()
def freezer_off(*args):
    """Control how long the freezer is powered off"""
    logger.debug(f"Function Called: {args}")
    start = time.perf_counter_ns()
    while GPIO.input(FREEZER_PIN) is GPIO.LOW:
        time.sleep(1)
    stop = time.perf_counter_ns()
    duration = stop - start
    logger.debug(f"freezer off for {duration / 1e9 } seconds")



def gather_temperature(sensor_id, *args):
    """Read temperature from Sensors"""
    logger.debug(f"gather_temperature called: {args}")
    # Issue the conv_temp command
    sensor = W1ThermSensor(sensor_type=Sensor.DS18B20, sensor_id=sensor_id)
    temperature_in_celsius = sensor.get_temperature()
    # return all values from the bus
    return temperature_in_celsius


if __name__ == '__main__':
    logger = setup_logger()
    logger.debug("Starting up the server")
    start_http_server(8000)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FREEZER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(FRIDGE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    logger.debug("Add event detector")
    signal.signal(signal.SIGINT, signal_handler)
    GPIO.add_event_detect(FREEZER_PIN, GPIO.FALLING , callback=freezer_off, bouncetime=1000)
    GPIO.add_event_detect(FRIDGE_PIN, GPIO.FALLING , callback=fridge_off, bouncetime=1000)
    while True:
        FREEZER_TEMP.set(gather_temperature(FREEZER_HWID))
        AMBIENT_TEMP.set(gather_temperature(AMBIENT_HWID))
        time.sleep(10)
