# src/ui/profile_selector.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox, QListWidgetItem)
from PyQt6.QtCore import Qt
from database.db_manager import obtener_perfiles, agregar_perfil, eliminar_perfil, actualizar_perfil

class DialogoPerfil(QDialog):
    """Diálogo reutilizable para CREAR y EDITAR perfiles"""
    def __init__(self, parent=None, perfil_id=None, nombre="", congregacion="", icono="⛪"):
        super().__init__(parent)
        self.perfil_id = perfil_id
        self.setWindowTitle("Editar Perfil" if perfil_id else "Crear Nuevo Perfil")
        self.resize(400, 250)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Nombre del Perfil (Ej. Culto Jóvenes):"))
        self.input_nombre = QLineEdit(nombre)
        layout.addWidget(self.input_nombre)
        
        layout.addWidget(QLabel("Nombre de la Congregación:"))
        self.input_congregacion = QLineEdit(congregacion)
        self.input_congregacion.setPlaceholderText("Ej. Iglesia A")
        layout.addWidget(self.input_congregacion)
        
        layout.addWidget(QLabel("Selecciona un Ícono:"))
        self.combo_icono = QComboBox()
        iconos = ["⛪", "🕊️", "🔥", "📖", "🎵", "🎸", "🙌", "👑", "🌐"]
        self.combo_icono.addItems(iconos)
        if icono in iconos:
            self.combo_icono.setCurrentText(icono)
        self.combo_icono.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.combo_icono)
        
        btn_guardar = QPushButton("Guardar Perfil")
        btn_guardar.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(btn_guardar)
        
        self.setLayout(layout)
        
    def guardar(self):
        if not self.input_nombre.text().strip() or not self.input_congregacion.text().strip():
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return
        
        if self.perfil_id:
            actualizar_perfil(self.perfil_id, self.input_nombre.text(), self.input_congregacion.text(), self.combo_icono.currentText())
        else:
            agregar_perfil(self.input_nombre.text(), self.input_congregacion.text(), self.combo_icono.currentText())
            
        self.accept()

class ProfileSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LuminaCast - Seleccionar Perfil")
        self.resize(500, 450)
        self.congregacion_seleccionada = ""
        self.perfil_seleccionado = ""
        
        layout_principal = QVBoxLayout()
        
        titulo = QLabel("Selecciona un Perfil de Trabajo")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout_principal.addWidget(titulo)
        
        self.lista_perfiles = QListWidget()
        self.lista_perfiles.setStyleSheet("font-size: 18px; padding: 5px;")
        self.lista_perfiles.itemDoubleClicked.connect(self.ingresar)
        layout_principal.addWidget(self.lista_perfiles)
        
        # Botones de acción
        layout_botones = QHBoxLayout()
        
        btn_nuevo = QPushButton("➕ Nuevo")
        btn_nuevo.clicked.connect(self.crear_perfil)
        
        btn_editar = QPushButton("✏️ Editar")
        btn_editar.clicked.connect(self.editar_perfil_seleccionado)
        
        btn_eliminar = QPushButton("🗑️ Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_perfil_seleccionado)
        
        layout_botones.addWidget(btn_nuevo)
        layout_botones.addWidget(btn_editar)
        layout_botones.addWidget(btn_eliminar)
        
        self.btn_ingresar = QPushButton("▶ Ingresar a LuminaCast")
        self.btn_ingresar.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 12px; margin-top: 10px;")
        self.btn_ingresar.clicked.connect(self.ingresar)
        
        layout_principal.addLayout(layout_botones)
        layout_principal.addWidget(self.btn_ingresar)
        
        self.setLayout(layout_principal)
        self.cargar_perfiles()

    def cargar_perfiles(self):
        self.lista_perfiles.clear()
        perfiles = obtener_perfiles()
        for p_id, nombre, congregacion, icono in perfiles:
            texto_mostrar = f"{icono}  {nombre} ({congregacion})"
            item = QListWidgetItem(texto_mostrar)
            item.setData(Qt.ItemDataRole.UserRole, {"id": p_id, "congregacion": congregacion, "nombre": nombre, "icono": icono})
            self.lista_perfiles.addItem(item)
            
        if self.lista_perfiles.count() > 0:
            self.lista_perfiles.setCurrentRow(0)

    def crear_perfil(self):
        dialogo = DialogoPerfil(self)
        if dialogo.exec():
            self.cargar_perfiles()

    def editar_perfil_seleccionado(self):
        item = self.lista_perfiles.currentItem()
        if not item: return
        datos = item.data(Qt.ItemDataRole.UserRole)
        
        dialogo = DialogoPerfil(self, perfil_id=datos["id"], nombre=datos["nombre"], congregacion=datos["congregacion"], icono=datos["icono"])
        if dialogo.exec():
            self.cargar_perfiles()

    def eliminar_perfil_seleccionado(self):
        item = self.lista_perfiles.currentItem()
        if not item: return
        datos = item.data(Qt.ItemDataRole.UserRole)
        
        respuesta = QMessageBox.question(self, "Eliminar", f"¿Seguro que deseas eliminar el perfil '{datos['nombre']}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if respuesta == QMessageBox.StandardButton.Yes:
            eliminar_perfil(datos["id"])
            self.cargar_perfiles()

    def ingresar(self):
        item = self.lista_perfiles.currentItem()
        if not item: return
        datos = item.data(Qt.ItemDataRole.UserRole)
        self.congregacion_seleccionada = datos["congregacion"]
        self.perfil_seleccionado = datos["nombre"]
        self.accept()