import tkinter as tk
from tkinter import simpledialog
import numpy as np
import cv2
from tkinter import Tk, simpledialog
from datetime import datetime
import os
import winsound
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
from openpyxl import load_workbook

def obtener_datos_gui():
    def on_button_click(num):
        nonlocal button_number
        button_number = num

    def submit_info():
        nonlocal nombre_voluntario, info_adicional
        nombre_voluntario = entry_nombre.get()
        info_adicional = entry_otro.get()
        if nombre_voluntario and button_number is not None:
            root.quit()
        else:
            label_error.config(text="Por favor, complete todos los campos.")

    # Crear la ventana
    root = tk.Tk()
    root.title("Registro de Voluntario")
    ruta_icono=os.path.abspath("../SOFT_TIF/Aplicacion/icono.ico")
    root.iconbitmap(ruta_icono)
    root.geometry("1080x720")  # Tamaño de la ventana

    # Cargar la imagen de fondo
    ruta_fondo=os.path.abspath("../SOFT_TIF/Aplicacion/Fondo.png")
    bg_image = Image.open(ruta_fondo)  # Cambia esta ruta por la de tu imagen
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Crear un canvas para poner la imagen de fondo
    canvas = tk.Canvas(root, width=1080, height=720)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Variables para almacenar los datos
    button_number = None
    nombre_voluntario = None
    info_adicional = None

    # Campo de entrada para el nombre
    entry_nombre = tk.Entry(root)
    canvas.create_window(875, 60, window=entry_nombre)  # Posicionar en el canvas

    # Etiqueta para el nombre
    label_nombre = tk.Label(root, text="Ingrese el nombre del voluntario:", bg="white")
    canvas.create_window(875, 30, window=label_nombre)

    # Crear botones numerados y colocarlos en posiciones personalizadas con `place`
    pos=[[429,436,453,453,453,221,244,264,252,352],[150,185,220,340,465,129,204,350,483,613]]
    buttons = []
    for i in range(0, 9):
        button = ttk.Button(root, text=f"{i+1}", command=lambda i=i: on_button_click(i))
        buttons.append(button)
        # Posicionar los botones de forma personalizada
        canvas.create_window(pos[0][i], pos[1][i], window=button)  # Cambia las coordenadas aquí
    button = ttk.Button(root, text=f"OTRO", command=lambda i=i: on_button_click(0))
    buttons.append(button)
    canvas.create_window(pos[0][9], pos[1][9], window=button)
    # Etiqueta y campo de entrada opcional
    label_otro = tk.Label(root, text="Otro:", bg="white")
    canvas.create_window(875, 600, window=label_otro)

    entry_otro = tk.Entry(root)
    canvas.create_window(875, 630, window=entry_otro)

    # Botón para enviar la información
    submit_button = ttk.Button(root, text="Enviar", command=submit_info)
    canvas.create_window(875, 670, window=submit_button)

    # Etiqueta para mensajes de error
    label_error = tk.Label(root, text="", fg="red", bg="white")
    canvas.create_window(875, 700, window=label_error)

    root.mainloop()

    # Retornar los datos obtenidos
    return nombre_voluntario, button_number, info_adicional

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
    k_resorte=((73.1*(10**9))*(1.81*(10**(-3))))/(8*(8.94**3)*13*(1+(0.5/(8.94**2))))
    area=1  #en cm2
    newt_kpn=0.101972
    kgcm_kpa=98.0665
    cv2.line(clone, (5,50), (250,50), (255,255,255), thickness=2, lineType=cv2.LINE_AA) 
    if event == cv2.EVENT_LBUTTONDOWN:
            med=str((center[1]/10)*(np.pi/24))
            a=str(med[0]+med[1]+med[2]+med[3]+" cm.")
            medidas.append(a)
            numero_str = ''.join(filter(lambda x: x.isdigit() or x == '.', a))
            numero_str = numero_str.rstrip('.')
            cm = float(numero_str)
            medf=k_resorte*(cm*10**(-2))
            pkpcm2=(medf*newt_kpn)/area
            kp=str(round(pkpcm2,2))
            nw=str(round((pkpcm2*kgcm_kpa),2))
            winsound.Beep(300, 500)
            cv2.putText(clone, "MEDICION: " + a, (10,700), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 1, lineType=cv2.LINE_AA)
    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            cv2.putText(clone, "Arriba", (10,32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
            center[1]-=scroll       
        else:
            center[1]+=scroll
            cv2.putText(clone, "Abajo", (10,32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    _center = check_location(cntr)
    if _center==[550, 0]:
            st="0,000"
    else:
            st=str((_center[1]/10)*(np.pi/24))
    cv2.line(clone, (5,cntr[1]), (image_width-5,cntr[1]), (255,255,255), thickness=2, lineType=cv2.LINE_AA)
    clone = draw(clone, _center)
    cv2.putText(clone, "MEDIDA: " + st[0]+st[1]+st[2]+st[3]+" cm.", (10,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 1, lineType=cv2.LINE_AA)
    altura=25
    for i in range (len(medidas)):
            a=medidas[i]
            numero_str = ''.join(filter(lambda x: x.isdigit() or x == '.', a))
            numero_str = numero_str.rstrip('.')
            cm = float(numero_str)
            medf=k_resorte*(cm*10**(-2))
            pkpcm2=(medf*newt_kpn)/area
            kp=str(round(pkpcm2,2))
            nw=str(round((pkpcm2*kgcm_kpa),2))
            if altura  < 700:
                cv2.putText(clone, "MEDIDA "+str(i+1)+": "+ medidas[i][0]+medidas[i][1]+medidas[i][2]+medidas[i][3]+" cm.", (700,altura), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, kp + " Kgf/cm2", (700,altura+12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, nw + " kPa", (700,altura+24), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                altura+=36
            else:
                cv2.putText(clone, "MEDIDA "+str(i+1)+": "+ medidas[i][0]+medidas[i][1]+medidas[i][2]+medidas[i][3]+" cm.", (900,altura-700), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, kp + " Kgf/cm2", (900,altura+12-700), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, nw + " kPa", (900,altura+24-700), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                altura+=36    
            
            
    cv2.imshow('DOLORIMETRO', clone) 










nombre_voluntario, button_number, otro = obtener_datos_gui()
optn=["Occipucio", "Trapecio", "Supraespinoso", "Glúteo", "Trocánter mayor", "Cervical inferior", "Segunda costilla", "Epicóndilo lateral", "Rodilla"]
k_resorte=((73.1*(10**9))*(1.81*(10**(-3))))/(8*(8.94**3)*13*(1+(0.5/(8.94**2))))
medidas_newton=[]
medidas_kp=[]
area=1  #en cm2
newt_kpn=0.101972
kgcm_kpa=98.0665

if nombre_voluntario is not None:
    if nombre_voluntario:
        # Obtener la fecha y hora actuales
        ahora = datetime.now()
        fecha_hora = ahora.strftime("%Y-%m-%d_%H-%M-%S")

        # Definir el nombre del archivo
        nombre_archivo = f"{nombre_voluntario}_{fecha_hora}.txt"
    else:
        print("No se ingresó un nombre.")
    
    if button_number!=0 or button_number!=None:
         lugar=optn[button_number-1]

    # Definir la ruta de la carpeta "Medidas" relativa al directorio actual del script
    carpeta_destino = os.path.abspath("../SOFT_TIF/Medidas")

    # Asegurarse de que la carpeta exista, si no, crearla
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    # Combinar la ruta de la carpeta con el nombre del archivo
    nombre_archivo = os.path.join(carpeta_destino, nombre_archivo)
    ruta_imagen = os.path.abspath("../SOFT_TIF/Aplicacion/im.png")
    image_height = 720 #480
    image_width = 1080 #640
    center = [550,0]
    scroll = 10
    img = cv2.imread(ruta_imagen)
    cv2.imshow('DOLORIMETRO', img)
    a=[]
    cv2.setMouseCallback('DOLORIMETRO', process_mouse_event, param=[center,a,ruta_imagen])
    cv2.waitKey(0)
    
    for i in a:
        numero_str = ''.join(filter(lambda x: x.isdigit() or x == '.', i))
        numero_str = numero_str.rstrip('.')
        cm = float(numero_str)
        medf=k_resorte*(cm*10**(-2))
        pkpcm2=(medf*newt_kpn)/area
        medidas_kp.append(round(pkpcm2,2))
        medidas_newton.append(round((pkpcm2*kgcm_kpa),2))
  
    with open(nombre_archivo, 'w') as file:
        file.write(f"Voluntario: {nombre_voluntario}\n")
        file.write(f"Fecha y Hora: {fecha_hora}\n")
        if button_number==0:
             file.write("Lugar de Medicion: "+otro+"\n\n")
        else:
             file.write("Lugar de Medicion: "+lugar+"\n\n")
        for i in range(len(a)):
            file.write("MEDIDA "+str(i+1)+":  "+str(medidas_kp[i])+" Kgf/cm2   "+str(medidas_newton[i])+" kPa  "+"\n")
    
    # Ruta del archivo Excel que queremos actualizar
    archivo_excel = os.path.join(carpeta_destino,"mediciones_voluntarios.xlsx")

    # Verifica si el archivo Excel ya existe
    if os.path.exists(archivo_excel):
        try:
            # Si el archivo existe, cargar el contenido
            df = pd.read_excel(archivo_excel)
        except Exception as e:
            print("Error al leer el archivo Excel:", e)
    else:
        # Crear un nuevo DataFrame si el archivo no existe
        df = pd.DataFrame(columns=["Voluntario", "Fecha y Hora", "Lugar de Medición", "Mediciones Kgf/cm2", "Mediciones kPa"])

    # Crear una fila con el nombre, la fecha, el lugar y una medida inicial vacía
    nueva_fila = {
        "Voluntario": nombre_voluntario,
        "Fecha y Hora": fecha_hora,
        "Lugar de Medición": otro if button_number == 0 else lugar,
        "Mediciones Kgf/cm2": "MEDIDAS(Kgf/cm2)",  
        "Mediciones kPa": "MEDIDAS (kPa)"  
    }

    # Agregar la fila inicial al DataFrame
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

    # Agregar cada medición como una nueva fila
    for i in range(len(a)):
        medicion_fila = {
            "Voluntario": None,  # Dejar vacío para que se copie de la fila anterior
            "Fecha y Hora": None,  # Dejar vacío para que se copie de la fila anterior
            "Lugar de Medición": None,  # Dejar vacío para que se copie de la fila anterior
            "Mediciones Kgf/cm2": medidas_kp[i],  
            "Mediciones kPa": medidas_newton[i]  
        }
        df = pd.concat([df, pd.DataFrame([medicion_fila])], ignore_index=True)

    # Guardar el DataFrame en el archivo Excel
    try:
        df.to_excel(archivo_excel, index=False, engine='openpyxl')

        # Ajustar el ancho de las columnas a un número fijo (ej. 25)
        workbook = load_workbook(archivo_excel)
        sheet = workbook.active

        for column in sheet.columns:
            sheet.column_dimensions[column[0].column_letter].width = 25  # Ajustar a un ancho fijo

        workbook.save(archivo_excel)  # Guardar los cambios en el archivo Excel
        print(f"Archivo Excel actualizado y guardado exitosamente en: {archivo_excel}")
    except Exception as e:
        print(f"Error al guardar el archivo Excel: {e}")
    cv2.destroyAllWindows()

else:
    print("No se completó el registro.")
