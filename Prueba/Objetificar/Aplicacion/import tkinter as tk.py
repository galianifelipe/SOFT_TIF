import tkinter as tk
from tkinter import simpledialog, ttk
import numpy as np
import cv2
from PIL import Image, ImageTk
from datetime import datetime
import os
import winsound
import pandas as pd
from openpyxl import load_workbook

class RegistroVoluntario:
    def __init__(self):
        self.nombre_voluntario = None
        self.button_number = None
        self.info_adicional = None
        self.create_gui()

    def create_gui(self):
        self.root = tk.Tk()
        self.root.title("Registro de Voluntario")
        ruta_icono = os.path.abspath("../Aplicacion/icono.ico")
        self.root.iconbitmap(ruta_icono)
        self.root.geometry("1080x720")

        # Cargar la imagen de fondo
        ruta_fondo = os.path.abspath("../Aplicacion/Fondo.png")
        bg_image = Image.open(ruta_fondo)
        bg_photo = ImageTk.PhotoImage(bg_image)

        canvas = tk.Canvas(self.root, width=1080, height=720)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")

        # Campos de entrada
        self.create_input_fields(canvas)

        self.root.mainloop()

    def create_input_fields(self, canvas):
        label_nombre = tk.Label(self.root, text="Ingrese el nombre del voluntario:", bg="white")
        canvas.create_window(875, 30, window=label_nombre)

        self.entry_nombre = tk.Entry(self.root)
        canvas.create_window(875, 60, window=self.entry_nombre)

        self.create_buttons(canvas)

        label_otro = tk.Label(self.root, text="Otro:", bg="white")
        canvas.create_window(875, 600, window=label_otro)

        self.entry_otro = tk.Entry(self.root)
        canvas.create_window(875, 630, window=self.entry_otro)

        submit_button = ttk.Button(self.root, text="Enviar", command=self.submit_info)
        canvas.create_window(875, 670, window=submit_button)

        self.label_error = tk.Label(self.root, text="", fg="red", bg="white")
        canvas.create_window(875, 700, window=self.label_error)

    def create_buttons(self, canvas):
        pos = [[429, 436, 453, 453, 453, 221, 244, 264, 252, 352],
               [150, 185, 220, 340, 465, 129, 204, 350, 483, 613]]
        self.buttons = []
        for i in range(10):
            button = ttk.Button(self.root, text=f"{i+1}" if i < 9 else "OTRO", command=lambda i=i: self.on_button_click(i))
            self.buttons.append(button)
            canvas.create_window(pos[0][i], pos[1][i], window=button)

    def on_button_click(self, num):
        self.button_number = num

    def submit_info(self):
        self.nombre_voluntario = self.entry_nombre.get()
        self.info_adicional = self.entry_otro.get()
        if self.nombre_voluntario and self.button_number is not None:
            self.root.quit()
        else:
            self.label_error.config(text="Por favor, complete todos los campos.")

class Medidor:
    def __init__(self, nombre_voluntario, button_number, info_adicional):
        self.nombre_voluntario = nombre_voluntario
        self.button_number = button_number
        self.info_adicional = info_adicional
        self.k_resorte = ((73.1 * (10 ** 9)) * (1.81 * (10 ** (-3)))) / (8 * (8.94 ** 3) * 13 * (1 + (0.5 / (8.94 ** 2))))
        self.medidas = []
        self.area = 1  # en cm2
        self.newt_kpn = 0.101972
        self.kgcm_kpa = 98.0665
        self.setup_measurement()

    def setup_measurement(self):
        # Aquí va la lógica para configurar la medición
        # Por ejemplo, cargar la imagen self.ruta_imagen = os.path.abspath("../Aplicacion/im.png")
        self.image_height = 720
        self.image_width = 1080
        self.center = [550, 0]
        self.scroll = 10
        self.img = cv2.imread(self.ruta_imagen)
        cv2.imshow('DOLORIMETRO', self.img)
        self.medidas = []
        cv2.setMouseCallback('DOLORIMETRO', self.process_mouse_event, param=[self.center, self.medidas, self.ruta_imagen])
        cv2.waitKey(0)
        self.save_measurements()

    def process_mouse_event(self, event, x, y, flags, l):
        clone = cv2.imread(l[2])
        cntr = l[0]
        medidas = l[1]
        if event == cv2.EVENT_LBUTTONDOWN:
            # Lógica para manejar la medición
            # Aquí se puede incluir el cálculo y la visualización
            pass
        # Continuar con el resto de la lógica de eventos del mouse

    def save_measurements(self):
        # Lógica para guardar las mediciones en un archivo
        pass

class Archivo:
    @staticmethod
    def guardar_en_txt(nombre_voluntario, fecha_hora, lugar, medidas_kp, medidas_newton):
        nombre_archivo = f"{nombre_voluntario}_{fecha_hora}.txt"
        carpeta_destino = os.path.abspath("../Medidas")
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
        nombre_archivo = os.path.join(carpeta_destino, nombre_archivo)
        with open(nombre_archivo, 'w') as file:
            file.write(f"Voluntario: {nombre_voluntario}\n")
            file.write(f"Fecha y Hora: {fecha_hora}\n")
            file.write(f"Lugar de Medición: {lugar}\n\n")
            for i in range(len(medidas_kp)):
                file.write(f"MEDIDA {i + 1}: {medidas_kp[i]} Kgf/cm2   {medidas_newton[i]} kPa\n")

    @staticmethod
    def guardar_en_excel(nombre_voluntario, fecha_hora, lugar, medidas_kp, medidas_newton):
        archivo_excel = os.path.join(os.path.abspath("../Medidas"), "mediciones_voluntarios.xlsx")
        if os.path.exists(archivo_excel):
            df = pd.read_excel(archivo_excel)
        else:
            df = pd.DataFrame(columns=["Voluntario", "Fecha y Hora", "Lugar de Medición", "Mediciones Kgf/cm2", "Mediciones kPa"])
        
        nueva_fila = {
            "Voluntario": nombre_voluntario,
            "Fecha y Hora": fecha_hora,
            "Lugar de Medición": lugar,
            "Mediciones Kgf/cm2": "MEDIDAS(Kgf/cm2)",
            "Mediciones kPa": "MEDIDAS (kPa)"
        }
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        for i in range(len(medidas_kp)):
            medicion_fila = {
                "Voluntario": None,
                "Fecha y Hora": None,
                "Lugar de Medición": None,
                "Mediciones Kgf/cm2": medidas_kp[i],
                "Mediciones kPa": medidas_newton[i]
            }
            df = pd.concat([df, pd.DataFrame([medicion_fila])], ignore_index=True)

        df.to_excel(archivo_excel, index=False, engine='openpyxl')

# Ejecución del programa
if __name__ == "__main__":
    registro = RegistroVoluntario()
    if registro.nombre_voluntario:
        medidor = Medidor(registro.nombre_voluntario, registro.button_number, registro.info_adicional)