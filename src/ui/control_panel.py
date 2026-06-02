# src/ui/control_panel.py
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LuminaCast - Panel de Control")
        self.resize(900, 600) # Tamaño inicial cómodo
        
        # UI Temporal para comprobar que funciona
        layout = QVBoxLayout()
        bienvenida = QLabel("Bienvenido a LuminaCast\nEl centro de control está listo para ser desarrollado.")
        bienvenida.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(bienvenida)
        
        contenedor = QWidget()
        contenedor.setLayout(layout)
        self.setCentralWidget(contenedor)