from parameters import *
import RPi.GPIO as GPIO


# try:
from sensors import CameraUtils 
camera=CameraUtils.cameraUtils()
# except Exception as ex:
#     print("error in camera")

from sensors import SHT1x
shtSensor=SHT1x(shtdataPin, shtClockPin, gpio_mode=GPIO.BCM) 

from sensors import bh1750 
luxSensor= bh1750.bh1750()