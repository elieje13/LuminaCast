# src/main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.control_panel import ControlPanel

def main():
    # Inicializar la aplicación base de Qt
    app = QApplication(sys.argv)
    app.setApplicationName("LuminaCast")
    
    # Instanciar y mostrar nuestro Panel de Control
    panel_control = ControlPanel()
    panel_control.show()
    
    # Bucle de ejecución de la app
    sys.exit(app.exec())

if __name__ == "__main__":
    main()