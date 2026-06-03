from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QApplication, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
from PyQt6.QtGui import QPixmap, QColor, QFont
from PyQt6.QtCore import Qt, QTimer, QTime, QPropertyAnimation, QEasingCurve, QVariantAnimation

class ProjectorView(QMainWindow):
    def __init__(self, nombre_congregacion):
        super().__init__()
        self.setWindowTitle("LuminaCast - Salida en Vivo")
        self.resize(1024, 768)
        self.setStyleSheet("background-color: black;")
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.fuente_actual = "Segoe UI"
        self.tamano_letra_actual = 45
        self.color_letra_actual = "#ffffff"
        
        self.reloj_tamano = 20
        self.reloj_posicion = "Arriba - Derecha"

        self.transiciones = {
            "cancion": {"tipo": "Fade", "vel": 300},
            "biblia": {"tipo": "Fade", "vel": 300}
        }

        # --- CAPAS DE FONDO ---
        self.label_fondo_base = QLabel(self.central_widget)
        self.label_fondo_base.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label_fondo_entrante = QLabel(self.central_widget)
        self.label_fondo_entrante.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.efecto_opacidad_fondo = QGraphicsOpacityEffect(self.label_fondo_entrante)
        self.label_fondo_entrante.setGraphicsEffect(self.efecto_opacidad_fondo)
        self.efecto_opacidad_fondo.setOpacity(0.0)
        
        self.animacion_fondo = QPropertyAnimation(self.efecto_opacidad_fondo, b"opacity")
        self.animacion_fondo.setDuration(600)
        self.animacion_fondo.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animacion_fondo.finished.connect(self._al_terminar_animacion_fondo)
        self.ruta_fondo_actual = None

        # --- TEXTO EN VIVO (SIN CONTENEDOR, DIRECTO AL CENTRAL WIDGET) ---
        self.texto_en_vivo = QLabel(f"{nombre_congregacion}\nBienvenidos", self.central_widget)
        self.texto_en_vivo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.texto_en_vivo.setWordWrap(True)
        
        # Efecto de sombra 
        self.efecto_sombra = QGraphicsDropShadowEffect()
        self.efecto_sombra.setBlurRadius(12)
        self.efecto_sombra.setColor(QColor(0, 0, 0, 255))
        self.efecto_sombra.setOffset(3, 3)
        self.texto_en_vivo.setGraphicsEffect(self.efecto_sombra)

        # --- NUEVO SISTEMA DE ANIMACIÓN DE TEXTO (Por Color/Alpha) ---
        self.animacion_texto_out = QVariantAnimation()
        self.animacion_texto_out.setStartValue(1.0)
        self.animacion_texto_out.setEndValue(0.0)
        self.animacion_texto_out.valueChanged.connect(self._actualizar_opacidad_texto)
        self.animacion_texto_out.finished.connect(self._cambiar_texto_intermedio)

        self.animacion_texto_in = QVariantAnimation()
        self.animacion_texto_in.setStartValue(0.0)
        self.animacion_texto_in.setEndValue(1.0)
        self.animacion_texto_in.valueChanged.connect(self._actualizar_opacidad_texto)
        
        self.texto_pendiente = ""
        self.actualizar_estilo_texto(self.fuente_actual, self.tamano_letra_actual, self.color_letra_actual)

        # Reloj y Logo
        self.label_reloj = QLabel("", self.central_widget)
        self.label_reloj.setStyleSheet("color: white; background-color: rgba(0,0,0,150); padding: 5px; border-radius: 5px;")
        self.label_reloj.setFont(QFont("Segoe UI", self.reloj_tamano, QFont.Weight.Bold))
        self.label_reloj.hide()
        
        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.actualizar_reloj)
        self.timer_reloj.start(1000)

        self.label_logo = QLabel(self.central_widget)
        self.label_logo.setStyleSheet("background-color: transparent;")
        self.label_logo.hide()

    def actualizar_estilo_texto(self, fuente, tamano, color_hex):
        self.fuente_actual = fuente
        self.tamano_letra_actual = tamano
        self.color_letra_actual = color_hex
        self.texto_en_vivo.setFont(QFont(fuente, tamano, QFont.Weight.Bold))
        self._actualizar_opacidad_texto(1.0) # Asegurar que esté 100% visible

    def _actualizar_opacidad_texto(self, opacidad):
        """ Cambia la transparencia del color de la letra y de la sombra sin usar QGraphicsOpacityEffect """
        color_texto = QColor(self.color_letra_actual)
        color_texto.setAlphaF(opacidad)
        rgba_texto = f"rgba({color_texto.red()}, {color_texto.green()}, {color_texto.blue()}, {color_texto.alpha()})"
        
        self.texto_en_vivo.setStyleSheet(f"color: {rgba_texto}; background-color: transparent;")
        
        color_sombra = QColor(0, 0, 0)
        color_sombra.setAlphaF(opacidad)
        self.efecto_sombra.setColor(color_sombra)

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
        self.label_fondo_base.resize(self.size())
        self.label_fondo_entrante.resize(self.size())
        self.texto_en_vivo.resize(self.size())
        if self.ruta_fondo_actual: 
            pixmap = QPixmap(self.ruta_fondo_actual).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.label_fondo_base.setPixmap(pixmap)
        self.actualizar_reloj()
        super().resizeEvent(event)

    def configurar_transiciones(self, c_tipo, c_vel, b_tipo, b_vel):
        self.transiciones["cancion"]["tipo"] = c_tipo
        self.transiciones["cancion"]["vel"] = c_vel
        self.transiciones["biblia"]["tipo"] = b_tipo
        self.transiciones["biblia"]["vel"] = b_vel

    def cambiar_fondo(self, ruta_imagen):
        if self.animacion_fondo.state() == QPropertyAnimation.State.Running:
            self.animacion_fondo.stop()
            self._al_terminar_animacion_fondo()

        if ruta_imagen == "sin_fondo":
            self.ruta_fondo_actual = None
            self.label_fondo_base.clear()
            self.label_fondo_entrante.clear()
        else:
            self.ruta_fondo_actual = ruta_imagen
            pixmap = QPixmap(ruta_imagen).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.label_fondo_entrante.setPixmap(pixmap)
            self.efecto_opacidad_fondo.setOpacity(0.0)
            self.animacion_fondo.setStartValue(0.0)
            self.animacion_fondo.setEndValue(1.0)
            self.animacion_fondo.start()

    def _al_terminar_animacion_fondo(self):
        if self.ruta_fondo_actual:
            pixmap = QPixmap(self.ruta_fondo_actual).scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.label_fondo_base.setPixmap(pixmap)
        else:
            self.label_fondo_base.clear()
        self.efecto_opacidad_fondo.setOpacity(0.0)
        self.label_fondo_entrante.clear()

    def proyectar_texto(self, texto, contexto="cancion"):
        if self.texto_en_vivo.text() == texto: return
            
        self.texto_pendiente = texto
        config = self.transiciones.get(contexto, {"tipo": "Fade", "vel": 300})

        if config["tipo"] == "Corte":
            if self.animacion_texto_out.state() == QVariantAnimation.State.Running: self.animacion_texto_out.stop()
            if self.animacion_texto_in.state() == QVariantAnimation.State.Running: self.animacion_texto_in.stop()
            self._actualizar_opacidad_texto(1.0)
            self.texto_en_vivo.setText(texto)
        else:
            vel = config["vel"]
            self.animacion_texto_out.setDuration(int(vel * 0.6)) 
            self.animacion_texto_in.setDuration(vel)
            
            if self.animacion_texto_out.state() == QVariantAnimation.State.Running: self.animacion_texto_out.stop()
            self.animacion_texto_out.start()

    def _cambiar_texto_intermedio(self):
        self.texto_en_vivo.setText(self.texto_pendiente)
        self.animacion_texto_in.start()

    def ocultar_proyeccion(self, ocultar): 
        self.texto_en_vivo.setVisible(not ocultar)
        
    def closeEvent(self, event): 
        event.accept()