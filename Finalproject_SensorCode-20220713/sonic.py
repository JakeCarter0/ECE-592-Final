import RPi.GPIO as gpio
import time
gpio.setmode(gpio.BCM)


gpio.setwarnings(False)

ECHO = 24
trig = 25


gpio.setup(ECHO, gpio.IN)
gpio.setup(trig, gpio.OUT, initial=gpio.LOW)


while(True):
 #   print ("Distance measurement in progress")
    time.sleep(0.1)  # sampling rate
    #sending a pulese to trig pin

    gpio.output(trig, True)
    time.sleep(0.00001)
    gpio.output(trig, False)
    
    while gpio.input(ECHO)==0:               #Check whether the ECHO is LOW
        pulse_start = time.time()              #Saves the last known time of LOW pulse

    while gpio.input(ECHO)==1:               #Check whether the ECHO is HIGH
        pulse_end = time.time()                #Saves the last known time of HIGH pulse 

    pulse_duration = (pulse_end - pulse_start)*1000000 #Get pulse duration to a variable in uS
    print(pulse_duration)

    distance = pulse_duration / 58.0        #Multiply pulse duration by 17150 to get distance
    distance = round(distance, 2)            #Round to two decimal points

    if distance > 2 and distance < 400:      #Check whether the distance is within range
        print("*Distance:{} cm".format((distance - 0.5)))  #Print distance with 0.5 cm calibration
    else:
        print("Out Of Range")

