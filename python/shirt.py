import numpy as np
import cv2
import math
import random

NB_RND = 35
LIMIT_DETECTION = 25

def delta_e(c1, c2):
    l = int(c2[0])-int(c1[0])
    a = int(c2[1])-int(c1[1])
    b = int(c2[2])-int(c1[2])
    res = math.sqrt(l*l+a*a+b*b)
    return res


def delta_im(im1, c):
    im2 = np.ones(im1.shape) * c
    f1 = im1.astype(float)
    f2 = im2.astype(float)
    l = np.subtract(f2[:,:,0], f1[:,:,0])
    a = np.subtract(f2[:,:,1], f1[:,:,1])
    b = np.subtract(f2[:,:,2], f1[:,:,2])
    res = np.sqrt(l*l+a*a+b*b)
    return res

def get_median_color(colors):
    #Remove weird colors from samples
    distances = []
    for i in range(len(colors)):
        sum = 0
        for j in range(len(colors)):
            if (i != j):
                sum += delta_e(colors[i],colors[j])
        distances.append(sum)

    test = np.array(distances)
    std = np.std(test)
    med = np.median(test)

    id = distances.index(med)
    return colors[id]


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

class Shirt(object):
    def __init__(self,img):
        #Load colors
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)

        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        self.colors = []
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            mid_x = math.floor(x + (w/2))
            shirt_y = y + 2 * h
            avg_h = 0
            cpt = 0
            start_w = math.floor(x - (w/3))
            end_w = math.floor(x + w + (w/3))
            start_h = math.floor(shirt_y - (h/4))
            end_h = math.floor(shirt_y + h + (h/4))
            randoms = np.random.uniform(low=[start_w,start_h], high=[end_w,end_h],size=(NB_RND,2))
            for i in range(NB_RND):
                xr = math.floor(randoms[i,0])
                yr = math.floor(randoms[i,1])
                cv2.rectangle(img,(xr-2,yr-2),(xr+2,yr+2),(0,255,0),2)
                l = []
                a = []
                b = []
                tmp_colors = []
                for yc in range(yr-2,yr+3):
                    for xc in range(xr-2,xr+3):
                        tmp_colors.append(lab[yr,xr,:])
                col = get_median_color(tmp_colors)
                self.colors.append(col)



    def change_color(self,img,hue):
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
        (h,w,d) = lab.shape
        mask = np.zeros((h,w), np.uint8)
        print(lab.shape)
        for c in self.colors:
            delta = delta_im(lab,c)
            tmp = np.zeros((h,w), np.uint8)
            tmp[np.where(delta < [LIMIT_DETECTION])] = 255
            mask = cv2.bitwise_or(mask,tmp)


        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(10,10))
        closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(hsv)
        h[np.where(closing == [255])] = 0
        hsv = cv2.merge((h,s,v))

        imgco = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        return imgco
