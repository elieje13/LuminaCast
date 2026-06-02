# src/ui/projector_view.py
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class ProjectorView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LuminaCast - Salida en Vivo")
        self.resize(800, 600)
        self.setStyleSheet("background-color: black; color: white;")

        # Texto por defecto al abrir la aplicación
        self.texto_en_vivo = QLabel("IPUC LAS FLORES\nBienvenidos")
        self.texto_en_vivo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texto_en_vivo.setWordWrap(True)
        
        # Tipografía grande para el proyector
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
        """Método público que el panel de control llamará para actualizar la pantalla"""
        self.texto_en_vivo.setText(texto)