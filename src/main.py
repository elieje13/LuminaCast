# src/main.py
import sys
import os

# --- ARQUITECTURA DE RUTAS ---
# Obtenemos la ruta absoluta de la carpeta 'src' y la añadimos al sistema de búsqueda de Python
RUTA_SRC = os.path.dirname(os.path.abspath(__file__))
if RUTA_SRC not in sys.path:
    sys.path.insert(0, RUTA_SRC)

# Ahora sí podemos importar los módulos de forma limpia
from PyQt6.QtWidgets import QApplication
from ui.control_panel import ControlPanel
from ui.projector_view import ProjectorView
from core.monitors import gestionar_pantallas

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LuminaCast")
    
    # 1. Instanciar el proyector
    proyector = ProjectorView()
    
    # 2. Aplicar la lógica inteligente de pantallas
    gestionar_pantallas(proyector)
    
    # 3. Instanciar y mostrar el panel de control para el operador
    panel_control = ControlPanel(proyector)
    panel_control.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()