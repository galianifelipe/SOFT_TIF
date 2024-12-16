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

class Archivador:
    def __init__(self, carpeta_destino):
        self.carpeta_destino = carpeta_destino

    def crear_archivo(self, nombre_voluntario, fecha_hora, lugar, medidas_kp, medidas_newton):
        nombre_archivo = f"{nombre_voluntario}_{fecha_hora}.txt"
        ruta_archivo = os.path.join(self.carpeta_destino, nombre_archivo)

        with open(ruta_archivo, 'w') as file:
            file.write(f"Voluntario: {nombre_voluntario}\n")
            file.write(f"Fecha y Hora: {fecha_hora}\n")
            file.write(f"Lugar de Medicion: {lugar}\n\n")
            for i in range(len(medidas_kp)):
                file.write("MEDIDA "+str(i+1)+":  "+str(medidas_kp[i])+" Kgf/cm2   "+str(medidas_newton[i])+" kPa  "+"\n")

    def actualizar_excel(self, nombre_voluntario, fecha_hora, lugar, medidas_kp, medidas_newton):
        archivo_excel = os.path.join(self.carpeta_destino, "mediciones_voluntarios.xlsx")

        if os.path.exists(archivo_excel):
            try:
                df = pd.read_excel(archivo_excel)
            except Exception as e:
                print("Error al leer el archivo Excel:", e)
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

        try:
            df.to_excel(archivo_excel, index=False, engine='openpyxl')

            workbook = load_workbook(archivo_excel)
            sheet = workbook.active

            for column in sheet.columns:
                sheet.column_dimensions[column[0].column_letter].width = 25

            workbook.save(archivo_excel)
            print(f"Archivo Excel actualizado y guardado exitosamente en: {archivo_excel}")
        except Exception as e:
            print(f"Error al guardar el archivo Excel: {e}")


