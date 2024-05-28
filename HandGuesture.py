#import all dependencies
import cv2
import time
import math
from ctypes import cast,POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities,IAudioEndpointVolume
import screen_brightness_control as sbc

from handmodel import handDetector

#Video capture Initialization
vidObj = cv2.VideoCapture(0)
vidObj.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
vidObj.set(cv2.CAP_PROP_FRAME_HEIGHT,720)

#Initialization of the handDetector function that detects hands if confidence > 70%
detection_confidence = int(0.7)
handlmsObj = handDetector(detectionCon=detection_confidence)

#Connecting to your system Audio controls
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()

#setting initial Volume controls
currentVolume = volume.GetMasterVolumeLevel() 
minVolume = volRange[0]
maxVolume = volRange[1]

#Function that controls volume
def setVolume(dist):
    global currentVolume
    if dist < 50:
        newVolume = max(currentVolume - 1, minVolume)  
    else:
        newVolume = min(currentVolume + 1, maxVolume)  

    # Set the new volume level
    volume.SetMasterVolumeLevel(newVolume, None)
    currentVolume = newVolume 


#Setting initial Brightness values
minBrightness = 0
maxBrightness = 100
currentBrightness = sbc.get_brightness(display=0)

#Function that controls Brightness
def setBrightness(dist):
    global currentBrightness
    if isinstance(currentBrightness, list):
        currentBrightness = currentBrightness[0]
    if dist < 50:
        newBrightness = max(currentBrightness - 1, minBrightness)  
    else:
        newBrightness = min(currentBrightness + 1, maxBrightness) 
    sbc.set_brightness(int(newBrightness),display=0)
    currentBrightness = newBrightness

#While camera is on
while True:

    _,frame = vidObj.read() 

    frame = cv2.flip(frame,1)
    frame = handlmsObj.findHands(frame)
    lndmrks = handlmsObj.findPosition(frame,draw=False)

    if lndmrks:
        xr1,yr1 = lndmrks[1][4][1],lndmrks[1][4][2] #Co-ordinates of the tip of thumb finger
        xr2,yr2 = lndmrks[1][8][1],lndmrks[1][8][2] #Co-ordinates of the tip of index finger

        #Visualize the detected hand
        cv2.circle(frame, (xr1,yr1),15,(255,255,255))  
        cv2.circle(frame, (xr2,yr2),15,(255,255,255))  
        cv2.line(frame,(xr1,yr1),(xr2,yr2),(0,255,0),3)

        #Calculate distance between the tip of thumb and index finger
        dist = math.hypot(xr2-xr1,yr2-yr1)

        if dist < 50:
            cv2.line(frame,(xr1,yr1),(xr2,yr2),(0,0,255),3)  #if distance is less than 50 color the line red
        
        if lndmrks[0] == 'Left':  #if hand if left adjust Brightness
            setBrightness(dist)
            time.sleep(0.01) #set speed of increase and decrease

        elif lndmrks[0] == 'Right':  #if hand if right adjust Volume
            setVolume(dist)
            time.sleep(0.01) #set speed of increase and decrease      

    cv2.imshow("stream",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vidObj.release()
cv2.destroyAllWindows()

