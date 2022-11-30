"""
Created on July 24 2022

@author: Jake Carter
PiE Final
This code is designed to download and display data recorded by MonitorigApp.py running on a Raspberry pi on the same network
"""

import os
import sys
import subprocess
import csv
import time
import datetime
try:
    import matplotlib.pyplot as plt
except:
    print("Warning: [matplotlib] library not installed, install with 'pip install matplotlib'")
    sys.exit(-1)
try:
    import numpy as np
except:
    print("Warning: [numpy] library not installed, install with 'pip install numpy'")
    sys.exit(-1)



if sys.argv[1:]:
    piAddress = sys.argv[1]
else:
    print("Please input argument IP for the Raspberry Pi as the first argument")
    sys.exit()

if sys.argv[2:]:
    runMode = int(sys.argv[2])
    if runMode != 0 and runMode != 1:
        print("Please input argument for program function as teh second argument. ('0' for file transfer, '1' for transfer and plot data)")
        sys.exit()
else:
    print("Please input argument for program function. ('0' for file transfer, '1' for transfer and plot data)")
    sys.exit()

if sys.argv[3:]:
    fname = sys.argv[3]
else:
    if runMode == 1:
        print("Target file needed for run mode 1, enter target file name as third argument")
        sys.exit()
    fname = ""

progDir = os.path.dirname(__file__)
try:
    os.mkdir(".\\DataFiles")
except:
    pass
finally:
    if os.name == "nt":
        targetFile = os.path.join(progDir, "DataFiles\\" + fname)
        if os.path.exists(".\\DataFiles\\" + fname) == False:
            username = str(input("Enter username: "))
            command = "scp " + username + "@" + piAddress + ":/home/" + username + "/Documents/" + fname + " .\\DataFiles\\"
            print(command)
            subprocess.run(command)
        elif fname == "":
            username = str(input("Enter username: "))
            command = "scp -r " + username + "@" + piAddress + ":/home/" + username + "/Documents/* .\\DataFiles\\"
            print(command)
            subprocess.run(command)
        else:
            print("File already downloaded")
        if os.path.exists(".\\DataFiles\\" + fname) == False:
            print("Error, file not found")
            sys.exit()
    else:
        targetFile = os.path.join(progDir, "DataFiles/" + fname)
        if os.path.exists("./DataFiles/" + fname) == False:
            username = str(input("Enter username: "))
            command = "scp " + username + "@" + piAddress + ":/home/" + username + "/Documents/" + fname + " ./DataFiles"
            print(command)
            subprocess.run(command)
        elif fname == "":
            username = str(input("Enter username: "))
            command = "scp -r " + username + "@" + piAddress + ":/home/" + username + "/Documents/* ./DataFiles"
            print(command)
            subprocess.run(command)
        else:
            print("File already downloaded")
        if os.path.exists("./DataFiles/" + fname) == False:
            print("Error, file not found")
            sys.exit()






if runMode == 0:
    print("File ready")
    sys.exit()
else:
    print("Plotting data...")

dataUS = list()
timeUS = list()
dataPot = list()
timePot = list()

try:
    with open(targetFile, "r", newline = "") as fr:
        reader = csv.DictReader(fr)
        for dataPoint in reader:
            if dataPoint["Data"] == "Distance":
                timeUS.append(float(dataPoint["Time"]))
                dataUS.append(float(dataPoint["Value"]))
            elif dataPoint["Data"] == "Percentage":
                timePot.append(float(dataPoint["Time"]))
                dataPot.append(float(dataPoint["Value"]))
except:
    print("Error,invalid file format")
    sys.exit(-1)

potStartTime = timePot[0]
usStartTime = timeUS[0]
startDateTime = datetime.datetime.fromtimestamp(min(potStartTime, usStartTime))

for i in range(0,len(timeUS)):
    timeUS[i] = round(timeUS[i] - usStartTime,3)
for i in range(0,len(timePot)):
    timePot[i] = round(timePot[i] - usStartTime,3)

plt.subplot(211)
plotUS = plt.plot(timeUS, dataUS)
plt.setp(plotUS, color = "b")
plt.title("Distance Recorded by Ultrasonic Sensor")
plt.xlabel("Time (s)")
plt.ylabel("Distance (cm)")
plt.xlim(min(timeUS[0],timePot[0]),max(timeUS[-1],timePot[-1]))

plt.subplot(212)
plotPot = plt.plot(timePot, dataPot)
plt.setp(plotPot, color = "C1")
plt.title("Potentiometer Percentage Turned")
plt.xlabel("Time (s)")
plt.ylabel("Position (%)")
plt.ylim(-10,110)
plt.xlim(min(timeUS[0],timePot[0]),max(timeUS[-1],timePot[-1]))

plt.suptitle("Data recorded on " + startDateTime.strftime("%m/%d/%Y") + " at " + startDateTime.strftime("%H:%M:%S"))
plt.subplots_adjust(hspace = .5)
plt.show()
# subprocess.run("admin")
# subprocess.run("yes")
# username = str(input("Enter username: "))
# subprocess.run(username)