class Graficador:
    def __init__(self, ruta_imagen, image_height, image_width):
        self.ruta_imagen = ruta_imagen
        self.image_height = image_height
        self.image_width = image_width
        self.center = [550, 0]
        self.scroll = 10
        self.img = cv2.imread(self.ruta_imagen)
        cv2.imshow('DOLORIMETRO', self.img)

    def procesar_evento_mouse(self, event, x, y, flags, medidas):
        clone = cv2.imread(self.ruta_imagen)
        k_resorte = ((73.1 * (10 ** 9)) * (1.81 * (10 ** (-3)))) / (8 * (8.94 ** 3) * 13 * (1 + (0.5 / (8.94 ** 2))))
        area = 1
        newt_kpn = 0.101972
        kgcm_kpa = 98.0665

        if event == cv2.EVENT_LBUTTONDOWN:
            med = str((self.center[1] / 10) * (np.pi / 24))
            a = str(med[0 ] + med[1] + med[2] + med[3] + " cm.")
            medidas.append(a)
            numero_str = ''.join(filter(lambda x: x.isdigit() or x == '.', a))
            numero_str = numero_str.rstrip('.')
            cm = float(numero_str)
            medf = k_resorte * (cm * 10 ** (-2))
            pkpcm2 = (medf * newt_kpn) / area
            kp = str(round(pkpcm2, 2))
            nw = str(round((pkpcm2 * kgcm_kpa), 2))
            winsound.Beep(300, 500)
            cv2.putText(clone, "MEDICION: " + a, (10, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1, lineType=cv2.LINE_AA)

        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                cv2.putText(clone, "Arriba", (10, 32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                self.center[1] -= self.scroll
            else:
                self.center[1] += self.scroll
                cv2.putText(clone, "Abajo", (10, 32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        _center = self.check_location(self.center)
        st = str((_center[1] / 10) * (np.pi / 24)) if _center != [550, 0] else "0,000"
        cv2.line(clone, (5, self.center[1]), (self.image_width - 5, self.center[1]), (255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
        clone = self.draw(clone, _center)
        cv2.putText(clone, "MEDIDA: " + st[0] + st[1] + st[2] + st[3] + " cm.", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1, lineType=cv2.LINE_AA)

        altura = 25
        for i in range(len(medidas)):
            a = medidas[i]
            numero_str = ''.join(filter(lambda x: x.isdigit() or x == '.', a))
            numero_str = numero_str.rstrip('.')
            cm = float(numero_str)
            medf = k_resorte * (cm * 10 ** (-2))
            pkpcm2 = (medf * newt_kpn) / area
            kp = str(round(pkpcm2, 2))
            nw = str(round((pkpcm2 * kgcm_kpa), 2))
            if altura < 700:
                cv2.putText(clone, "MEDIDA " + str(i + 1) + ": " + medidas[i][0] + medidas[i][1] + medidas[i][2] + medidas[i][3] + " cm.", (700, altura), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, kp + " Kgf/cm2", (700, altura + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, nw + " kPa", (700, altura + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                altura += 36
            else:
                cv2.putText(clone, "MEDIDA " + str(i + 1) + ": " + medidas[i][0] + medidas[i][1] + medidas[i][2] + medidas[i][3] + " cm.", (900, altura - 700), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, kp + " Kgf/cm2", (900, altura + 12 - 700), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, nw + " kPa", (900, altura + 24 - 700), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, lineType=cv2.LINE_AA)
                altura += 36

        cv2.imshow('DOLORIMETRO', clone)

    def check_location(self, center):
        if center[1] >= self.image_height:
            center[1] = self.image_height
        elif center[1] <= 0:
            center[1] = 0
        return center

    def draw(self, layer, center):
        cv2.circle(layer, tuple(center), 70, (255, 255, 255), thickness=2, lineType=cv2.LINE_AA)
        cv2.circle(layer, tuple(center), 5, (255, 255, 255), thickness=-1, lineType=cv2.LINE_AA)
        return layer


class Mouse:
    def __init__(self, graficador):
        self.graficador = graficador

    def iniciar(self):
        medidas = []
        cv2.setMouseCallback('DOLORIMETRO', self.graficador.procesar_evento_mouse, param=medidas)
        cv2.waitKey(0)
        return medidas


class Aplicacion:
    def __init__(self):
        self.carpeta_destino = os.path.abspath("../Medidas")
        ruta_imagen = os.path.join(os.path.dirname(__file__), "Aplicacion", "im.png")
        self.archivador = Archivador(self.carpeta_destino)
        self.graficador = Graficador(ruta_imagen, 720, 1080)
        self.mouse = Mouse(self.graficador)

    def obtener_datos_gui(self):
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

        root = tk.Tk()
        root.title("Registro de Voluntario")
        ruta_icono = os.path.abspath("../Aplicacion/icono.ico")
        root.iconbitmap(ruta_icono)
        root.geometry("1080x720")

        bg_image = Image.open(os.path.abspath("../Aplicacion/Fondo.png"))
        bg_photo = ImageTk.PhotoImage(bg_image)

        canvas = tk.Canvas(root, width=1080, height=720)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")

        button_number = None
        nombre_voluntario = None
        info_adicional = None

        entry_nombre = tk.Entry(root)
        canvas.create_window(875, 60, window=entry_nombre)

        label_nombre = tk.Label(root, text="Ingrese el nombre del voluntario:", bg="white")
        canvas.create_window(875, 30, window=label_nombre)

        pos = [[429, 436, 453, 453, 453, 221, 244, 264, 252, 352], [150, 185, 220, 340, 465, 129, 204, 350, 483, 613]]
        buttons = []
        for i in range(0, 9):
            button = ttk.Button(root, text=f"{i + 1}", command=lambda i=i: on_button_click(i))
            buttons.append(button)
            canvas.create_window(pos[0][i], pos[1][i], window=button)
        button = ttk.Button(root, text=f"OTRO", command=lambda: on_button_click(0))
        buttons.append(button)
        canvas.create_window(pos[0][9], pos[1][9], window=button)

        label_otro = tk.Label(root, text="Otro:", bg="white")
        canvas.create_window(875, 600, window=label_otro)

        entry_otro = tk.Entry(root)
        canvas.create_window(875, 630, window=entry_otro)

        submit_button = ttk.Button(root, text="Enviar", command=submit_info)
        canvas.create_window(875, 670, window=submit_button)

        label_error = tk.Label(root, text="", fg="red", bg="white")
        canvas.create_window(875, 700, window=label_error)

        root.mainloop()

        return nombre_voluntario, button_number, info_adicional

    def ejecutar(self):
        nombre_voluntario, button_number, otro = self.obtener_datos_gui()
        optn = ["Occipucio", "Trapecio", "Supraespinoso", "Glúteo", "Trocánter mayor", "Cervical inferior", "Segunda costilla", "Epicóndilo lateral", "Rodilla"]
        k_resorte = ((73.1 * (10 ** 9)) * (1.81 * (10 ** (-3)))) / (8 * (8.94 ** 3) * 13 * (1 + (0.5 / (8.94 ** 2))))
        medidas_newton = []
        medidas_kp = []
        area = 1  # en cm2
        newt_kpn = 0.101972
        kgcm_kpa = 98.0665

        if nombre_voluntario is not None:
            if nombre_voluntario:
                ahora = datetime.now()
                fecha_hora = ahora.strftime("%Y-%m-%d_%H-%M-%S")
                lugar = optn[button_number - 1] if button_number != 0 else otro

                if not os.path.exists(self.carpeta_destino):
                    os.makedirs(self.carpeta_destino)

                medidas = self.mouse.iniciar()

                for i in medidas:
                    numero_str = ''.join(filter(lambda x: x.isdigit() or x == '.', i))
                    numero_str = numero_str.rstrip('.')
                    cm = float(numero_str)
                    medf = k_resorte * (cm * 10 ** (-2))
                    pkpcm2 = (medf * newt_kpn) / area
                    medidas_kp.append(round(pkpcm2, 2))
                    medidas_newton.append(round((pkpcm2 * kgcm_kpa), 2))

                self.archivador.crear_archivo(nombre_voluntario, fecha_hora, lugar, medidas_kp, medidas_newton)
                self.archivador.actualizar_excel(nombre_voluntario, fecha_hora, lugar, medidas_kp, medidas_newton)

                cv2.destroyAllWindows()
            else:
                print("No se ingresó un nombre.")
        else:
            print("No se completó el registro.")


if __name__ == "__main__":
    app = Aplicacion()
    app.ejecutar()