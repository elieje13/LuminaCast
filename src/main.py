# src/main.py
import sys
import os

RUTA_SRC = os.path.dirname(os.path.abspath(__file__))
if RUTA_SRC not in sys.path:
    sys.path.insert(0, RUTA_SRC)

from PyQt6.QtWidgets import QApplication, QSplashScreen, QDialog
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont, QIcon, QLinearGradient
from PyQt6.QtCore import Qt, QRect, QTimer

from database.db_manager import inicializar_db
from ui.profile_selector import ProfileSelector
from ui.control_panel import ControlPanel
from ui.projector_view import ProjectorView
from core.monitors import gestionar_pantallas

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LuminaCast")
    
    ruta_icono = os.path.join(os.path.dirname(RUTA_SRC), "assets", "icono.ico")
    if os.path.exists(ruta_icono):
        app.setWindowIcon(QIcon(ruta_icono))
        
    # 1. INICIALIZAR BASE DE DATOS PRIMERO
    inicializar_db()
    
    # 2. MOSTRAR SELECTOR DE PERFILES
    selector = ProfileSelector()
    if selector.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0) # Si el usuario cierra la ventana con la X, el programa termina
        
    # Extraemos el nombre de la congregación seleccionada
    congregacion_activa = selector.congregacion_seleccionada

    # 3. PANTALLA DE CARGA (SPLASH SCREEN DINÁMICO)
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
    
    # Pintamos el nombre real de la congregación escogida
    painter.setPen(QColor("#94a3b8")) 
    painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Medium))
    painter.drawText(QRect(0, 150, 600, 30), Qt.AlignmentFlag.AlignCenter, congregacion_activa)

    painter.setPen(QColor("#64748b")) 
    painter.setFont(QFont("Segoe UI", 10))
    painter.drawText(QRect(0, 250, 600, 30), Qt.AlignmentFlag.AlignCenter, f"Cargando entorno para {congregacion_activa}...")
    
    painter.end()
    
    splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    
    # 4. INICIO ASÍNCRONO DE LA APLICACIÓN
    def iniciar_app():
        # Pasamos el nombre a la vista del proyector
        app.proyector = ProjectorView(congregacion_activa)
        gestionar_pantallas(app.proyector)
        
        # Pasamos el nombre al panel de control
        app.panel_control = ControlPanel(app.proyector, congregacion_activa)
        app.panel_control.show()
        
        splash.finish(app.panel_control)

    QTimer.singleShot(1800, iniciar_app)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()