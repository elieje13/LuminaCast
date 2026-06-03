import sys
import os

RUTA_SRC = os.path.dirname(os.path.abspath(__file__))
if RUTA_SRC not in sys.path:
    sys.path.insert(0, RUTA_SRC)

from PyQt6.QtWidgets import QApplication, QSplashScreen, QDialog
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont, QIcon, QLinearGradient
from PyQt6.QtCore import Qt, QRect, QTimer

from database.db_manager import inicializar_db, obtener_configuracion, obtener_perfiles
from ui.profile_selector import ProfileSelector
from ui.control_panel import ControlPanel
from ui.projector_view import ProjectorView
from core.monitors import gestionar_pantallas
from PyQt6.QtGui import QGuiApplication

def arrancar_luminacast(app):
    inicializar_db()
    
    # 1. VERIFICAR AUTOLOGIN
    ultimo_id = obtener_configuracion("ultimo_perfil")
    perfiles = obtener_perfiles()
    
    perfil_valido = None
    if ultimo_id:
        for p in perfiles:
            if str(p[0]) == str(ultimo_id):
                perfil_valido = p
                break
                
    if not perfil_valido:
        selector = ProfileSelector()
        if selector.exec() != QDialog.DialogCode.Accepted:
            return 0 
        congregacion_activa = selector.congregacion_seleccionada
    else:
        congregacion_activa = perfil_valido[2]

    # 2. PANTALLA DE CARGA
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
    painter.drawText(QRect(0, 150, 600, 30), Qt.AlignmentFlag.AlignCenter, congregacion_activa)
    painter.end()
    
    splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    
    # 3. LANZAR VENTANAS
    def iniciar_app():
        app.proyector = ProjectorView(congregacion_activa)
        gestionar_pantallas(app.proyector)
        app.panel_control = ControlPanel(app.proyector, congregacion_activa)
        
        idx_control = obtener_configuracion("pantalla_control")
        if idx_control and str(idx_control).isdigit():
            pantallas = QGuiApplication.screens()
            if int(idx_control) < len(pantallas):
                geo = pantallas[int(idx_control)].geometry()
                app.panel_control.move(geo.left() + 50, geo.top() + 50)
                
        app.panel_control.show()
        splash.finish(app.panel_control)

    QTimer.singleShot(1500, iniciar_app)
    return app.exec()

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("LuminaCast")
    ruta_icono = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets/icono.ico")
    if os.path.exists(ruta_icono): app.setWindowIcon(QIcon(ruta_icono))
        
    codigo_salida = 42
    while codigo_salida == 42:
        codigo_salida = arrancar_luminacast(app)
        
    sys.exit(codigo_salida)

if __name__ == "__main__":
    main()