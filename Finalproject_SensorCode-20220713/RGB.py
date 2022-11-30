import RPi.GPIO as gpio
import time
import sys

gpio.setmode(gpio.BCM)

print(gpio.getmode())

gpio.setwarnings(False)

Red = 5
Green = 6
Blue = 13

RGB = [Red, Green, Blue]

gpio.setup(RGB, gpio.OUT, initial=gpio.HIGH)
#gpio.setup(LED, gpio.OUT, initial=gpio.LOW)

rgbfreq = 100
rgbdc = 50
p1 = gpio.PWM(RGB[0], rgbfreq)
p2 = gpio.PWM(RGB[1], rgbfreq)
p3 = gpio.PWM(RGB[2], rgbfreq)

p1.start(rgbdc)
p2.start(rgbdc)
p3.start(rgbdc)
	
def RGB_LED(R, G, B):
	p1.ChangeDutyCycle(R)
	p2.ChangeDutyCycle(G)
	p3.ChangeDutyCycle(B)


def main():
	
	R = 100 - int(sys.argv[1])*100/255
	G = 100 - int(sys.argv[2])*100/255
	B = 100 - int(sys.argv[3])*100/255
	print(R, G, B)
	while(True):
		try:
			RGB_LED(R, G, B)
		except "KeyBoardInterrupt":
			p1.stop()
			p2.stop()
			p3.stop()
			
			gpio.cleanup()

if __name__ == "__main__":
	main()




