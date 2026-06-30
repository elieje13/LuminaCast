import re
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QListWidgetItem, QLabel, QPushButton,
                             QDialog, QLineEdit, QTextEdit, QMessageBox, QApplication, 
                             QFileDialog, QFontComboBox, QSpinBox, QTreeWidget, QTreeWidgetItem,
                             QComboBox, QStackedWidget, QGridLayout, QSplitter, QFrame, QMenu)
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter, QFont, QPen, QPainterPath, QLinearGradient
from database.db_manager import (inicializar_db, obtener_todas_las_canciones, 
                                 obtener_letra_cancion, agregar_cancion, 
                                 actualizar_cancion, eliminar_cancion, guardar_configuracion, 
                                 obtener_configuracion, obtener_versiones_biblia, 
                                 obtener_libros_biblia, obtener_capitulos_biblia, 
                                 obtener_versiculos_biblia)
from ui.screen_settings import ScreenSettingsDialog

class AppAjustesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajustes de LuminaCast")
        self.resize(450, 350)
        self.setStyleSheet("background-color: #111827; color: #F8FAFC;")
        layout = QVBoxLayout()
        lbl_titulo = QLabel("⚙️ Panel de Ajustes Generales")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #8A3FFC;")
        layout.addWidget(lbl_titulo)
        layout.addWidget(QLabel("Aquí se integrarán configuraciones avanzadas del sistema."))
        layout.addStretch()
        btn_cerrar = QPushButton("Cerrar Ajustes")
        btn_cerrar.setStyleSheet("background-color: #3B82F6; padding: 12px; border-radius: 6px; font-weight: bold;")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
        self.setLayout(layout)

class DialogoCancion(QDialog):
    def __init__(self, parent=None, song_id=None, titulo="", letra=""):
        super().__init__(parent)
        self.song_id = song_id
        self.setWindowTitle("Editar Canción" if song_id else "Agregar Nueva Canción")
        self.resize(550, 650)
        self.setStyleSheet("background-color: #111827; color: #F8FAFC;")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Título:"))
        self.input_titulo = QLineEdit(titulo)
        self.input_titulo.setStyleSheet("background-color: #0B1020; border: 1px solid #1E293B; padding: 10px; border-radius: 6px;")
        layout.addWidget(self.input_titulo)
        layout.addWidget(QLabel("Letra (Separa estrofas con doble salto de línea):"))
        self.input_letra = QTextEdit()
        self.input_letra.setPlainText(letra)
        self.input_letra.setStyleSheet("background-color: #0B1020; border: 1px solid #1E293B; padding: 10px; border-radius: 6px;")
        layout.addWidget(self.input_letra)
        btn_guardar = QPushButton("💾 Guardar Canción")
        btn_guardar.setStyleSheet("background-color: #8A3FFC; color: white; padding: 14px; font-weight: bold; border-radius: 8px;")
        btn_guardar.clicked.connect(self.guardar_bd)
        layout.addWidget(btn_guardar)
        self.setLayout(layout)
        
    def guardar_bd(self):
        if not self.input_titulo.text().strip(): return
        if self.song_id: actualizar_cancion(self.song_id, self.input_titulo.text(), self.input_letra.toPlainText())
        else: agregar_cancion(self.input_titulo.text(), self.input_letra.toPlainText())
        self.accept()

