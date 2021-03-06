import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# WALKERBOT

# GPIO pins that servos are connected to:
# 11, 13, 15, 40, 38, 36
# SERVO controls:
# 7.5 neutral, 2.5 is zero, 12.5 is 180

##### Servo setup #####
# For AR-3600HB Robot Servo
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(11, GPIO.OUT) # pin 11 used 
GPIO.setup(13, GPIO.OUT) # pin 15 used
GPIO.setup(15, GPIO.OUT)
GPIO.setup(36, GPIO.OUT)
##### PWM setup #####
s11 = GPIO.PWM(11, 50) # setting pin to pulse-width modulation with frequency of 50 hertz 
s13 = GPIO.PWM(13, 50)
s15 = GPIO.PWM(15, 50)
s36 = GPIO.PWM(36, 50)
s11.start(7.5) # sets duty cycle to 7.5 (neutral)
s13.start(7.5)
s15.start(7.5)
s36.start(7.5)


def empty(z):
    pass

def forwardStride(): # stepping legs forward
    s11.ChangeDutyCycle(12.5)
    s13.ChangeDutyCycle(7.5)
    s15.ChangeDutyCycle(12.5)
    s36.ChangeDutyCycle(7.5)
    #print("Forward Stride")
    move = 1 #true
    return move
def forwardPull(): # pulling body forward
    s11.ChangeDutyCycle(7.5)
    s13.ChangeDutyCycle(12.5)
    s15.ChangeDutyCycle(7.5)
    s36.ChangeDutyCycle(12.5)
    #print("Forward Pull")
    move = 0 #false
    return move

height = 120
width = 160
# third and twothird separate screen into 3 sections
third = width/3
twothird = third + third
minArea = 1 # minimum area to track object
criticalArea = 13000 # area to close claws (may be too large)
move = 0 # move legs
## TIMER VARIABLES ###
cTime = 0 # current time
pTime = 0 # previous time
timeDiff = 0 # time difference since last loop
Timer = .25 # time to wait


##### Camera/serial setup #####

cam = cv2.VideoCapture(0)
if cam.isOpened():
    cam.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT,120) # Setting camera height and width
    cam.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH,160) # in order to work with variables


while (True):
  
##### Setting up image tracking #####

    # big ball (pink): min: (121, 39, 98), max: (240, 255, 255)

    ret,frame = cam.read()
    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    image_mask=cv2.inRange(hsv,np.array([121,39,98]),np.array([240,255,255]))   
    erode=cv2.erode(image_mask,None,iterations=3)
    moments=cv2.moments(erode,True)
    area=moments['m00']
    
##### Movement decision making #####

    ## Timer ##
    pTime = cTime
    cTime = time.clock()
    timeDiff = cTime - pTime
    Timer -= timeDiff

    if moments['m00'] >=minArea:
        x=moments['m10']/moments['m00']
        y=moments['m01']/moments['m00']
        cv2.circle(frame,(int(x),int(y)),5,(0,255,0),-1)
    
        if (x>twothird):
	    if(Timer < 0): # Wait until Timer runs out, then take action
                if(move == 1):
                    move = forwardPull() # 180 degree
                elif(move == 0):
                    move = forwardStride() # 180 degree
	        Timer = .25 # resetting timer
    
    cv2.imshow('eroded',erode)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1)==27:
        break


s11.stop # stopping PWM
s13.stop
s15.stop
s36.stop
gpio.cleanup() # resets GPIO pin
cv2.destroyAllWindow()
scam.release()

