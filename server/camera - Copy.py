import cv2
import numpy as np
import sys
from glob import glob
import itertools as it
import datetime
import time

eyes = cv2.CascadeClassifier("haarcascade_eye.xml")
mouth = cv2.CascadeClassifier("haarcascade_mcs_mouth.xml")
nose = cv2.CascadeClassifier("haarcascade_mcs_nose.xml")
head = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
overlay = cv2.imread("overlay.png", -1)

def detect_bounds(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=10, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
def draw_overlay(img, rect):
    x1, y1, x2, y2 = rect
    y=y2-y1 + 40
    x=x2-x1 + 40
    small = cv2.resize(overlay, (x, y))

    x_offset = x1 - 10
    y_offset = y1 - 10

    for c in range(0,3):
        img[y_offset:y_offset + small.shape[0], x_offset:x_offset+ small.shape[1], c] = small[:,:,c] * (small[:,:,3]/255.0) + img[y_offset:y_offset+small.shape[0], x_offset:x_offset+small.shape[1], c] * (1.0 - small[:,:,3]/255.0)

def treatFrame(img):
    img = imutils.resize(img, width=500)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(img, (21, 21), 0)        
        
class VideoCamera(object):

    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
        
        self.minArea = 200
        self.adjustRate = 0.2
        self.status = "No Movement"
        self.color = (0, 255, 0)
    
    def __del__(self):
        self.video.release()

    def get_frame(self):
        
        success, image = self.video.read()
        normalFrame = treatFrame(image).copy().astype("float")
        success, image = self.video.read()

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        found_eyes = detect_bounds(gray, eyes)
        found_mouth = detect_bounds(gray, mouth)
        found_nose = detect_bounds(gray, nose)
        found_head = detect_bounds(gray, head)

        # only draw head
        if (len(found_head) > 0) and ((len(found_eyes) > 0) and (len(found_nose) > 0) and (len(found_mouth) > 0)):
            draw_rects(image, found_head, (0, 255, 0))
                
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        cv2.putText(image, status, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.color, 2)
        cv2.putText(image, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)            
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()