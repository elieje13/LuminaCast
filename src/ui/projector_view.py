from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QApplication, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QColor, QFont
from PyQt6.QtCore import Qt, QTimer, QTime

class ProjectorView(QMainWindow):
    def __init__(self, nombre_congregacion):
        super().__init__()
        self.setWindowTitle("LuminaCast - Salida en Vivo")
        self.resize(1024, 768)
        self.setStyleSheet("background-color: black;")
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Variables de estilo por defecto
        self.fuente_actual = "Segoe UI"
        self.tamano_letra_actual = 45
        self.color_letra_actual = "#ffffff"
        
        self.reloj_tamano = 20
        self.reloj_posicion = "Arriba - Derecha"

        # Capa 1: Fondo
        self.label_fondo = QLabel(self.central_widget)
        self.label_fondo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ruta_fondo_actual = None
        
        # Capa 2: Texto Principal
        self.texto_en_vivo = QLabel(f"{nombre_congregacion}\nBienvenidos", self.central_widget)
        self.texto_en_vivo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texto_en_vivo.setWordWrap(True)
        self.actualizar_estilo_texto(self.fuente_actual, self.tamano_letra_actual, self.color_letra_actual)
        self.aplicar_sombra(self.texto_en_vivo)

        # Capa 3: Reloj (Flotante)
        self.label_reloj = QLabel("", self.central_widget)
        self.label_reloj.setStyleSheet("color: white; background-color: rgba(0,0,0,150); padding: 5px; border-radius: 5px;")
        self.label_reloj.setFont(QFont("Segoe UI", self.reloj_tamano, QFont.Weight.Bold))
        self.label_reloj.hide()
        
        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.actualizar_reloj)
        self.timer_reloj.start(1000)

        # Capa 4: Logo (Flotante)
        self.label_logo = QLabel(self.central_widget)
        self.label_logo.setStyleSheet("background-color: transparent;")
        self.label_logo.hide()

    def aplicar_sombra(self, widget):
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(12)
        sombra.setColor(QColor(0, 0, 0, 255))
        sombra.setOffset(3, 3)
        widget.setGraphicsEffect(sombra)

    def actualizar_estilo_texto(self, fuente, tamano, color_hex):
        self.fuente_actual = fuente
        self.tamano_letra_actual = tamano
        self.color_letra_actual = color_hex
        
        self.texto_en_vivo.setFont(QFont(fuente, tamano, QFont.Weight.Bold))
        self.texto_en_vivo.setStyleSheet(f"color: {color_hex}; background-color: transparent;")

    def configurar_reloj(self, tamano, posicion):
        self.reloj_tamano = tamano
        self.reloj_posicion = posicion
        self.label_reloj.setFont(QFont("Segoe UI", tamano, QFont.Weight.Bold))
        self.actualizar_reloj()

    def actualizar_reloj(self):
        self.label_reloj.setText(QTime.currentTime().toString("hh:mm:ss AP"))
        self.label_reloj.adjustSize()
        
        margen = 20
        y = margen if "Arriba" in self.reloj_posicion else self.height() - self.label_reloj.height() - margen
        x = margen if "Izquierda" in self.reloj_posicion else self.width() - self.label_reloj.width() - margen
        
        self.label_reloj.move(x, y)

    def toggle_reloj(self, estado):
        self.label_reloj.setVisible(estado)

    def toggle_logo(self, estado, ruta=None):
        if estado and ruta:
            pixmap = QPixmap(ruta).scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.label_logo.setPixmap(pixmap)
            self.label_logo.adjustSize()
            self.label_logo.move(20, 20)
            self.label_logo.show()
        else:
            self.label_logo.hide()

    def resizeEvent(self, event):
        self.label_fondo.resize(self.size())
        self.texto_en_vivo.resize(self.size())
        if self.ruta_fondo_actual: self.cambiar_fondo(self.ruta_fondo_actual)
        self.actualizar_reloj()
        super().resizeEvent(event)

    def cambiar_fondo(self, ruta_imagen):
        if ruta_imagen == "sin_fondo":
            self.ruta_fondo_actual = None
            self.label_fondo.clear()
        else:
            self.ruta_fondo_actual = ruta_imagen
            pixmap = QPixmap(ruta_imagen).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.label_fondo.setPixmap(pixmap)

    def proyectar_texto(self, texto): self.texto_en_vivo.setText(texto)
    def ocultar_proyeccion(self, ocultar): self.texto_en_vivo.setVisible(not ocultar)
    def closeEvent(self, event): QApplication.instance().quit(); event.accept()