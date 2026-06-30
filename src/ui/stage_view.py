from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QFont, QColor

class StageView(QMainWindow):
    def __init__(self, nombre_congregacion):
        super().__init__()
        self.setWindowTitle(f"Stage Display (Interno) - {nombre_congregacion}")
        self.resize(1024, 768)
        self.setStyleSheet("background-color: #000000; color: white;")
        
        central = QWidget()
        self.setCentralWidget(central)
        lyt_main = QVBoxLayout(central)
        lyt_main.setContentsMargins(30, 30, 30, 30)

        # ================= HEADER: RELOJ Y CRONÓMETRO =================
        lyt_header = QHBoxLayout()
        
        self.lbl_reloj = QLabel("00:00:00")
        self.lbl_reloj.setStyleSheet("color: #38BDF8; font-size: 45px; font-weight: 900; font-family: 'Courier New', monospace;")
        self.lbl_reloj.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        self.lbl_cronometro = QLabel("00:00")
        self.lbl_cronometro.setStyleSheet("color: #10B981; font-size: 45px; font-weight: 900; font-family: 'Courier New', monospace;")
        self.lbl_cronometro.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        
        lyt_header.addWidget(self.lbl_reloj)
        lyt_header.addStretch(1)
        lyt_header.addWidget(self.lbl_cronometro)
        
        lyt_main.addLayout(lyt_header)
        lyt_main.addSpacing(10)

        # ================= TEXTO ACTUAL =================
        self.lbl_actual = QLabel("LuminaCast Studio\nListo para iniciar...")
        self.lbl_actual.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_actual.setStyleSheet("color: #FACC15; font-size: 60px; font-weight: 900;")
        self.lbl_actual.setWordWrap(True)
        lyt_main.addWidget(self.lbl_actual, stretch=3)

        # ================= TEXTO SIGUIENTE =================
        self.lbl_siguiente = QLabel("")
        self.lbl_siguiente.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        self.lbl_siguiente.setStyleSheet("color: #94A3B8; font-size: 40px; font-weight: bold;")
        self.lbl_siguiente.setWordWrap(True)
        lyt_main.addWidget(self.lbl_siguiente, stretch=1)

        # ================= FOOTER: MENSAJE INTERNO ALERTA =================
        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setStyleSheet("background-color: #EF4444; color: white; font-size: 30px; font-weight: bold; padding: 15px; border-radius: 8px;")
        self.lbl_mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mensaje.hide() # Oculto por defecto
        
        lyt_main.addSpacing(10)
        lyt_main.addWidget(self.lbl_mensaje)

        # ================= TIMERS =================
        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.actualizar_reloj)
        self.timer_reloj.start(1000)
        self.actualizar_reloj()

        self.timer_crono = QTimer(self)
        self.timer_crono.timeout.connect(self.tick_cronometro)
        self.tiempo_restante = 0

    def actualizar_reloj(self):
        hora_actual = QTime.currentTime().toString("hh:mm:ss AP")
        self.lbl_reloj.setText(hora_actual)

    def tick_cronometro(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            minutos, segundos = divmod(self.tiempo_restante, 60)
            # Cambia a color rojo si queda menos de 1 minuto
            color = "#EF4444" if self.tiempo_restante <= 60 else "#10B981"
            self.lbl_cronometro.setStyleSheet(f"color: {color}; font-size: 45px; font-weight: 900; font-family: 'Courier New', monospace;")
            self.lbl_cronometro.setText(f"{minutos:02d}:{segundos:02d}")
        else:
            self.timer_crono.stop()
            self.lbl_cronometro.setText("00:00")
            self.lbl_cronometro.setStyleSheet("color: #EF4444; font-size: 45px; font-weight: 900; font-family: 'Courier New', monospace;")

    def iniciar_cronometro(self, segundos):
        self.tiempo_restante = segundos
        self.tick_cronometro() # Actualiza de inmediato
        self.timer_crono.start(1000)

    def detener_cronometro(self):
        self.timer_crono.stop()
        self.tiempo_restante = 0
        self.lbl_cronometro.setText("00:00")
        self.lbl_cronometro.setStyleSheet("color: #10B981; font-size: 45px; font-weight: 900; font-family: 'Courier New', monospace;")

    def proyectar_texto(self, actual, siguiente=""):
        self.lbl_actual.setText(actual)
        if siguiente:
            self.lbl_siguiente.setText(f"Sig: {siguiente}")
        else:
            self.lbl_siguiente.setText("")

    def mostrar_mensaje_interno(self, mensaje):
        if mensaje.strip():
            self.lbl_mensaje.setText(f"⚠️ {mensaje}")
            self.lbl_mensaje.show()
        else:
            self.lbl_mensaje.hide()

    def ocultar_proyeccion(self, ocultar):
        if ocultar:
            self.lbl_actual.hide()
            self.lbl_siguiente.hide()
        else:
            self.lbl_actual.show()
            self.lbl_siguiente.show()