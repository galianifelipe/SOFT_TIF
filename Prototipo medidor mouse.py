import numpy as np
import cv2

image_height = 720 #480
image_width = 1080 #640
center = [550,0]
scroll = 10



img = cv2.imread(r'D:\Escritorio\FISIOLOGIA Y BIOFISICA\TIF\SOFT_TIF\im.png')

def check_location(center):
    if center[1] >= image_height:
        center[1] = image_height
    elif center[1] <= 0:
        center[1] = 0
    return center

def draw(layer, center):
    cv2.circle(layer, tuple(center), 70, (255,255,255), thickness=2, lineType=cv2.LINE_AA)
    cv2.circle(layer, tuple(center), 5, (255,255,255), thickness=-1, lineType=cv2.LINE_AA)
    return layer

def process_mouse_event(event,x,y,flags, cntr):
    clone = cv2.imread(r'D:\Escritorio\FISIOLOGIA Y BIOFISICA\TIF\SOFT_TIF\im.png')
    cv2.line(clone, (5,50), (250,50), (255,255,255), thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(clone, "Scroll ", (10,32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    if event == cv2.EVENT_LBUTTONDOWN:
        med=str((center[1]/10)*(np.pi/12))
        print(med[0]+med[1]+med[2]+med[3]+" cm.")
        cv2.putText(clone, "MEDICION: " + med[0]+med[1]+med[2]+med[3]+" cm.", (10,700), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 1, lineType=cv2.LINE_AA)
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            cv2.putText(clone, "Scroll Up", (10,32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
            center[1]-=scroll       
        else:
            center[1]+=scroll
            cv2.putText(clone, "Scroll Down", (10,32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    _center = check_location(cntr)
    if _center==[550, 0]:
        st="0,000"
    else:
        st=str((_center[1]/10)*(np.pi/12))
    cv2.line(clone, (5,cntr[1]), (image_width-5,cntr[1]), (255,255,255), thickness=2, lineType=cv2.LINE_AA)
    clone = draw(clone, _center)
    cv2.putText(clone, "MEDIDA: " + st[0]+st[1]+st[2]+st[3]+" cm.", (10,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 1, lineType=cv2.LINE_AA)
    cv2.imshow('DOLORIMETRO', clone) 

cv2.imshow('DOLORIMETRO', img)
cv2.setMouseCallback('DOLORIMETRO', process_mouse_event, param=center)
cv2.waitKey(0)
cv2.destroyAllWindows()