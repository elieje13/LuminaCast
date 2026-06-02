import re
import os
import shutil
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QListWidgetItem, QLabel, QPushButton,
                             QDialog, QLineEdit, QTextEdit, QMessageBox, QApplication, QMenu, QTabWidget, QFileDialog, QFontComboBox, QSpinBox, QColorDialog, QComboBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QColor
from database.db_manager import (inicializar_db, obtener_todas_las_canciones, 
                                 obtener_letra_cancion, agregar_cancion, 
                                 actualizar_cancion, eliminar_cancion, guardar_configuracion)
from ui.screen_settings import ScreenSettingsDialog

class DialogoCancion(QDialog):
    def __init__(self, parent=None, song_id=None, titulo="", letra=""):
        super().__init__(parent)
        self.song_id = song_id
        self.setWindowTitle("Editar Canción" if song_id else "Agregar Nueva Canción")
        self.resize(500, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Título:"))
        self.input_titulo = QLineEdit(titulo)
        self.input_titulo.setStyleSheet("background-color: #2d2d2d; border: 1px solid #3d3d3d; padding: 8px; border-radius: 4px; color: white;")
        layout.addWidget(self.input_titulo)
        
        layout.addWidget(QLabel("Letra (Separa estrofas con un espacio):"))
        self.input_letra = QTextEdit()
        self.input_letra.setPlainText(letra)
        self.input_letra.setStyleSheet("background-color: #2d2d2d; border: 1px solid #3d3d3d; padding: 8px; border-radius: 4px; color: white;")
        layout.addWidget(self.input_letra)
        
        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold; border-radius: 4px;")
        btn_guardar.clicked.connect(self.guardar_bd)
        layout.addWidget(btn_guardar)
        self.setLayout(layout)
        
    def guardar_bd(self):
        if not self.input_titulo.text().strip():
            QMessageBox.warning(self, "Error", "El título no puede estar vacío.")
            return
        if self.song_id: actualizar_cancion(self.song_id, self.input_titulo.text(), self.input_letra.toPlainText())
        else: agregar_cancion(self.input_titulo.text(), self.input_letra.toPlainText())
        self.accept()

class TextSettingsDialog(QDialog):
    def __init__(self, parent, font_actual, tamano_actual, color_actual):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Letra (Live)")
        self.resize(300, 250)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Fuente:"))
        self.combo_fuente = QFontComboBox()
        self.combo_fuente.setCurrentText(font_actual)
        self.combo_fuente.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(self.combo_fuente)

        layout.addWidget(QLabel("Tamaño:"))
        self.spin_tamano = QSpinBox()
        self.spin_tamano.setRange(20, 150)
        self.spin_tamano.setValue(tamano_actual)
        self.spin_tamano.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(self.spin_tamano)

        layout.addWidget(QLabel("Color del Texto:"))
        self.btn_color = QPushButton("Elegir Color")
        self.color_seleccionado = color_actual
        self.btn_color.setStyleSheet(f"background-color: {color_actual}; color: black; font-weight: bold;")
        self.btn_color.clicked.connect(self.elegir_color)
        layout.addWidget(self.btn_color)

        btn_guardar = QPushButton("Aplicar Cambios")
        btn_guardar.setStyleSheet("background-color: #007acc; color: white; padding: 8px;")
        btn_guardar.clicked.connect(self.accept)
        layout.addWidget(btn_guardar)
        self.setLayout(layout)

    def elegir_color(self):
        color = QColorDialog.getColor(QColor(self.color_seleccionado), self, "Elige el color del texto")
        if color.isValid():
            self.color_seleccionado = color.name()
            self.btn_color.setStyleSheet(f"background-color: {self.color_seleccionado}; color: black; font-weight: bold;")

class ClockSettingsDialog(QDialog):
    def __init__(self, parent, tamano_actual, pos_actual):
        super().__init__(parent)
        self.setWindowTitle("Configuración del Reloj")
        self.resize(300, 150)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Tamaño:"))
        self.spin_tamano = QSpinBox()
        self.spin_tamano.setRange(10, 80)
        self.spin_tamano.setValue(tamano_actual)
        self.spin_tamano.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(self.spin_tamano)

        layout.addWidget(QLabel("Posición:"))
        self.combo_pos = QComboBox()
        self.combo_pos.addItems(["Arriba - Izquierda", "Arriba - Derecha", "Abajo - Izquierda", "Abajo - Derecha"])
        self.combo_pos.setCurrentText(pos_actual)
        self.combo_pos.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(self.combo_pos)

        btn_guardar = QPushButton("Aplicar Cambios")
        btn_guardar.setStyleSheet("background-color: #007acc; color: white; padding: 8px;")
        btn_guardar.clicked.connect(self.accept)
        layout.addWidget(btn_guardar)
        self.setLayout(layout)

class ControlPanel(QMainWindow):
    def __init__(self, proyector, nombre_congregacion):
        super().__init__()
        self.proyector = proyector
        self.setWindowTitle(f"LuminaCast | {nombre_congregacion}")
        self.resize(1200, 800)
        self.aplicar_tema_oscuro()
        
        self.esta_visible = True
        self.reloj_activo = False
        self.logo_activo = False
        self.ruta_logo_global = None

        inicializar_db()
        self.crear_menu_superior() 

        widget_central = QWidget()
        layout_base = QVBoxLayout()
        layout_columnas = QHBoxLayout()

        # --- COLUMNA 1: TABS (CANCIONES Y BIBLIAS) ---
        self.tabs = QTabWidget()
        
        tab_canciones = QWidget()
        layout_canciones = QVBoxLayout(tab_canciones)
        layout_canciones.setContentsMargins(5, 10, 5, 5)
        self.input_filtro = QLineEdit()
        self.input_filtro.setPlaceholderText("🔍 Buscar canción...")
        self.input_filtro.textChanged.connect(self.filtrar_canciones)
        
        self.lista_recursos = QListWidget()
        self.lista_recursos.itemClicked.connect(self.cargar_diapositivas_cancion)
        self.lista_recursos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lista_recursos.customContextMenuRequested.connect(self.mostrar_menu_canciones)
        
        layout_canciones.addWidget(self.input_filtro)
        layout_canciones.addWidget(self.lista_recursos)
        
        tab_biblias = QWidget()
        layout_biblias = QVBoxLayout(tab_biblias)
        layout_biblias.setContentsMargins(5, 10, 5, 5)
        layout_biblias.addWidget(QLabel("📖 Selector de Libros y Capítulos (En desarrollo)"))
        self.lista_versiculos = QListWidget()
        layout_biblias.addWidget(self.lista_versiculos)

        self.tabs.addTab(tab_canciones, "🎵 Canciones")
        self.tabs.addTab(tab_biblias, "📖 Biblias")

        # --- COLUMNA 2: DIAPOSITIVAS ---
        self.lista_diapositivas = QListWidget()
        self.lista_diapositivas.itemClicked.connect(self.previsualizar_diapositiva)
        self.lista_diapositivas.itemDoubleClicked.connect(self.disparar_diapositiva_directo)
        
        # --- COLUMNA 3: PREVIEW, RELOJ Y LOGO ---
        panel_derecho = QVBoxLayout()
        barra_herramientas = QHBoxLayout()
        
        self.btn_ojo = QPushButton("👁️")
        self.btn_ojo.setFixedSize(45, 45)
        self.btn_ojo.clicked.connect(self.toggle_ojo)
        
        self.btn_reloj = QPushButton("⏱️")
        self.btn_reloj.setFixedSize(45, 45)
        self.btn_reloj.setToolTip("Mostrar/Ocultar Reloj (Click Derecho para opciones)")
        self.btn_reloj.clicked.connect(self.toggle_reloj)
        self.btn_reloj.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_reloj.customContextMenuRequested.connect(self.menu_editar_reloj)

        self.btn_logo = QPushButton("🖼️")
        self.btn_logo.setFixedSize(45, 45)
        self.btn_logo.setToolTip("Mostrar/Ocultar Logo")
        self.btn_logo.clicked.connect(self.toggle_logo)

        barra_herramientas.addWidget(self.btn_ojo)
        barra_herramientas.addWidget(self.btn_reloj)
        barra_herramientas.addWidget(self.btn_logo)
        barra_herramientas.addStretch()
        
        self.monitor_previa = QLabel("Selecciona un verso...")
        self.monitor_previa.setStyleSheet("background-color: #000000; color: white; padding: 10px; border: 2px solid #333333; font-size: 18px; border-radius: 5px;")
        self.monitor_previa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monitor_previa.setWordWrap(True)
        
        self.btn_proyectar = QPushButton("▶ ENVIAR A PANTALLA (Go Live)")
        self.btn_proyectar.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; padding: 20px; font-size: 16px; border-radius: 5px;")
        self.btn_proyectar.clicked.connect(self.enviar_en_vivo)
        
        panel_derecho.addLayout(barra_herramientas)
        panel_derecho.addWidget(self.monitor_previa, stretch=1)
        panel_derecho.addWidget(self.btn_proyectar)

        layout_columnas.addWidget(self.tabs, stretch=2)
        layout_columnas.addWidget(self.lista_diapositivas, stretch=2)
        layout_columnas.addLayout(panel_derecho, stretch=3)

        # --- GALERÍA ---
        panel_fondos = QVBoxLayout()
        self.lista_fondos = QListWidget()
        self.lista_fondos.setViewMode(QListWidget.ViewMode.IconMode)
        self.lista_fondos.setIconSize(QSize(120, 70))
        self.lista_fondos.setFixedHeight(120)
        self.lista_fondos.itemClicked.connect(self.aplicar_fondo)
        
        # Click derecho en galería para escoger Logo
        self.lista_fondos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lista_fondos.customContextMenuRequested.connect(self.menu_galeria_click_derecho)
        
        panel_fondos.addWidget(QLabel("🖼️ Galería (Agregar imágenes en la carpeta fondos. Click derecho en imagen para usar como Logo)"))
        panel_fondos.addWidget(self.lista_fondos)

        layout_base.addLayout(layout_columnas, 1)
        layout_base.addLayout(panel_fondos)
        widget_central.setLayout(layout_base)
        self.setCentralWidget(widget_central)
        
        self.cargar_canciones_desde_db()
        self.cargar_galeria_fondos()

    def aplicar_tema_oscuro(self):
        estilo_oscuro = """
        QMainWindow, QDialog { background-color: #1e1e1e; color: #ffffff; }
        QWidget { background-color: transparent; color: #ffffff; }
        QListWidget { background-color: #2d2d2d; border: 1px solid #3d3d3d; border-radius: 5px; font-size: 14px; padding: 5px; outline: none; }
        QListWidget::item { padding: 5px; border-radius: 3px; }
        QListWidget::item:selected { background-color: #007acc; color: white; }
        QListWidget::item:hover:!selected { background-color: #3d3d3d; }
        QLineEdit, QTextEdit { background-color: #2d2d2d; border: 1px solid #3d3d3d; padding: 8px; border-radius: 4px; color: white; }
        QPushButton { background-color: #3d3d3d; border: none; padding: 8px; border-radius: 4px; color: white; }
        QPushButton:hover { background-color: #4d4d4d; }
        QMenuBar { background-color: #2d2d2d; color: white; } 
        QMenuBar::item:selected { background-color: #007acc; }
        QMenu { background-color: #2d2d2d; border: 1px solid #3d3d3d; color: white; }
        QMenu::item:selected { background-color: #007acc; }
        QTabWidget::pane { border: 1px solid #3d3d3d; background: #1e1e1e; border-radius: 5px; }
        QTabBar::tab { background: #2d2d2d; padding: 8px 15px; border: 1px solid #3d3d3d; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #aaaaaa; }
        QTabBar::tab:selected { background: #007acc; color: white; font-weight: bold; }
        QTabBar::tab:hover:!selected { background: #3d3d3d; }
        QScrollBar:vertical { border: none; background: #1e1e1e; width: 12px; margin: 0px; }
        QScrollBar::handle:vertical { background: #4d4d4d; min-height: 20px; border-radius: 6px; margin: 2px; }
        QScrollBar::handle:vertical:hover { background: #6d6d6d; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        QScrollBar:horizontal { border: none; background: #1e1e1e; height: 12px; margin: 0px; }
        QScrollBar::handle:horizontal { background: #4d4d4d; min-width: 20px; border-radius: 6px; margin: 2px; }
        QScrollBar::handle:horizontal:hover { background: #6d6d6d; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
        """
        self.setStyleSheet(estilo_oscuro)

    def crear_menu_superior(self):
        menu_bar = self.menuBar()
        menu_archivo = menu_bar.addMenu("Archivo")
        menu_archivo.addAction("Cerrar Perfil y Cambiar").triggered.connect(self.cerrar_perfil)
        menu_archivo.addAction("Salir de LuminaCast").triggered.connect(self.close)
        
        menu_config = menu_bar.addMenu("Configuración")
        menu_config.addAction("🖥️ Administrar Pantallas").triggered.connect(lambda: ScreenSettingsDialog(self).exec())
        menu_config.addAction("🎨 Editar Letra y Color").triggered.connect(self.abrir_editor_letras)
        
        menu_ayuda = menu_bar.addMenu("Ayuda")
        menu_ayuda.addAction("ℹ️ Acerca de LuminaCast").triggered.connect(self.mostrar_acerca_de)

    def cerrar_perfil(self):
        # Borramos el auto-login para obligarlo a mostrar el selector de perfiles
        guardar_configuracion("ultimo_perfil", "")
        QApplication.exit(42)

    def mostrar_acerca_de(self):
        texto = (
            "<h3>LuminaCast v1.0</h3>"
            "<p>Software de proyección profesional.</p>"
            "<p><b>Desarrollado por:</b> Eliecer Conrado<br>"
            "<b>Correo:</b> tu_correo_aqui@gmail.com</p>"
            "<p><b>Estado:</b> Licencia Activa.</p>"
        )
        QMessageBox.about(self, "Acerca de LuminaCast", texto)

    def abrir_editor_letras(self):
        dialogo = TextSettingsDialog(self, self.proyector.fuente_actual, self.proyector.tamano_letra_actual, self.proyector.color_letra_actual)
        if dialogo.exec():
            self.proyector.actualizar_estilo_texto(dialogo.combo_fuente.currentText(), dialogo.spin_tamano.value(), dialogo.color_seleccionado)

    def menu_editar_reloj(self, pos):
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #2d2d2d; color: white; } QMenu::item:selected { background-color: #007acc; }")
        menu.addAction("⚙️ Configurar Tamaño y Posición").triggered.connect(self.abrir_configuracion_reloj)
        menu.exec(self.btn_reloj.mapToGlobal(pos))

    def abrir_configuracion_reloj(self):
        dialogo = ClockSettingsDialog(self, self.proyector.reloj_tamano, self.proyector.reloj_posicion)
        if dialogo.exec():
            self.proyector.configurar_reloj(dialogo.spin_tamano.value(), dialogo.combo_pos.currentText())

    def menu_galeria_click_derecho(self, pos):
        item = self.lista_fondos.itemAt(pos)
        if item and item.data(Qt.ItemDataRole.UserRole) != "sin_fondo":
            menu = QMenu()
            menu.setStyleSheet("QMenu { background-color: #2d2d2d; color: white; } QMenu::item:selected { background-color: #007acc; }")
            menu.addAction("👑 Establecer como Logo Global").triggered.connect(lambda: self.establecer_logo(item))
            menu.exec(self.lista_fondos.viewport().mapToGlobal(pos))

    def establecer_logo(self, item):
        self.ruta_logo_global = item.data(Qt.ItemDataRole.UserRole)
        QMessageBox.information(self, "Logo Seleccionado", "Has establecido esta imagen como tu Logo Global. Enciende el botón de logo para verlo.")

    def mostrar_menu_canciones(self, posicion):
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #2d2d2d; color: white; } QMenu::item:selected { background-color: #007acc; }")
        menu.addAction("➕ Agregar Nueva Canción").triggered.connect(self.agregar_nueva_cancion)
        item = self.lista_recursos.itemAt(posicion)
        if item:
            menu.addAction("✏️ Editar Canción").triggered.connect(lambda: self.editar_cancion(item))
            menu.addAction("🗑️ Eliminar Canción").triggered.connect(lambda: self.eliminar_cancion_ui(item))
        menu.exec(self.lista_recursos.viewport().mapToGlobal(posicion))

    def agregar_nueva_cancion(self):
        if DialogoCancion(self).exec(): self.cargar_canciones_desde_db()

    def editar_cancion(self, item):
        song_id = item.data(Qt.ItemDataRole.UserRole)
        if DialogoCancion(self, song_id=song_id, titulo=item.text(), letra=obtener_letra_cancion(song_id)).exec(): 
            self.cargar_canciones_desde_db()

    def eliminar_cancion_ui(self, item):
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar '{item.text()}'?") == QMessageBox.StandardButton.Yes:
            eliminar_cancion(item.data(Qt.ItemDataRole.UserRole))
            self.cargar_canciones_desde_db()
            self.lista_diapositivas.clear()

    def toggle_ojo(self):
        self.esta_visible = not self.esta_visible
        self.btn_ojo.setText("👁️" if self.esta_visible else "🙈")
        self.proyector.ocultar_proyeccion(not self.esta_visible)

    def toggle_reloj(self):
        self.reloj_activo = not self.reloj_activo
        self.btn_reloj.setStyleSheet("background-color: #007acc;" if self.reloj_activo else "background-color: #3d3d3d;")
        self.proyector.toggle_reloj(self.reloj_activo)

    def toggle_logo(self):
        if not self.ruta_logo_global:
            QMessageBox.warning(self, "Sin Logo", "Haz click derecho en una imagen de la galería para establecerla como logo primero.")
            return
        self.logo_activo = not self.logo_activo
        self.btn_logo.setStyleSheet("background-color: #007acc;" if self.logo_activo else "background-color: #3d3d3d;")
        self.proyector.toggle_logo(self.logo_activo, self.ruta_logo_global)

    def filtrar_canciones(self, texto):
        for i in range(self.lista_recursos.count()):
            item = self.lista_recursos.item(i)
            item.setHidden(texto.lower() not in item.text().lower())

    def cargar_galeria_fondos(self):
        self.lista_fondos.clear()
        
        # 1. Crear el ítem y asignarle los datos por separado (CORRECCIÓN IMPORTANTE)
        item_sin = QListWidgetItem("Sin Fondo")
        item_sin.setData(Qt.ItemDataRole.UserRole, "sin_fondo")
        self.lista_fondos.addItem(item_sin)
        
        ruta = os.path.join(os.path.dirname(__file__), '../../assets/fondos')
        if os.path.exists(ruta):
            for f in os.listdir(ruta):
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    item = QListWidgetItem()
                    item.setIcon(QIcon(os.path.join(ruta, f)))
                    item.setData(Qt.ItemDataRole.UserRole, os.path.join(ruta, f))
                    self.lista_fondos.addItem(item)

    def aplicar_fondo(self, item): 
        self.proyector.cambiar_fondo(item.data(Qt.ItemDataRole.UserRole))

    def cargar_canciones_desde_db(self):
        self.lista_recursos.clear()
        for song_id, titulo in obtener_todas_las_canciones():
            # 2. Crear el ítem y asignarle los datos por separado (CORRECCIÓN IMPORTANTE)
            item = QListWidgetItem(titulo)
            item.setData(Qt.ItemDataRole.UserRole, song_id)
            self.lista_recursos.addItem(item)

    def cargar_diapositivas_cancion(self, item):
        self.lista_diapositivas.clear()
        letra = obtener_letra_cancion(item.data(Qt.ItemDataRole.UserRole))
        if letra:
            for bloque in letra.split("\n\n"):
                if bloque.strip(): self.lista_diapositivas.addItem(QListWidgetItem(bloque.strip()))

    def previsualizar_diapositiva(self, item): 
        self.monitor_previa.setText(item.text())

    def enviar_en_vivo(self):
        if "Selecciona" not in self.monitor_previa.text():
            self.proyector.proyectar_texto(re.sub(r'\[.*?\]', '', self.monitor_previa.text()).strip())

    def disparar_diapositiva_directo(self, item): 
        self.previsualizar_diapositiva(item); self.enviar_en_vivo()

    def closeEvent(self, event): 
        QApplication.exit(0)