class ControlPanel(QMainWindow):
    def __init__(self, proyector, stage_view, nombre_congregacion):
        super().__init__()
        self.proyector = proyector
        self.stage_view = stage_view
        self.nombre_congregacion = nombre_congregacion
        self.setWindowTitle(f"LuminaCast Studio | {nombre_congregacion}")
        self.resize(1600, 900) 
        
        self.esta_visible = True
        self.logo_activo = False
        self.reloj_activo = False
        self.cambiando_perfil = False
        self.tipo_proyeccion_actual = "cancion" 
        self.color_actual = "#ffffff"
        self.version_map = {}

        inicializar_db()
        self.cargar_configuraciones_globales()
        self.aplicar_tema_pro()

        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # CABECERA
        self.crear_header(layout_principal)

        # CUERPO PRINCIPAL (Splitter)
        self.splitter_principal = QSplitter(Qt.Orientation.Horizontal)
        self.splitter_principal.setHandleWidth(1)

        self.crear_panel_izquierdo()
        self.crear_panel_central_stack()
        self.crear_panel_derecho()

        layout_principal.addWidget(self.splitter_principal, 1)

        # RECUPERAR ESTADO DE PANELES (Persistencia)
        estado_panel_der = obtener_configuracion(f"{self.nombre_congregacion}_panel_der_visible")
        if estado_panel_der == "0":
            self.panel_der.hide()
            self.btn_toggle_der.setText("⏮️ Panel")

        # INICIALIZACIÓN DE DATA
        self.cargar_canciones_desde_db()
        self.cargar_galeria_fondos()
        self.cargar_versiones_ui()
        self.lista_biblioteca.setCurrentRow(0)

    # ================= 1. CABECERA =================
    def crear_header(self, layout_padre):
        header = QWidget()
        header.setObjectName("Header")
        header.setFixedHeight(60)
        lyt_header = QHBoxLayout(header)
        lyt_header.setContentsMargins(15, 0, 15, 0)
        lyt_header.setSpacing(15)

        btn_hamburguesa = QPushButton("☰")
        btn_hamburguesa.setFixedSize(35, 35)
        btn_hamburguesa.setStyleSheet("background: transparent; color: #94A3B8; font-size: 22px; border:none;")
        btn_hamburguesa.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_hamburguesa.clicked.connect(self.toggle_barra_lateral)
        lyt_header.addWidget(btn_hamburguesa)

        lyt_logo = QHBoxLayout()
        lyt_logo.setSpacing(10)
        self.lbl_logo_app = QLabel()
        self.lbl_logo_app.setFixedSize(35, 35)
        self.lbl_logo_app.setScaledContents(True)
        
        ruta_logo = os.path.join(os.path.dirname(__file__), '../../assets/logo.png')
        if os.path.exists(ruta_logo): 
            self.lbl_logo_app.setPixmap(QPixmap(ruta_logo))
        else:
            pix = QPixmap(35, 35); pix.fill(Qt.GlobalColor.transparent); p = QPainter(pix); p.setRenderHint(QPainter.RenderHint.Antialiasing)
            g = QLinearGradient(0, 0, 35, 35); g.setColorAt(0, QColor("#A855F7")); g.setColorAt(1, QColor("#3B82F6"))
            p.setBrush(g); p.setPen(Qt.PenStyle.NoPen); p.drawRoundedRect(0, 0, 35, 35, 8, 8)
            p.setPen(QColor("white")); p.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold)); p.drawText(QRect(0, 0, 35, 35), Qt.AlignmentFlag.AlignCenter, "L"); p.end()
            self.lbl_logo_app.setPixmap(pix)
            
        lbl_texto = QLabel("<span style='color: #F8FAFC;'>lumina</span><span style='color: #A855F7;'>C</span><span style='color: #8A3FFC;'>a</span><span style='color: #6366F1;'>s</span><span style='color: #3B82F6;'>t</span>")
        lbl_texto.setStyleSheet("font-size: 21px; font-weight: 900; font-family: 'Segoe UI'; background: transparent;")
        lyt_logo.addWidget(self.lbl_logo_app)
        lyt_logo.addWidget(lbl_texto)
        lyt_header.addLayout(lyt_logo)

        lyt_header.addStretch(1)

        # BOTONES SISTEMA
        for icono, texto, funcion in [("🖥️", "Pantallas", lambda: ScreenSettingsDialog(self).exec()), 
                                      ("⚙️", "Ajustes", lambda: AppAjustesDialog(self).exec()),
                                      ("🚪", "Salir", self.cerrar_perfil)]:
            btn = QPushButton(f"{icono} {texto}")
            btn.setObjectName("TopBtn")
            btn.clicked.connect(funcion)
            lyt_header.addWidget(btn)

        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.VLine)
        linea.setStyleSheet("color: #1E293B; margin-left: 5px; margin-right: 5px;")
        lyt_header.addWidget(linea)

        # TOGGLE PANEL DERECHO
        self.btn_toggle_der = QPushButton("⏭️ Panel")
        self.btn_toggle_der.setObjectName("TopBtn")
        self.btn_toggle_der.clicked.connect(self.toggle_panel_derecho)
        lyt_header.addWidget(self.btn_toggle_der)

        layout_padre.addWidget(header)

    def toggle_barra_lateral(self):
        self.panel_menu.setVisible(not self.panel_menu.isVisible())

    def toggle_panel_derecho(self):
        visible = self.panel_der.isVisible()
        self.panel_der.setVisible(not visible)
        self.btn_toggle_der.setText("⏮️ Panel" if visible else "⏭️ Panel")
        guardar_configuracion(f"{self.nombre_congregacion}_panel_der_visible", "0" if visible else "1")

    # ================= 2. MENÚ IZQUIERDO =================
    def crear_panel_izquierdo(self):
        self.panel_menu = QWidget()
        self.panel_menu.setObjectName("PanelMenu")
        self.panel_menu.setFixedWidth(200)
        lyt_menu = QVBoxLayout(self.panel_menu)
        lyt_menu.setContentsMargins(10, 15, 10, 15)
        
        lbl_bib = QLabel("BIBLIOTECA")
        lbl_bib.setObjectName("LabelMiniatura")
        lyt_menu.addWidget(lbl_bib)

        self.lista_biblioteca = QListWidget()
        self.lista_biblioteca.setObjectName("ListaNavegacion")
        for icon, text in [("🎵", "Canciones"), ("📖", "Biblias"), ("🖼️", "Media")]:
            self.lista_biblioteca.addItem(QListWidgetItem(f" {icon}   {text}"))
            
        self.lista_biblioteca.currentRowChanged.connect(self.cambiar_modulo)
        lyt_menu.addWidget(self.lista_biblioteca)
        lyt_menu.addStretch()
        
        self.splitter_principal.addWidget(self.panel_menu)

    # ================= 3. CENTRO =================
    def crear_panel_central_stack(self):
        self.stack_modulos = QStackedWidget()

        # --- ENTORNO 1: CANCIONES ---
        pag_canciones = QWidget()
        lyt_p1 = QHBoxLayout(pag_canciones)
        lyt_p1.setContentsMargins(0,0,0,0)
        split_can = QSplitter(Qt.Orientation.Horizontal)
        split_can.setHandleWidth(1)

        panel_exp = QWidget()
        panel_exp.setObjectName("PanelExplorer")
        lyt_exp = QVBoxLayout(panel_exp)
        lyt_exp.setContentsMargins(15, 15, 10, 15)
        
        self.input_buscar_can = QLineEdit()
        self.input_buscar_can.setPlaceholderText("🔍 Buscar canción...")
        self.input_buscar_can.textChanged.connect(self.filtrar_canciones)
        self.lista_canciones = QListWidget()
        self.lista_canciones.setObjectName("ListaNormal")
        self.lista_canciones.itemClicked.connect(self.cargar_diapositivas_cancion)
        btn_add = QPushButton("➕ Nueva Canción")
        btn_add.setObjectName("BtnOscuro")
        btn_add.clicked.connect(self.agregar_nueva_cancion)
        
        lyt_exp.addWidget(self.input_buscar_can)
        lyt_exp.addWidget(self.lista_canciones)
        lyt_exp.addWidget(btn_add)

        panel_mid = QWidget()
        panel_mid.setObjectName("PanelCentral")
        lyt_mid = QVBoxLayout(panel_mid)
        lyt_mid.setContentsMargins(15, 15, 15, 15)

        self.lista_diapositivas = QListWidget()
        self.lista_diapositivas.setObjectName("GridDiapositivas")
        self.lista_diapositivas.setViewMode(QListWidget.ViewMode.IconMode)
        self.lista_diapositivas.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.lista_diapositivas.setSpacing(12)
        self.lista_diapositivas.setGridSize(QSize(200, 130))
        self.lista_diapositivas.itemClicked.connect(self.previsualizar_diapositiva_cancion)
        self.lista_diapositivas.itemDoubleClicked.connect(self.disparar_diapositiva_cancion)
        lyt_mid.addWidget(self.lista_diapositivas)

        split_can.addWidget(panel_exp)
        split_can.addWidget(panel_mid)
        split_can.setSizes([260, 800])
        lyt_p1.addWidget(split_can)
        self.stack_modulos.addWidget(pag_canciones)

        # --- ENTORNO 2: BIBLIAS ---
        pag_biblias = QWidget()
        lyt_p2 = QHBoxLayout(pag_biblias)
        lyt_p2.setContentsMargins(0,0,0,0)
        split_bib = QSplitter(Qt.Orientation.Horizontal)
        split_bib.setHandleWidth(1)

        panel_ver = QWidget()
        panel_ver.setObjectName("PanelExplorer")
        lyt_ver = QVBoxLayout(panel_ver)
        lyt_ver.setContentsMargins(12, 15, 10, 15)
        lbl_v = QLabel("VERSIONES")
        lbl_v.setObjectName("LabelMiniatura")
        lyt_ver.addWidget(lbl_v)
        self.lista_versiones = QListWidget()
        self.lista_versiones.setObjectName("ListaNormal")
        self.lista_versiones.currentRowChanged.connect(self.cambiar_version_biblia_desde_lista)
        lyt_ver.addWidget(self.lista_versiones)
        lyt_ver.addStretch()

        panel_lib = QWidget()
        panel_lib.setObjectName("PanelExplorer")
        lyt_lib = QVBoxLayout(panel_lib)
        lyt_lib.setContentsMargins(10, 15, 10, 15)
        self.input_buscar_bib = QLineEdit()
        self.input_buscar_bib.setPlaceholderText("🔍 Buscar libro...")
        self.arbol_libros = QTreeWidget()
        self.arbol_libros.setObjectName("ArbolLibros")
        self.arbol_libros.setHeaderHidden(True)
        self.arbol_libros.itemClicked.connect(self.seleccionar_libro_arbol)
        lyt_lib.addWidget(self.input_buscar_bib)
        lyt_lib.addWidget(self.arbol_libros)

        panel_lec = QWidget()
        panel_lec.setObjectName("PanelCentral")
        lyt_lec = QVBoxLayout(panel_lec)
        lyt_lec.setContentsMargins(15, 15, 15, 15)
        lyt_cab_bib = QHBoxLayout()
        self.lbl_titulo_lectura = QLabel("Selecciona un libro")
        self.lbl_titulo_lectura.setStyleSheet("font-size: 24px; font-weight: bold; color: #8A3FFC;")
        self.combo_cap_rapido = QComboBox()
        self.combo_cap_rapido.setFixedWidth(80)
        self.combo_cap_rapido.currentIndexChanged.connect(self.cargar_versiculos_biblia)
        lyt_cab_bib.addWidget(self.lbl_titulo_lectura)
        lyt_cab_bib.addStretch()
        lyt_cab_bib.addWidget(QLabel("Cap:"))
        lyt_cab_bib.addWidget(self.combo_cap_rapido)
        lyt_lec.addLayout(lyt_cab_bib)
        
        self.lista_lectura = QListWidget()
        self.lista_lectura.setObjectName("ListaLectura")
        self.lista_lectura.setWordWrap(True)
        self.lista_lectura.itemClicked.connect(self.previsualizar_versiculo)
        self.lista_lectura.itemDoubleClicked.connect(self.disparar_versiculo_directo)
        lyt_lec.addWidget(self.lista_lectura)

        split_bib.addWidget(panel_ver)
        split_bib.addWidget(panel_lib)
        split_bib.addWidget(panel_lec)
        split_bib.setSizes([180, 240, 600])
        lyt_p2.addWidget(split_bib)
        self.stack_modulos.addWidget(pag_biblias)

        # --- ENTORNO 3: MEDIA ---
        pag_media = QWidget()
        pag_media.setObjectName("PanelCentral")
        lyt_p3 = QVBoxLayout(pag_media)
        lyt_p3.setContentsMargins(20, 15, 20, 15)
        self.lista_media = QListWidget()
        self.lista_media.setObjectName("GridMedia")
        self.lista_media.setViewMode(QListWidget.ViewMode.IconMode)
        self.lista_media.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.lista_media.setIconSize(QSize(170, 100))
        self.lista_media.setGridSize(QSize(190, 140))
        self.lista_media.setSpacing(12)
        self.lista_media.itemClicked.connect(self.aplicar_fondo)
        
        lbl_m = QLabel("GALERÍA DE MEDIOS")
        lbl_m.setObjectName("LabelMiniatura")
        lyt_p3.addWidget(lbl_m)
        lyt_p3.addWidget(self.lista_media)
        self.stack_modulos.addWidget(pag_media)

        self.splitter_principal.addWidget(self.stack_modulos)

    # ================= 4. PANEL DERECHO (CONTROL Y PREVIEWS) =================
    def crear_panel_derecho(self):
        self.panel_der = QWidget()
        self.panel_der.setObjectName("PanelRight")
        self.panel_der.setMinimumWidth(340)
        lyt_der = QVBoxLayout(self.panel_der)
        lyt_der.setContentsMargins(15, 20, 15, 20)
        lyt_der.setSpacing(12)

        # 1. BOTONES SUPERIORES RAPIDOS
        lyt_botones_top = QHBoxLayout()
        self.btn_clear = QPushButton("⬛ Limpiar Pantalla")
        self.btn_clear.setObjectName("HeaderBtnClear")
        self.btn_clear.clicked.connect(self.toggle_ojo)

        self.btn_logo = QPushButton("🖼️ Logo")
        self.btn_logo.setObjectName("HeaderBtnAction")
        self.btn_logo.clicked.connect(self.toggle_logo)
        self.btn_logo.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_logo.customContextMenuRequested.connect(self.menu_opciones_logo)

        self.btn_reloj = QPushButton("⏱️ Reloj")
        self.btn_reloj.setObjectName("HeaderBtnAction")
        self.btn_reloj.clicked.connect(self.toggle_reloj)
        self.btn_reloj.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_reloj.customContextMenuRequested.connect(self.menu_opciones_reloj)
        
        lyt_botones_top.addWidget(self.btn_clear)
        lyt_botones_top.addWidget(self.btn_logo)
        lyt_botones_top.addWidget(self.btn_reloj)
        lyt_der.addLayout(lyt_botones_top)

        # 2. ENVIAR A PANTALLA
        self.btn_proyectar_principal = QPushButton("🚀 ENVIAR A PANTALLA")
        self.btn_proyectar_principal.setObjectName("BtnLive")
        self.btn_proyectar_principal.clicked.connect(self.enviar_en_vivo_desde_panel_derecho)
        lyt_der.addWidget(self.btn_proyectar_principal)

        # 3. SISTEMA DE PREVIEWS INTERCALADOS (PESTAÑAS)
        lyt_tabs_prev = QHBoxLayout()
        lyt_tabs_prev.setSpacing(0)
        self.btn_tab_pub = QPushButton("🖥️ PÚBLICO")
        self.btn_tab_stg = QPushButton("🎸 STAGE")
        self.btn_tab_pub.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tab_stg.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.btn_tab_pub.setStyleSheet("background-color: #8A3FFC; color: white; padding: 8px; border-top-left-radius: 6px; font-weight: bold;")
        self.btn_tab_stg.setStyleSheet("background-color: #1E293B; color: #94A3B8; padding: 8px; border-top-right-radius: 6px; font-weight: bold;")
        
        self.btn_tab_pub.clicked.connect(lambda: self.cambiar_pestana_preview(0))
        self.btn_tab_stg.clicked.connect(lambda: self.cambiar_pestana_preview(1))
        
        lyt_tabs_prev.addWidget(self.btn_tab_pub)
        lyt_tabs_prev.addWidget(self.btn_tab_stg)
        lyt_der.addLayout(lyt_tabs_prev)

        self.stack_previews = QStackedWidget()
        
        # Monitor Público
        self.monitor_previa_publico = QLabel("...")
        self.monitor_previa_publico.setObjectName("MonitorPreview")
        self.monitor_previa_publico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monitor_previa_publico.setWordWrap(True)
        self.stack_previews.addWidget(self.monitor_previa_publico)

        # Monitor Stage
        self.monitor_previa_interno = QLabel("...")
        self.monitor_previa_interno.setObjectName("MonitorPreviewStage")
        self.monitor_previa_interno.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.monitor_previa_interno.setWordWrap(True)
        self.stack_previews.addWidget(self.monitor_previa_interno)

        lyt_der.addWidget(self.stack_previews, stretch=2)

        # 4. CONTROLES DEL STAGE (CRONÓMETRO Y MENSAJES)
        lbl_stg_ctrl = QLabel("🛠️ CONTROLES DEL STAGE")
        lbl_stg_ctrl.setObjectName("LabelMiniatura")
        lyt_der.addWidget(lbl_stg_ctrl)
        
        # Fila Cronómetro
        lyt_crono = QHBoxLayout()
        lyt_crono.addWidget(QLabel("⏱️ Cronómetro:"))
        self.spin_crono_min = QSpinBox()
        self.spin_crono_min.setRange(1, 120)
        self.spin_crono_min.setSuffix(" min")
        
        btn_crono_play = QPushButton("▶")
        btn_crono_play.setStyleSheet("background-color: #10B981; color: white; border-radius: 4px; padding: 6px;")
        btn_crono_play.clicked.connect(self.iniciar_cronometro)
        
        btn_crono_stop = QPushButton("⏹")
        btn_crono_stop.setStyleSheet("background-color: #EF4444; color: white; border-radius: 4px; padding: 6px;")
        btn_crono_stop.clicked.connect(self.detener_cronometro)
        
        lyt_crono.addWidget(self.spin_crono_min)
        lyt_crono.addWidget(btn_crono_play)
        lyt_crono.addWidget(btn_crono_stop)
        lyt_der.addLayout(lyt_crono)

        # Fila Mensajes
        lyt_msg = QHBoxLayout()
        self.input_stage_msg = QLineEdit()
        self.input_stage_msg.setPlaceholderText("Alerta al stage...")
        self.input_stage_msg.returnPressed.connect(self.enviar_mensaje_stage)
        
        btn_send_msg = QPushButton("Enviar")
        btn_send_msg.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold; padding: 8px; border-radius: 6px;")
        btn_send_msg.clicked.connect(self.enviar_mensaje_stage)
        
        btn_clear_msg = QPushButton("X")
        btn_clear_msg.setStyleSheet("background-color: #1E293B; color: white; padding: 8px; border-radius: 6px;")
        btn_clear_msg.clicked.connect(self.limpiar_mensaje_stage)
        
        lyt_msg.addWidget(self.input_stage_msg)
        lyt_msg.addWidget(btn_send_msg)
        lyt_msg.addWidget(btn_clear_msg)
        lyt_der.addLayout(lyt_msg)

        # 5. PROPIEDADES (ESTILO)
        lbl_prop = QLabel("🎨 DISEÑO DE TEXTO")
        lbl_prop.setObjectName("LabelMiniatura")
        lyt_der.addWidget(lbl_prop)

        lyt_prop = QHBoxLayout()
        self.combo_fuente = QFontComboBox()
        self.combo_fuente.currentFontChanged.connect(self.aplicar_propiedades_texto)
        self.spin_tamano = QSpinBox()
        self.spin_tamano.setRange(20, 150)
        self.spin_tamano.valueChanged.connect(self.aplicar_propiedades_texto)
        lyt_prop.addWidget(self.combo_fuente, stretch=2)
        lyt_prop.addWidget(self.spin_tamano, stretch=1)
        lyt_der.addLayout(lyt_prop)

        grid_c = QGridLayout()
        grid_c.setSpacing(5)
        colores = ["#ffffff", "#facc15", "#60a5fa", "#34d399", "#f87171", "#c084fc"]
        for i, col in enumerate(colores):
            b = QPushButton()
            b.setFixedSize(30, 30)
            b.setStyleSheet(f"background-color: {col}; border-radius: 6px; border: 1px solid #1E293B;")
            b.clicked.connect(lambda checked, c=col: self.set_color_texto(c))
            grid_c.addWidget(b, 0, i)
        lyt_der.addLayout(grid_c)
        
        lyt_der.addStretch()

        self.combo_fuente.setCurrentFont(QFont(self.proyector.fuente_actual))
        self.spin_tamano.setValue(self.proyector.tamano_letra_actual)
        self.color_actual = self.proyector.color_letra_actual

        self.splitter_principal.addWidget(self.panel_der)

    # ================= MÉTODOS DE PESTAÑAS PREVIEW =================
    def cambiar_pestana_preview(self, index):
        self.stack_previews.setCurrentIndex(index)
        if index == 0:
            self.btn_tab_pub.setStyleSheet("background-color: #8A3FFC; color: white; padding: 8px; border-top-left-radius: 6px; font-weight: bold;")
            self.btn_tab_stg.setStyleSheet("background-color: #1E293B; color: #94A3B8; padding: 8px; border-top-right-radius: 6px; font-weight: bold;")
        else:
            self.btn_tab_pub.setStyleSheet("background-color: #1E293B; color: #94A3B8; padding: 8px; border-top-left-radius: 6px; font-weight: bold;")
            self.btn_tab_stg.setStyleSheet("background-color: #8A3FFC; color: white; padding: 8px; border-top-right-radius: 6px; font-weight: bold;")

    # ================= MÉTODOS CONTROLES STAGE =================
    def iniciar_cronometro(self):
        minutos = self.spin_crono_min.value()
        if self.stage_view:
            self.stage_view.iniciar_cronometro(minutos * 60)
            
    def detener_cronometro(self):
        if self.stage_view:
            self.stage_view.detener_cronometro()

    def enviar_mensaje_stage(self):
        msg = self.input_stage_msg.text()
        if self.stage_view:
            self.stage_view.mostrar_mensaje_interno(msg)
            
    def limpiar_mensaje_stage(self):
        self.input_stage_msg.clear()
        if self.stage_view:
            self.stage_view.mostrar_mensaje_interno("")

    def toggle_reloj(self):
        self.reloj_activo = not self.reloj_activo
        self.proyector.toggle_reloj(self.reloj_activo)
        guardar_configuracion(f"{self.nombre_congregacion}_reloj_activo", "1" if self.reloj_activo else "0")

    def toggle_ojo(self):
        self.esta_visible = not self.esta_visible
        self.proyector.ocultar_proyeccion(not self.esta_visible)
        if self.stage_view: self.stage_view.ocultar_proyeccion(not self.esta_visible)
        
        if self.esta_visible:
            self.btn_clear.setText("⬛ Limpiar Pantalla")
            self.btn_clear.setStyleSheet("background-color: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); color: #ef4444; font-weight: bold; padding: 6px 15px; border-radius: 6px;")
        else:
            self.btn_clear.setText("▶ Mostrar Pantalla")
            self.btn_clear.setStyleSheet("background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.4); color: #10b981; font-weight: bold; padding: 6px 15px; border-radius: 6px;")

    def toggle_logo(self):
        if not self.ruta_logo_global: return
        self.logo_activo = not self.logo_activo
        self.proyector.toggle_logo(self.logo_activo, self.ruta_logo_global)

    def menu_opciones_logo(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #1E293B; color: white; border: 1px solid #3d3d4e; padding: 5px; } QMenu::item:selected { background-color: #8A3FFC; border-radius: 3px; }")
        menu.addAction("📁 Cambiar archivo de Logo...").triggered.connect(self.seleccionar_logo_archivo)
        menu.addSeparator()
        menu_pos = menu.addMenu("📍 Posición en Pantalla")
        for p in ["Arriba - Izquierda", "Arriba - Derecha", "Abajo - Izquierda", "Abajo - Derecha", "Centro"]:
            menu_pos.addAction(p).triggered.connect(lambda checked, pos=p: guardar_configuracion(f"{self.nombre_congregacion}_logo_posicion", pos))
        menu.exec(self.btn_logo.mapToGlobal(pos))

    def menu_opciones_reloj(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #1E293B; color: white; border: 1px solid #3d3d4e; padding: 5px; } QMenu::item:selected { background-color: #8A3FFC; border-radius: 3px; }")
        menu_pos = menu.addMenu("📍 Posición del Reloj")
        for p in ["Arriba - Izquierda", "Arriba - Derecha", "Abajo - Izquierda", "Abajo - Derecha"]:
            menu_pos.addAction(p).triggered.connect(lambda checked, pos=p: self.cambiar_posicion_reloj(pos))
        menu.exec(self.btn_reloj.mapToGlobal(pos))

    def cambiar_posicion_reloj(self, posicion):
        guardar_configuracion(f"{self.nombre_congregacion}_reloj_posicion", posicion)
        tamano = int(obtener_configuracion(f"{self.nombre_congregacion}_reloj_tamano") or 20)
        self.proyector.configurar_reloj(tamano, posicion)

    def seleccionar_logo_archivo(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar Logo", "", "Imágenes (*.png *.jpg *.jpeg)")
        if archivo:
            self.ruta_logo_global = archivo
            guardar_configuracion(f"{self.nombre_congregacion}_logo_ruta", archivo)

    # ================= LÓGICA CORE NAVEGACIÓN Y DATA =================
    def cambiar_modulo(self, index):
        if index == 0:
            self.stack_modulos.setCurrentIndex(0)
            self.tipo_proyeccion_actual = "cancion"
        elif index == 1:
            self.stack_modulos.setCurrentIndex(1)
            self.tipo_proyeccion_actual = "biblia"
            if getattr(self, 'lista_versiones', None) and self.lista_versiones.count() > 0 and self.lista_versiones.currentRow() == -1: 
                self.lista_versiones.setCurrentRow(0)
        elif index == 2: 
            self.stack_modulos.setCurrentIndex(2)
            self.tipo_proyeccion_actual = "media"

    def cargar_configuraciones_globales(self):
        self.reloj_activo = obtener_configuracion(f"{self.nombre_congregacion}_reloj_activo") == "1"
        self.logo_activo = obtener_configuracion(f"{self.nombre_congregacion}_logo_activo") == "1"
        self.ruta_logo_global = obtener_configuracion(f"{self.nombre_congregacion}_logo_ruta")
        letra_fuente = obtener_configuracion(f"{self.nombre_congregacion}_letra_fuente") or "Segoe UI"
        letra_tamano = int(obtener_configuracion(f"{self.nombre_congregacion}_letra_tamano") or 65)
        letra_color = obtener_configuracion(f"{self.nombre_congregacion}_letra_color") or "#ffffff"
        self.proyector.actualizar_estilo_texto(letra_fuente, letra_tamano, letra_color)
        if self.ruta_logo_global and os.path.exists(self.ruta_logo_global):
            self.proyector.toggle_logo(self.logo_activo, self.ruta_logo_global)

    def crear_miniatura_diapositiva(self, texto):
        pixmap = QPixmap(190, 110); pixmap.fill(QColor("#111827")); painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing); painter.setPen(QPen(QColor("#1E293B"), 1))
        painter.drawRoundedRect(1, 1, 188, 108, 6, 6); painter.setPen(QColor("#F8FAFC"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        texto_limpio = re.sub(r'\[.*?\]', '', texto).strip()
        painter.drawText(QRect(8, 8, 174, 94), Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.TextWordWrap, texto_limpio)
        painter.end()
        return QIcon(pixmap)

    # --- CANCIONES ---
    def cargar_canciones_desde_db(self):
        self.lista_canciones.clear()
        canciones = obtener_todas_las_canciones()
        if not canciones: 
            agregar_cancion("1. Alaba a Dios", "Alaba a Dios en su santuario\nAlábale en su firmamento\n\nAlábale por sus proezas")
            canciones = obtener_todas_las_canciones()
        for song_id, titulo in canciones:
            item = QListWidgetItem(titulo)
            item.setData(Qt.ItemDataRole.UserRole, song_id)
            self.lista_canciones.addItem(item)

    def filtrar_canciones(self, texto):
        for i in range(self.lista_canciones.count()):
            self.lista_canciones.item(i).setHidden(texto.lower() not in self.lista_canciones.item(i).text().lower())

    def agregar_nueva_cancion(self):
        if DialogoCancion(self).exec(): self.cargar_canciones_desde_db()

    def cargar_diapositivas_cancion(self, item):
        if not item: return
        try:
            self.lista_diapositivas.clear()
            letra = obtener_letra_cancion(item.data(Qt.ItemDataRole.UserRole))
            if letra:
                for bloque in letra.split("\n\n"):
                    if bloque.strip():
                        slide_item = QListWidgetItem()
                        slide_item.setIcon(self.crear_miniatura_diapositiva(bloque.strip()))
                        slide_item.setData(Qt.ItemDataRole.UserRole, bloque.strip()) 
                        self.lista_diapositivas.addItem(slide_item)
        except Exception as e: print(f"Error cargando canción: {e}")

    def previsualizar_diapositiva_cancion(self, item):
        texto_actual = item.data(Qt.ItemDataRole.UserRole)
        texto_limpio = re.sub(r'\[.*?\]', '', texto_actual).strip()
        self.monitor_previa_publico.setText(texto_limpio)
        
        row = self.lista_diapositivas.row(item)
        texto_sig = ""
        if row + 1 < self.lista_diapositivas.count():
            texto_sig = re.sub(r'\[.*?\]', '', self.lista_diapositivas.item(row + 1).data(Qt.ItemDataRole.UserRole)).strip()

        stage_html = f"<span style='color: #FACC15; font-size: 20px; font-weight:bold;'>{texto_limpio}</span><br><br><span style='color: #94A3B8; font-size: 14px;'>Sig: {texto_sig}</span>"
        self.monitor_previa_interno.setText(stage_html)

    def disparar_diapositiva_cancion(self, item): 
        self.previsualizar_diapositiva_cancion(item)
        self.enviar_en_vivo_cancion()

    def enviar_en_vivo_cancion(self):
        item = self.lista_diapositivas.currentItem()
        if not item: return
        texto_limpio = re.sub(r'\[.*?\]', '', item.data(Qt.ItemDataRole.UserRole)).strip()
        self.proyector.proyectar_texto(texto_limpio, "cancion")
        
        row = self.lista_diapositivas.row(item)
        texto_sig = ""
        if row + 1 < self.lista_diapositivas.count():
            texto_sig = re.sub(r'\[.*?\]', '', self.lista_diapositivas.item(row + 1).data(Qt.ItemDataRole.UserRole)).strip()
        if self.stage_view: self.stage_view.proyectar_texto(texto_limpio, texto_sig)

    # --- BIBLIAS ---
    def cargar_versiones_ui(self):
        self.lista_versiones.clear(); self.version_map = {} 
        for v_id, nombre, abrev in obtener_versiones_biblia():
            item = QListWidgetItem(f"📄 {abrev}")
            item.setData(Qt.ItemDataRole.UserRole, v_id)
            self.version_map[v_id] = nombre
            self.lista_versiones.addItem(item)
            
    def cambiar_version_biblia_desde_lista(self, row):
        if row < 0 or not hasattr(self, 'version_map'): return
        item = self.lista_versiones.item(row)
        if not item: return
        v_id = item.data(Qt.ItemDataRole.UserRole)
        self.cargar_libros_arbol(v_id)

    def cargar_libros_arbol(self, v_id):
        self.arbol_libros.clear()
        antiguo = QTreeWidgetItem(self.arbol_libros, ["Antiguo Testamento"])
        nuevo = QTreeWidgetItem(self.arbol_libros, ["Nuevo Testamento"])
        for l_id, nombre in obtener_libros_biblia(v_id):
            nodo = antiguo if l_id <= 39 else nuevo
            item_libro = QTreeWidgetItem(nodo, [nombre])
            item_libro.setData(0, Qt.ItemDataRole.UserRole, l_id)
        self.arbol_libros.expandAll()

    def seleccionar_libro_arbol(self, item, col):
        l_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not l_id: return 
        self.lbl_titulo_lectura.setText(item.text(0))
        self.combo_cap_rapido.blockSignals(True)
        self.combo_cap_rapido.clear()
        for cap in obtener_capitulos_biblia(l_id): self.combo_cap_rapido.addItem(str(cap), cap)
        self.combo_cap_rapido.blockSignals(False)
        self.libro_actual_id = l_id
        if self.combo_cap_rapido.count() > 0:
            self.combo_cap_rapido.setCurrentIndex(0)
            self.cargar_versiculos_biblia()

    def cargar_versiculos_biblia(self):
        self.lista_lectura.clear()
        if not hasattr(self, 'libro_actual_id'): return
        l_id = self.libro_actual_id
        cap = self.combo_cap_rapido.currentData()
        libro_nombre = self.lbl_titulo_lectura.text().split(" ")[0]
        if l_id and cap:
            self.lbl_titulo_lectura.setText(f"{libro_nombre} {cap}")
            for ver_num, texto in obtener_versiculos_biblia(l_id, cap):
                item = QListWidgetItem(f"{ver_num}  {texto}")
                item.setData(Qt.ItemDataRole.UserRole, (libro_nombre, cap, ver_num, texto))
                self.lista_lectura.addItem(item)

    def previsualizar_versiculo(self, item):
        libro_nombre, capitulo, ver_num, texto_actual = item.data(Qt.ItemDataRole.UserRole)
        txt_publico = f"{texto_actual}\n[{libro_nombre} {capitulo}:{ver_num}]"
        self.monitor_previa_publico.setText(txt_publico)
        
        row = self.lista_lectura.row(item)
        texto_sig = ""
        if row + 1 < self.lista_lectura.count():
            l_n, c, v_n, txt_s = self.lista_lectura.item(row + 1).data(Qt.ItemDataRole.UserRole)
            texto_sig = f"{txt_s} [{v_n}]"
            
        stage_html = f"<span style='color: #FACC15; font-size: 20px; font-weight:bold;'>{txt_publico}</span><br><br><span style='color: #94A3B8; font-size: 14px;'>Sig: {texto_sig}</span>"
        self.monitor_previa_interno.setText(stage_html)

    def disparar_versiculo_directo(self, item):
        self.previsualizar_versiculo(item)
        self.enviar_en_vivo_biblia()

    def enviar_en_vivo_biblia(self):
        item = self.lista_lectura.currentItem()
        if not item: return
        libro_nombre, capitulo, ver_num, texto_actual = item.data(Qt.ItemDataRole.UserRole)
        txt_publico = f"{texto_actual}\n[{libro_nombre} {capitulo}:{ver_num}]"
        self.proyector.proyectar_texto(txt_publico, "biblia")
        
        row = self.lista_lectura.row(item)
        texto_sig = ""
        if row + 1 < self.lista_lectura.count():
            _, _, v_n, txt_s = self.lista_lectura.item(row + 1).data(Qt.ItemDataRole.UserRole)
            texto_sig = f"{txt_s} [{v_n}]"
            
        if self.stage_view: self.stage_view.proyectar_texto(txt_publico, texto_sig)

    # --- MEDIA ---
    def cargar_galeria_fondos(self):
        self.lista_media.clear()
        
        pix_sin = QPixmap(170, 100)
        pix_sin.fill(QColor("#000000"))
        p_sin = QPainter(pix_sin)
        p_sin.setRenderHint(QPainter.RenderHint.Antialiasing)
        p_sin.setPen(QPen(QColor("#1E293B"), 2))
        p_sin.drawRoundedRect(1, 1, 168, 98, 8, 8)
        p_sin.setPen(QColor("#94A3B8"))
        p_sin.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p_sin.drawText(QRect(0, 0, 170, 100), Qt.AlignmentFlag.AlignCenter, "SIN FONDO")
        p_sin.end()
        
        item_sin = QListWidgetItem()
        item_sin.setIcon(QIcon(pix_sin))
        item_sin.setData(Qt.ItemDataRole.UserRole, "sin_fondo")
        self.lista_media.addItem(item_sin)
        
        ruta = os.path.join(os.path.dirname(__file__), '../../assets/fondos')
        if os.path.exists(ruta):
            for f in os.listdir(ruta):
                ruta_completa = os.path.join(ruta, f)
                ext = f.lower().split('.')[-1]
                
                if ext in ['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov']:
                    if ext in ['mp4', 'avi', 'mov']:
                        pix_vid = QPixmap(170, 100)
                        pix_vid.fill(QColor("#111827"))
                        p = QPainter(pix_vid)
                        p.setRenderHint(QPainter.RenderHint.Antialiasing)
                        p.setPen(QPen(QColor("#1E293B"), 2))
                        p.drawRoundedRect(1, 1, 168, 98, 8, 8)
                        p.setPen(QColor("#8A3FFC"))
                        p.setFont(QFont("Segoe UI", 24))
                        p.drawText(QRect(0, 15, 170, 40), Qt.AlignmentFlag.AlignCenter, "🎬")
                        p.setPen(QColor("#94A3B8"))
                        p.setFont(QFont("Segoe UI", 9))
                        nombre_corto = f[:18] + "..." if len(f) > 18 else f
                        p.drawText(QRect(0, 60, 170, 30), Qt.AlignmentFlag.AlignCenter, nombre_corto)
                        p.end()
                        
                        item = QListWidgetItem()
                        item.setIcon(QIcon(pix_vid))
                        item.setData(Qt.ItemDataRole.UserRole, ruta_completa)
                        self.lista_media.addItem(item)
                    else:
                        pix_img = QPixmap(ruta_completa).scaled(170, 100, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                        canvas = QPixmap(170, 100)
                        canvas.fill(Qt.GlobalColor.transparent)
                        p = QPainter(canvas)
                        p.setRenderHint(QPainter.RenderHint.Antialiasing)
                        path = QPainterPath()
                        path.addRoundedRect(0, 0, 170, 100, 8, 8)
                        p.setClipPath(path)
                        p.drawPixmap(0, 0, pix_img)
                        p.end()

                        item = QListWidgetItem()
                        item.setIcon(QIcon(canvas))
                        item.setData(Qt.ItemDataRole.UserRole, ruta_completa)
                        self.lista_media.addItem(item)

    def aplicar_fondo(self, item): 
        self.proyector.cambiar_fondo(item.data(Qt.ItemDataRole.UserRole))

    def enviar_en_vivo_desde_panel_derecho(self):
        if self.tipo_proyeccion_actual == "cancion":
            self.enviar_en_vivo_cancion()
        elif self.tipo_proyeccion_actual == "biblia":
            self.enviar_en_vivo_biblia()

    def aplicar_propiedades_texto(self):
        fuente = self.combo_fuente.currentText()
        tamano = self.spin_tamano.value()
        self.proyector.actualizar_estilo_texto(fuente, tamano, self.color_actual)
        guardar_configuracion(f"{self.nombre_congregacion}_letra_fuente", fuente)
        guardar_configuracion(f"{self.nombre_congregacion}_letra_tamano", str(tamano))

    def set_color_texto(self, hex_color):
        self.color_actual = hex_color
        self.aplicar_propiedades_texto()
        guardar_configuracion(f"{self.nombre_congregacion}_letra_color", hex_color)

    def aplicar_transicion(self):
        tipo = "Corte" if "Corte" in self.combo_trans_tipo.currentText() else "Fade"
        self.proyector.configurar_transiciones(tipo, 300, tipo, 300)

    # ================= CSS GLOBAL =================
    def aplicar_tema_pro(self):
        qss = """
        QMainWindow, QDialog, QStackedWidget { background-color: #0B1020; color: #F8FAFC; font-family: 'Segoe UI', Arial, sans-serif; }
        QWidget { color: #F8FAFC; }
        #Header { background-color: #111827; border-bottom: 1px solid #1E293B; }
        #PanelMenu { background-color: #111827; border-right: 1px solid #1E293B; }
        #PanelExplorer { background-color: #0B1020; border-right: 1px solid #1E293B; }
        #PanelCentral { background-color: #0B1020; }
        #PanelRight { background-color: #111827; border-left: 1px solid #1E293B; }
        
        QSplitter::handle { background-color: #1E293B; }
        #LabelMiniatura { color: #94A3B8; font-size: 11px; font-weight: 800; letter-spacing: 1px; margin-top: 8px; margin-bottom: 4px; }
        
        #ListaNavegacion { background-color: transparent; border: none; outline: none; font-size: 14px; }
        #ListaNavegacion::item { padding: 12px 15px; border-radius: 6px; color: #94A3B8; margin-bottom: 2px; }
        #ListaNavegacion::item:selected { background-color: #1A1F35; color: #F8FAFC; font-weight: bold; border-left: 4px solid #8A3FFC; }
        #ListaNavegacion::item:hover:!selected { background-color: rgba(26, 31, 53, 0.4); color: #F8FAFC; }
        
        #ListaNormal { background-color: transparent; border: none; outline: none; font-size: 13px; }
        #ListaNormal::item { padding: 9px; border-radius: 4px; color: #94A3B8; border-bottom: 1px solid rgba(30, 41, 59, 0.3); }
        #ListaNormal::item:selected { background-color: #1A1F35; color: #F8FAFC; font-weight: bold; }
        
        #ArbolLibros { background-color: transparent; border: none; font-size: 13px; outline: none; }
        #ArbolLibros::item { padding: 6px; color: #94A3B8; }
        #ArbolLibros::item:selected { color: #8A3FFC; font-weight: bold; }
        
        #ListaLectura { background-color: transparent; border: none; outline: none; font-size: 15px; }
        #ListaLectura::item { padding: 12px; border-bottom: 1px solid #1E293B; color: #94A3B8; }
        #ListaLectura::item:selected { color: #38BDF8; font-weight: bold; background-color: #1A1F35; border-left: 4px solid #3B82F6; }
        
        #MonitorPreview { background-color: #050811; border: 2px solid #1E293B; border-radius: 8px; font-size: 20px; padding: 10px; color: #F8FAFC; }
        #MonitorPreviewStage { background-color: #000000; border: 2px solid #1E293B; border-radius: 8px; padding: 10px; font-size: 14px; }
        
        #GridDiapositivas { background-color: transparent; border: none; outline: none; }
        #GridDiapositivas::item { background-color: #111827; border: 2px solid #1E293B; border-radius: 8px; color: transparent; }
        #GridDiapositivas::item:selected { border: 2px solid #8A3FFC; background-color: #1A1F35; }

        #GridMedia { background-color: transparent; border: none; outline: none; }
        #GridMedia::item { background-color: transparent; border: 2px solid transparent; border-radius: 10px; color: transparent; }
        #GridMedia::item:selected { border: 2px solid #38BDF8; background-color: rgba(56, 189, 248, 0.1); }
        
        QLineEdit, QComboBox, QSpinBox { background-color: #0B1020; border: 1px solid #1E293B; padding: 8px 12px; font-size: 13px; border-radius: 6px; color: #F8FAFC; }
        QComboBox::drop-down { border: none; }
        
        #TopBtn { background-color: transparent; color: #94A3B8; font-weight: bold; padding: 8px 12px; border-radius: 6px; font-size: 13px; }
        #TopBtn:hover { background-color: #1E293B; color: #F8FAFC; }
        
        #HeaderBtnClear { background-color: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.4); color: #ef4444; font-weight: bold; padding: 6px 15px; border-radius: 6px; }
        
        #HeaderBtnAction { background-color: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.4); color: #38BDF8; font-weight: bold; padding: 6px 15px; border-radius: 6px; }
        #HeaderBtnAction:hover { background-color: #38BDF8; color: white; }
        
        #BtnOscuro { background-color: #1E293B; color: #F8FAFC; padding: 10px; border-radius: 6px; border: none; font-weight: bold; }
        #BtnOscuro:hover { background-color: #1A1F35; border: 1px solid #8A3FFC; }
        
        #BtnLive { 
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8A3FFC, stop:1 #3B82F6); 
            color: white; font-weight: 900; font-size: 14px; border-radius: 10px; padding: 14px; border: 1px solid #A855F7; letter-spacing: 1px;
        }
        #BtnLive:hover { border: 1px solid #38BDF8; }
        """
        self.setStyleSheet(qss)

    def cerrar_perfil(self):
        self.cambiando_perfil = True
        guardar_configuracion("ultimo_perfil", "")
        if self.proyector: self.proyector.close()
        if self.stage_view: self.stage_view.close()
        self.close()

    def closeEvent(self, event): 
        if self.cambiando_perfil: QApplication.instance().exit(42)
        else: QApplication.instance().exit(0)
        event.accept()