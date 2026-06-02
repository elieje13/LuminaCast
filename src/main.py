# src/main.py
import sys
import os
import time

RUTA_SRC = os.path.dirname(os.path.abspath(__file__))
if RUTA_SRC not in sys.path:
    sys.path.insert(0, RUTA_SRC)

# Importamos nuevas herramientas de dibujo (QLinearGradient, QRect)
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont, QIcon, QLinearGradient
from PyQt6.QtCore import Qt, QRect

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
    # Tamaño más ancho y cinematográfico (600x300)
    pixmap = QPixmap(600, 300)
    
    painter = QPainter(pixmap)
    # Mejorar la calidad del dibujo (Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Fondo con Degradado (De azul noche a casi negro)
    gradiente = QLinearGradient(0, 0, 600, 300)
    gradiente.setColorAt(0.0, QColor("#0f172a")) # Noche oscuro
    gradiente.setColorAt(1.0, QColor("#020617")) # Negro profundo
    painter.fillRect(pixmap.rect(), gradiente)
    
    # Línea de acento en la parte inferior (Azul brillante)
    painter.fillRect(0, 295, 600, 5, QColor("#3b82f6"))

    # Título Principal (LuminaCast)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
    painter.drawText(QRect(0, 60, 600, 80), Qt.AlignmentFlag.AlignCenter, "LuminaCast")
    
    # Subtítulo (Organización)
    painter.setPen(QColor("#94a3b8")) # Gris azulado suave
    painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Medium))
    painter.drawText(QRect(0, 150, 600, 30), Qt.AlignmentFlag.AlignCenter, "IPUC LAS FLORES")

    # Texto de estado de carga
    painter.setPen(QColor("#64748b")) # Gris más oscuro
    painter.setFont(QFont("Segoe UI", 10))
    painter.drawText(QRect(0, 250, 600, 30), Qt.AlignmentFlag.AlignCenter, "Iniciando sistema y cargando base de datos...")
    
    painter.end()
    
    splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)