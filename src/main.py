import sys
import os

RUTA_SRC = os.path.dirname(os.path.abspath(__file__))
if RUTA_SRC not in sys.path:
    sys.path.insert(0, RUTA_SRC)

from PyQt6.QtWidgets import QApplication, QSplashScreen, QDialog
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont, QIcon, QLinearGradient, QPen
from PyQt6.QtCore import Qt, QRect, QTimer

from database.db_manager import inicializar_db, obtener_configuracion, obtener_perfiles
from ui.profile_selector import ProfileSelector
from ui.control_panel import ControlPanel
from ui.projector_view import ProjectorView
from ui.stage_view import StageView
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

    # 2. PANTALLA DE CARGA (SPLASH PRO)
    pixmap = QPixmap(500, 280)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Fondo oscuro con borde
    painter.setBrush(QColor("#0B1020"))
    painter.setPen(QPen(QColor("#1E293B"), 2))
    painter.drawRoundedRect(1, 1, 498, 278, 15, 15)
    
    # Línea de carga neón
    grad = QLinearGradient(0, 0, 500, 0)
    grad.setColorAt(0, QColor("#A855F7"))
    grad.setColorAt(1, QColor("#3B82F6"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(grad)
    painter.drawRect(1, 270, 498, 10)
    
    # Textos
    painter.setPen(QColor("white"))
    painter.setFont(QFont("Segoe UI", 30, QFont.Weight.Black))
    painter.drawText(QRect(0, 50, 500, 80), Qt.AlignmentFlag.AlignCenter, "LuminaCast Studio")
    
    painter.setPen(QColor("#8A3FFC"))
    painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
    painter.drawText(QRect(0, 130, 500, 30), Qt.AlignmentFlag.AlignCenter, "INICIANDO SISTEMA...")

    painter.setPen(QColor("#94A3B8"))
    painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
    painter.drawText(QRect(0, 180, 500, 30), Qt.AlignmentFlag.AlignCenter, f"Perfil: {congregacion_activa}")
    
    painter.end()
    
    splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
    splash.show()
    
    # 3. LANZAR VENTANAS
    def iniciar_app():
        app.proyector = ProjectorView(congregacion_activa)
        app.stage_view = StageView(congregacion_activa) 
        
        gestionar_pantallas(app.proyector, app.stage_view) 
        
        app.panel_control = ControlPanel(app.proyector, app.stage_view, congregacion_activa) 
        
        idx_control = obtener_configuracion("pantalla_control")
        if idx_control and str(idx_control).isdigit():
            pantallas = QGuiApplication.screens()
            if int(idx_control) < len(pantallas):
                geo = pantallas[int(idx_control)].geometry()
                app.panel_control.move(geo.left() + 50, geo.top() + 50)
                
        app.panel_control.showMaximized()
        splash.finish(app.panel_control)

    QTimer.singleShot(1800, iniciar_app)
    return app.exec()

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("LuminaCast")
    ruta_icono = os.path.join(os.path.dirname(__file__), '../assets/icono.ico')
    if os.path.exists(ruta_icono):
        app.setWindowIcon(QIcon(ruta_icono))
    sys.exit(arrancar_luminacast(app))

if __name__ == '__main__':
    main()