# src/main.py
import sys
import os

RUTA_SRC = os.path.dirname(os.path.abspath(__file__))
if RUTA_SRC not in sys.path:
    sys.path.insert(0, RUTA_SRC)

# Importamos QTimer y removemos la librería 'time' estándar
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont, QIcon, QLinearGradient
from PyQt6.QtCore import Qt, QRect, QTimer

from ui.control_panel import ControlPanel
from ui.projector_view import ProjectorView
from core.monitors import gestionar_pantallas

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LuminaCast")
    
    # 1. CONFIGURAR EL ÍCONO
    ruta_icono = os.path.join(os.path.dirname(RUTA_SRC), "assets", "icono.ico")
    if os.path.exists(ruta_icono):
        app.setWindowIcon(QIcon(ruta_icono))
    
    # 2. PANTALLA DE CARGA (SPLASH SCREEN PROFESIONAL)
    pixmap = QPixmap(600, 300)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    gradiente = QLinearGradient(0, 0, 600, 300)
    gradiente.setColorAt(0.0, QColor("#0f172a")) 
    gradiente.setColorAt(1.0, QColor("#020617")) 
    painter.fillRect(pixmap.rect(), gradiente)
    
    painter.fillRect(0, 295, 600, 5, QColor("#3b82f6"))

    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
    painter.drawText(QRect(0, 60, 600, 80), Qt.AlignmentFlag.AlignCenter, "LuminaCast")
    
    painter.setPen(QColor("#94a3b8")) 
    painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Medium))
    painter.drawText(QRect(0, 150, 600, 30), Qt.AlignmentFlag.AlignCenter, "IPUC LAS FLORES")

    painter.setPen(QColor("#64748b")) 
    painter.setFont(QFont("Segoe UI", 10))
    painter.drawText(QRect(0, 250, 600, 30), Qt.AlignmentFlag.AlignCenter, "Iniciando sistema y cargando base de datos...")
    
    painter.end()
    
    splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    
    # 3. INICIO ASÍNCRONO DE LA APLICACIÓN
    def iniciar_app():
        # Atamos las variables a 'app' para evitar que Python las elimine de la memoria
        app.proyector = ProjectorView()
        gestionar_pantallas(app.proyector)
        
        app.panel_control = ControlPanel(app.proyector)
        app.panel_control.show()
        
        # Ocultar la pantalla de carga al mostrar el panel
        splash.finish(app.panel_control)

    # El QTimer espera 1800 milisegundos (1.8 seg) y luego ejecuta la función iniciar_app sin congelar
    QTimer.singleShot(1800, iniciar_app)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()