import pyscreenshot
import pytesseract
import time
from datetime import datetime
import os

# init preprocessing image 

import cv2
import numpy as np


# get grayscale image
def get_grayscale(image):
	return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	

# noise removal
def remove_noise(image):
    return cv2.medianBlur(image,5)
 
#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

#dilation
def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)
    
#erosion
def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

#opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

#canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)

#skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

#template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 


# end preprocessing


def busca_cant():
	image = pyscreenshot.grab(bbox=(200, 350, 530, 380))
	image.save("rectangulo.jpg")
   
	image = cv2.imread('rectangulo.jpg')
	gray = get_grayscale(image)
	thresh = thresholding(gray)
	openi = opening(gray)
	canni = canny(gray)
   
	cant0 = pytesseract.image_to_string(image, config='-l eng --psm 1')
	cant0 = cant0[cant0.index(':')+1:]
	
	cant1 = pytesseract.image_to_string(thresh, config='-l eng --psm 1')
	cant1 = cant1[cant1.index(':')+1:]
	return [cant0, cant1]

def uptime_load():
   with open('resultados_tplink.txt', 'a') as resulta2:
      while True:
         now = datetime.now()
         timestamp = datetime.timestamp(now)
         cant = busca_cant()
         print(timestamp, cant)
         resulta2.write(str(int(timestamp))+'\t'+str(cant)+ '\n')
         time.sleep(60)


os.system("/usr/bin/firefox --new-window http://192.168.66.32")
time.sleep(5)


var = os.popen('/usr/bin/xwininfo -name "TP-LINK - Mozilla Firefox" | grep "Window id:"').read()
vinfo = var.split(" ")
infcmd = 'printf %i ' + vinfo[3]
vwinfo = os.popen(infcmd).read()
print(int(vwinfo))

os.system("/usr/bin/xdotool windowfocus "+vwinfo)


os.system("/usr/bin/xdotool mousemove 50 390 click 1")
time.sleep(2)
os.system("/usr/bin/xdotool mousemove 50 495 click 1")
time.sleep(2)
uptime_load()

