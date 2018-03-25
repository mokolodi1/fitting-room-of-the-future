import sys, os.path
import cv2
import math
import numpy as np

from shirt import Shirt
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

class MyEventHandler(PatternMatchingEventHandler):
    def __init__(self,videocam,patterns):
        PatternMatchingEventHandler.__init__(self,patterns=patterns)
        self.videocam = videocam
    def on_moved(self, event):
        super(MyEventHandler, self).on_moved(event)
        print("File %s was just moved" % event.src_path)

    def on_created(self, event):
        super(MyEventHandler, self).on_created(event)
        print("File %s was just created" % event.src_path)

    def on_deleted(self, event):
        super(MyEventHandler, self).on_deleted(event)
        print("File %s was just deleted" % event.src_path)

    def on_modified(self, event):
        super(MyEventHandler, self).on_modified(event)
        print("File %s was just modified" % event.src_path)
        with open(event.src_path, 'r') as myfile:
            data=myfile.read().replace('\n', '')
            self.videocam.set_color(data)

class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
        self.initialized = False
        self.initTimer = 0
        self.silouhette = cv2.imread('silou.png')

        self.shirt = None
        self.colorize = False
        self.color = 0

        watched_dir = os.path.split("/tmp/over_here_arnaud")[0]
        patterns = ["/tmp/over_here_arnaud"]
        event_handler = MyEventHandler(self,patterns)
        self.observer = Observer()
        self.observer.schedule(event_handler, watched_dir, recursive=True)
        self.observer.start()


    def __del__(self):
        self.video.release()
        self.observer.stop()

    def get_frame(self):
        success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        (h,w,d) = image.shape
        #9:16
        #16->h
        #9->
        width = math.floor((9*h/16)/2)
        stx = math.floor(w/2)-width
        endx = math.floor(w/2)+width
        img = image[0:h, stx:endx]

        if not self.initialized:
            #Add silouhette
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(self.silouhette, (endx-stx,h))
            head_x = math.floor((endx-stx)/2)
            head_y = math.floor(h*140/720)

            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            if (len(faces)>0):
                (x,y,wf,hf) = faces[0]
                x_c = math.floor(x + wf/2)
                y_c = math.floor(y + hf/2)
                # print(abs(head_x-x)+abs(head_y-y))
                if (abs(head_x-x_c)+abs(head_y-y_c) < 50):
                    if (wf < (endx-stx)/2):
                        self.initTimer += 1
                        cv2.rectangle(img,(x,y),(x+wf,y+hf),(0,255,0),2)
                    else:
                        cv2.rectangle(img,(x,y),(x+wf,y+hf),(0,255,255),2)
                else:
                    cv2.rectangle(img,(x,y),(x+wf,y+hf),(0,0,255),2)

            if (self.initTimer >= 100):
                self.shirt = Shirt(img)
                self.initialized = True

            img = cv2.add(img,resized)
        else:
            #Can colorize if needed
            if self.colorize and (self.shirt != None):
                img = self.shirt.change_color(img,self.color)
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tobytes()

    def set_color(self,color):
        self.colorize = True
        tmp = color[4:-1]
        rgb = np.array(tmp.split(','))
        print(rgb)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        self.color = hsv[0]
        print("color",self.color)
