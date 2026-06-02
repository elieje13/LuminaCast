# src/ui/control_panel.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QListWidget, QLabel, QPushButton)
from PyQt6.QtCore import Qt

class ControlPanel(QMainWindow):
    def __init__(self, proyector):
        super().__init__()
        self.proyector = proyector
        self.setWindowTitle("LuminaCast - Panel de Control")
        self.resize(1024, 768)

        widget_central = QWidget()
        layout_principal = QHBoxLayout()

        # --- PANEL IZQUIERDO ---
        panel_izquierdo = QVBoxLayout()
        titulo_libreria = QLabel("Librería de Recursos")
        titulo_libreria.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.lista_recursos = QListWidget()
        self.lista_recursos.addItems([
            "01 - Cuan Grande es Él", 
            "02 - Océanos (Donde mis pies pueden fallar)", 
            "03 - Way Maker (Aquí estás)"
        ])
        # Conectar el clic en la lista para actualizar la vista previa
        self.lista_recursos.itemClicked.connect(self.previsualizar_item)
        
        panel_izquierdo.addWidget(titulo_libreria)
        panel_izquierdo.addWidget(self.lista_recursos)

        # --- PANEL DERECHO ---
        panel_derecho = QVBoxLayout()
        titulo_vista = QLabel("Vista Previa de Proyección")
        titulo_vista.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        self.monitor_previa = QLabel("Selecciona una canción de la lista...")
        self.monitor_previa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monitor_previa.setStyleSheet("background-color: black; color: white; font-size: 24px; border: 2px solid #555;")
        
        self.btn_proyectar = QPushButton("▶ ENVIAR A PANTALLA EN VIVO")
        self.btn_proyectar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 15px; font-size: 16px;")
        # Conectar el botón verde para enviar al proyector
        self.btn_proyectar.clicked.connect(self.enviar_en_vivo)
        
        panel_derecho.addWidget(titulo_vista)
        panel_derecho.addWidget(self.monitor_previa, stretch=1)
        panel_derecho.addWidget(self.btn_proyectar)

        layout_principal.addLayout(panel_izquierdo, stretch=1)
        layout_principal.addLayout(panel_derecho, stretch=2)

        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

    # --- FUNCIONES DE LÓGICA ---
    def previsualizar_item(self, item):
        """Muestra el texto en el monitor central (sin enviarlo al público)"""
        self.monitor_previa.setText(f"Letra de:\n{item.text()}")

    def enviar_en_vivo(self):
        """Toma lo que hay en la vista previa y lo dispara a la pantalla 2"""
        texto_actual = self.monitor_previa.text()
        self.proyector.proyectar_texto(texto_actual)

    def closeEvent(self, event):
        """Se activa automáticamente cuando el usuario da clic en la 'X' de esta ventana"""
        self.proyector.close() # Fuerza el cierre de la ventana del proyector
        event.accept()         # Acepta el cierre de la ventana principal