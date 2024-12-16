from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QOpenGLWidget, QLineEdit, QComboBox, QDialog
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
import sys
from PIL import Image
import os

class ImageClickDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccione un punto en la imagen")
        self.setGeometry(100, 100, 800, 600)
        self.image_path = "humano.png"
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
            image = Image.open(self.image_path)
            point_x = self.selected_point.x()
            point_y = self.selected_point.y()
            
            painter = QPainter(self.image)
            pen = QPen(Qt.red, 10)
            painter.setPen(pen)
            painter.drawPoint(QPoint(point_x, point_y))
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

        self.submit_button = QPushButton("Enviar", self)
        self.submit_button.setGeometry(20, 100, 100, 30)
        self.submit_button.clicked.connect(self.submit_info)

        self.info_label = QLabel(self)
        self.info_label.setGeometry(20, 140, 400, 30)
        self.info_label.setText("Seleccione un punto de medición.")

        self.volunteer_name = ""
        self.selected_point_name = ""
        self.point_coordinates = None

    def handle_point_selection(self):
        point = self.point_dropdown.currentText()
        if point == "Otro":
            self.open_image_click_dialog()

    def open_image_click_dialog(self):
        dialog = ImageClickDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.point_coordinates = dialog.selected_point
            filename = f"{self.name_input.text()}_custom_point.png"
            dialog.save_with_point(filename)

    def submit_info(self):
        self.volunteer_name = self.name_input.text()
        self.selected_point_name = self.point_dropdown.currentText()
        if self.volunteer_name:
            if self.selected_point_name == "Otro" and self.point_coordinates:
                coord_text = f"({self.point_coordinates.x()}, {self.point_coordinates.y()})"
                self.info_label.setText(f"Voluntario: {self.volunteer_name}, Coordenadas: {coord_text}")
            else:
                self.info_label.setText(f"Voluntario: {self.volunteer_name}, Punto: {self.selected_point_name}")
        else:
            self.info_label.setText("Por favor, ingrese el nombre del voluntario.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
