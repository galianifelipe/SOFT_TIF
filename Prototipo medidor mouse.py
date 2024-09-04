import numpy as np
import cv2
from tkinter import Tk, simpledialog
from datetime import datetime
import os



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

def process_mouse_event(event,x,y,flags, l):
    clone = cv2.imread(l[2])
    cntr=l[0]
    medidas=l[1]
    cv2.line(clone, (5,50), (250,50), (255,255,255), thickness=2, lineType=cv2.LINE_AA)
    cv2.putText(clone, "Scroll ", (10,32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    if event == cv2.EVENT_LBUTTONDOWN:
        med=str((center[1]/10)*(np.pi/12))
        print(med[0]+med[1]+med[2]+med[3]+" cm.")
        a=str(med[0]+med[1]+med[2]+med[3]+" cm.")
        medidas.append(a)
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
    altura=200
    for i in range (len(medidas)):
        cv2.putText(clone, "MEDIDA "+str(i+1)+": "+ medidas[i][0]+medidas[i][1]+medidas[i][2]+medidas[i][3]+" cm.", (700,altura), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 1, lineType=cv2.LINE_AA)
        altura+=25
    cv2.imshow('DOLORIMETRO', clone) 



# Crear una ventana de entrada
root = Tk()
root.withdraw()  # Oculta la ventana principal

# Solicitar el nombre del voluntario
nombre_voluntario = simpledialog.askstring("Nombre del voluntario", "Ingrese el nombre del voluntario:")

if nombre_voluntario:
    # Obtener la fecha y hora actuales
    ahora = datetime.now()
    fecha_hora = ahora.strftime("%Y-%m-%d_%H-%M-%S")

    # Definir el nombre del archivo
    nombre_archivo = f"{nombre_voluntario}_{fecha_hora}.txt"
else:
    print("No se ingresó un nombre.")

root.destroy()  # Cerrar la ventana


# Definir la ruta de la carpeta "Medidas" relativa al directorio actual del script
carpeta_destino = os.path.join(os.getcwd(), "Medidas")

# Asegurarse de que la carpeta exista, si no, crearla
if not os.path.exists(carpeta_destino):
    os.makedirs(carpeta_destino)

# Combinar la ruta de la carpeta con el nombre del archivo
nombre_archivo = os.path.join(carpeta_destino, nombre_archivo)
ruta_imagen = os.path.join(os.getcwd(), "im.png")
print(ruta_imagen)
image_height = 720 #480
image_width = 1080 #640
center = [550,0]
scroll = 10
img = cv2.imread(ruta_imagen)
cv2.imshow('DOLORIMETRO', img)
a=[]
cv2.setMouseCallback('DOLORIMETRO', process_mouse_event, param=[center,a,ruta_imagen])
cv2.waitKey(0)
print (a)
with open(nombre_archivo, 'w') as file:
    file.write(f"Voluntario: {nombre_voluntario}\n")
    file.write(f"Fecha y Hora: {fecha_hora}\n")
    for i in range(len(a)):
        file.write("MEDIDA "+str(i+1)+":  "+a[i]+"\n")
cv2.destroyAllWindows()