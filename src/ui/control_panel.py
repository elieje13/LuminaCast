import re
import os
import shutil
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QListWidgetItem, QLabel, QPushButton,
                             QDialog, QLineEdit, QTextEdit, QMessageBox, QMenu, QApplication, QFileDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from database.db_manager import (inicializar_db, obtener_todas_las_canciones, 
                                 obtener_letra_cancion, agregar_cancion, 
                                 actualizar_cancion, eliminar_cancion, guardar_configuracion)

class DialogoCancion(QDialog):
    def __init__(self, parent=None, song_id=None, titulo="", letra=""):
        super().__init__(parent)
        self.song_id = song_id
        self.setWindowTitle("Editar Canción" if song_id else "Agregar Nueva Canción")
        self.resize(500, 600)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Título:"))
        self.input_titulo = QLineEdit(titulo)
        layout.addWidget(self.input_titulo)
        layout.addWidget(QLabel("Letra:"))
        self.input_letra = QTextEdit()
        self.input_letra.setPlainText(letra)
        layout.addWidget(self.input_letra)
        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        btn_guardar.clicked.connect(self.guardar_bd)
        layout.addWidget(btn_guardar)
        self.setLayout(layout)
        
    def guardar_bd(self):
        if self.song_id: actualizar_cancion(self.song_id, self.input_titulo.text(), self.input_letra.toPlainText())
        else: agregar_cancion(self.input_titulo.text(), self.input_letra.toPlainText())
        self.accept()

class ControlPanel(QMainWindow):
    def __init__(self, proyector, nombre_congregacion):
        super().__init__()
        self.proyector = proyector
        self.setWindowTitle(f"LuminaCast | {nombre_congregacion}")
        self.resize(1200, 800)
        self.esta_visible = True

        inicializar_db()
        self.crear_menu_superior() 

        widget_central = QWidget()
        layout_base = QVBoxLayout()
        layout_columnas = QHBoxLayout()

        # --- COLUMNAS ---
        self.lista_recursos = QListWidget()
        self.lista_recursos.itemClicked.connect(self.cargar_diapositivas_cancion)
        
        self.lista_diapositivas = QListWidget()
        self.lista_diapositivas.itemClicked.connect(self.previsualizar_diapositiva)
        self.lista_diapositivas.itemDoubleClicked.connect(self.disparar_diapositiva_directo)
        
        # Panel Derecho (Preview)
        panel_derecho = QVBoxLayout()
        self.btn_ojo = QPushButton("👁️")
        self.btn_ojo.setFixedSize(40, 40)
        self.btn_ojo.setStyleSheet("background-color: #333; font-size: 20px; border-radius: 5px;")
        self.btn_ojo.clicked.connect(self.toggle_ojo)
        
        self.monitor_previa = QLabel("Selecciona un verso...")
        self.monitor_previa.setStyleSheet("background-color: #111; color: white; padding: 10px; border: 1px solid #444;")
        
        # BOTÓN VERDE GRANDE
        self.btn_proyectar = QPushButton("▶ ENVIAR A PANTALLA (Go Live)")
        self.btn_proyectar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 20px; font-size: 16px; border-radius: 5px;")
        self.btn_proyectar.clicked.connect(self.enviar_en_vivo)
        
        panel_derecho.addWidget(self.btn_ojo)
        panel_derecho.addWidget(self.monitor_previa, stretch=1)
        panel_derecho.addWidget(self.btn_proyectar)

        layout_columnas.addWidget(self.lista_recursos, stretch=2)
        layout_columnas.addWidget(self.lista_diapositivas, stretch=2)
        layout_columnas.addLayout(panel_derecho, stretch=3)

        # --- GALERÍA ---
        panel_fondos = QVBoxLayout()
        layout_fondos_header = QHBoxLayout()
        layout_fondos_header.addWidget(QLabel("🖼️ Galería"))
        btn_add_img = QPushButton("➕")
        btn_add_img.setFixedSize(30, 30)
        btn_add_img.clicked.connect(self.importar_fondo)
        layout_fondos_header.addWidget(btn_add_img)
        
        self.lista_fondos = QListWidget()
        self.lista_fondos.setViewMode(QListWidget.ViewMode.IconMode)
        self.lista_fondos.setIconSize(QSize(120, 70))
        self.lista_fondos.setFixedHeight(120)
        self.lista_fondos.itemClicked.connect(self.aplicar_fondo)
        
        panel_fondos.addLayout(layout_fondos_header)
        panel_fondos.addWidget(self.lista_fondos)

        layout_base.addLayout(layout_columnas, 1)
        layout_base.addLayout(panel_fondos)
        widget_central.setLayout(layout_base)
        self.setCentralWidget(widget_central)
        self.cargar_canciones_desde_db()
        self.cargar_galeria_fondos()

    def importar_fondo(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", "Images (*.png *.jpg *.jpeg)")
        if ruta:
            dest = os.path.join(os.path.dirname(__file__), '../../assets/fondos', os.path.basename(ruta))
            shutil.copy(ruta, dest)
            self.cargar_galeria_fondos()

    def crear_menu_superior(self):
        menu_bar = self.menuBar()
        menu_archivo = menu_bar.addMenu("Archivo")
        menu_archivo.addAction("Cerrar Perfil").triggered.connect(lambda: QApplication.exit(42))
        menu_archivo.addAction("Salir").triggered.connect(self.close)

    def toggle_ojo(self):
        self.esta_visible = not self.esta_visible
        self.btn_ojo.setText("👁️" if self.esta_visible else "🙈")
        self.proyector.ocultar_proyeccion(not self.esta_visible)

    def cargar_galeria_fondos(self):
        self.lista_fondos.clear()
        item_sin = QListWidgetItem("Sin Fondo")
        item_sin.setData(Qt.ItemDataRole.UserRole, "sin_fondo")
        self.lista_fondos.addItem(item_sin)
        ruta = os.path.join(os.path.dirname(__file__), '../../assets/fondos')
        for f in os.listdir(ruta):
            if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                item = QListWidgetItem()
                item.setIcon(QIcon(os.path.join(ruta, f)))
                item.setData(Qt.ItemDataRole.UserRole, os.path.join(ruta, f))
                self.lista_fondos.addItem(item)

    def aplicar_fondo(self, item): self.proyector.cambiar_fondo(item.data(Qt.ItemDataRole.UserRole))

    def cargar_canciones_desde_db(self):
        self.lista_recursos.clear()
        for song_id, titulo in obtener_todas_las_canciones():
            item = QListWidgetItem(titulo)
            item.setData(Qt.ItemDataRole.UserRole, song_id)
            self.lista_recursos.addItem(item)

    def cargar_diapositivas_cancion(self, item):
        self.lista_diapositivas.clear()
        for bloque in obtener_letra_cancion(item.data(Qt.ItemDataRole.UserRole)).split("\n\n"):
            if bloque.strip(): self.lista_diapositivas.addItem(QListWidgetItem(bloque.strip()))

    def previsualizar_diapositiva(self, item): self.monitor_previa.setText(item.text())

    def enviar_en_vivo(self):
        if "Selecciona" not in self.monitor_previa.text():
            self.proyector.proyectar_texto(re.sub(r'\[.*?\]', '', self.monitor_previa.text()).strip())

    def disparar_diapositiva_directo(self, item):
        self.previsualizar_diapositiva(item); self.enviar_en_vivo()

    def closeEvent(self, event): QApplication.exit(0)