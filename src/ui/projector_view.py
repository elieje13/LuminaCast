# src/ui/projector_view.py
from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QApplication, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt

class ProjectorView(QMainWindow):
    def __init__(self, nombre_congregacion):
        super().__init__()
        self.setWindowTitle("LuminaCast - Salida en Vivo")
        self.resize(1024, 768)
        self.setStyleSheet("background-color: black;")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.label_fondo = QLabel(self.central_widget)
        self.label_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_fondo.setStyleSheet("background-color: black;")
        self.ruta_fondo_actual = None
        
        self.texto_en_vivo = QLabel(f"{nombre_congregacion}\nBienvenidos", self.central_widget)
        self.texto_en_vivo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texto_en_vivo.setWordWrap(True)
        self.texto_en_vivo.setStyleSheet("color: white; background-color: transparent;")
        
        fuente = self.texto_en_vivo.font()
        fuente.setPointSize(45)
        fuente.setBold(True)
        self.texto_en_vivo.setFont(fuente)

        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(12)
        sombra.setColor(QColor(0, 0, 0, 255))
        sombra.setOffset(3, 3)
        self.texto_en_vivo.setGraphicsEffect(sombra)

    def resizeEvent(self, event):
        self.label_fondo.resize(self.size())
        self.texto_en_vivo.resize(self.size())
        if self.ruta_fondo_actual: self.aplicar_imagen_fondo()
        super().resizeEvent(event)

    def aplicar_imagen_fondo(self):
        pixmap = QPixmap(self.ruta_fondo_actual)
        pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
        self.label_fondo.setPixmap(pixmap)

    def cambiar_fondo(self, ruta_imagen):
        if ruta_imagen == "sin_fondo":
            self.ruta_fondo_actual = None
            self.label_fondo.clear()
            self.label_fondo.setStyleSheet("background-color: black;")
        else:
            self.ruta_fondo_actual = ruta_imagen
            self.aplicar_imagen_fondo()

    def proyectar_texto(self, texto):
        self.texto_en_vivo.setText(texto)
        self.texto_en_vivo.show() # Aseguramos que se vea

    def ocultar_proyeccion(self, ocultar):
        """Si ocultar es True, escondemos el texto"""
        if ocultar:
            self.texto_en_vivo.hide()
        else:
            self.texto_en_vivo.show()

    def closeEvent(self, event):
        QApplication.instance().quit()
        event.accept()