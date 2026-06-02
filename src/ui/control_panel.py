# src/ui/control_panel.py
import re # Librería nativa de Python para expresiones regulares (Regex)
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QListWidgetItem, QLabel, QPushButton,
                             QDialog, QLineEdit, QTextEdit, QMessageBox, QMenu, QApplication)
from PyQt6.QtCore import Qt
from database.db_manager import (inicializar_db, obtener_todas_las_canciones, 
                                 obtener_letra_cancion, agregar_cancion, 
                                 actualizar_cancion, eliminar_cancion)

# =================================================================
# VENTANA EMERGENTE PARA AGREGAR/EDITAR CANCIONES
# =================================================================
class DialogoCancion(QDialog):
    def __init__(self, parent=None, song_id=None, titulo="", letra=""):
        super().__init__(parent)
        self.song_id = song_id
        self.setWindowTitle("Editar Canción" if song_id else "Agregar Nueva Canción")
        self.resize(500, 600)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Título de la canción:"))
        self.input_titulo = QLineEdit(titulo)
        layout.addWidget(self.input_titulo)
        
        layout.addWidget(QLabel("Letra (Separa las estrofas con doble 'Enter'):"))
        self.input_letra = QTextEdit()
        self.input_letra.setPlainText(letra)
        layout.addWidget(self.input_letra)
        
        btn_guardar = QPushButton("💾 Guardar Canción")
        btn_guardar.setStyleSheet("background-color: #007bff; color: white; padding: 12px; font-weight: bold; border-radius: 4px;")
        btn_guardar.clicked.connect(self.guardar_bd)
        layout.addWidget(btn_guardar)
        
        self.setLayout(layout)
        
    def guardar_bd(self):
        titulo = self.input_titulo.text().strip()
        letra = self.input_letra.toPlainText().strip()
        
        if not titulo or not letra:
            QMessageBox.warning(self, "Error", "El título y la letra son obligatorios.")
            return
            
        if self.song_id:
            actualizar_cancion(self.song_id, titulo, letra)
        else:
            agregar_cancion(titulo, letra)
            
        self.accept()

