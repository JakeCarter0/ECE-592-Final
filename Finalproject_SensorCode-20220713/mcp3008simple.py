import RPi.GPIO as gpio
import time
import spidev
import os
gpio.setmode(gpio.BCM)

gpio.setwarnings(False)

ECHO = 24
trig = 25

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)  # open spi port 0, device (CS) 0
spi.max_speed_hz=1000000
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
    response = spi.xfer2([1,(8+channel)<<4,0])   #1000 0000    Start byte 00000001, channel selection: end byte
    print(response)
    data = ((response[1]&3) << 8) + response[2]         #011
#    print(data)
    return data
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data, places):
    volts = (data * 3.3) / float(1023)
    volts = round(volts, places)
    return volts
 
# Function to calculate temperature from
# TMP36 data, rounded to specified
# number of decimal places.
def ConvertTemp(data, places):
    #10mV per deg C
    #0.75 V at 25 C
 
  # ADC Value  taken from another wwbsite verified against the datasheet
    # (approx)  Temp  Volts
  #    0      -50    0.00
  #   78      -25    0.25
  #  155        0    0.50
  #  233       25    0.75
  #  310       50    1.00
  #  465      100    1.50
  #  775      200    2.50
  # 1023      280    3.30
 
    temp = ((data * 330)/float(1023))-50
    temp = round(temp,places)
    return temp

def Convertcolor(temp):
    if temp > 50:
        R, G, B = 255, 0, 0
    elif temp < 5:
        R, G, B = 0, 0, 255
    elif temp <= 50 and temp > 42:
        R = 255
        G = 0
        B = 0
    elif temp <= 42 and temp > 34:
        R = int(255.0*(42 - temp) / 8.0)
        G = 0.0
        B = 255
 
# Define sensor channels
pot_channel = 0
 
# Define delay between readings
delay = 1
 
try:
    while True:
        pot_level = ReadChannel(pot_channel)
        pot_volts = ConvertVolts(pot_level, 2)
        pot_angle = (pot_volts*360)/3.3

    # Print out results
        print("Pot : {} ({}V) {} deg".format(pot_level,pot_volts, pot_angle))
  # Wait before repeating loop
    
except KeyboardInterrupt:
    spi.close()
