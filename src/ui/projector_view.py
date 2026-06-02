# src/ui/projector_view.py
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QApplication
from PyQt6.QtCore import Qt

class ProjectorView(QMainWindow):
    def __init__(self, nombre_congregacion):
        super().__init__()
        self.setWindowTitle("LuminaCast - Salida en Vivo")
        self.resize(800, 600)
        self.setStyleSheet("background-color: black; color: white;")

        self.texto_en_vivo = QLabel(f"{nombre_congregacion}\nBienvenidos")
        self.texto_en_vivo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texto_en_vivo.setWordWrap(True)
        
        fuente = self.texto_en_vivo.font()
        fuente.setPointSize(45)
        fuente.setBold(True)
        self.texto_en_vivo.setFont(fuente)

        layout = QVBoxLayout()
        layout.addWidget(self.texto_en_vivo)
        
        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)

    def proyectar_texto(self, texto):
        self.texto_en_vivo.setText(texto)

    def closeEvent(self, event):
        """Si el usuario cierra la ventana del proyector, se apaga toda la aplicación"""
        QApplication.instance().quit()
        event.accept()