# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import simpledialog, ttk
import numpy as np
import cv2
from tkinter import Tk
from datetime import datetime
import os
import winsound
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pandas as pd
from openpyxl import load_workbook
import ctypes


# =========================
# Manejo de calibración
# =========================

def cargar_k():
    archivo = r"C:\SOFT_TIF\Aplicacion\calibracion.txt"
    if os.path.exists(archivo):
        try:
            with open(archivo, "r") as f:
                return float(f.read().strip())
        except:
            print("Error leyendo calibracion.txt, se usará valor por defecto.")
    # Valor por defecto si no hay archivo o hubo error
    k_defecto = ((73.1*(10**9))*(1.81*(10**(-3))))/(8*(8.94**3)*13*(1+(0.5/(8.94**2))))
    guardar_k(k_defecto)
    return k_defecto

def guardar_k(k):
    archivo = r"C:\SOFT_TIF\Aplicacion\calibracion.txt"
    with open(archivo, "w") as f:
        f.write(str(k))

# =========================
# Ventana inicial
# =========================

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

    def abrir_calibracion():
        global k_resorte
        ruta_imagen = r"C:\SOFT_TIF\Aplicacion\im.png"
        img = cv2.imread(ruta_imagen)
        medidas_calibracion = []
        center = [550, 0]
        scroll = 10
        image_height = 720
        image_width = 1080
        instrucciones = (
            "INSTRUCCIONES DE CALIBRACIÓN:\n"
            "1. Coloque el algómetro sobre la balanza.\n"
            "2. Aplique presión hasta que la balanza marque 2 kgf.\n"
            "3. Cuando llegue a 2 kgf, haga CLICK IZQUIERDO para registrar.\n"
            "4. Repita varias veces.\n"
            "5. Presione ESC para finalizar."
        )
        print(instrucciones)

        # dibuja instructivo UNA vez (PIL) y devuelve imagen BGR reutilizable
        def hacer_overlay_instructivo(base):
            # reutiliza la implementación previa de dibujar_instructivo pero sin medir cada loop
            import textwrap
            padding = 12
            rect_w = 420
            rect_x2 = image_width - 20
            rect_x1 = max(10, rect_x2 - rect_w)
            rect_y1 = max(10, image_height // 4)
            try:
                font_title = ImageFont.truetype("arial.ttf", 28)
                font_text = ImageFont.truetype("arial.ttf", 16)
            except Exception:
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()
            title = "INSTRUCTIVO"
            paragraphs = instrucciones.split('\n')

            pil = Image.fromarray(cv2.cvtColor(base, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil)

            # medir por píxeles (once) y wrap por píxeles
            def measure(text, font):
                try:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    return (bbox[2] - bbox[0], bbox[3] - bbox[1])
                except Exception:
                    try:
                        return font.getsize(text)
                    except Exception:
                        return (len(text) * 7, 12)

            max_text_w = rect_w - 2 * padding

            def wrap_paragraph(par):
                words = par.split()
                if not words:
                    return [""]
                lines = []
                cur = words[0]
                for w in words[1:]:
                    cand = cur + " " + w
                    if measure(cand, font_text)[0] <= max_text_w:
                        cur = cand
                    else:
                        lines.append(cur)
                        cur = w
                if cur:
                    lines.append(cur)
                return lines

            wrapped_lines = []
            for p in paragraphs:
                wrapped_lines.extend(wrap_paragraph(p))

            title_w, title_h = measure(title, font_title)
            _, line_h = measure("Ay", font_text)
            line_spacing = int(line_h * 1.35)
            rect_h = padding * 2 + title_h + 8 + line_spacing * len(wrapped_lines)
            rect_y2 = rect_y1 + rect_h
            if rect_y2 > image_height - 10:
                rect_y2 = image_height - 10
                rect_y1 = max(10, rect_y2 - rect_h)

            # crear overlay semitransparente con OpenCV por eficiencia
            overlay = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
            cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 0), -1)
            alpha = 0.62
            base_with_overlay = base.copy()
            cv2.addWeighted(overlay, alpha, base_with_overlay, 1 - alpha, 0, base_with_overlay)

            # ahora dibujar texto con PIL sobre la imagen combinada (solo una vez)
            pil_final = Image.fromarray(cv2.cvtColor(base_with_overlay, cv2.COLOR_BGR2RGB))
            draw_final = ImageDraw.Draw(pil_final)
            x_text = rect_x1 + padding
            y_text = rect_y1 + padding
            title_x = rect_x1 + (rect_w - title_w) // 2
            draw_final.text((title_x, y_text), title, font=font_title, fill=(220, 30, 30))
            y_text += title_h + 8
            for ln in wrapped_lines:
                draw_final.text((x_text, y_text), ln, font=font_text, fill=(255, 255, 255))
                y_text += line_spacing
            draw_final.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], outline=(200, 200, 200), width=1)
            return cv2.cvtColor(np.array(pil_final), cv2.COLOR_RGB2BGR)

        # pre-render del instructivo sobre la imagen base (se hace una sola vez)
        base_img = img.copy()
        instructivo_bgr = hacer_overlay_instructivo(base_img)

        # estado compartido entre callback y loop principal
        dirty = {"flag": True}  # fuerza primer dibujado
        last_med_text = [None]  # guarda último texto de medición para mostrar
        running = {"val": True}

        def evento_calibracion(event, x, y, flags, param):
            nonlocal medidas_calibracion, center, last_med_text
            # callback ligero: modificar estado y marcar dirty. NO llamar imshow aquí.
            if event == cv2.EVENT_LBUTTONDOWN:
                centro_val = [center[0], max(0, min(center[1], image_height))]
                med = (centro_val[1] / 10) * (np.pi / 24)
                med = max(0.0, med)
                medidas_calibracion.append(med)
                winsound.Beep(500, 150)
                center[1] = 0
                last_med_text[0] = f"Medida calibración: {med:.3f} cm"
                dirty["flag"] = True

            elif event == cv2.EVENT_MOUSEWHEEL:
                # invertir sentido
                if flags > 0:
                    center[1] += scroll
                else:
                    center[1] -= scroll
                center[1] = max(0, min(center[1], image_height))
                dirty["flag"] = True

        # crear ventana y centrar
        cv2.namedWindow("CALIBRACIÓN", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("CALIBRACIÓN", instructivo_bgr)
        user32 = ctypes.windll.user32
        sw = user32.GetSystemMetrics(0)
        sh = user32.GetSystemMetrics(1)
        cx = (sw - image_width) // 2
        cy = (sh - image_height) // 2
        cv2.moveWindow("CALIBRACIÓN", cx, cy)
        cv2.setMouseCallback("CALIBRACIÓN", evento_calibracion)

        # bucle principal: solo redibuja cuando dirty (o cada 100ms para mantener responsive)
        try:
            while running["val"]:
                key = cv2.waitKey(30) & 0xFF
                if key == 27:
                    break
                if cv2.getWindowProperty("CALIBRACIÓN", cv2.WND_PROP_VISIBLE) < 1:
                    break
                if dirty["flag"]:
                    # partimos de la imagen instructivo pre-renderizada
                    frame = instructivo_bgr.copy()
                    # dibujar línea y círculo actualizados
                    cv2.line(frame, (5, center[1]), (image_width - 5, center[1]), (255, 255, 255), 2)
                    cv2.circle(frame, tuple(center), 5, (255, 255, 255), -1)
                    # mostrar posible texto de última medición
                    if last_med_text[0]:
                        cv2.putText(frame, last_med_text[0], (10, 700), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow("CALIBRACIÓN", frame)
                    dirty["flag"] = False
        finally:
            # destruir de forma segura
            try:
                if cv2.getWindowProperty("CALIBRACIÓN", cv2.WND_PROP_VISIBLE) >= 0:
                    cv2.destroyWindow("CALIBRACIÓN")
            except cv2.error:
                pass

        # procesar calibración al finalizar
        if len(medidas_calibracion) > 0:
            desplazamiento_medio = np.mean(medidas_calibracion) / 100  # en metros (medidas están en cm)
            fuerza = 2 * 9.81  # 2 kgf ≈ 19.62 N
            k_resorte = fuerza / desplazamiento_medio
            guardar_k(k_resorte)
            print(f"Calibración completada (2 kgf). Nuevo valor de k = {k_resorte:.5f} N/m")
        else:
            print("No se realizaron mediciones de calibración.")

    # Crear la ventana
    root = tk.Tk()
    root.title("Registro de Voluntario")
    ruta_icono = r"C:\SOFT_TIF\Aplicacion\icono.ico"
    root.iconbitmap(ruta_icono)

    # bloquear tamaño y centrar la ventana en pantalla
    width, height = 1080, 720
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.resizable(False, False)

    ruta_fondo = r"C:\SOFT_TIF\Aplicacion\Fondo.png"
    bg_image = Image.open(ruta_fondo)
    bg_photo = ImageTk.PhotoImage(bg_image)

    canvas = tk.Canvas(root, width=1080, height=720)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Variables
    button_number = None
    nombre_voluntario = None
    info_adicional = None

    # Campo de entrada para el nombre
    entry_nombre = tk.Entry(root)
    canvas.create_window(875, 60, window=entry_nombre)

    label_nombre = tk.Label(root, text="Ingrese el nombre del voluntario:", bg="white")
    canvas.create_window(875, 30, window=label_nombre)

    # Botones de lugar
    pos=[[429,436,453,453,453,221,244,264,252,352],
         [150,185,220,340,465,129,204,350,483,613]]
    for i in range(0, 9):
        button = ttk.Button(root, text=f"{i+1}", command=lambda i=i: on_button_click(i))
        canvas.create_window(pos[0][i], pos[1][i], window=button)
    button = ttk.Button(root, text=f"OTRO", command=lambda i=i: on_button_click(0))
    canvas.create_window(pos[0][9], pos[1][9], window=button)

    label_otro = tk.Label(root, text="Otro:", bg="white")
    canvas.create_window(875, 600, window=label_otro)
    entry_otro = tk.Entry(root)
    canvas.create_window(875, 630, window=entry_otro)

    submit_button = ttk.Button(root, text="Enviar", command=submit_info)
    canvas.create_window(875, 670, window=submit_button)

    label_error = tk.Label(root, text="", fg="red", bg="white")
    canvas.create_window(875, 700, window=label_error)

    # Botón calibración
    boton_calibracion = ttk.Button(root, text="Calibración", command=abrir_calibracion)
    canvas.create_window(80, 700, window=boton_calibracion)

    root.mainloop()
    return nombre_voluntario, button_number, info_adicional, k_resorte

# =========================
# Funciones auxiliares
# =========================
def process_mouse_event(event,x,y,flags, l):
    clone = cv2.imread(l[2])
    cntr = l[0]
    medidas = l[1]
    global k_resorte
    area=1  #en cm2
    newt_kpn=0.101972
    kgcm_kpa=98.0665
    cv2.line(clone, (5,50), (250,50), (255,255,255), thickness=2, lineType=cv2.LINE_AA) 

    # siempre validar posición antes de calcular medidas para evitar negativos
    _center = check_location(cntr)
    _center[1] = max(0, _center[1])  # asegurar no negativo

    if event == cv2.EVENT_LBUTTONDOWN:
            med_val = (_center[1]/10)*(np.pi/24)
            med_val = max(0.0, med_val)
            med_str = f"{med_val:.3f}"
            a = med_str + " cm."
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
            print(k_resorte)
            # devolver la barra a 0 inmediatamente después del click
            cntr[1] = 0

    if event == cv2.EVENT_MOUSEWHEEL:
        # invertir arriba/abajo: rueda positiva -> bajar (mayor y), negativa -> subir (menor y)
        if flags > 0:
            cntr[1] += scroll
            cv2.putText(clone, "Abajo", (10,32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        else:
            cntr[1] -= scroll
            cv2.putText(clone, "Arriba", (10,32), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        # asegurar que no se cuenten desplazamientos negativos
        cntr[1] = max(0, min(cntr[1], image_height))

    _center = check_location(cntr)
    if _center==[550, 0]:
            st="0,000"
    else:
            st=str((_center[1]/10)*(np.pi/24))
    cv2.line(clone, (5,cntr[1]), (image_width-5,cntr[1]), (255,255,255), thickness=2, lineType=cv2.LINE_AA)
    clone = draw(clone, _center)
    cv2.putText(clone, "MEDIDA: " + st[0]+st[1]+st[2]+st[3]+" cm.", (10,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 1, lineType=cv2.LINE_AA)
    altura=25
    alt=25
    al=25
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
                cv2.putText(clone, "MEDIDA "+str(i+1)+": "+ medidas[i][0]+medidas[i][1]+medidas[i][2]+medidas[i][3]+" cm.", (650,altura), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, kp + " Kgf/cm2", (650,altura+12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, nw + " kPa", (650,altura+24), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                altura+=36
            elif alt < 700:
                cv2.putText(clone, "MEDIDA "+str(i+1)+": "+ medidas[i][0]+medidas[i][1]+medidas[i][2]+medidas[i][3]+" cm.", (800,alt), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, kp + " Kgf/cm2", (800,alt+12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, nw + " kPa", (800,alt+24), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                alt+=36    
            else:
                cv2.putText(clone, "MEDIDA "+str(i+1)+": "+ medidas[i][0]+medidas[i][1]+medidas[i][2]+medidas[i][3]+" cm.", (960,al), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, kp + " Kgf/cm2", (960,al+12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                cv2.putText(clone, nw + " kPa", (960,al+24), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1, lineType=cv2.LINE_AA)
                al+=36 
            
            
    cv2.imshow('DOLORIMETRO', clone) 

def check_location(center):
    if center[1] >= image_height:
        center[1] = image_height
    elif center[1] <= 0:
        center[1] = 0
    return center

def draw(layer, center):
    cv2.circle(layer, tuple(center), 70, (255,255,255), 2, cv2.LINE_AA)
    cv2.circle(layer, tuple(center), 5, (255,255,255), -1, cv2.LINE_AA)
    return layer

# =========================
# PROGRAMA PRINCIPAL
# =========================

k_resorte = cargar_k()
nombre_voluntario, button_number, otro, k_resorte = obtener_datos_gui()
optn=["Occipucio", "Trapecio", "Supraespinoso", "Glúteo", "Trocánter mayor",
      "Cervical inferior", "Segunda costilla", "Epicóndilo lateral", "Rodilla"]


medidas_newton=[]
medidas_kp=[]
area=1  # cm2
newt_kpn=0.101972
kgcm_kpa=98.0665

if nombre_voluntario is not None:
    if nombre_voluntario:
        ahora = datetime.now()
        fecha_hora = ahora.strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"{nombre_voluntario}_{fecha_hora}.txt"
    else:
        print("No se ingresó un nombre.")
    
    if button_number!=0 or button_number!=None:
         lugar=optn[button_number]

    carpeta_destino = r"C:\SOFT_TIF\Medidas"
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    nombre_archivo = os.path.join(carpeta_destino, nombre_archivo)
    ruta_imagen = r"C:\SOFT_TIF\Aplicacion\im.png"
    image_height = 720
    image_width = 1080
    center = [550,0]
    scroll = 10
    img = cv2.imread(ruta_imagen)
    # crear ventana OpenCV no redimensionable y centrarla
    cv2.namedWindow('DOLORIMETRO', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('DOLORIMETRO', img)
    user32 = ctypes.windll.user32
    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    cx = (sw - image_width) // 2
    cy = (sh - image_height) // 2
    cv2.moveWindow('DOLORIMETRO', cx, cy)
    a=[]
    cv2.setMouseCallback('DOLORIMETRO', lambda e,x,y,f,p: process_mouse_event(e,x,y,f,[center,a,ruta_imagen]))
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
    
    archivo_excel = os.path.join(carpeta_destino,"mediciones_voluntarios.xlsx")

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
        "Lugar de Medición": otro if button_number == 0 else lugar,
        "Mediciones Kgf/cm2": "MEDIDAS(Kgf/cm2)",  
        "Mediciones kPa": "MEDIDAS (kPa)"  
    }
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

    for i in range(len(a)):
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
    cv2.destroyAllWindows()
else:
    print("No se completó el registro.")
