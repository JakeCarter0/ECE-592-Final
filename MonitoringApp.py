"""
Created on July 12 2022

@author: Jake Carter
PiE Final
This code uses the MCP3008 to read analog potentiometer values, and the switch is low triggered
"""


import RPi.GPIO as gpio
import time
import threading
import socket
import subprocess
import os
import spidev
import csv
import datetime
import colorsys
import sys



gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
rLED = 5
gLED = 6
bLED = 13
regLED = 14
buzzer = 18
# AtoDCS = 8
# AtoDOut = 9
# AtoDIn = 10
# AtoDCLK = 11
SW = 16
echo = 24
trig = 25
gpio.setup(rLED, gpio.OUT, initial=gpio.LOW)
gpio.setup(gLED, gpio.OUT, initial=gpio.LOW)
gpio.setup(bLED, gpio.OUT, initial=gpio.LOW)
gpio.setup(regLED, gpio.OUT, initial=gpio.LOW)
gpio.setup(buzzer, gpio.OUT)
# gpio.setup(AtoD, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(SW, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(echo, gpio.IN)
gpio.setup(trig, gpio.OUT, initial=gpio.LOW)
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1000000
startTime = 0.0
pressTime = -1
prevPressTime = -1
releaseTime = -1
changedFlag = 0
MoP = 0 #0:MS, 1:RDM, 2:ORD, 3:OFF
distance = 100
indicator = gpio.PWM(regLED, 2)
indicator.start(0)
rVal = gpio.PWM(rLED, 100)
rVal.start(0)
gVal = gpio.PWM(gLED, 100)
gVal.start(0)
bVal = gpio.PWM(bLED, 100)
bVal.start(0)
buzzerVal = gpio.PWM(buzzer, 100)
buzzerVal.start(0)
fname = ""


def readUSThread():
    global MoP
    global dataUS
    global distance
    buzzerBeepTmr = 0
    while True:
        time.sleep(.1)
        #get sensor data and convert to cm
        gpio.output(trig, True)
        time.sleep(0.00001) #10microsecond
        gpio.output(trig, False)
        while gpio.input(echo)==0:
            t0 = time.time()
        while gpio.input(echo)==1:
            t1 = time.time()
        distance = round(1000000 * (t1 - t0) / 58.2, 2)
        if MoP < 2:
            if distance >= 4 and distance <= 20:
                buzzerVal.ChangeFrequency(118.75 * distance - 375)
                buzzerBeepTmr += 1
                if buzzerBeepTmr == 10:
                    buzzerVal.ChangeDutyCycle(50)
                elif buzzerBeepTmr == 20:
                    buzzerBeepTmr = 0
                    buzzerVal.ChangeDutyCycle(0)
            else:
                buzzerVal.ChangeDutyCycle(0)
            print(str(distance) + " cm")
        #print(distance)
        if MoP > 0:
            dataUS.append({"Data" : "Distance", "Time" : round(time.time(), 3), "Value" : distance})

def readPotThread():
    global MoP
    global dataPot
    while True:
        time.sleep(.5)
        response = spi.xfer2([1,8<<4,0])
        data = ((response[1]&3) << 8) + response[2]
        percentage = round(data / 1023 * 100, 2)
        if MoP < 2:
            RGBVals = colorsys.hsv_to_rgb(.01 * percentage, 1, 1)
            rVal.ChangeDutyCycle(RGBVals[0] * 100)
            gVal.ChangeDutyCycle(RGBVals[1] * 100)
            bVal.ChangeDutyCycle(RGBVals[2] * 100)
            print(str(percentage) + "%" + " R:" + str(round(RGBVals[0],2)) + " G:" + str(round(RGBVals[1],2)) + " B:" + str(round(RGBVals[2],2)))
        if MoP > 0:
            dataPot.append({"Data" : "Percentage", "Time" : round(time.time(), 3), "Value" : percentage})

def logDataThread():
    global fname
    global dataPot
    global dataUS
    global MoP
    while True:
        time.sleep(5)
        if MoP < 0:
            with open(fname, "a", newline = "") as fw:
                writer = csv.DictWriter(fw, fieldnames = ["Data", "Time", "Value"])
                for dataPoint in dataPot:
                    writer.writerow(dataPoint)
                for dataPoint in dataUS:
                    writer.writerow(dataPoint)
                dataPot = list()
                dataUS = list()


def SW_callback(channel):
    global MoP
    global pressTime
    global prevPressTime
    global changedFlag
    global releaseTime
    global dataPot
    global startTime
    global dataUS
    global fname
    if gpio.input(SW) == gpio.LOW:
        pressTime = time.time()
        while gpio.input(SW) == gpio.LOW:
            if time.time() - pressTime > 2:
                MoP = 2
                indicator.ChangeDutyCycle(50)
                changedFlag = 1
                buzzerVal.ChangeDutyCycle(0)
                rVal.ChangeDutyCycle(0)
                gVal.ChangeDutyCycle(0)
                bVal.ChangeDutyCycle(0)
                startTime = round(time.time(), 2)
                targetDir = "/home/admin/Documents"
                filename = "data" + datetime.datetime.now().strftime("%m%d_%H%M%S") + ".csv"
                fname = os.path.join(targetDir, filename)
                with open(fname, "w", newline = "") as fw:
                    writer = csv.DictWriter(fw, fieldnames = ["Data", "Time", "Value"])
                    writer.writeheader()
                return
            time.sleep(.1)
    elif gpio.input(SW) == gpio.HIGH:
        releaseTime = time.time()
        if changedFlag == 1:
            changedFlag = 0
        elif releaseTime - prevPressTime < 1:
            MoP = 1
            indicator.ChangeDutyCycle(100)
            startTime = round(time.time(), 2)
            targetDir = "/home/admin/Documents"
            filename = "data" + datetime.datetime.now().strftime("%m%d_%H%M%S") + ".csv"
            fname = os.path.join(targetDir, filename)
            with open(fname, "w", newline = "") as fw:
                writer = csv.DictWriter(fw, fieldnames = ["Data", "Time", "Value"])
                writer.writeheader()
            return
        else:
            MoP = 0
            indicator.ChangeDutyCycle(0)
            if len(dataUS) != 0:
                with open(fname, "a", newline = "") as fw:
                    writer = csv.DictWriter(fw, fieldnames = ["Data", "Time", "Value"])
                    for dataPoint in dataPot:
                        writer.writerow(dataPoint)
                    for dataPoint in dataUS:
                        writer.writerow(dataPoint)
                    dataPot = list()
                    dataUS = list()
        prevPressTime = pressTime




gpio.add_event_detect(SW, gpio.BOTH, callback=SW_callback, bouncetime=5)
tUS = threading.Thread(target = readUSThread)
tUS.start()
tPot = threading.Thread(target = readPotThread)
tPot.start()
tLog = threading.Thread(target = logDataThread)
tLog.start()

dataUS = list()
dataPot = list()


while True:
    try:
        time.sleep(.1)
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        MoP = 0
        indicator.ChangeDutyCycle(0)
        with open(fname, "a", newline = "") as fw:
            writer = csv.DictWriter(fw, fieldnames = ["Data", "Time", "Value"])
            for dataPoint in dataPot:
                writer.writerow(dataPoint)
            for dataPoint in dataUS:
                writer.writerow(dataPoint)
            dataPot = list()
            dataUS = list()
        print("Exiting Program")
        indicator.ChangeDutyCycle(0)
        rVal.ChangeDutyCycle(0)
        gVal.ChangeDutyCycle(0)
        bVal.ChangeDutyCycle(0)
        sys.exit()
