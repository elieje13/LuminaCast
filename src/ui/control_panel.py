# src/ui/control_panel.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QListWidget, QLabel, QPushButton)
from PyQt6.QtCore import Qt

class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LuminaCast - Panel de Control")
        self.resize(1024, 768) # Un tamaño más amplio para trabajar cómodamente

        # 1. Contenedor y Layout Principal (Horizontal)
        widget_central = QWidget()
        layout_principal = QHBoxLayout()

        # --- PANEL IZQUIERDO: Librería (Vertical) ---
        panel_izquierdo = QVBoxLayout()
        
        titulo_libreria = QLabel("Librería de Recursos")
        titulo_libreria.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Lista simulada de canciones
        self.lista_recursos = QListWidget()
        self.lista_recursos.addItems([
            "01 - Cuan Grande es Él", 
            "02 - Océanos (Donde mis pies pueden fallar)", 
            "03 - Way Maker (Aquí estás)"
        ])
        
        panel_izquierdo.addWidget(titulo_libreria)
        panel_izquierdo.addWidget(self.lista_recursos)

        # --- PANEL DERECHO: Vista Previa y Operación (Vertical) ---
        panel_derecho = QVBoxLayout()
        
        titulo_vista = QLabel("Vista Previa de Proyección")
        titulo_vista.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Pantalla negra simulando el proyector
        self.monitor_previa = QLabel("Selecciona una canción...")
        self.monitor_previa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monitor_previa.setStyleSheet("background-color: black; color: white; font-size: 24px; border: 2px solid #555;")
        
        # Botón de disparo
        self.btn_proyectar = QPushButton("▶ ENVIAR A PANTALLA EN VIVO")
        self.btn_proyectar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 15px; font-size: 16px;")
        
        panel_derecho.addWidget(titulo_vista)
        panel_derecho.addWidget(self.monitor_previa, stretch=1) # stretch=1 hace que la pantalla ocupe el máximo espacio posible
        panel_derecho.addWidget(self.btn_proyectar)

        # 2. Ensamblar los paneles en el layout principal
        # Le damos más proporción (stretch=2) al panel derecho para que sea más grande
        layout_principal.addLayout(panel_izquierdo, stretch=1)
        layout_principal.addLayout(panel_derecho, stretch=2)

        # 3. Aplicar al contenedor central
        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)