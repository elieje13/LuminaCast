# src/ui/control_panel.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QPushButton)
from PyQt6.QtCore import Qt
from database.db_manager import inicializar_db, obtener_todas_las_canciones, obtener_letra_cancion

class ControlPanel(QMainWindow):
    def __init__(self, proyector):
        super().__init__()
        self.proyector = proyector
        self.setWindowTitle("LuminaCast - Panel de Control")
        self.resize(1200, 768)

        # Inicializar la Base de Datos local
        inicializar_db()

        widget_central = QWidget()
        layout_principal = QHBoxLayout()

        # =================================================================
        # COLUMNA 1: LIBRERÍA DE CANCIONES (Izquierda)
        # =================================================================
        panel_izquierdo = QVBoxLayout()
        titulo_libreria = QLabel("📋 Canciones")
        titulo_libreria.setStyleSheet("font-weight: bold; font-size: 14px; color: #aaa;")
        
        self.lista_recursos = QListWidget()
        self.lista_recursos.itemClicked.connect(self.cargar_diapositivas_cancion)
        
        panel_izquierdo.addWidget(titulo_libreria)
        panel_izquierdo.addWidget(self.lista_recursos)

        # =================================================================
        # COLUMNA 2: DIAPOSITIVAS / SECUENCIA (Centro)
        # =================================================================
        panel_central = QVBoxLayout()
        titulo_diapositivas = QLabel("🔲 Diapositivas del Tema")
        titulo_diapositivas.setStyleSheet("font-weight: bold; font-size: 14px; color: #aaa;")
        
        self.lista_diapositivas = QListWidget()
        self.lista_diapositivas.itemClicked.connect(self.previsualizar_diapositiva)
        self.lista_diapositivas.itemDoubleClicked.connect(self.disparar_diapositiva_directo)
        
        panel_central.addWidget(titulo_diapositivas)
        panel_central.addWidget(self.lista_diapositivas)

        # =================================================================
        # COLUMNA 3: MONITOR DE VISTA PREVIA Y CONTROL (Derecha)
        # =================================================================
        panel_derecho = QVBoxLayout()
        titulo_vista = QLabel("🖥️ Vista Previa")
        titulo_vista.setStyleSheet("font-weight: bold; font-size: 14px; color: #aaa;")
        
        self.monitor_previa = QLabel("Selecciona un verso...")
        self.monitor_previa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monitor_previa.setWordWrap(True)
        self.monitor_previa.setStyleSheet("background-color: #111; color: #fff; font-size: 20px; border: 2px solid #333; padding: 10px;")
        
        self.btn_proyectar = QPushButton("▶ ENVIAR A PANTALLA (Go Live)")
        self.btn_proyectar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 15px; font-size: 15px; border-radius: 4px;")
        self.btn_proyectar.clicked.connect(self.enviar_en_vivo)
        
        panel_derecho.addWidget(titulo_vista)
        panel_derecho.addWidget(self.monitor_previa, stretch=1)
        panel_derecho.addWidget(self.btn_proyectar)

        # =================================================================
        # ENSAMBLE DE LA ARQUITECTURA (Distribución de espacio)
        # =================================================================
        # PyQt6 requiere números enteros (int) para el stretch. 
        # Multiplicamos por 2 para mantener la proporción sin usar decimales.
        layout_principal.addLayout(panel_izquierdo, stretch=2)  # Proporción 2
        layout_principal.addLayout(panel_central, stretch=2)    # Proporción 2
        layout_principal.addLayout(panel_derecho, stretch=3)    # Proporción 3

        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

        # Cargar los datos desde SQLite
        self.cargar_canciones_desde_db()

    # --- LÓGICA ---
    def cargar_canciones_desde_db(self):
        self.lista_recursos.clear()
        canciones = obtener_todas_las_canciones()
        for song_id, titulo in canciones:
            item = QListWidgetItem(titulo)
            item.setData(Qt.ItemDataRole.UserRole, song_id)
            self.lista_recursos.addItem(item)

    def cargar_diapositivas_cancion(self, item):
        self.lista_diapositivas.clear()
        song_id = item.data(Qt.ItemDataRole.UserRole)
        letra_completa = obtener_letra_cancion(song_id)
        
        diapositivas = letra_completa.split("\n\n")
        
        for bloque in diapositivas:
            if bloque.strip():
                item_diapositiva = QListWidgetItem(bloque.strip())
                self.lista_diapositivas.addItem(item_diapositiva)
                
        if self.lista_diapositivas.count() > 0:
            self.lista_diapositivas.setCurrentRow(0)
            self.previsualizar_diapositiva(self.lista_diapositivas.item(0))

    def previsualizar_diapositiva(self, item):
        self.monitor_previa.setText(item.text())

    def enviar_en_vivo(self):
        texto_actual = self.monitor_previa.text()
        if "Selecciona un verso..." not in texto_actual:
            self.proyector.proyectar_texto(texto_actual)

    def disparar_diapositiva_directo(self, item):
        self.previsualizar_diapositiva(item)
        self.enviar_en_vivo()

    def closeEvent(self, event):
        self.proyector.close()
        event.accept()