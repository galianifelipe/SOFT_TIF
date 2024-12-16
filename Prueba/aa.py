from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QDialog
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
import sys
from PIL import Image
import os
import numpy as np
import pandas as pd

class ImageClickDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccione un punto en la imagen")
        self.setGeometry(100, 100, 800, 600)
        self.image_path = "humano.png"  # Asegúrate de que esta imagen exista
        self.image = QPixmap(self.image_path)
        self.selected_point = None
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected_point = event.pos()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.image)
        if self.selected_point:
            pen = QPen(Qt.red, 5)
            painter.setPen(pen)
            painter.drawPoint(self.selected_point)

    def save_with_point(self, filename):
        if self.selected_point:
            painter = QPainter(self.image)
            pen = QPen(Qt.red, 10)
            painter.setPen(pen)
            painter.drawPoint(self.selected_point)
            painter.end()
            
            output_path = os.path.join(os.getcwd(), filename)
            self.image.save(output_path)
            print(f"Imagen guardada con el punto en: {output_path}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interfaz de Medición")
        self.setGeometry(100, 100, 600, 400)

        # Widgets principales
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Ingrese el nombre del voluntario")
        self.name_input.setGeometry(20, 20, 200, 30)

        self.point_dropdown = QComboBox(self)
        self.point_dropdown.setGeometry(20, 60, 200, 30)
        self.point_dropdown.addItems(["Occipucio", "Trapecio", "Supraespinoso", "Glúteo", "Otro"])
        self.point_dropdown.currentIndexChanged.connect(self.handle_point_selection)

        self.other_info_input = QLineEdit(self)
        self.other_info_input.setPlaceholderText("Ingrese información adicional")
        self.other_info_input.setGeometry(20, 100, 200, 30)
        self.other_info_input.setVisible(False)  # Ocultar inicialmente

        self.submit_button = QPushButton("Enviar", self)
        self.submit_button.setGeometry(20, 140, 100, 30)
        self.submit_button.clicked.connect(self.submit_info)

        self.info_label = QLabel(self)
        self.info_label.setGeometry(20, 180, 400, 30)
        self.info_label.setText("Seleccione un punto de medición.")

        self.volunteer_name = ""
        self.selected_point_name = ""
        self.point_coordinates = None

        # Variables para mediciones
        self.medidas_newton = []
        self.medidas_kp = []
        self.k_resorte = ((73.1 * (10 ** 9)) * (1.81 * (10 ** (-3)))) / (8 * (8.94 ** 3) * 13 * (1 + (0.5 / (8.94 ** 2))))
        self.area = 1  # en cm2
        self.newt_kpn = 0.101972
        self.kgcm_kpa = 98.0665

    def handle_point_selection(self):
        point = self.point_dropdown.currentText()
        if point == "Otro":
            self.other_info_input.setVisible(True)  # Mostrar campo de información adicional
        else:
            self.other_info_input.setVisible(False)  # Ocultar campo de información adicional

    def open_image_click_dialog(self):
        dialog = ImageClickDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.point_coordinates = dialog.selected_point
            filename = "im_1.png"  # Guardar la imagen como im_1.png
            dialog.save_with_point(filename)

    def submit_info(self):
        self.volunteer_name = self.name_input.text()
        self.selected_point_name = self.point_dropdown.currentText()
        additional_info = self.other_info_input.text() if self.other_info_input.isVisible() else ""

        if self.volunteer_name:
            if self.selected_point_name == "Otro" and self.point_coordinates:
                coord_text = f"({self.point_coordinates.x()}, {self.point_coordinates.y()})"
                self.info_label.setText(f"Voluntario: {self.volunteer_name}, Coordenadas: {coord_text}, Info: {additional_info}")
                self.save_data_to_file(coord_text, additional_info)
                self.take_measurement(coord_text)
            else:
                self.info_label.setText(f"Voluntario: {self.volunteer_name}, Punto: {self.selected_point_name}")
                self.save_data_to_file(self.selected_point_name, additional_info)
                self.take_measurement(self.selected_point_name)
        else:
            self.info_label.setText("Por favor, ingrese el nombre del voluntario.")

    def save_data_to_file(self, point_info, additional_info):
        # Guardar los datos en un archivo de texto
        filename = "mediciones.txt"
        with open(filename, 'a') as file:
            file.write(f"Voluntario: {self.volunteer_name}, Punto: {point_info}, Info: {additional_info}\n")
        print(f"Datos guardados en: {filename}")

    def take_measurement(self, point_info):
        # Simulación de la toma de mediciones
        print(f"Tomando mediciones para {point_info}...")

        # Simulación de mediciones
        medida = np.random.uniform(1, 10)  # Simulación de una medición en cm
        medida_kp = self.k_resorte * (medida * 10 ** (-2))
        pkpcm2 = (medida_kp * self.newt_kpn) / self.area
        self.medidas_kp.append(round(pkpcm2, 2))
        self.medidas_newton.append(round((pkpcm2 * self.kgcm_kpa), 2))

        # Guardar mediciones en un archivo Excel
        self.save_measurements_to_excel()

    def save_measurements_to_excel(self):
        # Definir la ruta del archivo Excel
        archivo_excel = "mediciones_voluntarios.xlsx"

        # Verifica si el archivo Excel ya existe
        if os.path.exists(archivo_excel):
            try:
                # Si el archivo existe, cargar el contenido
                df = pd.read_excel(archivo_excel)
            except Exception as e:
                print("Error al leer el archivo Excel:", e)
                df = pd.DataFrame(columns=["Voluntario", "Punto", "Mediciones Kgf/cm2", "Mediciones kPa"])
        else:
            # Crear un nuevo DataFrame si el archivo no existe
            df = pd.DataFrame(columns=["Voluntario", "Punto", "Mediciones Kgf/cm2", "Mediciones kPa"])

        # Crear una fila con los datos de medición
        nueva_fila = {
            "Voluntario": self.volunteer_name,
            "Punto": self.selected_point_name,
            "Mediciones Kgf/cm2": self.medidas_kp[-1] if self.medidas_kp else None,
            "Mediciones kPa": self.medidas_newton[-1] if self.medidas_newton else None
        }

        # Agregar la fila al DataFrame
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)

        # Guardar el DataFrame en el archivo Excel
        try:
            df.to_excel(archivo_excel, index=False)
            print(f"Archivo Excel actualizado y guardado exitosamente en: {archivo_excel}")
        except Exception as e:
            print(f"Error al guardar el archivo Excel: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.open_image_click_dialog()  # Abrir la ventana de selección de imagen
    sys.exit(app.exec_())