# =================================================================
# PANEL DE CONTROL PRINCIPAL
# =================================================================
class ControlPanel(QMainWindow):
    def __init__(self, proyector, nombre_congregacion):
        super().__init__()
        self.proyector = proyector
        self.setWindowTitle(f"LuminaCast - Panel de Control | Trabajando en: {nombre_congregacion}")
        self.resize(1200, 768)

        inicializar_db()
        self.crear_menu_superior() 

        widget_central = QWidget()
        layout_principal = QHBoxLayout()

        # --- COLUMNA 1: LIBRERÍA ---
        panel_izquierdo = QVBoxLayout()
        titulo_libreria = QLabel("📋 Canciones")
        titulo_libreria.setStyleSheet("font-weight: bold; font-size: 14px; color: #aaa;")
        
        self.btn_agregar = QPushButton("➕ Agregar Canción")
        self.btn_agregar.setStyleSheet("background-color: #444; color: white; padding: 8px; font-weight: bold; border-radius: 4px; marginBottom: 5px;")
        self.btn_agregar.clicked.connect(self.abrir_formulario_cancion)
        
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("🔍 Buscar canción por título...")
        self.buscador.setStyleSheet("padding: 8px; font-size: 14px; background-color: #222; color: white; border: 1px solid #444; border-radius: 4px;")
        self.buscador.textChanged.connect(self.filtrar_canciones)
        
        self.lista_recursos = QListWidget()
        self.lista_recursos.itemClicked.connect(self.cargar_diapositivas_cancion)
        
        self.lista_recursos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lista_recursos.customContextMenuRequested.connect(self.mostrar_menu_contextual_canciones)
        
        panel_izquierdo.addWidget(titulo_libreria)
        panel_izquierdo.addWidget(self.btn_agregar)
        panel_izquierdo.addWidget(self.buscador)
        panel_izquierdo.addWidget(self.lista_recursos)

        # --- COLUMNA 2: DIAPOSITIVAS ---
        panel_central = QVBoxLayout()
        titulo_diapositivas = QLabel("🔲 Diapositivas del Tema")
        titulo_diapositivas.setStyleSheet("font-weight: bold; font-size: 14px; color: #aaa;")
        
        self.lista_diapositivas = QListWidget()
        self.lista_diapositivas.itemClicked.connect(self.previsualizar_diapositiva)
        self.lista_diapositivas.itemDoubleClicked.connect(self.disparar_diapositiva_directo)
        
        panel_central.addWidget(titulo_diapositivas)
        panel_central.addWidget(self.lista_diapositivas)

        # --- COLUMNA 3: VISTA PREVIA ---
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

        layout_principal.addLayout(panel_izquierdo, stretch=2)
        layout_principal.addLayout(panel_central, stretch=2)
        layout_principal.addLayout(panel_derecho, stretch=3)

        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

        self.cargar_canciones_desde_db()

    # --- LÓGICA DE MENÚ SUPERIOR ---
    def crear_menu_superior(self):
        menu_bar = self.menuBar()
        
        menu_archivo = menu_bar.addMenu("Archivo")
        accion_salir = menu_archivo.addAction("Salir de LuminaCast")
        accion_salir.triggered.connect(self.close)
        
        menu_config = menu_bar.addMenu("Configuración")
        menu_config.addAction("Pantallas y Salidas (Próximamente)")
        menu_config.addAction("Temas y Fuentes (Próximamente)")
        
        menu_ayuda = menu_bar.addMenu("Ayuda")
        accion_acerca = menu_ayuda.addAction("Acerca de LuminaCast")
        accion_acerca.triggered.connect(self.mostrar_acerca_de)

    def mostrar_acerca_de(self):
        QMessageBox.about(self, "Acerca de LuminaCast",
            "<h3>LuminaCast v1.0</h3>"
            "<p>Software potente y simple para proyección multimedia.</p>"
            "<p><b>Creador y Desarrollador Principal:</b><br>"
            "Eliecer Jesús Conrado Alarcón<br>"
            "<i>Arquitectura IT & Telecomunicaciones</i></p>"
            "<p>Hecho con Python y PyQt6.</p>"
        )

    # --- LÓGICA DE CANCIONES ---
    def mostrar_menu_contextual_canciones(self, position):
        item = self.lista_recursos.itemAt(position)
        if not item: return
        
        menu = QMenu()
        accion_editar = menu.addAction("✏️ Editar Canción")
        accion_eliminar = menu.addAction("🗑️ Eliminar Canción")
        
        accion_seleccionada = menu.exec(self.lista_recursos.mapToGlobal(position))
        
        if accion_seleccionada == accion_editar:
            self.editar_cancion(item)
        elif accion_seleccionada == accion_eliminar:
            self.eliminar_cancion(item)

    def abrir_formulario_cancion(self):
        dialogo = DialogoCancion(self)
        if dialogo.exec():
            self.cargar_canciones_desde_db()
            self.buscador.clear()

    def editar_cancion(self, item):
        song_id = item.data(Qt.ItemDataRole.UserRole)
        titulo_actual = item.text()
        letra_actual = obtener_letra_cancion(song_id)
        
        dialogo = DialogoCancion(self, song_id=song_id, titulo=titulo_actual, letra=letra_actual)
        if dialogo.exec():
            self.cargar_canciones_desde_db()
            self.lista_diapositivas.clear()

    def eliminar_cancion(self, item):
        song_id = item.data(Qt.ItemDataRole.UserRole)
        respuesta = QMessageBox.question(self, "Eliminar Canción", 
                                         f"¿Seguro que deseas eliminar '{item.text()}'?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if respuesta == QMessageBox.StandardButton.Yes:
            eliminar_cancion(song_id)
            self.cargar_canciones_desde_db()
            self.lista_diapositivas.clear()

    def cargar_canciones_desde_db(self):
        self.lista_recursos.clear()
        canciones = obtener_todas_las_canciones()
        for song_id, titulo in canciones:
            item = QListWidgetItem(titulo)
            item.setData(Qt.ItemDataRole.UserRole, song_id)
            self.lista_recursos.addItem(item)

    def filtrar_canciones(self, texto_busqueda):
        for i in range(self.lista_recursos.count()):
            item = self.lista_recursos.item(i)
            coincide = texto_busqueda.lower() in item.text().lower()
            item.setHidden(not coincide)

    def cargar_diapositivas_cancion(self, item):
        self.lista_diapositivas.clear()
        song_id = item.data(Qt.ItemDataRole.UserRole)
        letra_completa = obtener_letra_cancion(song_id)
        
        diapositivas = letra_completa.split("\n\n")
        
        for bloque in diapositivas:
            if bloque.strip():
                self.lista_diapositivas.addItem(QListWidgetItem(bloque.strip()))
                
        if self.lista_diapositivas.count() > 0:
            self.lista_diapositivas.setCurrentRow(0)
            self.previsualizar_diapositiva(self.lista_diapositivas.item(0))

    def previsualizar_diapositiva(self, item):
        self.monitor_previa.setText(item.text())

    # --- EL FILTRO MÁGICO PARA EL PROYECTOR ---
    def enviar_en_vivo(self):
        texto_actual = self.monitor_previa.text()
        if "Selecciona un verso..." not in texto_actual:
            # 1. Filtramos: Borra cualquier cosa que esté entre corchetes, ej: [Coro], [Estrofa 1]
            texto_limpio = re.sub(r'\[.*?\]', '', texto_actual)
            # 2. Limpiamos: Borra espacios y saltos de línea extra que queden al principio o al final
            texto_limpio = texto_limpio.strip()
            
            self.proyector.proyectar_texto(texto_limpio)

    def disparar_diapositiva_directo(self, item):
        self.previsualizar_diapositiva(item)
        self.enviar_en_vivo()

    def closeEvent(self, event):
        """Si el usuario cierra el panel de control, se apaga toda la aplicación"""
        QApplication.instance().quit()
        event.accept()