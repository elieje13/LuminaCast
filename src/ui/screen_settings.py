from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QPushButton, QMessageBox
from PyQt6.QtGui import QGuiApplication
from database.db_manager import guardar_configuracion, obtener_configuracion

class ScreenSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Pantallas")
        self.resize(350, 250)
        
        # Aplicamos el tema oscuro a esta ventana también
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: white; }
            QLabel { color: white; font-weight: bold; margin-top: 5px; }
            QComboBox { background-color: #2d2d2d; color: white; border: 1px solid #3d3d3d; padding: 5px; border-radius: 3px; }
            QComboBox QAbstractItemView { background-color: #2d2d2d; color: white; selection-background-color: #007acc; }
            QPushButton { background-color: #007acc; color: white; border: none; padding: 10px; border-radius: 4px; font-weight: bold; margin-top: 15px; }
            QPushButton:hover { background-color: #005f9e; }
        """)
        
        layout = QVBoxLayout()
        
        self.pantallas = QGuiApplication.screens()
        nombres_pantallas = [f"{p.name()} ({p.geometry().width()}x{p.geometry().height()})" for p in self.pantallas]
        
        self.combos = {}
        roles = [
            ("pantalla_audience", "🖥️ Pantalla de Audiencia (Proyector/Live):"), 
            ("pantalla_control", "🎛️ Pantalla de Control (Operador Principal):"), 
            ("pantalla_stage", "🎸 Stage Display (Músicos/Oradores):")
        ]
                 
        for clave, etiqueta in roles:
            layout.addWidget(QLabel(etiqueta))
            combo = QComboBox()
            combo.addItems(nombres_pantallas)
            
            guardado = obtener_configuracion(clave)
            if guardado and guardado.isdigit() and int(guardado) < len(self.pantallas):
                combo.setCurrentIndex(int(guardado))
                
            layout.addWidget(combo)
            self.combos[clave] = combo
            
        btn_guardar = QPushButton("💾 Guardar Configuración")
        btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(btn_guardar)
        
        self.setLayout(layout)

    def guardar(self):
        for clave, combo in self.combos.items():
            guardar_configuracion(clave, combo.currentIndex())
            
        QMessageBox.information(self, "Configuración Guardada", "Los cambios se aplicarán la próxima vez que abras LuminaCast.")
        self.accept()