import re
import os
import shutil
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QListWidgetItem, QLabel, QPushButton,
                             QDialog, QLineEdit, QTextEdit, QMessageBox, QApplication, 
                             QMenu, QTabWidget, QFileDialog, QFontComboBox, QSpinBox, 
                             QColorDialog, QComboBox, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QColor
from database.db_manager import (inicializar_db, obtener_todas_las_canciones, 
                                 obtener_letra_cancion, agregar_cancion, 
                                 actualizar_cancion, eliminar_cancion, guardar_configuracion, 
                                 obtener_configuracion, obtener_versiones_biblia, 
                                 obtener_libros_biblia, obtener_capitulos_biblia, 
                                 obtener_versiculos_biblia)
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

class TransitionSettingsDialog(QDialog):
    def __init__(self, parent, c_tipo, c_vel, b_tipo, b_vel):
        super().__init__(parent)
        self.setWindowTitle("Animaciones y Transiciones")
        self.resize(350, 300)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        layout = QVBoxLayout()

        self.velocidades = {"Rápida (150ms)": 150, "Normal (300ms)": 300, "Suave (600ms)": 600}
        self.tipos = ["Fade (Desvanecido)", "Corte Directo"]

        def get_vel_key(val):
            for k, v in self.velocidades.items():
                if v == val: return k
            return "Normal (300ms)"

        def get_tipo_str(tipo_bd): return "Corte Directo" if tipo_bd == "Corte" else "Fade (Desvanecido)"

        gb_canciones = QGroupBox("🎵 Transiciones para Canciones")
        gb_canciones.setStyleSheet("QGroupBox { border: 1px solid #3d3d3d; border-radius: 5px; margin-top: 15px; font-weight: bold; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        fl_canciones = QFormLayout()
        self.combo_c_tipo = QComboBox(); self.combo_c_tipo.addItems(self.tipos); self.combo_c_tipo.setCurrentText(get_tipo_str(c_tipo)); self.combo_c_tipo.setStyleSheet("background-color: #2d2d2d; color: white;")
        self.combo_c_vel = QComboBox(); self.combo_c_vel.addItems(self.velocidades.keys()); self.combo_c_vel.setCurrentText(get_vel_key(c_vel)); self.combo_c_vel.setStyleSheet("background-color: #2d2d2d; color: white;")
        fl_canciones.addRow("Efecto:", self.combo_c_tipo)
        fl_canciones.addRow("Velocidad:", self.combo_c_vel)
        gb_canciones.setLayout(fl_canciones)

        gb_biblias = QGroupBox("📖 Transiciones para Biblias")
        gb_biblias.setStyleSheet("QGroupBox { border: 1px solid #3d3d3d; border-radius: 5px; margin-top: 15px; font-weight: bold; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }")
        fl_biblias = QFormLayout()
        self.combo_b_tipo = QComboBox(); self.combo_b_tipo.addItems(self.tipos); self.combo_b_tipo.setCurrentText(get_tipo_str(b_tipo)); self.combo_b_tipo.setStyleSheet("background-color: #2d2d2d; color: white;")
        self.combo_b_vel = QComboBox(); self.combo_b_vel.addItems(self.velocidades.keys()); self.combo_b_vel.setCurrentText(get_vel_key(b_vel)); self.combo_b_vel.setStyleSheet("background-color: #2d2d2d; color: white;")
        fl_biblias.addRow("Efecto:", self.combo_b_tipo)
        fl_biblias.addRow("Velocidad:", self.combo_b_vel)
        gb_biblias.setLayout(fl_biblias)

        layout.addWidget(gb_canciones)
        layout.addWidget(gb_biblias)

        btn_guardar = QPushButton("💾 Aplicar Cambios")
        btn_guardar.setStyleSheet("background-color: #007acc; color: white; padding: 10px; font-weight: bold; margin-top: 10px;")
        btn_guardar.clicked.connect(self.accept)
        layout.addWidget(btn_guardar)
        self.setLayout(layout)

    def get_valores(self):
        c_tipo = "Corte" if "Corte" in self.combo_c_tipo.currentText() else "Fade"
        c_vel = self.velocidades[self.combo_c_vel.currentText()]
        b_tipo = "Corte" if "Corte" in self.combo_b_tipo.currentText() else "Fade"
        b_vel = self.velocidades[self.combo_b_vel.currentText()]
        return c_tipo, c_vel, b_tipo, b_vel

class ControlPanel(QMainWindow):
    def __init__(self, proyector, nombre_congregacion):
        super().__init__()
        self.proyector = proyector
        self.nombre_congregacion = nombre_congregacion
        self.setWindowTitle(f"LuminaCast | {nombre_congregacion}")
        self.resize(1200, 800)
        self.aplicar_tema_oscuro()
        
        self.esta_visible = True
        self.cambiando_perfil = False
        self.tipo_proyeccion_actual = "cancion" 

        inicializar_db()

        # --- CARGAR CONFIGURACIONES ---
        reloj_act = obtener_configuracion(f"{nombre_congregacion}_reloj_activo")
        self.reloj_activo = True if reloj_act == "1" else False
        reloj_tamano = int(obtener_configuracion(f"{nombre_congregacion}_reloj_tamano") or 20)
        reloj_posicion = obtener_configuracion(f"{nombre_congregacion}_reloj_posicion") or "Arriba - Derecha"
        
        logo_act = obtener_configuracion(f"{nombre_congregacion}_logo_activo")
        self.logo_activo = True if logo_act == "1" else False
        self.ruta_logo_global = obtener_configuracion(f"{nombre_congregacion}_logo_ruta")
        
        letra_fuente = obtener_configuracion(f"{nombre_congregacion}_letra_fuente") or "Segoe UI"
        letra_tamano = int(obtener_configuracion(f"{nombre_congregacion}_letra_tamano") or 45)
        letra_color = obtener_configuracion(f"{nombre_congregacion}_letra_color") or "#ffffff"

        c_tipo = obtener_configuracion(f"{self.nombre_congregacion}_trans_cancion_tipo") or "Fade"
        c_vel = int(obtener_configuracion(f"{self.nombre_congregacion}_trans_cancion_vel") or 300)
        b_tipo = obtener_configuracion(f"{self.nombre_congregacion}_trans_biblia_tipo") or "Fade"
        b_vel = int(obtener_configuracion(f"{self.nombre_congregacion}_trans_biblia_vel") or 300)

        self.proyector.actualizar_estilo_texto(letra_fuente, letra_tamano, letra_color)
        self.proyector.configurar_reloj(reloj_tamano, reloj_posicion)
        self.proyector.toggle_reloj(self.reloj_activo)
        self.proyector.configurar_transiciones(c_tipo, c_vel, b_tipo, b_vel)
        if self.ruta_logo_global and os.path.exists(self.ruta_logo_global):
            self.proyector.toggle_logo(self.logo_activo, self.ruta_logo_global)

        self.crear_menu_superior() 

        widget_central = QWidget()
        layout_base = QVBoxLayout()
        layout_columnas = QHBoxLayout()

        # --- COLUMNA 1: TABS (CANCIONES Y BIBLIAS) ---
        self.tabs = QTabWidget()
        
        # TAB CANCIONES
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
        
        # TAB BIBLIAS
        tab_biblias = QWidget()
        layout_biblias = QVBoxLayout(tab_biblias)
        layout_biblias.setContentsMargins(5, 10, 5, 5)
        
        # 1. Selectores de Biblia (Moviéndolo arriba para mejor UX)
        filtros_biblia = QHBoxLayout()
        self.combo_version = QComboBox(); self.combo_version.setStyleSheet("background-color: #2d2d2d;")
        self.combo_libro = QComboBox(); self.combo_libro.setStyleSheet("background-color: #2d2d2d;")
        self.combo_capitulo = QComboBox(); self.combo_capitulo.setStyleSheet("background-color: #2d2d2d;")
        
        self.combo_version.currentIndexChanged.connect(self.cargar_libros_ui)
        self.combo_libro.currentIndexChanged.connect(self.cargar_capitulos_ui)
        self.combo_capitulo.currentIndexChanged.connect(self.cargar_versiculos_ui)

        filtros_biblia.addWidget(QLabel("Biblia:")); filtros_biblia.addWidget(self.combo_version)
        filtros_biblia.addWidget(QLabel("Libro:")); filtros_biblia.addWidget(self.combo_libro)
        filtros_biblia.addWidget(QLabel("Cap:")); filtros_biblia.addWidget(self.combo_capitulo)
        
        layout_biblias.addLayout(filtros_biblia)

        # 2. Buscador local por capítulo
        self.input_buscar_biblia = QLineEdit()
        self.input_buscar_biblia.setPlaceholderText("🔍 Filtrar versículo en este capítulo (Ej: 3, amor, Dios)...")
        self.input_buscar_biblia.setStyleSheet("background-color: #2d2d2d; border: 1px solid #3d3d3d; padding: 8px; border-radius: 4px; color: white;")
        # Conectamos el evento textChanged para filtrar en tiempo real
        self.input_buscar_biblia.textChanged.connect(self.filtrar_versiculos_capitulo)
        layout_biblias.addWidget(self.input_buscar_biblia)
        
        # 3. Lista de Versículos
        self.lista_versiculos = QListWidget()
        self.lista_versiculos.setWordWrap(True)
        self.lista_versiculos.itemClicked.connect(self.previsualizar_versiculo)
        self.lista_versiculos.itemDoubleClicked.connect(self.disparar_diapositiva_directo)
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
        self.btn_reloj.clicked.connect(self.toggle_reloj)
        self.btn_reloj.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_reloj.customContextMenuRequested.connect(self.menu_editar_reloj)

        self.btn_logo = QPushButton("🖼️")
        self.btn_logo.setFixedSize(45, 45)
        self.btn_logo.clicked.connect(self.toggle_logo)

        self.btn_reloj.setStyleSheet("background-color: #007acc;" if self.reloj_activo else "background-color: #3d3d3d;")
        self.btn_logo.setStyleSheet("background-color: #007acc;" if self.logo_activo else "background-color: #3d3d3d;")

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
        
        panel_fondos.addWidget(QLabel("🖼️ Galería (Agregar imágenes en la carpeta fondos)"))
        panel_fondos.addWidget(self.lista_fondos)

        layout_base.addLayout(layout_columnas, 1)
        layout_base.addLayout(panel_fondos)
        widget_central.setLayout(layout_base)
        self.setCentralWidget(widget_central)
        
        self.tabs.currentChanged.connect(self.actualizar_contexto_proyeccion)
        
        self.cargar_canciones_desde_db()
        self.cargar_galeria_fondos()
        self.cargar_versiones_ui()

    # ================= FUNCIONES DE BIBLIA =================
    def cargar_versiones_ui(self):
        self.combo_version.blockSignals(True)
        self.combo_version.clear()
        versiones = obtener_versiones_biblia()
        for v_id, nombre, abrev in versiones:
            self.combo_version.addItem(f"{nombre} ({abrev})", v_id)
        self.combo_version.blockSignals(False)
        if self.combo_version.count() > 0:
            self.cargar_libros_ui()

    def cargar_libros_ui(self):
        self.combo_libro.blockSignals(True)
        self.combo_libro.clear()
        v_id = self.combo_version.currentData()
        if v_id:
            libros = obtener_libros_biblia(v_id)
            for l_id, nombre in libros:
                self.combo_libro.addItem(nombre, l_id)
        self.combo_libro.blockSignals(False)
        if self.combo_libro.count() > 0:
            self.cargar_capitulos_ui()

    def cargar_capitulos_ui(self):
        self.combo_capitulo.blockSignals(True)
        self.combo_capitulo.clear()
        l_id = self.combo_libro.currentData()
        if l_id:
            capitulos = obtener_capitulos_biblia(l_id)
            for cap in capitulos:
                self.combo_capitulo.addItem(str(cap), cap)
        self.combo_capitulo.blockSignals(False)
        if self.combo_capitulo.count() > 0:
            self.cargar_versiculos_ui()

    def cargar_versiculos_ui(self):
        self.lista_versiculos.clear()
        # Limpiamos el buscador al cambiar de capítulo para mostrar todo
        self.input_buscar_biblia.clear()
        
        l_id = self.combo_libro.currentData()
        cap = self.combo_capitulo.currentData()
        libro_nombre = self.combo_libro.currentText()
        if l_id and cap:
            versiculos = obtener_versiculos_biblia(l_id, cap)
            for ver_num, texto in versiculos:
                item = QListWidgetItem(f"{ver_num}. {texto}")
                item.setData(Qt.ItemDataRole.UserRole, (libro_nombre, cap, ver_num, texto))
                self.lista_versiculos.addItem(item)

    # NUEVA FUNCIÓN: Filtro en tiempo real dentro de la lista de versículos actual
    def filtrar_versiculos_capitulo(self, texto):
        for i in range(self.lista_versiculos.count()):
            item = self.lista_versiculos.item(i)
            # Ocultamos el versículo si no contiene el número o palabra buscada
            item.setHidden(texto.lower() not in item.text().lower())

    def previsualizar_versiculo(self, item):
        if not item or not item.data(Qt.ItemDataRole.UserRole): return
        libro_nombre, capitulo, ver_num, texto = item.data(Qt.ItemDataRole.UserRole)
        texto_formateado = f"{texto}\n[{libro_nombre} {capitulo}:{ver_num}]"
        
        self.monitor_previa.setText(texto_formateado)
        self.lista_diapositivas.clearSelection()

    # ========================================================

    def actualizar_contexto_proyeccion(self, index):
        self.tipo_proyeccion_actual = "cancion" if index == 0 else "biblia"
        if index == 1:
            self.lista_diapositivas.hide()
        else:
            self.lista_diapositivas.show()

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
        QComboBox { background-color: #2d2d2d; border: 1px solid #3d3d3d; padding: 5px; color: white; border-radius: 4px; }
        QComboBox QAbstractItemView { background-color: #2d2d2d; color: white; selection-background-color: #007acc; }
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
        menu_config.addAction("🖼️ Seleccionar Logo Global").triggered.connect(self.seleccionar_logo_archivo)
        menu_config.addAction("🎞️ Animaciones y Transiciones").triggered.connect(self.abrir_configuracion_transiciones)
        
        menu_ayuda = menu_bar.addMenu("Ayuda")
        menu_ayuda.addAction("ℹ️ Acerca de LuminaCast").triggered.connect(self.mostrar_acerca_de)

    def cerrar_perfil(self):
        self.cambiando_perfil = True
        guardar_configuracion("ultimo_perfil", "")
        if self.proyector: self.proyector.close()
        self.close()

    def mostrar_acerca_de(self):
        texto = ("<h3>LuminaCast v1.0</h3><p>Software de proyección profesional.</p><p><b>Desarrollado por:</b> Eliecer Conrado<br><b>Correo:</b> elieje13@gmail.com</p><p><b>Estado:</b> Licencia Activa.</p>")
        QMessageBox.about(self, "Acerca de LuminaCast", texto)

    def abrir_configuracion_transiciones(self):
        c_tipo = obtener_configuracion(f"{self.nombre_congregacion}_trans_cancion_tipo") or "Fade"
        c_vel = int(obtener_configuracion(f"{self.nombre_congregacion}_trans_cancion_vel") or 300)
        b_tipo = obtener_configuracion(f"{self.nombre_congregacion}_trans_biblia_tipo") or "Fade"
        b_vel = int(obtener_configuracion(f"{self.nombre_congregacion}_trans_biblia_vel") or 300)

        dialogo = TransitionSettingsDialog(self, c_tipo, c_vel, b_tipo, b_vel)
        if dialogo.exec():
            n_c_tipo, n_c_vel, n_b_tipo, n_b_vel = dialogo.get_valores()
            guardar_configuracion(f"{self.nombre_congregacion}_trans_cancion_tipo", n_c_tipo)
            guardar_configuracion(f"{self.nombre_congregacion}_trans_cancion_vel", str(n_c_vel))
            guardar_configuracion(f"{self.nombre_congregacion}_trans_biblia_tipo", n_b_tipo)
            guardar_configuracion(f"{self.nombre_congregacion}_trans_biblia_vel", str(n_b_vel))
            self.proyector.configurar_transiciones(n_c_tipo, n_c_vel, n_b_tipo, n_b_vel)

    def seleccionar_logo_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Imágenes (*.png *.jpg *.jpeg)")
        if archivo:
            self.ruta_logo_global = archivo
            guardar_configuracion(f"{self.nombre_congregacion}_logo_ruta", archivo)
            QMessageBox.information(self, "Logo Actualizado", "Imagen cargada. Activa el botón de logo en el panel para mostrarla.")

    def abrir_editor_letras(self):
        dialogo = TextSettingsDialog(self, self.proyector.fuente_actual, self.proyector.tamano_letra_actual, self.proyector.color_letra_actual)
        if dialogo.exec():
            fuente = dialogo.combo_fuente.currentText()
            tamano = dialogo.spin_tamano.value()
            color = dialogo.color_seleccionado
            self.proyector.actualizar_estilo_texto(fuente, tamano, color)
            guardar_configuracion(f"{self.nombre_congregacion}_letra_fuente", fuente)
            guardar_configuracion(f"{self.nombre_congregacion}_letra_tamano", str(tamano))
            guardar_configuracion(f"{self.nombre_congregacion}_letra_color", color)

    def menu_editar_reloj(self, pos):
        menu = QMenu()
        menu.setStyleSheet("QMenu { background-color: #2d2d2d; color: white; } QMenu::item:selected { background-color: #007acc; }")
        menu.addAction("⚙️ Configurar Tamaño y Posición").triggered.connect(self.abrir_configuracion_reloj)
        menu.exec(self.btn_reloj.mapToGlobal(pos))

    def abrir_configuracion_reloj(self):
        dialogo = ClockSettingsDialog(self, self.proyector.reloj_tamano, self.proyector.reloj_posicion)
        if dialogo.exec():
            tamano = dialogo.spin_tamano.value()
            posicion = dialogo.combo_pos.currentText()
            self.proyector.configurar_reloj(tamano, posicion)
            guardar_configuracion(f"{self.nombre_congregacion}_reloj_tamano", str(tamano))
            guardar_configuracion(f"{self.nombre_congregacion}_reloj_posicion", posicion)

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
        if DialogoCancion(self, song_id=song_id, titulo=item.text(), letra=obtener_letra_cancion(song_id)).exec(): self.cargar_canciones_desde_db()

    def eliminar_cancion_ui(self, item):
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar '{item.text()}'?") == QMessageBox.StandardButton.Yes:
            eliminar_cancion(item.data(Qt.ItemDataRole.UserRole)); self.cargar_canciones_desde_db(); self.lista_diapositivas.clear()

    def toggle_ojo(self):
        self.esta_visible = not self.esta_visible
        self.btn_ojo.setText("👁️" if self.esta_visible else "🙈")
        self.proyector.ocultar_proyeccion(not self.esta_visible)

    def toggle_reloj(self):
        self.reloj_activo = not self.reloj_activo
        self.btn_reloj.setStyleSheet("background-color: #007acc;" if self.reloj_activo else "background-color: #3d3d3d;")
        self.proyector.toggle_reloj(self.reloj_activo)
        guardar_configuracion(f"{self.nombre_congregacion}_reloj_activo", "1" if self.reloj_activo else "0")

    def toggle_logo(self):
        if not self.ruta_logo_global:
            self.seleccionar_logo_archivo()
            return
        self.logo_activo = not self.logo_activo
        self.btn_logo.setStyleSheet("background-color: #007acc;" if self.logo_activo else "background-color: #3d3d3d;")
        self.proyector.toggle_logo(self.logo_activo, self.ruta_logo_global)
        guardar_configuracion(f"{self.nombre_congregacion}_logo_activo", "1" if self.logo_activo else "0")

    def filtrar_canciones(self, texto):
        for i in range(self.lista_recursos.count()):
            item = self.lista_recursos.item(i)
            item.setHidden(texto.lower() not in item.text().lower())

    def cargar_galeria_fondos(self):
        self.lista_fondos.clear()
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

    def aplicar_fondo(self, item): self.proyector.cambiar_fondo(item.data(Qt.ItemDataRole.UserRole))

    def cargar_canciones_desde_db(self):
        self.lista_recursos.clear()
        for song_id, titulo in obtener_todas_las_canciones():
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
        self.lista_versiculos.clearSelection()

    def enviar_en_vivo(self):
        if "Selecciona" not in self.monitor_previa.text():
            if self.tipo_proyeccion_actual == "cancion":
                texto_limpio = re.sub(r'\[.*?\]', '', self.monitor_previa.text()).strip()
            else:
                texto_limpio = self.monitor_previa.text().strip()
            self.proyector.proyectar_texto(texto_limpio, self.tipo_proyeccion_actual)

    def disparar_diapositiva_directo(self, item): 
        if self.tipo_proyeccion_actual == "cancion":
            self.previsualizar_diapositiva(item)
        else:
            self.previsualizar_versiculo(item)
        self.enviar_en_vivo()

    def closeEvent(self, event): 
        if self.cambiando_perfil: QApplication.instance().exit(42)
        else: QApplication.instance().exit(0)
        event.accept()